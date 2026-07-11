---
description: 复盘入口 — 默认每日 check-in；按时间自动提议升级到周/季复盘
---

统一复盘入口。AI 根据"距上次 weekly / quarterly 多久"决定要不要在 daily 末尾升级。

## 流程总览

1. 加载上下文 + 时间检测
2. 走 daily 流程（5-8 分钟，每天必跑）
3. 按时间提议升级 weekly（候选人点头才走）
4. 按时间提议升级 quarterly（候选人点头才走）

显式触发：候选人若说"只做周复盘 / 只做季复盘 / 跳过 daily"，直接进对应段。

## Step 1：加载上下文 + 时间检测

并行读取：
- `~/.claude/goals.md`（不存在或空模板时提示但不强制）
- `~/wpx/my/my-daily/habits.md`
- `~/wpx/my/note.md`（疑惑 / 待办 / 灵感清单）
- 昨天的 journal：`~/wpx/my/my-daily/journal/<昨日 YYYY-MM-DD>.md`（不存在则跳过）
- `~/wpx/my/my-daily/weekly/` 最新文件
- `~/wpx/my/my-daily/quarterly/` 最新文件

今天日期用系统的 `Today's date`（YYYY-MM-DD）。

判断升级时机（结果先记着，daily 走完才用）：
- **weekly**：今日距 weekly/ 最新文件日期 > 7 天（无文件 = 距今 ∞）
- **quarterly**：今日所在 ISO 周已到本季最后 1-2 周（Q1 W12-13 / Q2 W25-26 / Q3 W38-39 / Q4 W51-52）**且** quarterly/ 没本季文件

## Step 2：daily 流程（每天必跑）

按顺序问四件事，**一次一个，等答案再问下一个**：

**a. 昨日回顾**
- 有昨日 journal：对照"今日计划"逐条问"X 完成度怎么样？"
- 无：问"上次工作是什么时候？最近在推进什么？"

**b. 今日计划**
先扫 note.md，挑出 [待办] 状态=待做、[疑惑] 状态=待消化、最近 7 天的 [灵感]，列 1-3 条最显眼的：
> "my-note 里这几条还没动：① ... ② ...，今天要不要捎上一两条？"
不强求，候选人摇头跳过；点头就并入今日计划。

然后问"今天打算做哪几件事？"收集 3-7 项。

**c. 当前卡点**
问"现在有什么卡住或纠结的？"

**d. 目标对照**
对今日计划每一条，问"这件服务于 goals 的哪一条？"
完全无关 → 问"这件和当前 chapter 无关，是刚需 / 插入 / 可 backlog？"
**只确认，不说教。**

### Habits 打卡

对 habits.md 里每条活跃 habit 问"<描述> —— 今天做了吗？"，记 yes / no。

### 写入 journal

按 `~/wpx/my/my-daily/CLAUDE.md` 的 journal 模板，写到：
`~/wpx/my/my-daily/journal/<今日 YYYY-MM-DD>.md`

整个 daily 段控制在 5-8 分钟内。

## Step 3：weekly 升级判断

daily 写完后，看 Step 1 的 weekly 检测结果：

- 不满足 → 跳到 Step 4
- 满足 → 直接问：
  > "距上次周复盘 N 天了，顺便做周复盘？大概再花 5 分钟。"
- 摇头 → 跳到 Step 4；点头 → 走 **weekly 子流程**

### weekly 子流程

加载最近 7 天 journal（按日期倒序），不足 7 篇按实际算。

**前置守门：** journal < 3 篇 → 不做，提示"先积累几天"，跳到 Step 4。

**直接总结四件事，让候选人确认或纠正：**

**a. 本周亮点** —— 3-5 件推进了的事（带来变化，不是"做了什么"）
**b. 本周卡点** —— 反复出现（≥ 2 天）的卡点
**c. 反复出现的模式** —— 特别关注：
- 说过 ≥ 2 次但未进 persona 的偏好
- 推迟 ≥ 2 次的任务
- 新兴趣 / 新领域

**d. 与 goals 关联度** —— 推进的条目 / 脱节的条目（及占比）

**提议固化（候选人批准才改）：**
- "你这周说过 3 次 X，要不要加到 persona.md？"
- "你连续 5 天推进 Y，要不要加到 goals.md 季度 KPI？"

**Habits 周打卡统计：** 读 7 天 journal 算每条完成率（X/7）。连续 7 天零打卡 → 问是否归档。

**写入 weekly：**
按 my-daily/CLAUDE.md 的 weekly 模板，写到：
`~/wpx/my/my-daily/weekly/<YYYY>-W<两位数 ISO 周号>.md`

ISO 周号：取今日的 ISO week number，注意跨年边界。

**整体脱节**（出差 / 休假）→ 客观记录，标"非推进周"，不批评。

## Step 4：quarterly 升级判断

看 Step 1 的 quarterly 检测结果：

- 不满足 → 结束
- 满足 → 直接问：
  > "本季度（Q<N>）还没复盘，顺便做季度复盘？大概再花 10 分钟。"
- 摇头 → 结束；点头 → 走 **quarterly 子流程**

### quarterly 子流程

加载本季所有 weekly：`~/wpx/my/my-daily/weekly/` 本季文件。
季度映射：Q1 = W01-W13，Q2 = W14-W26，Q3 = W27-W39，Q4 = W40-W53。

**前置守门：** 本季 weekly < 4 篇 → 做轻量版（只列已有 weekly 的要点），不强行评估 KPI。

**评估四件事：**

**a. 季度重心回顾** —— 读 goals.md 里"当前 chapter"和"季度 KPI"，列给候选人看
**b. 完成度评估** —— 每条 KPI：完成 / 部分完成 / 未完成 / 已作废，用 weekly 证据支撑
**c. 偏离事项** —— 本季哪些精力花在不在 KPI 里的事？客观记录，不评判（可能是刚需）
**d. 典型案例** —— 3-5 件代表性的事（高光 / 低谷 / 转折）

**下季度 goals 建议（候选人批准后才改 goals.md）：**
- 滚动哪些 KPI 到下季度
- 作废哪些 KPI
- 新增哪些 KPI
- chapter 是否要换

**写入 quarterly：**
按 my-daily/CLAUDE.md 的 quarterly 模板，写到：
`~/wpx/my/my-daily/quarterly/<YYYY>-Q<1-4>.md`

候选人中途调整过 chapter → 记录转折点，前后分开评估。

## 边界

### daily 段
- goals.md 为空 → "要不要先填？跳过今天对照也行"
- 候选人说"只记计划就行" → 跳过 a、d、habits，只写今日计划

### 升级提议
- 一天最多升级一次（每次 daily 完只问一遍 weekly + 一遍 quarterly）
- 候选人摇头不要追问、不要劝
- 当 weekly 和 quarterly 同时满足时，先问 weekly，再问 quarterly（quarterly 依赖 weekly 数据）

### 显式跳段
- "只做周复盘" → 跳过 daily，直接走 weekly 子流程
- "只做季复盘" → 跳过 daily 和 weekly，直接走 quarterly 子流程
- "今天只 daily" → 走完 daily 直接结束，不问升级
