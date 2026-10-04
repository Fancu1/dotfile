# 异步、外部系统与运行时规范

本文件规定后端项目中的异步任务、Worker、Job、Cron、后台循环、外部系统调用、重试、超时、并发、恢复以及进程生命周期。

目标是：

> 让异步处理和外部调用的责任边界清楚，
> 让失败、重试、重复执行和进程退出都有明确语义，
> 并保证读者能够理解：
> 一个请求什么时候算被接受、任务由谁执行、失败以后会发生什么、重启以后如何恢复。

本文件不规定具体队列、HTTP Client、Cron 框架或部署平台。

---

# 1. 先判断是否真的需要异步

不要因为操作“比较重要”或“以后可能变慢”就默认使用队列。

优先同步完成以下类型的工作：

- 能在一次合理请求时间内完成；
- 用户需要立即知道最终结果；
- 失败后由当前请求直接处理更清楚；
- 不需要独立重试；
- 不需要进程重启后继续执行。

例如：

```text
读取配置
查询数据库
保存简单表单
轻量业务校验
快速计算
```

通常没有必要为了架构形式进入队列。

---

以下情况更适合异步：

- 调用时间较长；
- 外部系统可能暂时失败，需要独立重试；
- 用户不需要等待最终结果；
- 请求结束后任务仍应继续；
- 需要进程重启后恢复；
- 任务存在明确的并发控制要求；
- 需要持久化执行状态；
- 一个操作可能持续数秒、数十秒甚至更久。

例如：

```text
AI 生成
大文件处理
网页抓取
批量导入
邮件发送
长时间第三方 API 操作
```

原则是：

> **异步是为了解决具体的执行问题，不是架构层级。**

---

# 2. 异步以后必须先定义“接受成功”是什么意思

异步 API 最重要的不是 Worker，而是：

> **什么时候可以向调用方承诺“这个任务已经被接受”？**

例如：

```text
POST /article-imports
```

如果返回：

```text
202 Accepted
```

应该意味着：

> 即使 HTTP 请求现在结束，系统仍然拥有足够的持久状态，
> 可以继续执行或恢复这个任务。

不能：

```text
数据库写入 pending
→ 返回 202
→ 之后才尝试入队
→ 入队失败
```

否则调用方已经得到“已接受”，系统却没有任何执行机会。

---

如果业务状态和持久任务共享数据库事务，优先：

```text
Transaction
→ 创建业务 pending 状态
→ EnqueueTx
→ Commit
→ Notify Worker
```

只有事务提交成功后，才算任务正式接受。

如果无法共享事务，则必须明确采用什么恢复机制，例如：

- Outbox；
- 恢复扫描；
- 补偿；
- 可重复提交；
- 其他明确的一致性方案。

不要因为看到异步就默认建设 Outbox。

先确认业务到底需要什么保证。

---

# 3. 区分业务状态与任务状态

业务状态和队列内部状态不是同一个概念。

例如：

```text
article_imports.status

pending
ready
failed
```

属于业务状态。

而：

```text
queued
running
retrying
completed
```

可能只是任务系统内部状态。

用户通常应该查询：

> **业务资源现在是什么状态**

而不是依赖某个队列 Task ID。

不要把：

```text
job_id
```

直接当成长期业务 API。

因为任务可能：

- 重试时创建新任务；
- 被重新领取；
- 被内部替换；
- 队列实现以后发生变化。

稳定业务状态应该有自己的业务身份。

---

# 4. Job / Queue 只负责执行机制

通用 Job / Queue 层负责：

- 持久任务；
- 入队；
- 领取；
- 分发；
- 重试调度；
- 并发限制；
- Worker 生命周期；
- 延迟任务；
- 任务恢复；
- 必要的运行指标。

Job 不负责：

- Article 是否可以改写；
- Subscription 是否可以抓取；
- Admin 是否允许创建；
- 业务状态应该变成什么；
- HTTP 应返回什么错误。

不要把业务判断写进通用队列框架。

例如不要：

```text
job.ProcessArticleImport()
job.HandleUserSubscription()
```

让 Job 层逐渐变成业务中心。

---

# 5. Task 表达稳定的执行请求

每种持久任务应该有明确的 Task 类型。

例如：

```go
type ImportArticle struct {
    UserID   int64
    ImportID int64
    Revision int64
}
```

并拥有稳定 Kind，例如：

```text
import_article
```

Task 应只携带执行任务所必需的稳定身份和必要参数。

优先传：

```text
ArticleID
ImportID
UserID
Revision
RequestKey
```

而不是把完整业务对象复制到 Task 中。

原因是：

> 任务真正执行时，应重新读取当前业务状态，
> 而不是盲目信任几分钟前入队时复制出来的数据。

---

