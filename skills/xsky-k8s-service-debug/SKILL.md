---
name: xsky-k8s-service-debug
description: Use when diagnosing XSKY infrastructure services (Jenkins, Artifactory/Conan, PostgreSQL, Vault, Netbox, Rancher, Grafana/Loki, victoria-metrics, etc.) running on XSKY internal K8s clusters or standalone Docker hosts. Triggers include service down/unhealthy, pod CrashLoopBackOff, container Exited (139/143/137), HTTP 5xx, application-layer hang, iSCSI/XFS I/O errors, kubelet mount stuck, "Jenkins / Conan / xxx 挂了 / 异常 / 不能用", or any K8s-side runtime issue on XSKY infra. Read-only by default — does NOT mutate clusters, pods, mounts, storage, or containers unless the user explicitly authorizes a specific step.
---

# XSKY K8s / Infra Service Debug

## Overview
Use this skill to localize service failures on XSKY internal infra with a fixed evidence chain: node connectivity → cluster topology → pod / container state → application layer → storage stack (mount, iSCSI, XFS, kernel) → cross-service correlation. Default scope is **diagnosis only**. Do not stop, restart, delete, umount, mount, login/logout, kill, or modify anything unless the user has explicitly authorized the specific action.

This is the companion to `xsky-cicd-debug`. CI/CD debug is for "why did the Jenkins build fail"; this skill is for "why is the Jenkins service itself broken" (and the same for any other infra service).

## Hard Rules

