# API 与外部契约规范

本文件规定 Go 后端项目中 HTTP API、请求与响应 DTO、错误、状态码、异步接口、幂等及兼容性的设计方式。

目标是：

> API 表达稳定的业务能力和资源契约，
> 而不是直接暴露数据库结构、Repository CRUD 或内部任务实现。

调用方应能够仅通过 API 契约理解：

- 可以完成什么业务操作；
- 请求需要提供什么；
- 成功以后得到什么；
- 失败如何判断；
- 操作是同步还是异步；
- 重复调用会发生什么；
- 如何查询后续状态。

项目已有明确 API 风格时，保持现有一致性，不为了套用本文机械修改已有接口。

---

# 1. API 从业务能力和资源出发

设计 API 时，先问：

> 调用方想完成什么业务操作？
> 操作围绕哪个稳定资源？

不要先看数据库表，再机械生成 CRUD。

例如：

```text
article_imports 表
```

不意味着一定需要：

```text
POST   /article-imports
GET    /article-imports
PUT    /article-imports/:id
DELETE /article-imports/:id
```

真正的业务能力可能只有：

```text
POST /api/article-imports
GET  /api/article-imports/:id
```

因为业务需求只是：

```text
提交导入
→ 查询导入结果
```

API 数量由真实业务能力决定，不由表数量决定。

---

# 2. API 与 Service 的职责边界

默认调用关系：

```text
HTTP Request
→ Handler
→ Service
→ 业务结果
→ Handler
→ HTTP Response
```

Handler 负责：

- HTTP Method 和 Path；
- Path / Query 参数解析；
- JSON / Form / Multipart 解码；
- 请求大小限制；
- 协议级格式校验；
- 调用 Service；
- 将业务错误映射成 HTTP；
- 将业务结果转换成 Response DTO。

Service 负责：

- 业务规则；
- 业务校验；
- 状态判断；
- 权限与资源归属判断；
- 幂等语义；
- 事务和业务流程编排；
- 最终业务结果。

Handler 不应：

- 直接访问 Repository；
- 直接执行 SQL / GORM；
- 直接访问业务表；
- 编排多个持久化操作；
- 直接调用 AI；
- 直接提交业务任务；
- 实现业务状态机；
- 复制其他入口也必须保证的业务规则。

---

# 3. 协议校验和业务校验分开

API 层处理协议是否有效。

例如：

```text
JSON 是否合法
字段类型是否正确
必填 JSON 字段是否出现
Path ID 是否能解析
limit 是否是整数
Content-Type 是否正确
请求体是否超限
```

Service 处理业务是否允许。

例如：

```text
管理员账号是否已经存在
角色是否有效
文章是否允许改写
导入是否可以重试
当前用户是否拥有资源
状态是否允许转换
```

例如：

```text
POST /api/admins

role_ids 不是数组
→ API 拒绝

role_ids 中存在已停用角色
→ Service 拒绝
```

不能只在 Handler 做业务校验，因为 Worker、CLI 或其他入口可能绕过 HTTP。

---

# 4. HTTP DTO 与业务类型分开

HTTP Request / Response DTO 属于 API 契约。

Service 输入输出属于业务契约。

Repository Model 属于持久化契约。

三者默认不要混用。

例如：

```go
// API
type CreateAdminRequest struct {
    ADAccount string  `json:"ad_account"`
    RoleIDs   []int64 `json:"role_ids"`
}

// Service
type CreateAdminInput struct {
    ADAccount string
    RoleIDs   []int64
}

// Repository
type AdminRecord struct {
    ...
}
```

不要：

```text
Handler 直接把数据库 Model BindJSON
```

也不要：

```text
Service 返回 GORM Model 给 Handler 直接 JSON 序列化
```

否则数据库变化会意外成为外部 API 变化。

---

# 5. Request 只暴露调用方真正能控制的字段

请求 DTO 只接受用户有权决定的信息。