# 6. Task Payload 是持久契约

如果任务会持久化到数据库，Task 的：

- Kind；
- JSON 字段；
- 字段类型；
- 字段语义；

就是持久数据契约。

不要随意：

```text
重命名字段
删除字段
改变 Kind
改变字段语义
```

否则旧任务可能无法恢复。

需要变化时，应考虑：

- 向后兼容；
- 新 Kind；
- Payload 版本；
- 迁移已有任务；
- 明确清理旧任务。

不能只保证：

> 当前代码新创建的任务能执行。

还要考虑：

> 升级前已经排队的任务怎么办。

---

# 7. Worker 是执行流程入口，不是业务状态拥有者

Worker 负责：

- 接收 Task；
- 读取当前业务状态；
- 调用外部 Client / AI；
- 调用业务 Service 应用结果；
- 分类执行错误；
- 将结果返回给 Job。

典型流程：

```text
Worker.HandleImport

1. ArticleService.GetPendingImport(...)
2. sourceClient.FetchArticle(...)
3. ArticleService.CreateArticleFromImport(...)
4. return success
```

Worker 可以编排：

```text
Service
Client / Connector
AI Adapter
```

但不应直接绕过 Service：

```text
Worker
→ repo.UpdateArticleStatus(...)
→ repo.CreateContent(...)
```

否则业务状态修改规则会分散到 Worker。

原则是：

> **Worker 负责执行一条后台流程，
> Service 负责业务判断和业务状态变化。**

---

# 8. Worker 不复制同步业务规则

如果同一业务行为既可能从：

```text
HTTP
```

触发，也可能从：

```text
Worker
```

触发，不应分别实现两套业务逻辑。

例如：

```text
API
→ ArticleService.StartImport

Worker
→ ArticleService.CreateArticleFromImport
```

Service 是业务能力。

API 和 Worker 是不同入口。

不要：

```text
API 校验一套
Worker 再复制一套
```

容易随着时间产生不同业务行为。

---

# 9. 外部系统通过 Client / Connector / Adapter 隔离

对第三方 HTTP API、RSS、文件服务、支付、邮件、AI 等外部能力，建立明确的外部适配边界。

项目可以根据现有命名采用：

```text
Client
Connector
Adapter
Gateway
```

但职责应清楚。

它负责：

- 外部协议；
- HTTP / RPC；
- 序列化；
- 第三方认证；
- 第三方错误识别；
- 超时；
- 必要的协议级重试信息；
- 将外部响应转换为内部明确结果。

它不负责：

- 修改业务数据库；
- 决定业务状态；
- 入队业务任务；
- 决定当前用户能否执行业务；
- 返回 HTTP API 状态码。

---

例如：

```text
sourceClient.FetchArticle(url)
```

负责：

```text
访问 URL
→ 校验响应
→ 提取正文
→ 返回 ArticleContent
```

不负责：

```text
创建 Article
更新 Import
改变用户状态
```

这些属于业务 Service。

---

# 10. 外部结果先转换成内部类型

不要让第三方 SDK 的 Response 类型直接穿透整个项目。

例如：

```text
OpenAI SDK Response
Stripe Charge
GitHub API Response
```

不应该成为 Service 或 Repository 的核心业务类型。

外部边界应转换为内部明确结果：

```go
type ArticleContent struct {
    Title string
    Text  string
}
```

这样：

- 第三方 SDK 可以替换；
- 业务层不依赖第三方字段；
- 测试更容易；
- 外部协议变化不会扩散到整个项目。

---

# 11. 外部调用不得放进数据库事务

数据库事务内不得等待：

- HTTP；
- RPC；
- AI；
- 文件解析；
- 用户输入；
- 第三方系统；
- 长时间 CPU 工作。

错误：

```text
Transaction
→ 创建记录
→ 调用 AI，等待 30 秒
→ 保存结果
→ Commit
```

正确方向：

```text
事务 1
→ 保存 pending + Task
→ Commit

Worker
→ 调用 AI / 外部系统

事务 2
→ 条件保存结果
→ Commit
```

或者：

```text
事务外
→ 获取外部结果

事务内
→ 快速校验当前状态
→ 保存结果
```

数据库事务应该：

> **短、确定、只包含本数据库能够控制的操作。**

---

# 12. 每次外部调用必须有超时

不能依赖：

> 系统默认超时。

每个外部调用都必须存在合理时间边界。

例如：

```text
HTTP Request Timeout
AI Request Timeout
Feed Fetch Timeout
File Parse Timeout
```

不同阶段可以使用不同预算。

同时要区分：

```text
单次外部调用超时
任务整体执行超时
HTTP 请求超时
进程关闭预算
```

它们不是一个概念。

例如：

