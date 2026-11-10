#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IN="${1:?uso: export_platforms.sh <master.mp4> [stem]}"
STEM="${2:-fitas-da-serra-ep01}"
python3 "$ROOT/scripts/vhs_pipeline.py" export -i "$IN" --stem "$STEM"