不要因为数据库存在某个字段，就允许客户端提交。

例如数据库存在：

```text
user_id
status
created_at
updated_at
revision
retry_count
```

不意味着创建请求可以接受：

```json
{
  "user_id": 1,
  "status": "ready",
  "revision": 7
}
```

这些字段如果由：

- 当前身份；
- Service；
- 数据库；
- Worker；
- 系统时间；

决定，就不应该交给客户端控制。

原则：

> 外部输入表达用户意图，
> 内部状态由系统决定。

---

# 6. Response 返回调用方需要的稳定信息

Response 不默认返回完整数据库记录。

返回内容应围绕：

- 调用结果；
- 稳定资源 ID；
- 当前状态；
- 后续操作需要的信息；
- 用户真正需要展示的数据。

例如异步导入：

```json
{
  "id": 123,
  "url": "https://example.com/article",
  "status": "pending",
  "revision": 1,
  "article_id": null,
  "error_code": ""
}
```

而不是暴露：

```text
queue_task_id
database_row_version
worker_attempt_count
internal_error
```

除非这些信息本身就是对外契约。

---

# 7. HTTP Method 按语义选择

## GET

读取资源，不产生业务副作用。

```text
GET /api/articles/:id
GET /api/article-imports/:id
```

GET 不应：

- 创建数据；
- 修改业务状态；
- 启动任务；
- 领取任务；
- 标记已读；
- 更新访问时间作为业务行为。

纯技术性缓存、日志等不改变业务语义的行为除外。

---

## POST

用于：

- 创建新资源；
- 发起业务操作；
- 无法天然表示为完整目标资源替换的命令。

例如：

```text
POST /api/articles
POST /api/article-imports
POST /api/articles/:id/rewrites
POST /api/sentence-reviews
```

POST 不代表可以忽略重复请求和幂等问题。

---

## PUT

用于：

> 调用方提交某个资源的完整目标表示，
> 重复提交相同内容应得到相同结果。

如果实际语义只是局部修改，不为了 REST 形式机械使用 PUT。

---

## PATCH

用于：

> 对现有资源进行明确的局部修改。

例如：

```text
PATCH /api/subscriptions/:id
{
  "enabled": false
}
```

如果项目当前统一采用其他更新方式，保持现有约定。

---

## DELETE

表示删除资源或取消其存在。

DELETE 默认设计成重复调用安全。

如果业务上是：

```text
停用
归档
撤销
```

而不是删除，应使用能表达真实业务语义的操作，不为了使用 DELETE 改变业务概念。

---

# 8. HTTP Path 表达资源，不表达内部实现

推荐：

```text
POST /api/article-imports
GET  /api/article-imports/:id
```

不推荐：

```text
POST /api/startArticleImport
GET  /api/checkImportTask
POST /api/runArticleWorker
```

Path 应表达业务资源或业务行为，而不是：

- Service 方法名；
- Worker 名；
- Repository 方法；
- 数据库表；
- 内部任务实现。

内部从同步改成异步时，理想情况下不应该因此被迫重新设计整个资源模型。

---

# 9. 同步与异步必须在契约中明确

一个操作如果在当前 HTTP 请求内可以得到最终业务结果，可以同步完成。

例如：

```text
创建设置
更新收藏
保存笔记
```

如果操作依赖：

- AI；
- 大文件处理；
- 不稳定外部网络；
- 长耗时任务；
- 后台执行；

可以设计成异步。

异步 API 必须有稳定的业务状态资源。

例如：

```text
POST /api/article-imports
→ 202 Accepted
→ 返回 article_import id

GET /api/article-imports/:id
→ pending / ready / failed
```

不要只返回：

```text
queue_task_id
```

让调用方直接依赖内部队列。

队列任务是实现细节。

业务状态资源才是外部契约。

---

# 10. 202 Accepted 的语义

返回 `202 Accepted` 表示：

