# Git / Commit 规范

本文件规定 Agent 在 Git 工作区中的修改、暂存、Commit、分支和远程操作方式。

目标是：

> 每个 Commit 都表达一个清晰的逻辑变化；
> Agent 只提交本次任务拥有的修改；
> 用户已有工作区修改必须被保留；
> 任何可能改写历史、覆盖修改或影响远程仓库的操作都必须有明确授权。

---

# 1. 核心原则

Git 操作必须遵守：

1. 不覆盖用户已有修改；
2. 不把无关修改带入本次 Commit；
3. Commit 按逻辑变化组织，不按文件数量机械拆分；
4. Commit 前检查 staged diff；
5. Commit 后确认实际提交内容；
6. Commit 权限不代表 Push 权限；
7. 不在没有明确授权时改写 Git 历史。

工作区不是 Agent 的临时沙盒。

默认认为：

> 当前未提交修改可能属于用户或其他任务。

---

# 2. 开始开发前先检查工作区

开始修改代码前，至少检查：

```text
git status --short
```

必要时检查：

```text
git diff
git diff --cached
git log -5 --oneline
```

目标是知道：

- 当前分支；
- 是否已有未提交修改；
- 是否已有 staged 修改；
- 哪些文件可能属于用户正在进行的其他工作。

如果工作区不是干净的，不要求用户先清空。

Agent 应在保留现状的前提下继续工作。

---

# 3. 不要求干净工作区

存在用户已有修改时：

```text
继续开发
```

而不是：

```text
要求用户先 Commit
要求用户先 stash
自动 reset
自动 checkout
```

除非当前修改确实无法安全继续。

用户已有修改应被视为：

> 需要保护的工作成果。

---

# 4. 不擅自撤销已有修改

禁止为了获得“干净状态”自动执行：

```text
git reset --hard
git checkout -- .
git restore .
git clean -fd
```

以及其他会删除、覆盖或丢失用户修改的操作。

需要撤销 Agent 自己刚刚产生的错误修改时，也应：

> 精确撤销自己负责的部分。

不要顺便恢复整个文件。

---

# 5. 不擅自 stash 用户修改

不要默认执行：

```text
git stash
```

因为 stash：

- 会改变用户当前工作状态；
- 可能包含其他任务；
- 后续恢复可能产生冲突；
- 用户可能不知道自己的修改去了哪里。

确实需要 stash 时，应先说明原因并获得确认。

如果只需要隔离本次 Commit，优先精确 staging，而不是 stash 整个工作区。

---

# 6. 修改文件前先判断是否存在已有变化

准备修改一个已经有未提交 Diff 的文件时，先查看现有变化。

例如：

```text
git diff -- path/to/file
```

区分：

```text
用户已有修改
+
本次任务新增修改
```

不要假设整个文件都属于本次任务。

---

# 7. 保留用户已有修改

修改已有未提交内容时：

- 不覆盖用户改动；
- 不为了自己的实现恢复文件到 HEAD；
- 不把用户改动重新格式化；
- 不因为“顺手整理”修改任务无关部分。

如果本次需求必须修改同一段代码，应：

1. 理解当前工作区版本；
2. 在其基础上继续；
3. 尽量缩小改动范围；
4. Commit 时精确区分本次修改。

---

# 8. Commit 表达逻辑变化

一个 Commit 应回答：

> 这次代码发生了哪一个可以独立理解的逻辑变化？

例如：

```text
feat: add article import persistence
```

表示：

> 增加文章导入所需持久化能力。

而不是：

```text
modify repository files
```

Commit 描述的是：

> 为什么改、改出了什么能力。

不是：

> 改了哪些文件。

---

# 9. 一个 Commit 应尽量保持逻辑完整

通常应让以下内容一起进入同一个 Commit：

```text
实现
+
对应测试
+
必要文档
```

例如：

```text
feat: add admin creation
```

可以同时包含：

```text
API
Service
Repository
Tests
API documentation
```

只要它们共同表达：

> 创建管理员这一项完整能力。

