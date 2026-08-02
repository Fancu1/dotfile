---
name: crs-debug
description: 用于诊断我们自部署的 claude-relay-service (CRS) AI 反代平台的所有运行时问题。触发场景包括但不限于：团队成员反馈 Codex/Claude Code 慢、卡死、报"认证问题无法路由"、API key 失效、OpenAI 账号 token_revoked / token_invalidated、号商账号被吊销、cache 命中率低、Redis 慢、单请求耗时 5-8 分钟、sticky session 不生效、调度策略问题、迁移镜像、调整配置。**只要话题涉及 10.10.102.14 上的 CRS / claude-relay-service / claude-relay 反代 / 我们的代理平台 / 给团队共享的 Codex 服务,就 invoke 这个 skill**,即使用户没说"CRS"几个字也要用。先采证后下结论,默认只读,任何写操作必须显式授权。
---

# CRS 诊断 Skill

## 这个 skill 是什么

把过去诊断 claude-relay-service (CRS) 这套自部署 AI 反代平台时踩过的所有坑、找到的所有方法、用过的所有数据通路,**沉淀成系统性的故障排查流程**。后续遇到同类问题(团队成员说"codex 慢/卡/挂了")直接进入这套流程,不需要每次从零开始猜。

## 核心原则(违反任一条就会走偏)

### 1. 不预设结论,先采证

用户描述的症状**只是表象**。"codex 慢"可能是 12 种不同根因(见 [known-patterns.md](references/known-patterns.md))。先采集数据,让数据指向根因,而不是听到关键词就跳到结论。

具体反模式:
- ❌ "codex 慢 → 一定是 cache miss → 改 sticky TTL" (上次就是这样误诊的)
- ❌ "慢 → 一定是 OpenAI 限流 → 加号商账号" (越加越慢)
- ❌ "401 → 一定是配置错 → 改代码" (实际是 OpenAI 主动吊销)

正模式:
- ✅ 用户描述症状 → 先用[诊断 playbook](references/diagnosis-playbook.md) 跑一轮采证 → 看数据指向 → 再下结论

### 2. 分层诊断,从外往内排除

CRS 是个多层系统:

```
团队成员客户端 (Codex Desktop / Claude Code)
    ↓
CCR 桥接 (ccr-codex 容器,Claude API → OpenAI 转换)
    ↓
claude-relay-service (主反代,路由 + 鉴权 + 账号调度)
    ↓
Redis (账号 / API key / sticky session / usage)
    ↓
ChatGPT 后端 (https://chatgpt.com/backend-api/codex/responses)
    ↓
OpenAI 风控系统
```

**每一层都可能慢/挂**。诊断时按"从最外层开始排除"的顺序,不要一上来就钻进某一层。具体每层怎么排除见 [diagnosis-playbook.md](references/diagnosis-playbook.md)。

### 3. 只读优先,改动要明确授权

CRS 是生产服务,改一下就影响 10 个团队成员。规则:

- **采集信息(SSH、docker logs、redis 查询)**:直接做,不用问
- **修改配置(docker-compose、admin UI、Redis 写入)**:必须给用户讲清楚影响 + 拿到明确同意才动
- **重启容器**:同上,会有 1-3 秒断流
- **删除数据**:必须备份 + 明确同意

详细环境清单(SSH 命令、容器名、关键路径、配置位置)见 [environment.md](references/environment.md)。

### 4. 多维度并行采证,一次性拿齐

诊断时不要一个维度查完看完再查下一个。**单次 SSH 把 5-7 个维度的快照同时拿下来**,这样:
- 时间一致(避免维度间相互"已经变了")
- 总耗时短
- 一眼能看出"哪个维度跟其他维度不对劲"

playbook 里给出了"一次性采证套餐"的模板思路。

### 5. 时间维度对照——"什么时候开始?之前正常吗?"

这是最容易遗漏的关键问题。同一个症状:
- "一直就慢" → 大概率是配置 / 用法问题
- "这一周才慢" → 大概率是上游事故 / 风控规则变更
- "刚才好好的突然慢了" → 大概率是某个具体变更触发的回归

诊断开始时**必问**这个问题,不问就容易诊断错(上次就把"OpenAI 5 月持续劣化"误诊成"reasoning_effort 配置问题")。

### 6. 区分"OpenAI 官方事实"与"我的推断"

写报告或回答用户时严格区分:

