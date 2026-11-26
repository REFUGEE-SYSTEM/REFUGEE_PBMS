#!/usr/bin/env bash
# Standalone Docker deployment helper
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
docker compose -f "$PROJECT_ROOT/deployment/docker-compose.yml" --env-file "$PROJECT_ROOT/.env" "$@"
