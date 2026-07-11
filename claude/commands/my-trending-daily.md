---
description: 每日 GitHub trending 推荐 — 三窗口（monthly + weekly + daily）+ 多语言数据视角，每天产出 reports/YYYY-MM-DD.md，按分类列出 + Top 10 + 优先级
---

# 任务：每日 GitHub trending 推荐

读完这个 prompt 直接开始执行。当前调用形态：用户每天手动触发 `/my-trending-daily`，期望产出 `~/wpx/my/my-trending/reports/YYYY-MM-DD.md`。

每天一份新文件。同日重跑覆盖。

## 输入解析

参数（紧跟 `/my-trending-daily` 后的字符串）：

- **无参数** → `DATE_KEY = $(TZ=Asia/Shanghai date +%Y-%m-%d)`
- **`YYYY-MM-DD` 格式**（如 `2026-04-15`） → 显式日期（补跑）
- **其他自然语言**（如 `偏 RAG`） → `DATE_KEY` 用默认（当天），自然语言作为本次"侧重"补充进画像匹配

## 工作流（严格按顺序）

1. **解析参数**，得到 `DATE_KEY` 和可选的"侧重"短语
2. `cd ~/wpx/my/my-trending`
3. `git pull --rebase origin main`（失败警告但继续，不阻塞）
4. 准备目标 `reports/$DATE_KEY.md`：已存在则**覆盖**（同日重跑覆盖是预期行为）
5. Read `trending-profile.md`，**所有推荐必须扎根此文件**
6. **WebFetch 多窗口 + 多语言（可并发）：**

   全语言（看绝对热度、抓爆款）：
   - `https://github.com/trending?since=monthly`
   - `https://github.com/trending?since=weekly`
   - `https://github.com/trending?since=daily`

   语言过滤（抓用户主栈深耕项目，避免被全语言榜 Python / TS 爆款挤出可见区）：
   - `https://github.com/trending/go?since=monthly`（Go：用户主栈）
   - `https://github.com/trending/go?since=weekly`
   - `https://github.com/trending/python?since=monthly`（Python：大厂样板、Anthropic、Agent 框架）
   - `https://github.com/trending/typescript?since=monthly`（TS：Coding harness、Agent 平台）
   - `https://github.com/trending/rust?since=monthly`（Rust：终端、沙箱）

   每个 URL 抓 top 25：`owner/repo`、主语言、总 stars、窗口增量、一句 desc。

   **抓不全 fallback**：如果某个 URL 返回的可解析项目数 < 20，用 curl 兜底：
   `curl -sL '<url>' -o /tmp/t-<lang>-<window>.html`，再用 python 解析 HTML 抽 repo 列表。
7. **去重合并**（按 `owner/repo`），记录每个项目命中的"来源 fetch"集合（共 8 个可能值）：
   - 全语言：`monthly-all` / `weekly-all` / `daily-all`
   - 语言过滤：`monthly-go` / `weekly-go` / `monthly-python` / `monthly-ts` / `monthly-rust`
   多重命中（≥ 3 个来源、或全语言+语言过滤双中）是强信号，优先列入
8. **严过滤**（按 `trending-profile.md` 的"略过"规则）：
   - awesome-lists / 纯 curated lists → 排除
   - 纯教程 / 学习材料（除非高质量系统性教程）→ 排除
   - 纯 demo / 一次性玩具 → 排除
   - 非技术（书单、营销）→ 排除
   - 加密货币 / 投机 → 排除
   - 纯前端 UI 库 / JS-TS 纯前端框架（除非与 AI 平台强相关）→ 排除
   - 推不出"对用户有什么具体学习点" → 排除
   留 25-30 个为目标
9. **自适应分类**（按当日项目 organic 分组）。常见维度（按需用，不强凑）：
   - LLM 网关 / 模型路由
   - Agent 编排 / Multi-Agent
   - RAG / 向量检索
   - Memory / 上下文管理
   - Dev Tools / Coding Agent
   - 基础设施 / 可观测
   - 沙箱 / 安全约束
   - MCP / 工具协议
   - 大厂样板（Anthropic / Google / 腾讯等）
10. **写 `reports/$DATE_KEY.md`**，结构见下
11. **更新 `INDEX.md`**：在表格中查找 `| $DATE_KEY |` 开头的行：
    - 已有该日行 → **替换**为最新数据
    - 没有 → 在表格分隔符下一行**插入新行**（最新在上）
    格式：`| $DATE_KEY | [reports/$DATE_KEY.md](reports/$DATE_KEY.md) | <项目数> | <Top 10 主题，一句话> |`
12. `git add reports/$DATE_KEY.md INDEX.md`
13. **不**自动 commit / push。终端打印：
    > 已 stage `reports/$DATE_KEY.md` 和 `INDEX.md`，请 review 后 commit / push。

## 报告结构（写到 `reports/$DATE_KEY.md`）

```markdown
# Trending Report — YYYY-MM-DD

_Source: github.com/trending — 8 个来源（全语言 monthly/weekly/daily + Go monthly/weekly + Python/TS/Rust monthly）去重_
_生成时间: <ISO8601> CST_

## 概要
- 8 个来源去重后原始：~XX 个
- 严过滤后：N 个
- 今日观察：1-2 句对比最近一份 `reports/<上次日期>.md`（如有就提关键差异，否则跳过）

## 完整列表（按分类）

### 类别名（如：LLM 网关 / 模型路由）

#### owner/repo（Lang · 总 N⭐ · 月度 +XK · 来源：monthly-all + monthly-go + weekly-go）
- **解决什么问题**：1-2 句
- **能用来做什么**：1-2 句
- **学习点**：1-2 句（关联用户技术栈，简短）

(更多分类...)

## 你只读 10 个：推荐这 10

(每项 200-300 字，明确关联用户项目 / 转型方向)

### 1. owner/repo
**为什么推荐**：扎根你 X 项目 / Y 方向...

(2-10 同结构)

## 优先级排序（高 → 低）

1. **owner/repo** — 排第 1：1-2 句（为啥优先于第 2）
2. **owner/repo** — 排第 2：1-2 句
...
10. ...

## 警示（如出现反模式）

(纯 Agent 放飞 / 灰色中转 / hype 无落地 / 编造 benchmark)
```

## 硬规则

- 全程中文输出（报告模板中固定的英文标签如 `Trending Report`、`Source:` 保持原样，其余叙述性内容用中文）
- 不动 `trending-profile.md` / `scripts/` / 既有非当日 reports
- 完整列表每项 80-120 字
- Top 10 推荐每项 200-300 字，明确关联用户项目（AI 排障 / Venus / Scope）或转型方向
- 优先级排序每项 1-2 句解释为什么排这个位置
- "推不出具体学习点 / 关联点" 的项目直接略过，不要硬凑
- WebFetch 单窗口失败：标注"数据源 X 异常"+ 错误日志，剩下窗口正常出报告
- 三窗口都失败：报错退出（无米下锅）
- 同日报告已存在 → **覆盖**（重跑覆盖是预期行为）
- 不调 GitHub API（trending 页够）
- 不自动 commit / push（用户每天手动 review；如果未来接入自动化，commit/push 策略另议）

## 可读性原则

- 不写"X 是 Y 团队做的 Z 框架"百科式开头
- 推荐理由要具体，不要"对 AI 开发有用"这种泛泛的话
- ✅ 好："你排障平台 YAML 模板注册工具 + 这个项目的 schema 校验更严，可以挪用减少手写"
- ❌ 差："对你方向有用"

开始。
