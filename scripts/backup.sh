#!/usr/bin/env bash
# Forwarder wrapper to organized script in scripts/backup/backup.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/backup/backup.sh" "$@"
