# 业务流程与 Service 编排规范

本文件规定 Go 后端项目中业务 Use Case、Service、Repository、Worker、Client / Connector 等模块之间的职责与编排方式。

目标是：

> 让业务代码能够按照真实业务流程阅读。
>
> 读者从业务入口进入 Service 后，应能够看出：
> 业务做了哪些判断、调用了哪些能力、修改了哪些数据、
> 哪些操作需要共同成功，以及最终产生什么结果。

---

# 1. 核心原则

一个业务 Use Case 应有明确的业务负责人。

默认由对应业务 Service 负责：

- 业务校验；
- 状态判断；
- 业务规则；
- 多步骤流程编排；
- 多项持久化操作的业务顺序；
- 对其他业务能力或外部能力的调用；
- 最终业务结果的判断。

Service 是理解业务流程的主要代码入口。

对于一个核心 Use Case，读者不应该为了知道：

> “这个业务实际上做了什么？”

而不断深入 Repository、Worker、Helper 或数据库实现后才能拼出完整流程。

---

# 2. 先确定业务负责人

新增业务能力前，先回答：

> 谁拥有这条业务规则和最终结果？

例如：

```text
创建文章
→ Article Service

订阅网站
→ WebsiteSubscription Service

审批一个申请
→ Approval Service

给员工计算工资
→ Salary Service
```

业务负责人通常依据业务能力确定，而不是依据：

- 数据表；
- HTTP 路径；
- 文件数量；
- 技术动作；
- Worker 数量。

不要因为新增一张表，就自动新增一个 Service。

不要因为新增一个异步任务，就把它变成新的业务模块。

不要因为一个方法变长，就把其中每一步拆成不同 Service。

---

# 3. Service 表达的是 Use Case，不是 CRUD

Service 方法应表达调用方能够理解的业务行为。

优先：

```go
CreateAdmin(...)
StartArticleImport(...)
CreateArticleFromImport(...)
SubscribeWebsite(...)
ApproveApplication(...)
SubmitPayroll(...)
```

避免：

```go
Process(...)
Handle(...)
Do(...)
Execute(...)
SaveData(...)
UpdateInfo(...)
```

也不要为了与 Repository 一一对应，把 Service 设计成：

```go
Create(...)
Get(...)
Update(...)
Delete(...)
```

除非这些操作本身就是明确的业务能力。

Service 方法的名称应该让读者知道：

> 调用这个方法，在业务上准备发生什么。

---

# 4. Service 应显式展示业务流程

Service 中应该能够直接看到 Use Case 的主要步骤。

例如：

```text
AdminService.CreateAdmin

1. 规范化输入
2. 检查管理员是否存在
3. 检查角色是否有效
4. 开启事务
5. 创建管理员
6. 写入审计事件
7. 提交事务
8. 返回结果
```

对应代码应该尽量保持类似阅读顺序：

```go
func (s *Service) CreateAdmin(
    ctx context.Context,
    operator Operator,
    input CreateAdminInput,
) (Admin, error) {
    account := normalizeAccount(input.ADAccount)
    if account == "" {
        return Admin{}, ErrInvalidRequest
    }

    roles, err := s.store.ListRolesByIDs(ctx, input.RoleIDs)
    if err != nil {
        return Admin{}, err
    }

    if err := validateRoles(roles, input.RoleIDs); err != nil {
        return Admin{}, err
    }

    var created Admin

    err = s.store.Transaction(ctx, func(tx *repository.Store) error {
        var err error

        created, err = tx.CreateAdmin(ctx, ...)
        if err != nil {
            return err
        }

        if err := tx.AppendEvent(ctx, ...); err != nil {
            return err
        }

        return nil
    })
    if err != nil {
        return Admin{}, err
    }

    return created, nil
}
```

这段代码的重点不是具体写法。

重点是：

> 读 Service 就能知道业务按什么顺序执行。

---

# 5. 不要隐藏重要业务步骤

