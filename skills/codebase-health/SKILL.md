---
name: codebase-health
description: 持续审计代码库的可读性、可维护性、健壮性、测试安全网与架构一致性，结合历史状态覆盖近期代码变化、从未或很久没有 Review 的模块，以及跨模块全局问题。用户明确调用 $codebase-health，或要求定期代码质量 Review、AI 生成代码审计、技术债盘点、重构候选发现、模块健康检查或重构结果复查时使用。
---

# Codebase Health

持续建立对整个代码库的质量认知。默认只读项目代码，只把审计进度、结论和报告写入全局状态目录；发现问题后生成候选，不自动重构。

## 1. 确认意图与写入边界

1. 读取项目适用的 `AGENTS.md`、仓库状态、项目说明和现有验证命令。
2. 用户只要求讨论、分析流程或制定计划时保持完全只读，不创建审计状态。
3. 用户明确调用本 Skill 或要求执行代码健康审计时，可写入状态根目录；不得修改被审计项目、提交、切换分支、拉取远程、创建 PR 或部署。
4. 默认状态根目录为 `~/.codex/state/codebase-health/`。用户明确指定其他状态根时使用指定位置。
5. 写入前解析项目根和状态根的真实路径（含符号链接）。默认状态根与项目重叠时自动改用 `~/.codex-state/codebase-health/`；fallback 仍重叠或用户指定的状态根不安全时才停止并请用户选择项目外目录。
6. 不保存凭证、环境变量值、完整私有源码或不必要的大段代码摘录。

## 2. 理解自然语言入口

用户只需调用 `$codebase-health` 并描述希望检查的项目、模块、问题或历史结论；没有补充时审计当前项目。不要要求用户选择运行模式、记忆 finding ID 或提供固定命令参数。

根据意图与状态自动选择内部路由：

- 没有可信状态时建立项目认知。
- 常规健康检查时执行滚动审计。
- 指定模块、调用链或质量关注点时执行专项审计。
- 询问旧问题是否解决时复查原 finding。

用户偶尔使用旧的模式词时将其视为兼容提示，不主动推荐。用户用自然语言引用历史问题时，先按标题、根因、范围与证据匹配；只有多个 finding 同时合理匹配时才提问。执行前阅读 [references/modes.md](references/modes.md)。

## 3. 识别项目并加载状态

1. 目标路径位于 Git 仓库时，默认以 `git rev-parse --show-toplevel` 得到的仓库根作为项目根；用户传入的子目录只是本次范围，不另建项目身份。
2. 只有用户明确要求把 monorepo workspace 或其他逻辑子项目独立跟踪时，才使用“仓库身份 + 相对路径”生成子项目 ID，并记录父仓库关系；不得根据目录结构静默推断。
3. Git 项目优先以清理凭证后的 canonical remote 和仓库名生成 `<repo-name>-<8-char-sha256>`；remote 选择、归一化和哈希输入必须遵循 [references/state-schema.md](references/state-schema.md) 的确定性契约。不同 clone 和 worktree 共用该项目身份。
4. 无 remote 的 Git 项目使用仓库名和排序后的根提交集合生成 ID；非 Git 项目使用项目名和规范化绝对路径生成 ID。
5. 若身份匹配存在歧义，不静默合并状态；列出候选并请用户选择。
6. 读取全局 `INDEX.md` 与项目目录下的 `PROJECT.md`、`STATE.md`、`COVERAGE.md`、`FINDINGS.md`。文件缺失时按 [references/state-schema.md](references/state-schema.md) 初始化。

## 4. 选择 Review 范围

每次先快速建立全局方向，再组合三条视线：

1. **Change Coverage**：上次审计后的已提交变化、直接调用方、消费者与测试。
2. **Module Coverage**：从未 Review、只做过浅层 Review、结论过期或重要性高的模块。
3. **System Coverage**：依赖方向、领域模型、错误处理、配置、状态、测试链路等跨模块问题。

不要求每次完整覆盖三条线，但必须逐条考虑、说明本次选择和延期项。具体优先级、Git 分叉处理与覆盖失效规则见 [references/coverage-and-scope.md](references/coverage-and-scope.md)。

## 5. 执行有证据的审计

按当前范围读取定义、调用链、消费者、测试、配置和必要的版本历史。使用 [references/quality-lenses.md](references/quality-lenses.md) 选择相关视角。

- 区分已验证事实、推断和未知项。
- 大文件、复杂度、重复或样式问题只能触发调查，不能单独构成候选。
- 没有具体证据或真实维护成本的问题保留为观察，不包装成确定结论。
- 不通过修改代码、弱化测试或运行有副作用的修复来证明问题。

## 6. 记录结果与交接

1. 先在内存中完成去重和结论，再写本次 append-only 报告，随后覆盖更新当前状态与全局索引。
2. 每份报告最多推荐 1 个主要候选和 2 个次级候选；没有实质发现时明确写“本次无需行动”。
3. 对同一根因更新原 finding，不创建措辞不同的重复项。
4. 仅根据用户明确决定更新 `accepted` 或 `declined`；复查旧结论时可更新为 `resolved`、`observing` 或 `reopened`。
5. 候选、报告、状态更新和 `$dev-workflow` 交接卡格式见 [references/findings-reports-handoff.md](references/findings-reports-handoff.md)。
6. 需要实施时只输出交接卡并建议调用 `$dev-workflow`；不得自动进入代码修改阶段。

## 7. 完成判定

仅在以下条件满足时结束：本次范围及选择理由清楚；三条覆盖视线均已考虑；证据与未知项已区分；历史 finding 已去重并更新；延期范围和下次建议已记录；项目源码保持不变；状态与报告写入结果已说明。
