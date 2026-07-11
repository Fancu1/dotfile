---
description: 中文博客生成 — 两阶段（想法 → 草稿 → 终稿补丁）+ 风格 DNA + deai 串行清 AI 痕迹 + Soul-Loss Guard 反"中性说明书"。产出 ~/wpx/my/my-blog/drafts/YYYY-MM-DD-<slug>/{01-ideas,02-draft,03-final}.md
---

# 触发 my-blog skill

调用 Skill tool，name = `my-blog`，把用户在 `/my-blog` 后传入的所有内容作为初始 prompt 传给 skill。

## 输入语义

`/my-blog` 后字符串：
- **无参数** → 从空白开始，由 skill 主动追问 5 个 hook
- **任意自然语言**（如 `/my-blog "想聊聊 X 的设计"`）→ 作为"用户初始想法"传入 skill，skill 把它当 Hook 1+2 的种子，继续追问缺失项

## 工作目录

skill 工作目录 = `~/wpx/my/my-blog/`（产物落 drafts/）。当前 Claude Code session 的 cwd 不影响 skill；skill 内部用绝对路径定位项目。

## 不在这里做

- 任何工作流细节（在 `~/.claude/skills/my-blog/SKILL.md` 里）
- 任何风格规则（在 `~/.claude/skills/my-blog/references/` 里）
- 任何脚本调用（脚本由用户手动 `python ~/.claude/skills/my-blog/scripts/profile_corpus.py` 跑）

## 相关文件

- skill 主入口：`~/.claude/skills/my-blog/SKILL.md`
- 设计 spec：`~/wpx/my/my-trending/docs/specs/2026-05-21-my-blog-design.md`
- 实施 plan：`~/wpx/my/my-trending/docs/plans/2026-05-21-my-blog.md`
