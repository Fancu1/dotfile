# 个性化治理状态

默认状态根：`~/.codex/state/personalize-codex/`。只有用户明确要求固化、撤销或执行规则整理时才创建。

```text
INDEX.md
decisions/<YYYY-MM-DD>-<short-slug>.md
```

## INDEX.md

```markdown
# Codex Personalization Index

| Preference ID | Summary | Scope | Source of truth | Status | Last reviewed |
|---|---|---|---|---|---|
```

- ID 使用递增 `PX-0001`，只服务去重与历史，不要求用户记忆。
- `Scope` 使用 `global / project:<path> / skill:<name> / state:<name>`。
- `Status` 使用 `proposed / active / superseded / rejected`。
- `active / superseded` 条目的 `Source of truth` 指向实际生效或曾经生效的 `AGENTS.md`、Skill 或状态文件；索引本身不控制行为。
- `proposed` 条目尚无生效事实源，填写 `target:<计划落点>`，只表示若获批准准备修改的位置；不得把该路径解释为规则已经生效，也不做内容一致性校验。
- 每次运行只对 `active` 条目核对事实源仍存在且内容一致；外部修改后更新索引，不反向覆盖事实源。`proposed` 条目只检查目标落点与冲突是否发生变化。

## 决策记录

```markdown
# Personalization Decision — <date> — <slug>

- Preference ID:
- User intent: add | replace | revoke | organize
- Normalized preference:
- Scope:
- Source of truth:
- Authorization evidence: <用户明确表达的简短摘要，不复制完整对话>
- Alternatives considered:
- Duplicate/conflict check:
- Result: active | superseded | rejected | proposed
- Replaces:
- Validation:
- Reversal:
```

每次已生效的新增、替换或撤销追加一份记录，不覆盖历史。批量整理在用户批准前可以记录 `proposed`，但不得把索引写成已经生效。

## 写入顺序

普通新增、替换或撤销：

1. 读取并验证事实源与已有索引。
2. 修改或撤销实际事实源。
3. 运行与目标相称的校验。
4. 追加决策记录。
5. 最后更新 INDEX。

批量整理的提案阶段：

1. 只读检查事实源与冲突，不修改任何生效规则。
2. 用户已明确要求执行整理时，可追加 `Result: proposed` 的决策报告，并在 INDEX 标为 `proposed`；其 `Source of truth` 必须写成 `target:<计划落点>`，不得声称目标文件已经生效。没有执行授权时只在对话中展示。
3. 用户批准后再按普通写入顺序执行，并追加新的 `active` 决策记录；不改写旧提案来伪装为一次完成。

任一步失败时停止，报告已完成和未完成部分。不得保存完整会话、敏感个人信息、凭证或与决策无关的内容。
