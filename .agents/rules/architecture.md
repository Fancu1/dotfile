# 架构与模块边界规范

本文件规定 Go 后端项目中模块如何划分、职责如何归属、模块之间如何依赖和调用。

目标是：

> 一个新需求出现时，Agent 能够判断代码应该放在哪里；
> 一个模块可以用一句话说明自己负责什么；
> 从业务入口能够顺着清晰的调用方向理解实现；
> 不因为功能增加就不断创建新的包、层和抽象。

本文件只规定架构和模块边界。

---

# 1. 基本原则

模块优先按照：

> **业务职责**

划分，而不是按照：

- 数据表；
- API 数量；
- 文件数量；
- 技术动作；
- CRUD 操作；
- 代码行数；

机械拆分。

一个模块应该能够用一句话说明：

> 它拥有哪一类业务规则和结果。

例如：

```text
article
负责文章创建、导入、正文版本和阅读状态。

subscription
负责用户订阅、订阅源状态和更新规则。
```

而不是：

```text
article_creator
article_loader
article_manager
article_processor
```

如果几个能力围绕同一个业务对象、共享同一组规则和依赖，并且通常一起变化，应优先属于同一个业务模块。

---

# 2. 默认后端结构

对于采用分层组织的 Go HTTP 后端，默认职责如下：

```text
cmd
│
├── api
│     ↓
├── service
│     ↓
├── repository
│
├── worker
├── job
├── integrations / client
└── domain-specific utilities
```

这不是要求所有项目必须具有所有目录。

只在真实存在对应职责时创建。

---

# 3. API / Handler

API 层负责协议边界。

包括：

- 路由；
- HTTP Method / Path；
- 请求解析；
- Path / Query 参数解析；
- 请求 DTO；
- 基础协议格式校验；
- 调用 Service；
- 将业务结果映射为 HTTP Response；
- 将业务错误映射为状态码和错误结构。

API 不负责：

- 完整业务流程；
- 数据库读写；
- 事务；
- 调用 Repository；
- 调用 AI；
- 调用任务队列；
- 编排多个业务模块；
- 直接访问外部系统。

默认调用：

```text
Handler
→ Service
```

而不是：

```text
Handler
→ Repository
```

或：

```text
Handler
→ Repository
→ Queue
→ Client
```

如果 Handler 中已经需要理解多个业务步骤，通常说明业务逻辑放错了位置。

---

# 4. Service

Service 是业务能力的主要负责人，也是业务代码的主要阅读入口。

Service 负责：

- 业务规则；
- 输入的业务校验；
- 当前状态判断；
- Use Case 编排；
- 数据变化顺序；
- 多项持久化操作的业务事务范围；
- 跨模块业务协作；
- 对外部结果进行业务验收；
- 决定业务错误。

从一个核心 Service 方法中，应该能够理解：

> 这个业务为什么执行、按什么顺序执行、最后产生什么结果。

Service 不负责：

- HTTP 协议；
- SQL / GORM 等数据库实现细节；
- 队列底层调度；
- 外部协议解析细节；
- 进程生命周期。

默认：

```text
API
→ Service
→ Repository
```

异步场景中：

```text
Worker
→ Service
→ Repository
```

---

# 5. Repository

Repository 负责持久化能力，而不是业务流程。

Repository 可以负责：

- 查询；
- 插入；
- 更新；
- 删除；
- 条件更新；
- 唯一约束对应的数据操作；
- 批量数据操作；
- 数据库事务机制；
- 数据库错误识别；
- 持久化模型映射。

Repository 不负责：

- 决定业务流程；
- HTTP 状态码；
- 调用 Service；
- 调用外部系统；
- 调用 AI；
- 启动异步任务；
- 决定任务重试；
- 隐藏与方法名称无关的业务副作用。

例如：

```text
CreateArticle
CreateArticleContent
MarkImportReady
```

职责明确。

应谨慎使用：

```text
CompleteImport
ProcessArticle
HandleResult
SaveEverything
```

如果一个 Repository 方法内部会修改多个业务对象，应确认：

> 这些修改是否真的属于一个不可再分的持久化操作，
> 还是把原本应该由 Service 展示的业务步骤隐藏起来了。

