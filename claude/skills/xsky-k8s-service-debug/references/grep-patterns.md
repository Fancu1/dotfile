# Grep / Awk Patterns

Reusable patterns for sifting noisy outputs (dmesg, container logs, journald) without loading the whole file.

## Kernel events (dmesg) — XFS / SCSI / iSCSI

```bash
# Any XFS failure on this host
dmesg -T | grep -E 'XFS \([a-z]+\)' | tail -20

# Anything pointing to force shutdown (Pattern 1)
dmesg -T | grep -E 'xfs_do_force_shutdown|Shutting down filesystem|Log I/O error|Corruption Alert'

# Any SCSI command-layer failures (Pattern 2)
dmesg -T | grep -E 'sd [0-9]+:.*(parity error|FAILED Result|timing out command|Aborted Command|Add. Sense:)'

# Just for a specific device
dev=sdX; dmesg -T | grep -E "XFS \($dev\)|sd .*\[$dev\]" | tail -30

# Time-window grep (from a timestamp onward)
dmesg -T | awk '/三 5月 13 04:25/,EOF' | head -50
# or English locale: awk '/Wed May 13 04:25/,EOF'

# Reboots / panics / OOM
dmesg -T | grep -iE 'panic|oops|out of memory|Killed process|hung_task|hardware error'

# iSCSI session / network at the kernel level
dmesg -T | grep -iE 'iscsi|connection error'
```

## Container Logs

```bash
# Read only the tail — never raw `docker logs <c>` on a verbose container
docker logs --tail 100 <c> 2>&1 | tail -120

# Time-bounded
docker logs --since 30m <c> 2>&1 | grep -iE 'error|fatal|panic|exception' | tail -30

# Java startup milestones (Jenkins specifically)
docker logs <jenkins> 2>&1 | grep -E 'InitReactorRunner.*onAttained|Jenkins is fully|Completed initialization' | head -20

# PostgreSQL crash + recovery
docker logs <pg> 2>&1 | grep -E 'PANIC|FATAL|redo starts|redo done|ready to accept|invalid record' | tail -30
```

## K8s Pod Events

```bash
KUBE_NODE='docker exec kube-apiserver kubectl --kubeconfig=/etc/kubernetes/ssl/kubecfg-kube-node.yaml'
KUBE_EVT='docker exec kube-apiserver kubectl --kubeconfig=/etc/kubernetes/ssl/kubecfg-kube-controller-manager.yaml'

# Cluster anomaly snapshot
$KUBE_NODE get pods -A 2>&1 | grep -vE 'Running|Completed|^NAMESPACE'

# Pod events (controller-manager kubeconfig required)
$KUBE_EVT get events -n <ns> --field-selector involvedObject.name=<pod> --sort-by=.lastTimestamp 2>&1 | tail -15

# Recent cluster-wide warnings
$KUBE_EVT get events -A --field-selector type=Warning --sort-by=.lastTimestamp 2>&1 | tail -25
```

## /var/log/messages (CentOS / RHEL family)

```bash
# Time-window slice
awk '/^May 13 04:2[5-9]/,/^May 13 04:35/' /var/log/messages | head -100

# Crash-related (around suspected reboot)
grep -iE 'panic|fatal|hung_task|out of memory|shutdown|reboot' /var/log/messages | tail -30
```

## /proc-based Process State

```bash
# JVM (find real PID after tini)
JPID=$(pgrep -f 'jenkins.war' | head -1)

# Thread state distribution
for t in /proc/$JPID/task/*/status; do awk '/^State:/ {print $2}' "$t" 2>/dev/null; done | sort | uniq -c | sort -rn
# Reading: many S=sleeping (waiting on IO/network), R=running, D=disk-stuck

# D-state threads — what are they waiting on?
for t in /proc/$JPID/task/*; do
  tid=$(basename "$t")
  st=$(awk '/^State:/ {print $2}' "$t/status" 2>/dev/null)
  if [ "$st" = "D" ]; then
    echo "tid=$tid wchan=$(cat "$t/wchan" 2>/dev/null) stack:"
    head -5 "$t/stack" 2>/dev/null
  fi
done
```

## iSCSI / Mount

```bash
# Session list, brief
iscsiadm -m session 2>&1

# Session detail (per-portal state, error counts)
iscsiadm -m session -P 1 2>&1 | head -40

# Mount table for iSCSI-backed
mount | grep -E 'iscsi|/dev/sd'

# /proc/mounts is the kernel truth (mount command may stale-cache)
grep iscsi /proc/mounts

# Per-device error counter (iSCSI / SCSI both)
cat /sys/block/<dev>/device/ioerr_cnt 2>&1
```

## "What's busy right now"

```bash
# IO at the device level
iostat -xy 1 5 | grep -E 'Device|<dev>'

# CPU & process — top X by CPU
top -bn1 -p $JPID
top -bn1 | head -20

# D-state processes globally (often the first signal of stuck IO)
ps -eo pid,state,wchan:30,cmd | awk '$2 ~ /D/'
```

## Time Stamp Cross-Reference

Always include timestamps in your evidence table. The CST/UTC offset frequently trips up correlation:

| Source | Timezone |
|---|---|
| `dmesg -T` | Local (`/etc/timezone`, usually CST on these hosts) |
| `journalctl` | Local |
| `docker logs` | **Container-internal** — often UTC! Check the timestamp prefix. |
| PostgreSQL log | UTC by default (`log_timezone` setting) |
| Jenkins log | UTC by default |
| `kubectl get events` | UTC (RFC3339) when `-o json`; relative ("3m ago") in default output |

Convert UTC → CST: add 8 hours.

## Don't Do This

- `docker logs <container>` without `--tail` / `--since` on a long-running container. Easy to push tens of MB into context.
- `cat /var/log/messages` — same problem. Use `awk` time slicing.
- `dmesg` without `-T` — raw uptime seconds are unreadable for cross-correlation.
- `grep` over the whole `/var/jenkins_home/workspace/` — too many files. Scope to `@script/*` first.
