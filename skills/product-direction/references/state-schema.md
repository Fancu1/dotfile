# 产品方向全局状态

默认状态根：`~/.codex/state/product-direction/`。若该目录与项目根重叠，自动使用 `~/.codex-state/product-direction/`；只有 fallback 仍重叠时才请求用户提供安全位置。仅在用户明确执行产品方向分析时创建。状态根必须是目录；用户指定的替代路径也按目录解释。若候选路径已是普通文件则停止，不覆盖、不追加，也不得把本次报告写成该路径本身。已存在的状态根目录必须保留，不得通过删除、替换、移动或先清空目录来生成单文件结果。

```text
INDEX.md
projects/<project-id>/
├── PROJECT.md
├── STATE.md
├── CAPABILITIES.md
├── EVIDENCE.md
├── OPPORTUNITIES.md
├── DIRECTION.md
└── reviews/<YYYY-MM-DD>-<short-commit>.md
```

同日同 commit 已有报告时追加 `-02`、`-03`。非 Git 项目使用 `nogit`。创建目录前解析项目根与候选状态根的真实路径；对于不存在目录，解析最近存在父目录后拼回剩余路径。默认目录重叠时先尝试上述 fallback；fallback 或用户指定目录仍重叠时拒绝写入。一次成功运行至少应产生或协调根 `INDEX.md`、项目当前状态文件和一份 `reviews/` 报告；单个汇总文件不满足状态契约。

## 项目 ID

Git remote 按目标分支 upstream remote、`origin`、remote 名字典序第一项选择，只读本地配置。将 SCP/SSH/HTTP(S) URL 归一为 `<lowercase-host>/<path-without-leading-slash-or-.git>`，移除 scheme、凭证、端口、query、fragment、末尾斜杠和 `.git`；无法安全解析时使用无 remote 规则。

哈希输入为 UTF-8 精确字符串：

- 有 remote：`git:<canonical-remote>|repo:<repo-name>`。
- 无 remote：`git-roots:<sorted-root-commits>|repo:<repo-name>`。
- 用户明确独立跟踪逻辑子项目：在父输入追加 `|scope:<normalized-relative-path>`。
- 非 Git：`path:<normalized-real-path>|project:<project-name>`。

逻辑相对路径以 Git 顶层为基准，统一 `/`、折叠 `.` 与重复分隔符、保留大小写并移除首尾 `/`；拒绝空路径、绝对路径和包含 `..` 的结果。项目 ID 为清理后的项目名加 SHA-256 前 8 位。仓库内普通子目录沿用父仓库身份，不静默建立逻辑子项目。

## INDEX.md

```markdown
# Product Direction Index

| Project ID | Product | Known paths | Last review | Current direction | Open opportunities | Evidence to refresh |
|---|---|---|---|---|---:|---|
```

## PROJECT.md

记录项目身份、已知路径、产品承诺、目标用户、核心任务、阶段、约束、明确非目标、核心旅程、可用反馈或数据入口和未知项。路径和产品事实变化时增量更新，不把推论写成定位事实。

## STATE.md

```markdown
# Direction State

- Last reviewed at:
- Last reviewed commit:
- Working tree observed: clean | dirty | unavailable
- Working tree evidence: none | <report-relative-path#section>
- Product understanding confidence: high | medium | low | unknown
- Next capability gap:
- Next user question:
- External evidence to refresh:
- Known limitations:
```

## CAPABILITIES.md

```markdown
# Capabilities

| Capability | User task | Status | End-to-end | Discoverable | Trustworthy | User validated | Evidence | Revisit when |
|---|---|---|---|---|---|---|---|---|
```

`Status` 使用 `implemented / in-progress / planned / unknown`。代码存在不等于端到端可用、容易发现或经过用户验证。

## EVIDENCE.md

使用稳定 ID `EV-0001`，记录：类型 `fact / inference / hypothesis / decision`、摘要、来源或路径、观察日期、关联 commit、置信度、时效状态、支持/反对的机会和刷新条件。不得保存原始敏感反馈或大段源码。

## OPPORTUNITIES.md

使用稳定 ID `PD-0001`，按用户问题和产品矛盾去重。状态使用 `proposed / selected / validating / deferred / rejected / shipped / superseded`。记录目标用户、问题、证据、与现有能力关系、推荐目标、克制边界、最小验证、成功信号、风险、用户决定和历史。

用户可用自然语言引用机会；ID 只用于内部连续性。用户未明确选择时不得标为 `selected`。

## DIRECTION.md

保存当前产品诊断、主要方向、最多两个备选、克制清单、最小验证、证据边界和下一次重新判断条件。它是当前摘要，不覆盖 append-only 报告和机会历史。

## 写入顺序

1. 完成分析、证据分类和机会去重。
2. 写入 append-only review 报告。
3. 更新 PROJECT、STATE、CAPABILITIES、EVIDENCE、OPPORTUNITIES、DIRECTION。
4. 最后更新 INDEX。

任一步失败时停止后续写入并报告部分结果；不得删除旧报告来恢复一致性。
