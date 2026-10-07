"""Experiment 0: verify live data fetch + baselines on REAL public data.
Writes data/*.csv + results/baselines.csv + results/data_report.json.
Fails loudly if no real data (no synthetic fallback for prices).
"""
import os
import json
import pandas as pd
from src.data_live import load_universe
from src.baselines import BASELINES
from src.metrics import summarize

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)


def main():
    uni, attempts = load_universe()
    print("fetch:", attempts)
    if not uni:
        raise SystemExit("No live market data available. Check network.")
    report = {"attempts": attempts, "assets": {}}
    rows = []
    for name, df in uni.items():
        fp = f"data/{name}.csv"
        df.to_csv(fp)
        closes = df["close"]
        rets = closes.pct_change().fillna(0.0)
        report["assets"][name] = {
            "rows": len(df), "from": str(df.index.min()), "to": str(df.index.max()),
            "last_close": round(float(closes.iloc[-1]), 2),
        }
        for bname, fn in BASELINES.items():
            r = fn(closes).dropna()
            s = summarize(r, label=f"{name}:{bname}", trials=len(BASELINES))
            rows.append(s)
    pd.DataFrame(rows).to_csv("results/baselines.csv", index=False)
    with open("results/data_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(pd.DataFrame(rows).to_string(index=False))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if os.path.basename(os.getcwd()) == "experiments" else os.getcwd())
    main()
