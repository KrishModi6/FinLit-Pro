"""The legacy FinLit Pro "AI Predictor" signal engine, ported from the Streamlit app.

The original combined four things: a Monte Carlo median, a linear regression
trend, an EMA momentum target, and a six-signal technical score. All four
survive here with the same thresholds and weights, so results line up with
what the old app showed, apart from the defects listed below (and in
docs/FIXLOG.md), which are fixed rather than preserved.

  1. RSI used a plain rolling mean (Cutler's RSI). Now Wilder's, like every
     charting platform.
  2. "10-day momentum" compared against closes[-10], which is 9 sessions back.
     Now closes[-11].
  3. The EMA target extrapolated momentum linearly for the whole horizon, so a
     3% MACD gap became +63% at a one-year horizon. Momentum now decays with a
     60-session half-life, which leaves short horizons close to the original.
  4. A "confidence %" was computed as 90 minus the models' disagreement. It
     looked like a probability and was not one. The disagreement itself is
     now reported, labelled as what it is.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from finlit_quant.analytics import indicators as ind

WEIGHTS = {"monte_carlo": 0.40, "trend": 0.30, "ema": 0.30}
MOMENTUM_HALF_LIFE = 60


@dataclass
class Signal:
    name: str
    reading: str
    score: int


@dataclass
class PredictorResult:
    signals: list[Signal]
    score: int
    max_score: int
    verdict: str
    trend_target: float
    trend_r2: float
    ema_target: float
    mc_median: float
    composite_target: float
    composite_change: float
    model_spread_pct: float
    agreement: str


def _effective_days(horizon: int) -> float:
    """Sum of a decaying momentum weight over the horizon (~= horizon when short)."""
    k = np.log(2) / MOMENTUM_HALF_LIFE
    return float((1 - np.exp(-k * horizon)) / k)


def signals(bars: pd.DataFrame) -> list[Signal]:
    close = bars["close"]
    price = float(close.iloc[-1])
    out: list[Signal] = []

    # 1. RSI
    rsi_val = float(ind.rsi(close).iloc[-1])
    if rsi_val < 30:
        out.append(Signal("RSI", f"Oversold at {rsi_val:.0f}: strong bullish", 2))
    elif rsi_val < 40:
        out.append(Signal("RSI", f"Approaching oversold at {rsi_val:.0f}: bullish", 1))
    elif rsi_val > 70:
        out.append(Signal("RSI", f"Overbought at {rsi_val:.0f}: strong bearish", -2))
    elif rsi_val > 60:
        out.append(Signal("RSI", f"Approaching overbought at {rsi_val:.0f}: caution", -1))
    else:
        out.append(Signal("RSI", f"Neutral at {rsi_val:.0f}", 0))

    # 2. MACD
    m = ind.macd(close)
    line, sig, hist, hist_prev = m["macd"].iloc[-1], m["signal"].iloc[-1], m["hist"].iloc[-1], m["hist"].iloc[-2]
    if line > sig and hist > hist_prev:
        out.append(Signal("MACD", "Above signal line and accelerating", 2))
    elif line > sig:
        out.append(Signal("MACD", "Above signal line", 1))
    elif line < sig and hist < hist_prev:
        out.append(Signal("MACD", "Below signal line and accelerating down", -2))
    elif line < sig:
        out.append(Signal("MACD", "Below signal line", -1))
    else:
        out.append(Signal("MACD", "Flat", 0))

    # 3. Moving averages
    sma20, sma50 = float(ind.sma(close, 20).iloc[-1]), float(ind.sma(close, 50).iloc[-1])
    if price > sma20 > sma50:
        out.append(Signal("Moving averages", "Price > SMA20 > SMA50: strong uptrend", 2))
    elif price > sma20:
        out.append(Signal("Moving averages", "Above SMA20: short-term bullish", 1))
    elif price < sma20 < sma50:
        out.append(Signal("Moving averages", "Price < SMA20 < SMA50: strong downtrend", -2))
    elif price < sma20:
        out.append(Signal("Moving averages", "Below SMA20: short-term bearish", -1))
    else:
        out.append(Signal("Moving averages", "Mixed", 0))

    # 4. Bollinger position
    bb = ind.bollinger(close)
    upper, lower = float(bb["upper"].iloc[-1]), float(bb["lower"].iloc[-1])
    pos = (price - lower) / (upper - lower) if upper != lower else 0.5
    if pos > 0.95:
        out.append(Signal("Bollinger Bands", f"At the upper band ({pos:.0%}): stretched", -2))
    elif pos > 0.8:
        out.append(Signal("Bollinger Bands", f"Near the upper band ({pos:.0%})", -1))
    elif pos < 0.05:
        out.append(Signal("Bollinger Bands", f"At the lower band ({pos:.0%}): washed out", 2))
    elif pos < 0.2:
        out.append(Signal("Bollinger Bands", f"Near the lower band ({pos:.0%})", 1))
    else:
        out.append(Signal("Bollinger Bands", f"Inside the bands ({pos:.0%})", 0))

    # 5. Volume
    vol = bars["volume"]
    vol_avg = float(vol.rolling(20).mean().iloc[-1])
    ratio = float(vol.iloc[-1]) / vol_avg if vol_avg > 0 else 1.0
    up = close.iloc[-1] > close.iloc[-2]
    if ratio > 1.5 and up:
        out.append(Signal("Volume", f"{ratio:.1f}x average on an up day: confirmed rally", 2))
    elif ratio > 1.5:
        out.append(Signal("Volume", f"{ratio:.1f}x average on a down day: distribution", -2))
    elif ratio > 1.2 and up:
        out.append(Signal("Volume", f"{ratio:.1f}x average and rising", 1))
    elif ratio < 0.6:
        out.append(Signal("Volume", f"{ratio:.1f}x average: weak conviction", 0))
    else:
        out.append(Signal("Volume", f"{ratio:.1f}x average: normal", 0))

    # 6. Momentum (rate of change over 10 and 30 sessions)
    roc10 = (price / float(close.iloc[-11]) - 1) * 100 if len(close) > 11 else 0.0
    roc30 = (price / float(close.iloc[-31]) - 1) * 100 if len(close) > 31 else 0.0
    if roc10 > 5 and roc30 > 10:
        out.append(Signal("Momentum", f"Strong: 10d {roc10:+.1f}%, 30d {roc30:+.1f}%", 2))
    elif roc10 > 2:
        out.append(Signal("Momentum", f"Positive: 10d {roc10:+.1f}%", 1))
    elif roc10 < -5 and roc30 < -10:
        out.append(Signal("Momentum", f"Strongly negative: 10d {roc10:+.1f}%, 30d {roc30:+.1f}%", -2))
    elif roc10 < -2:
        out.append(Signal("Momentum", f"Negative: 10d {roc10:+.1f}%", -1))
    else:
        out.append(Signal("Momentum", f"Flat: 10d {roc10:+.1f}%", 0))
    return out


def verdict_for(score: int) -> str:
    if score >= 4:
        return "Strong bullish"
    if score >= 2:
        return "Bullish"
    if score <= -4:
        return "Strong bearish"
    if score <= -2:
        return "Bearish"
    return "Neutral"


def run(bars: pd.DataFrame, mc_median: float, horizon_days: int) -> PredictorResult:
    close = bars["close"]
    price = float(close.iloc[-1])

    # Linear regression trend over the last 120 sessions.
    lookback = min(120, len(close))
    y = close.iloc[-lookback:].to_numpy(dtype=float)
    x = np.arange(lookback, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    ss_res = float(((y - fitted) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    trend_target = float(slope * (lookback - 1 + horizon_days) + intercept)
    # A straight line through a falling stock crosses zero eventually; a
    # price cannot.
    trend_target = max(trend_target, 0.01 * price)

    # EMA momentum target. Legacy used pandas' default adjust=True EMAs.
    ema12 = float(close.ewm(span=12).mean().iloc[-1])
    ema26 = float(close.ewm(span=26).mean().iloc[-1])
    momentum = (ema12 - ema26) / ema26
    ema_target = max(price * (1 + momentum * _effective_days(horizon_days) / 12), 0.01 * price)

    sigs = signals(bars)
    score = sum(s.score for s in sigs)
    composite = WEIGHTS["monte_carlo"] * mc_median + WEIGHTS["trend"] * trend_target + WEIGHTS["ema"] * ema_target
    spread = float(np.std([mc_median, trend_target, ema_target]) / price * 100)
    agreement = "High" if spread < 2 else ("Medium" if spread < 5 else "Low")

    return PredictorResult(
        signals=sigs,
        score=score,
        max_score=2 * len(sigs),
        verdict=verdict_for(score),
        trend_target=trend_target,
        trend_r2=r2,
        ema_target=ema_target,
        mc_median=mc_median,
        composite_target=composite,
        composite_change=composite / price - 1,
        model_spread_pct=spread,
        agreement=agreement,
    )
