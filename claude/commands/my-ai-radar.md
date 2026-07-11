---
description: AI 信号雷达 — on-demand 扫描 9 个 AI 信号源（配方 / 范式 / 工具链 / 厂商），按 4 类 narrative 段落风格写到 reports/radar/YYYY-MM-DD.md + 末尾 Top 5 深读
---

# 任务：AI Radar 信号扫描

读完这个 prompt 直接开始执行。on-demand 触发 `/my-ai-radar`，期望产出 `~/wpx/my/my-trending/reports/radar/YYYY-MM-DD.md`。

## 输入解析

紧跟 `/my-ai-radar` 后的字符串：

- **无参数** → `DATE_KEY = $(TZ=Asia/Shanghai date +%Y-%m-%d)`
- **`YYYY-MM-DD` 格式**（如 `2026-05-15`） → 显式日期（补跑）
- **其他自然语言**（如 `偏 RAG`） → `DATE_KEY` 用默认（当天），自然语言作为本次"侧重"补充进画像匹配

## 工作流（严格按顺序）

1. **解析参数**，得到 `DATE_KEY` 和可选的"侧重"短语
2. `cd ~/wpx/my/my-trending`
3. `git pull --rebase origin main`（失败警告但继续，不阻塞）
4. `mkdir -p reports/radar`
5. 准备目标 `reports/radar/$DATE_KEY.md`：已存在则**覆盖**（同日重跑覆盖是预期行为）
6. Read `trending-profile.md`，**所有推荐必须扎根此文件**（读不到硬错）
7. **WebFetch 9 源并发**：

   配方源（3）：
   - `https://github.com/anthropics/skills`
   - `https://github.com/hesreallyhim/awesome-claude-code`
   - `https://developers.openai.com/cookbook`

   范式源（3）：
   - `https://www.anthropic.com/engineering`
   - `https://simonwillison.net/`
   - `https://eugeneyan.com/`

   工具链 + 范式（1）：
   - HN Algolia: `https://hn.algolia.com/api/v1/search?query=claude+OR+agent+OR+llm&numericFilters=points>50&tags=story&hitsPerPage=15`

   综合（1）：
   - `https://www.latent.space/archive`

   厂商（2 in 1 类）：
   - `https://www.anthropic.com/news`
   - `https://cursor.com/changelog`

   每个源抓 top 10-15 条候选，提取：`title` · `URL` · `简介` · `发布时间`（如有）

   **抓不全 fallback**：某源返回可解析项目数 < 5，用 curl 兜底：
   `curl -sL '<url>' -o /tmp/radar-<n>.html`，再用 python 解析 HTML 抽列表。

   **已知上游异常**（不算 fetch bug，直接标"数据源 X 异常"）：
   - `hesreallyhim/awesome-claude-code` README 处于重组期（TOC 全 TODO），抓不到结构化条目；上游 README 恢复后自然好
   - `github.com/anthropics/skills` 主页只返回 repo 高层结构（document-skills / template / spec），抓不到最近 commit 级别新 skill；写报告时如实说明"信号源识别但未拿到具体新 skill"，不要硬编
8. **去重合并**（按 URL）
9. **严过滤**（按 `trending-profile.md` 的"略过"规则）：
   - 加密货币 / 投机 → 排除
   - 营销 / 书单 / 非技术 → 排除
   - 纯前端 UI 库 / JS-TS 纯前端框架（除非与 AI 平台强相关）→ 排除
   - 推不出"对用户有什么具体学习点" → 排除

   **radar 覆盖 trending 的两条规则**（必须执行）：
   - `awesome-*` 仓库**允许作为信号源**（不要因为是 awesome 就跳过它的 README 里推荐的 skill）
   - docs / cookbook / changelog 类内容**允许作为合法条目**（trending 默认排除"纯教程"，radar 不排除）

10. **按 4 类 organic 分组**：
    - 配方 / 可复用 skill
    - 范式 / 新 pattern
    - 工具链 / Coding agent 动向
    - 厂商动态

    某类无内容显式标"本次无新信号"，不强凑。

