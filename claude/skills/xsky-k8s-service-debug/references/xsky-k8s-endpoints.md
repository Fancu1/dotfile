# XSKY K8s / Infra Endpoints

## Output Layout

Save all probe evidence under:

```
/tmp/xsky-k8s-service-debug/
  <service>/
    <YYYY-MM-DD-HHMM>/
      00-node-probe.txt        # parallel SSH connectivity / uptime / load / df
      01-pod-status.txt        # kubectl get pods, docker ps -a
      02-app-logs.txt          # docker logs / kubectl logs (filtered)
      03-storage.txt           # mount, iscsi sessions, dmesg XFS, iostat
      04-dmesg-window.txt      # dmesg -T grep for the suspected time window
      summary.md               # conclusion + evidence table + next step
```

## Known Clusters

### Primary RKE K8s cluster (`xsky-rd` namespace family)

| Field | Value |
|---|---|
| Type | Rancher RKE1 v1.26.4 |
| controlplane + etcd + worker | 10.252.80.13, 10.252.80.14, 10.252.80.15 |
| worker only | 10.16.83.25, 10.16.83.27 |
| SSH user | `root` |
| SSH key | `~/wpx/key111` |
| OS (controlplane) | CentOS 7 (kernel 3.10) — **EOL, watch out** |
| OS (workers) | Rocky Linux 9 (kernel 5.14) |
| Rancher UI | runs as `xsky-rancher` container on 10.252.80.15, ports 10080/10443 |
| Service URL convention | NodePort on controlplane IPs (look up via `kubectl get svc -n <ns>`) |

#### kubectl access (no admin kubeconfig on host)

`kubectl` binary is NOT on the host. Use the apiserver container:

```bash
docker exec kube-apiserver kubectl --kubeconfig=/etc/kubernetes/ssl/kubecfg-kube-node.yaml get pods -A
```

Available kubeconfigs on controlplane nodes (`/etc/kubernetes/ssl/`):

| kubeconfig | User | Can | Cannot |
|---|---|---|---|
| `kubecfg-kube-node.yaml` | system:node | get pods, describe pods, get nodes | list events, list ingress, list endpoints (Forbidden) |
| `kubecfg-kube-controller-manager.yaml` | system:kube-controller-manager | list events (cluster-wide) | get pods (Forbidden) |
| `kubecfg-kube-scheduler.yaml` | system:kube-scheduler | scheduling-related | most things Forbidden |
| `kubecfg-kube-apiserver-*.yaml` | apiserver internal | — | not useful for ops |

**Workaround for missing admin kubeconfig**: use node kubeconfig for pod inspection + controller-manager kubeconfig for events. Combine in the same probe.

Path inside apiserver container is the same (volume-mounted): `/etc/kubernetes/ssl/...`.

#### etcd

3-node etcd: `https://10.252.80.13:2379,https://10.252.80.14:2379,https://10.252.80.15:2379` (peer port 2380).

To talk to etcd directly (read-only stats):
```bash
docker exec etcd etcdctl --cacert=/etc/kubernetes/ssl/kube-ca.pem \
  --cert=/etc/kubernetes/ssl/kube-node.pem --key=/etc/kubernetes/ssl/kube-node-key.pem \
  --endpoints=https://10.252.80.13:2379 endpoint status -w table
```

### Standalone hosts

| Host | Purpose | OS | SSH key |
|---|---|---|---|
| 10.16.43.10 | Conan / JFrog Artifactory + Grafana / Loki | Rocky 9.1 | `~/.ssh/id_ed25519_xsky` |

Deployment shape: docker-compose, files in `/home/conan/docker-compose.yml` and `/home/conan-center/docker-compose.yml`.

`autoheal` container runs alongside as a health-driven restarter (willfarrell/autoheal image). **Note**: autoheal will infinite-loop-restart containers that fail because of underlying storage IO error — neutralize it (`docker stop autoheal`) before any recovery operation.

## Storage Backend

| Backend | Type | Portals | Initiator scope |
|---|---|---|---|
| XSKY iSCSI | iSCSI over TCP 3260 | 10.252.2.41, 10.252.2.42, 10.252.2.43 | Both K8s cluster and standalone hosts |

Common `iqn`s seen:
- `iqn.2020-01.com.xsky:jenkins-sds` — Jenkins data
- `iqn.2020-02.com.xsky:jenkins-sds` — Redis (despite the name)
- `iqn.2020-08.com.xsky:cicd-sds` — CICD
- `iqn.2020-10.com.xsky:cicd-sds`
- `iqn.2021-07.com.xsky:cicd` — Vault, MariaDB
- `iqn.2022-02.com.xsky:xsky-x8664` — Netbox
- `iqn.2023-03.com.xsky:xsky-x8664` — xsky-doc-qa
- `iqn.2023-06.com.xsky:xsky-x8664`
- `iqn.2026-03.com.xsky:xsky-x8664.iscsi.317` — Conan / Artifactory (on 10.16.43.10)

LUN-to-mountpoint mapping is per-host and dynamic (`/dev/sda`, `/dev/sds`, `/dev/sdu` ... can change across reboot / re-attach). Always derive via `iscsiadm -m session -P 3` + `lsblk` + `mount`.

## Infra Repository (Source of Truth for Deployments)

GitLab: `https://gitlab.xsky.com/infra/infrastructures`

Use this repo to look up:
- Helm values for each service
- Kustomize / manifest definitions
- Ingress / service definitions
- Backup / restore scripts (if any)

When uncertain about a service's deployment shape or storage, grep this repo before guessing. Clone read-only into `/tmp/xsky-k8s-service-debug/repos/infrastructures` if needed:

```bash
git clone --depth 1 https://gitlab.xsky.com/infra/infrastructures.git /tmp/xsky-k8s-service-debug/repos/infrastructures
```

## Credential Lookup

Script-level credentials (if needed) should follow the same order as `xsky-cicd-debug`:
1. Environment variables
2. `~/.config/xsky-k8s-service-debug/credentials.json`

Supported keys:
- `XSKY_GITLAB_USER` / `XSKY_GITLAB_TOKEN` — for cloning infra repo if not anonymous

Do not embed any secret in skill files.
