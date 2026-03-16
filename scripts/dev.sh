#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Missing virtualenv at $ROOT_DIR/.venv"
  echo "Create it with: python3.11 -m venv .venv"
  exit 1
fi

source ".venv/bin/activate"
python -m app.main
