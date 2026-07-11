---
name: my-blog
description: 我的中文博客生成 skill — 两阶段工作流（想法 → 草稿 → 终稿补丁）+ 风格 DNA 兜底 + 显式串行调 deai 做 AI 痕迹清除 + Soul-Loss Guard 反"中性说明书"。读完 03-final.md 让别人 100% 相信是我自己写的。用户触发 /my-blog 或在 ~/wpx/my/my-blog 项目里手动调用。
---

# /my-blog 工作流

读完这个 prompt 直接开始执行。预期产出 `~/wpx/my/my-blog/drafts/YYYY-MM-DD-<slug>/{01-ideas,02-draft,03-final}.md`。

## Stage 0 — 加载（静默，~100ms）

1. **定位项目**：`PROJECT_ROOT=~/wpx/my/my-blog`
   - 不存在 → 提示并执行 `mkdir -p` 全套骨架 + 写默认 `.my-blog.yml`（参考 ~/wpx/my/my-blog/README.md 的目录约定）
2. **读配置**：`PROJECT_ROOT/.my-blog.yml`
   - 字段缺失静默 fallback 默认值
3. **风格 DNA 探测**：
   ```
   if test -f $PROJECT_ROOT/user-style-dna.md:
       STYLE_DNA = ./user-style-dna.md
   else:
       STYLE_DNA = ~/.claude/skills/my-blog/references/piglei-style-dna.md
   ```
   **不打 warning、不询问、不报错**。
4. **drafts/ 探测（恢复模式）**：扫 `PROJECT_ROOT/drafts/YYYY-MM-DD-*/`：
   | 检测到 | 行为 |
   |---|---|
   | 只有 `01-ideas.md` | 问"继续从草稿阶段开始？还是想补充想法？" |
   | 有 `01` + `02` | 问"继续做终稿补丁？还是回去改草稿？" |
   | 三个全有 | 问"这篇已完成。开新文章？还是回顾这篇？" |
   | 同一天多个 slug | 列出来让用户选 |
   | 无 | 进入 Stage 1 |
5. **加载 references**：根据 STYLE_DNA 路径，把对应 `*.md` 全读进上下文 + 同时读 `ai-trace-detector.md` + `hugo-template.md` + `elicitation-hooks.md`（写草稿时用）；**soul-loss-guard.md 不在 Stage 0 加载**（Stage 2.a 才用）。

## Stage 1.a — Elicitation（追问 hook）

按 `references/elicitation-hooks.md` 的 5 个 Hook 追问。

**硬门槛**：Hook 1（核心观点）+ Hook 2（具体锚点）必须满足，否则拒绝进 Stage 1.b。

追问完成后：
1. 生成 slug（按 `references/hugo-template.md` 文件命名规则）
2. 创建 `PROJECT_ROOT/drafts/YYYY-MM-DD-<slug>/`
3. 写 `01-ideas.md`，schema 见 `references/elicitation-hooks.md` 末尾

**⏸ 中断点 1**：
```
01-ideas.md 已写到 drafts/YYYY-MM-DD-<slug>/01-ideas.md。
请读一遍，确认或补充。读完说"OK 写草稿"我就进 Stage 1.b。
```

## Stage 1.b — 写草稿

接到用户"OK 写草稿"信号后进入。

加载：`STYLE_DNA` + `ai-trace-detector.md` + `hugo-template.md`。

**写作硬约束**：
1. 全文按 `STYLE_DNA` 的 20 条 checklist 控制（含 `[when-applicable]` 条目自动跳过的判定）
2. `ai-trace-detector.md` 的禁用词清单 / 句式黑名单 **零容忍**
3. Hugo frontmatter 按 `hugo-template.md` 模板填
4. 字数按 elicitation Hook 4 的答案（用户没填 → 按文章性质自决）

**自检流程**（每段写完前）：
- grep 禁用词 / 句式黑名单 → 命中即重写本段
- 对照 checklist 当前段位置（单句段 / 段长 / 标点密度）

写完整篇后：
1. 写 `02-draft.md` 到 `drafts/YYYY-MM-DD-<slug>/`
2. 报告：「草稿 X 字 / N 段 / 我自评 20 条 checklist 跑了 Y 条 pass / Z 条 fail / W 条 n/a」

**⏸ 中断点 2**：
```
draft 已写到 drafts/YYYY-MM-DD-<slug>/02-draft.md，你可以：

[1] 直接进入终稿补丁 (默认)
[2] 我先在编辑器改改 draft，改完你再补丁
[3] 跳过补丁，把 draft 当终稿用 (不调 deai)

选哪个？
```

- 选 [1] → 进 Stage 2.a
- 选 [2] → 等用户说"OK 改完了"，重新读 `02-draft.md`（用户可能改了），再进 Stage 2.a
- 选 [3] → 跳过 Stage 2，直接 `cp 02-draft.md 03-final.md`，附 audit 报告（标记"用户跳过补丁"）

## Stage 2.a — 终稿补丁（显式串行调 deai）