```text
HTTP 请求最多等待 3 秒完成受理

后台任务总预算 60 秒

其中外部网页请求最多 20 秒
```

不要简单使用一个：

```text
context.WithTimeout(..., 60*time.Second)
```

覆盖所有不同生命周期。

---

# 13. Context 必须表达真正的生命周期

需要 Context 的 Go 函数遵循 `go.md`。

核心原则：

> Context 属于一次操作，而不是全局对象。

HTTP 请求中的同步操作应继承：

```text
request.Context()
```

如果任务在 HTTP 请求结束后仍应该继续，则不能继续依赖该 HTTP Context。

正确：

```text
HTTP
→ 持久接受任务
→ 请求结束

Worker
→ 使用任务自己的 Context
```

错误：

```text
HTTP request.Context
↓
启动后台 goroutine
↓
浏览器关闭
↓
任务被意外取消
```

---

# 14. 不随意使用 context.Background()

不能为了让任务“不被取消”：

```go
context.Background()
```

到处切断上游 Context。

如果一个工作需要独立生命周期，应由：

- Worker；
- Service runtime；
- Scheduler；
- Application；

明确拥有它的 Context。

Context 的所有者必须能回答：

> 谁创建它？
> 谁取消它？
> 谁等待这个工作结束？

---

# 15. 重试之前必须先分类错误

不是所有失败都应该重试。

至少区分：

## 临时错误

例如：

- 网络暂时不可用；
- 连接重置；
- 超时；
- 429；
- 第三方 5xx；
- 临时服务不可用。

通常允许有限重试。

---

## 永久错误

例如：

- 非法 URL；
- 请求参数错误；
- 不支持的文件；
- 第三方明确返回资源不存在；
- 内容本身无法解析。

通常不重试。

---

## 配置错误

例如：

- API Key 缺失；
- 模型配置错误；
- 必要依赖未安装。

通常不应该快速重复重试。

---

## 业务拒绝

例如：

```text
资源已经被删除
旧 revision
状态已经不是 pending
```

这通常不是系统错误。

可能直接：

```text
正常结束任务
```

而不是记录成三次失败。

---

# 16. Job 负责“何时重试”，业务代码负责“是否值得重试”

比较清晰的职责是：

```text
Client / Adapter
→ 识别底层错误性质

Worker / Service
→ 判断当前业务是否允许重试

Job
→ 根据策略安排下一次执行
```

例如：

```text
sourceClient
→ TemporaryError

Worker
→ job.Retryable(err)

Job
→ 2 秒后重新执行
```

不要让：

```text
Repository
```

决定网络错误应该重试几次。

也不要让每个 Worker 自己：

```go
for i := 0; i < 3; i++ {
    ...
}
```

如果已经有统一持久队列重试机制。

---

# 17. 重试必须有上限

所有自动重试必须有明确上限。

包括：

```text
最大次数
最大时间
Backoff
Deadline
```

禁止：

```text
for {
    retry()
}
```

无限重试。

重试策略应与实际任务匹配。

例如：

```text
网络暂时失败
→ 可以有限重试

AI 返回永久非法结果
→ 不要无限重新付费调用

配置缺失
→ 不要每两秒打一次失败请求
```

---

# 18. 重试必须考虑副作用

在执行重试前，必须确认：

> 上一次调用是不是可能已经成功，只是我们没收到结果？

例如：

```text
发送邮件
扣款
调用第三方创建资源
发布消息
```

网络超时并不一定表示：

> 对方没有执行。

需要根据外部系统能力设计：

- Idempotency Key；
- Stable Request ID；
- 查询已有结果；
- 去重；
- 条件写入。

不能因为：

> HTTP 返回错误

就简单重复所有外部副作用。

---

# 19. 异步任务默认按“可能重复执行”设计

除非底层系统有非常强并且已经验证的保证，否则默认：

> **任务可能至少执行一次。**

因此 Worker 应考虑：

- 同一个 Task 被重新领取；
- 进程执行一半崩溃；
- 外部调用成功但确认失败；
- Job 重试；
- 同一个业务操作被再次提交。

业务结果应尽可能幂等。

不要轻易宣称：

```text
exactly once
```

如果真正保证的是：

```text
at least once
+
业务结果幂等
```

就准确这样描述。

---

# 20. 旧任务不得覆盖新的业务状态

如果用户可以：

```text
失败后重试
重新提交
取消后重新开始
```

而旧 Worker 仍可能晚到，需要明确竞争保护。

典型方式：

```text
Task
- ResourceID
- Revision
```

完成时：

```text
UPDATE ...
WHERE id = ?
  AND revision = ?
  AND status = 'pending'
```

如果匹配不到：

```text
说明任务已经过期
→ 不写结果
→ 正常结束
```