“一项 Repository 操作”不等于“一条 SQL”。

为了完成一个明确的数据操作，可以执行多条 SQL。

---

# 6. Worker

Worker 是异步 Use Case 的执行入口和流程协调者。

典型流程：

```text
Job
→ Worker
→ Service / Client / AI
→ Service
→ Repository
```

Worker 可以负责：

- 接收任务；
- 根据任务调用相关能力；
- 调用外部 Client；
- 调用 AI；
- 将外部结果交给业务 Service；
- 对错误进行执行层分类；
- 判断任务应该成功、失败还是重试。

Worker 不应该：

- 直接修改业务数据表；
- 自己实现另一套业务规则；
- 绕过业务 Service 更新业务状态；
- 将 Service 的业务逻辑复制一份。

例如：

```text
Worker
→ SourceClient.FetchArticle
→ ArticleService.CreateArticleFromImport
```

优于：

```text
Worker
→ Repository.CreateArticle
→ Repository.CreateContent
→ Repository.UpdateImport
```

业务状态变化仍由业务负责人控制。

---

# 7. Job / Queue

Job 或 Queue 是异步基础设施。

负责：

- 持久化任务；
- 任务注册；
- 调度；
- 获取任务；
- 重试机制；
- 并发执行控制；
- Worker 生命周期；
- 队列自身状态。

Job 不拥有业务规则。

Job 不应该依赖：

- 具体业务 Service；
- 业务 Repository；
- AI；
- 外部业务 Client。

业务任务参数可以放在独立的 task / job type 包中：

```text
job/task
```

该包只包含：

- 稳定任务标识；
- 任务参数类型；

不要包含：

- 队列实现；
- Service；
- Repository；
- 业务执行逻辑。

---

# 8. Client / Connector / Integration

与外部系统交互的代码必须有明确边界。

例如：

- 第三方 HTTP API；
- Feishu；
- GitHub；
- RSS；
- 网页抓取；
- 支付；
- 邮件；
- AI Provider；
- 对象存储。

默认通过 Client / Connector / Integration 进行隔离。

负责：

- 外部协议；
- HTTP 请求；
- 鉴权；
- 序列化与反序列化；
- 超时；
- 外部错误识别；
- 外部数据转换。

不负责：

- 本系统业务规则；
- 写业务数据库；
- 调用业务 Repository；
- 决定业务状态；
- 启动内部业务流程。

例如：

```text
SourceClient.FetchArticle(url)
→ ArticleResult
```

Client 只负责取得文章。

之后：

```text
ArticleService
→ 决定是否接受
→ 决定如何保存
```

不要让 Client 在获得数据后直接修改本系统状态。

---

# 9. Cron / Scheduler

Cron 只是定时触发入口。

典型方式：

```text
Cron
→ Service
```

如果任务本身需要异步队列的持久化、重试或并发管理：

```text
Cron
→ Service
→ Job
```

但不要机械地：

```text
Cron
→ Queue
→ Worker
```

所有定时任务都绕一遍队列。

如果定时操作：

- 执行很快；
- 不需要持久恢复；
- 不需要独立重试；
- 不需要排队；

可以直接：

```text
Cron
→ Service
```

是否使用 Queue，根据任务真实需求判断。

---

# 10. 一个新能力应该放进哪个模块

收到新需求时，按下面的顺序判断。

## 第一步：找到业务负责人

先问：

> 这个能力最终改变的是哪个业务对象或业务结果？

例如：

```text
导入文章成功
→ 最终产生 Article
→ Article 是主要业务负责人
```

而不是因为存在：

```text
article_imports
```

就自动创建：

```text
ArticleImportService
```

数据表不等于业务模块。

---

## 第二步：检查现有模块是否能够自然承担

如果新能力：

- 围绕同一个业务对象；
- 使用相同核心规则；
- 与现有能力共同变化；
- 使用相似依赖；
- 最终结果仍属于同一个业务负责人；

优先加入已有模块。

可以通过同包新文件组织代码，例如：

```text
service/article/
├── service.go
├── import.go
├── rewrite.go
└── reading_progress.go
```

这些文件仍属于：

```text
Article Service
```

不是四个 Service。

---

## 第三步：只有出现独立业务职责才创建新模块

