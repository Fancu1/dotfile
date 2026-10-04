# Go 代码规范

本文件规定 Go 代码的具体写法，包括命名、函数、类型、接口、错误处理、Context、并发、资源管理和注释。

目标不是追求复杂抽象、极度简短或者“高级”的命名，而是：

> 让代码尽可能自己解释自己。
>
> 读者通过包名、类型名、函数名、变量名和调用关系，
> 就能大致理解代码正在处理什么业务、执行什么操作。

核心原则：

> **简单、清晰、直接。**

如果“短但模糊”和“稍长但清楚”之间需要选择，优先后者。

如果“专业但需要理解一下”和“普通但一眼能懂”之间需要选择，优先后者。

---

# 1. 基础要求

所有 Go 代码必须使用 `gofmt`。

如果项目已经使用：

- `goimports`
- `staticcheck`
- `golangci-lint`
- 其他 Go 检查工具

继续使用项目现有入口，不自行建立重复工具链。

遵循 Go 正常可见性规则：

```go
GetTask      // 导出
getTask      // 包内私有

ParseContent // 导出
parseContent // 包内私有
```

不要为了“统一”把本来只应该包内使用的函数全部导出。

---

# 2. 命名的核心原则

名称应该尽可能回答：

> 这是什么？

或者：

> 它具体做什么？

不要让读者必须打开实现以后，才能知道名字是什么意思。

例如：

```go
Claim
Resolve
Processor
Result
```

虽然语法没有问题，但脱离上下文通常无法理解真实业务含义。

命名应优先使用：

> **简单动词 + 明确对象**

例如：

```go
GetTask
StartTask
FinishTask

LoadRule
SaveRule

FetchArticle
ParseContent
BuildRequest

CreateUser
UpdateUser
DeleteUser
```

这种命名结构应作为默认方式。

---

# 3. 优先使用简单、常见的动词

大多数函数优先从一组简单、稳定的动词中选择。

| 行为 | 默认动词 |
| --- | --- |
| 获取一个对象 | `Get` |
| 获取多个对象 | `List` |
| 查找可能不存在的对象 | `Find` |
| 从配置、文件或本地来源加载 | `Load` |
| 从外部系统获取 | `Fetch` |
| 创建 | `Create` |
| 更新已有对象 | `Update` |
| 保存结果 | `Save` |
| 删除 | `Delete` |
| 开始流程 | `Start` |
| 停止流程 | `Stop` |
| 完成流程 | `Finish` |
| 重试 | `Retry` |
| 解析 | `Parse` |
| 构造一个值 | `Build` |
| 校验 | `Validate` |
| 检查条件或状态 | `Check` |
| 读取 | `Read` |
| 写入 | `Write` |
| 发送 | `Send` |

没有明显必要时，不要为了显得专业重新发明动词。

谨慎使用：

```text
Claim
Resolve
Acquire
Hydrate
Materialize
Reconcile
Finalize
Orchestrate
Provision
Dispatch
```

如果这些词不是项目业务中的正式概念，应优先换成更简单的动作。

例如根据实际含义：

```text
Claim      → Get / Start
Acquire    → Get
Finalize   → Finish
Hydrate    → Load
Materialize → Build / Create
Reconcile  → Update / Sync
Resolve    → Get / Find / Parse
```

不是机械替换，应根据函数真正做的事情选择最直接的普通动词。

---

# 4. 动词后面直接写操作对象

默认函数结构：

```text
Verb + Object
```

例如：

```go
GetTask
ListTasks
StartTask
FinishTask
RetryTask

LoadRule
SaveRule

FetchContent
ParseContent
SaveContent

CreateArticle
GetArticle
DeleteArticle
```

避免大量角色式或抽象式命名：

```go
TaskClaimer
RuleProvider
ContentResolver
ImportFinalizer
```

如果代码可以直接描述“做什么”，不要先创造一个抽象角色再让读者理解。

---

# 5. 不把所有条件塞进函数名

名称应该表达主要动作，而不是把完整实现写进名字。

避免：

