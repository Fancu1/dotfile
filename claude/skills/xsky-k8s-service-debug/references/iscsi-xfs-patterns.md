# iSCSI / XFS Failure Patterns Seen on XSKY Infra

Curated from real incidents. Each pattern has a kernel signature, a symptom set, and a (read-only) verification.

---

## Pattern 1: XFS `force_shutdown(0x2)` — Log I/O Error

### Signature
```
XFS (sdX): xfs_do_force_shutdown(0x2) called from line 1238 of file fs/xfs/xfs_log.c.
XFS (sdX): Log I/O error (0x2) detected at xlog_ioend_work
XFS (sdX): Shutting down filesystem
XFS (sdX): Please unmount the filesystem and rectify the problem(s)
```

### What it means
The XFS journal couldn't write. To protect on-disk consistency, XFS stops all IO on this filesystem. The filesystem is **dead until unmount + remount**. No userspace process can do anything useful with files on this mount — every syscall returns `-EIO`.

### Symptoms upstream
- `ls <mountpoint>`: "Input/output error"
- `stat <mountpoint>`: "Input/output error"
- `xfs_info /dev/sdX`: "not a mounted XFS filesystem" (kernel disowns it)
- `df -h <mountpoint>`: "Input/output error"
- App-layer: any read/write returns IO error; PG `fsync` fails → PANIC → SIGSEGV (exit 139); Jenkins HTTP 500 + can't even load `oops.jelly`
- iostat shows 0 IO on the device (not stuck — totally bypassed)

### Verification (read-only)
```bash
# Did the fs get shut down?
dmesg -T | grep -E 'xfs_do_force_shutdown|Shutting down filesystem'

# Is the block device itself OK, or is the backend also broken?
dd if=/dev/sdX of=/dev/null bs=4K count=1 iflag=direct
# If this succeeds, backend recovered; only the fs needs remount.
# If this hangs / fails, backend is still broken — fixing fs won't help yet.
```

### Recovery shape (requires user authorization)
- `umount -l <mountpoint>` (lazy unmount tolerates the dead fs)
- For iSCSI volumes, full logout/login often needed: `iscsiadm -m node --logout && iscsiadm -m node --login`
- Re-mount triggers XFS log replay. Watch for `Starting recovery (logdev: internal)` → `Ending recovery (logdev: internal)`. If replay fails, `xfs_repair` may be needed (mutating; ask first).

---

## Pattern 2: Persistent SCSI parity errors with no XFS shutdown

### Signature
```
sd N:0:0:0: [sdX] Add. Sense: Scsi parity error
sd N:0:0:0: [sdX] timing out command, waited 180s
sd N:0:0:0: [sdX] FAILED Result: ... Sense Key: Aborted Command
XFS (sdX): metadata I/O error in "xfs_buf_iodone_callback_error" ... error 5
XFS (sdX): writeback error on sector ...
XFS (sdX): Failing async write on buffer block ... Retrying async write.
```
Note: **`Failing async write ... Retrying`** — XFS is retrying. Filesystem **has not** shut down. Yet.

### What it means
The SCSI command layer is intermittently failing. iSCSI portal is reachable (TCP 3260 open, ping fine), but the storage backend is taking >180s to respond or rejecting parity. App-level IO becomes very slow with sporadic errors but the filesystem stays up.

### Symptoms upstream
- App-layer transactions occasionally fail with "could not write" / connection timeouts
- High system load (`load_avg_15` can hit triple digits) — many processes piling up waiting on IO
- iostat shows huge `await` and `svctm` on the device
- D-state process count growing

### Verification (read-only)
```bash
# Is the kernel still actively erroring or has it calmed down?
dmesg -T | grep -E 'sd [0-9]+:.*parity|waited 180s' | tail -10
# Note the latest timestamp — if minutes ago, still flaky; if hours ago, may have self-healed.

# Current IO health
iostat -xy 1 5 | grep -E 'Device|<dev>'
# Look for await > 100ms, %util pegged at 100, or all-zeros (stuck).
```

### What to do
- This is a **storage-backend-side** issue (XSKY OSD slow, controller failover, network flap). The host can do little.
- Look at XSKY management console for the same time window.
- Wait for backend to stabilize, then re-evaluate. If XFS hasn't shut down, no remount needed.

---

## Pattern 3: kubelet stale plugin-level mount (in-tree iSCSI)

### Signature
- User deletes a K8s pod with an iSCSI PV
- New pod stuck in `ContainerCreating` indefinitely
- Pod events:
  ```
  Warning FailedMount: MountVolume.WaitForAttach failed for volume "X":
  mkdir /var/lib/kubelet/plugins/kubernetes.io/iscsi/iface-.../...-lun-0: file exists
  ```

### What it means
The in-tree iSCSI plugin (deprecated in K8s ≥ 1.27) doesn't unmount its `plugins/.../-lun-0` directory after pod deletion. If that mount is in XFS-shutdown state (Pattern 1), it can never be reused — but kubelet won't actively unmount it either. New pod's SetUp fails on `mkdir file exists`.