不得使用一个看起来简单的方法，隐藏多个调用者必须知道的重要业务行为。

例如：

```go
repo.CompleteArticleImport(...)
```

如果内部实际上执行：

```text
创建 Article
→ 创建 ArticleContent
→ 更新 ArticleImport 为 ready
```

那么这个方法会隐藏业务流程。

更推荐：

```text
ArticleService.CreateArticleFromImport

→ tx.CreateArticle(...)
→ tx.CreateArticleContent(...)
→ tx.MarkArticleImportReady(...)
```

Repository 仍然可以封装：

- SQL；
- ORM；
- 条件更新；
- 数据库错误；
- 行锁；
- 查询实现；
- 事务底层细节。

但不能因为“Repository 负责数据库”，就把完整业务步骤也隐藏进去。

---

# 6. 判断“一个 Repository 操作”的标准

Repository 方法应表达一个明确的持久化操作。

“一件事”不等于“一条 SQL”。

例如下面的方法都可以合理包含多条 SQL：

```text
ReplaceArticleTags
UpsertUserSetting
ListArticlesWithStatuses
DeleteBookCascadeData
```

只要这些 SQL 共同表达一个清晰的持久化语义。

真正需要避免的是：

```text
CompleteImport
FinalizeOrder
HandleCreation
ProcessApproval
```

这类名称背后同时：

- 创建多个业务对象；
- 修改多个业务状态；
- 执行业务判断；
- 决定后续流程。

判断标准是：

> 调用者看到 Repository 方法名，是否能够准确知道它会修改哪些业务数据？

如果答案是否定的，应考虑拆分。

---

# 7. Repository 不拥有业务流程

Repository 负责：

- 持久化模型；
- 查询；
- 插入；
- 更新；
- 删除；
- 唯一约束；
- 条件更新；
- 数据库事务能力；
- 数据库错误识别；
- 必要的持久化一致性。

Repository 不负责：

- 决定业务流程；
- 决定一个状态是否允许变化；
- 决定应该调用哪个外部系统；
- 决定是否提交异步任务；
- 决定 HTTP 状态码；
- 决定 Worker 是否应该重试；
- 编排多个业务步骤。

例如：

```text
GetImport
CreateArticle
CreateArticleContent
MarkArticleImportReady
```

属于合理 Repository 能力。

而：

```text
如果 import pending
→ 判断 revision
→ 查有没有文章
→ 决定复用
→ 创建文章
→ 保存正文
→ 更新 import ready
```

属于业务流程，应由 Article Service 负责。

---

# 8. 事务由 Service 决定业务范围

Service 决定：

> 哪些业务变化必须共同成功。

Repository 提供：

> 如何开启、提交和回滚数据库事务。

推荐形式：

```go
err := s.store.Transaction(ctx, func(tx *repository.Store) error {
    if err := tx.CreateA(...); err != nil {
        return err
    }

    if err := tx.CreateB(...); err != nil {
        return err
    }

    return tx.UpdateC(...)
})
```

这里：

```text
A + B + C 必须共同成功
```

是业务决定。

而：

```text
BEGIN
COMMIT
ROLLBACK
transaction-bound connection
```

是 Repository 的实现责任。

Service 不直接操作 SQL、GORM、数据库连接或底层事务对象。

---

# 9. 事务中的业务步骤必须可见

跨表写入时，优先让 Service 显式展示主要写入顺序。

例如：

```text
ArticleService.CreateArticleFromImport

Transaction
├── GetArticleImport
├── 检查 user / revision / status
├── GetArticleBySourceURL
├── CreateArticle
├── CreateArticleContent
└── MarkArticleImportReady
```

不推荐：

```text
ArticleService
→ repo.CompleteArticleImport(...)
```

然后所有步骤都隐藏在 Repository。

如果已有历史组合 Repository 方法，不要求因为本规范立即全仓重构。

但新增业务默认遵循显式编排方式。

修改历史流程时，再根据当前需求判断是否顺带调整。

---