```go
GetPendingTaskByUserAndRevision
ClaimPendingTaskForExecution
CreateArticleFromCompletedImportResult
```

如果核心行为可以表达为：

```go
GetTask
StartTask
CreateArticle
```

优先使用简单名称。

以下细节由：

- 参数；
- 类型；
- 所在模块；
- 调用上下文；
- 函数内部校验；

共同表达：

```text
属于哪个用户
必须处于什么状态
revision 是否一致
是否允许重试
```

不要为了追求“名字绝对精确”把函数名写成一句话。

---

# 6. 但不能因为短而丢失业务对象

避免：

```go
Get()
Start()
Finish()
Process()
```

在业务代码中默认省略对象。

即使接收者已经提供一部分上下文，也优先让调用点本身容易理解：

```go
taskService.StartTask(...)
taskRepo.GetTask(...)

ruleStore.LoadRule(...)

articleService.CreateArticle(...)
```

而不是：

```go
taskService.Start(...)
taskRepo.Get(...)

ruleStore.Load(...)

articleService.Create(...)
```

例外是 Go 中已经非常明确的通用行为，例如：

```go
server.Run()
client.Close()
buffer.Reset()
value.String()
```

判断标准是：

> 单独阅读调用语句时，是否能快速知道它在操作什么。

---

# 7. 不重复堆叠已经明确的信息

虽然保留业务对象，但也不要无限重复。

避免：

```go
articleService.CreateArticleServiceArticle(...)
articleRepo.GetArticleByArticleID(...)
```

应该保持自然：

```go
articleService.CreateArticle(...)
articleRepo.GetArticle(...)
```

如果需要表达特殊查询：

```go
articleRepo.GetArticleByURL(...)
```

命名的目标不是最长，而是调用点最容易理解。

---

# 8. 同一个业务概念统一使用同一个词

一旦项目确定一个概念叫：

```text
Task
Article
Rule
Subscription
Import
```

不要在不同地方随意换成：

```text
Job
Item
Entry
Record
Entity
Process
```

除非它们真的代表不同概念。

例如如果业务概念叫：

```text
ArticleImport
```

应尽量统一：

```go
StartArticleImport
GetArticleImport
RetryArticleImport
```

不要同一流程中又出现：

```go
ArticleClaim
Ingestion
ImportProcess
ArticleLoadJob
```

同义词越多，代码理解成本越高。

---

# 9. 谨慎使用抽象名词

以下词单独使用时通常不够清楚：

```text
Claim
Item
Entry
Record
Data
Info
Object
Entity
Context
State
Result
Action
Resource
```

例如避免：

```go
type Claim struct{}
type Item struct{}
type Result struct{}
```

如果真实业务对象是任务：

```go
type Task struct{}
```

如果是真正的任务执行结果：

```go
type TaskResult struct{}
```

如果是文章导入结果：

```go
type ArticleImportResult struct{}
```

不要为了领域建模创造一个读者需要重新学习的抽象词。

---

# 10. 包名

包名使用：

- 简短；
- 小写；
- 明确职责；
- 稳定的业务词。

例如：

```text
article
task
rule
repository
worker
sourceclient
subscription
```

谨慎使用：

```text
common
utils
helpers
manager
processor
core
base
misc
shared
```

如果不知道代码应该放哪里，不要通过创建 `utils` 或 `common` 解决。

模块边界遵循 `architecture.md`。

---

# 11. 类型命名

类型应该直接表达：

> 它是什么。

例如：

```go
Task
Rule
Article
ArticleImport
WebsiteSubscription
ReviewBatch
```

如果需要区分层次，可以加入必要后缀：

```go
CreateTaskInput
TaskRecord
TaskResponse
```

但不要机械添加：

```text
Model
Entity
Object
Impl
Bean
Data
Info
```

例如避免：

```go
TaskEntity
ArticleInfo
RuleData
```

如果：

```go
Task
Article
Rule
```

已经足够。

---

# 12. Interface 命名

Interface 应该保持简单，并让人知道它代表什么能力或协作对象。

例如：

