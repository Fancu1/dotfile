---
description: High-quality default workflow for product/dev/refactor/debug tasks (phase gates + skill dispatch)
globs: ["**/*"]
alwaysApply: true
---

# 高质量工作流（默认）

目的：把常见高价值工作（需求/开发/重构/排障/调研/代码管理）变成可重复、可验收的流水线；用 skill 提高一致性，用 gates 防止跳步。

## 任务分类（必须先判定）
在开始前，必须将本次任务归为以下之一，并在 Start-of-Task Header 写出：
- **Feature**：新功能/新需求/产品行为变更
- **Bugfix**：修 bug/回归/线上故障定位与修复
- **Refactor**：重构/整理/抽象/性能优化（不改外部行为或尽量不改）
- **Research**：竞品/资料/方案对比调研
- **Ops**：CI/PR 评论/Release notes/工具集成等代码管理
- **Other**：不适用本工作流（按具体 rules 执行）

若用户明确说“只要一个快速回答/只改一行/跳过文档”，则缩减流程；但必须保留必要 gates（验证/回归/风险说明），并在最终输出记录“跳过了哪些环节以及风险”。

## Vibe Coding 默认策略（高自治 + 低打扰）
- 默认少问：**最多 3 个阻塞问题**（会改变验收口径/安全边界/是否 Ask First 才能继续的那种）；其余写进 Assumptions 并继续推进。
- 默认给选项：每个阻塞点给 2-3 个可选项（含默认选项），若用户未回答则按默认选项推进，并在最终交付显式记录。
- 仍遵守 Ask First：新依赖/破坏兼容/大重构/长时间服务/生产与外部副作用，必须停下确认（见 `10-core.md` 与 `00-general.md`）。

---

## Feature 工作流（默认：先 PRD/Plan，再编码）
### Phase 0：需求澄清（最多 3 个问题）
Skill Policy（Auto）：
- May Use: `brainstorming`（需求不清晰/取舍明显时）

规则：
- 只问会改变验收口径的问题；其余写进 Assumptions。
- 给 2-3 个可选项让用户选，减少来回。

### Phase 1：调研与对比（按需）
Skill Policy（Auto）：
- May Use: `deep-research`（需要竞品/类似项目对比、或信息不确定且影响方向时）

最低标准（若启用）：
- 至少 3 个竞品/类似项目（带链接）
- 维度对比表（至少 3 个维度）
- 明确“借鉴点/不做点/取舍”

### Phase 2：产出 PRD（必须先于编码）
Skill Policy（Auto）：
- Must Use: `kiro-skill`

产出标准：
- 遵循 `50-prd.md` 的 1-13 结构与 Self-Check
- 禁止写实现细节；只写行为契约与验收契约

Gate：PRD 完成后必须执行 `52-prd-audit.md`，FAIL 则按 Minimal Patch List 修到 PASS 为止。

### Phase 3：产出 Plan（必须先于编码）
Skill Policy（Auto）：
- Must Use: `writing-plans`
- May Use: `backend-development` / `database-design` / `frontend-design` / `webapp-testing`（按任务触发）

产出标准：
- 遵循 `51-plan.md` 的 1-13 结构
- 任务必须可执行：Goal / Touch / Steps / Tests / Verification
- 必须包含：验收、Self-test、Review 步骤

Gate：Plan 完成后必须执行 `53-plan-audit.md`，FAIL 则按 Minimal Patch List 修到 PASS 为止。

### Phase 4：实现（按 Plan 执行）
Skill Policy（Auto）：
- Must Use: `test-driven-development`（新增/改动核心逻辑时）
- May Use: `executing-plans`（当 Plan 任务 > 5 个或跨模块时）

实现规则（默认）：
- 按 `00-general.md` 使用 git worktree 隔离开发与验证；默认以 PR 合并为交付（或用户确认后本地 merge），避免把 WIP 合到主线。

### Phase 5：验证与评审（交付前强制）
规则：
- 按 `20-testing-and-verification.md` 跑验证闭环，产出 Verification Evidence。
- 当有代码/配置/行为变更且验证通过：按 `25-review-and-quality.md` 做资深 Review（审计问题优先于总结）。

---

## Bugfix 工作流（先复现与根因，再修复）
Skill Policy（Auto）：
- Must Use: `systematic-debugging`
- Must Use: `verification-before-completion`

最低标准：
- 明确复现步骤或失败信号（日志/错误/断言/截图）
- 根因定位（不是“可能是”）
- 最小修复 + 回归验证（至少 1 条 fast check）
- 交付前：按 `20-testing-and-verification.md` 输出证据；验证通过后按 `25-review-and-quality.md` 做 Review

---

## Refactor 工作流（先定边界与验证，再动手）
Skill Policy（Auto）：
- Must Use: `writing-plans`（先写最小可执行 Plan）
- May Use: `test-driven-development`（涉及核心逻辑时，先补测试再重构）

最低标准：
- 明确“不改什么”（外部契约/行为）以及如何证明没变（测试/对照）
- 分批提交，避免大范围 churn
- 交付前：按 `20-testing-and-verification.md` 输出证据；验证通过后按 `25-review-and-quality.md` 做 Review

---

## Research 工作流（证据驱动）
Skill Policy（Auto）：
- Must Use: `deep-research`

最低标准：
- 来源可追溯（链接/日期）
- 结论可复核（引用对上原文）
- 输出“可执行建议”，而不是资料堆砌

---

## Ops 工作流（代码管理/集成）
Skill Policy（Auto）：
- CI 失败排查：Must Use `gh-fix-ci`
- PR/Issue 评论处理：Must Use `gh-address-comments`
- 变更日志/Release notes：Must Use `changelog-generator`
- MCP/协议/外部 API 集成：Must Use `mcp-builder`

---

## 最终交付（必须包含）
- 任务分类（Feature/Bugfix/Refactor/Research/Ops/Other）
- Skill Dispatch 记录（用到哪些 skill）
- Verification Evidence（命令 + 结果摘要）
