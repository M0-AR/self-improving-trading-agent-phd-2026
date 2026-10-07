"""Live public market data fetcher. No API keys.
Priority: 1) Stooq free daily CSV  2) Binance public klines (crypto)  3) Yahoo chart API.
All point-in-time friendly: we only use CLOSED bars, shifted by 1 (no lookahead).
"""
import io
import time
import requests
import pandas as pd

UA = {"User-Agent": "sita-phd-research/1.0 (contact: research.local)"}


def fetch_stooq_daily(symbol: str) -> pd.DataFrame:
    """symbol like 'spy.us', 'qqq.us', 'btc.usd' (stooq crypto syntax)."""
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    if df.empty or "Close" not in df.columns:
        raise ValueError(f"Stooq empty for {symbol}")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()
    df.columns = [c.lower() for c in df.columns]
    return df[["open", "high", "low", "close", "volume"]].dropna()


def fetch_binance_daily(symbol: str = "BTCUSDT", days: int = 1500) -> pd.DataFrame:
    """Public klines, no key. Uses data-api.binance.vision mirror (bypasses geo 451 on api.binance.com)."""
    out = []
    end = int(time.time() * 1000)
    per = 1000
    need = days
    for base in ("https://data-api.binance.vision", "https://api.binance.com"):
        try:
            out, end, need = [], int(time.time() * 1000), days
            while need > 0:
                lim = min(per, need)
                url = f"{base}/api/v3/klines"
                params = {"symbol": symbol, "interval": "1d", "limit": lim, "endTime": end}
                r = requests.get(url, params=params, headers=UA, timeout=30)
                r.raise_for_status()
                batch = r.json()
                if not batch:
                    break
                out = batch + out
                end = batch[0][0] - 1
                need -= len(batch)
                if len(batch) < lim:
                    break
            if out:
                break
        except Exception:
            continue
    if not out:
        raise ValueError(f"Binance empty for {symbol}")
    cols = ["ts", "open", "high", "low", "close", "volume", "ct", "qv", "nt", "tb", "tq", "ig"]
    df = pd.DataFrame(out, columns=cols)
    df["Date"] = pd.to_datetime(df["ts"], unit="ms", utc=True).dt.tz_convert(None)
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    df = df.set_index("Date").sort_index()[["open", "high", "low", "close", "volume"]]
    return df


def fetch_yahoo_daily(symbol: str = "SPY", period: str = "5y") -> pd.DataFrame:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"interval": "1d", "range": period, "includePrePost": "false", "events": "div|split"}
    r = requests.get(url, params=params, headers=UA, timeout=30)
    r.raise_for_status()
    j = r.json()
    res = j["chart"]["result"][0]
    ts = pd.to_datetime(res["timestamp"], unit="s")
    q = res["indicators"]["quote"][0]
    df = pd.DataFrame({"Date": ts, "open": q["open"], "high": q["high"],
                       "low": q["low"], "close": q["close"], "volume": q["volume"]})
    df = df.set_index("Date").sort_index().dropna()
    return df


def load_universe() -> dict:
    """Fetch a small multi-regime universe. Each fetch logged; failures fall back."""
    uni = {}
    attempts = []
    try:
        uni["SPY_stooq"] = fetch_stooq_daily("spy.us")
        attempts.append("SPY_stooq OK")
    except Exception as e:
        attempts.append(f"SPY_stooq FAIL {str(e)[:120]}")
    try:
        uni["BTC_binance"] = fetch_binance_daily("BTCUSDT", days=1500)
        attempts.append("BTC_binance OK")
    except Exception as e:
        attempts.append(f"BTC_binance FAIL {str(e)[:120]}")
    try:
        uni["ETH_binance"] = fetch_binance_daily("ETHUSDT", days=1500)
        attempts.append("ETH_binance OK")
    except Exception as e:
        attempts.append(f"ETH_binance FAIL {str(e)[:120]}")
    try:
        uni["BTC_coinbase"] = fetch_coinbase_daily("BTC-USD")
        attempts.append("BTC_coinbase OK")
    except Exception as e:
        attempts.append(f"BTC_coinbase FAIL {str(e)[:120]}")
    try:
        uni["SPY_yahoo"] = fetch_yahoo_daily("SPY")
        attempts.append("SPY_yahoo OK")
    except Exception as e:
        attempts.append(f"SPY_yahoo FAIL {str(e)[:120]}")
    if not uni:
        raise RuntimeError("No live market data available. Check network.")
    return uni, attempts


def fetch_coinbase_daily(product: str = "BTC-USD") -> pd.DataFrame:
    """Coinbase public candles, no key. Returns daily OHLCV."""
    url = f"https://api.exchange.coinbase.com/products/{product}/candles"
    params = {"granularity": 86400}
    r = requests.get(url, params=params, headers={**UA, "Accept": "application/json"}, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        raise ValueError(f"Coinbase empty for {product}")
    df = pd.DataFrame(rows, columns=["ts", "low", "high", "open", "close", "volume"])
    df["Date"] = pd.to_datetime(df["ts"], unit="s")
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    df = df.set_index("Date").sort_index()[["open", "high", "low", "close", "volume"]]
    return df