```go
type TaskStore interface {
    GetTask(...)
    CreateTask(...)
}

type RuleStore interface {
    LoadRule(...)
    SaveRule(...)
}

type ContentParser interface {
    ParseContent(...)
}

type ArticleClient interface {
    FetchArticle(...)
}
```

相比：

```go
TaskClaimer
ImportResultWriter
RuleResolver
ArticleMaterializer
```

优先前一种简单形式。

Interface 名称通常可以使用：

```text
XxxStore
XxxClient
XxxReader
XxxWriter
XxxParser
XxxLoader
XxxService
```

前提是这些词准确描述其职责。

---

# 13. 不使用 Java 风格 Interface 名称

不要：

```go
IArticleService
ITaskRepository
IRuleStore
```

Go Interface 不使用 `I` 前缀。

---

# 14. Interface 应该小而清楚

Interface 由使用方根据实际需要定义。

例如一个 Worker 只需要：

```go
type TaskService interface {
    GetTask(...)
    FinishTask(...)
}
```

不要为了 Mock，把整个 Service 的几十个方法复制成一个 Interface。

默认使用具体类型。

只有存在真实协作边界时才定义 Interface，例如：

- 外部 Client；
- Queue；
- AI；
- 文件解析器；
- 跨模块需要的少量能力；
- 有价值的测试替换点。

---

# 15. Interface 方法仍采用简单动词 + 对象

例如：

```go
type TaskStore interface {
    GetTask(ctx context.Context, taskID int64) (Task, error)
    CreateTask(ctx context.Context, input CreateTaskInput) (Task, error)
    UpdateTask(ctx context.Context, input UpdateTaskInput) error
}
```

而不是：

```go
type TaskStore interface {
    Claim(...)
    Resolve(...)
    Apply(...)
}
```

除非这些词本身就是业务正式动作。

---

# 16. 变量命名

变量优先使用实际业务对象名称：

```go
task
rule
article
subscription
articleImport
content
user
```

避免：

```go
item
entry
obj
data
info
record
thing
value
res
ret
tmp
```

例如：

```go
task, err := repo.GetTask(ctx, taskID)
```

优于：

```go
record, err := repo.GetTask(ctx, taskID)
```

因为即使类型相同，前者更容易读。

---

# 17. result 不是默认变量名

如果返回结果有明确业务含义，直接使用业务名称。

优先：

```go
task, err := ...
article, err := ...
content, err := ...
subscription, err := ...
```

而不是：

```go
result, err := ...
```

只有返回值真的就是一个通用 Result 类型，并且上下文足够明确时才使用 `result`。

---

# 18. ID 带对象名

函数同时存在多个对象时，不要使用：

```go
id
```

而应：

```go
taskID
userID
articleID
ruleID
```

例如：

```go
func GetTask(ctx context.Context, userID, taskID int64)
```

很小且只有一个对象的私有函数可以适当简化。

---

# 19. 布尔变量

布尔变量应该直接表达：

> true 意味着什么。

例如：

```go
enabled
ready
exists
finished
shouldRetry
canStart
hasPermission
```

避免：

```go
flag
value
result
status
```

代码应尽量能够自然阅读：

```go
if shouldRetry {
    ...
}
```

---

# 20. 不用多个 bool 表达一个状态

如果真实状态是：

```text
pending
running
ready
failed
```

不要设计：

```go
isStarted bool
isReady   bool
isFailed  bool
```

这会产生非法组合。

应使用一个明确状态类型：

```go
type TaskStatus string

const (
    TaskStatusPending TaskStatus = "pending"
    TaskStatusRunning TaskStatus = "running"
    TaskStatusReady   TaskStatus = "ready"
    TaskStatusFailed  TaskStatus = "failed"
)
```

---

# 21. Get / List / Find

默认保持稳定语义。

```text
Get
= 获取一个明确对象

List
= 获取一组对象

Find
= 根据条件寻找一个可能不存在的对象
```

例如：

```go
GetTask
ListTasks
FindTaskByKey
```

不要同一项目随机使用：