> 请求已经被系统可靠接受，
> 但业务结果尚未完成。

在返回 202 前，应满足项目定义的“接受保证”。

例如：

```text
创建 pending article_import
+
持久化 import_article 任务
```

两者需要共同成功时，应在返回 202 前保证原子性。

不能：

```text
先返回 202
→ 后台再尝试创建任务
```

否则可能产生：

```text
客户端认为已接受
但服务端实际上没有任务
```

202 应同时提供稳定的状态查询方式。

推荐：

```text
Location: /api/article-imports/123
```

如果项目已有统一方式，则沿用。

---

# 11. 成功状态码的默认语义

默认遵循：

```text
200 OK
请求成功，并返回现有或更新后的结果。

201 Created
成功创建新的资源。

202 Accepted
请求已经可靠接受，但最终处理尚未完成。

204 No Content
成功完成，不需要返回响应正文。
```

例如：

```text
POST /api/admins
新建成功
→ 201
```

```text
POST /api/article-imports
新异步任务已接受
→ 202
```

```text
PUT /api/sentences/:id/favorite
成功且无需正文
→ 204
```

不要所有成功都机械返回 200。

但项目已有稳定约定时，优先保持兼容。

---

# 12. 客户端错误状态码的默认语义

常用状态码按下面语义区分。

## 400 Bad Request

请求本身非法或无法按照当前接口契约处理。

例如：

```text
JSON 非法
字段格式错误
非法 URL
参数范围错误
```

---

## 401 Unauthorized

当前请求需要身份，但没有有效身份。

不要把“没有权限访问某资源”统一写成 401。

---

## 403 Forbidden

身份已经确定，但明确没有执行该操作的权限。

如果为了避免泄露资源是否存在，项目可能统一返回 404；这种策略应由安全规范明确。

---

## 404 Not Found

目标资源不存在，或按当前安全策略对调用方不可见。

---

## 409 Conflict

请求格式本身合法，但与当前资源状态冲突。

例如：

```text
资源已经存在
当前状态不允许操作
revision 已过期
资源尚未 ready
并发状态发生变化
```

409 非常适合表达：

> “请求本身没写错，但当前业务状态不允许这样做。”

---

## 422 Unprocessable Content

请求格式合法，但内容无法满足接口定义的语义约束，并且项目选择将此类问题与 400 区分时使用。

不要为了追求状态码精细度强制引入 422。

如果项目一直使用：

```text
400 + stable error_code
```

表达业务输入错误，可以继续保持一致。

---

## 429 Too Many Requests

存在明确限流机制时使用。

---

# 13. 服务端错误状态码的默认语义

## 500 Internal Server Error

服务内部非预期失败。

不要将数据库原始错误、panic 文本或内部堆栈直接返回给客户端。

---

## 502 Bad Gateway

当前服务作为网关或代理时，上游返回了无效响应。

普通第三方调用失败不需要为了“外部服务错误”机械使用 502。

---

## 503 Service Unavailable

当前能力暂时不可用，但请求本身没有问题。

例如：

```text
任务队列暂时不可接受请求
AI Provider 未配置或暂时不可用
必要外部依赖暂时不可用
```

---

## 504 Gateway Timeout

当前请求依赖的上游操作明确超时，并且该超时需要作为当前 HTTP 契约暴露时使用。

项目已有统一外部错误映射时保持一致。

---

# 14. 业务错误必须有稳定 error code

客户端需要根据错误采取不同操作时，不能只依赖错误字符串。

推荐：

```json
{
  "error": {
    "code": "ADMIN_ALREADY_EXISTS",
    "message": "管理员已经存在"
  }
}
```

其中：

```text
code
→ 稳定、机器可识别

message
→ 面向人类，可调整文案

details
→ 必要时提供结构化补充信息
```

不要让客户端：

```text
if strings.Contains(message, "already exists")
```

判断业务状态。

---

# 15. Error Code 表达业务，不表达内部实现

