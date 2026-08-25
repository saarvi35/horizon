#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-beleva-cluster}"

for command in docker kind kubectl helm; do
  command -v "$command" >/dev/null || { echo "Missing required command: $command" >&2; exit 1; }
done

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop and retry." >&2
  exit 1
fi

if ! kind get clusters | grep -Fxq "$cluster_name"; then
  kind create cluster --name "$cluster_name"
fi

kubectl config use-context "kind-$cluster_name" >/dev/null
kubectl get nodes