不要因为跨了多个目录就机械拆 Commit。

---

# 10. Commit 不按技术层机械拆分

默认不要这样拆：

```text
Commit 1
add repository

Commit 2
add service

Commit 3
add handler

Commit 4
add tests
```

如果四者只有组合起来才能形成有效业务能力，这种拆法会产生大量：

> 中间 Commit 不完整、无法独立理解

的历史。

优先按业务或自然技术阶段拆分。

---

# 11. 大型需求可以拆多个自然 Commit

如果需求存在真正独立的阶段，可以拆分。

例如：

```text
Commit 1
feat: add article import persistence

- migration
- repository
- storage tests


Commit 2
feat: process article import jobs

- task
- worker
- source client
- service
- worker tests


Commit 3
feat: expose article import API

- handler
- DTO
- frontend integration
- E2E
```

每个 Commit 都应该：

- 有明确目的；
- 具备合理完整性；
- 可以被独立阅读；
- 不只是因为“文件很多”而拆分。

Commit 拆分方案应与 `plan.md` 中确认的 Commit Plan 一致。

---

# 12. 重构和功能开发是否拆 Commit

如果重构只是完成当前功能所必需的小调整：

```text
可以和功能一起提交。
```

如果重构本身是：

- 独立逻辑变化；
- 范围明显较大；
- 不属于功能行为；
- 值得单独 Review；

可以拆成独立 Commit。

例如：

```text
refactor: make article persistence explicit in service
```

然后后续：

```text
feat: add article import flow
```

不要在一个 `feat` Commit 中夹带大量无关历史重构。

---

# 13. 修复问题时 Commit 应表达问题本身

推荐：

```text
fix: preserve import task during shutdown
fix: reject stale article import revisions
fix: rollback admin creation when audit write fails
```

不推荐：

```text
fix: update worker
fix: change logic
fix: bug
```

Commit Message 应让读者不打开 Diff，也大致知道修复了什么。

---

# 14. Commit Message 默认格式

如果项目已有明确规范，遵循项目规范。

没有额外约定时，默认使用：

```text
<type>: <summary>
```

常用 type：

```text
feat
fix
refactor
test
docs
chore
build
ci
```

例如：

```text
feat: add website subscription flow
fix: preserve pending import during shutdown
refactor: make article persistence explicit in service
test: cover stale import completion
docs: document article import lifecycle
```

Summary 应：

- 简短；
- 表达逻辑变化；
- 使用项目已有语言风格；
- 不写句号也可以；
- 不罗列文件名。

---

# 15. 不机械使用 Conventional Commits

`feat / fix / refactor` 等格式用于保持历史清晰。

不要为了格式：

- 把一个逻辑 Commit 强拆多个；
- 给每个小文件修改单独 Commit；
- 创建无意义 `chore`；
- 使用复杂 scope 体系。

项目已有 scope 约定时再使用：

```text
feat(article): ...
```

没有真实需要时：

```text
feat: ...
```

足够。

---

# 16. Commit 前必须检查工作区

准备 Commit 前至少执行：

```text
git status --short
```

并检查：

```text
git diff
```

确认：

- 哪些是本次任务修改；
- 哪些是用户原有修改；
- 是否存在未跟踪文件；
- 是否存在之前已经 staged 的修改。

不要直接进入：

```text
git add .
git commit
```

---

# 17. 默认禁止使用 `git add .`

存在任何可能的混合工作区时，不使用：

```text
git add .
git add -A
```

因为它容易把：

- 用户已有修改；
- 临时文件；
- 数据文件；
- 调试输出；
- 其他任务；

一起提交。

优先：

```text
git add path/to/file1 path/to/file2
```

或者使用：

```text
git add -p
```

进行 hunk 级暂存。

---

# 18. 只 Stage 本次任务拥有的修改

Commit 前建立明确的：

```text
本次任务文件 / hunk 清单
```

然后只暂存这些内容。

例如：

```text
git add \
  internal/service/article/import.go \
  internal/service/article/import_test.go \
  internal/repository/article_import.go
```

