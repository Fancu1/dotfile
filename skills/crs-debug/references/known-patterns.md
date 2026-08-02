# 已知病例库

每个 pattern 给出:**指纹**(怎么识别)、**根因**(为什么发生)、**缓解**(临时止血)、**治本**(根本方案)。

按"被遇到的频率"排序,最常见的在前。

---

## 1. 号商账号被批量吊销 (token_revoked / token_invalidated)

### 指纹

- 日志里大量 401:`"code":"token_revoked"` 或 `"code":"token_invalidated"`
- 报错文本:`"Encountered invalidated oauth token for user, failing request"` 或 `"Your authentication token has been invalidated"`
- Redis 里这些账号 `status=unauthorized`、`schedulable=false`
- **关键特征**:`unauthorizedAt` 时间戳**集中在 18 分钟到 1 小时内**,几乎所有账号同时被吊销
- **账号归属**:全部是号商账号(命名规律,例如 `jun01-jun20`、`Y20`、`YJ01-YJ19`、`haomai-xianyu-codex`)。个人账号(`boyin-codex` / `siming-codex` / `haomai-codex` / `wenxin-codex` / `刘名欣-codex`)**几乎不中招**

### 根因

OpenAI 风控系统识别批量购买的低信任度账号,**直接吊销其 OAuth access_token + refresh_token**。这是账号级别的处罚:
- ChatGPT 网页登录还能用(因为是 session cookie,不是 OAuth token)
- 但 OAuth 颁发的 access_token 被列入黑名单
- 重新 OAuth 能颁新 token,但通常 10-20 分钟后又会被同样的风控批处理识别并吊销

### 缓解

```
1. 在 admin UI 里把这些账号 schedulable=false
   → 让调度器不再轮到它们,避免反复挂在它们上面
2. 不要再去重新 OAuth 这些账号
   → 重新授权也救不回,只会让 unauthorizedCount 累积
3. 如果 unauthorizedCount > 2 → 直接放弃这个账号
```

### 治本

迁到 `openai-responses` 账号类型(用 OpenAI API key,不依赖 ChatGPT 订阅)。详见末尾"方案对比"章节。

---

## 2. ChatGPT 后端软排队 (p99 长尾 5-9 分钟)

### 指纹

- p50 看着正常(5-10s),但 p99 蹿到 4-8 分钟,max 可达 9 分钟+
- **完全没有 429**(关键!不是硬限流)
- 慢请求账号归属:80%+ 集中在号商账号
- 用户体感"一个问题等很久才回复"
- 慢请求里 `cached_tokens` 比例不一定低(说明不是 cache 问题)
- 中间几分钟没有任何中间日志(只有最终 200 响应那一行)

### 根因

OpenAI 风控**升级版**:不直接 revoke,改成给请求加 queue,慢慢响应。比直接 401 更阴险:
- 不返回 429 → relay 没机会熔断/标记
- 不返回 401 → 不会被 markAccountUnauthorized
- 最后真的返回 200 → 从指标上看"成功",从体验上看"卡死"
- 客户端只要不 abort,就一直等

### 缓解

- **不要把流量集中到少数账号**(见 Pattern 3 的教训)
- 让 sticky 自然均匀分散
- 客户端层面教育团队成员: 卡 > 30s 就 abort 重试(可能换到健康账号)

### 治本

跟 Pattern 1 同源: 迁 API key。号商账号被 OpenAI 内部打了风险分,在这条路径下无法翻身。

---

## 3. priority 调整的反作用

### 指纹

- 用户把"个人账号"调高优先级(数字调小,如 37/40),想让流量优先走个人号
- 调完 30 分钟后,p95/p99 **翻倍**
- 个人账号开始出现 2+ 分钟慢请求(之前几乎从不慢)
- 号商账号仍偶尔被 sticky 命中,慢请求体验跟之前相同

### 根因

**ChatGPT 软限流的阈值是按单账号 RPM/TPM 算的,不是按"号商 vs 个人"。**

- 之前 25 个账号摊薄流量 → 每个账号都低于阈值
- 现在流量被强制集中到 5-6 个个人账号 → **个人账号也被推过阈值**
- 同时号商账号还在(sticky 命中),继续慢

