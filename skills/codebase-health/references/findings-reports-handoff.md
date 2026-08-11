# 候选、报告与交接

## Finding 卡

```markdown
## CH-0001：<人话标题>

- Status: new | observing | ready | accepted | declined | resolved | reopened
- Value: 现在处理 | 先补安全网 | 顺手处理 | 暂不处理
- Implementation risk: small | medium | large | unknown
- First seen: <date + commit>
- Last confirmed: <date + commit>
- Scope: <模块、职责或调用链>
- Evidence: <文件/符号、调用链、行为差异、测试缺口或历史>
- Maintenance cost: <正在造成什么真实成本>
- Must preserve: <行为、契约或数据不变量>
- Recommended target: <目标状态，不写成详细实现指令>
- Verification: <如何证明改善且没有回归>
- Revisit when: <触发复查的条件>
- User decision: <无，或用户明确决定与日期>
- History: <简短状态变化>
```

仅凭审美、文件长度、复杂度数字或通用最佳实践不得标为 ready。安全网不足但问题真实时使用“先补安全网”。

## Review 报告

```markdown
# Codebase Health Review — <project> — <date>

## 结论
<一句话说明是否有值得行动的新变化>

## 本次范围
- Change Coverage：<检查或延期及原因>
- Module Coverage：<检查深度及原因>
- System Coverage：<全局视角及原因>

## 主要候选
<最多 1 个；没有则写“本次无需行动”>

## 次级候选
<最多 2 个；没有则省略>

## 已有 Finding 变化
<resolved / worsened / unchanged / reopened，避免复述完整旧卡>

## 覆盖进展
<哪些模块或全局视角从 none→mapped、mapped→sampled 等>

## 未覆盖与未知
<本次明确延期、无法验证或历史分叉造成的缺口>

## 下一轮建议
<一个模块候选 + 一个全局视角；按实际价值压缩>

## 运行信息
- Review kind: initial | rolling | focused | verification
- Project ID:
- Target ref/commit:
- Working tree included: yes/no
- Working tree snapshot: <none，或所读相对路径 + Git 状态 + SHA-256>
- State updates:
```

报告面向决策，不复制机器台账。引用相对路径和符号名即可，避免粘贴敏感源码。

## `$dev-workflow` 交接卡

用户准备处理 finding 时输出：

```markdown
交给 $dev-workflow
- Finding：<ID + 标题>
- 当前证据：<已验证事实>
- 当前行为与成本：<问题如何影响正确性或开发>
- 必须保持：<行为、接口、数据、权限等不变量>
- 推荐目标：<期望结构或安全网>
- 非目标：<本轮不处理什么>
- 验收条件：<可观察结果>
- 验证建议：<characterization / focused / adjacent / full>
- 建议风险等级：<small / medium / large + 原因>
- 未知与风险：<实施前仍需确认的内容>
```

交接只提供证据和边界。具体方案、批准门、实现、Review 与验证由 `$dev-workflow` 决定。

## 复查结果

复查报告必须回答：原证据是否仍成立、复杂度是否转移、必须保持项是否满足、验证证据是否足够，以及 finding 为什么变为 resolved、observing 或 reopened。