如果某个文件同时存在：

```text
用户已有修改
+
本次修改
```

则不能直接：

```text
git add path/to/file
```

把整个文件提交。

应使用：

```text
git add -p
```

或其他可靠的精确 staging 方法。

---

# 19. 混合文件必须按 Hunk 区分

例如：

```text
README.md
```

当前包含：

```text
用户之前新增的数据库报告说明
+
本次新增的文章导入说明
```

本次 Commit 只允许提交：

```text
文章导入说明
```

不能因为都在 README 中，就把整个文件加入 Commit。

判断依据是：

> 逻辑归属，而不是文件归属。

---

# 20. 无法安全拆分时不要猜

如果同一 Hunk 中：

```text
用户修改
+
本次修改
```

已经深度交织，无法可靠区分，不要自行猜测归属。

应先尝试：

- 对照 HEAD；
- 对照任务开始状态；
- 对照 Agent 本次实际修改；
- 精确构造 staged 内容。

仍无法安全确定时，再向用户确认。

确认方式使用：

> 推荐方案 + 选择题。

例如：

```text
README.md 中本次文章导入说明与之前的数据库文档修改位于同一段，
无法安全自动拆分。

A. 本次 Commit 不包含 README，代码先提交
B. 将整段 README 修改一起提交

推荐：A

原因：
- 可以保证本次 Commit 不带入旧修改；
- README 可以之后单独整理。

请选择 A / B。
```

不要问：

```text
这个文件怎么办？
```

---

# 21. Stage 后必须检查 staged diff

完成暂存后必须执行：

```text
git diff --cached
```

或至少：

```text
git diff --cached --stat
git diff --cached --name-only
```

重要 Commit 应阅读完整 staged diff。

确认：

- 只有计划中的修改；
- 没有遗漏关键实现；
- 没有无关代码；
- 没有用户已有修改；
- 没有调试代码；
- 没有密钥；
- 没有临时文件。

Commit 的最终来源是：

> staged diff

不是工作区 Diff。

---

# 22. Commit 前执行 Diff 检查

适用时执行：

```text
git diff --cached --check
```

检查：

- whitespace 错误；
- conflict marker；
- 其他明显 Diff 问题。

同时结合 `testing.md` 确认：

> 对应验证已经完成。

---

# 23. Commit 前验证 staged 内容是否可成立

如果工作区中还有其他未提交修改，而本次只提交其中一部分：

> 当前工作区测试通过

不一定代表：

> 本次 staged snapshot 单独成立。

对于高风险或拆分复杂的 Commit，应考虑验证：

```text
仅 staged 内容构成的快照
```

是否可以：

- build；
- test；
- 正常编译。

尤其在：

```text
本次功能依赖工作区中其他未提交代码
```

时必须检查。

如果当前 Commit 无法脱离其他未提交修改独立成立，应重新评估 Commit 拆分。

---

# 24. 不制造不可构建的中间 Commit

除非项目明确允许，否则一个 Commit 不应该留下明显无法：

```text
build
test
```

的状态。

例如不要：

```text
Commit 1
修改 Service 调用新方法

Commit 2
才新增这个方法
```

如果 Commit 1 无法编译。

Commit 拆分应保持合理的仓库历史完整性。

---

# 25. Commit 授权

默认：

> Agent 修改代码和运行测试，不代表自动获得 Commit 权限。

只有用户明确表达以下意图时才 Commit：

```text
提交
commit
完成后提交
实现并提交
只提交你修改的部分
```

如果用户只是说：

```text
实现这个需求
```

默认：

```text
修改 + 验证
```

完成后等待用户决定是否 Commit。

---

# 26. 已经明确授权 Commit 时不要重复确认

如果用户已经说：

```text
实现并提交
```

那么：

```text
实现
→ 验证
→ 精确 staging
→ Commit
```

即可。

不要完成以后再问：

```text
是否需要我 Commit？
```

除非：

