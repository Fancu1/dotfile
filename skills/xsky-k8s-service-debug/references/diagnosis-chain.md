# Diagnosis Chain Reference

The fixed evidence chain when a service is reported broken. Walk every layer top-down, do not skip.

## Layer 0: Symptom Capture

Before SSH, write down:
- Service name
- User-visible symptom (HTTP code, error message, "can't log in", "build hangs", etc.)
- Approximate start time
- Is it currently ongoing or recovered?
- Did anything change recently (deploy, network maintenance, storage maintenance)?

## Layer 1: Node Connectivity & Health

Single parallel SSH burst to all candidate nodes:

```bash
for ip in <IPs>; do
  (timeout 8 ssh -i <KEY> -o ... root@$ip \
    "hostname; uptime; date; free -h | head -3; df -hT 2>&1 | grep -vE 'tmpfs|overlay' | head -8; last reboot | head -3" \
    2>&1 | sed "s/^/[$ip] /") &
done; wait
```

**What to look for:**
- Unreachable nodes (while peers are reachable) → network or node death
- Recent unexpected reboot (uptime small, peers uptime large) → likely kernel issue
- 15-min load >> CPU count → process pileup, often stuck-IO
- Memory available near 0 → OOM territory
- Disk usage > 90% → may have already triggered fs errors

## Layer 2: Deployment Shape Identification

Per candidate node, identify which orchestration owns the service:

```bash
ssh root@<host> '
  echo "=== K8s presence: ==="
  ls /etc/kubernetes/ 2>/dev/null | head -3
  ps -ef | grep -E "kubelet|kube-apiserver" | grep -v grep | head -3
  echo "=== Docker presence: ==="
  docker ps -a 2>&1 | head -5
  echo "=== docker-compose files: ==="
  find /home /opt /srv /root -maxdepth 4 -name "docker-compose*.yml" 2>/dev/null | head -10
  echo "=== systemd units for service: ==="
  systemctl list-units --type=service --all 2>&1 | grep -i "<service>" | head -5
'
```

## Layer 3: Pod / Container State

### K8s side

```bash
KUBE='docker exec kube-apiserver kubectl --kubeconfig=/etc/kubernetes/ssl/kubecfg-kube-node.yaml'

# Full anomaly view (not just the target service)
$KUBE get pods -A 2>&1 | grep -vE 'Running|Completed|^NAMESPACE'

# Target pod details
$KUBE get pod <name> -n <ns> -o wide
$KUBE describe pod <name> -n <ns> | tail -40   # events at the bottom

# Pod events (requires controller-manager kubeconfig)
EVT='docker exec kube-apiserver kubectl --kubeconfig=/etc/kubernetes/ssl/kubecfg-kube-controller-manager.yaml'
$EVT get events -n <ns> --field-selector involvedObject.name=<pod> --sort-by=.lastTimestamp | tail -20
```

### Docker side (standalone)

```bash
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.RunningFor}}'
docker inspect <name> --format 'Status={{.State.Status}} ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}} StartedAt={{.State.StartedAt}} FinishedAt={{.State.FinishedAt}} Health={{.State.Health.Status}}'
docker logs --tail 60 <name> 2>&1 | tail -80
```

### Container-exit code map

| Code | Likely meaning | Investigation |
|---|---|---|
| 0 | Normal exit | Why did the process choose to exit? Check logs. |
| 1 | App error | Logs almost always have a stack trace or error message |
| 137 | SIGKILL — usually OOM or `docker kill` | Check `OOMKilled=true`, dmesg for `Out of memory` |
| 139 | SIGSEGV — segfault | Often consequence of bad IO (e.g. PG `pg_control: IO error`). Check disk and dmesg. |
| 143 | SIGTERM — graceful kill | Likely orchestrator (healthcheck failure → docker stop, kubelet eviction, autoheal) |
| 255 | Java fatal init / unhandled | First log line of next start usually shows config error |

## Layer 4: Application-Layer Health (Important)

`Running` from K8s/Docker only means the supervisor sees the process. Always actively poke the app:

