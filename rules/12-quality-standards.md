---
description: Explicit quality standards with measurable acceptance and evidence
globs: ["**/*"]
alwaysApply: true
---

# 质量标准（明确可验收）

> 若不适用，必须写明 **N/A**，不得省略。

## 通用输出（必须满足）
- **目标一句话**：明确“做什么、改什么”。
- **范围边界**：列出不做什么（或 N/A）。
- **假设与阻塞**：所有不确定信息必须进入 Open Questions。
- **验收标准**（可验证、可量化）：至少 3 条；若不适用写 N/A。
- **验证证据**：列出命令/工具与实际结果；无法执行需说明原因与替代证据。

## 代码/配置/行为变更（额外要求）
- **变更清单**：文件路径 + 变更目的。
- **风险点与缓解**：至少 1 条；无则写 N/A。
- **边界/错误路径**：至少 2 条已考虑的边界或错误情况；无则写 N/A。
- **测试**：至少 1 条可执行命令或说明阻塞原因。
- **Git 交付信息（若适用）**：worktree 路径 / 分支名 / commit hash（以及是否已 merge 回用户本地目录）。

### Completion Signal（提交提醒，强制）
当本次任务涉及代码改动且满足以下任一条件时，必须在最终回复 **末尾** 输出一个醒目的 ASCII 提示块：

1) **已创建 commit**：输出 `COMMIT CREATED` 提示块（包含：worktree/branch/commit hash）。
2) **存在未提交变更**（`git status` 非空）且用户未明确说“不用提交”：输出 `UNCOMMITTED CHANGES` 提示块，并给出推荐的最小命令（例如 `git status --porcelain`、`git add -A`、`git commit -m "<message>"`）。

提示块格式（固定，允许替换占位符）：

```
==============================
CODEX DELIVERY SIGNAL
<COMMIT CREATED | UNCOMMITTED CHANGES>
worktree: <path-or-N/A>
branch:   <branch-or-N/A>
commit:   <hash-or-N/A>
next:     <one short action>
==============================
```

## 方案/计划/设计文档
- **输入/输出**：清楚写明输入数据与预期输出。
- **阶段与里程碑**：每步可验证。
- **非目标**：至少 1 条。

## 研究/对比/调研
- **来源与时间**：注明来源与发布日期（或访问日期）。
- **评价维度**：至少 3 个维度。
- **结论与置信度**：给出结论与信心等级。
