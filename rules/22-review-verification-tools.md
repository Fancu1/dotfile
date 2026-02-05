---
description: Preferred tools for review & verification (gh/playwright/MCP fallbacks)
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- May Use: `gh-address-comments`（PR/Issue 评论处理与批量回应）
- May Use: `gh-fix-ci`（CI 失败定位与修复建议/实施）
- May Use: `webapp-testing`（需要浏览器验收、截图、控制台/网络证据时）

## Tool Preference
- Code review / diff: 优先 `gh`，其次 `git diff`
- UI/E2E: 优先 Playwright，其次 MCP 浏览器工具
- API 验证：优先项目脚本/curl（以 `90-project-profile.md` 为准）

## Evidence Rule
任何“验证通过”的结论都必须附带：
- 用了什么工具/命令
- 看到什么结果（通过标准）
- 若工具不可用：说明原因 + 替代方式
