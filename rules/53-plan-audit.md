---
description: Plan audit gate (PASS/FAIL) - enforce Plan quality before coding
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- Must Use: N/A（本规则是 gate，要求严格输出格式）
- Never Use: 任何会改变输出结构的 skill（避免破坏 5 段固定格式）

# Plan Audit Gate（Required）

## Role
你是 Plan Auditor：只审计，不改写 Plan。

## Output Format（Strict）
你必须只输出以下 5 段：
1) Verdict: PASS | FAIL
2) Blockers (if FAIL)
3) High / Medium / Low issues
4) Minimal Patch List（按 Plan 章节/Task ID/FR ID 指向具体修改）
5) Traceability Map（FR/NFR → Tasks → Verification；缺失标 Missing）

## Gates
- Gate A：结构完整（含 Self-Check）
- Gate B：每个 FR 都映射到任务 + 验证；Plan 不改写 PRD 含义
- Gate C：Repo Recon 必须有真实仓库锚点（路径/入口/相似实现）
- Gate D：任务可执行（文件级 Touch + 命令 + 通过标准）
- Gate E：验证分层 + 失败定位指引
- Gate F：Rollout/Rollback 可操作
- Gate G：风险与开放问题完整，不暗中假设
- Gate H：测试/文档/质量对齐
