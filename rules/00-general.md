---
description: General collaboration rules (language, tooling hygiene, safety)
globs: ["**/*"]
alwaysApply: true
---

## Default Language
- 默认用简体中文解释与总结。
- 代码标识符/文件名/函数名保持英文。
- 注释跟随仓库风格；若无既有风格，默认英文注释。

## Tooling & Command Hygiene
- 优先使用仓库已有脚本/Makefile/package scripts（参考 `90-project-profile.md`）。
- 搜索优先 `rg`（文本）与 `rg --files`（文件），避免交互式 TUI。
- 避免会卡住的命令：任何长时间运行（dev server、watch、compose up 等）都必须 Ask First，除非用户已明确授权。
- 命令尽量加非交互参数（例如 `--yes`），避免等待输入。

## Git Worktrees（默认隔离开发，不污染当前工作目录）
当任务需要改代码/改配置/跑测试，且目标目录是 git repo：
- 默认在 **git worktree** 中开发与验证，不直接修改用户当前工作目录（除非用户明确要求“直接在当前目录改/不使用 worktree”）。
- 默认 worktree 位置（优先级从高到低）：
  - 若 repo 内存在 `.worktrees/`：优先放到 `./.worktrees/<branch>`（便于与项目一起管理）
  - 否则使用全局目录（不进仓库）：`~/.codex/worktrees/<repo-name>/<branch>`
- 默认分支命名：`codex/<task-type>/<yyyymmdd>/<slug>`（保持短、ASCII、可读）

执行流程（确定性，默认 PR-first）：
1) 在用户当前目录识别 repo root 与 base branch（通常是当前分支）。
2) 创建 worktree + 新分支，后续所有编辑/测试都在 worktree 内完成。
3) 验证通过后：在 worktree 内提交 commit（默认 1 个；除非用户要求拆分）。
4) 默认不做本地 merge：输出分支名与 commit hash，给出创建 PR 的下一步建议（但不自动 `push` / `gh pr create`）。
5) 仅当用户明确要求“合回本地 base branch / 合主线跑测试”时，才执行本地 merge（优先 `--ff-only`），并在输出里给出验证证据。
6) worktree 清理策略：默认保留（便于并行迭代）；只有用户明确要求或确认不再需要时才清理。

PR 准备约定（团队式）：
- PR 前做一次同步：优先 `git rebase <base>`（或 `git merge <base>`，按团队习惯），并在同步后重跑关键测试。
- 需求间有依赖：优先“堆叠 PR”（B 基于 A 分支）或 feature flag，避免把多个需求揉进同一分支/PR。

并行 Worktree（多套 Docker Compose）：
- 若 repo 存在 `.env.worktree.example` 或依赖 `COMPOSE_PROJECT_NAME` 做容器/网络隔离：在执行 `docker compose ...` / `make test` 之前，**优先自动运行** `scripts/ensure-worktree-env.sh`（若存在）以生成/更新 worktree 的 `.env`，避免端口/网络/容器名冲突。

兜底与安全：
- 若 repo 不存在 / 不是 git repo：跳过 worktree 流程，直接在当前目录工作，并明确标注原因。
- 若 base worktree 有未提交变更：仍可在 worktree 完成开发与提交，但**不自动 merge 回来**（避免踩用户 WIP）；改为输出分支/commit 信息 + 让用户决定合并时机。
- 禁止自动 `push` / `gh pr create` 等外部动作（除非用户明确要求），遵循 `External Side Effects`。

## Network / Proxy（网络问题优先用环境变量）
- 若遇到网络问题（超时、连接失败、拉取依赖/镜像失败等），优先在当前 shell 里开启代理后再重试命令：
  - `export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890`
  - 例如：`docker pull` / `docker compose build` / `git clone` / `npm install` 失败时，先设置代理再重试。
- 避免依赖用户本机自定义的 alias/function；规则与文档里统一用可复制的 `export ...` 指令。

## Logs Rule
- 禁止使用 `*-f` 跟随日志（如 `docker logs -f`）。
- 只允许 tail：`docker logs --tail=200 <container>` 或同等工具。

## Safety Baseline
- 只有在用户允许的前提下，才可以写入/提交任何密钥、token、真实账号密码；
- 避免破坏性命令默认执行（删除数据、重置环境、清库、重建集群等）。如需要必须 Ask First 并说明影响/可回滚方式。

## External Side Effects（外部副作用，必须可控）
以下行为视为“外部副作用”，除非用户明确说“执行/发送/创建/关闭/发布/合并”等动作，否则只能停留在“草稿/建议/本地变更”：
- 发送或发布：Email、Slack/IM、推文/帖子、公告、消息通知
- 修改第三方系统：Linear/Jira 工单、GitHub 评论/合并/关闭、云资源/权限变更、支付/订阅配置
- 任何会触发费用、配额消耗或不可逆影响的操作

默认策略：
- 先给出 **Dry-run**（草稿/计划/将要执行的命令），再执行副作用动作。
- 若需要凭证：只接受用户通过安全方式在本机环境变量/凭证管理器里配置；不在代码/文档/日志中回显明文。
