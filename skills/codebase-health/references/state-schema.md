# 全局状态格式

默认状态根：`~/.codex/state/codebase-health/`。仅在用户明确执行代码健康审计时创建。若该目录与项目根重叠，自动使用 `~/.codex-state/codebase-health/`；用户不需要为常见的 `.codex` 自审计手动提供路径。

```text
INDEX.md
projects/<project-id>/
├── PROJECT.md
├── STATE.md
├── COVERAGE.md
├── FINDINGS.md
└── reviews/<YYYY-MM-DD>-<short-commit>.md
```

同日同 commit 已有报告时追加 `-02`、`-03`，不得覆盖历史报告。非 Git 项目使用 `nogit` 代替 commit。

创建任何目录前，先对项目根和候选状态根做真实路径解析。对于尚不存在的状态目录，解析最近的已存在父目录后拼回剩余路径；此检查必须同时覆盖符号链接路径和规范化路径。默认目录重叠时尝试上述 fallback；fallback 仍重叠，或用户明确指定的目录重叠时拒绝写入并请求安全位置。

## 项目 ID 契约

Git remote 按以下顺序选择：目标分支 upstream 所属 remote、`origin`、remote 名字典序第一项。只使用本地 Git 配置，不访问网络；无法得到可用 remote 时进入无 remote 规则。

将常见 SCP/SSH/HTTP(S) remote 归一为 `<lowercase-host>/<path-without-leading-slash-or-.git>`：移除 scheme、用户名、密码、端口、query、fragment、末尾斜杠和 `.git`。不得把原始含凭证 URL 写入状态。无法安全解析时不要猜测，改用无 remote 规则并记录限制。

哈希输入使用 UTF-8 的精确字符串：

- 有 remote：`git:<canonical-remote>|repo:<repo-name>`。
- 无 remote：`git-roots:<sorted-root-commits>|repo:<repo-name>`。
- 显式逻辑子项目：在父项目输入后追加 `|scope:<normalized-relative-path>`。
- 非 Git：`path:<normalized-real-path>|project:<project-name>`。

`normalized-relative-path` 必须相对 Git 顶层目录计算，统一使用 `/` 分隔，折叠 `.` 和重复分隔符，保留大小写，并移除首尾 `/`。空路径、绝对路径或规范化后仍包含 `..` 的路径无效，不创建逻辑子项目身份。

取 SHA-256 的前 8 个小写十六进制字符。显示 ID 为清理后的项目名加短哈希；不同类型不得共用相同哈希输入前缀。

## INDEX.md

```markdown
# Codebase Health Index

| Project ID | Project | Known paths | Last review | Target | Open findings | Next scope |
|---|---|---|---|---|---:|---|
```

路径变化时更新 known paths；同一项目可记录多个 clone/worktree。索引只放摘要。

## PROJECT.md

记录：项目身份依据、清理后的 canonical remote、Git 项目根、已知 clone/worktree 路径、本次范围根、可选的逻辑子项目相对路径与父仓库身份、技术栈、项目目的、模块职责、入口与核心调用链、外部边界、重要不变量、默认排除路径、可用验证命令和仍未知的信息。

用户传入仓库内子目录时，只更新本次范围根，不把它加入独立项目。只有显式启用逻辑子项目跟踪时，才建立独立状态目录。

不要存 remote 中的用户名、Token 或其他凭证。默认排除生成代码、vendor、构建产物、大型夹具和项目明确声明不应人工维护的文件，但保留它们与人工代码的边界检查。

## STATE.md

```markdown
# Review State

- Last review kind: initial | rolling | focused | verification
- Last reviewed at:
- Last target ref:
- Last reviewed commit:
- History status: normal | diverged | unavailable
- Last baseline at:
- Next module candidate:
- Next system lens:
- Last verification summary:
- Working tree snapshot: none | <report-relative-path#section>
- Known limitations:
```

替换过期状态，不追加运行日志。

旧状态中的 `Last mode` 仍可读取；下次成功写入时迁移为 `Last review kind`，不要求用户处理。

显式纳入未提交内容时，在 append-only 报告中记录实际读取文件的相对路径、Git 状态和 SHA-256，并让 `Working tree snapshot` 指向该节。排除敏感文件，且不得存储文件内容。未纳入时写 `none`。

## COVERAGE.md

```markdown
# Coverage

## Module coverage

| Module | Responsibility | Criticality | Depth | Confidence | Last reviewed | Last commit | Revisit when | Next step |
|---|---|---|---|---|---|---|---|---|

## System coverage

| Lens | Status | Confidence | Last reviewed | Evidence/summary | Revisit when | Next step |
|---|---|---|---|---|---|---|
```

置信度使用 `high / medium / low / unknown`。覆盖深度与置信度分开：曾经 deep 的模块也可能因重大变化降为 low。

## FINDINGS.md

按稳定 ID 保存 finding 卡，ID 为项目内递增的 `CH-0001`。创建前按根因、责任边界和受影响行为去重。

允许状态：`new / observing / ready / accepted / declined / resolved / reopened`。保留首次证据和用户决定；后续验证追加简短历史，不改写为仿佛从未出错。

## 写入顺序

1. 完成分析和去重。
2. 写入新的 append-only review 报告。
3. 更新 PROJECT、STATE、COVERAGE、FINDINGS。
4. 最后更新 INDEX。

某一步失败时停止后续写入，报告已成功与未成功的文件；下次从最近报告和当前状态协调，不删除历史。
