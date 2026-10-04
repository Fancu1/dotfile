# Plan 设计规范

本文件规定 Codex Plan 模式下 Plan 的设计与输出方式。

本文件不负责判断什么时候进入 Plan 模式，也不规定 Plan 确认后的具体开发操作。

目标是：

> 在开始实现之前，让用户能够通过 Plan 清楚理解：
> 这个需求准备怎样实现、完整业务链路是什么、代码准备放在哪里、
> 数据怎样变化、关键函数叫什么、模块如何协作，以及最终如何验证。

Plan 不是 TODO List，也不是文件修改清单。

Plan 应是一份可以直接指导后续实现的设计说明。

---

## 1. 生成 Plan 前先理解现状

编写 Plan 前，先检查与当前需求直接相关的：

- 现有业务流程；
- 模块职责；
- Service；
- Repository；
- API；
- 数据表；
- Worker / Job / Cron；
- Client / Connector；
- 相关测试；
- 当前项目规则。

如果存在项目地图、Codebase Map 或其他代码导航能力，优先使用它定位相关实现，再阅读必要源码确认。

不要为了生成 Plan 默认扫描整个仓库或读取全部规则。

根据当前任务按需读取对应规范：

- 模块与依赖：`architecture.md`
- Use Case 与业务编排：`usecase.md`
- 数据设计：`data.md`
- Go 命名、函数、接口与注释：`go.md`
- 异步、Worker、Job、生命周期：`runtime.md`
- 测试：`testing.md`
- Commit：`contributing.md`

Plan 中的设计不得脱离当前代码凭空建立另一套架构。

---

# 2. Plan 的核心原则

Plan 应优先回答：

1. 用户最终要完成什么；
2. 完整业务流程怎样执行；
3. 每一步由哪个模块负责；
4. 关键函数和类型叫什么；
5. 代码准备放在哪些文件；
6. 会读取和修改哪些数据；
7. 哪些步骤属于同一个事务；
8. 哪里发生外部调用或异步切换；
9. 重要失败、重复和并发如何处理；
10. 最终怎样验证。

Plan 的主体是：

> **Use Case + 业务链路 + 关键设计决定**

而不是：

> 文件列表 + TODO List

---

# 3. Plan 默认结构

非简单后端功能的 Plan 默认按照下面的结构编写。

---

## 3.1 目标与范围

简短说明：

- 用户最终获得什么能力；
- 本次实现哪些内容；
- 明确不实现哪些相关内容；
- 哪些已有行为必须保持。

例如：

```text
目标：
管理员可以创建新的管理员账号，并配置已有角色。

本次包括：
- 创建管理员；
- 关联已有角色；
- 写入审计记录。

本次不包括：
- 修改管理员；
- 删除管理员；
- 创建角色。

保持：
- 现有管理员查询接口不变。
```

不要把未来可能需要的能力提前设计进本次需求。

---

## 3.2 Use Cases

按照用户或系统真正执行的业务行为拆分。

例如：

```text
Use Cases

1. 创建管理员
2. 禁用管理员
3. 查询管理员详情
```

不要按照技术层拆成：

```text
修改 API
修改 Service
修改 Repository
增加测试
```

一个 Use Case 应对应一条可以完整描述的业务流程。

---

# 4. 完整业务链路伪代码

每个核心 Use Case 必须提供一份完整的业务链路伪代码。

这是 Plan 最重要的部分。

伪代码应该从真实入口开始，一直描述到最终结果。

至少展示：

- Handler / Worker / Cron 等入口；
- Service 调用；
- 关键业务判断；
- Repository 查询；
- Repository 写入；
- Client / Connector 调用；
- 事务边界；
- 异步任务提交和消费；
- 主要错误分支；
- 最终返回或状态变化。

例如：

```text
创建管理员

Handler.CreateAdmin

1. BindJSON
   JSON / 字段类型错误
   → invalid_request

2. AdminService.CreateAdmin(operator, input)

   2.1 规范化 ad_account
       TrimSpace
       空值
       → invalid_request

   2.2 规范化 role_ids
       去空
       去重
       排序

   2.3 repo.GetAdmin(ad_account)
       已存在
       → admin_exists

   2.4 repo.ListRolesByIDs(roleIDs)
       存在缺失或停用角色
       → invalid_roles

   2.5 repo.Transaction

       repo.CreateAdmin(...)

       eventRepo.Append(
           category = access,
           action = create_admin,
           target = ad_account,
           ...
       )

   2.6 Commit

3. 返回
   201 {ad_account}
```

涉及异步时，需要继续展开生产和消费两部分：

```text
POST /api/article-imports

Handler.CreateImport
→ ArticleService.StartImport
    → Transaction
        → repo.CreateArticleImport
        → queue.EnqueueTx(import_article)
    → Notify Queue
→ 返回 202


Worker.HandleArticleImport
→ ArticleService.GetPendingImport
→ sourceClient.FetchArticle
→ ArticleService.CreateArticleFromImport
    → Transaction
        → repo.CreateArticle
        → repo.CreateArticleContent
        → repo.MarkArticleImportReady
→ Worker Success
```

