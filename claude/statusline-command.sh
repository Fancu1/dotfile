#!/usr/bin/env bash
# Claude Code status line
# Layout: 🍃 branch · 🌳 worktree[ [linked]] · /absolute/path   model  ctx:NN%  session
# Git detection is worktree-aware: it works inside linked git worktrees
# (where .git is a file, not a directory).

input=$(cat)

# ---- current directory (full, absolute) ----
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
[ -z "$cwd" ] && cwd="$PWD"

# ---- git: branch + worktree (worktree-aware via `git -C`) ----
branch=""
worktree=""
worktree_linked=""
if git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch=$(git -C "$cwd" branch --show-current 2>/dev/null)
  # Detached HEAD -> short sha
  [ -z "$branch" ] && branch="@$(git -C "$cwd" rev-parse --short HEAD 2>/dev/null)"

  toplevel=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)
  [ -n "$toplevel" ] && worktree=$(basename "$toplevel")

  # A linked worktree's git dir lives under <mainrepo>/.git/worktrees/<name>
  gitdir=$(git -C "$cwd" rev-parse --absolute-git-dir 2>/dev/null)
  case "$gitdir" in
    */worktrees/*) worktree_linked=1 ;;
  esac
fi

# ---- model / context / session ----
model=$(echo "$input" | jq -r '.model.display_name // ""')
remaining=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')
session_short=$(echo "$input" | jq -r '.session_id // empty' | cut -c1-8)
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty')
transcript_url=""
[ -n "$transcript_path" ] && transcript_url="file://${transcript_path}"

# ---- assemble ----
sep=' \033[2m·\033[0m '
first=1

# branch (green + leaf icon)
if [ -n "$branch" ]; then
  printf '\033[32m🍃 %s\033[0m' "$branch"
  first=0
fi

# worktree (magenta + tree icon; distinct from the green branch for CVD)
if [ -n "$worktree" ]; then
  [ "$first" -eq 0 ] && printf '%b' "$sep"
  if [ -n "$worktree_linked" ]; then
    printf '\033[35m🌳 %s\033[0m \033[2m[linked]\033[0m' "$worktree"
  else
    printf '\033[35m🌳 %s\033[0m' "$worktree"
  fi
  first=0
fi

# full absolute path (bold)
[ "$first" -eq 0 ] && printf '%b' "$sep"
printf '\033[1m%s\033[0m' "$cwd"

# model
[ -n "$model" ] && printf '  \033[34m%s\033[0m' "$model"

# context remaining
if [ -n "$remaining" ]; then
  remaining_int=${remaining%.*}
  if [ "${remaining_int:-100}" -le 20 ]; then
    color='\033[31m'   # red
  elif [ "${remaining_int:-100}" -le 50 ]; then
    color='\033[33m'   # yellow
  else
    color='\033[32m'   # green
  fi
  printf "  ${color}ctx:%s%%\033[0m" "$remaining_int"
fi

# session id — OSC 8 hyperlink to the transcript JSONL
if [ -n "$session_short" ]; then
  if [ -n "$transcript_url" ]; then
    printf '  \033[2m\033]8;;%s\033\\%s\033]8;;\033\\\033[0m' "$transcript_url" "$session_short"
  else
    printf '  \033[2m%s\033[0m' "$session_short"
  fi
fi

printf '\n'
