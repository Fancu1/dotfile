---
description: MCP / Skill usage rules (especially for UI verification) - supplement to Plan
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- Must Use: `webapp-testing`（当 Plan 涉及 UI/交互验收且需要可复现证据时）
- May Use: `frontend-design`（当需要补齐 UI/交互验收口径与页面结构时）

## Scope
- Applies when: Plan 涉及 UI/交互，或需要 MCP/SKILL 做验证/自动化
- Does NOT apply when: 纯后端/纯文档且不需要交互验证

## Outputs
- Expected output: 补充 MCP Verification 小节（工具+步骤+预期结果+异常路径）
- Minimum verification evidence: 至少 1 条可执行验证路径（或说明不可执行原因）

## Ask First
- Situations: 需要启动长时间服务、需要新增外部依赖、需要改运行环境

## MCP Usage（UI/交互验证优先）
当涉及 UI/交互：
- 先列出可用 MCP 资源（例如 list_mcp_resources）
- 明确：
  - 访问哪个 URL（引用 `90-project-profile.md`）
  - 走哪些页面路径
  - 做哪些交互（click/type/select）
  - 预期看到的 UI 状态与网络请求结果
  - 至少 2 条异常路径（空数据/权限不足/网络失败等）

> 不要自动启动长时间服务；如必须启动，Ask First。

## Skill Usage（确定性优先）
- 若场景 rule/技术栈 rule 已声明 `Skill Policy`：必须按其调度（见 `11-skill-invocation.md`）。
- 若 skill 不可用：必须说明缺失，并给出等价的降级步骤与证据采集方式。