| App | Probe |
|---|---|
| HTTP (Jenkins, Grafana, Rancher, ...) | `docker exec <c> curl -sS -m 5 -o /dev/null -w '%{http_code} %{time_total}s\n' http://localhost:<port>/` |
| Jenkins JVM specifically | Above; if 500, fetch the body — `oops.jelly` loading failure means data volume IO error |
| PostgreSQL | `docker exec <c> pg_isready -U <user>` |
| Redis | `docker exec <c> redis-cli ping` |
| Artifactory (multi-service) | Router: `curl -sS http://localhost:3000/router/api/v1/system/health` (requires auth — 302 redirect counts as "service alive but ACL gating, which is normal") |

For Java/long-startup services:
- Find real PID via `pgrep -f <jar/war-name>` or `pgrep -P <tini-pid>`
- Thread state distribution: `for t in /proc/<pid>/task/*/status; do awk '/^State:/ {print \$2}' "$t"; done | sort | uniq -c`
- Many `S` (sleeping) + low CPU = waiting on network IO (slave reconnect, DB connect, plugin init). Not stuck on disk.
- Many `D` (uninterruptible sleep) + low CPU = stuck on disk IO. Storage layer is the next stop.
- Many `R` (running) + high CPU = actual CPU work.

## Layer 5: Storage Stack Walk

If application logs / probes show "Input/output error", "could not fsync", "could not open file", "no space", or anything storage-flavored:

```bash
# 1. What's mounted at the suspicious path?
mount | grep -E '<mountpoint>|<expected-device>'

# 2. Is the underlying device alive at the block layer?
ls -la /dev/<dev>          # exists?
dd if=/dev/<dev> of=/dev/null bs=4K count=1 iflag=direct 2>&1     # raw read works?

# 3. Is the file system alive?
ls <mountpoint> 2>&1       # "Input/output error" here while raw dev reads fine = XFS shutdown
stat <mountpoint> 2>&1
df -h <mountpoint> 2>&1
xfs_info /dev/<dev> 2>&1   # "not a mounted XFS filesystem" = XFS has been force-shut

# 4. iSCSI session state (if iSCSI-backed)
iscsiadm -m session
iscsiadm -m session -P 1 | head -20   # per-session detail
# All TCP portals up?
for p in 10.252.2.41 10.252.2.42 10.252.2.43; do
  timeout 3 bash -c "</dev/tcp/$p/3260" 2>&1 && echo "$p:3260 OPEN" || echo "$p:3260 CLOSED"
done

# 5. Kernel evidence
dmesg -T | grep -E 'XFS|sd [0-9]+:|iscsi|scsi.*error' | tail -40
cat /sys/block/<dev>/device/ioerr_cnt    # accumulated IO errors

# 6. Real-time IO activity
iostat -xy 1 5 | grep -E 'Device|<dev>'
```

The XFS-specific failure modes are described in `iscsi-xfs-patterns.md`.

## Layer 6: Cross-Service Correlation

Once a layer-5 root cause is found (especially iSCSI / XFS / network), **enumerate other services that share** the broken resource:

```bash
# Same iSCSI target/portal?
grep -l '<iqn>' /etc/iscsi/ /var/lib/iscsi/ 2>/dev/null
# Other services pinned to the same node?
$KUBE get pods -A -o wide 2>&1 | awk -v n=<node> '$8==n {print}'
# Other services with mount in same parent directory?
mount | grep <mount-parent>
```

The number of victims with the same time-window kernel error is the strongest correlation signal.

## Layer 7: Frozen Evidence vs Live State

When the user is mid-recovery, distinguish:
- **Frozen evidence**: logs / inspect output saved to `/tmp/xsky-k8s-service-debug/...` at time T1
- **Live state**: re-run the probe at time T2

When claiming "fixed", do a fresh live probe (HTTP, `pg_isready`, etc.) and quote the output with timestamp. See `verification-before-completion`.

## Stop Condition

Finish when you can answer all of:
1. Which layer is broken (1=node / 2=orchestration / 3=container / 4=app / 5=storage / 6=multi-victim)?
2. Which exact device / file / process / endpoint is the failing input?
3. What changed (storage backend / deploy / config / external dependency)?
4. Are there other victims of the same root cause?

If less than four are answered, keep walking.
