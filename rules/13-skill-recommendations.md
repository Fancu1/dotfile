---
description: Skill routing map by path/task (fallback when scenario rules don't specify)
globs: ["**/*"]
alwaysApply: true
---

# Skill 路由映射（兜底）

> 当已加载的场景 rules 没有给出 `Skill Policy` 时，使用本映射作为兜底自动调度依据。

## 路径映射（示例）
- 后端/服务：`**/internal/**`, `**/api/**`, `**/server/**`, `**/services/**`, `**/backend/**`
  - 推荐：`backend-development`
- 数据库/迁移：`**/db/**`, `**/migrations/**`, `**/*.sql`
  - 推荐：`database-design`
- 前端/UI：`**/web/**`, `**/frontend/**`, `**/ui/**`, `**/app/**`
  - 推荐：`frontend-design`
- 前端测试/E2E：`**/tests/**`, `**/e2e/**`, `**/playwright/**`
  - 推荐：`webapp-testing`
- 文档/规格：`**/docs/**`, `**/specs/**`, `**/prd/**`
  - 推荐：`kiro-skill` / `spec-kit-skill` / `prd-orchestrator` / `create-plan`

- GitHub/CI：涉及 `gh`、`GitHub Actions`、PR 评论、CI 失败日志
  - 推荐：`gh-fix-ci` / `gh-address-comments`

- 变更日志：涉及 `changelog`、release notes
  - 推荐：`changelog-generator`

- 深度调研：明确提到“深度调研/竞品分析/对比/资料整理/多来源引用”
  - 推荐：`deep-research`

- MCP/工具集成：涉及“写 MCP server / 接入外部 API / 协议对接”
  - 推荐：`mcp-builder`

## 常见通用任务映射
- 需求澄清/方向探索/方案权衡：`brainstorming`
- 分批执行计划/推进长任务：`executing-plans`
- 新功能/核心逻辑改动（希望高质量）：`test-driven-development`
- 疑难 bug/回归定位：`systematic-debugging`
- 修复完成前复核：`verification-before-completion`

- 邮件撰写/润色：`email-draft-polish`
- 会议纪要/行动项：`meeting-notes-and-actions`
- 会议沟通复盘：`meeting-insights-analyzer`
- 客服工单分拣：`support-ticket-triage`
- 简历定制：`tailored-resume-generator`

- 文件整理/重命名/归档：`file-organizer`
- 发票/收据整理：`invoice-organizer`
- 域名脑暴：`domain-name-brainstormer`
- 表格公式：`spreadsheet-formula-helper`
- 图片生成/编辑：`canvas-design` / `nanobanana-skill`
- 图片增强/清晰化：`image-enhancer`
- 视频下载：`video-downloader`
- YouTube 转录：`youtube-transcribe-skill`

- 用户明确要求“使用 autonomous-skill 自动推进（多阶段/跨会话）”：`autonomous-skill`
- 用户明确要求“使用 claude-skill/Claude Code 执行”：`claude-skill`

## 任务类型映射
- 代码评审/审计/找问题：推荐 `code-review`
- 计划/实施步骤：推荐 `create-plan`
- Notion 知识沉淀/研究：推荐 `notion-knowledge-capture` / `notion-research-documentation`
- 规格转实施：推荐 `notion-spec-to-implementation`
- 研究/比较：推荐 `deep-research` 或 `lead-research-assistant`
- CI 失败排查：推荐 `gh-fix-ci`
- PR/Issue 评论处理：推荐 `gh-address-comments`
- 生成变更日志：推荐 `changelog-generator`
- MCP 集成/协议：推荐 `mcp-builder`

## 规则
- 若命中多个技能：选择最小集合（通常 1 个），并在 Start-of-Task Header 说明理由。
- Tie-breaker（确定性）：若多个技能都“看起来合理”，按以下优先级取 1 个主 skill：
  - 数据/迁移优先于其他：`database-design`
  - 后端优先于前端：`backend-development`
  - UI/E2E 明确时：`frontend-design` / `webapp-testing`（以任务主目标为准）
  - CI/PR/Release 明确时：`gh-fix-ci` / `gh-address-comments` / `changelog-generator`
  - 其余默认：`writing-plans`（需要步骤化推进）或不调用 skill（仅按 rules）
- 若 skill 未安装：
  - Must Use 场景：自动安装（见 `11-skill-invocation.md`）
  - 兜底场景：优先自动安装；若失败则降级并说明影响
