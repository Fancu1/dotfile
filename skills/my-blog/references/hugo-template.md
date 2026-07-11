# Hugo Frontmatter 模板

skill Stage 1.b 写草稿时给 `02-draft.md` 套上以下 frontmatter；Stage 2.b 写 `03-final.md` 时不动 frontmatter。

## 模板

```yaml
---
title: "<标题>"
date: <YYYY-MM-DDTHH:MM:SS+08:00>
draft: false
tags:
  - <tag1>
  - <tag2>
categories:
  - <category>
description: "<≤80 字摘要>"
---
```

## 字段生成规则

| 字段 | 生成方式 |
|---|---|
| `title` | 从 elicitation 的"核心观点"派生：去掉句末标点，限 25 字内 |
| `date` | `$(TZ=Asia/Shanghai date -Iseconds)`（首次写草稿时刻；终稿不更新） |
| `draft` | 默认 `false`（用户手动 cp 到 posts/ 时已视为可发布）；用户在 elicitation 反例里说"先存为草稿"则置 `true` |
| `tags` | 1-3 个，从核心观点 + 锚点关键词提取；不堆 5+ 个 |
| `categories` | 1 个；按文章性质：技术 / 反思 / 想法记录 / 阅读笔记 / 生活观察 |
| `description` | 直接用 elicitation 的"核心观点"原句，≤80 字 |

## 文件命名规则

`drafts/YYYY-MM-DD-<slug>/{01-ideas,02-draft,03-final}.md`

- `slug` 由"核心观点"生成：
  - 中文 → 取主语 + 动词 + 宾语前 3-4 个语义词，转拼音 kebab-case
  - 英文 → 直接小写 kebab-case
  - 长度 ≤30 字符
- 同日同 slug 已存在 → 追加 `-2` / `-3`

## 不做

- ❌ 不生成封面图
- ❌ 不抓取外链作为 references
- ❌ 不写多语言 i18n 字段
- ❌ 不强制 sluggify 英文 title（中文 title 也可以原样保留，hugo 自己处理）
