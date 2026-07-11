# 诊断 Playbook

## 总原则

**5 分钟拿全 7 个维度的快照,再下结论**。不要一个维度看完再看下一个——时间不一致会让你看到的"问题"自相矛盾。

---

## 必问的前置问题(不问就容易诊断错)

收到症状描述,**先问这三件事**:

1. **什么时候开始的?** — "一直就这样" vs "今天才慢" vs "刚才好好的突然慢了"
2. **影响范围?** — "所有人都慢" vs "就某几个人" vs "某些操作慢、某些不慢"
3. **最近有什么变更?** — 客户端版本升级 / 配置改动 / 加了账号 / 改了 priority / 镜像升级

这三个问题答完,候选根因往往已经收敛到 2-3 个。

**反例**(没问就开始猜的代价): 5/25 那次同事反馈"很慢",我立刻跳到"reasoning_effort 太高" → 改了一通后用户说"之前用同样配置就是好的" → 才意识到是 OpenAI 上游 5 月 21 日开始的 GPT-5.5 性能事件。如果一开始问"什么时候开始的"就能少走 1 小时弯路。

---

## 7 个采证维度

每个维度都给出"采什么"和"指纹是什么"。具体命令让 Claude 现场写——因为日志路径、grep pattern 会随诉求变化。

### 维度 1:环境与状态

**采什么:**
- 当前镜像版本(`docker inspect` Image 字段)
- 容器健康状态(`docker compose ps`)
- 上次配置改动时间(`ls -la /opt/claude-relay-service/docker-compose.yml.bak-*`)
- 关键环境变量(`docker exec ... env | grep -E "STICKY|LOG_LEVEL|ENCRYPTION"`)

**正常指纹:**
- 镜像 `weishaw/claude-relay-service:1.1.304` 或更新
- 容器 status `Up X (healthy)`
- 没有最近 24 小时的备份文件(说明没人最近改过)

**异常指纹:**
- 镜像变成本地 build(`claude-relay-service:pr*` / `claude-relay-service:latest`) — 可能有人切回了未发布版本
- 容器反复 restart(`Restarting (X) Y minutes ago`) — 启动失败
- 备份文件刚出现 — 有人改了但没告诉你

### 维度 2:账号池

**采什么:**
- 总账号数 / active 数 / unauthorized 数
- schedulable=true vs false 数
- 个人账号 (boyin/siming/haomai/wenxin/刘名欣) 是否全 active
- 号商账号 (jun*/YJ*/Y20) 是否大批 unauthorized
- proxy 字段是否为空(目前应该都是空)

**正常指纹:**
- active >> unauthorized,或两者比例与历史一致
- 6 个个人账号全 active
- 号商账号即便有 unauthorized 也是少数,不是集体

**异常指纹:**
- **号商账号集体 unauthorized,unauthorizedAt 集中在 18 分钟内** → OpenAI 风控批处理,这次会话遇到过 5/22 17:36 那波
- **个人账号也开始 unauthorized** → 风控扩大,严重信号
- **某账号 unauthorizedCount > 2** → 用户反复重新 OAuth 但又被吊销,**别再 OAuth 了,救不回来**

### 维度 3:Host + 容器资源

**采什么:**
- Host load average / 16 核
- 容器 CPU%(docker stats)
- 容器 mem usage
- Redis 容器 mem

**正常指纹:**
- Host load < 8(50% 容量)
- CRS 容器 CPU < 100%
- CRS 容器 mem < 1GB
- Redis 容器 mem < 200MB

**异常指纹:**
- Host load > 12 → 机器要顶不住,但要先看是不是别的容器占的
- CRS 容器 CPU 持续 > 200%(超过 2 个核) → Node.js 在跑非常 CPU intensive 的活,可能 GC / 加解密暴增
- CRS 容器 mem 持续上涨 → 内存泄漏,**用 `docker logs --tail` 别用 `docker compose logs`**

