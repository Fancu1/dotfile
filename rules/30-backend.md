---
description: Backend rules (API contracts, error handling, compatibility)
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- Must Use: `backend-development`
- May Use: `systematic-debugging`（线上/并发/性能类疑难问题排查）

## Scope
- Applies when: 后端相关任务（服务/API/性能/数据处理）

## Rules
- 任何对外契约变更（API/事件/错误码）必须 Ask First。
- 错误处理不得吞错或默默降级；必须显式返回或记录。
- 保持向后兼容；若不可避免，必须说明迁移与回滚方案。
