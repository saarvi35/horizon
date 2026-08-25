#!/usr/bin/env bash
set -euo pipefail

context="${1:-kind-beleva-cluster}"
namespace="${2:-horizon}"
env_file="${3:-.env}"

if [[ ! -f "$env_file" ]]; then
  echo "Missing $env_file. Copy .env.example to .env and set real values first." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$env_file"
set +a

: "${SECRET_KEY:?SECRET_KEY is required in $env_file}"
: "${DB_USER:?DB_USER is required in $env_file}"
: "${DB_PASSWORD:?DB_PASSWORD is required in $env_file}"

db_root_password="${MYSQL_ROOT_PASSWORD:-$DB_PASSWORD}"

kubectl --context "$context" create namespace "$namespace" --dry-run=client -o yaml | kubectl --context "$context" apply -f -
kubectl --context "$context" -n "$namespace" create secret generic beleva-secret \
  --from-literal=SECRET_KEY="$SECRET_KEY" \
  --from-literal=DB_USER="$DB_USER" \
  --from-literal=DB_PASSWORD="$DB_PASSWORD" \
  --from-literal=MYSQL_ROOT_PASSWORD="$db_root_password" \
  --dry-run=client -o yaml | kubectl --context "$context" apply -f -

echo "Updated $namespace/beleva-secret from $env_file."
