#!/usr/bin/env bash
# End-to-end test on fake data: copies the pipeline to a temp folder, builds fake
# inputs with the real file layouts, then runs every stage except download.
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
cp -r "$HERE/wigan_crime" "$TMP/"
mkdir -p "$TMP/outputs" "$TMP/models"
python3 "$HERE/tests/make_fake_data.py" "$TMP"
cd "$TMP"
python3 -m wigan_crime.run --skip-download
ls outputs/charts
echo "Test passed. Output in $TMP"
