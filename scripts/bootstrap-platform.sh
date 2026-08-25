#!/usr/bin/env bash
set -euo pipefail

cluster_name="${1:-beleva-cluster}"
context="kind-$cluster_name"

bash "$(dirname "$0")/bootstrap-kind.sh" "$cluster_name"

if ! kubectl --context "$context" get namespace argocd >/dev/null 2>&1; then
  kubectl --context "$context" create namespace argocd
fi

if ! kubectl --context "$context" get deployment argocd-server -n argocd >/dev/null 2>&1; then
  kubectl --context "$context" apply -n argocd --server-side --force-conflicts \
    -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
fi

helm --kube-context "$context" repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
helm --kube-context "$context" repo update
helm --kube-context "$context" upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

bash "$(dirname "$0")/create-k8s-secret.sh" "$context" horizon .env

if kubectl --context "$context" get application horizon-stack -n argocd >/dev/null 2>&1; then
  echo "Warning: legacy Argo CD application 'horizon-stack' still exists." >&2
  echo "It manages the old Django-only chart. Review the migration notes before deleting it." >&2
fi

kubectl --context "$context" apply -f argocd/application.yaml

echo "Bootstrap complete. Run 'make status' to follow application health."