不要让旧任务因为晚到而重新覆盖：

```text
ready
failed
canceled
new revision
```

---

# 21. Worker 执行前重新检查业务状态

持久任务可能排队很久。

因此开始执行时，应根据任务身份重新检查：

```text
资源是否还存在？
状态是否仍允许执行？
revision 是否仍然有效？
用户是否仍有权限？
依赖对象是否还有效？
```

不能认为：

> 入队时合法，所以执行时仍然合法。

例如：

```text
Worker
→ GetPendingImport(id, revision)

不是 pending / revision 已变化
→ 直接结束
```

这能够避免大量无效外部调用。

---

# 22. 外部调用完成后再次做条件写回

流程通常应是：

```text
检查任务仍有效
↓
调用外部系统
↓
得到结果
↓
进入 Service
↓
再次校验当前业务状态
↓
条件写回
```

因为在外部调用期间，业务状态可能已经变化。

不能因为调用前是：

```text
pending
```

就直接无条件：

```text
UPDATE status = ready
```

---

# 23. 取消要区分“业务取消”和“进程中断”

这两个概念不要混在一起。

## 业务取消

例如用户主动取消：

```text
status = canceled
```

意味着：

> 即使进程继续运行，旧任务也不应再产生业务结果。

---

## 进程中断

例如：

```text
服务 shutdown
context canceled
进程重启
```

可能只表示：

> 当前这次执行被中断，但业务任务仍然有效。

这种情况下通常应该：

```text
保留 pending
保留持久任务
等待重启恢复
```

而不是：

```text
MarkFailed("context canceled")
```

否则一次正常部署可能把大量有效任务标记成失败。

---

# 24. Task 超时与 Shutdown Cancel 语义分开

例如：

```text
任务单次 Deadline 到期
```

可以视为：

> 当前尝试失败，可以按重试规则处理。

而：

```text
服务正在关闭导致 Context Cancel
```

可能应该视为：

> 执行被中断，不消耗业务重试次数。

具体行为按任务业务决定，但必须明确区分。

不要把所有：

```go
context.Canceled
context.DeadlineExceeded
```

都统一归类成同一种失败。

---

# 25. 进程启动顺序必须明确

应用启动应按照依赖关系组织。

典型顺序：

```text
读取并校验配置
↓
连接数据库
↓
确认 Migration / Schema 可用
↓
构造 Repository
↓
构造 Client / Connector
↓
构造 Service
↓
创建 Job
↓
注册 Worker
↓
启动后台循环
↓
启动 HTTP Server
```

具体项目可以不同，但应该保证：

> 对外开始接收请求时，处理该请求所需的关键依赖已经准备好。

不能出现：

```text
HTTP 已经开始接请求
但 Worker 还没注册
```

导致请求成功受理却无法执行。

---

# 26. 初始化失败必须清理已经取得的资源

例如：

```text
数据库已打开
↓
Client 创建成功
↓
HTTP Listen 失败
```

应该关闭之前已经取得的资源。

不要因为初始化中途失败而留下：

- goroutine；
- 文件锁；
- Listener；
- 数据库连接；
- 临时文件。

在 Go 中优先让：

```text
run()
```

负责完整生命周期，并返回错误给：

```text
main()
```

统一决定最终退出。

---

# 27. Goroutine 必须有明确 Owner

新增 goroutine 时必须能回答：

```text
谁启动？
谁停止？
谁等待？
错误去哪？
```

禁止：

```go
go func() {
    for {
        ...
    }
}()
```

然后没有任何退出和 Wait 机制。

长期后台工作应由：

- Application；
- Worker Manager；
- Scheduler；
- Service Runtime；

明确拥有。

---

# 28. 后台循环必须支持停止和等待

例如订阅轮询：

```text
Application
→ StartSubscriptionLoop(ctx)

Shutdown
→ cancel(ctx)
→ wait loop exit
```

不能：

```text
启动 goroutine
↓
进程退出时不管它
```

长期后台循环内部也应：

- 遵循 Context；
- 避免永久阻塞；
- 对每轮工作设置合理边界；
- 正确释放 Timer / Ticker；
- 处理单项失败，而不是让整个循环悄悄退出。

---

# 29. Cron 与 Worker 不强制互相嵌套

定时执行不代表必须：

```text
Cron
→ Queue
→ Worker
```

如果定时工作：

- 本身很轻；
- 可以安全重新执行；
- 不需要持久队列重试；
- 执行时间短；

可以：

```text
Cron
→ Service
```

直接处理。

如果定时任务：

- 很重；
- 需要独立并发；
- 需要持久恢复；
- 需要任务级重试；

再考虑：

```text
Cron
→ Enqueue
→ Worker
```

不要为了“统一架构”增加没有必要的队列跳转。

