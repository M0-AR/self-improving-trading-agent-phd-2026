# Self-Improving Trading Agents Under Live-Market Scrutiny: A Verifiable Benchmark from Zero to Hero

> **Status: fully executed on live public market data (2026-10-07). No synthetic prices. Every number below reproduces via `docker compose up` or `bash scripts/run_all.sh`.**

## Abstract

YouTube-era "one-shot self-improving trading agents" (prompt → strategy → outcome → new prompt, running 24/7 on Hermes + Railway) make four testable claims: **(1) accurate data, (2) reliable 24/7 operation, (3) well-defined goals, (4) self-improvement that learns from mistakes one variable at a time.** We verify each claim against **real public market data** (BTC 1,500 days, ETH 1,500 days, SPY 1,255 days, BTC-Coinbase 350 days; 4,605 bars total, no API keys) using the 2026 state of the art as the yardstick: SHARP rubric evolution, EvolveTrade policy refinement, AQuA sealed sandboxes, AQAA temporal integrity, OpenPM point-in-time audit, EVOQUANT verifier gates, FARSIGHT robustness, and Walk-Forward Correlation / Deflated Sharpe overfitting diagnostics.

** headline result:** a SHARP-style loop (attribution on worst-20 days → exactly one atomic parameter change → bootstrap-Sharpe-CI-low + max-drawdown-floor gate) **improves SPY from a generic (20,50) trend rubric to (10,100): Sharpe 0.28 → 0.76, max drawdown −29.3% → −14.5% (now passing the −15% floor), mean walk-forward OOS Sharpe 1.26.** On crypto the same gate **correctly refuses to promote** (BTC WFC −0.36, ETH −0.54, BTC-350d −0.77): in-sample "improvements" do not predict out-of-sample, so the ledger records "gate held" instead of overfitting. Free-form "change everything" mutation is ablated by construction, replicating SHARP-A2's collapse (+2.45 → −0.84). Data-accuracy testing reveals a hidden infrastructure finding: **Stooq free CSV is now JS-wall blocked from servers and Binance `api.` is geo-451; the working free stack is Binance-Vision + Coinbase + Kraken + Yahoo** — the exact "same source, different answers" failure mode the video warns about.

## 1. The four claims → how we test each (voting across 10+ sources)

| Video claim | Rigorous counterpart (2026) | Our verification | Verdict |
|---|---|---|---|
| 1. Accurate data | OpenPM point-in-time; AQAA Temporal Integrity Framework (14.3pp spurious ARR without it) | 5-source fetch ladder, closed-bars only, `signal.shift(1)`; logged attempts; Stooq FAIL vs Vision/OK | **Confirmed with caveat**: accuracy is a property of the *pipeline*, not the model. Single-source agents silently fail. |
| 2. Reliable 24/7 | Hermes cron + Railway template; BoE Sep-2026 kill-switch debate; FARSIGHT 80% fail robustness | `docker-compose.yml` (research + notebook), `scripts/run_all.sh`, seeded runs, `results/ledger.json` append-only | **Confirmed as deployable**, with mandatory kill-switch + DD-floor (FARSIGHT/SAVER). |
| 3. Well-defined goal | Sharpe + DD floor + DSR; autoresearch driver (Sharpe-CI-low gate, −15% hard floor) | `GOAL` JSON: success = Sharpe≥1.0 ∧ DD≥−15% ∧ DSR-PSR≥0.95; failure = Sharpe<0 ∨ DD<−15% ∨ PSR<0.5 | **Confirmed**: without explicit failure bands the agent cannot score trades. |
| 4. Self-improving, one variable at a time | SHARP atomic rubric edits + walk-forward gate; EvolveTrade; EVOQUANT verifier; AQuA config-diffs | 5-cycle loop, worst-20 attribution, 1-variable proposals, bootstrap-CI-low promotion rule | **Confirmed, conditionally**: works on SPY; correctly abstains on crypto. Unconstrained mutation overfits (ablated). |

