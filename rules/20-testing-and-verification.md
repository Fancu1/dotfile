---
description: Mandatory verification loop after behavior changes (test -> fix -> retest)
globs: ["**/*"]
alwaysApply: true
---

## Skill Policy（Auto）
- Must Use: `webapp-testing`（当涉及 UI/交互变更且需要浏览器验收时）
- May Use: `verification-before-completion`（修复 bug / 回归风险较高时，用于完成前复核）

## Scope
- Applies when: 任何代码/配置/行为/契约/UI 变化
- Does NOT apply when: 纯文档（且不影响行为契约）

## Outputs
- Expected output: 列出运行的命令、通过标准、实际结果摘要；失败则给根因与修复记录
- Minimum verification evidence: 至少 1 条可执行命令或明确说明为什么不能执行

## Ask First
- Situations: 需要启动长时间服务/重建全量环境/引入新测试基础设施

## Non-Negotiable Verification Loop
1) 选择验证命令（优先使用 `90-project-profile.md` 中的 Tests/Lint/Build）
2) 执行并记录结果
3) 若失败：修复 -> 重新执行（至少回到 fast checks）
4) 直到通过；否则必须写清阻塞点（环境/权限/缺依赖）+ 替代证据 + 需要用户做什么

## UI Changes（额外要求）
若涉及 UI/交互：
- 至少验证：
  - 1 条 happy path
  - 1 条 error 或 empty path
- 证据来源可为：MCP/Playwright/截图/控制台无错误等（能复现即可）