11. **写 `reports/radar/$DATE_KEY.md`**，结构见下
12. **更新 `RADAR_INDEX.md`**：在表格中查找 `| $DATE_KEY |` 开头的行：
    - 已有该日行 → **替换**为最新数据
    - 没有 → 在表格分隔符下一行**插入新行**（最新在上）
    格式：`| $DATE_KEY | [reports/radar/$DATE_KEY.md](reports/radar/$DATE_KEY.md) | <条目数> | <主要主题，一句话> |`
13. `git add reports/radar/$DATE_KEY.md RADAR_INDEX.md`（skill 不动 README.md）
14. **不**自动 commit / push。终端打印：
    > 已 stage `reports/radar/$DATE_KEY.md` 和 `RADAR_INDEX.md`，请 review 后 commit / push。

## 报告结构（写到 `reports/radar/$DATE_KEY.md`）

```markdown
# AI Radar — YYYY-MM-DD

_Source: 9 sources (anthropics/skills · awesome-claude-code · openai-cookbook · anthropic engineering · simonwillison · eugeneyan · HN Algolia · latent.space · anthropic news + cursor changelog)_
_生成时间: <ISO8601> CST_

## 概要

（2-3 句 narrative，像朋友汇报：今天主线大概是什么 + 哪些源异常 + 总条目数。不要 bullet 堆诊断信息。）

## 配方 / 可复用 skill

#### <title>
[link](url) · <来源标签> · <日期 / stars / pts 等关键 meta>

第一段叙述（80-120 字）：介绍这是什么。像跟人聊天，不要百科式开头（"X 是 Y 团队做的 Z 框架" 这种）。

第二段叙述（30-60 字，可选）：跟手头项目（AI 排障 / Venus / Scope）有具体关联才写；没有就省略，不强凑。如该条已在 Top 5 展开，这段写"详细放 Top 5 讲"占位即可。

#### <title>
（同结构，narrative 段落而非 bullet 化二段切分）

(若干条；本类无内容则写 "本次无新信号")

## 范式 / 新 pattern

(同结构)

## 工具链 / Coding agent 动向

(同结构)

## 厂商动态

(同结构)

## 本次关注 Top 5（按推荐顺序）

### 1. <title>
[link](url) · <meta>

200-300 字 narrative，比上面分类里同条目更深一层 — 重点讲"为什么今天值得花时间看这一篇"+ 跟你项目的关联怎么落地（具体到字段 / 改造点 / 决策影响）。上面分类列表里同一条要写"详细放 Top 5 讲"避免重复。

### 2. <title>
...

## 警示（如出现反模式）

(纯 Agent 放飞 / hype / 编造 benchmark / 灰色)
```

## 硬规则

- 全程中文输出（报告模板中固定英文标签如 `AI Radar`、`Source:` 保持原样，其余叙述性内容用中文）
- 不动 `trending-profile.md` / `scripts/` / 既有 trending reports / `INDEX.md`
- 每条 narrative 80-180 字；Top 5 每条 200-300 字
- 推不出"具体学习点 / 关联点"的条目直接略过，不要硬凑
- WebFetch 单源失败：标"数据源 X 异常" + 错误日志，剩下源正常出报告
- 9 源全部失败：报错退出（无米下锅）
- 同日报告已存在 → **覆盖**（重跑覆盖是预期行为，与 daily 一致）
- 不调任何需要鉴权的 API；HN 走公开 Algolia
- 不自动 commit / push（用户每天手动 review）

## 可读性原则

- **语气**：像朋友 / 老师娓娓道来，不是 PR 列表 / 清单 inbox
- **结构**：每条 narrative 段落（标题独立成行 + meta 副标题分开行 + 1-2 段叙述），不用 bullet 化的"价值 + 关联"二段硬切
- **关联**：真有关联到 AI 排障 / Venus / Scope / 转型方向才写"你 X 项目..."；没有就只写"这是什么 / 为啥值得"，不形式化重复
- **不要**百科式开头（"X 是 Y 团队做的 Z 框架"）
- **不要**泛泛"对 AI 开发有用"，要具体到字段 / 改造点 / 决策影响
- ✅ 好："你 pgvector 现在是把故障描述直接 embed 的，没做这种上下文 prefix。改造的好处是几乎不动架构 — embed 入参那里加一段 prefix 就完事"
- ❌ 差："对 RAG 有用"

开始。
