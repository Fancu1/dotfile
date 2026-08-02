# CRS 部署环境地图

这是我们当前 claude-relay-service 部署的"事实清单"。诊断时先确认这些事实没变,再开始采集运行时数据。

---

## SSH 连接

```bash
ssh -i ~/.ssh/id_ed25519_xsky root@10.10.102.14
```

- 用户: `root`(不需要 sudo)
- 密钥: `~/.ssh/id_ed25519_xsky`
- 跨会话保持的工作目录: `/opt/claude-relay-service/`

## Docker Compose 部署

### 项目目录

```
/opt/claude-relay-service/
├── docker-compose.yml                            ← 主配置
├── docker-compose.yml.bak-*                      ← 历史备份(每次改动留一份)
├── data/                                         ← 挂载到容器 /app/data
│   ├── init.json                                 ← 管理员凭据(单一信任源,不要乱删)
│   ├── model_pricing.json                        ← 模型价格表
│   └── model_pricing.sha256
├── logs/                                         ← 挂载到容器 /app/logs(~5GB+)
├── redis_data/                                   ← Redis 持久化数据(126MB)
├── source/(可能已 archived 成 source.archived-*) ← 旧的本地构建源码
└── deploy/ccr/                                   ← ccr-codex 桥接服务相关
```

### 容器清单

| 容器名 | 镜像 | 端口 | 作用 |
|--------|------|------|------|
| `claude-relay-service-claude-relay-1` | `weishaw/claude-relay-service:1.1.304` (官方) | `0.0.0.0:3000` | **主服务**,处理所有 API 路由、鉴权、调度 |
| `claude-relay-service-redis-1` | `redis:7-alpine` | `6379` (容器内,不暴露) | Redis 存账号/API key/sticky session/usage |
| `ccr-codex` | `local/ccr-codex:latest` | `127.0.0.1:3456` | **CCR 桥接**(Claude API → Codex 协议转换),给依赖 Claude API 的旧基础设施用 |

注意:可能还有 `jovial_cannon` 之类临时跑 claude-code 的容器,跟 CRS 本身**无关**,诊断时忽略。

### 关键端口

- `3000`: CRS 主服务对外口,团队成员客户端打这里
- `3456`: CCR 桥接,只暴露 127.0.0.1
- 上游: `https://chatgpt.com/backend-api/codex/responses` (Codex 路径)、`https://auth.openai.com/oauth/token` (OAuth 路径)

## 容器内关键路径

```
claude-relay-service-claude-relay-1 内部:
/app/
├── src/                              ← Node.js 代码
│   ├── routes/openaiRoutes.js        ← OpenAI/Codex 主路由 handleResponses()
│   ├── services/account/
│   │   ├── openaiAccountService.js   ← OpenAI 账号管理(加密/解密/刷新)
│   │   └── openaiResponsesAccountService.js ← API key 版账号(治本方案的目的地)
│   ├── services/scheduler/
│   │   └── unifiedOpenAIScheduler.js ← 账号调度主逻辑(sticky session 写入点在这里)
│   ├── services/tokenRefreshService.js   ← 分布式锁刷新
│   ├── services/requestBodyRuleService.js ← 请求体改写规则(可强制覆盖 model / reasoning_effort)
│   └── middleware/auth.js
├── config/
│   ├── config.js                     ← 主配置(读 env vars,合并默认值)
│   └── config.example.js
├── data/                             ← 挂载自宿主 ./data
└── logs/                             ← 挂载自宿主 ./logs
```

## 关键配置 (docker-compose.yml 里的 environment)

### 🔴 永远不能改的(改了等于数据全废)

```yaml
- ENCRYPTION_KEY=dYDJCl8X1Rd52i3F2sZPCbr7NmQFH578   # AES 加密所有 OAuth token、refresh token、邮箱、API key
- JWT_SECRET=DgRScUf4T4ofQd7II3rRS9Flkm9Zti1y       # admin session 签名
```

**ENCRYPTION_KEY 一旦改了,Redis 里所有加密字段都会变成乱码,所有账号、API key 都要重做。** 升级镜像、换容器、改 compose 时务必保持原值。