# 10. 外部调用不要隐藏在数据操作里

网络、AI、文件解析和其他外部调用必须在业务流程中具有明确位置。

例如：

```text
Worker
→ ArticleService.GetPendingImport
→ SourceClient.FetchArticle
→ ArticleService.CreateArticleFromImport
```

不要：

```text
repo.CompleteImport(...)
```

内部偷偷：

```text
访问网页
→ 调 AI
→ 写数据库
```

Repository 不负责外部系统调用。

数据库事务中原则上不得等待：

- HTTP；
- RPC；
- AI；
- 浏览器；
- 文件上传；
- 长时间子进程；
- 其他不可控外部操作。

除非当前项目有明确且经过设计的特殊契约。

---

# 11. Client / Connector 负责外部能力，不拥有业务

Client / Connector 负责：

- 外部协议；
- 请求构造；
- 响应解析；
- 认证；
- 超时；
- 外部错误分类；
- 外部数据转换。

例如：

```text
SourceClient.FetchArticle
GitHubClient.GetRepository
FeishuClient.GetEmployee
LLMClient.Generate
```

它们返回外部结果。

它们不决定：

```text
拿到文章以后是否创建 Article；
飞书员工不存在是否停止审批；
AI 返回失败以后业务状态改成什么；
外部结果应该写哪几张业务表。
```

这些决定属于业务 Service。

---

# 12. API 是协议入口，不是业务负责人

HTTP Handler 默认负责：

```text
解析请求
→ 协议级校验
→ 调用 Service
→ 将业务结果转换成 HTTP Response
```

例如：

```text
Handler.CreateAdmin
→ BindJSON
→ Service.CreateAdmin
→ mapError
→ WriteResponse
```

Handler 不应：

- 直接访问 Repository；
- 编排多个 Repository 写入；
- 决定业务状态转换；
- 直接调用 AI；
- 直接提交业务任务；
- 复制 Service 中已有的业务校验。

例如：

```go
if req.RoleIDs == nil {
    ...
}
```

如果这是 JSON 格式要求，可以在 API。

但：

```text
角色必须存在且 enabled
```

属于业务规则，应由 Service 保证。

即使未来出现第二个入口，例如 Worker、CLI 或 RPC，也必须得到同样的业务保证。

---

# 13. Worker 是执行入口，不是业务负责人

Worker 负责：

- 接收任务；
- 读取任务参数；
- 调用必要外部能力；
- 调用 Service；
- 将错误分类给任务框架；
- 遵守任务 context 和生命周期。

Worker 不应直接拥有业务表写入逻辑。

推荐：

```text
ArticleImportWorker

1. ArticleService.GetPendingImport
2. SourceClient.FetchArticle
3. ArticleService.CreateArticleFromImport
```

不推荐：

```text
Worker

1. 查 article_imports
2. 判断 revision
3. 创建 articles
4. 创建 article_contents
5. 更新 article_imports
```

后者把 Article 业务规则复制到了 Worker。

如果相同业务以后被：

- HTTP；
- Worker；
- Cron；
- CLI；

多个入口触发，应复用同一个业务 Service。

---

# 14. Cron 和后台循环也是入口

Cron、Ticker、后台扫描器与 Worker 一样：

> 它们负责“什么时候执行”，不负责重新定义业务规则。

例如：

```text
SubscriptionScanner

→ 找到到期订阅
→ WebsiteSubscriptionService.RefreshSubscription(...)
```

或者：

```text
Scanner
→ SourceClient.FetchFeed
→ WebsiteSubscriptionService.AcceptFeedResult(...)
```

具体怎么拆取决于该 Service 是否拥有外部调用。

但不要让后台循环直接：

```text
查询表
→ 修改一堆业务状态
→ 创建其他业务数据
```

绕过业务 Service。

---

# 15. Service 之间可以调用，但必须有明确业务方向

Service 之间不是绝对禁止调用。

当一个业务 Use Case 合理地使用另一个业务模块已经拥有的能力时，可以调用对应 Service。

