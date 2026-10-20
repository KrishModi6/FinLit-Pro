import numpy as np
import pandas as pd

from finlit_quant.analytics import indicators as ind


def reference_wilder_rsi(values, period=14):
    """Straight transcription of Wilder's definition, for comparison."""
    changes = np.diff(values)
    out = [np.nan] * len(values)
    g = np.mean(np.clip(changes[:period], 0, None))
    lo = np.mean(np.clip(-changes[:period], 0, None))
    out[period] = 100 - 100 / (1 + g / lo)
    for i in range(period + 1, len(values)):
        c = changes[i - 1]
        g = (g * (period - 1) + max(c, 0)) / period
        lo = (lo * (period - 1) + max(-c, 0)) / period
        out[i] = 100 - 100 / (1 + g / lo)
    return np.array(out)


def test_rsi_matches_wilder_definition():
    rng = np.random.default_rng(1)
    values = 100 + np.cumsum(rng.normal(0, 1, 300))
    got = ind.rsi(pd.Series(values)).to_numpy()
    want = reference_wilder_rsi(values)
    assert np.isnan(got[:14]).all()
    np.testing.assert_allclose(got[14:], want[14:], rtol=1e-12)


def test_rsi_edge_cases():
    assert ind.rsi(pd.Series(np.arange(1, 40, dtype=float))).iloc[-1] == 100.0
    assert ind.rsi(pd.Series(np.full(40, 5.0))).iloc[-1] == 50.0
    assert ind.rsi(pd.Series([1.0, 2.0])).isna().all()


def test_sma_bollinger_macd_shapes():
    s = pd.Series(np.linspace(1, 100, 100))
    assert ind.sma(s, 10).iloc[9] == np.mean(np.linspace(1, 100, 100)[:10])
    bb = ind.bollinger(s, 20)
    assert (bb["upper"].dropna() > bb["lower"].dropna()).all()
    m = ind.macd(s)
    assert m["macd"].iloc[-1] > 0  # a rising line has the fast EMA above the slow one


def test_drawdown():
    s = pd.Series([100, 120, 60, 90, 130.0])
    assert abs(ind.max_drawdown(s) - 0.5) < 1e-12
    assert ind.drawdown_series(s).min() == -0.5