---

# 30. Polling / Scheduler 状态属于业务还是运行时，要明确

例如：

```text
next_check_at
last_checked_at
last_error
```

如果这些值决定：

> 一个订阅什么时候应该再次检查，

它们属于订阅业务状态。

Service / Repository 管理它们。

而：

```text
Scheduler 每分钟扫描一次
```

属于运行机制。

不要把：

```text
每分钟 Tick
```

保存成新的业务表，仅为了驱动定时器。

---

# 31. 批量处理必须定义部分失败语义

例如：

```text
一个 Feed 发现 20 个 URL
```

需要明确：

```text
第 8 个受理失败怎么办？
前 7 个是否保留？
是否推进 next_check_at？
下次如何补剩余？
```

不能只有：

```text
for _, item := range items {
    Process(item)
}
```

而没有定义业务结果。

常见合理做法可能是：

```text
每个 item 单独幂等受理
↓
中途失败
↓
已成功的保留
↓
不推进整体检查时间
↓
下一轮重新扫描
↓
已存在 item 自动跳过
```

具体规则由业务决定。

---

# 32. 外部批量调用避免无限并发

不要：

```go
for _, item := range items {
    go process(item)
}
```

无限创建 goroutine。

根据：

- 外部系统限流；
- 数据库能力；
- CPU / 内存；
- 请求耗时；
- 当前项目规模；

设置明确的并发上限。

默认从简单、保守的并发开始。

没有性能证据时，不为了吞吐提前建立复杂 Worker Pool。

---

# 33. 外部 HTTP Client 统一管理网络策略

同一种外部访问能力不要在多个业务 Service 中各自：

```go
http.Get(...)
```

应集中管理：

- Timeout；
- Transport；
- Redirect；
- DNS；
- Proxy；
- TLS；
- 响应大小；
- User-Agent；
- 必要的连接池设置。

这样安全和资源限制只有一个实现位置。

---

# 34. 用户可控 URL 必须考虑 SSRF

只要后端接受用户输入 URL 并主动访问，就必须评估 SSRF。

至少考虑：

- 只允许必要协议；
- 拒绝 URL 中凭据；
- DNS 解析结果；
- 回环地址；
- 内网地址；
- Link-local；
- 云 Metadata 地址；
- IPv4 / IPv6；
- 每一跳 Redirect；
- DNS Rebinding；
- Proxy 行为。

不能只：

```text
检查输入字符串不是 localhost
```

然后允许网络层实际连接内网地址。

---

# 35. 每次 Redirect 都重新校验目标

第一次 URL 安全，不代表：

```text
302 Location
```

也安全。

流程应该类似：

```text
验证 URL
↓
DNS / Connect 校验
↓
请求
↓
收到 Redirect
↓
再次验证新 URL
↓
再次连接
```

不能：

```text
首个 URL 安全
→ 自动跟随任意 Redirect
```

---

# 36. 对外部响应设置大小限制

不能：

```text
io.ReadAll(response.Body)
```

无限读取未知响应。

根据业务设置：

- 原始响应上限；
- 解压后上限；
- 文件大小上限；
- JSON / XML 深度或条目数；
- 上传大小。

尤其注意：

> 压缩响应很小，不代表解压后很小。

限制应该作用于真正可能占用内存或磁盘的数据量。

---

# 37. 外部输入解析失败不能静默降级成成功

例如正文提取：

```text
HTML 获取成功
```

不代表：

```text
文章导入成功。
```

如果业务承诺：

> 成功后用户可以阅读完整正文，

那么正文为空或解析明显失败应该产生明确失败。

不要：

```text
抓到一点导航文字
→ 当文章成功保存
```

同理：

```text
AI 返回无法解析 JSON
```

不能偷偷保存空结构并返回成功。

---

# 38. 外部结果的降级行为必须有明确语义

允许降级时，必须说明：

> 哪部分失败以后，业务仍然算成功？

例如：

```text
文章正文提取成功
目录 metadata 提取失败
```

如果目录不是核心结果，可以：

```text
保存正文
+
记录 warning
```

但如果：

```text
正文提取失败
```

则不能因为标题成功读取就返回成功。

不要把：

> “尽量返回点东西”

当成通用错误策略。

---

# 39. AI / LLM 是外部系统

AI 调用遵守与其他外部系统相同的基本边界：

- 明确 Timeout；
- 明确错误分类；
- 不放数据库事务内；
- 不把模型原始结果直接当可信业务数据；
- 结构化结果需要验证；
- 失败不能伪装成功；
- 重试可能产生额外费用；
- 重复调用不能默认等价；
- 日志不能泄露敏感 Prompt / 原文 / Key。

业务 Service 或 Worker 决定：

