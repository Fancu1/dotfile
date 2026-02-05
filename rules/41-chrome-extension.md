---
description: Chrome extension rules (manifest, permissions, packaging)
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- Must Use: `frontend-design`
- May Use: `webapp-testing`（涉及扩展 UI/交互验收）
- May Use: `systematic-debugging`（权限/消息通信/注入脚本等疑难问题）

## Scope
- Applies when: Chrome 插件/扩展开发

## Rules
- 优先使用 Manifest V3；若必须使用 V2，需说明原因。
- 权限最小化；新增权限必须 Ask First 并说明用途。
- 打包/发布步骤需在 Plan 或验证中说明。
