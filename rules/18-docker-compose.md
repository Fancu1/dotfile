---
description: Docker Compose workflow (start/build/ps/logs/down) with safe defaults and cleanup
globs: ["**/docker-compose.yml", "**/docker-compose.*.yml", "**/compose.yml", "docker/**"]
alwaysApply: false
---

## Scope
- Applies when: 需要用 Docker Compose 启动/重建/验证服务，或需要读取容器日志/状态
- Does NOT apply when: 纯代码阅读/文档输出，不涉及运行环境

## Ask First
- `docker compose up -d` / `docker compose up --build -d`（长时间运行、会占用资源）
- `docker compose down -v`（会删除 volumes，可能丢本地数据）

## Safe Defaults
- 不要使用 `docker logs -f`；只允许 `docker logs --tail=200 <container>`
- 若你需要显式指定 compose 文件：**不要只带一个 `-f docker-compose.yml`**，否则会跳过 `docker-compose.override.yml` 的自动加载。
  - 推荐：`docker compose up -d`
  - 必须 `-f` 时：`docker compose -f docker-compose.yml -f docker-compose.override.yml up -d`
- 操作前后用状态确认：
  - `docker compose ps`

## Resource Hygiene (After Commit)
- 当本次任务完成并且代码已提交（commit 已落地），且你不再需要该 worktree 的服务继续运行：
  - 在**目标 worktree 目录**执行：`docker compose down`
- 默认不要清理 volumes（避免误删数据）；如用户明确要求释放磁盘，再考虑 `docker compose down -v` 或手动 `docker volume rm ...`。
