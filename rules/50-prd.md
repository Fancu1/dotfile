# PRD Rule - Contract-First, Testable, Unambiguous

## Skill Policy（Auto）
- Must Use: `kiro-skill`
- May Use: `deep-research`（当需要竞品/类似项目调研，且需要多来源引用时）
- May Use: `spec-kit-skill`（当仓库已存在 `.specify/` 或用户要求 Spec-Kit 工作流时）
- Never Use: `backend-development` / `frontend-design` / `database-design`（除非用户同一任务明确要求进入实现/方案阶段）

## 定位
PRD 是【产品/行为契约 + 验收契约】，不是技术方案或代码实现。
PRD 的目标：让另一个 AI 能基于 PRD 产出工程 Plan，再按 Plan 编码。

## 硬要求
- 任何会导致不同实现路径或不同验收结果的内容必须唯一确定（无歧义）。
- 每条需求必须可测试、可验收（能转成测试用例）。
- 缺信息必须列“开放问题”，不得脑补关键规则。

---

## Scope
- Applies when: 用户要求输出 PRD/需求文档/产品规格
- Does NOT apply when: 仅输出 Plan/Review/代码实现

## Outputs
- Expected output shape: 按 1-13 章节固定结构输出，缺省写 N/A
- Minimum verification evidence: 末尾 Self-Check 逐条 Yes/No

## Gate（必须）
- PRD 完成后必须用 `52-prd-audit.md` 自检并给出 Verdict；FAIL 则按 Minimal Patch List 修到 PASS。

## Ask First
- Situations: 需求关键规则缺失且会导致不同验收路径

---

## 1) 元信息
- 标题：
- 版本：
- 日期：
- 适用端（Web/APP/Service/…）：
- 相关链接（可选）：
- 技术/环境约束（Context）：（引用 `90-project-profile.md` 的关键信息）

## 2) 背景与问题
要求（可选但推荐）：
- 竞品/类似项目对比：至少 3 个（含链接 + 借鉴点 + 不做的点）；若不做，写 N/A 并说明原因
## 3) 目标与非目标
## 4) 用户与场景
## 5) 概念与术语（强制）
## 6) 核心流程（强制：成功 + 失败 + 异常）
## 7) 功能需求（逐条编号 FR-xxx，模板字段必须全）
每条 FR 必须包含：
- Why / What / Inputs / Outputs / Rules / Edge Cases / Errors / Compatibility & Migration / Acceptance Criteria
- Acceptance Criteria：3-8 条，至少包含 1 成功 + 1 失败 + 1 边界
- 禁止写实现细节（模块拆分/SQL/缓存/类设计）

## 8) 数据与事件契约（强制：无歧义）
- 必须使用 JSON Schema 或 TypeScript Interface 描述对外数据结构
- 给出请求/响应/对象示例
- 错误码表（code/message/user_action）

## 9) 非功能需求（必须量化或可度量）
## 10) 配置与开关（必须写关闭时行为）
## 11) 验收与测试（FR 映射）
## 12) 风险与开放问题
## 13) 附录（决策表/状态机/示例）

---

## Self-Check（必须）
- [ ] 每条 FR 都有可测试的 Acceptance Criteria
- [ ] 核心流程包含成功/失败/异常反馈
- [ ] 对外契约有 schema/interface + 示例
- [ ] NFR 可度量或有验证方法
- [ ] 所有不确定点进入开放问题
- [ ] 没有写实现细节
- [ ] 竞品/类似项目对比已完成，或明确标注 N/A