1. **Read-only by default.** Never run `kubectl delete`, `kubectl apply`, `kubectl edit`, `docker stop/start/restart/rm`, `umount`, `mount`, `iscsiadm --logout/--login`, `systemctl restart`, `kill`, `rm`, or any other state-changing command unless the user has explicitly asked for that exact step. When in doubt, ask.
2. **Don't load full logs into context.** Save raw output to `/tmp/xsky-k8s-service-debug/<service>/<timestamp>/` and grep/awk the saved file. Especially: `docker logs` of a noisy container, `dmesg` on a long-running host, `journalctl` without filters.
3. **Parallelize node probing.** When given multiple IPs, SSH them in parallel for connectivity + uptime + load + disk + mem in the first round. Don't go node-by-node.
4. **Treat application-layer "Running" as observation, not health.** K8s `pod Running` and Docker `Up` only mean the supervisor sees the process. Always verify the app responds at its real endpoint (HTTP, pg_isready, redis-cli ping, etc.) before claiming health.
5. **Don't stop at the first error.** Walk the stack: app HTTP error → app logs → process state → data volume access → mount state → block device → iSCSI session → kernel dmesg → storage backend. Name the deepest concrete cause.
6. **Cross-service correlation.** When you find an iSCSI/storage/network root cause, **immediately** check other services on the same backend / same node / same time window. The same root cause usually has multiple victims (today's example: Jenkins on `sds` + Conan on `sda` both broken by the same XSKY iSCSI window).
7. **Distinguish deployment shape early.** XSKY infra mixes:
   - **RKE K8s pods** (Jenkins, postgres, vault, netbox, redis, weblate, etc. on 10.252.80.x cluster)
   - **Standalone docker-compose hosts** (Conan/Artifactory on 10.16.43.10; misc service hosts)
   - **systemd services** on bare hosts
   Each has a different `kubectl get` / `docker ps` / `systemctl status` entry point. Identify the shape in the first round.
8. **Output order:** conclusion → evidence (with timestamps + file paths) → ruled-out hypotheses → next-step recommendation. Always include the **timestamp of every key event** in the evidence section — correlation across services depends on it.
9. **Preserve evidence when you must act.** If the user authorizes a destructive step (umount, delete pod, rm corrupted workspace), prefer `mv` to `.broken-<date>` over `rm -rf`. Only delete the backup after success is verified.
10. **Never read whole files (especially `/var/log/messages`, `journalctl`, `dmesg`) blindly.** Always combine with `grep -E`, `awk '/ts/,EOF'`, `tail -N`, or `--since`.

## When To Use

- User says "Jenkins / Conan / Rancher / Vault / Netbox / Artifactory / postgres / redis ... 挂了 / 不能用 / 异常 / 报错"
- User pastes a K8s pod that's CrashLoopBackOff / ImagePullBackOff / Pending
- User pastes a docker container that's Exited (139 / 143 / 137 / 1)
- HTTP 5xx / 503 / 502 / 504 from an internal service
- Storage symptoms: I/O error, slow IO, mount stuck, "no space", iSCSI disconnect
- Suspected kernel-level issue: dmesg full of XFS / SCSI / OOM, kernel panic suspected
- "Why is X service slow to start"
- Service was working yesterday, broken today — diff/compare mode
- User gives an IP and says "看看这台机器怎么了"

## Workflow

### 0) Capture The Scope

Before any probe, capture:
1. Service name + reported symptom (HTTP code? container exit code? CrashLoop reason? slow?)
2. Approximate start time of the issue (用户什么时候发现的？现在还在持续吗？)
3. Recent changes (deploy / upgrade / network maintenance / storage maintenance / OS patch)
4. Save all subsequent raw outputs under `/tmp/xsky-k8s-service-debug/<service>/<date>-<time>/`

If user only said "X 挂了" with no other context, proceed with the probe and infer scope from evidence.

### 1) Resolve The Cluster / Host

Use `references/known-services.md` and `references/xsky-k8s-endpoints.md` to map service → host(s) → SSH key. If the service is unknown:
1. Ask user for the IP and SSH key.
2. Optionally check the infra repo `https://gitlab.xsky.com/infra/infrastructures` for declarative deployment definitions (helm values, kustomize manifests, ansible inventories).

### 2) Probe Node Health (Parallel)

For every relevant node, in a single parallel SSH burst, collect:
- `hostname`, `uptime`, `date`
- `free -h`, `df -hT` (exclude tmpfs/overlay), `load average` (15min)
- `last reboot | head -5` — recent reboots often correlate with the failure window

**Red flags out of this round:**
- Unexpected reboot in the last 24h (especially if other long-uptime peers are fine)
- 15-min load >> CPU count (signals stuck-IO process pileup, not CPU work)
- Disk usage > 90% on `/`, `/var`, or any data mount
- Available memory near 0 with swap heavy
- Any node unreachable while peers are reachable

### 3) Identify Deployment Shape

For each node where the service is suspected:
- **K8s pod?** Look for `kubelet`, `containerd`, `dockerd`, and `/etc/kubernetes/` directory. If present, use `scripts/kubectl_via_rke.sh` or the equivalent inline command (see `references/xsky-k8s-endpoints.md` for the `docker exec kube-apiserver kubectl ...` pattern).
- **Standalone docker-compose?** `docker ps -a`, then find the compose file via `find /home /opt /srv -maxdepth 4 -name 'docker-compose*.yml'`.
- **systemd service?** `systemctl status <name>`.

### 4) Pod / Container State

Always look at the **full** state, not just the green ones:
- `kubectl get pods -A | grep -vE 'Running|Completed'` — find CrashLoop / Pending / Error / Init
- `docker ps -a` — find Exited containers (which `docker ps` alone hides)
- `kubectl describe pod <name>` — look at the **Events** section last (with admin or controller-manager kubeconfig — `system:node` kubeconfig cannot list events)
- `docker inspect <container> --format 'ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}} StartedAt={{.State.StartedAt}} FinishedAt={{.State.FinishedAt}}'`

**Exit code map** (the most common ones for infra services):
| Code | Meaning |
|---|---|
| 0 | Clean exit |
| 1 | Application error (usually shows up in container logs) |
| 137 | SIGKILL (OOM, or `docker kill`) — check `OOMKilled` |
| 139 | SIGSEGV — segfault (often from underlying IO error, e.g. PostgreSQL on broken disk) |
| 143 | SIGTERM — graceful kill by orchestrator (e.g. healthcheck failure + docker policy) |
| 255 | Java often returns this on fatal init error |

### 5) Application Layer Verification

A container being "Up" is not enough. Always poke the app:
- HTTP service: `curl -sS -m 5 -o /dev/null -w '%{http_code} %{time_total}s\n' http://<endpoint>/` from inside the container (`docker exec ...`) and from the host network
- PostgreSQL: `docker exec <pg> pg_isready -U <user>`
- Redis: `docker exec <r> redis-cli ping`
- Always look at the **JVM/process tree** inside the container, not just the supervisor PID. For tini-fronted containers, the real workload is `pgrep -P <tini-pid>` or `pgrep -f <app-name>`.
- For Java apps stuck mid-startup: `/proc/<pid>/status` shows thread count + state distribution. **919 threads all `S` (sleeping) with low CPU = waiting on network IO, not CPU bound** — this was today's Jenkins case.

### 6) Storage Stack Walk

When the application layer reports IO error, walk down:

```
app log "Input/output error"
  → mount table:  mount | grep <mountpoint>
  → block device exists?  ls -la /dev/<dev>
  → device readable?  dd if=/dev/<dev> of=/dev/null bs=4K count=1 iflag=direct
  → mountpoint readable?  ls <mountpoint> 2>&1   (may show "Input/output error" even if device is fine)
  → XFS state:  dmesg -T | grep -E "XFS \($dev\)"  → look for "xfs_do_force_shutdown", "Log I/O error", "metadata I/O error"
  → iSCSI session:  iscsiadm -m session
  → iSCSI portal reachable:  for p in 10.252.2.41 10.252.2.42 10.252.2.43; do timeout 3 bash -c "</dev/tcp/$p/3260" && echo "$p OPEN" || echo "$p CLOSED"; done
  → IO stats:  iostat -xy 1 5
  → device error count:  cat /sys/block/<dev>/device/ioerr_cnt
  → kernel events around the suspected timestamp
```

See `references/iscsi-xfs-patterns.md` for the patterns seen so far (force_shutdown 0x2, stale plugin mount, etc.).

### 7) Cross-Service Correlation

When a root cause is identified, **always check other services that share** any of:
- Same iSCSI portal / target / backend
- Same node
- Same time window (within ±30 min)
- Same upstream dependency (DNS, auth, gitlab, ldap, ...)

Use `references/known-services.md` to enumerate candidate victims.

### 8) Frozen-In-Time vs Live State

When using saved evidence (`/tmp/xsky-k8s-service-debug/...`), label it with timestamps. When the user is in the middle of a recovery, recheck live state before claiming "fixed" — `verification-before-completion`-style: run the actual health probe (HTTP, pg_isready, etc.) and quote its output.

## Diagnosis Standard

Don't conclude until you can answer all of:
1. Which layer is actually broken? (network / node OS / storage backend / file system / orchestration / application / dependency)
2. Which exact resource / device / file is the failing input? (e.g. `/dev/sds`, `iqn.2020-01.com.xsky:jenkins-sds`, `pg_control`, `oops.jelly`)
3. What changed? (storage backend event / deploy / config / external system / OS upgrade)
4. Are there other victims of the same root cause?

For multi-victim cases also answer:
5. Why didn't existing monitoring catch this earlier?

## Output Format

```
## Conclusion
<one-line root cause>

## Evidence
| Time (CST) | Source | Signal |
|---|---|---|
| 04:28:11 | dmesg on 10.252.80.15 | XFS (sds): xfs_do_force_shutdown(0x2) |
| 04:30:59 | dmesg on 10.16.43.10 | XFS (sda): Log I/O error → Shutting down filesystem |
| ... | ... | ... |

## Ruled out
- Hypothesis A: <evidence why not>
- Hypothesis B: <evidence why not>

## Suggested next step (read-only by default)
- <concrete command, with risk note if it's mutating>
```

## Quick Commands

See `references/xsky-k8s-endpoints.md` for full credential / IP map. Common patterns:

```bash
# Parallel connectivity probe to N nodes
for ip in <IP1> <IP2> ...; do
  (timeout 8 ssh -i <KEY> -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 -o LogLevel=ERROR root@$ip \
    "hostname; uptime; date" 2>&1 | sed "s/^/[$ip] /") &
done; wait

# kubectl via RKE apiserver container (no admin kubeconfig on the host)
KUBE='docker exec kube-apiserver kubectl --kubeconfig=/etc/kubernetes/ssl/kubecfg-kube-node.yaml'
# node kubeconfig: can get pods, cannot list events
# controller-manager kubeconfig: can list events, cannot get pods
# scheduler kubeconfig: similar limitations
# admin kubeconfig: not deployed by default — see references/xsky-k8s-endpoints.md

# Cross-host correlation: same XFS shutdown signal
ssh root@<host> 'dmesg -T | grep -E "xfs_do_force_shutdown|Log I/O error|Shutting down filesystem"'

# Find compose / systemd shape on an unknown infra host
ssh root@<host> '
  ls /etc/kubernetes/ 2>/dev/null  # K8s?
  docker ps -a 2>/dev/null | head
  find /home /opt /srv -maxdepth 4 -name "docker-compose*.yml" 2>/dev/null
  systemctl list-units --type=service --state=running 2>/dev/null | grep -iE "<service>"
'
```

## Common Mistakes (Anti-patterns)

- Reading full `dmesg` / `journalctl` / `docker logs` without grep — wastes context, hides the signal.
- Trusting `kubectl get pod` showing `1/1 Running` as "service is fine." (today's Jenkins: HTTP 500 for hours while pod said Running.)
- Treating exit code 0 / SIGTERM as "graceful shutdown" without checking what triggered it (e.g. healthcheck failure due to upstream IO error).
- Running mutating commands (`umount`, `docker stop`, `kubectl delete`) without explicit user authorization for that specific step.
- Fixing only the obvious victim and missing other services on the same root cause (today: didn't immediately check Conan until user asked).
- Using `system:node` or `system:kube-controller-manager` kubeconfig and getting `Forbidden` errors, then assuming the cluster is broken (it's just permissions — try a different kubeconfig).
- Assuming `iSCSI portal reachable + TCP open = storage healthy`. SCSI command-layer failures are invisible at TCP level.
- Trying to repair an XFS shutdown filesystem with `mount -o remount,rw` (won't work; must umount + re-mount).
- Trying to write to a 0-byte `pg_control` (file system has shut down; need to remount first, not pg_resetwal first).
- Assuming a `0-byte .git/index` can be fixed with `git reset` — usually objects are also corrupted (today's tag-fetcher case).

## References
- `references/xsky-k8s-endpoints.md` — known clusters, SSH keys, kubeconfig paths, output layout
- `references/known-services.md` — infra service inventory (where each service lives, which iSCSI LUN, which port, which DB)
- `references/diagnosis-chain.md` — detailed walkthrough of the full diagnosis chain with example outputs
- `references/iscsi-xfs-patterns.md` — the iSCSI / XFS failure modes seen so far, with the exact kernel signatures
- `references/grep-patterns.md` — useful grep / awk patterns for sifting logs

## Companion Skill
- `xsky-cicd-debug` — for "why did the Jenkins build fail" (different scope: business pipeline / code logic / git topology). If the Jenkins job is broken because the **Jenkins service itself** is broken, use this skill first; once Jenkins is back, switch to `xsky-cicd-debug`.
