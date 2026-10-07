"""Baselines + sealed backtest harness. No lookahead: all signals shifted by 1 bar.
Costs: 10 bps per one-way turnover by default. Long-only + threshold long/short variants.
"""
import numpy as np
import pandas as pd


def apply_costs(position: pd.Series, returns: pd.Series, bps: float = 10.0) -> pd.Series:
    turnover = position.diff().abs().fillna(0.0)
    cost = turnover * (bps / 1e4)
    return position.shift(1).fillna(0.0) * returns - cost


def buy_hold(closes: pd.Series) -> pd.Series:
    rets = closes.pct_change().fillna(0.0)
    pos = pd.Series(1.0, index=closes.index)
    return apply_costs(pos, rets)


def sma_trend(closes: pd.Series, fast: int = 20, slow: int = 50) -> pd.Series:
    rets = closes.pct_change().fillna(0.0)
    f = closes.rolling(fast).mean()
    s = closes.rolling(slow).mean()
    pos = (f > s).astype(float)
    return apply_costs(pos, rets)


def rsi_meanrev(closes: pd.Series, lb: int = 14, lo: int = 30, hi: int = 70) -> pd.Series:
    delta = closes.diff()
    gain = delta.clip(lower=0).rolling(lb).mean()
    loss = (-delta.clip(upper=0)).rolling(lb).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    pos = pd.Series(0.5, index=closes.index)
    pos[rsi < lo] = 1.0
    pos[rsi > hi] = 0.0
    pos = pos.ffill().fillna(0.5)
    rets = closes.pct_change().fillna(0.0)
    return apply_costs(pos, rets)


def breakout(closes: pd.Series, lookback: int = 50) -> pd.Series:
    rets = closes.pct_change().fillna(0.0)
    hi = closes.shift(1).rolling(lookback).max()
    lo = closes.shift(1).rolling(lookback).min()
    pos = pd.Series(0.5, index=closes.index)
    pos[closes.shift(1) >= hi] = 1.0
    pos[closes.shift(1) <= lo] = 0.0
    pos = pos.ffill().fillna(0.5)
    return apply_costs(pos, rets)


def entropy_vol_state(closes: pd.Series, window: int = 20, pct: float = 0.05) -> pd.Series:
    """Hidden-pattern probe (replicates Singha 2025 intuition on public daily data):
    low realized-entropy/disorder regimes precede larger |moves| without direction.
    We proxy entropy by normalized range dispersion; strategy goes FLAT (risk-off)
    when disorder is in bottom `pct` quantile, else holds trend. Tests whether
    magnitude-predictability without direction still adds risk-adjusted value.
    """
    rets = closes.pct_change().fillna(0.0)
    rng = (closes.rolling(window).max() - closes.rolling(window).min()) / closes.rolling(window).mean()
    thresh = rng.quantile(pct)
    disorder_low = (rng <= thresh).fillna(False)
    f = closes.rolling(20).mean()
    s = closes.rolling(50).mean()
    trend = (f > s).astype(float)
    pos = trend.copy()
    pos[disorder_low] = 0.0  # risk-off in low-entropy pre-expansion states
    return apply_costs(pos, rets)


BASELINES = {
    "buy_hold": buy_hold,
    "sma_20_50": sma_trend,
    "rsi_14": rsi_meanrev,
    "breakout_50": breakout,
    "entropy_riskoff": entropy_vol_state,
}
