---
description: Senior review checklist after tests pass (scope control, correctness, security, operability)
globs: ["**/*"]
alwaysApply: false
---

## Skill Policy（Auto）
- Must Use: `code-review`
- May Use: `requesting-code-review`（提交前自检清单）
- May Use: `receiving-code-review`（逐条响应评审意见的规范流程）

## Trigger
实现完成且验证通过后，再进行本 Review（不要在没跑通前做无效洁癖）。

## Output（固定）
- Issues（按严重度：Critical/High/Medium/Low，尽量给文件定位）
- Questions & Assumptions
- Change Summary（改了什么、为什么）
- Known Issues / Follow-ups（不能当场修的要说明风险与下一步）

## Review Checklist（硬门槛）
- Scope 控制：没有无关 churn、没有大范围格式化
- 正确性：边界/错误路径/幂等/并发（若适用）
- 契约：API/事件/错误码不被无意改变
- 安全：敏感信息不落日志、不绕过鉴权、不引入风险依赖
- 可维护：命名清晰、重复逻辑收敛、注释只解释非显然意图
- 文档：对外行为变化同步 docsforai 或项目文档
