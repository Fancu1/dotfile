---
description: Parallel worktrees + multiple Docker Compose stacks (isolation via COMPOSE_PROJECT_NAME, ports, test naming)
globs: ["**/*"]
alwaysApply: false
---

## Scope
- Applies when: 需要并发运行多套 Docker Compose（多 worktree 同时跑服务/测试，互不影响）
- Does NOT apply when: 只跑一套服务或不涉及 Docker/Compose

## Non-Negotiable (Isolation)
- **每个 worktree 必须有独立的 `COMPOSE_PROJECT_NAME`**，并确保同机运行时不会重复。
- **Host 端口必须全部唯一**（Postgres/Redis/Kafka/API/gRPC/pprof 等），否则会互相抢占端口。
- 避免 Docker 资源名冲突：container / volume / network / test container name。
- 所有 `docker compose` 命令必须在“目标 worktree 目录”执行（或确保同一套 `.env`/compose 项目配置被加载）。
- **不要只用 `-f docker-compose.yml` 启动**：指定 `-f` 会关闭默认的 `docker-compose.override.yml` 自动加载；如果必须用 `-f`，请显式带上 `-f docker-compose.override.yml`。

## Recommended Flow (Per Worktree)
0) Prefer repo-provided bootstrap scripts if present:
   - If the repo has `scripts/ensure-worktree-env.sh`, run it to generate/update `.env` with a unique `COMPOSE_PROJECT_NAME` and non-conflicting ports.
1) 创建 `.env` 并追加 worktree 变量：
   - `cp env.example .env`
   - `cat .env.worktree.example >> .env`
   - 修改 `.env` 中的 `COMPOSE_PROJECT_NAME` 与端口（保持唯一）
2) 启动该 worktree 的服务：
   - 推荐：`docker compose up -d`
   - 或（当你需要显式指定 compose 文件时）：`docker compose -f docker-compose.yml -f docker-compose.override.yml up -d`
3) 并行跑容器化测试时，显式隔离测试容器与网络（避免不同 worktree 抢同名容器/网络）：
   - `TEST_CONTAINER_NAME="${COMPOSE_PROJECT_NAME}-test" TEST_NETWORK="${COMPOSE_PROJECT_NAME}-net" make test`

## Shutdown After Completion (Resource Hygiene)
- 当一个需求/任务已经完成并提交（或你明确说“这个 worktree 已经完成”）：
  - **优先关闭该 worktree 的 Compose 栈以释放资源**：在该 worktree 目录执行 `docker compose down`
  - 不要默认执行 `docker compose down -v`（会删除 volume，可能丢本地数据）
- 若用户明确希望保留服务继续跑（例如用于手动验收、或另一个任务依赖该栈），则跳过 shutdown。

## Notes
- 如果 repo 的 `docker-compose.override.yml` 使用 `COMPOSE_PROJECT_NAME` 来命名 network/volume/container，则上述隔离策略通常是充分的。
- 若发现 Kafka/Redis/Postgres 仍互相影响，优先检查：端口是否重复、`.env` 是否被正确加载、以及是否误在“另一个 worktree 目录”执行了 `docker compose` 命令。
- 排障快速法：在目标 worktree 里跑 `docker compose config`，确认 `ports:` 是否出现了你期望的 `${POSTGRES_PORT}` 等值，以及 `container_name`/`networks`/`volumes` 是否带 worktree 的 `COMPOSE_PROJECT_NAME` 前缀。