- 工作区归属存在无法解决的冲突；
- Commit 范围需要改变；
- 验证失败；
- 出现可能影响用户已有工作的情况。

---

# 27. Commit 权限不包含 Push 权限

用户说：

```text
提交
commit
```

只代表：

```text
创建本地 Commit
```

不代表：

```text
git push
```

Push 必须单独明确授权。

同样：

```text
push
```

不自动包含：

- 创建 PR；
- Merge；
- Deploy。

---

# 28. Push 前必须确认目标

获得 Push 授权后，先确认：

```text
当前分支
remote
upstream
待推送 commits
```

必要时：

```text
git status
git branch --show-current
git remote -v
git log @{u}..HEAD
```

不要猜：

```text
应该 push origin main
```

尤其不要直接向：

```text
main
master
release
production branch
```

推送，除非当前工作流明确如此。

---

# 29. 默认禁止 Force Push

没有明确授权时，不执行：

```text
git push --force
git push -f
```

如果确实需要改写自己分支的远程历史，优先：

```text
git push --force-with-lease
```

但仍然需要明确授权。

不要使用裸 `--force` 覆盖远程他人修改。

---

# 30. 默认不 Rewrite 历史

没有明确要求时，不执行：

```text
git rebase
git rebase -i
git commit --amend
git reset --soft
git reset --mixed
git reset --hard
filter-branch
filter-repo
```

来“整理历史”。

已经存在的 Commit 默认视为不可随意修改。

如果用户明确要求：

```text
整理 commits
合并 commits
修改上一条 commit
```

再执行对应历史操作。

---

# 31. 不自动 Amend

即使刚刚的 Commit 有一个小问题，也不要默认：

```text
git commit --amend
```

因为用户可能已经：

- 查看了 Commit；
- 基于它继续工作；
- 推送到远程。

默认创建新的修正 Commit，或者先根据用户要求决定。

如果 Commit 明确由当前 Agent 刚刚创建、尚未推送，并且用户明确要求：

```text
修正刚才的提交
```

才可以考虑 amend。

---

# 32. 不自动 Squash

多个 Commit 是否 squash 属于历史组织决定。

Agent 不因为：

```text
看起来更整洁
```

就自动 squash。

Plan 中可以规划：

```text
最终一个 Commit
```

但实现过程中产生多个临时 Commit 时，是否整理需要遵守用户和项目工作流。

---

# 33. 分支操作需要谨慎

不要为了每个任务自动：

```text
git checkout -b ...
git switch -c ...
```

如果用户已经在合适分支上，直接开发。

只有：

- 用户要求；
- 项目工作流明确要求；
- 当前分支明显不适合直接修改；

时再创建分支。

---

# 34. 不自动切换用户当前分支

用户当前分支可能包含未提交工作。

没有明确原因，不执行：

```text
git checkout other-branch
git switch other-branch
```

切换分支前必须确认：

- 当前未提交修改是否安全；
- 是否会产生冲突；
- 用户是否希望离开当前分支。

---

# 35. 分支命名遵循项目约定

如果项目已有：

```text
feature/...
fix/...
refactor/...
```

等规则，沿用。

没有约定时，不需要为了一个本地任务强制建立复杂命名体系。

---

# 36. Merge / Rebase 不属于普通开发步骤

实现一个功能默认不需要：

```text
merge main
rebase main
```

除非：

- 用户要求同步最新代码；
- 当前分支无法继续；
- 项目流程要求。

不要为了“保持最新”擅自改变分支历史。

---

# 37. 出现冲突时不要盲目解决

Merge / Rebase / Cherry-pick 出现冲突时：

1. 阅读冲突双方；
2. 理解各自业务意图；
3. 结合当前需求解决；
4. 运行相关测试。

不要：

```text
全部选择 ours
全部选择 theirs
```

来快速消除冲突。

如果两边表达互斥业务决定，应向用户确认。

---

# 38. 不自动 Cherry-pick 不明 Commit

用户提供一个 Commit Hash 并不一定意味着：

```text
请 cherry-pick。
```