一个新模块通常应该同时满足多个条件：

1. 有明确、独立的业务职责；
2. 可以用一句话描述自己的负责人身份；
3. 有相对独立的生命周期或规则；
4. 有自己的主要调用方；
5. 有独立依赖；
6. 与现有模块的变化原因不同。

例如：

```text
Article
```

与：

```text
WebsiteSubscription
```

可以是两个业务模块，因为：

- Article 负责最终阅读内容；
- Subscription 负责持续订阅关系与更新状态；
- 两者生命周期不同；
- Subscription 最终把新链接交给 Article。

---

# 11. 以下情况不能作为新增模块的唯一理由

不要因为以下原因单独创建模块：

```text
新增了一张表
新增了三个函数
service.go 太长
代码超过几百行
新增了一个 API
出现了一个新的 DTO
需要调用一个第三方库
想让目录看起来更整齐
未来可能还会扩展
```

这些都不足以证明存在新的业务职责。

文件可以拆，模块不一定需要拆。

---

# 12. 同一模块如何拆文件

文件是阅读单位，不是架构单位。

一个 Service 可以分成多个文件：

```text
article/
├── service.go
├── import.go
├── rewrite.go
├── reading_progress.go
└── book.go
```

它们可以：

- 共用一个 `Service`；
- 共用一个 `NewService`；
- 共用相同依赖；
- 使用同一个业务负责人。

不要因为新增文件就创建：

```text
ImportService
RewriteService
ReadingService
BookService
```

除非它们已经成为真正独立的业务模块。

文件按：

> 业务主题

拆分，而不是按：

> 固定行数

拆分。

---

# 13. Service 之间的调用

Service 之间允许调用。

不要为了避免 Service 调 Service：

- 绕过对方直接访问其表；
- 将所有逻辑搬进一个超级 Service；
- 建立一个没有真实职责的 Manager；
- 建立通用 Orchestrator 层。

跨业务调用时，应有明确方向。

例如：

```text
WebsiteSubscriptionService
→ ArticleService.StartImport
```

含义是：

> Subscription 发现一个新文章；
> Article 负责接受这个文章导入行为。

Subscription 不应该为了减少一次 Service 调用：

```text
→ ArticleRepository
→ ArticleImportRepository
→ Job
```

直接实现 Article 的业务规则。

---

# 14. Service 调用方向

跨 Service 调用必须能够说明：

> 谁是上游业务，谁拥有最终被修改的业务状态。

允许：

```text
A Service
→ B Service 的公开业务方法
```

但应避免：

```text
A → B
B → A
```

形成循环业务依赖。

如果两个 Service 经常双向调用，应重新判断：

- 模块是否拆错；
- 是否存在更明确的业务负责人；
- 某些能力是否只是查询能力；
- 是否应该通过业务结果或异步事件解耦。

不要通过全局变量、Service Locator 或隐藏 callback 掩盖循环依赖。

---

# 15. 跨模块读取与写入

“读取其他模块的数据”和“修改其他模块的业务状态”区别对待。

读取必要关联数据时，可以根据项目规模：

```text
Service
→ Repository
```

读取相关数据。

但修改另一个业务模块拥有的业务状态时，优先：

```text
Service A
→ Service B.PublicOperation
```

而不是：

```text
Service A
→ Repository
→ 直接修改 B 的业务表
```

判断标准：

> 如果这个写入需要理解 B 的业务规则，就应该由 B 的业务负责人执行。

---

# 16. API 模块和 Service 模块不要求一一对应

API 通常按照：

> 对外资源和用户操作

组织。

Service 按照：

> 业务职责

组织。

所以：

```text
api/book
api/article
```

完全可以共同调用：

```text
service/article
```

只要它们最终都属于 Article 的业务规则。

反过来，一个 API Use Case 也可以调用多个业务 Service。

不要为了“目录看起来对应”机械建立：

```text
每个 API 包
=
一个 Service 包
=
一个 Repository 文件
=
一张表
```

这些层之间不是一一映射关系。

---

# 17. Repository 和 Service 不要求一一对应

Repository 主要按照持久化对象和数据操作组织。

Service 按业务能力组织。

可能存在：

```text
ArticleService
→ article repository
→ article_content repository
→ article_import repository
```