**净效果:个人账号从安全 → 也慢,号商账号还是慢 = 整体更差。**

### 缓解 + 治本

**直接回滚 priority,所有账号统一 50。** 这是个验证过的反作用,不要再做"个人账号优先"的实验。

如果一定要做账号分级,正确做法是 `schedulable=false` 完全禁用号商账号(把它们移出调度池),而不是调 priority。但禁用后流量全压个人账号也会被打挂,**所以根本上还是"账号池不够"的问题,只有迁 API key 才能解决**。

---

## 4. OpenAI 上游服务事故 (持续 / 间歇性)

### 指纹

- **用户描述**:"之前用同样配置就是好的" / "这一两天才慢"
- 配置没改、账号没动、relay 健康(host load 低、Redis 正常)
- 慢请求**不集中在号商账号**,而是均匀分布
- 个人账号也开始慢
- **status.openai.com/history 显示近期 Codex / GPT-5.5 / Thinking 相关 incident**

### 历史先例

参考 2026 年 5 月这一波(skill 撰写时刚发生):

```
5/8   Increased Error Rate for gpt-5.5 model in the API
5/11  GPT 5.5 elevated error rates
5/13  Codex 5.5 engines high error rate
5/14  Codex Cloud / Code Review high failure rate
5/17  GPT-5.5 Performance Degradation
5/20  API users see increased GPT-5.4 / GPT-5.5 error rates
5/21  Elevated latency for ChatGPT 5.5 Thinking  ← reasoning_effort 路径命中
5/23  Increase in users hitting Codex rate limits
```

更早的先例:2025-09-16 那次 GPT-5 Codex regression,Sam Altman 在 X 上承认"GPU 紧缺,服务降速约 2 倍",2 天后扩容恢复。

### 根因

OpenAI 后端 GPU 容量紧缺 / 新模型上线 / 内部 bug。**跟你的反代、跟号商账号、跟 cache miss 全部无关**——OpenAI 的所有用户(包括 ChatGPT 网页用户)都受影响。

### 缓解(等扩容期间能用的)

1. **临时切模型**: `gpt-5.5` → `gpt-5.4-codex` 或 `gpt-5.3`(老版本通常更稳)
   - 可以通过 CRS 的 `requestBodyRuleService` 在服务端强制覆盖,**不需要团队每人改配置**
   - admin UI → API key → "OpenAI Responses Payload Rules" → 加规则覆盖 `model` 字段
2. **临时降 reasoning_effort**(如果之前用 high/xhigh): 5/21 incident 直接命中 5.5 Thinking 路径,这段时间用 medium 更稳
3. **错峰使用**: 太平洋时间 9AM-6PM 高峰期最差,中国团队下午到晚上反而好

### 治本

**等 OpenAI 修**。参考历史经验,这种全平台 incident 通常 2 天到 2 周内恢复。期间持续监控 status 页面。

---

## 5. Cache 命中率低 (sticky TTL 太短)

### 指纹

- 整体 cache hit ratio < 30%
- 抓 `cached:X` 字段,**几乎所有请求 X = 2304**(刚好是 Codex Desktop fixed system prompt 长度)
- 长会话连续多次请求,但每次都重新预热

### 根因

- 默认 `STICKY_SESSION_TTL_HOURS=1`(1 小时)
- 长会话每小时被换到新账号
- 新账号的 ChatGPT cache 是空的,前几轮全 miss
- 刚 hot 起来又被换走

### 缓解 = 治本

加两个环境变量(本会话已经做过,标准化为 4h + 自动续期):

```yaml
# docker-compose.yml
environment:
  - STICKY_SESSION_TTL_HOURS=4
  - STICKY_SESSION_RENEWAL_THRESHOLD_MINUTES=60
```

效果:
- sticky 寿命从 1h → 4h
- 剩余 < 60min 时自动续期(只要会话还在用,sticky 永不过期)
- 整体 cache hit ratio 25% → 45-55%
- 长会话单请求 cache hit 提升到 70%+

**注意**: ChatGPT 单账号 cache 也有"5-10 分钟 idle 自动 evict"机制,所以 sticky 长不等于 cache 永远命中。中间空闲 10 分钟后回来,第一个请求还是要重新预热。

