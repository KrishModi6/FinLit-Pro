import numpy as np
import pandas as pd
import pytest
from conftest import bars_from, gbm_closes

from finlit_quant.analytics import portfolio, predictor, risk


def test_signal_engine_reads_a_steady_uptrend_as_bullish():
    closes = pd.Series(np.linspace(50, 100, 300) * (1 + 0.002 * np.sin(np.arange(300))), index=pd.bdate_range("2020-01-01", periods=300))
    res = predictor.run(bars_from(closes), mc_median=105, horizon_days=21)
    names = [s.name for s in res.signals]
    assert names == ["RSI", "MACD", "Moving averages", "Bollinger Bands", "Volume", "Momentum"]
    assert res.max_score == 12
    ma = res.signals[2]
    assert ma.score == 2
    assert res.trend_target > closes.iloc[-1]
    assert res.trend_r2 > 0.95
    expected = 0.4 * res.mc_median + 0.3 * res.trend_target + 0.3 * res.ema_target
    assert res.composite_target == pytest.approx(expected)


def test_ema_momentum_decays_at_long_horizons():
    short = predictor._effective_days(21)
    long = predictor._effective_days(252)
    assert 18 < short < 21  # close to the legacy linear projection
    assert long < 100  # instead of 252: the +63% blow-up is gone


def test_verdict_thresholds():
    assert predictor.verdict_for(4) == "Strong bullish"
    assert predictor.verdict_for(2) == "Bullish"
    assert predictor.verdict_for(1) == "Neutral"
    assert predictor.verdict_for(-2) == "Bearish"
    assert predictor.verdict_for(-5) == "Strong bearish"


def test_beta_and_correlation_of_a_levered_copy():
    bench = gbm_closes(n=900, seed=4)
    rb = bench.pct_change().fillna(0)
    stock = 50 * (1 + 2 * rb).cumprod()
    rep = risk.report(stock, bench, 0.0, 3, "BENCH")
    m = rep.metrics
    assert m["beta"] == pytest.approx(2.0, rel=1e-6)
    assert m["correlation"] == pytest.approx(1.0, abs=1e-9)
    assert m["volatility"] == pytest.approx(2 * m["bench_volatility"], rel=1e-6)
    assert rep.rolling_beta is not None


def test_risk_without_benchmark_notes_it():
    rep = risk.report(gbm_closes(), None, 0.04, 3, "SPY")
    assert "beta" not in rep.metrics
    assert any("SPY" in n for n in rep.notes)
    assert rep.metrics["max_drawdown"] > 0
    assert rep.metrics["cvar95_1d"] >= rep.metrics["var95_1d"]


def test_risk_rejects_tiny_window():
    with pytest.raises(ValueError, match="60 trading days"):
        risk.report(gbm_closes(n=40), None, 0.04, 1)


def test_compare_and_frontier():
    closes = {"A": gbm_closes(seed=1), "B": gbm_closes(seed=2, sigma=0.01), "C": gbm_closes(seed=3, sigma=0.025)}
    cmp = portfolio.compare(closes, 3, 0.03)
    assert list(cmp.stats.index) == ["A", "B", "C"]
    assert (cmp.growth.iloc[0] == 100).all()
    assert np.allclose(np.diag(cmp.correlation), 1)
    fr = portfolio.frontier(cmp.returns, 0.03, n=2000)
    assert np.allclose(fr.weights.sum(axis=1), 1)
    assert fr.vols[fr.min_vol] <= fr.vols.min() + 1e-12
    assert fr.sharpes[fr.max_sharpe] == fr.sharpes.max()
