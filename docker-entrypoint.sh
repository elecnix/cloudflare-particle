#!/bin/sh
set -e

# Default sleep interval (in hours)
SLEEP_HOURS="${SLEEP_HOURS:-24}"

while true; do
  echo "[Entrypoint] Running Cloudflare Access Policy Updater..."
  uv run python update_cf_access_policy.py
  echo "[Entrypoint] Sleeping for $SLEEP_HOURS hour(s)..."
  sleep $(expr $SLEEP_HOURS \* 3600)
done