```text
Get
Load
Query
Lookup
Find
```

表达同一件事情。

---

# 22. Load 与 Fetch

默认区分：

```text
Load
= 从本地、配置、已有存储或静态来源加载

Fetch
= 从外部或远端系统获取
```

例如：

```go
LoadRule
LoadConfig

FetchArticle
FetchFeed
```

不要为了“英文更准确”频繁更换近义词。

---

# 23. Parse

`Parse` 表示：

> 把一种已有表示解析成结构化内容。

例如：

```go
ParseContent
ParseFeed
ParseURL
```

不要用：

```go
ResolveContent
MaterializeContent
HydrateContent
```

表达普通解析行为。

---

# 24. Create

`Create` 表示：

> 创建一个新的对象或业务记录。

例如：

```go
CreateTask
CreateArticle
CreateSubscription
```

不要把复杂的“开始业务流程”全部叫 `Create`。

例如异步任务发起更适合：

```go
StartTask
StartImport
```

最终真正产生文章时：

```go
CreateArticle
```

---

# 25. Start / Stop / Finish

存在明确生命周期时优先使用普通状态动作：

```go
StartTask
StopTask
FinishTask
```

优于：

```go
ClaimTask
AcquireTask
FinalizeTask
```

如果真实行为就是：

> 开始处理一个 Task

直接叫：

```go
StartTask
```

不要为了领域感改成 `ClaimTask`。

---

# 26. Update / Save

`Update` 用于：

> 修改已有对象的一部分状态。

例如：

```go
UpdateTask
UpdateSettings
```

`Save` 用于：

> 保存一个明确的整体结果。

例如：

```go
SaveRule
SaveContent
SaveProgress
```

不要使用：

```go
SaveData
UpdateRecord
```

这种缺少业务对象的名称。

---

# 27. Check / Validate

`Check` 更偏向：

> 检查当前状态或条件。

例如：

```go
CheckTaskStatus
CheckPermission
```

`Validate` 更偏向：

> 验证输入或对象是否满足规则。

例如：

```go
ValidateTask
ValidateURL
ValidateContent
```

如果简单：

```go
isValid
```

能够更清楚，也可以使用普通布尔函数。

不要为了精确区分制造太多近义动词。

---

# 28. 函数名称应该暴露副作用

如果函数会修改状态，名称应该让人看出来。

例如：

```go
CreateTask
UpdateTask
DeleteTask
StartTask
FinishTask
SaveRule
```

不要：

```go
GetTask
CheckTask
ValidateTask
```

内部偷偷修改数据库。

查询与检查函数默认不产生业务写入副作用。

---

# 29. 不用一个宽泛函数隐藏多个业务动作

谨慎：

```go
ProcessTask
HandleTask
ExecuteTask
CompleteImport
```

如果内部真实逻辑是：

```text
GetTask
→ CreateArticle
→ SaveContent
→ FinishTask
```

关键业务流程应该在 Service 中直接展示。

不要通过一个宽泛方法把重要步骤藏起来。

具体边界遵循 `service.md`。

---

# 30. 函数围绕一个明确行为

一个函数应该能够使用一句简单的话说明：

> 它做什么。

如果只能起名：

```text
process
handle
doWork
execute
```

通常应该检查函数是否承担了太多职责。

如果内部存在多个独立阶段，可以按照真实业务阶段拆分。

不要按照固定行数拆函数。

---

# 31. 私有函数也保持简单清楚

推荐：

```go
loadRule
parseContent
checkTask
buildRequest
normalizeURL
validateInput
```

而不是：

```go
handleData
processInfo
resolveContext
prepareStuff
```

私有不代表名称可以随意。

---

# 32. 文件命名

文件名应该帮助开发者找到业务。

优先：

```text
task.go
rule.go
article.go
import.go
content.go
subscription.go
client.go
service.go
```

按业务主题需要时：

```text
reading_progress.go
article_import.go
website_subscription.go
```

谨慎：

```text
manager.go
processor.go
helper.go
utils.go
common.go
impl.go
misc.go
```

文件名同样遵循：