加载：`soul-loss-guard.md`。

1. **调用 deai skill**：
   - 用 Skill tool, name = `deai`, 输入 = `02-draft.md` 全文
   - 输出存为内存中的 `deai-version`（**不落盘**）
2. **生成 diff**：`diff(02-draft.md, deai-version)` → 提取 patch candidates 列表，每条标注：
   - 位置（line range）
   - 原文
   - 建议改法
   - 类别（按 ai-trace-detector.md 分类：P1 禁用词 / P2 句式黑名单 / P3 风格 DNA 越界 / P4 其他）
3. **排序 + 应用 Top N**（N = `.my-blog.yml` 的 `patch_budget`，默认 10；长文 >4000 字用 `patch_budget_long`，默认 15）：
   - **P1**：全部接受
   - **P2**：取与黑名单距离最大的若干
   - **P3**：仅修复"硬指标越界"的位置（单句段比例 <30%、平均段长 >70 字 等）
   - **P4**：**一律拒绝**
4. **预算耗尽后多余的 patch**：附在 `03-final.md` 末尾 `<!-- unused-patches -->` 注释块里，让用户回看

应用后得到 `patch-version`（仍内存中）。

5. **Soul-Loss Guard 反检**：按 `soul-loss-guard.md` 的 7 条对比 `patch-version` vs `02-draft.md`：
   - **命中 ≥3 条 → 全部回滚**：`03-final.md = 02-draft.md` 副本 + 附 audit 报告（"补丁会破坏 X, Y, Z，已回滚；建议手动改：[列出 P1 候选]"）
   - **命中 1-2 条 → 警告但接受**：`03-final.md = patch-version` + 附 audit 报告（标"以下灵魂位被改动，请确认"）
   - **命中 0 条 → 全盘接受**：`03-final.md = patch-version` + 附 audit 报告（"Soul-Loss Guard 通过"）

## Stage 2.b — 写终稿 + diff 输出

1. 把 `03-final.md` 落到 `drafts/YYYY-MM-DD-<slug>/`
2. 在 `03-final.md` **末尾**附 HTML 注释包裹的 audit 报告：
   ```
   <!--
   dna-audit.json:
   {
     "passed": ..., "failed": ..., "na": ..., "pass_rate": "...",
     "checks": [...]
   }

   soul-loss-guard: <pass | warning | rollback>
   <详细命中 evidence>

   unused-patches:
   - line X: "..." → "..." (P3 风格越界，预算外)
   ...
   -->
   ```
3. 给用户输出 `02-draft.md` → `03-final.md` 的 unified diff（标注每个改动属于哪类）

**⏸ 中断点 3**：
```
终稿已写到 drafts/YYYY-MM-DD-<slug>/03-final.md。
满意 → cp drafts/YYYY-MM-DD-<slug>/03-final.md posts/<slug>.md，然后 git commit。
不满意 → 改 02-draft.md，调用 /my-blog 我会按恢复模式继续。
```

## dna-audit.json schema（生成主体：LLM）

由 LLM 在 Stage 2 末尾**生成**（不是脚本）：硬指标（句长、密度类数字）由 LLM 现场统计；软指标（"≥1 个非编程比喻"、"≥1 处自嘲"）由 LLM 阅读判定。`[when-applicable]` 条目（"反引号包裹代码"、"中英术语对照"）若文章里没出现触发条件，标 `n/a`。

```json
{
  "passed": 16,
  "failed": 2,
  "na": 2,
  "pass_rate": "89%",
  "checks": [
    {"id": "sent_len_avg", "expected": "30-42", "actual": 38.7, "result": "pass"},
    {"id": "single_sent_para_ratio", "expected": ">=35%", "actual": 28.2, "result": "fail"},
    {"id": "code_backtick_wrap", "result": "n/a", "reason": "文章里没出现代码标识符"}
  ]
}
```

## 失败模式

| 场景 | 行为 |
|---|---|
| `~/wpx/my/my-blog/` 不存在 | `mkdir -p` 全套骨架 + 写默认 `.my-blog.yml` |
| `.my-blog.yml` 字段缺失 | 字段级 fallback 到默认 |
| `samples/` 全空 | 不报错，静默走 piglei |
| Stage 1.a 用户拒绝答 Hook 1/2 | 拒绝进 Stage 1.b，重问 |
| `deai` skill 不存在 | 提示并跳过 Stage 2（02-draft.md 直接作 03-final.md） |
| `drafts/<slug>/` 同名已存在 | slug 追加 `-2` / `-3` |
| frontmatter 被手改坏 | 重写 frontmatter，不动正文 |

## 关键不做

- ❌ 自动 `cp 03-final.md → posts/`（用户手动）
- ❌ 自动 `git commit` 用户博客 repo
- ❌ 多轮补丁（一轮就够）
- ❌ 让 deai 改段落小标题 / frontmatter
- ❌ 在 Stage 0 自动跑 `profile_corpus.py`（用户主动跑）
