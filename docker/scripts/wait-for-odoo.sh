#!/usr/bin/env bash
set -euo pipefail
host="$1"
max_retries=${2:-60}
delay=${3:-5}
for i in $(seq 1 "$max_retries"); do
  if curl -fs "http://$host/web/version" >/dev/null 2>&1; then
    echo "Odoo at $host is ready"
    exit 0
  fi
  echo "Waiting for Odoo at $host ($i/$max_retries)"
  sleep "$delay"
done
echo "Timeout waiting for Odoo at $host" >&2
exit 1