### 🟢 可以调的(已经在用的)

```yaml
- STICKY_SESSION_TTL_HOURS=4                       # sticky session 寿命,默认 1h,调成 4h 提升 cache 命中
- STICKY_SESSION_RENEWAL_THRESHOLD_MINUTES=60      # 剩余 < 60min 时自动续期,默认 0 关闭
- LOG_LEVEL=info                                   # debug 时临时调成 debug,会让 docker logs 变非常大
- REDIS_HOST=redis
- REDIS_PORT=6379
```

### 影响范围速查

- 改 ENCRYPTION_KEY / JWT_SECRET → 全部账号 + API key 失效
- 改 sticky 相关 → 30-60 分钟内 sticky 逐步过渡到新配置
- 改 image tag → 需要 docker compose pull + up -d,3-5 秒断流
- 改 LOG_LEVEL → 实时生效(无需重启)

## Redis 数据模型

Redis 容器内执行 `redis-cli` 不需要密码。**dbsize ~64K key**,大部分是 `usage:*`。

### 关键 key 前缀

| 前缀 | 数量级 | 内容 | 备注 |
|------|-------|------|------|
| `openai:account:<uuid>` | ~25-30 | hash,每个 OpenAI 账号的全部字段(name/status/accessToken/refreshToken/schedulable/priority/...) | accessToken/refreshToken/email 是加密的 |
| `openai:account:index` | 1 | 账号索引 set | |
| `unified_openai_session_mapping:<hash>` | ~100-300 | sticky session 映射(sessionHash → accountId) | **主路径**走这个,改 TTL 配置就影响它 |
| `shared_openai_accounts` | 1 | 共享账号 ID 集合 | |
| `openai_account_sessions:<id>` | ~25 | 反向索引(account → sessions) | 删账号时清理用 |
| `openai_session_account_mapping:*` | 0 | **旧路径,实际未使用**(代码里还有但走不到) | `openaiAccountService.js` 里硬编码 3600 那两处 |
| `api_key:<id>` | 180+ | API key 数据 | |
| `apikey:tag:*` | ? | API key 索引 | |
| `usage:*` | **~46000** | 使用统计 (hincrby 频繁) | **dbsize 大头**,SCAN 时小心,可能拖慢 |
| `session:*` | ~6 | OAuth 会话(短暂) | |
| `token_refresh_lock:<platform>:<accountId>` | 偶发 | 分布式锁,TTL 60s | refresh 时存在 |

### 重要 hash 字段(`openai:account:<id>`)

```
name                      → 账号名(如 "boyin-codex" / "YJ05" / "jun03")
status                    → "active" / "unauthorized" / "error" / "created"
schedulable               → "true" / "false"  (注意是字符串)
priority                  → 数字,**越小越优先**(默认 50)
isActive                  → "true" / "false"
accountType               → "shared" / "dedicated" / "group"
expiresAt                 → OAuth token 过期时间(ISO 字符串)
subscriptionExpiresAt     → 业务字段订阅过期(手动设)
rateLimitStatus           → "normal" / "limited"
rateLimitedAt / rateLimitResetAt
unauthorizedAt / unauthorizedCount → 401 失败次数
errorMessage              → 上次失败的具体原因
accessToken               → 加密的 OAuth access_token (是 JWT)
refreshToken              → 加密的 OAuth refresh_token
idToken                   → 加密的 OAuth id_token
email                     → 加密的邮箱
accountId                 → ChatGPT 内部 account_id(JWT 里的 chatgpt_account_id)
chatgptUserId             → ChatGPT 内部 user_id
proxy                     → JSON 字符串,代理配置(目前全部为空,所有账号共用服务器 IP)
```

## 日志文件

容器内 `/app/logs/`(宿主 `/opt/claude-relay-service/logs/`):

```
claude-relay-2026-MM-DD.log              ← 主日志,当天的明文,可达 GB 级
claude-relay-2026-MM-DD.log.gz           ← 历史日志压缩
claude-relay-error-2026-MM-DD.log        ← error 级别日志,体量小,容易抓
claude-relay-security-2026-MM-DD.log     ← 安全相关(认证失败、可疑请求)
token-refresh.log                        ← OAuth token 刷新成功历史
token-refresh-error.log                  ← OAuth token 刷新失败历史 ← 出问题时优先看这个
exceptions.log                           ← node 未捕获异常
rejections.log                           ← unhandled promise rejection
```

