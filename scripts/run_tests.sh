#!/usr/bin/env bash
# Run every test in tests/ with Python's built-in unittest.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHONPATH="$ROOT/app" exec python3 -m unittest discover -s tests -v "$@"
