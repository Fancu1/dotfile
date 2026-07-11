# Known Services Inventory

Service-to-location map for XSKY internal infra. Use this when a user says "X 挂了" to find the host(s) / pod(s) / volume(s) without guessing.

This is **not exhaustive** — always cross-check live state. When adding to this file, prefer evidence from `https://gitlab.xsky.com/infra/infrastructures` over memory.

## On the primary RKE K8s cluster (10.252.80.x)

| Service | Namespace | Pod / Workload | Node affinity | Storage (iSCSI iqn) | External port |
|---|---|---|---|---|---|
| Jenkins | xsky-rd | StatefulSet `jenkins-0` | nodeSelector `kubernetes.io/hostname=10-252-80-15` | `iqn.2020-01.com.xsky:jenkins-sds.iscsi.44` | NodePort 18091 → 8080 |
| Jenkins dev | xsky-rd | `jenkins-dev-0` | — | — | ClusterIP only |
| Sonarqube | xsky-rd | `sonarqube-0` | — | — | — |
| Weblate | xsky-rd | `weblate-0` | — | — | — |
| Metabase | xsky-rd | `metabase-*` | — | — | — |
| Redis | (check) | — | 10.252.80.15 | `iqn.2020-02.com.xsky:jenkins-sds.iscsi.115` (yes, name says jenkins-sds — historical naming, this is actually Redis) | — |
| MariaDB | (check) | — | 10.252.80.15 | `iqn.2021-07.com.xsky:cicd.iscsi.269` | — |
| Vault | (check) | — | 10.252.80.15 | `iqn.2021-07.com.xsky:cicd.iscsi.270` | — |
| Netbox | xsky-it | `netbox-0`(5 容器:netbox / netbox-worker / netbox-housekeeping / redis / redis-cache;redis 与主容器共挂 iscsi 卷) | 10.252.80.15 | `iqn.2022-02.com.xsky:xsky-x8664.iscsi.272` | — |
| xsky-doc-qa | — | — | 10.252.80.15 | `iqn.2023-03.com.xsky:xsky-x8664.iscsi.275` | — |
| PostgreSQL (xsky-infra) | xsky-infra | `postgres-0` | 10.252.80.14 | `iqn.2020-08.com.xsky:cicd-sds.iscsi.261` | 5432 |
| victoria-metrics | xsky-infra | `victoria-metrics-0` | 不固定:`is_major` nodeSelector 多节点可调度(2026-06-10 起在 10.16.83.25,之前在 .27) | `iqn.2023-06.com.xsky:xsky-x8664.iscsi.311`(xfs, portals 含 10.252.2.44) | NodePort 18428 → 8428(`/health` 探活) |
| cattle-cluster-agent | cattle-system | Deployment | — | — | — |
| Rancher (local) | host | `xsky-rancher` (docker on 10.252.80.15, not K8s pod) | 10.252.80.15 | hostPath | 10080 / 10443 |
| pypi-proxy | xsky-infra | StatefulSet `pypi-proxy` (nginx cache → `mirrors.cloud.tencent.com/pypi/`, image `harbor.xsky.com/infra/cache-server`) | nodeSelector `node.dev.xsky.com/is_major=true` | `iqn.2020-01.com.xsky:jenkins-sds.iscsi.43` → `/var/cache/nginx/pypi` (xfs, 10Gi) | via ingress `pypi.xsky.com` / `pypi.dev.xsky.com` |
| goproxy (athens) | xsky-infra | Deployment `goproxy` + github-vanity nginx sidecar | `is_major=true` | — | via ingress `goproxy.xsky.com` |
| gatus (拨测/状态页) | xsky-infra | 见 `k8s/manifests/ns-infra/gatus/` | — | — | `status.xsky.com`(API: `/api/v1/endpoints/statuses`,仅存最近 100 条结果) |

**入口公网路径(2026-06 实测)**: `pypi.xsky.com` → CNAME `dev.xsky.com` → **10.252.3.251 = keepalived VIP**(漂在 10.252.80.13/14/15/135/139/148,conf 见 infra 仓库 `k8s/keepalived.confd/`)→ ingress-nginx → ClusterIP svc。对未知 `*.xsky.com` 服务先 `dig`,落到 10.252.3.251 即 K8s ingress 服务。
**pypi-proxy 已知坑**: nginx `proxy_pass` 静态域名只在启动时解析;上游腾讯镜像走 EdgeOne CDN,IP 轮换后 pod 内 nginx 抱死 IP → 全站 504(connect timeout 75s 特征)。判别法:504 响应带 `X-Cache-Status` 头 = pod 自身 nginx 所发。

