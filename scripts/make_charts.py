"""Generate docs charts from REAL data/results. No synthetic values."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("docs/img", exist_ok=True)
os.makedirs("assets", exist_ok=True)

# 1. Equity curves: SPY buy-hold vs evolved (10,100) vs BTC breakout, from real CSVs
from src.baselines import apply_costs

def sma_pos(closes, fast, slow):
    f = closes.rolling(fast).mean(); s = closes.rolling(slow).mean()
    return (f > s).astype(float)

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=False)
for ax, fname, title, cfg in [
    (axes[0], "data/SPY_yahoo.csv", "SPY — buy-hold vs evolved (10,100) [real 1,255d]", [(None, "buy-hold"), ((10, 100), "evolved 10/100")]),
    (axes[1], "data/BTC_binance.csv", "BTC — buy-hold vs breakout_50 [real 1,500d]", [(None, "buy-hold"), ("breakout", "breakout_50")]),
]:
    df = pd.read_csv(fname, parse_dates=["Date"], index_col="Date").sort_index()
    closes = df["close"]
    rets = closes.pct_change().fillna(0.0)
    if "SPY" in fname:
        eq_bh = (10000 * (1 + apply_costs(pd.Series(1.0, index=closes.index), rets)).cumprod())
        eq_ev = (10000 * (1 + apply_costs(sma_pos(closes, 10, 100), rets)).cumprod())
        ax.plot(eq_bh.index, eq_bh.values, label="buy-hold")
        ax.plot(eq_ev.index, eq_ev.values, label="evolved (10,100)")
    else:
        eq_bh = (10000 * (1 + apply_costs(pd.Series(1.0, index=closes.index), rets)).cumprod())
        hi = closes.shift(1).rolling(50).max(); lo = closes.shift(1).rolling(50).min()
        pos = pd.Series(0.5, index=closes.index)
        pos[closes.shift(1) >= hi] = 1.0; pos[closes.shift(1) <= lo] = 0.0
        pos = pos.ffill().fillna(0.5)
        eq_bo = (10000 * (1 + apply_costs(pos, rets)).cumprod())
        ax.plot(eq_bh.index, eq_bh.values, label="buy-hold")
        ax.plot(eq_bo.index, eq_bo.values, label="breakout_50")
    ax.set_title(title); ax.legend(); ax.set_ylabel("$ (from $10k)")
    ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("docs/img/equity_real.png", dpi=110); print("equity_real.png OK")

# 2. Sharpe comparison bar from results/baselines.csv
b = pd.read_csv("results/baselines.csv")
b["short"] = b["label"].str.split(":").str[1]
pivot = b[b["label"].str.contains("BTC_binance|SPY_yahoo")].copy()
fig2, ax2 = plt.subplots(figsize=(10, 4))
x = range(len(pivot))
ax2.bar(x, pivot["sharpe"].values)
ax2.set_xticks(list(x)); ax2.set_xticklabels(pivot["label"].values, rotation=30, ha="right", fontsize=8)
ax2.set_title("Net Sharpe (10 bps costs) — real data baselines")
ax2.grid(axis="y", alpha=0.3)
fig2.tight_layout(); fig2.savefig("docs/img/sharpe_real.png", dpi=110); print("sharpe_real.png OK")

# 3. WFC + gate outcome from self_improving_summary.csv
s = pd.read_csv("results/self_improving_summary.csv")
fig3, ax3 = plt.subplots(figsize=(8, 3.5))
ax3.bar(s["asset"], s["wfc"].values)
ax3.axhline(0, color="black", linewidth=1)
ax3.set_title("Walk-Forward Correlation (IS→OOS): ~0/negative = no exploitable surface")
ax3.set_ylabel("WFC"); ax3.grid(axis="y", alpha=0.3)
fig3.tight_layout(); fig3.savefig("docs/img/wfc_real.png", dpi=110); print("wfc_real.png OK")
print("ALL_CHARTS_OK")