- **官方事实**:status.openai.com 上的 incident 标题、OpenAI 公告、官方推文
- **强证据**:服务器日志里的错误码、Redis 里的实际数据、reproducible 现象
- **推断**:把官方事实和现象拼成的因果链 (例如"因为有 incident 标题 + 你说慢 = 所以是 incident 导致的")

不要把推断说成事实。这次会话踩过这个坑(用"GPU 紧缺"解释 5 月慢,但没有官方 5 月的 GPU 紧缺声明,只有 2025-09 那次有)。**承认不确定,提出验证方法,让事实说话**。

### 7. 数据先 → 结论后,不反过来

写诊断报告的顺序应该是:

```
[采集到的数据]      ← 先把客观数据列出来
    ↓
[这些数据排除了什么] ← 然后说排除了哪些可能
    ↓
[剩下指向什么]      ← 最后给指向的结论
    ↓
[需要验证什么]      ← 不确定的地方提出验证方法
```

不要倒过来:不要先给结论,然后挑选支持的数据。

## 入口工作流

收到"CRS / 反代慢 / 团队反馈 codex 不可用"类问题时:

1. **先问时间** — "什么时候开始的?之前正常吗?最近有什么变更吗(配置、账号、客户端版本)?"

2. **看[环境地图](references/environment.md)** — 确认 SSH、容器、路径都还是上次那一套

3. **跑[诊断 playbook](references/diagnosis-playbook.md)** — 多维度并行采证,5 分钟拿全数据

4. **对照[已知病例库](references/known-patterns.md)** — 看看症状指纹是否匹配某个已知 pattern

5. **写报告** — 按"数据 → 排除 → 指向 → 验证"四段式

6. **给方案** — 明确区分"立刻能做(不要授权)"、"小改动(要授权)"、"重决策(要讨论)"

## 经验教训(必读,避免重蹈覆辙)

下面这些坑在过去会话里都踩过一次,**写下来是为了下次别再踩**:

| 教训 | 出处 |
|------|------|
| 不要看到 token_revoked 就猜代码 bug,先确认是不是号商账号集体被吊销(账号名规律) | 第一次会话误诊 JWT exp 解析问题 |
| 不要看到长尾延迟就跳到"限流",可能是 OpenAI 上游事故(查 status 页面) | 5/22 GPT-5.5 事件 |
| 不要把流量集中到少数账号,会触发新的软限流(p99 翻倍) | 调高个人账号 priority 的反作用 |
| 不要在用户没说"账号失效"时就告诉他"是号商账号问题",先看 Redis 里 status 字段 | 多次混淆症状归因 |
| 不要忽略时间维度,"之前正常,现在慢"几乎一定是上游变更 | 5/22-25 这一波 |
| docker compose logs 比 docker logs 慢得多,大日志量场景用 docker logs --tail | 多次踩坑 |
| `docker logs --tail 50000 > /tmp/relay.log` 然后本地 grep,比反复 docker logs 高效 | 诊断长会话标配 |
| ENCRYPTION_KEY 改了等于所有账号数据废掉,**永远不要动** | 切镜像前的最大风险 |
| 优先级数字"越小越优先",不是越大越优先(容易记反) | priority 调整时差点搞反 |
| Codex Desktop 的请求体很大(系统提示词几千 tokens),docker logs 容易 OOM,grep 时一定要先 tail/head 限流 | 性能 |

## 已知能解决问题的工具/方案(快速索引)

按"治标 → 治本"排序,详细见 [known-patterns.md](references/known-patterns.md):

| 问题 | 临时缓解 | 根本方案 |
|------|---------|---------|
| 号商账号集体被吊销 | 禁用 schedulable=false | 迁 OpenAI API key (`openai-responses` 账号类型) |
| 上游软限流(p99 长尾) | 等(短时事件) / 加账号摊薄 | 同上 |
| cache 命中率低 | `STICKY_SESSION_TTL_HOURS=4 + RENEWAL_THRESHOLD=60` | 同上 |
| 上游 GPT-5.5 劣化 | 切 model 到 5.4-codex / 5.3 | 等 OpenAI 扩容,或迁 API |
| 大上下文请求慢 | 客户端加 .codexignore / /compact | 拆任务 |
| 个人账号被打挂 | **回滚 priority** ← 别再做"个人优先"了 | 加 Codex-only Seats |