推荐：

```text
ARTICLE_NOT_FOUND
ARTICLE_CONTENT_NOT_READY
ADMIN_ALREADY_EXISTS
INVALID_ROLES
IMPORT_UNAVAILABLE
```

不推荐：

```text
SQLITE_CONSTRAINT_FAILED
GORM_RECORD_NOT_FOUND
BACKLITE_INSERT_FAILED
EOF_FROM_PROVIDER
```

底层错误应在对应边界转换成业务错误。

内部日志可以记录底层原因。

外部契约暴露调用方真正需要理解的业务结果。

---

# 16. 相同业务错误应保持一致

同一种业务状态通过不同 HTTP 入口访问时，应尽量使用相同错误语义。

例如：

```text
Article 不存在
```

不要一个接口返回：

```text
ARTICLE_NOT_FOUND
```

另一个接口返回：

```text
RESOURCE_MISSING
```

如果它们表达的是同一业务事实，应保持一致。

但不同 Use Case 下语义确实不同，可以使用不同错误。

不要为了错误码复用而丢失业务含义。

---

# 17. Error Mapping 放在 API 边界

Service 返回业务错误：

```text
ErrAdminExists
ErrInvalidRoles
ErrArticleNotReady
ErrStaleRevision
```

Handler 或本业务 API 包负责映射：

```text
ErrAdminExists
→ 409 ADMIN_ALREADY_EXISTS

ErrInvalidRoles
→ 400 INVALID_ROLES
```

Repository 不决定 HTTP 状态码。

Service 也不需要返回：

```text
http.StatusConflict
```

HTTP 属于 API 边界。

---

# 18. 不把内部错误直接返回给客户端

禁止直接返回：

```text
UNIQUE constraint failed: admins.ad_account
database is locked
context deadline exceeded while calling xxx
provider response: ...
```

应该转换成稳定的外部语义。

内部日志根据安全要求记录：

- 操作；
- 资源 ID；
- 错误类别；
- 必要底层原因。

不能把：

- 密钥；
- Cookie；
- Authorization；
- 数据库 DSN；
- 敏感业务内容；

写进外部错误。

---

# 19. 重复请求必须定义语义

任何可能被客户端重复提交的写接口，都应该回答：

> 同样的请求再次发送，会发生什么？

常见方案：

### 返回已有结果

例如：

```text
POST /api/article-imports
同用户同 URL 已 ready
→ 返回已有 import / article
```

### 幂等更新

例如：

```text
PUT /api/sentences/:id/favorite
重复收藏
→ 仍然成功
```

### 明确冲突

例如：

```text
POST /api/admins
相同 ad_account 已存在
→ 409 ADMIN_ALREADY_EXISTS
```

不能完全忽略重复调用，依赖“正常情况下前端不会点两次”。

---

# 20. POST 是否需要幂等键按业务风险决定

不是所有 POST 都必须引入 Idempotency-Key。

如果已有自然业务唯一键，例如：

```text
user_id + url
ad_account
external_order_id
```

可以基于业务唯一性实现幂等或冲突语义。

如果：

- 请求可能因网络重试重复；
- 创建操作没有自然唯一键；
- 重复执行会产生严重副作用；

再考虑显式幂等键。

不要为了“最佳实践”给所有 POST 加幂等表和 request key。

---

# 21. 并发正确性不能只靠 API 预检查

例如：

```text
GET 不存在
→ POST 创建
```

两个请求可以同时通过预检查。

因此：

```text
Service 业务判断
+
数据库唯一约束 / 条件更新
```

需要共同保证结果。

API 对外仍应返回稳定业务错误，例如：

```text
409 ADMIN_ALREADY_EXISTS
```

而不是把数据库唯一约束错误原样暴露。

---

# 22. 状态字段应表达稳定业务状态

对外状态应该是调用方真正需要理解的业务状态。

例如：

```text
pending
ready
failed
```

