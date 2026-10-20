"""Technical indicators, matching the definitions the FinLit Pro course teaches."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(values: pd.Series, period: int) -> pd.Series:
    return values.rolling(period, min_periods=period).mean()


def ema(values: pd.Series, span: int) -> pd.Series:
    return values.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(values: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index with Wilder's smoothing.

    First Version (legacy Streamlit app): averaged gains and losses with a
    plain 14-day rolling mean. That is Cutler's RSI, a different indicator,
    and it reads noticeably jumpier than the RSI every charting platform shows.
    Current Version: Wilder's smoothing (an EMA with alpha = 1/period), seeded
    with the simple average of the first `period` changes, the same maths as
    the FinLit Pro web Market Explorer.
    """
    n = len(values)
    out = np.full(n, np.nan)
    if n <= period:
        return pd.Series(out, index=values.index)

    change = np.diff(values.to_numpy(dtype=float))
    gains = np.clip(change, 0, None)
    losses = np.clip(-change, 0, None)

    def at(g: float, lo: float) -> float:
        # No losses pins RSI at 100 by convention, but no gains AND no losses
        # means the price never moved, which is neutral, not overbought.
        if lo == 0:
            return 50.0 if g == 0 else 100.0
        return 100 - 100 / (1 + g / lo)

    g, lo = gains[:period].mean(), losses[:period].mean()
    out[period] = at(g, lo)
    for i in range(period + 1, n):
        g = (g * (period - 1) + gains[i - 1]) / period
        lo = (lo * (period - 1) + losses[i - 1]) / period
        out[i] = at(g, lo)
    return pd.Series(out, index=values.index)


def macd(values: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    line = values.ewm(span=fast, adjust=False).mean() - values.ewm(span=slow, adjust=False).mean()
    sig = line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})


def bollinger(values: pd.Series, period: int = 20, mult: float = 2.0) -> pd.DataFrame:
    mid = sma(values, period)
    # Population standard deviation over the window, the Bollinger convention.
    sd = values.rolling(period, min_periods=period).std(ddof=0)
    return pd.DataFrame({"mid": mid, "upper": mid + mult * sd, "lower": mid - mult * sd})


def atr(bars: pd.DataFrame, period: int = 14) -> pd.Series:
    prev = bars["close"].shift()
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - prev).abs(), (bars["low"] - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def log_returns(values: pd.Series) -> pd.Series:
    clean = values[values > 0]
    return np.log(clean / clean.shift()).dropna()


def max_drawdown(values: pd.Series) -> float:
    """Largest peak-to-trough fall as a positive fraction (0.35 = -35%)."""
    peak = values.cummax()
    return float(((peak - values) / peak).max()) if len(values) else 0.0


def drawdown_series(values: pd.Series) -> pd.Series:
    return values / values.cummax() - 1
