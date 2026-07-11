#!/usr/bin/env bash
# ~/.claude 配置 <-> dotfile 仓库 claude/ 目录的同步
#
# 用法:
#   ./sync.sh collect   # ~/.claude -> 仓库（镜像式，仓库里多余的会被删掉）
#   ./sync.sh apply     # 仓库 -> ~/.claude（覆盖同名文件，不删本机多余文件）
#
# 同步范围（白名单）:
#   文件: CLAUDE.md settings.json statusline-command.sh persona.md goals.md
#   目录: commands/ skills/ hooks/
# 白名单之外的一律不进仓库：凭证、settings.json.* 变体（含反代 token）、
# projects/（会话记录）、plans/、tasks/、plugins/、缓存等运行时内容。
set -euo pipefail

CLAUDE_DIR="$HOME/.claude"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FILES=(CLAUDE.md settings.json statusline-command.sh persona.md goals.md)
DIRS=(commands skills hooks)

case "${1:-}" in
collect)
  for f in "${FILES[@]}"; do
    cp -p "$CLAUDE_DIR/$f" "$REPO_DIR/$f"
  done
  for d in "${DIRS[@]}"; do
    rsync -a --delete --delete-excluded --exclude '.DS_Store' --exclude '__pycache__/' --exclude '*.pyc' "$CLAUDE_DIR/$d/" "$REPO_DIR/$d/"
  done
  ;;
apply)
  mkdir -p "$CLAUDE_DIR"
  for f in "${FILES[@]}"; do
    cp -p "$REPO_DIR/$f" "$CLAUDE_DIR/$f"
  done
  for d in "${DIRS[@]}"; do
    rsync -a --exclude '.DS_Store' --exclude '__pycache__/' --exclude '*.pyc' "$REPO_DIR/$d/" "$CLAUDE_DIR/$d/"
  done
  ;;
*)
  echo "usage: $0 {collect|apply}" >&2
  exit 1
  ;;
esac

echo "sync $1 done"