> 这个结果是否满足业务要求。

LLM Adapter 只负责：

> 如何调用模型和解析协议。

---

# 40. AI 结果必须经过业务验收

例如要求：

> 生成五条例句。

模型返回后应验证：

```text
是不是五条？
是不是互不重复？
是不是包含目标词？
长度是否符合要求？
格式是否正确？
```

不能：

```text
模型 HTTP 200
→ 任务成功
```

HTTP 成功只表示：

> 外部调用成功。

不是：

> 业务结果有效。

---

# 41. 外部系统的 Retry-After / Rate Limit 应被正确表达

如果第三方明确提供：

```text
429
Retry-After
rate limit reset
```

Client 应能够让上层识别：

> 这是临时限流。

但不要在没有需要时自行建设复杂的全局 Rate Limiter。

只有真实存在：

- 供应商配额；
- 高并发；
- 明确 QPS 限制；

时，再增加对应机制。

---

# 42. Circuit Breaker 不是默认配置

不要看到外部系统就自动加入：

```text
Circuit Breaker
Bulkhead
Fallback
```

这些机制只在存在实际故障模式和收益时使用。

小型系统通常：

```text
Timeout
+
有限重试
+
并发上限
+
明确失败
```

已经足够。

不要为了“高可用”提前建设复杂运行框架。

---

# 43. 配置集中读取和校验

运行时配置应在应用入口集中：

```text
读取
→ 默认值
→ 校验
→ 转成 Config
→ 显式传入需要的模块
```

业务模块不要各自：

```go
os.Getenv(...)
```

否则难以知道真正运行配置。

配置错误应尽量在启动阶段暴露。

例如：

```text
RSS_CHECK_INTERVAL <= 0
→ 启动失败
```

而不是运行数小时后后台循环才异常。

---

# 44. 配置值与业务默认值不要混淆

例如：

```text
HTTP timeout
Worker concurrency
RSS polling interval
```

属于运行配置。

而：

```text
新用户默认英语等级
订单初始状态
业务最大选择数量
```

可能属于业务规则。

不要因为都能写成数字就统一放环境变量。

运行环境配置与业务规则应有明确边界。

---

# 45. Graceful Shutdown 必须定义顺序

有 HTTP、后台 Worker 和长期循环的程序，应定义关闭顺序。

典型：

```text
收到退出信号
↓
停止接受新的 HTTP 请求
↓
等待 / 取消在途 HTTP
↓
停止 Scheduler / Cron 接受新工作
↓
取消并等待后台循环
↓
停止 Worker 领取新任务
↓
处理或中断在途任务
↓
关闭 Queue
↓
关闭数据库和其他资源
↓
进程退出
```

具体顺序取决于依赖关系。

原则：

> **不能先关闭数据库，再要求 Worker 保存结果。**

---

# 46. Shutdown 必须有时间预算

Graceful Shutdown 不能无限等待。

应该有：

```text
正常等待预算
↓
超过以后取消在途工作
↓
给清理动作有限时间
↓
最终退出
```

例如：

```text
15 秒正常结束
+
5 秒强制清理
```

具体数值根据项目实际确定。

不要虚构“所有任务一定能在关闭前完成”。

持久任务应该能够在重启后恢复。

---

# 47. 强制退出不能伪报任务完成

如果任务在：

```text
写结果之前
```

被强制终止，就不能在 Shutdown 路径里：

```text
MarkSuccess()
```

只是为了清理状态。

持久任务恢复机制应该决定：

> 下次是否重新执行。

业务状态应该保持真实。

---

# 48. 启动恢复必须设计

对于持久任务，进程重启后应该明确：

```text
未领取任务怎么办？
正在执行时进程崩溃的任务怎么办？
超过 Lease 的任务什么时候重新可用？
```

这些应该由队列机制负责。

业务代码只需要确保：

> 再次执行不会破坏结果。

如果队列本身不能自动恢复，应有明确恢复扫描或启动补偿。

不能默认：

> 服务重启以后任务自然就会继续。

---

# 49. In-Memory 后台任务不能伪装成可靠异步

例如：

```go
go sendEmail()
```

只适合：

- 丢失也可以接受；
- 生命周期非常短；
- 没有持久恢复要求。

如果 API 已经向用户承诺：

> 任务已经被可靠接受，

就不能只存在进程内存。

进程重启会丢失的工作，应明确为：

> best effort

或者使用持久任务机制。

---

# 50. Health 与 Readiness 分开考虑

Health 表示：

> 进程还活着。

Readiness 表示：

> 当前是否具备处理请求的关键条件。

例如：

```text
数据库完全不可用
```

可能导致：

```text
readiness = false
```

但进程仍然：

```text
health = true
```

是否需要两套检查取决于部署环境。

