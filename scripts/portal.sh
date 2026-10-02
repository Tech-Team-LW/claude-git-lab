#!/usr/bin/env bash
# Run the DevOps Team Portal from anywhere: ./scripts/portal.sh team list
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHONPATH="$ROOT/app" exec python3 -m devops_portal "$@"