> 简单、明确、能够定位业务。

---

# 33. 不默认创建 types.go

类型优先靠近它实际所属的业务。

例如：

```text
import.go
```

可以同时包含：

```go
StartImportInput
ImportResult
```

不要习惯性建立：

```text
types.go
```

然后把整个包的所有 Struct 都塞进去。

只有共享类型较多，且独立文件明显更清楚时才使用。

---

# 34. 不默认创建 interfaces.go

Interface 靠近使用方定义。

不要把所有 Interface 集中进：

```text
interfaces.go
```

让读者必须跳到另一个文件才能知道当前对象依赖什么。

---

# 35. service.go 不需要承载全部业务

业务包可以：

```text
task/
├── service.go
├── start.go
├── retry.go
└── finish.go
```

或者按照较大的业务主题拆文件。

这些仍然可以属于同一个 `Service`。

文件拆分不等于创建新的 Service。

具体模块边界遵循 `architecture.md`。

---

# 36. Struct 设计

Struct 只保存当前对象真正需要的数据和依赖。

例如：

```go
type Service struct {
    store  *repository.Store
    client *Client
}
```

字段名称按照用途命名：

```go
store
client
queue
parser
clock
```

避免：

```go
manager
helper
dependency
impl
repo1
service1
```

如果一个 Struct 依赖持续增加，而且不同方法使用完全不同的依赖，应重新检查职责边界。

---

# 37. Input 类型

参数较多时可以使用明确 Input：

```go
type CreateTaskInput struct {
    UserID int64
    Name   string
}
```

调用：

```go
CreateTask(ctx, input)
```

参数很少且自然时，不机械创建 Struct。

例如：

```go
GetTask(ctx, taskID)
DeleteTask(ctx, taskID)
```

保持简单即可。

---

# 38. 避免多个 bool 参数

不要：

```go
StartTask(task, true, false)
```

因为调用方不知道两个布尔值是什么。

可以使用明确 Input：

```go
type StartTaskInput struct {
    Force bool
}
```

或者重新设计成更明确的方法。

---

# 39. 类型明确时不要使用 any

已经知道结构时：

```go
type Task struct {
    ID     int64
    Status TaskStatus
}
```

不要为了省事写：

```go
map[string]any
any
[]any
```

`any` 只用于真正需要处理未知类型的基础设施边界。

---

# 40. nil 和零值必须有明确含义

例如：

```go
ArticleID *int64
```

应明确：

```text
nil = 尚未关联 Article
```

不要同时使用：

```text
nil
0
-1
```

表达“没有值”。

一个状态只选择一种表达。

---

# 41. Context

需要 `context.Context` 的函数，将它放第一个参数：

```go
func GetTask(ctx context.Context, taskID int64)
```

通常命名：

```go
ctx
```

不要：

- 把 Context 存在长期 Struct 字段；
- 放入业务 Input Struct；
- 使用 nil Context；
- 无理由用 `context.Background()` 切断上游 Context。

请求链路应持续向下传递当前 Context。

独立后台生命周期遵循 `runtime.md`。

---

# 42. 错误处理

普通失败返回：

```go
error
```

不要使用 `panic` 处理普通业务失败。

调用下层失败时，为错误增加当前操作上下文：

```go
task, err := repo.GetTask(ctx, taskID)
if err != nil {
    return Task{}, fmt.Errorf("get task %d: %w", taskID, err)
}
```

需要调用方识别时：

```go
errors.Is
errors.As
```

不要匹配错误字符串。

---

# 43. 错误名称简单但明确

例如：

```go
ErrTaskNotFound
ErrTaskAlreadyStarted
ErrRuleNotFound
ErrInvalidContent
```

避免：

```go
ErrInvalid
ErrFailed
ErrBad
ErrError
```

错误名称仍遵循：

> 简单 + 明确对象。

---

# 44. 不重复记录同一个错误

通常：

```text
Repository
→ Service
→ Handler / Worker
```

底层负责增加错误上下文。

最终处理边界负责日志。

不要每一层都：

```go
log.Error(err)
```