⚠️ **主日志单天可达 300MB+**,直接 `docker logs` 会非常慢且可能 OOM。诊断时:

```bash
# 反模式 ❌
docker compose logs --tail=10000 claude-relay   # 慢,几分钟

# 正模式 ✅
docker logs --tail 50000 claude-relay-service-claude-relay-1 > /tmp/relay.log
# 然后本地 grep / awk /sed 分析
```

## Admin Web UI

```
URL:       http://10.10.102.14:3000/admin-next/
登录凭据:   见 /opt/claude-relay-service/data/init.json
```

### 关键页面

- `/admin-next/openai-accounts` — 账号管理(查看状态、调 priority、toggle schedulable、reset-status)
- `/admin-next/api-keys` — API key 管理(分发给团队成员的 key 在这)
- `/admin-next/dashboard` — 概览(总账号数、健康度)

### 关键 admin API(诊断时可能用到,只读)

```
GET  /admin/openai-accounts             ← 列所有账号
GET  /admin/api-keys                    ← 列所有 key
GET  /admin/dashboard                   ← 概览
GET  /health                            ← 公开健康检查,无需鉴权
```

写操作(动账号 / 改配置)优先走 UI,**不要直接调 admin POST/PUT**,以免出错难回滚。

## 上次会话动过的东西(状态快照)

1. **2026-05-23 镜像迁移**:从 `claude-relay-service:pr1167-8b45891`(本地构建,基于 v1.1.303 + GPT-5.5 patch)切到 `weishaw/claude-relay-service:1.1.304`(官方)。`source/` 目录可能被 archive 成 `source.archived-20260523`。
2. **2026-05-23 sticky TTL 调整**:加了 `STICKY_SESSION_TTL_HOURS=4` 和 `STICKY_SESSION_RENEWAL_THRESHOLD_MINUTES=60` 两个环境变量。
3. **2026-05-25 priority 调整尝试**:个人账号(boyin/siming/haomai/wenxin/刘名欣)曾被调到 37-40 优先,**已回滚到全部 50 默认值**。

下次诊断前先确认这些状态没被新的会话改动:
```bash
ssh root@10.10.102.14 'docker inspect claude-relay-service-claude-relay-1 --format "{{.Config.Image}}"'
# 应该看到 weishaw/claude-relay-service:1.1.304 或更新版本

ssh root@10.10.102.14 'docker exec claude-relay-service-claude-relay-1 sh -c "env | grep STICKY"'
# 应该看到 STICKY_SESSION_TTL_HOURS=4 / RENEWAL_THRESHOLD_MINUTES=60
```

## 团队 / 账号背景

- **6 个个人账号**:`boyin-codex`、`siming-codex`、`haomai-codex`、`wenxin-codex`、`刘名欣-codex`、(可能还有 `J02` 系列)— ChatGPT Pro 订阅,真实个人账号,基础风险分低
- **20+ 号商账号**:`jun01`~`jun20`、`Y20`、`YJ01`~`YJ19`、`haomai-xianyu-codex` — 从号商购买的 ChatGPT Pro 账号,基础风险分高,**会被 OpenAI 风控针对**
- **团队规模**:~10 人,主要用 Codex Desktop,部分用 Claude Code(走 CCR 桥接)
- **当前模式**:OAuth 反代(`openai` 账号类型),非 API key 模式

## 治本方向(还没切但应该切)

迁到 `openai-responses` 账号类型(用 OpenAI API key,不依赖 ChatGPT 订阅):
- 不会被 OAuth 吊销
- 没有 5 小时推理时间窗口
- 没有共享检测
- 现有 relay 直接支持(`src/services/scheduler/unifiedOpenAIScheduler.js:140-148` 已经有 `responses:` 前缀绑定逻辑)
- admin UI 有"添加 OpenAI Responses 账号"入口

成本估算见 [known-patterns.md](known-patterns.md) 末尾的方案对比表。