不能使用过大的方法名隐藏重要业务步骤：

```text
repo.CompleteImport()
service.Process()
manager.Handle()
```

如果一个方法内部实际上包含多个重要业务判断或数据修改，Plan 中必须继续展开。

不要求展开纯实现细节或所有私有 helper。

判断标准是：

> 用户只看这份伪代码，是否已经能够理解这条业务是怎样完成的。

---

# 5. 关键代码设计

Plan 阶段应确定影响代码结构和可读性的关键符号。

至少包括：

- 核心 Handler 方法；
- 核心 Service 方法；
- 重要 Repository 方法；
- Worker / Cron 入口；
- Client / Connector 方法；
- 重要公开类型；
- Request / Response DTO；
- Task 类型和稳定 Kind；
- 新增数据表；
- 关键状态和字段。

同时明确它们所在的文件。

例如：

```text
internal/api/admin/handler.go
- Handler.CreateAdmin

internal/api/admin/request.go
- CreateAdminRequest

internal/api/admin/response.go
- CreateAdminResponse

internal/service/admin/service.go
- Service.CreateAdmin

internal/repository/admin.go
- Store.GetAdmin
- Store.CreateAdmin

internal/repository/event.go
- Store.AppendEvent
```

关键名称和文件位置是 Plan 的一部分，不应等到实现阶段随意决定。

具体命名规则遵循：

- `go.md`
- `architecture.md`
- `usecase.md`
- `data.md`

Plan 不需要提前确定：

- 普通局部变量；
- 循环变量；
- 很小的私有临时 helper；
- 不影响代码结构的局部实现细节。

---

# 6. 模块职责与调用关系

Plan 应明确本需求涉及哪些模块，以及各自为什么参与。

例如：

```text
API
- 解析 HTTP 输入；
- 调用 Admin Service；
- 将业务错误映射成 HTTP。

Admin Service
- 创建管理员 Use Case 的业务负责人；
- 校验管理员和角色状态；
- 编排管理员与审计记录的写入。

Repository
- 提供管理员、角色和事件的持久化操作；
- 提供事务能力；
- 不决定管理员创建流程。
```

同时给出主要调用方向：

```text
API
→ Admin Service
    → Admin Repository
    → Role Repository
    → Event Repository
```

如果新增模块，Plan 必须说明：

```text
为什么现有模块无法承担；
新模块拥有哪项独立职责；
谁调用它；
它依赖谁。
```

不得只因为：

- 文件变长；
- 方法变多；
- 新增一张表；

就建立新的业务模块。

具体判断遵循 `architecture.md` 与 `usecase.md`。

---

# 7. 数据设计

涉及数据库时，Plan 必须单独展示数据变化。

先写业务事实，再写表结构。

例如：

```text
数据

读
- admin：按 ad_account 查询是否已存在
- role：按 role_ids 查询角色和状态

写
- admin：新增管理员
- event：新增创建审计

事务
- admin + event 必须共同提交
```

新增表时必须说明：

```text
表：article_imports

一行代表：
- 一个用户对一个 URL 的稳定导入状态。

为什么独立存在：
- 导入在 Article 创建前已经存在；
- 有 pending / ready / failed 生命周期；
- 支持失败重试和 revision；
- 需要独立查询状态。

唯一性：
- user_id + url

关联：
- ready 后关联 article_id
```

修改已有表时说明：

```text
修改：articles

新增字段：
- source_url

含义：
- 保存文章原始来源地址；
- 手工粘贴文章为空。

唯一范围：
- user_id + source_url
```

具体表、字段、JSON、唯一约束、外键和迁移原则遵循 `data.md`。

---

# 8. API、异步与外部调用

涉及 HTTP 时，Plan 至少写清：

```text
POST /api/admins

Request
- ad_account
- role_ids

Success
- 201

Errors
- invalid_request
- admin_exists
- invalid_roles
```

涉及异步时，Plan 至少说明：

```text
Task
- ImportArticle

Kind
- import_article

Producer
- ArticleService.StartImport

Consumer
- ArticleImportWorker

状态
- article_imports

重试
- 按 runtime.md 约定

结果写回
- ArticleService.CreateArticleFromImport
```

涉及外部调用时，明确：

```text
sourceClient.FetchArticle

调用方
- ArticleImportWorker

职责
- 获取网页；
- 提取正文；
- 返回结构化结果。

不负责
- 保存文章；
- 更新导入状态；
- 提交任务。
```

详细规则遵循：

- `runtime.md`

---

# 9. 失败、重复和并发

Plan 应列出会影响设计的重要异常和边界。

例如：

```text
失败与边界

输入非法
→ invalid_request

管理员已经存在
→ admin_exists

角色不存在或停用
→ invalid_roles

event 写入失败
→ 整个事务回滚

并发创建相同 ad_account
→ 业务预检查
→ DB 唯一约束兜底
→ admin_exists
```

异步业务还应根据实际情况说明：

```text
重复消费
旧 revision
外部超时
最终失败
进程取消
恢复
```

不需要为了形式枚举与当前需求无关的所有理论异常。