导致同一个错误重复输出。

---

# 45. 不吞错误

禁止：

```go
value, _ := loadRule()
```

除非错误确实与正确性无关。

禁止：

```go
if err != nil {
    log.Println(err)
}

return nil
```

把失败伪装成成功。

如果忽略错误的原因不明显，应写简短注释。

---

# 46. 主流程应该顺着读

优先提前处理错误和特殊情况。

例如：

```go
task, err := repo.GetTask(ctx, taskID)
if err != nil {
    return err
}

if task.Status != TaskStatusPending {
    return ErrTaskNotPending
}

rule, err := ruleStore.LoadRule(ctx, task.RuleID)
if err != nil {
    return err
}

return service.StartTask(ctx, task, rule)
```

避免过深嵌套：

```go
if err == nil {
    if condition {
        if anotherCondition {
            ...
        }
    }
}
```

---

# 47. 代码应该尽量像业务步骤

希望代码能够自然读成：

```go
task, err := repo.GetTask(ctx, taskID)
if err != nil {
    return err
}

rule, err := ruleStore.LoadRule(ctx, task.RuleID)
if err != nil {
    return err
}

content, err := client.FetchContent(ctx, task.URL)
if err != nil {
    return err
}

parsed, err := parseContent(content)
if err != nil {
    return err
}

return service.FinishTask(ctx, task.ID, parsed)
```

而不是：

```go
claim, err := taskClaimer.Acquire(...)
rule, err := provider.Resolve(...)
payload, err := resolver.Materialize(...)
result, err := processor.Process(...)
return finalizer.Finalize(...)
```

后者即使“专业”，阅读成本也更高。

---

# 48. 不按行数拆函数

函数是否需要拆分，取决于：

> 是否存在能够独立命名、独立理解的行为。

不是：

```text
30 行必须拆
50 行必须拆
```

一个较长但完整、顺序清晰的业务函数，可能比十个小函数更容易理解。

---

# 49. 不为少量重复制造抽象

只有两段代码：

- 表达同一个规则；
- 未来应当共同变化；

才提取公共能力。

只是看起来相似，可以保持独立。

允许少量重复换取：

> 更清楚的业务代码。

---

# 50. 构造函数

需要依赖的对象使用普通构造函数：

```go
NewService(...)
NewClient(...)
NewStore(...)
```

构造函数应该显式接收真实依赖：

```go
func NewService(
    store *repository.Store,
    client *Client,
) *Service
```

不要：

- 从全局变量偷偷取依赖；
- 通过 `init()` 连接数据库；
- 通过 `init()` 启动 goroutine；
- 要求调用方构造后再按特殊顺序初始化。

---

# 51. 不机械使用 Option Pattern

简单构造：

```go
NewService(store, client)
```

就足够时，不改成：

```go
NewService(
    WithStore(store),
    WithClient(client),
)
```

只有可选参数明显增加，而且 Option 真正改善调用可读性时才使用。

---

# 52. 不机械创建 Interface

默认使用具体类型。

不要：

```go
type TaskServiceInterface interface { ... }
type TaskRepositoryInterface interface { ... }
```

仅为了：

> “分层”
> “方便 Mock”

创建接口。

Interface 必须对应真实协作能力。

---

# 53. 不使用可变全局业务状态

避免：

```go
var globalStore *Store
var globalService *Service
```

依赖通过构造函数传入。

包级常量和真正不可变的静态值可以保留。

---

# 54. init()

`init()` 不用于：

- 读取业务配置；
- 数据库连接；
- 网络调用；
- 启动 goroutine；
- 注入业务依赖。

这些都应该在显式启动流程中完成。

---

# 55. goroutine

不要因为 Go 很适合并发，就默认使用 goroutine。

新增 goroutine 必须知道：

- 谁创建；
- 谁取消；
- 谁等待；
- 什么时候退出；
- 错误怎么处理。

避免：

```go
go doWork()
```

这种无人管理的后台任务。

需要长期运行或请求结束后继续执行的操作，由 `runtime.md` 中定义的 Worker / Job / Service 生命周期负责。

