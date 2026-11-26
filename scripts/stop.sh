#!/usr/bin/env bash
# Forwarder wrapper to organized script in scripts/shutdown/stop.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/shutdown/stop.sh" "$@"
