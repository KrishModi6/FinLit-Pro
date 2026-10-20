"""The owner's model: the v1.0 port must reproduce the original, v1.1 must differ only where documented,
and the evaluation must be point in time."""

import numpy as np
import pandas as pd
import pytest
from conftest import bars_from, gbm_closes

from finlit_pro.model import registry
from finlit_pro.model.evaluation import walk_forward
from finlit_pro.model.finlit_predictor import FinLitPredictor, adjusted_window
from finlit_pro.model.interface import Forecast, InputSpec, Signal


def sample_bars(n=900, seed=11):
    closes = gbm_closes(n, mu=0.0005, sigma=0.018, seed=seed)
    bars = bars_from(closes)
    rng = np.random.default_rng(seed)
    bars["volume"] = rng.integers(500_000, 2_000_000, len(bars)).astype(float)
    return bars


def legacy_reference(raw: pd.DataFrame, forecast_days: int, num_simulations: int) -> dict:
    """A line-by-line transcription of the AI Predictor page in finlit-pro-legacy/app.py
    (calculate_indicators, then the prediction block), loops and global RNG included.
    Only the Streamlit calls are removed. scipy's linregress is replaced by polyfit and
    corrcoef, which give the same slope, intercept and r."""
    data = raw.copy()
    data["SMA_20"] = data["close"].rolling(20).mean()
    data["SMA_50"] = data["close"].rolling(50).mean()
    data["BB_middle"] = data["close"].rolling(20).mean()
    data["BB_std"] = data["close"].rolling(20).std()
    data["BB_upper"] = data["BB_middle"] + (data["BB_std"] * 2)
    data["BB_lower"] = data["BB_middle"] - (data["BB_std"] * 2)
    delta = data["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    data["RSI"] = 100 - (100 / (1 + gain / loss))
    exp1 = data["close"].ewm(span=12).mean()
    exp2 = data["close"].ewm(span=26).mean()
    data["MACD"] = exp1 - exp2
    data["MACD_signal"] = data["MACD"].ewm(span=9).mean()
    data["MACD_hist"] = data["MACD"] - data["MACD_signal"]

    closes = data["close"].dropna().values
    current_price = closes[-1]
    log_returns = np.diff(np.log(closes))
    mu, sigma = log_returns.mean(), log_returns.std()
    np.random.seed(42)
    sims = np.zeros((num_simulations, forecast_days))
    for sim in range(num_simulations):
        prices = [current_price]
        for _ in range(forecast_days):
            prices.append(prices[-1] * np.exp(np.random.normal(mu, sigma)))
        sims[sim] = prices[1:]
    mc_median = np.median(sims[:, -1])
    prob_up = np.mean(sims[:, -1] > current_price) * 100

    lookback = min(120, len(closes))
    recent = closes[-lookback:]
    slope, intercept = np.polyfit(np.arange(lookback), recent, 1)
    r_value = np.corrcoef(np.arange(lookback), recent)[0, 1]
    trend_target = (slope * np.arange(lookback, lookback + forecast_days) + intercept)[-1]

    ema_12 = pd.Series(closes).ewm(span=12).mean().iloc[-1]
    ema_26 = pd.Series(closes).ewm(span=26).mean().iloc[-1]
    ema_target = current_price * (1 + (ema_12 - ema_26) / ema_26 * forecast_days / 12)

    score = 0
    rsi_val = data["RSI"].dropna().iloc[-1]
    score += 2 if rsi_val < 30 else 1 if rsi_val < 40 else -2 if rsi_val > 70 else -1 if rsi_val > 60 else 0
    macd_val, macd_sig = data["MACD"].dropna().iloc[-1], data["MACD_signal"].dropna().iloc[-1]
    h, hp = data["MACD_hist"].dropna().iloc[-1], data["MACD_hist"].dropna().iloc[-2]
    score += 2 if macd_val > macd_sig and h > hp else 1 if macd_val > macd_sig else -2 if macd_val < macd_sig and h < hp else -1 if macd_val < macd_sig else 0
    sma20, sma50 = data["SMA_20"].dropna().iloc[-1], data["SMA_50"].dropna().iloc[-1]
    p = current_price
    score += 2 if p > sma20 > sma50 else 1 if p > sma20 else -2 if p < sma20 < sma50 else -1 if p < sma20 else 0
    up, lo = data["BB_upper"].dropna().iloc[-1], data["BB_lower"].dropna().iloc[-1]
    bb = (p - lo) / (up - lo) if (up - lo) != 0 else 0.5
    score += -2 if bb > 0.95 else -1 if bb > 0.8 else 2 if bb < 0.05 else 1 if bb < 0.2 else 0
    vol_ratio = data["volume"].iloc[-1] / data["volume"].rolling(20).mean().dropna().iloc[-1]
    price_up = closes[-1] > closes[-2]
    score += 2 if vol_ratio > 1.5 and price_up else -2 if vol_ratio > 1.5 else 1 if vol_ratio > 1.2 and price_up else 0
    roc_10 = (closes[-1] - closes[-10]) / closes[-10] * 100
    roc_30 = (closes[-1] - closes[-30]) / closes[-30] * 100
    score += 2 if roc_10 > 5 and roc_30 > 10 else 1 if roc_10 > 2 else -2 if roc_10 < -5 and roc_30 < -10 else -1 if roc_10 < -2 else 0

    composite = mc_median * 0.40 + trend_target * 0.30 + ema_target * 0.30
    spread = np.std([mc_median, trend_target, ema_target]) / current_price * 100
    conf = min(95, 90 - spread) if spread < 2 else min(80, 75 - spread) if spread < 5 else max(30, 60 - spread)
    verdict = "STRONG BUY" if score >= 4 else "BUY" if score >= 2 else "STRONG SELL" if score <= -4 else "SELL" if score <= -2 else "HOLD"
    return {"mc_median": mc_median, "prob_up": prob_up, "trend": trend_target, "r2": r_value**2, "ema": ema_target, "rsi": rsi_val, "score": score, "composite": composite, "confidence": conf, "verdict": verdict}


@pytest.mark.parametrize("horizon,sims,seed", [(30, 1000, 11), (7, 500, 5), (90, 500, 23)])
def test_v10_reproduces_the_original_model(horizon, sims, seed):
    bars = sample_bars(seed=seed)
    ref = legacy_reference(adjusted_window(bars), horizon, sims)
    fc = FinLitPredictor("original").predict(bars, horizon, sims)
    assert fc.components["Monte Carlo median"] == pytest.approx(ref["mc_median"], rel=1e-9)
    assert fc.prob_up * 100 == pytest.approx(ref["prob_up"])
    assert fc.components["Regression trend"] == pytest.approx(ref["trend"], rel=1e-9)
    assert fc.components["EMA momentum"] == pytest.approx(ref["ema"], rel=1e-12)
    assert fc.diagnostics["Regression R2"] == pytest.approx(ref["r2"], rel=1e-9)
    assert fc.diagnostics["RSI"] == pytest.approx(ref["rsi"], rel=1e-12)
    assert fc.score == ref["score"] and fc.verdict == ref["verdict"]
    assert fc.target == pytest.approx(ref["composite"], rel=1e-9)
    assert fc.diagnostics["Confidence % (original heuristic, not a probability)"] == pytest.approx(ref["confidence"], rel=1e-9)


def test_v10_uses_the_original_inputs():
    bars = sample_bars(n=1500)
    fc = FinLitPredictor("original").predict(bars, 30, 500)
    assert fc.diagnostics["Sessions used"] < 530  # 730 calendar days of a 1,500-session history
    assert isinstance(fc, Forecast) and all(isinstance(s, Signal) for s in fc.signals) and len(fc.signals) == 6
    assert all(isinstance(i, InputSpec) for i in fc.inputs)
    assert fc.score_range == (-12, 12)
    assert list(fc.quantiles) == [10, 25, 50, 75, 90] and len(fc.bands[50]) == 30


def test_v10_is_reproducible_and_seeded():
    bars = sample_bars()
    m = FinLitPredictor("original")
    assert m.predict(bars, 30, 500).target == m.predict(bars, 30, 500).target
    assert m.predict(bars, 30, 500, seed=1).components["Monte Carlo median"] != m.predict(bars, 30, 500).components["Monte Carlo median"]


def test_v11_changes_only_the_documented_parts():
    bars = sample_bars()
    a = FinLitPredictor("original").predict(bars, 60, 500)
    b = FinLitPredictor("corrected").predict(bars, 60, 500)
    # Same simulation and regression.
    assert a.components["Monte Carlo median"] == b.components["Monte Carlo median"]
    assert a.components["Regression trend"] == b.components["Regression trend"]
    # Wilder's RSI differs from the rolling-mean RSI.
    assert a.diagnostics["RSI"] != pytest.approx(b.diagnostics["RSI"], abs=1e-6)
    # The decayed EMA projection moves less than the linear one.
    move_a = a.components["EMA momentum"] / a.price - 1
    move_b = b.components["EMA momentum"] / b.price - 1
    assert abs(move_b) < abs(move_a) and np.sign(move_b) == np.sign(move_a)
    # No pseudo-probability in v1.1.
    assert not any("Confidence" in k for k in b.diagnostics)


def test_model_refuses_short_or_invalid_requests():
    bars = sample_bars(n=40)
    with pytest.raises(ValueError, match="at least 60 sessions"):
        FinLitPredictor().predict(bars, 30, 500)
    with pytest.raises(ValueError, match="at least 1"):
        FinLitPredictor().predict(sample_bars(), 0, 500)


def test_registry_lists_both_versions_and_rejects_unknown_keys():
    assert set(registry.MODELS) == {"finlit-v1.0", "finlit-v1.1"}
    assert registry.get().key == registry.DEFAULT == "finlit-v1.0"
    with pytest.raises(ValueError, match="No prediction model"):
        registry.get("finlit-v9")


# ------------------------------------------------------------------ evaluation


class Spy:
    """A stand-in model that records what history it was shown and always calls a rise."""

    key, name, version, description = "spy", "Spy", "0", "test"
    horizons, simulations = (5,), (10,)
    lookback_calendar_days = 60
    bullish, bearish = ("BUY",), ("SELL",)

    def __init__(self):
        self.seen = []

    def input_spec(self, horizon, simulations):
        return []

    def predict(self, bars, horizon, simulations, seed=42):
        self.seen.append(bars.index[-1])
        p = float(bars["adjclose"].iloc[-1])
        return Forecast("Spy", "0", bars.index[-1], horizon, p, p * 1.01, "BUY", 1, (-1, 1), {10: p * 0.9, 90: p * 1.1}, 0.6)


def test_walk_forward_is_point_in_time_and_scores_against_the_future():
    bars = sample_bars(n=600)
    spy = Spy()
    ev = walk_forward(spy, bars, horizon=5)
    rec = ev.records
    # The model only ever saw history up to each origin.
    assert spy.seen == list(rec.index)
    # Outcomes are the move over the next 5 sessions.
    closes = bars["adjclose"]
    for when in rec.index[:20]:
        i = closes.index.get_loc(when)
        assert rec.at[when, "realized_return"] == pytest.approx(closes.iloc[i + 5] / closes.iloc[i] - 1)
    # Non-overlapping origins by default.
    gaps = np.diff([closes.index.get_loc(d) for d in rec.index])
    assert set(gaps) == {5}


def test_walk_forward_metrics_against_hand_calculation():
    bars = sample_bars(n=600)
    ev = walk_forward(Spy(), bars, horizon=5, cost_bps=10)
    real = ev.records["realized_return"].to_numpy()
    assert ev.metric("Directional hit rate").value == pytest.approx((real > 0).mean())
    # Always long: the long/flat strategy is buy-and-hold less one entry cost.
    growth = ev.equity["Long/flat"].to_numpy()
    assert growth[-1] == pytest.approx((1 + real[0] - 0.001) * np.prod(1 + real[1:]), rel=1e-12)
    assert ev.metric("Long/flat exposure").value == 1.0
    assert ev.metric("Skill vs no-change") is not None and ev.metric("Information coefficient") is not None
    assert list(ev.buckets.index) == ["BUY"]


def test_walk_forward_needs_enough_history_and_can_be_cancelled():
    with pytest.raises(ValueError, match="at least 8"):
        walk_forward(Spy(), sample_bars(n=70), horizon=5)
    with pytest.raises(InterruptedError):
        walk_forward(Spy(), sample_bars(n=600), horizon=5, cancelled=lambda: True)


def test_walk_forward_on_the_real_model_reports_progress():
    calls = []
    ev = walk_forward(registry.get("finlit-v1.0"), sample_bars(n=1100), horizon=30, simulations=200, progress=lambda d, t: calls.append((d, t)))
    assert calls[-1][0] == calls[-1][1] == len(ev.records)
    assert ev.model_key == "finlit-v1.0" and ev.horizon == 30
    assert 0 <= ev.metric("10-90 band coverage").value <= 1
