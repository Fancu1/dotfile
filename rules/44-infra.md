---
description: Infra rules (deployments, environments, safety)
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- May Use: `writing-plans`（变更较大、需要回滚/迁移方案时）
- May Use: `systematic-debugging`（环境/部署/运行失败定位）
- May Use: `executing-plans`（任务多、跨模块、需要 checkpoint 推进时）

## Scope
- Applies when: 基础设施/部署/环境配置相关任务

## Rules
- 任何生产环境或云资源操作必须 Ask First。
- 变更需包含回滚方案与影响面说明。
- 不得在规则或代码中写入密钥/证书。
