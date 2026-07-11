#!/usr/bin/env bash
# Logs every AI-executed Bash command to ~/wpx/my/ai-commands.log
# Format:
#   # YYYY-MM-DD HH:MM:SS - <description>
#   <command>
#
# Triggered by PostToolUse hook on Bash in ~/.claude/settings.json.
# Reads hook input JSON from stdin.

jq -r '"\n# \(now | strflocaltime("%Y-%m-%d %H:%M:%S")) - \(.tool_input.description // "(no description)")\n\(.tool_input.command)"' \
  >> ~/wpx/my/ai-commands.log 2>/dev/null || true
