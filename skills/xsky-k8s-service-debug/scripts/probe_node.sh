#!/usr/bin/env bash
# probe_node.sh — parallel basic-health probe across N nodes
#
# Usage:
#   probe_node.sh <ssh-key-path> <ip1> [ip2] ...
#
# Output:
#   For each node: hostname, uptime, load, mem, top mounts (excl tmpfs/overlay),
#   last 3 reboots, OS name.
#
# Read-only. Safe to run anytime.

set -u
KEY="${1:-}"
shift || true

if [[ -z "$KEY" || $# -lt 1 ]]; then
  echo "Usage: $0 <ssh-key-path> <ip1> [ip2] ..." >&2
  exit 2
fi

if [[ ! -r "$KEY" ]]; then
  echo "SSH key not readable: $KEY" >&2
  exit 2
fi

SSH_OPTS=(-i "$KEY" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null \
          -o ConnectTimeout=5 -o LogLevel=ERROR)

REMOTE_CMD='
echo "host=$(hostname)"
echo "date=$(date "+%Y-%m-%d %H:%M:%S %Z")"
echo "uptime: $(uptime)"
echo "--- mem ---"
free -h | head -3
echo "--- disk (excl tmpfs/overlay) ---"
df -hT 2>&1 | grep -vE "tmpfs|overlay|proc|sysfs|cgroup" | head -8
echo "--- recent reboots ---"
last reboot 2>/dev/null | head -3
echo "--- os ---"
grep -E "^(NAME|VERSION)=" /etc/os-release 2>/dev/null | head -2
'

for ip in "$@"; do
  (timeout 12 ssh "${SSH_OPTS[@]}" "root@$ip" "$REMOTE_CMD" 2>&1 | sed "s/^/[$ip] /") &
done
wait
