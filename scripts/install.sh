#!/usr/bin/env bash
# Forwarder wrapper to organized script in scripts/setup/install.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/setup/install.sh" "$@"