⚠️ **常见误判**: `docker stats` 显示的 CPU% 是瞬时,容易看到 112%、150% 的尖峰但实际平均只有 20%。**Host load average 才是真实负载**。

### 维度 4:请求量 + 错误率

**采什么:**
- 最近 10 分钟账号选择次数(`Selected OpenAI account` 出现次数)
- 错误分布:429 / 401 / 403 / 503 / 504 / ECONNRESET / Client disconnected
- Slow request 标记数

**正常指纹:**
- 10 分钟内 500-1000 次账号选择(团队 10 人活跃用 codex)
- 429 < 5%
- 401 < 1%(没有持续吊销)
- ECONNRESET 极少

**异常指纹:**
- **429 突然 > 20%** → 上游硬限流,可能 Codex Cloud 容量问题
- **401 集中爆发(60-80 个/小时)** → 看 [known-patterns.md](known-patterns.md#1-号商账号被批量吊销)
- **Slow request 数 / 总请求数 > 80%** → 全员慢,大概率上游事故,**优先查 status.openai.com**

### 维度 5:延迟分布(关键!)

**采什么:**
- 200 响应耗时的 p50/p75/p90/p95/p99/max
- 超过 2 分钟的请求列表(账号、key、耗时)

**正常指纹**(基于历史正常值):
```
p50: 3-5s
p75: 8-12s
p90: 15-25s
p95: 25-40s
p99: 60-90s
max: < 3min
```

**异常指纹**:
- **p99 突然跳到 4-8 分钟** → 看是否集中在号商账号(软限流)还是全账号(上游事故)
- **p50 突然 > 10s** → 全局劣化,上游问题概率大
- **p99 > p95 * 5+** → 长尾极重,典型软排队特征

**关键判断**:延迟分布是**双峰**(大多数请求快,少数极慢)还是**整体上移**(中位数也涨)。
- 双峰 → 单账号被 throttle 之类的局部问题
- 整体上移 → 上游服务问题

### 维度 6:慢请求归因

**采什么:**
- 取 >= 2 分钟的请求,从日志往前找它们的 `Selected OpenAI account: XXX`
- 统计哪些账号占比最高

**正常指纹:**
- 慢请求账号分布跟整体请求量分布大致一致(均匀慢)

**异常指纹:**
- **全部集中在号商账号(YJ*/jun*)** → ChatGPT 后端给号商账号软排队(5/22 那次会话的情况)
- **集中在某几个被调高 priority 的账号** → priority 调整反作用,**回滚 priority**
- **集中在一两个账号(无明显 priority 偏好)** → 那几个账号可能用量配额耗尽

### 维度 7:Cache 命中率

**采什么:**
- 抓 `Recorded OpenAI usage - Input: X(actual:Y+cached:Z)` 的样本
- 加权计算整体 cache hit ratio = sum(Z) / sum(X)

**正常指纹:**
- 整体 hit ratio: 45-65%
- 长会话单请求(input > 50K): hit ratio 70-90%
- `cached:` 值多样化(2304、几千、几万都有)

**异常指纹:**
- 整体 hit ratio < 30% → sticky session 不工作,检查 `STICKY_SESSION_TTL_HOURS` 配置
- **`cached:` 几乎全是 2304** → 只有 system prompt 命中,会话上下文全 miss。sticky 太短导致每次换号
- input 大但 cached:0 → 新会话首请求(正常)或 sticky 失败(异常)

### 额外:Redis 健康

**采什么:**
- `redis-cli info stats` 看 `instantaneous_ops_per_sec`
- `redis-cli slowlog get 10`
- `redis-cli dbsize`
- 各 key prefix 数量

**正常指纹:**
- ops/sec < 500
- slowlog 无近期记录(或都是 < 10ms)
- dbsize ~64K(`usage:*` 占大头)

**异常指纹:**
- ops/sec > 2000 → Redis 在被疯狂打,看是哪些 key
- slowlog 有 SCAN 操作 > 50ms → dbsize 太大导致 SCAN 慢
- dbsize 在涨 → 可能有 key 没设 TTL

### 额外:上游事件

**采什么:**
- `WebFetch https://status.openai.com/history` 取最近一周 incident
- 重点看 Codex / GPT-5.5 / GPT-5.4 / Thinking 相关条目

**正常指纹:**
- 一周内 < 2 个相关 incident,都标记"已恢复"

**异常指纹:**
- 最近 24-48 小时多个 Codex / GPT-5.5 incident(即便标"已恢复")
- 与用户感知时间窗口完全重合 → 强证据,**优先归因到上游**

---

## 决策树:从症状到根因

```
症状: 用户说"慢/卡/不可用"
    │
    ├─ 先问时间维度
    │   "之前正常吗?" → "对,这一两天才出问题"
    │       → 查 status.openai.com  ← 第一优先级
    │       → 如果有相关 incident → 多半是上游事故,给"切模型 + 等扩容"方案
    │
    │   "对,刚刚还好,突然就卡了"
    │       → 查容器是否刚重启 / 是否有人改了配置
    │
    │   "一直就慢"
    │       → 这是基线问题,不是回归,走完整 7 维度采证
    │
    ├─ 看账号池
    │   号商账号集体 unauthorized 且时间集中
    │       → token_revoked 风控波,见 [known-patterns.md#1]
    │
    │   个人账号也 unauthorized
    │       → 严重,风控扩大,**必须迁 API key**
    │
    ├─ 看延迟分布
    │   p50 正常 + p99 长尾极重
    │       → 看慢请求归因
    │           集中号商 → 软限流
    │           集中个人(priority 高的) → 回滚 priority
    │           均匀分布 → 上游事故
    │
    │   p50 也变高
    │       → 全局劣化,优先查 status.openai.com
    │
    ├─ 看 cache 命中率
    │   < 30% 且都是 2304
    │       → sticky 没生效,查 STICKY_SESSION_TTL_HOURS 配置
    │
    │   30-50%
    │       → 正常区间,不是 cache 的锅
    │
    └─ 资源 / Redis 全绿
        → 不是 relay 本身瓶颈,问题在上游或客户端
```

---

## 写报告的格式

排查完发给用户,严格按这四段:

```
## 数据(我看到了什么)
[列出每个维度的关键数字,不解读]

## 排除(数据已经否决了哪些可能性)
- 不是 relay CPU 瓶颈(host load X/16)
- 不是 Redis 慢(slowlog 0 条)
- 不是账号不够(active 25 个)
- ...

## 指向(剩下的最强假说)
[1-2 个最强的根因解释]

## 不确定的部分 + 怎么验证
[明确标出"这是推断不是事实"的部分,给出验证方法]
```

最后给方案,分三档:
- **立刻能做(不用授权)**: 看日志、跑诊断、查 status
- **小改动(要授权)**: 调 STICKY_SESSION_TTL、toggle schedulable
- **重决策(要讨论)**: 迁 API key、切镜像、改架构

---

## 常见的诊断陷阱(踩过的)

1. **`docker compose logs --tail=N` 慢到爆** — 它会全文件扫描所有服务的日志再过滤。**用 `docker logs --tail N <container-name>` 代替**,直接对单容器,快 10x
2. **`docker logs` 输出包含巨大请求体** — Codex Desktop 每个请求带几千 tokens 的 system prompt,在日志里很大。grep 时一定要先 `--tail 50000 > /tmp/relay.log`,再本地 grep,不要管道传递
3. **`docker stats` 的 CPU% 看一次没用** — 是瞬时值,要看 host `uptime` 的 load average 才是真实负载
4. **不要用 `redis-cli keys "<pattern>"`** — 阻塞整个 Redis,生产严禁。用 `--scan --pattern`
5. **不要看到 SCAN 慢就改代码** — 先看 slowlog 实时是否真的慢,可能是历史值
6. **API key 认证偶尔 12s** 是 Node.js event loop 偶发阻塞,**不是主要瓶颈**,p99 = 100ms 就是健康的
