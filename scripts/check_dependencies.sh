#!/usr/bin/env bash
# Forwarder wrapper to organized script in scripts/setup/check_dependencies.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/setup/check_dependencies.sh" "$@"