不要为了规范完整就机械增加 Kubernetes 风格接口。

已有单体本地应用可能一个简单 Health 就足够。

---

# 51. 日志记录“发生了什么”，不要记录所有数据

异步和外部调用日志优先记录：

- operation；
- business ID；
- task kind；
- task / request ID；
- attempt；
- duration；
- external host / provider；
- error category；
- result state。

例如：

```text
operation=article_import
import_id=123
revision=2
attempt=1
duration=1.8s
result=retryable_error
```

不要默认记录：

- Authorization；
- Cookie；
- API Key；
- 完整配置；
- 用户完整正文；
- AI 原始 Prompt；
- 第三方完整 Response。

---

# 52. 日志责任放在真正处理错误的边界

不要：

```text
Client log error
→ Service 再 log error
→ Worker 再 log error
→ Job 再 log error
```

导致同一个错误出现四遍。

底层通常：

```text
wrap / classify error
```

真正决定：

```text
retry / fail / return HTTP
```

的边界负责主要日志。

必要的 Debug 日志除外。

---

# 53. 错误必须保留上下文和错误链

外部错误向上传递时，应增加操作上下文：

```go
fmt.Errorf("fetch article %q: %w", url, err)
```

但不要在错误信息里加入：

- 密钥；
- Token；
- Cookie；
- 敏感正文。

上层需要分类时使用：

```text
errors.Is
errors.As
typed error
```

不要匹配错误字符串。

---

# 54. Observability 只建设当前真正需要的部分

如果项目已经使用 Metrics / Tracing，应保持统一。

如果当前只是个人单体项目，不要为了一个 Worker 引入完整：

```text
Prometheus
OpenTelemetry
Grafana
Jaeger
```

除非它们解决当前真实问题。

第一阶段通常：

```text
结构化日志
+
明确业务状态
+
必要运行指标
```

就已经足够定位大多数问题。

---

# 55. 运行时并发必须符合底层存储能力

不要只根据 CPU 数量提高 Worker 并发。

需要共同考虑：

- SQLite / 数据库连接；
- 外部系统限制；
- 内存；
- CPU；
- 网络；
- 锁竞争；
- API Rate Limit。

例如：

> SQLite 单文件单进程

不代表适合同时开启几十个数据库写 Worker。

增加并发前，应实际检查：

> 当前瓶颈是什么？

而不是默认：

```text
并发越高越快。
```

---

# 56. 单个慢任务不能无限阻塞整个调度器

如果后台 Scheduler 串行处理多个来源，需要确保：

```text
每一项都有 Timeout
```

否则一个慢外部源可能阻塞所有后续任务。

可以根据场景采用：

- 单项 Timeout；
- 有限并发；
- 每批数量限制；
- 下一轮继续处理。

不要为了一个慢源让整个后台循环永久停住。

---

# 57. 任务规模必须有边界

所有用户可触发的后台任务都要考虑：

```text
一次最大处理多少？
输入最大多大？
并发最多多少？
是否可能无限产生任务？
```

例如：

```text
一次最多选择 50 个词
一个 EPUB 最大 32 MiB
每轮最多处理 20 个到期订阅
```

具体数值属于项目契约。

本文件只要求：

> 对可能持续增长的任务量有明确边界。

---

# 58. 不为所有异步任务建立统一状态机

不同业务可以拥有不同的状态：

```text
pending / ready / failed

queued / processing / completed

active / paused
```

不要为了“统一任务系统”强迫所有业务共用一张：

```text
jobs_status
```

业务状态属于业务对象。

Job 只负责通用执行状态。

---

# 59. 不建立万能 BackgroundService

避免：

```text
BackgroundService
SchedulerManager
WorkerManager
AsyncManager
```

收集所有后台业务。

应该优先让：

```text
Article Import Worker
Subscription Checker
Email Worker
```

各自有明确职责。

只有共同的：

- 任务领取；
- Retry；
- Shutdown；
- Concurrency；

才下沉到通用运行机制。

---

# 60. 外部系统的接口应尽可能小

例如业务只需要：

```go
type ArticleFetcher interface {
    FetchArticle(ctx context.Context, url string) (ArticleContent, error)
}
```

不要因为第三方 Client 有 40 个方法，就把完整 SDK Interface 暴露给业务层。

接口由使用方需要定义。

这样：

- 测试更简单；
- 依赖更明确；
- 外部实现更容易替换。

---

# 61. Plan 涉及异步或外部系统时必须展示这些内容

当需求涉及异步、Worker、Cron、外部 Client 或后台循环时，Plan 至少应展示：