---

# 56. Channel

Channel 用于真正需要的 goroutine 通信。

使用时必须明确：

- 谁发送；
- 谁接收；
- 谁关闭；
- 何时结束；
- Buffer 为什么存在。

不要为了“Go 风格”把普通函数调用改成 Channel。

---

# 57. Mutex 与共享状态

共享可变状态必须有明确同步方式。

使用锁时：

- 明确锁保护什么；
- Critical Section 尽量小；
- 不在锁中执行慢网络请求；
- 不在锁中调用不可控外部代码。

不要为了“线程安全”给整个 Service 随便套一把全局锁。

---

# 58. 资源释放

成功取得资源后，安排可靠释放。

例如：

```go
resp, err := client.Do(req)
if err != nil {
    return err
}
defer resp.Body.Close()
```

循环中需要及时释放的资源不要不断 `defer` 到整个函数结束。

必要时提取单次处理函数或显式 Close。

---

# 59. Slice / Map 所有权

不要在调用方不知道的情况下修改传入的 Slice 或 Map。

例如如果函数只是读取：

```go
func CheckTasks(tasks []Task)
```

不要内部偷偷排序 `tasks`。

确实需要修改时：

- 名称或契约明确；
- 或复制以后再修改。

Map 同样如此。

---

# 60. 时间类型

时间点使用：

```go
time.Time
```

时间长度使用：

```go
time.Duration
```

不要用普通 `int` 表示不明确单位的时长。

如果外部协议必须用整数：

```go
TimeoutSeconds
DurationMillis
```

名称或注释必须体现单位。

---

# 61. 常量

普通常量遵循 Go 命名：

```go
const maxRetries = 3
const DefaultPageSize = 20
```

不要：

```go
MAX_RETRIES
DEFAULT_PAGE_SIZE
```

除非必须保持某个外部协议名称。

---

# 62. 状态常量使用明确类型

例如：

```go
type TaskStatus string

const (
    TaskStatusPending TaskStatus = "pending"
    TaskStatusRunning TaskStatus = "running"
    TaskStatusReady   TaskStatus = "ready"
    TaskStatusFailed  TaskStatus = "failed"
)
```

不要让：

```text
"pending"
"ready"
"failed"
```

散落在业务代码各处。

---

# 63. Generics

只有存在多个真实使用场景，并且共享同一算法时才使用泛型。

不要为了“减少重复”创造：

```go
Repository[T]
Service[T]
Manager[T]
```

把不同业务对象强行放进一个模板。

业务代码优先保持具体。

---

# 64. Reflection

普通业务代码避免使用反射。

优先：

- 明确类型；
- 普通函数；
- 显式代码。

只有框架、序列化或其他真实基础设施需求才使用反射。

---

# 65. 注释语言

自有业务代码的解释性注释默认使用简体中文。

Go 标识符和必要技术词保留英文：

```text
HTTP
URL
Context
Repository
Worker
```

不需要为了中文化强行翻译技术词。

---

# 66. 所有自有导出声明必须有注释

包括：

- 导出类型；
- 导出函数；
- 导出方法；
- 导出常量；
- 导出变量；
- Interface 导出方法；
- Struct 导出字段。

`internal` 包同样适用。

例如：

```go
// TaskID 是当前任务 ID。
TaskID int64
```

```go
// Revision 是当前任务执行版本。
// 重试后旧 Worker 的结果不得覆盖新版本。
Revision int64
```

---

# 67. 导出注释以标识符开头

例如：

```go
// GetTask 获取指定任务。
func GetTask(...)
```

```go
// TaskID 是当前任务 ID。
TaskID int64
```

不要：

```go
// 获取指定任务。
func GetTask(...)
```

---

# 68. 注释写业务语义，不翻译代码

好的注释说明：

- 为什么；
- 前提；
- 空值含义；
- 单位；
- 副作用；
- 特殊错误；
- 兼容限制。

例如：

```go
// Revision 是当前任务版本。
// 每次重试递增，避免旧执行结果覆盖新的任务状态。
Revision int64
```

