#!/usr/bin/env bash
# probe_storage.sh — full storage-stack walk on a single host
#
# Usage:
#   probe_storage.sh <ssh-key-path> <ip> [device-name]
#
#   device-name (optional): focus on /dev/<device-name>. If omitted, scans all
#                            iSCSI-related devices.
#
# Output:
#   Mount table, iSCSI sessions, dmesg XFS/SCSI errors (with timestamps),
#   iostat sample, error counters, XFS shutdown events.
#
# Read-only. No mutating commands.

set -u
KEY="${1:-}"; IP="${2:-}"; DEV="${3:-}"

if [[ -z "$KEY" || -z "$IP" ]]; then
  echo "Usage: $0 <ssh-key-path> <ip> [device-name]" >&2
  exit 2
fi

SSH_OPTS=(-i "$KEY" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null \
          -o ConnectTimeout=5 -o LogLevel=ERROR)

REMOTE_CMD='
echo "=== 1) mount table (iSCSI / XFS): ==="
mount | grep -E "iscsi|/dev/sd" | head -30 || true

echo
echo "=== 2) iSCSI sessions: ==="
iscsiadm -m session 2>&1 || true

echo
echo "=== 3) /proc/mounts iSCSI lines: ==="
grep -E "iscsi|/dev/sd" /proc/mounts 2>&1 | head -20 || true

echo
echo "=== 4) lsblk all disks: ==="
lsblk -o NAME,MAJ:MIN,SIZE,STATE,TYPE,MOUNTPOINT 2>&1 | head -40

echo
echo "=== 5) Any XFS shutdown / log error in dmesg: ==="
dmesg -T 2>&1 | grep -E "xfs_do_force_shutdown|Shutting down filesystem|Log I/O error|Corruption Alert" | tail -10

echo
echo "=== 6) Recent SCSI command errors: ==="
dmesg -T 2>&1 | grep -E "sd [0-9]+:.*(parity error|FAILED Result|timing out command|Aborted Command)" | tail -15

echo
echo "=== 7) Recent XFS metadata / IO errors: ==="
dmesg -T 2>&1 | grep -E "XFS \(sd" | grep -iE "error|fail|shutdown" | tail -15

echo
echo "=== 8) iostat sample (5s): ==="
iostat -xy 1 5 2>&1 | grep -E "Device|sd[a-z]+" | tail -30 || echo "iostat not installed"
'

if [[ -n "$DEV" ]]; then
  REMOTE_CMD+="
echo
echo \"=== 9) Focus on /dev/$DEV: ===\"
ls -la /dev/$DEV 2>&1
cat /sys/block/$DEV/device/ioerr_cnt 2>&1 || echo \"no ioerr_cnt\"
xfs_info /dev/$DEV 2>&1 | head -5 || echo \"not an XFS or not mounted\"
echo \"raw read test (4K, direct):\"
timeout 8 dd if=/dev/$DEV of=/dev/null bs=4K count=1 iflag=direct 2>&1
"
fi

timeout 45 ssh "${SSH_OPTS[@]}" "root@$IP" "$REMOTE_CMD" 2>&1