```text
谁产生工作
↓
什么时候算接受成功
↓
业务状态保存在哪里
↓
Task 类型和稳定 Kind
↓
谁消费
↓
执行前检查什么
↓
调用什么外部系统
↓
超时
↓
结果由哪个 Service 写回
↓
失败怎样分类
↓
哪些错误重试
↓
最大重试次数
↓
重复执行怎样保证安全
↓
进程关闭怎样处理
↓
重启怎样恢复
```

例如：

```text
文章导入

Producer
ArticleService.StartImport

接受成功
Transaction
→ CreateArticleImport(pending)
→ EnqueueTx(ImportArticle{
    UserID,
    ImportID,
    Revision,
  })
→ Commit
→ Notify Queue

Task
Kind: import_article

Consumer
ArticleImportWorker

执行
1. ArticleService.GetPendingImport(id, revision)
2. sourceClient.FetchArticle(url)
3. ArticleService.CreateArticleFromImport(...)
   Transaction
   → CreateArticle
   → CreateArticleContent
   → MarkArticleImportReady

失败
- 网络超时 / 429 / 临时 5xx
  → retryable
- 非法 URL / 无正文
  → permanent failure
- revision 已过期
  → 正常结束，不写结果

Shutdown
- 进程取消不把业务标记为 failed
- 持久任务保留，重启后重新领取
```

不要只写：

```text
增加 Worker 异步处理文章导入。
```

---

# 62. 需要用户确认的运行时决策

如果多个方案都会明显改变：

- 用户体验；
- 可靠性；
- 任务恢复能力；
- 数据一致性；
- 外部成本；
- 系统复杂度；

则按照 `plan.md` 使用：

> **推荐方案 + 选择题**

向用户确认。

例如：

```text
文章导入是否需要在浏览器关闭后继续执行？

A. 请求结束后取消导入
B. 接受后独立后台执行，浏览器关闭不影响

推荐：B

原因：
- 网页抓取可能持续数秒；
- 用户无需保持页面打开；
- 项目已有持久任务能力；
- pending 状态可以在重新打开页面后查询。

请选择 A / B。
```

普通运行时实现细节由 Agent 根据本规范自行决定。

---

# 63. 设计完成前自检

涉及异步与外部系统的设计完成后，至少检查：

## 是否真的需要异步

- 同步能否更简单完成？
- 为什么用户不能等待最终结果？
- 是否真的需要持久任务和恢复？

## 接受语义

- 什么时间点可以向调用方承诺 Accepted？
- 业务状态和 Task 是否可能一个成功、一个失败？

## 职责

- Service 是否仍拥有业务状态？
- Worker 是否只是执行流程？
- Job 是否只负责通用执行机制？
- Client 是否只负责外部协议？

## Task

- Payload 是否只携带稳定身份？
- Kind 和字段是否考虑持久兼容？
- 执行前是否重新检查业务状态？

## 重试

- 哪些错误可重试？
- 哪些错误不能重试？
- 最大次数和时间是多少？
- 外部副作用重复调用是否安全？

## 并发

- 重复消费是否安全？
- 旧任务是否可能覆盖新状态？
- UNIQUE / revision / 条件更新是否足够？

## 外部系统

- 是否有 Timeout？
- 是否限制响应大小？
- 用户 URL 是否存在 SSRF 风险？
- Redirect 是否重新验证？
- 错误和外部结果是否经过转换和校验？

## Context

- HTTP Context 是否被错误带入长期后台任务？
- 每个后台 Context 谁创建、谁取消、谁等待？

## Shutdown

- 停机顺序是否正确？
- 在途任务被取消以后是什么业务状态？
- 是否有关闭时间预算？

## Recovery

- 进程重启以后未完成任务如何恢复？
- 恢复后重复执行是否安全？

如果这些问题没有明确答案，运行时设计还没有完成。

---

# 64. 最终目标

异步与运行时设计应该做到：

```text
业务请求
↓
明确是否需要异步
↓
可靠接受
↓
持久业务状态 + Task
↓
Worker 执行
↓
外部 Client / AI
↓
Service 条件写回业务结果
↓
失败分类
↓
有限重试
↓
重复执行安全
↓
Graceful Shutdown
↓
重启可恢复
```

最终读者应该能够回答：

> 为什么这个操作需要异步？
> 什么时候算已经接受成功？
> Task 里保存什么？
> 谁执行任务？
> 谁拥有业务状态？
> 外部 API 在哪里调用？
> 超时是多少？
> 哪些失败会重试？
> 重试会不会重复产生副作用？
> 旧任务会不会覆盖新结果？
> 浏览器关闭以后任务还会不会继续？
> 服务重启以后任务怎么办？
> Shutdown 时正在执行的任务怎么办？

如果这些问题只能通过追踪 Job、Worker、Service 和 Client 的实现代码才能弄清楚，
异步和运行时设计还不够清晰。