例如：

```text
WebsiteSubscriptionService
→ ArticleService.StartRSSImport(...)
```

因为：

```text
WebsiteSubscription
负责发现新文章

Article
负责文章导入
```

订阅模块不应该为了避免 Service 调 Service，而绕过 Article Service 直接操作 Article Repository。

调用时应满足：

- 被调用 Service 确实拥有这项业务；
- 调用方向符合业务依赖；
- 不产生循环依赖；
- 不通过 Service 暴露内部实现细节；
- 不为了共享少量代码建立互相调用。

如果两个 Service 经常双向调用，应重新检查：

- 业务边界是否拆错；
- 是否存在第三个真正的业务负责人；
- 是否只是共享纯计算逻辑，可以提取无业务状态的组件。

---

# 16. 跨 Service 调用优先依赖最小能力

Service A 使用 Service B 时，不必机械依赖 B 的完整具体类型。

如果只需要一项稳定能力，可以由使用方定义小接口：

```go
type ArticleImporter interface {
    StartRSSImport(
        ctx context.Context,
        input StartRSSImportInput,
    ) (ArticleImport, error)
}
```

然后：

```go
type Service struct {
    articles ArticleImporter
}
```

但不要因为“解耦”就为所有 Service 自动生成完整 Interface。

默认仍然使用具体类型。

只有存在真实协作边界、替换需求或测试价值时，再定义小接口。

具体接口规范遵循 `go.md`。

---

# 17. 不要把同一业务拆成多个互相转发的 Service

避免：

```text
ArticleService
→ ArticleImportService
→ ArticleCreationService
→ ArticlePersistenceService
```

如果这些模块都在共同完成：

> 创建一篇文章

而没有独立业务生命周期，那么通常应该保持在 Article Service 中。

可以通过同包文件拆分：

```text
service/article/
├── service.go
├── import.go
├── rewrite.go
├── reading_progress.go
└── book.go
```

它们仍然属于同一个：

```go
*article.Service
```

文件用于组织代码。

文件不代表独立业务 Service。

---

# 18. 什么时候才应该新建 Service

新建 Service 通常意味着出现了新的独立业务能力。

应至少能够回答：

```text
它拥有哪一组业务规则？
它的主要调用方是谁？
它管理什么业务生命周期？
它有哪些独立依赖？
为什么现有 Service 不应该承担？
```

例如：

```text
Article Service
→ 文章生命周期

WebsiteSubscription Service
→ 用户订阅及刷新生命周期

SentenceReview Service
→ 例句复习生命周期
```

不要因为：

```text
新增表
新增接口
新增 Worker
新增文件
代码超过多少行
```

就自动新建 Service。

---

# 19. 一个 Service 可以拆多个文件

Service 变大时，优先按业务主题拆同包文件。

例如：

```text
service/article/

service.go
- Service
- NewService
- 基础文章能力

import.go
- StartImport
- CreateArticleFromImport

rewrite.go
- StartRewrite
- CompleteRewrite

reading_progress.go
- GetReadingProgress
- SaveReadingProgress

book.go
- ImportBook
- GetBook
```

它们仍然使用同一个：

```go
type Service struct {
    ...
}
```

以及同一次构造传入的依赖。

不要因为拆文件，再建立多个互相转发的 Service。

---

# 20. Service 构造函数应暴露真实依赖

Service 的依赖应能够从构造函数看出来。

例如：

```go
func NewService(
    store *repository.Store,
    queue TaskEnqueuer,
    source SourceClient,
) *Service
```

不要通过：

- 全局变量；
- init；
- package singleton；
- 隐藏 setter；
- 调用顺序；

偷偷补齐业务依赖。

如果某项依赖只有部分能力需要，可以使用 Option 或独立构造方式，但不要为了形式把所有 Service 都改成 Options 模式。

构造方式应让读者知道：

> 这个 Service 真正依赖什么。

---

