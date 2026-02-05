---
description: Follow AGENTS.md and keep docsforai/ in sync (create if missing)
globs: ["**/*"]
alwaysApply: true
---

## Instruction Priority
- `AGENTS.md` 是规则路由器，冲突时以其加载/裁决逻辑为准。
- 若规则与代码/脚本冲突：以代码/脚本为真，并修正规则/文档。

## docsforai/ (Recommended)
为了让 AI 稳定理解项目，建议维护 `docsforai/`（若不存在可创建最小集）：
- `docsforai/01_architecture_and_map.md`：模块/目录地图、边界、入口
- `docsforai/02_database_schema.md`：数据模型/迁移/索引（如适用）
- `docsforai/03_interfaces_and_events.md`：HTTP/gRPC/事件契约（如适用）
- `docsforai/04_conventions.md`：错误、日志、测试、代码风格约定

## Read First
当需要理解项目上下文时，优先读 docsforai（若存在），再读代码。

## Update After Changes (Non-Negotiable)
当你引入新特性/改动对外行为或契约：
- 必须同步更新 docsforai 对应文件（最少写清：改了什么、影响面、如何验证）。
