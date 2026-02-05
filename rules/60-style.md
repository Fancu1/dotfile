---
description: Code style and formatting rules
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- May Use: `code-review`（确保纯风格变更没有引入行为变化/回归风险）

## Scope
- Applies when: 用户要求风格/格式化/命名/规范类调整
- Does NOT apply when: 行为改动为主

## Rules
- 仅风格调整不得改变行为与对外契约。
- 优先使用项目已有 lint/format 工具（参考 `90-project-profile.md`）。
- 避免全仓库格式化；若必须，先 Ask First 并说明影响。
