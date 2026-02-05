# Plan 产出规范（工程可执行版）

定位：Plan 是“实现作战计划 + 轻量技术设计”，把 PRD 的【行为契约/验收契约】落为【可执行任务序列】。

## Skill Policy（Auto）
- Must Use: `writing-plans`
- May Use: `backend-development`（后端/API/性能/架构决策）
- May Use: `database-design`（表结构/迁移/索引/SQL）
- May Use: `frontend-design`（UI/交互/信息架构）
- May Use: `webapp-testing`（UI/E2E 验收与证据采集）

---

## Scope
- Applies when: 用户要求输出 Plan/设计文档/实施方案/技术方案
- Does NOT apply when: 仅输出 PRD/Review 或仅编码

## Outputs
- Expected output shape: 1-13 章节完整输出，缺省写 N/A
- Minimum verification evidence: Verification Plan + Self-Check 必须完整

## Gate（必须）
- Plan 完成后必须用 `53-plan-audit.md` 自检并给出 Verdict；FAIL 则按 Minimal Patch List 修到 PASS。

## Ask First
- Situations: 新依赖/破坏兼容/大重构/长时间服务/迁移与回滚风险

---

## 0) 总体原则（硬规则）
- Plan 不得改写 PRD 含义，只能映射/实现化。
- 每个任务必须写清：Goal / Touch(文件路径) / Steps / Tests / Verification(命令+通过标准)
- 信息不足影响验收的：进入 Open Questions，不得自创关键规则。
- 所有可运行命令优先引用 `90-project-profile.md`；没有就 Repo Recon 补齐。

## 1) Context / Scope
## 2) PRD → Plan 映射（强制）
## 3) Repo Recon（强制：基于真实仓库，不许臆测）
## 4) Constraints / Rules Applied（列出加载规则 + Ask First/Never）
## 5) High-Level Design（克制：只写数据流与落点）
## 6) Task Breakdown（强制：0.5~2h 粒度）
## 7) Verification Plan（强制：fast / integration / final 三层）
## 8) MCP Verification（如有 UI/交互，强制；细则见 06-planning-and-mcp.md）
## 9) Review Plan（资深自检）
## 10) Docs Update（docsforai 或项目文档）
## 11) Rollout / Rollback（强制）
## 12) Risks & Open Questions（强制）
## 13) Self-Check（强制）
