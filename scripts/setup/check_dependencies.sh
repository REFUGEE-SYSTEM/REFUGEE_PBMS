#!/usr/bin/env bash
# ==============================================================================
# check_dependencies.sh — Refugee Management Dependency & Port Verification
# ==============================================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "==> [check_dependencies] Inspecting system environment for refugee_management..."

# 1. System tool prerequisites
for cmd in docker git python3 curl lsof; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  [OK] Found command: $cmd"
  else
    echo "  [WARN] Missing command: $cmd"
  fi
done

# 2. Check proposed standalone ports
STANDALONE_PORTS=(8169 5543 6389 8150 8140 8180 9110 9111 8102 8104)
echo "==> [check_dependencies] Checking standalone port availability..."
CONFLICT=0
for port in "${STANDALONE_PORTS[@]}"; do
  if lsof -iTCP:"${port}" -sTCP:LISTEN -n -P >/dev/null 2>&1; then
    echo "  [CONFLICT] Port ${port} is currently IN USE by another process!"
    CONFLICT=1
  else
    echo "  [FREE] Port ${port} is available"
  fi
done

if [[ "$CONFLICT" -eq 1 ]]; then
  echo "==> Port conflicts detected. Please adjust .env before deployment."
  exit 1
else
  echo "==> All proposed ports are free."
fi
