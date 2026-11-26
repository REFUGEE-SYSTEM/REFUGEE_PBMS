#!/usr/bin/env bash
# Forwarder wrapper to organized script in scripts/validation/status.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/validation/status.sh" "$@"