不要暴露内部执行状态：

```text
queued
leased
retry_wait
worker_running
attempt_2
```

除非产品确实需要这些状态。

内部任务状态可以比外部业务状态更复杂。

API 不应把内部队列状态直接当作业务状态机。

---

# 23. 状态转换由 Service 控制

如果 API 接受：

```text
PATCH /resource/:id
{
  "status": "approved"
}
```

应谨慎检查：

> 客户端是否真的应该直接指定目标状态？

很多情况下更合适的是业务动作：

```text
POST /approvals/:id/approve
POST /approvals/:id/reject
```

因为：

```text
approve
```

可能意味着：

- 校验权限；
- 校验当前状态；
- 写审批记录；
- 写事件；
- 通知其他模块。

不要把复杂业务行为伪装成普通字段更新。

具体业务编排遵循 `usecase.md`。

---

# 24. 创建资源后返回稳定资源标识

创建成功时，应返回后续操作需要的稳定 ID。

例如：

```json
{
  "id": 123
}
```

不要让调用方依赖：

- 数据库内部 RowID 偶然行为；
- Queue ID；
- 临时文件路径；
- Worker 执行 ID；

除非它们就是正式资源 ID。

---

# 25. 分页默认采用稳定排序

列表 API 必须定义：

- 排序字段；
- 排序方向；
- page size；
- cursor / offset 语义；
- 最大 limit。

对持续增长的业务数据，优先考虑稳定 cursor。

例如：

```text
GET /api/articles?limit=20&before_id=100

ORDER BY id DESC
WHERE id < 100
LIMIT 20
```

不要只写：

```text
支持分页
```

而不定义排序。

没有稳定排序，就没有可靠分页。

---

# 26. Cursor 应来自稳定字段

适合：

```text
id
created_at + id
稳定业务序列
```

不适合：

```text
数组下标
当前页面位置
不稳定计算值
```

如果使用时间作为 Cursor，并且时间可能重复，应增加稳定的次级排序字段。

---

# 27. 列表和详情不必返回同样内容

列表接口应该返回：

> 列表展示和定位需要的信息。

详情接口返回：

> 当前资源完整业务信息。

不要为了代码复用，让列表加载：

- 大正文；
- 大 JSON；
- 大量关联对象；
- 二进制内容；

然后客户端再丢弃。

例如：

```text
GET /articles
→ ArticleSummary[]

GET /articles/:id
→ ArticleDetail
```

这是合理的两个 Response DTO。

---

# 28. 空结果与不存在要区分

列表没有数据：

```text
200
[]
```

而不是：

```text
404
```

查询单个资源不存在：

```text
404
```

可空业务结果，例如：

```text
当前没有进行中的 review batch
```

如果这是正常业务状态，可以：

```text
200
data: null
```

不要把正常“没有结果”伪装成服务器错误。

---

# 29. Optional、Null 和空值必须有明确语义

对于每一个可空字段，应明确：

```text
字段不存在
null
""
[]
0
```

分别意味着什么。

不要让客户端猜。

例如：

```text
source_url = null
→ 手工粘贴文章，没有来源 URL

words = []
→ 当前生成文章没有选词

note = ""
→ 当前没有笔记
```

如果这些差异有业务意义，应写入 API 契约和测试。

---

# 30. 时间字段必须明确语义

时间字段应说明：

- 表示什么事件；
- 时区；
- 是否可空；
- 精度要求。

外部 API 默认推荐使用明确时区的标准时间格式，例如 RFC3339。

不要让：

```text
created_at
finished_at
next_run_at
```

出现本地时间、UTC、无时区字符串混用。

具体项目约定优先。

---

# 31. ID 类型保持一致

同一类资源的 ID 在：

- Path；
- Query；
- Request；
- Response；

中保持一致类型。

不要：

```text
Path 是 int
Response 是 string
Request 又是 float
```

除非存在明确兼容原因。

