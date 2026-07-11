#!/usr/bin/env bash
# kubectl.sh — run kubectl on the RKE cluster via the apiserver container
#
# Usage:
#   kubectl.sh <ssh-key-path> <master-ip> [--role=node|controller|scheduler] <kubectl args...>
#
#   --role=node       (default) uses kubecfg-kube-node.yaml — can get/describe pods/nodes
#   --role=controller             kubecfg-kube-controller-manager.yaml — can list events
#   --role=scheduler              kubecfg-kube-scheduler.yaml
#
# Read-only by default; nothing prevents the caller from passing mutating verbs.
# Callers are responsible for staying read-only unless explicitly authorized.

set -u
KEY="${1:-}"; IP="${2:-}"; shift 2 || true

if [[ -z "$KEY" || -z "$IP" ]]; then
  echo "Usage: $0 <ssh-key-path> <master-ip> [--role=node|controller|scheduler] <kubectl args>" >&2
  echo "Examples:" >&2
  echo "  $0 ~/wpx/key111 10.252.80.15 get pods -A" >&2
  echo "  $0 ~/wpx/key111 10.252.80.15 --role=controller get events -A --field-selector type=Warning --sort-by=.lastTimestamp" >&2
  exit 2
fi

ROLE="node"
if [[ "${1:-}" == --role=* ]]; then
  ROLE="${1#--role=}"; shift
fi

case "$ROLE" in
  node)       CONF=/etc/kubernetes/ssl/kubecfg-kube-node.yaml ;;
  controller) CONF=/etc/kubernetes/ssl/kubecfg-kube-controller-manager.yaml ;;
  scheduler)  CONF=/etc/kubernetes/ssl/kubecfg-kube-scheduler.yaml ;;
  *) echo "Unknown role: $ROLE" >&2; exit 2 ;;
esac

if [[ $# -lt 1 ]]; then
  echo "No kubectl args given." >&2
  exit 2
fi

SSH_OPTS=(-i "$KEY" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null \
          -o ConnectTimeout=5 -o LogLevel=ERROR)

# Quote each kubectl arg for the remote shell.
printf -v ARGS '%q ' "$@"

timeout 30 ssh "${SSH_OPTS[@]}" "root@$IP" \
  "docker exec kube-apiserver kubectl --kubeconfig=$CONF $ARGS" 2>&1