不要：

```go
// 如果 err 不为空则返回错误。
if err != nil {
    return err
}
```

---

# 69. 私有函数不强制写注释

如果：

```go
loadRule
parseContent
checkTask
```

已经足够清楚，不需要机械写注释。

只有：

- 算法复杂；
- 业务前提不明显；
- 存在特殊兼容规则；
- 代码无法直接表达原因；

时补充说明。

---

# 70. TODO 必须说明原因和条件

好的：

```go
// TODO: 接入认证后从身份上下文读取 UserID。
// 当前项目仍固定使用默认用户。
```

避免：

```go
// TODO fix
// TODO optimize
// TODO refactor
```

留下无法行动的 TODO 没有意义。

---

# 71. 修改代码时同步修改名称和注释

如果实现已经变化，旧名称或注释不再准确：

> 必须一起修改。

不要因为：

> “改名字会多改几行”

继续保留错误语义。

错误名称比稍长的 Diff 更难维护。

---

# 72. 不顺手重命名整个项目

本规范主要约束：

- 新增代码；
- 本次实际修改代码。

普通功能开发不要顺手：

- 批量重命名旧变量；
- 给全项目补注释；
- 改所有历史 Interface；
- 清理所有模糊文件名。

范围外问题单独记录。

---

# 73. Go 代码自检

完成代码后，对本次新增和修改内容检查：

## 命名

是否大量出现：

```text
Claim
Resolve
Acquire
Materialize
Processor
Manager
Data
Info
Item
Record
Result
```

如果存在，检查能否改成：

> 简单动词 + 明确对象。

## 函数

调用点是否容易读：

```go
task := repo.GetTask(...)
rule := store.LoadRule(...)
content := client.FetchContent(...)
result := parseContent(...)
service.FinishTask(...)
```

而不是充满必须翻译的抽象动作。

## Interface

Interface 是否使用简单名称表达合作对象：

```text
TaskStore
RuleStore
ContentParser
ArticleClient
```

方法是否仍然使用明确的 `Verb + Object`。

## 变量

变量是否直接表达：

```text
task
rule
article
content
subscription
```

而不是：

```text
item
record
obj
data
res
```

## 文件

是否可以根据业务直接找到文件？

如果新增：

```text
manager.go
processor.go
helper.go
utils.go
```

需要重新检查名称和职责。

## 函数结构

是否能够顺着代码看出主要流程？

是否因为过度拆 helper，导致一个简单业务需要连续跳转多个文件？

## 错误和 Context

是否保留错误链？

是否吞错？

Context 是否正常向下传递？

## 注释

所有导出声明是否有中文解释性注释？

注释是否准确？

是否出现没有信息量的模板注释？

---

# 74. 最终判断标准

好的 Go 代码应该尽量做到：

```text
看到包名
→ 知道属于哪个业务

看到类型
→ 知道它是什么

看到 Interface
→ 知道它提供什么合作能力

看到函数
→ 知道它对什么对象做什么

看到变量
→ 知道当前拿的是什么业务对象

顺着调用
→ 可以直接理解主要业务流程
```

希望代码更接近：

```go
task, err := repo.GetTask(ctx, taskID)
if err != nil {
    return err
}

rule, err := ruleStore.LoadRule(ctx, task.RuleID)
if err != nil {
    return err
}

content, err := client.FetchContent(ctx, task.URL)
if err != nil {
    return err
}

parsed, err := parseContent(content)
if err != nil {
    return err
}

return service.FinishTask(ctx, task.ID, parsed)
```

而不是：

```go
claim, err := claimer.Acquire(...)
rule, err := provider.Resolve(...)
payload, err := resolver.Materialize(...)
result, err := processor.Process(...)
return finalizer.Finalize(...)
```

最终目标是：

> **使用有限、普通、稳定的词汇写代码。**
>
> **名称不追求高级，不追求过度抽象，也不把完整业务条件全部塞进名字。**
>
> **优先采用“简单动词 + 明确对象”，让调用代码本身就足够容易阅读。**