不要把数据库内部主键类型随意暴露成长期公共协议；项目内部 API 可以结合实际规模选择，但一旦成为契约就保持稳定。

---

# 32. JSON 字段命名保持项目一致

新接口沿用项目已有 JSON 命名方式。

不要同一个项目同时出现：

```text
user_id
userId
UserID
```

如果项目没有约定，应先建立统一风格，再批量使用。

不要为了个人偏好单独改变某一个接口。

---

# 33. 请求默认拒绝意外字段

对于业务 API，推荐严格解析请求。

例如客户端提交：

```json
{
  "ad_account": "alice",
  "rolse": [1, 2]
}
```

其中 `rolse` 是拼写错误。

如果服务端静默忽略，调用方可能认为角色已经设置。

因此默认应考虑：

> 拒绝未知字段。

但兼容已有第三方客户端、Webhook 或开放协议时，需要根据实际协议决定。

---

# 34. 请求体应有限制

所有外部输入都应有与业务场景相符的大小限制。

例如：

```text
普通 JSON
上传文件
Webhook
文章正文
批量请求
```

不能无限读取请求体。

具体大小属于项目配置或安全契约，不在通用规范里虚构固定值。

---

# 35. 文件上传使用正确协议

文件上传默认使用：

```text
multipart/form-data
```

不要：

- Base64 塞进普通 JSON，除非业务确实需要；
- 手动伪造 multipart boundary；
- 把本地文件路径作为远程 API 输入。

上传接口应明确：

- 文件字段名；
- 数量；
- 大小；
- 支持格式；
- 同步还是异步；
- 失败后是否留下状态资源。

---

# 36. 文件和二进制下载不强制套 JSON Envelope

普通 JSON API 可以统一：

```json
{
  "data": ...
}
```

但：

- 图片；
- 文件；
- 流式下载；
- 204；

不需要为了形式套 JSON。

例如：

```text
GET /books/:bookID/assets/:assetID
→ image/png
```

应直接返回正确 Content-Type。

---

# 37. Response Envelope 保持项目一致

如果项目采用：

```json
{
  "data": ...
}
```

以及：

