#!/usr/bin/env bash
# Set up a virtual environment and run the full pipeline from scratch.
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
python -m wigan_crime.run "$@"