也可能存在：

```text
SubscriptionService
→ subscription repository
→ article repository（只读取必要关联）
```

不要为了保持形式统一创建：

```text
ArticleServiceRepository
```

这种包含所有底层数据操作的巨大接口。

---

# 18. 不建立万能模块

谨慎创建以下名称：

```text
common
utils
helpers
manager
processor
handler
core
base
shared
platform
```

这些名字不是绝对禁止。

但新增前必须能说明：

> 它实际拥有哪项具体职责？

如果回答只是：

```text
很多地方都会用
方便统一
以后可能扩展
```

通常还不应该提取。

优先让能力靠近实际业务使用方。

---

# 19. 不建立无职责的中间层

不要出现：

```text
API
→ Application
→ Manager
→ Service
→ Repository
```

但每一层只是调用下一层。

新增一层必须解决真实问题，例如：

- 协议适配；
- 独立业务规则；
- 外部系统隔离；
- 生命周期管理；
- 跨多个入口共享的真实 Use Case。

纯转发不是职责。

例如：

```go
func (s *Service) Create(ctx context.Context, input Input) error {
    return s.repo.Create(ctx, input)
}
```

如果 Service 没有业务语义，应该判断：

- 当前是否根本不需要 Service；
- 业务规则是否遗漏；
- 当前边界是否拆错。

不要为了满足固定层数保留空壳。

---

# 20. 接口的架构边界

默认使用具体类型。

接口用于表达：

> 使用方真正需要的能力边界。

适合接口的场景包括：

- 外部 Client；
- AI Provider；
- Queue Producer；
- 文件解析器；
- 需要替换实现的真实依赖；
- Service 之间希望暴露最小能力。

例如：

```go
type ArticleImporter interface {
    StartImport(ctx context.Context, input StartImportInput) (...)
}
```

由使用方定义自己需要的方法。

不要机械创建：

```text
ArticleServiceInterface
ArticleRepositoryInterface
UserRepositoryInterface
```

然后完整复制实现类型的全部方法。

接口不是架构层数的证明。

---

# 21. 依赖方向

依赖应该总体从入口向具体能力流动。

典型方向：

```text
API
  ↓
Service
  ↓
Repository
```

异步：

```text
Job
  ↓
Worker
  ↓
Service / Client / AI
```

外部系统：

```text
Service / Worker
  ↓
Client / Connector
  ↓
External System
```

基础设施：

```text
Service
  ↓
small interface
  ↓
Queue / Storage / External Adapter
```

Repository 不反向依赖 Service。

Client 不反向依赖业务 Service。

Job Core 不反向依赖具体业务。

AI Adapter 不直接依赖业务 Repository。

---

# 22. 依赖组装

依赖在应用入口显式组装。

例如：

```text
main / run

→ 创建 DB
→ 创建 Repository Store
→ 创建 Queue
→ 创建 Client
→ 创建 Service
→ 创建 Worker
→ 注册 Handler
→ 启动 Server
```

构造函数应显式表达模块需要什么。

不要使用：

- 全局 Service；
- 全局 Store；
- Service Locator；
- init 中启动 goroutine；
- init 中连接数据库；
- 隐式注册才能正常工作的业务依赖。

从构造代码中应该能够理解主要模块之间的关系。

---

# 23. 循环依赖

包级循环依赖必须避免。

业务上的双向依赖也应尽量避免。

如果出现：

```text
Service A
→ Service B

Service B
→ Service A
```

不要首先通过：

```text
提取接口
移动到 common
增加 callback
```

技术性绕开。

先重新判断业务边界。

通常可能意味着：

- 两个模块实际上属于同一个业务能力；
- 其中一方不应该拥有当前逻辑；
- 存在更上层的 Use Case；
- 一侧只需要非常小的读取能力；
- 某一步应该改为事件或异步协作。

先修正职责，再解决 Go import。

---

# 24. 横切能力

以下能力通常不是业务模块：

- 日志；
- tracing；
- metrics；
- config；
- 数据库连接；
- HTTP 通用解析；
- 通用错误输出；
- migration。

它们可以作为基础设施被多个模块使用。

但横切能力不得借机承载业务规则。

例如：

```text
httpkit
```

可以负责：