---

# 10. 需要用户确认的设计问题

生成 Plan 时，如果存在无法从需求、现有代码和规则中可靠确定，并且会影响：

- 产品行为；
- 模块边界；
- 数据结构；
- API 契约；
- 兼容性；
- 需求范围；

的决策，可以向用户确认。

确认时不得直接让用户从零设计。

默认使用：

> **推荐方案 + 选择题**

如果环境支持交互式选择控件，优先使用交互式选择。

否则使用文本选项。

例如：

```text
首次订阅时如何处理 Feed 已有文章？

A. 导入当前 Feed 已有文章
B. 只接收订阅以后新增的文章

推荐：A

原因：
- 用户订阅后立即有内容；
- 不需要额外保存初始链接基线；
- 当前 URL 去重机制已经能够避免重复导入。

请选择 A / B。
```

不要问：

```text
你希望首次订阅怎么做？
```

如果某个问题只是普通技术设计，并且可以根据已有规则形成明确方案，应直接给出设计，不询问用户。

相关确认尽量集中进行。

通常一次不超过 3 个真正影响方案的决定。

---

# 11. 实现范围与明确不做的内容

Plan 应清楚列出本次明确不实现的相关能力。

例如：

```text
本次不做

- 管理员编辑；
- 管理员删除；
- 角色管理；
- 批量创建；
- 新的权限模型。
```

这部分用于防止 Agent 在实现阶段因为“顺手”扩大范围。

不要设计没有当前需求的扩展点。

---

# 12. 预计文件变更

在业务设计之后，再汇总主要文件变更。

例如：

```text
新增

internal/api/admin/
- handler.go
- request.go
- response.go

internal/service/admin/
- service.go

internal/repository/
- admin.go


修改

internal/api/router.go
- 注册管理员创建路由

internal/repository/store.go
- 无结构变化，仅复用现有 Store
```

不要把文件列表放在 Plan 最前面。

不要为了 Plan 看起来完整而提前创建没有实际内容的文件。

---

# 13. 验收设计

Plan 必须给出业务级验收条件。

例如：

```text
验收

正常创建
→ 返回 201
→ admin 新增一行
→ event 新增一行

空 ad_account
→ invalid_request
→ 不写数据库

管理员已存在
→ admin_exists
→ 不写数据库

非法角色
→ invalid_roles
→ 不写数据库

event 写入失败
→ admin 同时回滚

并发创建同一账号
→ 最终仅存在一条 admin
```

再根据 `testing.md` 指定需要的：

```text
- unit test
- integration test
- lint
- build
- race
- E2E
- migration test
```

不要只写：

```text
补充相关测试。
```

---

# 14. Commit 计划

Plan 中需要包含本次需求预期的 Commit 组织方式。

这里仅规划 Commit，不处理 Commit 授权和实际 Git 操作。

小型完整需求通常一个 Commit：

```text
Commit

feat: add admin creation
```

较大需求如果存在自然独立阶段，可以拆分：

```text
Commit 1
feat: add article import persistence

内容：
- migration
- repository
- storage tests


Commit 2
feat: process article import jobs

内容：
- task
- worker
- source client
- service


Commit 3
feat: expose article import API

内容：
- HTTP API
- frontend integration
- E2E
```

Commit 应按照逻辑变化拆分，不按文件数量机械拆分。

具体 Commit 与 Git 操作遵循 `contributing.md`。

---

# 15. Plan 末尾必须提供实施摘要

Plan 最后增加一段简短的实施摘要，让用户能够快速复核整个方案。

格式建议：

```text
实施摘要

入口
POST /api/admins

主业务负责人
AdminService.CreateAdmin

主链路
Handler.CreateAdmin
→ AdminService.CreateAdmin
→ GetAdmin
→ ListRolesByIDs
→ Transaction(
    CreateAdmin
    → AppendEvent
  )
→ 201

数据
读：admin、role
写：admin、event

新增模块
无

新增表
无

主要文件
- internal/api/admin/handler.go
- internal/service/admin/service.go
- internal/repository/admin.go
- internal/repository/event.go

Commit
feat: add admin creation
```

这部分不是替代前面的详细设计。

它的作用是让用户能够在几十秒内重新确认：

> Agent 到底准备怎样实现这个需求。

---

# 16. Plan 的质量标准

完成 Plan 前自行检查。

用户读完 Plan 后，不应该还需要追问：

- 这个业务到底怎么走？
- 谁调用谁？
- 这个判断在哪里做？
- 什么时候写这张表？
- 哪些表一起写？
- 为什么要新建这个模块？
- 这个函数准备叫什么？
- 文件准备放在哪里？
- Worker 最后调用谁？
- 失败以后是什么状态？
- 重复执行会发生什么？
- 这个需求最终准备拆几个 Commit？

如果这些问题仍然需要用户通过阅读未来代码才能知道，Plan 还不够清晰。

Plan 的目标不是描述“准备改哪些东西”。

Plan 的目标是：

> **在代码尚未实现的时候，就把未来实现的主要结构和业务行为展示出来。**