先理解用户意图。

明确要求 cherry-pick 时，再执行。

---

# 39. 不提交敏感文件

Commit 前检查：

- `.env`
- 密钥；
- Token；
- Credential；
- 私钥；
- 数据库文件；
- 用户数据；
- 临时导出；
- 日志；
- 调试抓包；
- 本机绝对路径配置。

这些文件不应因为：

```text
git status 中出现
```

就自动提交。

必要时同步 `.gitignore`，但不要借当前任务大范围重写忽略规则。

---

# 40. 不提交本机专属配置

例如：

```text
本地 Codex MCP 绝对路径
本地虚拟环境
IDE workspace 私人配置
个人 token
机器专属 cache
```

除非项目明确要求版本管理。

如果某工具同时需要：

```text
共享项目配置
+
本机配置
```

应区分两者。

---

# 41. 生成文件按项目约定处理

遇到：

- generated code；
- schema report；
- lock file；
- compiled assets；
- documentation generator output；

先检查项目是否要求提交。

不要因为：

```text
是自动生成的
```

就一定忽略。

也不要因为：

```text
git status 出现
```

就一定提交。

以项目契约为准。

---

# 42. Lock File 与依赖声明保持一致

修改依赖时，如果项目要求提交 Lock File，应与依赖声明一起提交。

例如：

```text
go.mod
go.sum
```

属于同一个依赖变化。

不要：

```text
Commit 1 修改 go.mod
Commit 2 才补 go.sum
```

如果这样会让中间状态不完整。

---

# 43. Migration 与代码的 Commit 组织

新增数据库能力时，Migration 是否与业务代码同 Commit，取决于逻辑完整性。

如果：

```text
Migration + Repository + Service
```

共同形成一个不可分割的能力，可以一起提交。

大型需求也可以先提交：

```text
feat: add article import persistence
```

包含：

```text
migration
repository
storage tests
```

再提交消费该能力的业务流程。

判断标准：

> 每个 Commit 是否是清晰、可工作的逻辑阶段。

---

# 44. 测试应与实现一起提交

默认：

```text
实现代码
+
对应测试
```

属于同一个逻辑 Commit。

不要习惯性：

```text
Commit 1 实现
Commit 2 补测试
```

除非：

- 测试本身是独立任务；
- 补历史缺失测试；
- 项目明确采用测试先行且中间 Commit 有价值。

---

# 45. 文档与行为变化保持同步

如果本次修改改变：

- API；
- 配置；
- 数据库；
- 使用方式；
- 运行命令；
- 架构契约；

必要文档应与对应逻辑变化一起提交。

不要留下：

```text
代码已经改变
README 还描述旧行为
```

但也不要因为改一个局部功能：

```text
顺便重写整个 README
```

---

# 46. Commit 前不自动格式化整个仓库

只格式化：

```text
本次实际修改的代码
```

或者使用项目已有不会产生无关大范围变化的统一入口。

不要因为：

```text
gofmt ./...
prettier .
```

导致大量与任务无关的 Diff，然后一起提交。

---

# 47. Commit 前检查新文件

特别检查：

```text
?? untracked files
```

确认每一个新文件：

- 是否属于本次任务；
- 是否应该版本管理；
- 是否包含临时内容。

不要忽略 untracked 文件，因为真正的新实现经常就在其中。

也不要把所有 untracked 文件自动 stage。

---

# 48. Commit 后必须核对结果

Commit 后至少检查：

```text
git status --short
git show --stat --oneline HEAD
```

必要时：

```text
git show --name-only HEAD
```

确认：

- Commit 创建成功；
- Commit 范围正确；
- staging area 没有残留；
- 用户其他修改仍然存在；
- 没有意外文件进入 Commit。

---

# 49. Commit 后不要声称工作区必须干净

如果任务开始时用户已有修改，Commit 后：

```text
git status
```

仍然存在修改是正常的。

应该说明：

```text
本次修改已提交；
其他已有修改仍保留在工作区。
```

不要把：