# 21. 业务判断属于拥有该规则的 Service

判断一条逻辑应该放在哪里时，问：

> 谁拥有这条规则？

例如：

```text
Article 是否允许改写
→ Article Service

Role 是否有效
→ Role / Admin Use Case 对应 Service

Subscription 是否允许刷新
→ WebsiteSubscription Service

Sentence 是否已经可以复习
→ SentenceReview Service
```

不要因为判断需要数据库数据，就把判断放入 Repository。

Repository 可以返回：

```text
status = disabled
```

Service 决定：

```text
disabled role 不能分配给管理员
```

数据事实和业务判断必须区分。

---

# 22. 校验分层

校验根据语义归属不同层。

## API

负责协议级校验：

```text
JSON 是否合法
字段类型是否正确
Query 是否能解析
Path ID 是否合法
请求体是否超限
```

## Service

负责业务级校验：

```text
账号能否创建
角色是否允许分配
文章是否可以改写
当前 revision 是否仍有效
状态是否允许转换
```

## Repository / Database

负责最终数据约束：

```text
NOT NULL
UNIQUE
FOREIGN KEY
CHECK
并发条件更新
```

不能只依赖 API 校验业务。

不能只依赖数据库错误表达全部业务规则。

三层可以共同保护同一结果，但职责不同。

---

# 23. 状态转换必须有业务负责人

存在状态机时，例如：

```text
pending
ready
failed
disabled
approved
rejected
```

应由业务 Service 决定：

```text
当前状态是否允许进入目标状态。
```

Repository 负责执行：

```text
UPDATE ... WHERE status = ...
```

并通过条件更新保护并发。

例如：

```text
Service
判断：
pending + 当前 revision → 可以 ready

Repository
执行：
UPDATE article_imports
SET status = ready
WHERE id = ?
  AND revision = ?
  AND status = pending
```

业务规则和并发保护共同存在。

不要让 Repository 根据数据库当前值自行发明状态机规则。

---

# 24. 重复请求和幂等属于业务流程的一部分

涉及创建、异步消费或外部回调时，应明确：

```text
重复请求会发生什么？
重复消费会发生什么？
并发执行会发生什么？
旧结果会发生什么？
```

例如：

```text
CreateArticleFromImport

如果同 revision 已 ready
→ 返回已有 Article

如果同 URL 已有有效 Article
→ 复用 Article

如果旧 revision
→ 返回 stale

如果当前 pending 且无 Article
→ 正常创建
```

不要把这些情况全部交给数据库唯一冲突后再临时处理。

数据库约束负责兜底。

Service 负责定义业务语义。

---

# 25. Helper 不应隐藏业务阶段

可以使用私有函数减少重复和改善阅读。

但不要把完整业务阶段藏进名字模糊的 helper。

不推荐：

```go
prepare(...)
process(...)
handleState(...)
doSave(...)
finalize(...)
```

如果内部实际发生重要业务操作。

推荐：

```go
normalizeRoleIDs(...)
validateAssignableRoles(...)
reuseExistingArticle(...)
validatePendingImport(...)
```

读调用处应该能够知道：

> 为什么调用它，以及它大概做什么。

涉及重要数据写入的 helper 应特别谨慎。

如果写入行为对理解 Use Case 很重要，优先直接显示在 Service 主流程。

---

# 26. 不要为了减少代码重复破坏业务边界

两个 Use Case 的代码长得相似，不代表应该共享同一业务函数。

只有同时满足下面条件时再考虑提取：

```text
它们表达同一业务规则；
未来应该一起变化；
共享不会模糊业务归属。
```

例如：

```text
normalizeURL
```

可能可以共享。

但：

```text
CreateArticleFromImport
CreateArticleFromBook
```

即使都创建 Article，也可能具有完全不同的业务规则和事务范围。

不要为了消除几行重复强行统一。

---

# 27. Service 返回业务结果，不返回传输或数据库模型

Service 的输入输出应表达业务需要。

默认不要直接使用：