---

## 6. 大上下文请求的纯模型计算时间

### 指纹

- 用户体感"问个问题等 8-20 秒才出第一个字"
- input 大小 100K-200K tokens(p75 = 145K 是典型的)
- output 反而少(200-500 tokens)
- cache hit ratio 正常(50-70%)
- 慢请求**均匀分布**在所有账号

### 根因

不是 relay 慢,不是限流,**是 GPT-5.5 模型本身处理大上下文需要时间**。

算笔账:
- 200K input + 50% cache hit → 100K fresh tokens
- GPT-5.5 处理速度 ≈ 5K-15K input tokens/秒
- 模型纯计算时间: 7-20 秒
- 加上 stream 输出时间: 总 8-25 秒
- 跟实测 p50=8.6s / p75=19s 完全吻合

这是模型本身的物理时间,**relay 无能为力**。

### 缓解

只能从客户端侧减少 input:

1. **`.codexignore`** 排除 `node_modules` / `dist` / `build` / `coverage` 等
2. **`/compact` 或 `/clear`** 定期压缩 codex 长会话上下文
3. **拆问题**: "重构整个模块" → "看 X 文件,然后建议改 Y"
4. **避免读大文件**: 一旦某个工具调用返回 50K tokens 文件,后续每轮都带它

### 治本

无。这是模型物理特性。除非 OpenAI 出更快的模型,否则 200K input 就是要算 10-30 秒。

---

## 7. Reasoning effort 配置导致的慢(在 OpenAI 上游正常时)

### 指纹

- 请求体里 `"reasoning":{"effort":"high"}` 或 `"effort":"xhigh"`
- 这种请求耗时显著长于 `"effort":"medium"` 的请求
- input 不大但耗时几分钟、output 极少(几十到几百 tokens)
- 团队成员 codex 配置 `reasoning_effort = high/xhigh`

### 根因

GPT-5 / 5.5 系列的 extended thinking 机制:

| effort | reasoning tokens 量 | 典型耗时 |
|--------|------------------|---------|
| `low` | 几十-几百 | < 1s |
| `medium`(默认) | 几百-几千 | 1-10s |
| `high` | 几千-上万 | 10-60s |
| `xhigh` | 上万 | 1-10 分钟 |

reasoning tokens 不计入 input 也不计入 output,但实际消耗 GPU 时间。

### 缓解

⚠️ **如果是回归(之前同样配置不慢,现在慢了),不要先归因到这里。** 先排除 Pattern 4(上游事故)。

只在确认上游服务健康但 reasoning 慢时:

- **服务端强制覆盖**(推荐): admin UI → API key → "OpenAI Responses Payload Rules" → 把 `reasoning.effort` 强制改成 medium
- **客户端配置**: 每人改 `~/.codex/config.toml` 的 `reasoning_effort = "medium"`

### 治本

教团队成员只在确实需要(大重构、复杂调试)时手动改 xhigh,默认 medium。

---

## 8. Redis SCAN 慢拖累整体响应

### 指纹

- redis-cli slowlog 看到 `SCAN ... MATCH pattern COUNT N` 耗时 > 10ms
- 整体 ops/s > 2000
- dbsize 大(> 50K),`usage:*` 占大头

### 根因

Redis SCAN 是 O(N),N 是 dbsize。当 dbsize ≈ 64K 时,即使只匹配 6 个 key,也要扫遍全 keyspace,单次 12ms。

主要慢操作来源:
- `src/app.js:520` 某个定时任务扫 `session:*`
- `src/models/redis.js:3082` 的清理任务扫多个 pattern

### 缓解

实时检查是否真的慢:
```bash
docker exec claude-relay-service-redis-1 redis-cli config set slowlog-log-slower-than 5000
docker exec claude-relay-service-redis-1 redis-cli slowlog reset
sleep 30
docker exec claude-relay-service-redis-1 redis-cli slowlog get 10
```

如果实时 0 条慢操作,**不是热路径瓶颈**,可以忽略。

### 治本