```text
working tree clean
```

当作成功标准。

成功标准是：

> 本次 Commit 范围正确，并保留其他工作。

---

# 50. Commit 结果汇报

创建 Commit 后至少报告：

```text
Commit
<hash>
<message>
```

并简要说明：

- 逻辑范围；
- 是否还有未提交修改；
- 是否 Push。

例如：

```text
已提交：

1d1d5d1
refactor: make article persistence explicit in service

包含：
- Article Service 显式编排文章与正文写入；
- Repository 单项持久化拆分；
- 对应事务和回归测试；
- 相关契约文档。

工作区仍有此前的数据库报告修改，未包含。
未 Push。
```

不需要重新粘贴整个 Diff。

---

# 51. 如果没有 Commit 权限

如果用户没有要求 Commit，交付时说明：

```text
代码和验证已完成，当前未创建 Commit。
```

不要主动：

```text
为了方便帮你提交了。
```

---

# 52. 如果 Commit 失败

例如：

```text
pre-commit hook failed
Git identity missing
staged validation failed
conflict
filesystem error
```

应先解释失败原因。

能在当前任务范围内安全修复的：

```text
修复
→ 重新验证
→ 再 Commit
```

需要用户决定的，使用：

> 推荐方案 + 选择题。

不要：

- `--no-verify` 跳过 Hook；
- 修改 Hook；
- 删除检查；

只为了完成 Commit。

---

# 53. 默认不使用 `--no-verify`

禁止默认：

```text
git commit --no-verify
```

或者：

```text
git push --no-verify
```

项目 Hook 属于开发流程的一部分。

Hook 失败应处理失败原因。

只有用户明确授权绕过，并理解影响时才使用。

---

# 54. Git Hook 不代替正式验证

Commit Hook 通过只说明：

> Hook 配置的检查通过。

不能自动替代 `testing.md` 中要求的：

- tests；
- build；
- race；
- E2E；
- migration；
- design review。

反过来，测试通过也不能成为跳过 Hook 的理由。

---

# 55. Agent 自己产生的临时文件必须清理

开发过程可能产生：

```text
/tmp output
debug logs
temporary fixtures
generated preview
test database
coverage file
```

任务结束前应检查并清理不应版本管理的临时产物。

不要把开发垃圾留在工作区，让用户自己判断。

---

# 56. 不操作用户真实数据来整理 Git

Git 操作不得为了：

```text
让 status 看起来干净
```

而删除：

- 数据库；
- 上传文件；
- Volume；
- 配置；
- 用户生成内容。

Git 工作区管理和业务数据管理是两件事。

---

# 57. Plan 中的 Commit 设计必须在实施后复核

如果 `plan.md` 规划：

```text
Commit 1
Commit 2
Commit 3
```

实现完成后应根据真实 Diff 再检查：

> 原拆分是否仍然合理？

如果实际实现证明：

```text
Commit 1 和 Commit 2 无法独立成立
```

不要为了服从旧 Plan 强行制造坏 Commit。

可以调整 Commit 组织，但应说明原因。

Plan 是设计依据，不是机械束缚。

---

# 58. 一个好的 Commit 应能被独立 Review

Reviewer 查看单个 Commit 时，应该基本能够回答：

```text
为什么改？
改了什么？
对应测试在哪里？
有没有隐藏无关修改？
```

如果一个 Commit 同时包含：

```text
文章导入
重写用户设置
升级 20 个依赖
格式化整个项目
```

说明范围不清晰。

---

# 59. 一个好的 Commit 应方便回退

Commit 应尽量使：

```text
git revert <commit>
```

能够撤回一个明确逻辑变化。

这不是要求每个 Commit 完全无依赖。

而是避免：

> 多项毫无关系的变化被绑在一起，导致无法安全回退其中一个。

---

# 60. 不为了 Atomic Commit 过度切碎

“一个 Commit 一个逻辑变化”不等于：

```text
一个函数一个 Commit
一个文件一个 Commit
一个测试一个 Commit
```

