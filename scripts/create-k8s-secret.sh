#!/usr/bin/env bash
set -euo pipefail

context="${1:-kind-beleva-cluster}"
namespace="${2:-horizon}"
env_file="${3:-.env}"

if [[ ! -f "$env_file" ]]; then
  echo "Missing $env_file. Copy .env.example to .env and set real values first." >&2
  exit 1
fi

read_env_value() {
  local key="$1"
  local line value

  line="$(grep -E "^${key}=" "$env_file" | tail -n 1 || true)"
  value="${line#*=}"
  value="${value%$'\r'}"

  # .env values may be enclosed in single or double quotes. Only the secret
  # variables needed below are read, so values such as ALLOWED_HOSTS may safely
  # contain spaces without being executed as shell code.
  if [[ "$value" == \"*\" && "$value" == *\" ]]; then
    value="${value:1:${#value}-2}"
  elif [[ "$value" == \'*\' && "$value" == *\' ]]; then
    value="${value:1:${#value}-2}"
  fi
  printf '%s' "$value"
}

SECRET_KEY="$(read_env_value SECRET_KEY)"
DB_USER="$(read_env_value DB_USER)"
DB_PASSWORD="$(read_env_value DB_PASSWORD)"
MYSQL_ROOT_PASSWORD="$(read_env_value MYSQL_ROOT_PASSWORD)"

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