- 等上游 fix(给 SCAN 改成索引)
- 或者降 `LOG_LEVEL` 减少 logger 间接触发的 Redis 写入
- 或者清掉历史 `usage:*` key(需要确认这些数据不再需要)

---

## 9. ENCRYPTION_KEY 改变的次生灾害(从未发生,但要避免)

### 指纹

- 切换镜像后所有账号都报"Failed to decrypt"
- admin UI 里账号列表的 email、token 显示乱码
- 上游请求统统 401(因为 access_token 解密后是垃圾)

### 根因

`ENCRYPTION_KEY` 是 AES 加密所有敏感字段(access_token / refresh_token / id_token / email)的密钥。改了 → Redis 里加密的数据全部解密失败。

### 缓解

**永远不要让这种事发生。** 任何 docker-compose 改动前先 `diff` 备份,确认 `ENCRYPTION_KEY` 和 `JWT_SECRET` 行没动过。

### 如果真的发生了

1. 立刻停服 `docker compose stop claude-relay`
2. 改回原始 `ENCRYPTION_KEY` 值
3. `docker compose up -d`
4. **不要重启 Redis**(Redis 里的数据还是用原 key 加密的,只要 key 改回就能解)

---

## 10. ccr-codex 桥接的额外路径

### 指纹

- 错误信息里出现 `Error from provider(crs-openai,gpt-5.5: 401)` 的格式
- 这种格式不是 CRS 自己输出的,是 CCR (claude-code-router) 输出的
- 报错堆栈里有 `/usr/local/lib/node_modules/@musistudio/claude-code-router`

### 根因

部分团队成员用 Claude Code 客户端(原本接 Anthropic),通过 ccr-codex 容器转换协议到 OpenAI/Codex 格式,然后再发给 CRS。链路:

```
Claude Code → ccr-codex (协议转换) → CRS (反代) → ChatGPT 后端
```

CCR 在中间会重新打包错误,把上游 401 包装成 `Error from provider(...)` 格式。

### 排查含义

- 看到 `Error from provider(crs-openai,...)` 不是 CRS 自身的 bug,**原始错误码在内层 JSON 里**(status / code 字段)
- 解读原始错误要剥两层(外层 CCR + 内层 CRS),最终 ChatGPT 的真实响应在最内层

---

## 方案对比表

按"治本程度"排序。

| 方案 | 月成本(10 人团队) | 改造工作量 | 治本程度 | 备注 |
|------|------------------|----------|---------|------|
| 现状(OAuth 反代 + 号商号) | $1500+/月(订阅 + 反复买号) | - | 0% | 风险持续累积 |
| 调 sticky / cache 优化 | 0 | 1 小时 | 10% | 只缓解 cache miss |
| 配住宅代理 IP 池 | +$30-60/月 | 1-2 周 | 30% | 降低被检测概率,治标 |
| 换 codex-proxy (icebear0828) | 0 | 3-5 天迁移 | 30% | TLS 指纹伪装,治标 |
| 切到 GPT-5.4-codex 模型 | 0 | 1 小时 | 视上游情况 | 上游 5.5 紧缺时有效 |
| **OpenAI Codex-only Seats** | **$25 + $300-500/月** | **2-3 天** | **100%** | **零座位费,无 rate limit,需 Business 主账号 + 海外信用卡** |
| **OpenAI API key + openai-responses 账号** | **$300-500/月** | **1 天** | **100%** | **现有 CRS 直接支持,门槛最低的治本方案** |

> 治本只有两个: Codex-only Seats 或直接 API key。**两者都依赖海外信用卡 / OpenAI 商业账号**,这是核心阻塞点。

---

## 时间戳记录(基于已知会话)

- 2026-04-09: OpenAI 改 Codex 限额为"按推理时间"
- 2026-05-08 起: GPT-5.5 持续小事故
- 2026-05-22 17:36 UTC: 号商账号集体被 token_revoked(本仓库观测到的第一次集体吊销)
- 2026-05-23: 本仓库从 `pr1167-8b45891` 切到 `weishaw/claude-relay-service:1.1.304`,加 STICKY_SESSION_TTL_HOURS=4
- 2026-05-25: 用户感知 "之前正常,这一周慢",验证为 OpenAI 上游事件(非配置问题)