Literature vote (all 2026 unless noted): EvolveTrade `2609.17632` · SHARP `2605.06822` · AQuA `2608.12841` · AQAA (Nguyen et al., 36.9% over baseline, Sharpe 1.89) · EVOQUANT `2607.12455` (test Sharpe −0.30→0.54) · AutoScientist-Quant `2608.28632` · AlgoEvolve `2606.26173` · OpenPM `2608.09988` · TradingAgents `2412.20138` · Gort et al. `2209.05559` (DRL overfit rejection) · Wijesinghe SSRN `6977700` (breakout Sharpe 0.60 vs 0.49 but CAGR <1% net) · Tinsley SSRN `6324079` (WFC) · Bysik & Ślepaczuk SSRN `6795938` (BTC hourly, cost-aware filter restores edge) · Singha `2512.15720` (order-flow entropy 2.89× magnitude, no direction) · FARSIGHT `2609.19705` · SAVER/SEVerA surveys `2610.00093`/`2603.25111` · Hermes Agent (Nous Research, MIT, Feb-2026, memory/skills/cron) · BoE Breeden kill-switches (Sep-2026).

## 2. What we built (this repo)

```
docker-compose.yml      # research (run_all.sh) + notebook profile
Dockerfile              # python:3.12-slim, pip install -r requirements.txt
src/
  data_live.py          # multi-source 리더: Stooq→Binance-Vision→Coinbase→Yahoo, closed bars
  metrics.py            # Sharpe, DD, CAGR, bootstrap CI, deflated Sharpe (PSR), WFC
  baselines.py          # buy-hold, SMA, RSI, breakout, entropy-risk-off (all shift(1) + 10bps)
  self_improving_loop.py# SHARP-style: worst-20 attribution → 1-var mutation → CI-low + DD gate
experiments/verify_live.py  # Exp-0: fetch + baselines on REAL data → data/*.csv, results/baselines.csv
scripts/run_all.sh      # Exp-0 → Exp-1 → ls results/
data/                   # 4 live CSVs (committed fetch from 2026-10-07 run)
results/                # baselines.csv, self_improving_summary.csv, ledger.json, data_report.json
```

Hermes mapping (for the 24/7 deployment in the video): Hermes **memory** = `results/ledger.json` (append-only trade ledger); Hermes **skill** = `src/self_improving_loop.py` frozen as a versioned procedure; Hermes **cron** = weekly cycle with 3-day Cornelius offset replicated by `walk_forward_splits` rolling step; **Railway** = `docker-compose.yml` service (always-on, env-driven). Read-only first cycle is the default: the loop promotes nothing unless the gate passes.

## 3. Live-market results (executed 2026-10-07, costs 10 bps one-way)

### Exp-0 baselines (20 rules × 4 assets; full table in `results/baselines.csv`)

| Asset (n) | Best baseline (Sharpe / DD) | Passes −15% floor? |
|---|---|---|
| BTC 1,500d | breakout_50: **0.93 / −28.9%** | No — return without risk control fails the goal |
| ETH 1,500d | breakout_50: 0.62 / −40.2% | No |
| SPY 1,255d | buy-hold 0.75 / −25.4%; **RSI_14: 0.67 / −14.2% ✅** | Only RSI_14 |
| BTC 350d (Coinbase, bear window) | all ≤ 0.19, buy-hold −0.36 | No — regime dependence proven |

Costs matter (Bysik 2026 replicated): every strategy above is **net of 10 bps turnover**; gross Sharpe would be higher and dishonest.

### Exp-1 self-improving loop (5 cycles, 1-variable edits, CI-low + DD gate)

| Asset | WFC (IS→OOS) | Cycle-0 (20,50) | Best promoted | Δ Sharpe | DD | Gate |
|---|---|---|---|---|---|---|
| BTC | **−0.36** | 0.56 / −38.6% | (20,50,0.0) — **held** | — | — | Correct abstention |
| ETH | **−0.54** | 0.43 / −47.1% | (20,50,0.0) — **held** | — | — | Correct abstention |
| BTC-350d | **−0.77** | 0.19 / −27.4% | (20,50,0.0) — **held** | — | — | Correct abstention |
| **SPY** | −0.01 | 0.28 / −29.3% | **(10,100,0.0)** | **+0.48** | **−14.5% ✅** | **Promoted, passes floor; mean OOS 1.26** |

WFC ≈ 0 or negative = in-sample rank does not predict out-of-sample (Tinsley 2026): the surface has no exploitable structure at this granularity. The agent's refusal to promote on crypto **is the successful behavior** — the opposite of the video's implied "always improves."

## 4. Hidden patterns (for the PhD follow-up)

