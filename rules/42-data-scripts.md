---
description: Data/scripts rules (ETL, one-off scripts, reproducibility)
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- May Use: `database-design`（涉及 SQL/表结构/索引时）
- May Use: `backend-development`（一次性脚本/ETL/性能优化时）

## Scope
- Applies when: 数据处理/脚本/ETL/一次性工具

## Rules
- 任何破坏性操作必须 Ask First（删除/覆盖/重算）。
- 输出要可复现（输入来源、运行命令、结果校验）。
- 大数据量处理需说明性能与资源占用。
