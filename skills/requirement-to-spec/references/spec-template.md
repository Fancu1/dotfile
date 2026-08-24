# Requirement implementation specification template

Use concise, plain language for both developers and implementation agents. Include only decision-relevant facts. Omit optional sections that have no content rather than filling them with boilerplate.

Write each fact, exclusion, and rationale once. Let later sections reference the established boundary implicitly instead of repeating the same list. For a small change, keep each section to a short paragraph, a compact table, or a few bullets unless additional detail prevents a real implementation decision.

## 1. Interactive confirmation card

Use one card per main decision. Keep it to no more than five short bullets and one question.

```markdown
### 本轮确认：<要决定的事情>

- 目标：<这项决定服务的当前结果>
- 建议：<现在采用的方案>
- 当前不做：<明确后置或排除的内容>
- 原因：<最关键的必要性和取舍依据>
- 结构影响：<无／修改哪些现有职责／新增什么边界>

需要你确认：<一个清晰问题>
```

Lead with the recommendation. Do not paste the full internal analysis unless the user asks. When the user confirms, replace the current conclusion in the working context and move to the next unresolved decision.

## 2. Final specification

Use the title `# 需求实现规格：<需求名称>`.

### 需求与当前问题

Explain what the user wants to accomplish, what happens now, and why the difference matters. Use plain language before technical terms, files, or abstractions.

### 当前项目事实

List only verified facts and constraints that influence the solution. Mark material inferences and unresolved unknowns explicitly. Do not summarize the whole repository.

### 目标与非目标

State observable goals and explicit non-goals. Make deferred adjacent capabilities clearly distinguishable from the delivery target.

### 必要性判断

For every disputed or scope-expanding candidate, record:

```markdown
#### <候选项> — <当前必须实现／当前只做最小版本／明确后置／本次不做>

- 判断依据：关系=<...>；证据=<...>；不做后果=<...>；后补成本=<...>；结构影响=<...>；更小方案=<...>
- 原因：<为什么属于这个结论>
- 后置条件：<仅后置项填写，说明什么事实出现时重新评估>
```

Keep obvious, low-impact items brief. Never show a numeric score or derive a total score.

Group closely related deferred items instead of giving each mature-system capability its own subsection. Omit hypothetical future concerns that do not change the current plan.

### 外部参考与取舍

Include only when research changed or confirmed a decision. For each influential reference, state the relevant mechanism, prerequisites, what is adopted, and what is rejected as too heavy. Do not write a general competitor survey.

### 推荐实现方案

Describe the core behavior, responsibility flow, state or data changes, and main trade-off. Include at most one strong alternative. Use short pseudocode only when it removes a material ambiguity; do not provide production code.

### 模块与职责

Name only affected modules and describe what each owns after the change. Preserve existing ownership where suitable, but do not copy accidental boundaries.

### 目录改动前后

Show only the relevant subtree before and after the change. Do not paste the complete repository tree. Make created, moved, merged, or deleted paths obvious.

### 文件级变更计划

Use a compact table:

```markdown
| 文件 | 动作 | 职责 | 大致改动 |
|---|---|---|---|
| `path/to/file` | 修改／新建／移动／合并／删除 | <该文件负责什么> | <行为级逻辑，可列必要的函数名> |
```

Do not write line-by-line patches. Allow a cohesive file to remain large. Add function names only when they help an implementer locate a responsibility; do not invent unnecessary helper functions.

Include only files that implement required behavior, prove acceptance, preserve a hard contract, or were explicitly requested. Do not add README, changelog, cleanup, formatting, or configuration work by convention.

### 最低保障

List only core-path blockers, irreversible data risks, existing hard contracts, and minimum recovery behavior. Do not create a standalone exhaustive failure catalogue.

### 伴随结构调整

Include only requirement-coupled deletion, movement, merge, abstraction removal, or small refactor. For each adjustment, state:

- Why the current requirement needs it.
- Relevant directory shape before and after.
- Affected files and actions.
- Why a wider cleanup is not included.

Omit this section when no accompanying structural adjustment is necessary.

### 实施顺序与提交边界

Order behavior in runnable or verifiable semantic steps. Each prospective commit should complete one thing, but do not prescribe commit titles. Align every step with the file plan, and normally include its focused tests in the same step.

### 验收与验证

Use observable outcomes rather than “tests pass” alone:

```markdown
| 场景 | 输入或前置条件 | 操作 | 可观察结果 | 证明方式 | 通过标准 |
|---|---|---|---|---|---|
| <场景> | <条件> | <动作> | <用户或系统能观察到什么> | <测试、命令或人工检查> | <明确判定> |
```

Distinguish focused tests, broader regression checks, build or static checks, and actual runtime verification. Do not claim a verification that has not been performed.

## 3. Final consistency check

Before delivery, ensure:

- Goals, necessity decisions, solution, file plan, implementation order, and acceptance scenarios describe the same scope.
- Every created file, directory, abstraction, safeguard, or adjacent refactor has a current justification.
- Every deferred item includes a reason and reevaluation condition.
- Related deferrals are grouped, and purely hypothetical future caveats are omitted.
- The implementation agent does not need to choose where responsibilities belong or reopen product scope.
- The specification contains no production code, commit titles, broad cleanup plan, or unsupported project fact.
- The same non-goal, rationale, or structural decision is not explained repeatedly across sections.
- Every file action, including documentation and tests, is justified by behavior, acceptance, a hard contract, or an explicit user request.
- No file is written unless the user explicitly requested file output.