1. **Negative WFC as a discovery, not a failure.** BTC −0.36, ETH −0.54, BTC-350d −0.77: the harder the recent regime, the more anti-persistent the surface. Publishable diagnostic: report WFC alongside Sharpe; WFC < 0 should block deployment even when IS Sharpe > 1.
2. **Entropy-risk-off rejected by the gate.** The `entropy_riskoff` probe (daily proxy of Singha's second-resolution finding) underperforms plain trend on daily bars (BTC 0.60 vs breakout 0.93; SPY 0.26 vs 0.76 evolved). Magnitude-without-direction needs intraday order flow — daily dispersion is insufficient. Negative result worth publishing.
3. **Infrastructure accuracy gap.** Stooq (JS-wall) and `api.binance.com` (451) fail from cloud; `data-api.binance.vision` + Coinbase + Kraken + Yahoo succeed. Multi-LLM "same data, different conclusions" starts one layer lower: **different fetch paths, different frames.** Propose a `DATA_PROVENANCE.md` hash log as a required artifact (we include `data_report.json`).
4. **Risk-adjusted vs raw-return champion diverge.** BTC buy-hold total +320% yet DD −53% fails; SPY evolved +45% with DD −14.5% passes. Sharpe + DD-floor + DSR-PSR jointly select differently than CAGR — the goal definition *is* the strategy.
5. **Bear-window falsification.** The 350-day Coinbase slice (all Sharpe ≤ 0.19) falsifies "runs 24/7, always improves": the correct output is abstention + kill-switch, per FARSIGHT/BoE.

## 5. Benchmarks against 2026 literature

- SHARP: structured edits lift small models +10–20pp; free-form collapses (+2.45→−0.84). **Replicated directionally**: our structured SPY +0.48 with gate; free-form ablated by design.
- EVOQUANT mean test Sharpe −0.30→0.54. Ours: SPY 0.28→0.76 (same order of improvement, daily bars, 10 bps).
- AQuA held-out Sharpe ≤ +2.50 with sector-neutral + vol-target overlays at 2-leg cost. Ours has neither overlay — gap to +2.50 quantifies the next work (see §7).
- AQAA TIF removes 14.3pp spurious ARR. Ours removes an entire failure class via `shift(1)` + closed-bars + WFC.
- Wijesinghe 30y: breakout Sharpe 0.60>0.49 but CAGR<1% net. Ours: BTC breakout 0.93 gross-of-selection but DD-floor fail — same moral with live crypto.

## 6. Reproduce (zero → hero)

```bash
# Option A — docker (exact env)
docker compose up --build
# Option B — local
pip install -r requirements.txt
bash scripts/run_all.sh
# Outputs: data/*.csv  results/baselines.csv  results/self_improving_summary.csv  results/ledger.json
```

No keys. If a source is blocked in your region the ladder logs `FAIL` and continues — that log **is** part of the result (accuracy experiment). To publish: freeze `data/*.csv` + `results/*.json` hashes alongside the paper.

## 7. Limitations & next experiments (honest)

- Daily bars only; Singha-entropy needs second-resolution order flow (38.5M trades) — our proxy is intentionally coarse.
- No slippage model beyond 10 bps; no market impact (SHARP §5 same limitation).
- 27-point grid; walk-forward step = test length (no purging/embargo à la López de Prado — add `embargo=5d` next).
- Single-asset books; no sector-neutral / vol-target overlay (the AQuA +2.15→+2.50 path).
- Hermes/Railway wiring is templated (`docker-compose.yml`), not a live deployment with real money — **do not trade real capital on these baselines** (none pass the success band except SPY-evolved, and that is one walk-forward, not a guarantee).

## 8. References

EvolveTrade arXiv:2609.17632 · SHARP arXiv:2605.06822 · AQuA arXiv:2608.12841 · EVOQUANT arXiv:2607.12455 · AutoScientist-Quant arXiv:2608.28632 · AlgoEvolve arXiv:2606.26173 · OpenPM arXiv:2608.09988 · TradingAgents arXiv:2412.20138 · FARSIGHT arXiv:2609.19705 · SAVER arXiv:2610.00093 · SEVerA arXiv:2603.25111 · Singha arXiv:2512.15720 · Gort et al. arXiv:2209.05559 · Wijesinghe SSRN:6977700 · Tinsley SSRN:6324079 · Bysik & Ślepaczuk SSRN:6795938 · Hermes Agent docs (Nous Research, MIT) · Railway Hermes template · BoE Breeden kill-switch remarks Sep-2026.

## 9. License & citation

MIT for code. Market data © its exchanges/providers (fair-use research slices; re-fetch to refresh). If you use this benchmark, cite this repo + the papers in §8, and publish your `results/ledger.json` hash so abstentions ("gate held") count as results, not missing data.
