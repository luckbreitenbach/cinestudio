#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/vhs_pipeline.py preview
echo "Previews em: $ROOT/preview/"
ls -lh preview/*.mp4 2>/dev/null || true
