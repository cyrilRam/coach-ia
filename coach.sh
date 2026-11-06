#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
PYTHON="${COACH_PYTHON:-.venv/bin/python}"

git pull --rebase --autostash
"$PYTHON" scripts/sync.py
"$PYTHON" scripts/build_dashboard.py --ouvrir
