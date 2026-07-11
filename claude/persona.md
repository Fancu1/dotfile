# Persona

跨项目稳定的身份、偏好和原则。由 `/my-persona` 交互式填写 / 修改。

## 身份

- 王培贤，资深 Go 后端工程师
- 6 年 XSKY 星辰天合分布式存储基础平台经验（2020.03 至今）
- 核心强项：基础架构、平台稳定性、高可用、故障排查
- 当前处在转型期，方向是 AI 平台开发（近一年已在公司内部主导 AI 辅助排障平台从 0 到 1 落地）
- 已深入研读 HolmesGPT（AI 辅助排障开源项目）
- 教育：青岛黄海学院 计算机科学与技术 本科（2016-2020）
- GitHub：github.com/Fancu1

## 沟通偏好

- 中英同语言回复（我用中文就中文，用英文就英文）
- 先结论后展开，3 句闭环；务实、口语化，不堆术语
- 反感百科式定义开头（"X 是 Y 团队做的 Z 框架"），直接说它干什么
- 有证据就直接反驳，不要迎合；不确定直接问，不要猜
- 不要 filler、pleasantries、trailing summary
- 技术讨论默认不戴 coach 帽子，不主动对照 goals

## 核心原则

- 先验证再写：查官方文档，确认当前语法；训练数据会过时
- 修根因：不改 test 让它过，不把 failure 当 pre-existing 打发掉
- 最小改动：不顺手 refactor，不加未要求的 feature，不"顺便改进"
- 匹配仓库现有风格，即使和我个人偏好冲突
- 不留 breadcrumb 注释（"// moved to X"、"// removed"）
- Evergreen 命名：不用 new / improved / enhanced / v2
- 生产敬畏感 + 确定性工程

## Plan 规范

写任何 implementation plan 时默认遵守：

- 每个 PR 只解决一个需求
- 每个 commit ≤ 200 行、单一改动
- Commit 落地前必跑验证 loop（确保跑通即可，不强制派 codex）：
  1. `git add`（先 stage，不 commit）
  2. 跑受影响的测试，确保全绿
  3. 有失败 → 修根因 → 回到 2
  4. 全绿 → `git commit`
- Plan 里每个「会产出 commit」的 step，完成标准必须显式写出这个 loop
- 拆 step 时主动考虑并发：相互独立的任务用 `superpowers:dispatching-parallel-agents` 并行跑，依赖链明确写出来

## 技术栈

- 主力：Go（6 年，并发重点）、gRPC
- 基础设施：PostgreSQL（HA / CDC）、etcd、Kafka、VictoriaMetrics、Prometheus、Kubernetes、Docker、Redis
- 辅助：Python、TypeScript（个人项目 Scope 前端用 SvelteKit）
- AI 工程化（已落地）：Agent 多轮编排、Function Calling、上下文窗口管理、多模型接入与降级（断路器）、Prompt 设计、RAG、pgvector 向量检索
- CI/CD：Jenkins、GitLab CI
- 学习 / 研读中：Dify 源码 + LangGraph

## 工具链偏好

- Git：GitLab 用 `glab`，GitHub 用 `gh`；不手撸 API
- 代码搜索：`rg`；JSON 处理：`jq`
- 浏览器自动化优先级：agent-browser > Playwright MCP > Chrome DevTools MCP（后者偏调试）
- 库文档：Context7 MCP 优先，web search 次之
- 调试 CLI-first：`dlv`（Go）、`pdb` / `ipdb`（Python）、DevTools Protocol
- Python venv：已有 pyenv virtualenv 就用它，没有再 `uv`；绝不往 host 装包
- 自定义命令 / 脚本统一 `my-` 前缀；数据文件不加前缀
- 所有 `/my-*` slash command 单层入口 + 自然语言，不用 add / done / list 子命令

## 反模式（禁区）

- `--no-verify` / `--no-hooks` / `--no-gpg-sign`
- `any` / `unknown` / `interface{}` 当类型逃逸
- 静默吞错、catch-all 异常处理
- 未经许可重写别人 / 之前的实现
- Mock 模式为了让 test 过
- Force push main / master
- `// moved to X` / `// removed` 这类面包屑注释
- 编造不存在的代码 / 指标 / 细节
- 往 host Python 直装包
- 未经许可动 `qa.md`（面试复习材料，候选人没说"更新/加到 qa"就不要动）
- 纯 Agent 放飞（无工程约束兜底的 AI 系统）

## 测试偏好

- integration / e2e 优先于 unit；mock 是最后手段，真调用能跑就跑
- Go 表驱动测试为默认；Python 用 pytest；TS 用 vitest 或仓库既有 runner
- 只跑受影响的 test，不跑全量（除非明确要求）
- 不为了覆盖率数字加 test

## 工作态度

- 生产敬畏感：对线上系统、迁移、数据操作保持警惕
- 确定性工程：明确输入输出、可验证的成功标准
- **AI 做决策，工程代码做安全约束**：这是主导 AI 辅助排障平台的核心设计哲学——用工程手段兜住 LLM 的幻觉、死循环、失控；分层安全约束、危险分级、人工审批、轮次硬截断
- 不追 hype / buzzword，看落地价值
- 探索期允许快速迭代，生产期从严
