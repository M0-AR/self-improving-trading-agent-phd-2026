#!/usr/bin/env bash
set -euo pipefail
echo "[1/3] verifying live market data fetch..."
python3 experiments/verify_live.py
echo "[2/3] running baselines + self-improving loop (SHARP-style)..."
python3 src/self_improving_loop.py
echo "[3/3] done. See results/ + README.md"
ls -lh results/ data/
