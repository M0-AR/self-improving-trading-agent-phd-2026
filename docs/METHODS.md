# METHODS — exact protocol (so a stranger can redo it)

## Data (Exp-0 `experiments/verify_live.py`)
1. Fetch ladder, no keys: Stooq CSV → Binance-Vision klines (1,500d) → Coinbase candles → Yahoo chart (5y).
2. Keep CLOSED daily bars only. All signals use `.shift(1)`. Costs 10 bps × turnover.
3. Log every attempt in `results/data_report.json` (FAIL lines are data).
4. Assets realized 2026-10-07: BTC_binance 1500, ETH_binance 1500, BTC_coinbase 350, SPY_yahoo 1255.

## Metrics (`src/metrics.py`)
- Sharpe = sqrt(252)·mean/std of net returns. DD from equity peak. CAGR annualized.
- Bootstrap Sharpe CI (default 2000; 200/100 inside search for speed, 2000 for final tables).
- Deflated Sharpe PSR vs `trials` = number of baselines (multiple-testing correction).
- WFC = corr(IS-Sharpe, OOS-Sharpe) across the 27-point surface (Tinsley SSRN:6324079).

## Self-improving loop (`src/self_improving_loop.py`)
- Cycle 0: shared generic rubric (20,50, no filter) — the SHARP R(0).
- Each cycle: attribution = worst-20 days autocorrelation (whipsaw vs expansion);
  propose atomic 1-variable neighbors; promote iff `sharpe_ci_low` improves AND DD ≥ −15%.
- Walk-forward: 365d train / 90d test rolling; params frozen, scored on test slices only.
- Ablation: free-form multi-variable jumps are never proposed (SHARP-A2 collapse cited).

## What counts as success
GOAL JSON in `src/self_improving_loop.py`. Success and failure bands are pre-registered;
the loop cannot move the goalposts. Abstention ("gate held") is a valid, publishable outcome.
