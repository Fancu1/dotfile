---
description: Rule-driven skill dispatch (automatic but constrained)
globs: ["**/*"]
alwaysApply: true
---

# Skill 调度规则（自动，但受控）

目标：让 Codex 在**关键任务类型**上自动用“专家 skill”提高一致性，同时避免“随便调用 skill”导致的不可预测行为。

## Non-Negotiable
- **只能使用“已加载 rules 明确指定/允许”的 skill**。
- 未被允许的 skill：不得临时加用（除非用户明确要求）。

## 调度来源（按优先级）
1) **已加载 rules 的 `Skill Policy`**（优先使用更具体的场景 rule；例如 PRD/Plan/Review）
2) 若当前 loaded rules 未覆盖：使用 `13-skill-recommendations.md` 的路径/任务映射（兜底）
3) 若仍无法判定：不调用 skill，仅按 rules 执行，并在 Open Questions 里说明缺口

## 多规则 Skill Policy 合并（确定性算法）
当多个已加载规则同时声明了 `Skill Policy`：
1) 先按优先级裁决（见 `AGENTS.md`）：Task-specific > Scenario > Tech-specific > Quality > Core/General
2) 生成集合：
   - Never：高优先级规则声明的 `Never Use` 优先；命中则禁止使用（即使低优先级写了 Must）
   - Must：只保留“当前要交付的输出阶段”需要的 Must（例如：写 PRD 用 PRD skill；写 Plan 用 Plan skill；做 Review 用 Review skill）
   - May：作为候选补强 skill，仅在能提升质量且不引入冲突时取 0-1 个
3) 若出现“同一阶段”同时存在多个 Must 且互斥：必须在 Conflicts/Gaps 里说明，并 Ask First 给出取舍选项。

## Skill 不存在/不可用（自动恢复）
- 若被指定为 Must Use：
  - **优先自动安装**（仅 allowlist 仓库：`openai/skills`、`ComposioHQ/awesome-codex-skills`、`feiskyer/codex-settings`、`obra/superpowers`）。
  - 若无法安装：降级为纯 rules 执行，并在最终输出标注“缺少 skill 的影响（质量/覆盖范围）”。
- 若只是 May Use：跳过并继续，不视为失败。

## 高风险/外部副作用技能（默认禁止自动调度）
以下类型 skill **不得通过兜底映射自动触发**；仅在用户明确要求（点名 skill 或明确说要执行对应外部动作）且遵循 `00-general.md` 的 Dry-run/Ask First 后才允许使用：
- 外部系统集成/改动：`connect`, `connect-apps`, `linear`
- 可能引入不可预测执行流或额外成本：`autonomous-skill`, `claude-skill`

## 多 skill（顺序与最小集）
- 默认只取**最小集合**（通常 1 个主 skill + 0-1 个补强 skill）。
- 建议顺序（从左到右执行）：Research → Spec/PRD → Plan → Implement → Verify → Review。
- 若多个 skill 的输出格式冲突：以更具体的场景 rule 为准，并在 Conflicts/Gaps 里说明裁决。

## 输出约束
- 在 Start-of-Task Header 中增加一行：`Skill Dispatch: <skills> (why)`
- 在正文第一次落地输出前，用 1 句话声明“正在使用哪些 skill 以及原因”。