```json
{
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

新接口继续沿用。

如果项目没有统一 Envelope，不为了本规范立即全量引入。

API 一致性比个人偏好重要。

---

# 38. Location 用于指向新资源或状态资源

创建资源后，适合时可以返回：

```text
Location
```

例如：

```text
POST /api/article-imports
→ Location: /api/article-imports/123
```

或者：

```text
POST /api/admins
→ Location: /api/admins/456
```

不强制每个创建接口都必须使用。

但异步 202 有稳定状态资源时，优先考虑提供。

---

# 39. API 不暴露内部任务实现

禁止把：

```text
job table
worker attempt
queue lease
retry row
internal task kind
```

直接作为主要业务查询协议。

例如不要：

```text
GET /api/jobs/:task_id
```

来查询“文章是否导入成功”，如果用户真正关心的是：

```text
ArticleImport
```

应该：

```text
GET /api/article-imports/:id
```

内部 Job 可以替换。

业务资源应该保持稳定。

---

# 40. API 不暴露数据库结构

不要因为 Repository 返回：

```text
ArticleRecord
```

就自动把所有字段输出。

例如数据库可能存在：

```text
internal_revision
deleted_at
raw_provider_response
owner_id
migration_flag
```

这些字段如果不是外部契约，就不应该出现在 Response。

API 是业务边界，不是数据库调试接口。

---

# 41. 资源归属必须在业务入口保证

当前请求操作资源时，需要明确：

> 谁拥有这个资源？

例如：

```text
GET /articles/:id
```

不能只是：

```text
SELECT * FROM articles WHERE id = ?
```

如果系统存在用户或租户，应通过当前身份保证归属。

客户端提交：

```text
user_id
tenant_id
owner_id
```

不能自动被视为可信身份。

---

# 42. 不从 Response 推断不存在的能力

接口只承诺明确返回的信息。

例如 Response 包含：

```text
status = ready
```

不意味着：

```text
已经阅读
已经掌握
已经审核
已经同步给第三方
```

除非这些语义明确属于该状态。

状态名必须避免承载超出真实业务的隐含意义。

---

# 43. 兼容性优先于“更漂亮”的设计

已经被调用的 API 是外部契约。

重构内部代码时，默认保持：

- Path；
- Method；
- Request 字段；
- Response 字段；
- 状态码；
- Error Code；
- 同步 / 异步语义；
- 幂等行为。

不要借内部重构：

```text
顺手改字段名
顺手改状态码
顺手合并接口
顺手改变 null 语义
```

需要改变时，应作为明确 API 变更设计，并在 Plan 中说明影响。

---

# 44. 新字段默认考虑向后兼容

Response 新增字段通常比：

```text
删除字段
改字段类型
改变字段语义
```

更容易兼容。

Request 新增必填字段会破坏旧调用方。

如果必须引入，应该明确：

- 默认值；
- 迁移方案；
- 版本策略；
- 调用方同步修改。

不要默默改变已有客户端必须提供的信息。

---

# 45. 删除和重命名契约必须显式处理

不要直接：

```text
rename JSON field
remove endpoint
change enum value
```

然后只修改当前前端。

即使当前仓库只有一个前端，也要先确认：

> 是否存在其他调用者或持久客户端数据？

如果确定 API 只服务同仓库客户端，也可以同步修改，但仍要在 Plan 明确这是契约变更。

---

# 46. API Versioning 按真实需要引入

不要一开始就机械创建：

```text
/api/v1/
```

如果项目当前：

- 单客户端；
- 快速迭代；
- 前后端同步发布；

可能不需要版本化。

出现：

- 外部第三方客户端；
- 多版本长期并存；
- 无法同步升级；

等真实需要时，再设计版本策略。

---

# 47. 批量接口应有独立业务语义

不要为了减少 HTTP 请求就随意增加：

```text
POST /batch
```

批量操作应明确：

- 单条失败是否影响其他条；
- 是否整体事务；
- 返回每项状态还是整体状态；
- 最大数量；
- 重复输入如何处理。

例如：

```text
OPML 导入多个订阅
```

可能适合：

```text
每个源独立得到：
created / existed / failed
```

而不是假装全部操作是一个简单 CRUD。

---

# 48. API 设计不要提前暴露未来能力

不要为了“以后可能用到”提前增加：

```text
sort
filter
include
expand
fields
dry_run
force
mode
strategy
options
```

如果当前没有真实需求，就先不提供。

外部契约一旦暴露，比内部代码更难删除。

API 应比内部实现更克制。

---

# 49. Handler 文件按资源和职责组织

一个业务 API 包通常可以包含：

```text
internal/api/admin/
├── handler.go
├── request.go
├── response.go
└── errors.go    # 确有需要时
```

但不要求机械创建所有文件。

规模很小时可以合并。

增长后按：

```text
请求
响应
Handler
错误映射
```

等实际职责拆分。

不要：

```text
一个 endpoint 一个 package
```

也不要建立一个包含所有业务 API 的万能 Handler。

具体包划分遵循 `architecture.md`。

---

# 50. Handler 应保持容易顺读

典型 Handler 应接近：

```go
func (h *Handler) CreateAdmin(w http.ResponseWriter, r *http.Request) {
    var req CreateAdminRequest
    if err := decodeJSON(r, &req); err != nil {
        writeError(...)
        return
    }

    result, err := h.admins.CreateAdmin(
        r.Context(),
        toCreateAdminInput(req),
    )
    if err != nil {
        writeAdminError(w, err)
        return
    }

    writeJSON(w, http.StatusCreated, toAdminResponse(result))
}
```

读 Handler 应主要看见：

```text
解析
→ 调 Service
→ 映射错误
→ 返回
```

如果 Handler 里出现大量：

```text
数据库查询
状态判断
事务
任务提交
业务计算
```

应检查职责是否放错。

---

# 51. 公共 HTTP 工具只抽取真正共享的协议机制

适合公共化：

```text
严格 JSON 解码
统一 Response Envelope
Path ID 解析
通用请求体限制
基础错误输出
```

不适合为了“复用”放入公共层：

```text
article query 默认值
review batch 规则
subscription 状态
业务错误判断
```

业务协议仍留在对应 API 包。

不要建立庞大的：

```text
BaseHandler
BaseController
GenericCRUDHandler
```

除非项目真实需要。

---

# 52. API 注释描述契约，而不是重复路由

对于 Request / Response / Handler 等导出声明，注释遵循 `go.md`。

注释重点说明：

- 特殊输入语义；
- 空值含义；
- 状态；
- 副作用；
- 失败行为。

不要只写：

```go
// CreateAdmin 创建管理员。
```

如果真正重要的是：

```text
重复账号返回冲突
创建成功同时写审计
```

这些调用者必须知道的契约应体现在：

- 类型；
- API 文档；
- 测试；
- 必要注释；

中的合适位置。

---

# 53. Plan 中如何描述 API

使用 Codex Plan 模式时，与 `plan.md` 配合。

Plan 中一个重要 API 至少说明：

```text
POST /api/article-imports