过度切碎会让历史难以阅读。

更重要的是：

> 业务或技术意图是否完整。

---

# 61. 文档型 Commit 可以独立存在

如果任务只是：

```text
完善规则
补 README
更新架构说明
```

可以使用：

```text
docs: ...
```

如果文档只是某项功能变化的必要同步：

> 与功能 Commit 一起提交通常更清晰。

根据逻辑归属决定。

---

# 62. Refactor 不应偷偷改变行为

标记为：

```text
refactor:
```

意味着主要目标是：

> 改变内部结构，而不是改变外部业务行为。

如果实际修改了：

- API；
- 状态；
- 错误；
- 数据语义；
- 用户行为；

Commit Message 不应伪装成纯 refactor。

应使用更准确类型，或者拆分。

---

# 63. Fix 必须对应可描述的问题

`fix:` 应能够回答：

> 修了什么错误行为？

例如：

```text
fix: keep article import pending after shutdown
```

而不是：

```text
fix: improve logic
```

如果只是代码清理，不使用 fix。

---

# 64. Feat 表示可观察的新能力

`feat:` 通常用于：

> 用户、调用方或系统新增了一项可观察能力。

例如：

```text
feat: add article URL import
feat: support website subscriptions
```

内部纯重构不要使用 feat。

---

# 65. 测试和文档变化不要掩盖业务变化

如果一个 Commit 真正增加了业务能力，同时包含测试和文档：

推荐：

```text
feat: add article import
```

而不是：

```text
test: add article tests
```

Commit 类型表达主要逻辑变化。

---

# 66. Git 操作中的确认方式

遇到需要用户决定的 Git 问题时，使用：

> **推荐方案 + 选择题**

例如：

```text
当前工作区有两组修改：

A. 本次文章导入功能
B. 之前未提交的 EPUB 修改

这次 Commit 怎么处理？

A. 只提交文章导入
B. 两组一起提交

推荐：A

原因：
- 两组修改逻辑独立；
- 可以保持 Commit 范围清晰；
- EPUB 修改继续保留在工作区。

请选择 A / B。
```

不要只问：

```text
这些修改怎么提交？
```

---

# 67. 不重复询问已有明确意图

如果用户刚刚说：

```text
只提交你修改的部分
```

则直接按照该要求操作。

不要再问：

```text
要不要把其他修改一起提交？
```

除非：

> 当前文件修改已经无法安全区分。

用户明确要求优先于默认规则。

---

# 68. 交付前 Git 检查清单

在涉及 Commit 的任务结束前至少确认：

## 工作区

- 是否读取了当前 `git status`？
- 是否识别用户已有修改？

## Scope

- staged 内容是否全部属于当前任务？
- 是否遗漏当前任务必要文件？
- 是否夹带无关文件？

## Diff

- 是否查看 staged diff？
- 是否执行适用的 diff check？
- 是否有敏感信息或调试内容？

## Validation

- 当前 Commit 对应验证是否通过？
- 部分 staging 时，Commit 是否能独立成立？

## Commit

- Message 是否表达逻辑变化？
- Commit 是否与 Plan 的逻辑范围一致？

## After Commit

- 是否核对 Commit 内容？
- 用户其他修改是否仍存在？
- 是否明确没有 Push？

---

# 69. 最终目标

Git 历史应该让人能够顺着理解：

```text
项目是如何一步一步演进的
```

而不是只能看到：

```text
update
fix
more changes
final fix
```

Agent 使用 Git 的最终目标是：

> **安全地保护用户工作，
> 精确地管理自己产生的修改，
> 用清晰的 Commit 表达软件的逻辑演进。**

理想流程：

```text
开始任务
↓
检查已有工作区
↓
开发并保留用户修改
↓
按照 Plan 完成验证
↓
确认任务 Diff
↓
精确 Stage
↓
检查 Staged Diff
↓
Commit
↓
核对 Commit
↓
保留其他未提交工作
```

而不是：

```text
开发完成
↓
git add .
↓
git commit
```
