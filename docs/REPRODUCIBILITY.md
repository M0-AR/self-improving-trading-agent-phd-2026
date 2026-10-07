# REPRODUCIBILITY

- Python 3.12, pinned in `requirements.txt`. Seeds: 42 (bootstrap), deterministic grids.
- `docker compose up --build` reproduces `data/` + `results/` from scratch (network needed).
- To freeze a publication slice: `sha256sum data/*.csv results/*.json > results/SHA256SUMS`.
- Network matrix on 2026-10-07 (Frankfurt cloud): Stooq JS-wall FAIL, api.binance.com 451 FAIL,
  data-api.binance.vision OK, Coinbase OK, Kraken OK, Yahoo OK. Re-run to get your region's matrix.
- Known nondeterminism: bootstrap CI ±0.02 across seeds; WFC ±0.03. Conclusions stable (SPY promotes, crypto holds).
