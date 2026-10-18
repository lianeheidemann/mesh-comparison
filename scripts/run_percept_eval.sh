#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m meshcomparison.perceptual --gt data/samples/gt.stl --rm data/samples/mod.stl --out output "$@"