### Verification (read-only)
```bash
# Find the stuck plugin mount
mount | grep '/var/lib/kubelet/plugins/.*iscsi.*-lun-0'
# Can we stat it? (no = dead mount)
stat <that path> 2>&1
ls  <that path> 2>&1
# What pod-level mounts exist for this volume? (none = orphan)
mount | grep '/var/lib/kubelet/pods/.*iscsi/<volume-name>'
```

### Recovery shape (requires user authorization)
- `umount -l <stuck-path>` (`-l` is lazy, tolerates dead fs)
- kubelet will then succeed on the next SetUp retry (within ~30s)

### Permanent fix
- Upgrade to K8s ≥ 1.27 + migrate to CSI iSCSI driver (out-of-tree, has proper teardown)
- Or run a systemd-timer cleanup script (see SKILL.md P1 in the postmortem)

---

## Pattern 4: PostgreSQL crash from underlying IO error

### Signature (in `docker logs postgres-*`)
```
PANIC:  could not fsync file "pg_logical/replorigin_checkpoint.tmp": Input/output error
PANIC:  could not fdatasync file "000000010000...": Input/output error
FATAL:  could not open file "global/pg_filenode.map": Input/output error
LOG:    checkpointer process (PID 27) was terminated by signal 6: Aborted
PANIC:  could not open file "global/pg_control": Input/output error
```
Container exits with code **139** (SIGSEGV — postmaster aborts after checkpointer dies).

### What it means
Storage went bad while PG was writing. Last successful checkpoint is in the past; everything after is at risk.

### Restart behavior (when storage comes back)
- PG enters crash recovery automatically on next start
- Looks for last checkpoint in `pg_control`, replays WAL from there
- Expected good log lines on recovery:
  ```
  LOG:  database system was not properly shut down; automatic recovery in progress
  LOG:  redo starts at <LSN>
  LOG:  invalid record length at <LSN>: expected at least 24, got 0   <-- normal end-of-WAL signal
  LOG:  redo done at <LSN> system usage: ... elapsed: <small> s
  LOG:  database system is ready to accept connections
  ```
- Data loss: at most the unflushed in-flight transactions between the last successful checkpoint and the crash. Typically minutes of work.

### Verification (read-only, after storage is back)
- Storage must be remounted first (Pattern 1 recovery)
- Then `docker start <pg-container>` and read logs
- Confirm `ready to accept connections`
- `docker exec <pg> pg_isready -U <user>` from outside

### When it goes wrong
- `pg_control` itself corrupted → PG refuses to start with `PANIC: could not read checkpoint record`. Don't `pg_resetwal` without a backup. Stop and ask.
- WAL severely damaged → PG starts but data inconsistent. Look for PANIC during redo.

---

## Pattern 5: Application Pod Healthy, Service Dead (the "K8s liveness lies" pattern)

### Signature
- `kubectl get pod`: `1/1 Running 0 restarts`
- Process exists (`ps aux | grep java/python/...`)
- TCP port open (`ss -tlnp`)
- HTTP returns **5xx** for every request (not connection refused — actual 500/503 body)

### What it means
The liveness probe is **TCP-level** (or HTTP shallow), so K8s sees the port open and considers the pod healthy. But the application internally has hit a state it can't recover from (most commonly: the data volume gave it an IO error in mid-request and the app is now returning errors for everything).

### Verification (read-only)
```bash
# HTTP body, not just status code
docker exec <container> curl -sS -m 5 http://localhost:<port>/ | head -50

# Java specifically — look at thread state distribution and stack of one R-state thread
JPID=$(pgrep -f <app-name> | head -1)
ls /proc/$JPID/task | wc -l    # total threads
for t in /proc/$JPID/task/*/status; do awk '/^State:/ {print $2}' "$t"; done | sort | uniq -c

# Data volume access
docker exec <container> ls /<data-mount>/ 2>&1   # Look for "Input/output error"
docker exec <container> df -h /<data-mount> 2>&1
```

### Recovery
- Almost always Pattern 1 underneath. Fix the filesystem, the app self-heals on restart.

---

## Pattern 6: Git workspace corruption (Jenkins post-XFS-shutdown)

### Signature
Jenkins build fails on SCM checkout with:
```
fatal: .git/index: index file smaller than expected
```
or `git fsck` finds:
```
error: object file .git/objects/XX/YYYY... is empty
```

### What it means
When XFS shut down (Pattern 1), any file with dirty page cache that hadn't been fsynced was written as truncated / zero-byte on disk. Jenkins workspace files (`.git/index`, `.git/objects/*`, randomly any file) end up 0 bytes.

### Verification (read-only)
```bash
# Specifically the @script pipeline-loader workspaces
docker exec <jenkins> sh -c '
for d in /var/jenkins_home/workspace/*@script/*/; do
  idx="$d.git/index"
  [ -e "$idx" ] && printf "%10d  %s\n" "$(stat -c%s "$idx")" "$d"
done | sort -n | head -30'
# Any 0-byte index = corrupted workspace

# Deeper: count 0-byte git objects in a suspicious workspace
docker exec <jenkins> sh -c "find <workspace>/.git -size 0 -type f | wc -l"
```

### Recovery shape (requires user authorization)
- `mv` the corrupted workspace to `.broken-<date>` (safer than `rm -rf`)
- Jenkins will re-clone from remote on next build
- After verifying success, delete the backup
