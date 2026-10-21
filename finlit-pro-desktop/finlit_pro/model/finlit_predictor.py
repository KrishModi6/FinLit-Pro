"""The FinLit AI Predictor: the owner's existing stock-prediction model.

Source: `finlit-pro-legacy/app.py`, the "AI Predictor" page (lines 2134-2688).
Two versions are provided, and neither replaces the other:

v1.0 "original"
    A faithful port. Same inputs (730 calendar days of adjusted daily bars,
    horizons of 7/14/30/60/90 trading days, 500 to 10,000 simulations, seed
    42), same calculations, same thresholds, same weights, same outputs,
    including the "confidence %" and the STRONG BUY ... STRONG SELL verdict.
    The original's Python loops are vectorised in a way that draws the
    identical random stream, so its numbers are reproduced (tested against
    a transcription of the loop in tests/test_model.py).

v1.1 "corrected"
    Identical structure, inputs, weights and labels, with four documented
    defects fixed (see docs/MODEL.md):
      1. RSI used plain rolling means (Cutler's RSI); v1.1 uses Wilder's.
      2. "10-day" momentum compared with closes[-10], nine sessions back;
         v1.1 uses closes[-11] (and closes[-31] for 30 days).
      3. The EMA target extrapolated momentum linearly over the horizon;
         v1.1 decays it with a 60-session half-life.
      4. The "confidence %" was 90 minus the models' disagreement, which
         reads like a probability and is not one; v1.1 reports the
         disagreement itself and drops the percentage.

Neither version claims any accuracy. The evaluation module measures it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from finlit_pro.analytics import indicators as ind
from finlit_pro.model.interface import Forecast, InputSpec, Signal

WEIGHTS = {"monte_carlo": 0.40, "regression": 0.30, "ema": 0.30}
HORIZONS = (7, 14, 30, 60, 90)
SIMULATIONS = (500, 1000, 5000, 10000)
LOOKBACK_CALENDAR_DAYS = 730
REGRESSION_LOOKBACK = 120
MIN_BARS = 60
MOMENTUM_HALF_LIFE = 60  # v1.1 only


def adjusted_window(bars: pd.DataFrame, lookback_days: int = LOOKBACK_CALENDAR_DAYS) -> pd.DataFrame:
    """The legacy input: `yf.Ticker(s).history(period="730d")`, which is auto-adjusted.

    yfinance's auto-adjust scales open/high/low/close by adjclose / close,
    so dividends and splits are folded into every price field.
    """
    end = bars.index[-1]
    w = bars[bars.index > end - pd.Timedelta(days=lookback_days)].copy()
    ratio = (w["adjclose"] / w["close"]).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    for col in ("open", "high", "low", "close"):
        w[col] = w[col] * ratio
    return w


def legacy_indicators(data: pd.DataFrame, variant: str) -> pd.DataFrame:
    """`calculate_indicators` from the legacy app, column for column."""
    d = data.copy()
    c = d["close"]
    d["SMA_20"] = c.rolling(20).mean()
    d["SMA_50"] = c.rolling(50).mean()
    d["SMA_200"] = c.rolling(200).mean()
    d["BB_middle"] = c.rolling(20).mean()
    d["BB_std"] = c.rolling(20).std()  # pandas default ddof=1, as in the original
    d["BB_upper"] = d["BB_middle"] + d["BB_std"] * 2
    d["BB_lower"] = d["BB_middle"] - d["BB_std"] * 2
    if variant == "original":
        delta = c.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        d["RSI"] = 100 - (100 / (1 + gain / loss))
    else:
        d["RSI"] = ind.rsi(c, 14)
    exp1 = c.ewm(span=12).mean()  # adjust=True, the pandas default the original used
    exp2 = c.ewm(span=26).mean()
    d["MACD"] = exp1 - exp2
    d["MACD_signal"] = d["MACD"].ewm(span=9).mean()
    d["MACD_hist"] = d["MACD"] - d["MACD_signal"]
    return d


def monte_carlo(closes: np.ndarray, horizon: int, simulations: int, seed: int | None):
    """The legacy simulation: N(mu, sigma) daily log-return shocks.

    The original looped `for sim: for day: np.random.normal(mu, sigma)` after
    `np.random.seed(42)`. Drawing a (simulations, horizon) block from a
    RandomState seeded the same way yields the same numbers in the same
    order, so this is the original simulation, only faster.
    """
    log_returns = np.diff(np.log(closes))
    mu = log_returns.mean()
    sigma = log_returns.std()  # numpy default ddof=0, as in the original
    rng = np.random.RandomState(seed) if seed is not None else np.random.RandomState()
    shocks = rng.normal(mu, sigma, size=(simulations, horizon))
    paths = closes[-1] * np.exp(np.cumsum(shocks, axis=1))
    return paths, mu, sigma


def _signals(data: pd.DataFrame, closes: np.ndarray, price: float, variant: str) -> list[Signal]:
    out: list[Signal] = []
    rsi_val = float(data["RSI"].dropna().iloc[-1])
    if rsi_val < 30:
        out.append(Signal("RSI", f"Oversold ({rsi_val:.1f})", 2))
    elif rsi_val < 40:
        out.append(Signal("RSI", f"Approaching oversold ({rsi_val:.1f})", 1))
    elif rsi_val > 70:
        out.append(Signal("RSI", f"Overbought ({rsi_val:.1f})", -2))
    elif rsi_val > 60:
        out.append(Signal("RSI", f"Approaching overbought ({rsi_val:.1f})", -1))
    else:
        out.append(Signal("RSI", f"Neutral ({rsi_val:.1f})", 0))

    macd_val = data["MACD"].dropna().iloc[-1]
    macd_sig = data["MACD_signal"].dropna().iloc[-1]
    hist = data["MACD_hist"].dropna()
    h_now, h_prev = hist.iloc[-1], hist.iloc[-2]
    if macd_val > macd_sig and h_now > h_prev:
        out.append(Signal("MACD", "Bullish crossover, accelerating", 2))
    elif macd_val > macd_sig:
        out.append(Signal("MACD", "Bullish", 1))
    elif macd_val < macd_sig and h_now < h_prev:
        out.append(Signal("MACD", "Bearish crossover, accelerating", -2))
    elif macd_val < macd_sig:
        out.append(Signal("MACD", "Bearish", -1))
    else:
        out.append(Signal("MACD", "Neutral", 0))

    sma20 = data["SMA_20"].dropna().iloc[-1]
    sma50 = data["SMA_50"].dropna().iloc[-1]
    if price > sma20 > sma50:
        out.append(Signal("Moving averages", "Uptrend: price > SMA20 > SMA50", 2))
    elif price > sma20:
        out.append(Signal("Moving averages", "Above SMA20", 1))
    elif price < sma20 < sma50:
        out.append(Signal("Moving averages", "Downtrend: price < SMA20 < SMA50", -2))
    elif price < sma20:
        out.append(Signal("Moving averages", "Below SMA20", -1))
    else:
        out.append(Signal("Moving averages", "Mixed", 0))

    upper = data["BB_upper"].dropna().iloc[-1]
    lower = data["BB_lower"].dropna().iloc[-1]
    pos = (price - lower) / (upper - lower) if (upper - lower) != 0 else 0.5
    if pos > 0.95:
        out.append(Signal("Bollinger Bands", f"At upper band ({pos:.0%})", -2))
    elif pos > 0.8:
        out.append(Signal("Bollinger Bands", f"Near upper band ({pos:.0%})", -1))
    elif pos < 0.05:
        out.append(Signal("Bollinger Bands", f"At lower band ({pos:.0%})", 2))
    elif pos < 0.2:
        out.append(Signal("Bollinger Bands", f"Near lower band ({pos:.0%})", 1))
    else:
        out.append(Signal("Bollinger Bands", f"Within bands ({pos:.0%})", 0))

    vol_avg = data["volume"].rolling(20).mean().dropna().iloc[-1]
    vol_now = data["volume"].iloc[-1]
    ratio = vol_now / vol_avg if vol_avg > 0 else 1
    price_up = closes[-1] > closes[-2]
    if ratio > 1.5 and price_up:
        out.append(Signal("Volume", f"High-volume rally ({ratio:.1f}x)", 2))
    elif ratio > 1.5:
        out.append(Signal("Volume", f"High-volume selloff ({ratio:.1f}x)", -2))
    elif ratio > 1.2 and price_up:
        out.append(Signal("Volume", f"Above-average volume, up ({ratio:.1f}x)", 1))
    elif ratio < 0.6:
        out.append(Signal("Volume", f"Low volume ({ratio:.1f}x)", 0))
    else:
        out.append(Signal("Volume", f"Normal volume ({ratio:.1f}x)", 0))

    back10, back30 = (10, 30) if variant == "original" else (11, 31)
    roc10 = (closes[-1] - closes[-back10]) / closes[-back10] * 100 if len(closes) >= back10 else 0.0
    roc30 = (closes[-1] - closes[-back30]) / closes[-back30] * 100 if len(closes) >= back30 else 0.0
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
        return "STRONG BUY"
    if score >= 2:
        return "BUY"
    if score <= -4:
        return "STRONG SELL"
    if score <= -2:
        return "SELL"
    return "HOLD"


class FinLitPredictor:
    bullish = ("BUY", "STRONG BUY")
    bearish = ("SELL", "STRONG SELL")
    horizons = HORIZONS
    simulations = SIMULATIONS
    lookback_calendar_days = LOOKBACK_CALENDAR_DAYS

    def __init__(self, variant: str = "original") -> None:
        if variant not in ("original", "corrected"):
            raise ValueError("variant must be 'original' or 'corrected'")
        self.variant = variant
        self.version = "1.0" if variant == "original" else "1.1"
        self.key = f"finlit-v{self.version}"
        self.name = "FinLit AI Predictor"
        self.description = (
            "Composite of a Monte Carlo median (40%), a 120-session linear regression trend (30%) and an "
            "EMA 12/26 momentum projection (30%), with a six-signal technical score (RSI, MACD, moving "
            "averages, Bollinger position, volume, momentum) that sets the verdict."
            + (" Original implementation." if variant == "original" else " With the four documented corrections.")
        )

    def input_spec(self, horizon: int, simulations: int) -> list[InputSpec]:
        return [
            InputSpec("Price history", f"{LOOKBACK_CALENDAR_DAYS} calendar days, daily", "Open, high, low, close, volume; adjusted for splits and dividends"),
            InputSpec("Forecast horizon", f"{horizon} trading days", "Allowed: " + ", ".join(map(str, HORIZONS))),
            InputSpec("Simulations", f"{simulations:,}", "Monte Carlo paths. Allowed: " + ", ".join(f"{s:,}" for s in SIMULATIONS)),
            InputSpec("Random seed", "42", "Fixed in the original, so results are reproducible"),
            InputSpec("Regression window", f"{REGRESSION_LOOKBACK} sessions", "Least-squares line through the latest closes"),
            InputSpec("Indicators", "SMA 20/50, Bollinger 20/2, RSI 14, MACD 12/26/9, volume 20", "RSI: " + ("rolling mean (original)" if self.variant == "original" else "Wilder smoothing")),
            InputSpec("Component weights", "MC 40% / regression 30% / EMA 30%", "Fixed in the original"),
            InputSpec("Minimum history", f"{MIN_BARS} sessions", "Below this the model does not run"),
        ]

    def predict(self, bars: pd.DataFrame, horizon: int, simulations: int, seed: int | None = 42) -> Forecast:
        if horizon < 1:
            raise ValueError("Forecast horizon must be at least 1 trading day.")
        if simulations < 1:
            raise ValueError("Simulations must be at least 1.")
        raw = adjusted_window(bars)
        if len(raw) < MIN_BARS:
            raise ValueError(f"The model needs at least {MIN_BARS} sessions of history; {len(raw)} are available.")
        data = legacy_indicators(raw, self.variant)
        # First Version: a price that never moves (a money market fund such as VMFXX) gives the original's
        # rolling-mean RSI 0/0 in every window, and the signal step failed with "IndexError: single positional
        # indexer is out-of-bounds", which the original raised too. Current Version: the same refusal, as a
        # ValueError that says why. Every other input is computed exactly as before.
        if data["RSI"].notna().sum() == 0:
            raise ValueError(
                f"The price did not change in any 14-session window of the last {LOOKBACK_CALENDAR_DAYS} calendar days (a constant-price "
                "fund such as a money market fund gives this), so the model's RSI is undefined and it cannot forecast. "
                "Choose a ticker whose price moves."
            )
        closes = data["close"].dropna().values
        price = float(closes[-1])

        # 1. Monte Carlo
        paths, mu, sigma = monte_carlo(closes, horizon, simulations, seed)
        final = paths[:, -1]
        mc_median = float(np.median(final))
        quantiles = {q: float(np.percentile(final, q)) for q in (10, 25, 50, 75, 90)}
        prob_up = float(np.mean(final > price))
        days = np.arange(1, horizon + 1)
        bands = {q: np.percentile(paths, q, axis=0) for q in (10, 25, 50, 75, 90)}

        # 2. Linear regression trend over the last 120 closes
        lookback = min(REGRESSION_LOOKBACK, len(closes))
        recent = closes[-lookback:]
        x = np.arange(lookback, dtype=float)
        slope, intercept = np.polyfit(x, recent, 1)
        r = np.corrcoef(x, recent)[0, 1] if np.std(recent) > 0 else 0.0
        trend_target = float(slope * (lookback + horizon - 1) + intercept)

        # 3. EMA momentum projection
        s = pd.Series(closes)
        ema12, ema26 = float(s.ewm(span=12).mean().iloc[-1]), float(s.ewm(span=26).mean().iloc[-1])
        momentum = (ema12 - ema26) / ema26
        if self.variant == "original":
            steps = horizon
        else:
            k = np.log(2) / MOMENTUM_HALF_LIFE
            steps = (1 - np.exp(-k * horizon)) / k
        ema_target = float(price * (1 + momentum * steps / 12))

        # 4. Signals and verdict
        signals = _signals(data, closes, price, self.variant)
        score = int(sum(sg.score for sg in signals))

        # 5. Composite
        composite = WEIGHTS["monte_carlo"] * mc_median + WEIGHTS["regression"] * trend_target + WEIGHTS["ema"] * ema_target
        preds = [mc_median, trend_target, ema_target]
        spread_pct = float(np.std(preds) / price * 100)
        if spread_pct < 2:
            agreement, conf_pct = "HIGH", min(95, 90 - spread_pct)
        elif spread_pct < 5:
            agreement, conf_pct = "MEDIUM", min(80, 75 - spread_pct)
        else:
            agreement, conf_pct = "LOW", max(30, 60 - spread_pct)

        diagnostics: dict[str, float | str] = {
            "Model agreement": agreement,
            "Model spread (% of price)": spread_pct,
            "Model spread ($)": float(max(preds) - min(preds)),
            "Regression R2": float(r**2),
            "RSI": float(data["RSI"].dropna().iloc[-1]),
            "MACD histogram": float(data["MACD_hist"].dropna().iloc[-1]),
            "Volatility (annual)": float(sigma * np.sqrt(252)),
            "Mean daily log return": float(mu),
            "Monte Carlo mean": float(np.mean(final)),
            "Sessions used": float(len(closes)),
        }
        if self.variant == "original":
            diagnostics["Confidence % (original heuristic, not a probability)"] = float(conf_pct)

        return Forecast(
            model=self.name,
            version=self.version,
            as_of=raw.index[-1],
            horizon_days=horizon,
            price=price,
            target=float(composite),
            verdict=verdict_for(score),
            score=score,
            score_range=(-2 * len(signals), 2 * len(signals)),
            quantiles=quantiles,
            prob_up=prob_up,
            components={"Monte Carlo median": mc_median, "Regression trend": trend_target, "EMA momentum": ema_target},
            weights={"Monte Carlo median": 0.40, "Regression trend": 0.30, "EMA momentum": 0.30},
            diagnostics=diagnostics,
            signals=signals,
            band_days=days,
            bands=bands,
            inputs=self.input_spec(horizon, simulations),
        )