**Gotchas:**
- LUN device names (`/dev/sda`, `/dev/sds`, ...) are NOT stable across reboot or re-attach. Always resolve via `iscsiadm -m session` + `lsblk` + `mount`.
- **鬼设备模式(2026-06-10 victoria-metrics 案)**:iSCSI session 超时后自动重连会生成**新** sdX,旧设备变 `transport-offline` 留在 `iscsiadm -m session -P 3` 设备表里;kubelet plugin mount 仍指旧设备 → 容器 `ContainerCannotRun(128)` + `error while creating mount source path ... file exists`。判别:`cat /sys/block/<dev>/device/state`。
- **stale-AOF-fd 模式(2026-06-10 netbox 案)**:存储抖动后 fs 路径恢复,但长寿进程(redis 等)持有的旧 fd 永久 EIO。特征:`rdb_last_bgsave_status:ok`(新开文件可写)+ `aof_last_write_status:err`(旧 fd 死)→ redis MISCONF 拒写 → 依赖它的组件(netbox-worker rqworker)CrashLoop 而 fs 检查全正常。只需重启该容器。pod "Running/4-5 Ready" 也可能藏着这种病——按容器逐个看 restartCount。
- `iqn.2020-02.com.xsky:jenkins-sds` despite its name is NOT the Jenkins data — it's Redis. The Jenkins LUN is `iqn.2020-01.com.xsky:jenkins-sds` (note the `2020-01` vs `2020-02`).

## On standalone host 10.16.43.10

| Service | Container | Image | Storage | External port |
|---|---|---|---|---|
| JFrog Artifactory (Conan repo) | `artifactory` | `harbor.xsky.com/jfrog/artifactory-cpp-ce:7.111.x` | `/mnt/iscsi/conan/artifactory` (on `iqn.2026-03.com.xsky:xsky-x8664.iscsi.317`) | 3000 |
| Artifactory's PostgreSQL | `postgres-conan` | `harbor.xsky.com/jfrog/postgres:16.x` | `/mnt/iscsi/conan/postgres` (same iSCSI LUN) | 5432 |
| autoheal | `autoheal` | `willfarrell/autoheal` | — | — |
| Grafana | `grafana` | `grafana/grafana-enterprise` | local volume | 3100 (or check) |
| Loki | `loki` | `grafana/loki:3.x` | local volume | — |
| Local monitoring PG | `pgsql` | `postgres:16-alpine` | local volume | shares 5432 docker-proxy |

Compose files: `/home/conan/docker-compose.yml`, `/home/conan-center/docker-compose.yml`.

**Autoheal hazard**: when the underlying iSCSI volume goes into XFS shutdown state, autoheal will infinite-loop-restart `postgres-conan` and `artifactory` containers (each restart fails on the first IO operation). Always `docker stop autoheal` before any recovery operation involving these containers.

## Common iSCSI Portal Cluster

All XSKY iSCSI traffic from the above goes to **the same backend**:

- Portals: 10.252.2.41:3260, 10.252.2.42:3260, 10.252.2.43:3260
- A single backend-side incident (XSKY OSD down, network flap, controller restart) typically takes out **all** iSCSI-backed services simultaneously. **This is the #1 cross-service correlation signal**: if you find one victim with XFS / iSCSI errors, check every other iSCSI-using service in the same time window.

## Discovery: When a Service Is Not Listed Here

1. Grep the infra repo for the service name:
   ```bash
   git -C /tmp/xsky-k8s-service-debug/repos/infrastructures grep -l -i '<service>' || \
     (cd /tmp/xsky-k8s-service-debug/repos && git clone --depth 1 https://gitlab.xsky.com/infra/infrastructures.git && \
      git -C infrastructures grep -l -i '<service>')
   ```
2. Look at the K8s cluster for a matching pod:
   ```bash
   docker exec kube-apiserver kubectl --kubeconfig=/etc/kubernetes/ssl/kubecfg-kube-node.yaml \
     get pods -A 2>&1 | grep -i '<service>'
   ```
3. Look at all standalone hosts (the infra inventory should list them):
   ```bash
   for h in <list-from-ansible-or-helm-values>; do
     ssh ... root@$h "docker ps -a 2>/dev/null | grep -i '<service>'" &
   done; wait
   ```
4. If still missing, ask the user for the IP / namespace.

After locating a new service, **update this file** so the next probe is faster.