```text
严格 JSON Decode
统一 Response Envelope
Path 参数解析
```

但不应该负责：

```text
校验某个 Article 是否允许改写
```

后者属于 Article 业务。

---

# 25. 目录不是架构本身

不要因为现有目录名称而机械延续错误职责。

也不要为了满足一份理想目录树大规模搬代码。

判断顺序应是：

```text
业务职责
↓
依赖关系
↓
调用方向
↓
代码位置
```

而不是：

```text
先设计目录
↓
再强行把业务塞进去
```

目录的目的是帮助读者定位职责。

如果需要大量解释才能说明“为什么这个文件在这里”，通常应该重新检查归属。

---

# 26. 新增模块时必须说明

Plan 中只要新增业务模块，必须回答：

```text
模块名称：
articleimport

职责：
负责什么？

为什么不能放入已有模块：
现有哪个模块被考虑过？
为什么不适合？

入口：
谁调用它？

依赖：
它调用哪些模块？

拥有的数据或状态：
哪些业务状态由它负责？

与相邻模块的边界：
哪些事情明确不由它负责？
```

如果这些问题无法清楚回答，优先不要新增模块。

---

# 27. 修改现有模块边界时

如果需求需要改变已有模块职责，Plan 必须明确说明：

```text
原职责
→ 新职责

为什么需要改变

哪些调用方向发生变化

哪些代码需要迁移

是否影响现有 Use Case
```

不能在实现过程中因为：

> 放这里比较方便

就静默改变模块边界。

---

# 28. 判断架构是否过度设计

完成设计后检查：

- 是否存在只转发调用的层？
- 是否因为一张表创建了一个 Service？
- 是否因为一个 API 创建了一个模块？
- 是否为了测试机械创建接口？
- 是否提前建设当前没有使用方的扩展点？
- 是否为了消除少量重复提取了错误公共抽象？
- 是否增加了 Manager / Coordinator / Processor 但职责说不清？
- 是否一个业务流程被拆散到太多包中才能理解？
- 是否目录复杂度明显高于业务复杂度？

如果答案为是，应优先简化。

---

# 29. 判断架构是否拆得不够

简单不等于把所有逻辑塞在一起。

出现以下情况时，应考虑拆出独立职责：

- 一个模块承担明显不同的业务规则；
- 构造函数依赖持续增加，而且只有部分方法使用；
- 不同功能有完全不同的生命周期；
- 多组代码很少共同变化；
- 一个包既处理业务，又处理复杂外部协议；
- 一个 Service 已经成为所有功能的入口；
- 为理解一个业务必须过滤大量无关代码。

拆分的目标仍然是：

> 让业务负责人更清晰。

而不是单纯减少文件长度。

---

# 30. 架构评审标准

设计完成后，Agent 应能回答：

1. 每个业务模块分别负责什么？
2. 当前 Use Case 的主要负责人是谁？
3. 为什么代码放在这个模块？
4. 为什么没有复用另一个已有模块？
5. 如果新增模块，为什么真的需要？
6. API、Service、Repository、Worker、Client 分别承担什么？
7. 主要调用方向是什么？
8. 有没有反向依赖或循环依赖？
9. 有没有 Service 绕过另一个 Service 修改其业务状态？
10. 有没有 Repository 或 Client 隐藏额外业务流程？
11. 有没有只做转发的无职责层？
12. 有没有因为表、API 或文件数量机械拆模块？
13. 从入口开始，是否能较容易找到最终业务负责人？

如果这些问题无法清楚回答，架构边界还不够明确。

---

# 31. 最终目标

一个符合本规范的 Go 后端应该做到：

```text
看到 API
↓
知道进入哪个业务 Service
↓
从 Service 看懂业务流程
↓
知道哪些 Repository 负责数据
↓
知道哪些 Client 负责外部系统
↓
异步时能继续追到 Worker
↓
每个模块的负责人和调用方向都清楚
```

开发者不应该为了理解：

> “这件事情到底是谁负责的？”

在多个：

```text
manager
processor
handler
helper
repository
service
```

之间反复搜索。

架构设计的最终判断标准不是目录是否漂亮，而是：

> **业务职责清楚、调用方向稳定、代码容易定位、重要业务流程容易阅读。**
