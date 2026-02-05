---
description: Project Profile (single source of truth for commands, stack, ports, environments)
globs: ["**/*"]
alwaysApply: true
---

# Project Profile（必填：这是项目的单一事实源）

> 目的：让 AI 不靠猜也能跑起来、测起来、验收起来。
> 所有 rules 都应优先引用这里的字段，而不是自己臆测端口/命令/账号/环境。
> 若项目根存在 `.codex/project.profile.md`，必须以项目文件为准；本文件作为全局模板与兜底。

## 1) Project Snapshot
- Project Name: <TBD>
- Primary Goal: <TBD>
- Target Users: <TBD>
- Non-Goals: <TBD>

## 2) Tech Stack
- Backend:
  - Language/Runtime: <TBD>
  - Framework: <TBD>
  - Package Manager / Build Tool: <TBD>
- Frontend (if any):
  - Stack: <TBD>
  - Frontend Paths (for rule matching): <TBD e.g. web/**, frontend/**>
- Data:
  - Database: <TBD>
  - Cache/Queue/Search: <TBD or N/A>
- Infra/Runtime:
  - Docker/Compose: <TBD yes/no>
  - Deployment Target: <TBD local only / k8s / serverless / etc>

## 3) Local Runbook (copy/paste commands)
> 不知道就写 TBD。AI 遇到 TBD 必须进入 Open Questions，或通过仓库勘察补齐。

- Install deps:
  - Command: <TBD>
- Start dev (short-lived / foreground):
  - Command: <TBD>
- Start full stack (long-running):
  - Command: <TBD>
  - Ask First Required: yes/no (建议 yes)
- Build:
  - Command: <TBD>
- Lint/Format/Typecheck:
  - Command(s): <TBD>
- Tests:
  - Fast Checks (per-task): <TBD>
  - Full Test Suite (before finish): <TBD>
  - Integration/E2E (if any): <TBD>

## 4) URLs / Ports
- Web App URL: <TBD e.g. http://localhost:3000/>
- API Base URL: <TBD e.g. http://localhost:8080/>
- Health Endpoint (if exists): <TBD e.g. GET /health>
- Admin Panel URL (if any): <TBD>

## 5) Environment & Secrets Policy（硬规则）
- Where env lives: <TBD e.g. .env, .env.local, docker compose env_file>
- .env committed?: MUST be no (use .env.example)
- Secrets Handling:
  - 默认不写入版本库；仅在用户明确授权且指定目标路径/范围时可处理（允许写入用户指定路径，包含仓库文件；是否提交由用户决定）
  - 不在日志/文档/代码中输出明文 token/password
  - 需要密钥才能继续：Ask First + 提供安全的用户设置方式

## 6) Test Data / Accounts（本地验收需要）
- Default user account (local only): <TBD or N/A>
- Default admin account (local only): <TBD or N/A>
- Seed command (if any): <TBD or N/A>
- Destructive operations allowed in local dev DB? <TBD yes/no>

## 7) Definition of Done（全局 DoD）
完成一个需求/任务，必须满足：
- 实现与 PRD/Plan 的验收口径一致
- 相关测试通过（至少 Fast + Full，具体命令见上面）
- 输出 Verification Evidence（跑了什么、结果如何）
- 关键 docs 更新（若有 docsforai 或对外契约变化）

## 8) Notes / Known Constraints
- Timezone/Locale assumptions: <TBD>
- Browser support: <TBD>
- Performance SLO: <TBD>

## 9) How to Update This File（强制）
- 当端口/命令/栈/路径发生变化：必须同步更新本文件。
- 本文件与仓库真实情况冲突时：以代码/脚本为准，并修正本文件。