```text
HTTP Request DTO
HTTP Response DTO
GORM Model
SQL Row
```

作为跨层业务契约。

例如：

```go
type CreateAdminInput struct {
    ADAccount string
    RoleIDs   []int64
}
```

属于 Service 业务输入。

API 自己负责：

```go
CreateAdminRequest
CreateAdminResponse
```

Repository 自己负责持久化结构。

这样修改 HTTP 或数据库时，不需要自动污染整个业务层。

---

# 28. 错误在业务边界转换

Repository 返回：

```text
not found
unique violation
foreign key violation
database unavailable
```

Service 根据业务上下文转换成：

```text
admin_exists
invalid_roles
article_not_found
stale_revision
```

API 再将业务错误映射成：

```text
400
404
409
503
```

不要让数据库驱动错误成为 HTTP 契约。

也不要让 Repository 决定 HTTP 状态码。

---

# 29. Service 中应优先保持主流程可读

业务方法应尽量做到：

```text
先处理失败和特殊分支
→ 再展示主要成功路径
```

例如：

```go
if invalid {
    return ...
}

if alreadyDone {
    return existing, nil
}

if reusable {
    return reuse(...)
}

// 正常新建路径
```

避免过多嵌套：

```go
if ... {
    if ... {
        if ... {
            ...
        }
    }
}
```

不要为了追求一个函数只有十几行，把主流程拆散到大量私有函数。

判断标准仍然是：

> 阅读 Service 主方法时，能不能理解 Use Case。

---

# 30. 新增 Use Case 时的检查清单

设计新的业务流程时，至少检查：

## 业务负责人

- 谁拥有这个 Use Case？
- 已有 Service 是否可以承担？
- 是否真的需要新 Service？

## 流程

- Service 中能否看出完整主要步骤？
- 是否有重要业务行为被隐藏？

## 数据

- 哪些数据读取属于事实查询？
- 哪些判断属于业务规则？
- 哪些写入需要共同成功？

## Repository

- 每个方法是否表达明确的持久化操作？
- 是否隐藏了额外业务副作用？

## 外部能力

- Client / Connector 是否只负责外部系统？
- 网络或 AI 是否错误地进入数据库事务？

## 入口

- API / Worker / Cron 是否只承担各自入口职责？
- 是否绕过 Service 修改业务状态？

## 跨模块

- 如果调用其他 Service，业务依赖方向是否合理？
- 是否产生循环依赖？

## 可读性

最终应能够回答：

> 从业务入口进入 Service 后，
> 是否可以顺着代码理解整个 Use Case，
> 而不需要到多个底层文件中重新拼业务流程？

如果不能，应重新检查编排方式。

---

# 31. Plan 中如何展示业务编排

使用 Codex Plan 模式时，本规范与 `plan.md` 配合使用。

Plan 中每个核心 Use Case 应展示类似：

```text
Handler.CreateAdmin

→ AdminService.CreateAdmin

    → NormalizeInput

    → repo.GetAdmin
        已存在 → admin_exists

    → repo.ListRolesByIDs
        不合法 → invalid_roles

    → Transaction
        → repo.CreateAdmin
        → eventRepo.Append

→ 201
```

如果最终计划只能写成：

```text
修改 Admin Service
修改 Repository
增加 Event
```

说明业务编排还没有设计清楚。

---

# 32. 判断实现是否符合本规范

完成一个 Use Case 后，应能够从代码回答：

```text
业务负责人是谁？
入口调用哪个 Service？
Service 做了哪些关键判断？
读取了哪些业务数据？
修改了哪些业务数据？
哪些写入属于同一个事务？
外部调用发生在哪里？
异步边界在哪里？
失败由谁解释？
重复执行由谁处理？
```

这些答案不应该依赖：

> “继续深入五层调用才能知道”。

最终目标是：

> **业务流程显式，
> 职责边界稳定，
> 数据副作用可见，
> 技术实现隐藏在正确的边界之后。**