用途
提交文章链接并受理异步导入。

Request
{
  "url": string
}

Success

新请求
→ 202
→ ArticleImport(status=pending)

已有 pending
→ 202
→ 返回已有 ArticleImport

已有 ready
→ 200
→ 返回已有 ArticleImport + article_id

Errors

非法 URL
→ 400 ARTICLE_IMPORT_INVALID_URL

任务无法接受
→ 503 ARTICLE_IMPORT_UNAVAILABLE

状态查询

GET /api/article-imports/:id
```

不要只写：

```text
新增文章导入接口。
```

Plan 应让用户在开发前知道接口准备承诺什么。

---

# 54. 新增 API 时的检查清单

设计新 API 时至少检查：

## 业务

- 调用方真正想完成什么？
- 这是资源还是业务命令？
- 是否已经存在可以复用的 API？

## Request

- 客户端真正应该控制哪些字段？
- 哪些状态应由系统决定？
- Optional / Null / Empty 的语义是否明确？

## Response

- 调用方下一步需要什么？
- 有没有暴露数据库或任务实现？
- 列表和详情是否需要不同 DTO？

## HTTP

- Method 是否符合真实语义？
- 成功状态码是否准确？
- 错误状态码是否与项目一致？
- Error Code 是否稳定？

## 重复调用

- 重复请求如何处理？
- 是否有自然业务唯一键？
- 是否需要额外幂等机制？

## 异步

- 什么时间点算已经接受？
- 状态在哪里查询？
- 是否错误地暴露 Queue Task？

## 安全

- 资源归属由谁保证？
- 客户端是否能够伪造 user_id / owner_id？
- 是否暴露内部错误或敏感信息？

## 兼容

- 是否改变已有字段、状态码或空值语义？
- 当前调用方是否需要同步修改？

如果这些问题还没有答案，API 契约还没有设计完成。

---

# 55. 最终判断标准

一个良好的 API 应做到：

> 调用方理解业务资源和结果，
> 不需要理解数据库、Service、Worker 或 Queue 的内部实现。

同时：

> Handler 足够薄，
> Service 保持业务负责人，
> DTO 与数据库解耦，
> 错误和状态稳定，
> 重复调用有明确语义，
> 异步操作有稳定的业务状态资源。

最终目标是：

```text
HTTP 负责表达协议
Service 负责表达业务
Repository 负责表达持久化
Worker / Job 负责表达执行机制
```

各层可以协作，但不能让内部实现细节泄漏成不必要的外部契约。
