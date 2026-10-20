import numpy as np
import pytest
from conftest import gbm_closes

from finlit_quant.analytics import montecarlo as mc
from finlit_quant.validation import ValidationError


def test_historical_drift_is_not_ito_corrected_twice():
    """Regression test for the FinLit Pro website bug.

    The website subtracted sigma^2/2 from a drift that was already a mean LOG
    return. With historical drift, the median path must grow at the mean log
    return itself: S0 * exp(mu_log * h).
    """
    closes = gbm_closes(n=2000, mu=0.0006, sigma=0.03)
    cfg = mc.MCConfig(model="gbm", drift_mode="historical", horizon_days=252, n_paths=40000, seed=1)
    r = mc.simulate(closes, cfg)
    expected_median = r.start_price * np.exp(r.est.hist_mu * 252)
    double_corrected = r.start_price * np.exp((r.est.hist_mu - r.est.sigma**2 / 2) * 252)
    assert abs(r.stats["median"] / expected_median - 1) < 0.02
    # The buggy version would sit about 11% lower at 3% daily vol.
    assert r.stats["median"] > double_corrected * 1.07


def test_zero_drift_keeps_expected_price_flat():
    r = mc.simulate(gbm_closes(), mc.MCConfig(model="gbm", drift_mode="zero", horizon_days=126, n_paths=60000, seed=2))
    assert abs(r.stats["mean"] / r.start_price - 1) < 0.01


def test_custom_return_sets_the_arithmetic_mean():
    r = mc.simulate(gbm_closes(), mc.MCConfig(model="gbm", drift_mode="custom", custom_return=0.10, horizon_days=252, n_paths=60000, seed=3))
    assert abs(r.stats["mean"] / r.start_price - 1.10) < 0.012


def test_student_t_has_fatter_tails_but_same_volatility():
    rng = np.random.default_rng(9)
    # A fat-tailed history so the fitted df is low.
    import pandas as pd

    r = rng.standard_t(3, 2000) * 0.01
    closes = pd.Series(100 * np.exp(np.cumsum(r)), index=pd.bdate_range("2016-01-01", periods=2000))
    base = dict(horizon_days=1, n_paths=100000, seed=4, drift_mode="zero", lookback_days=2000)
    t = mc.simulate(closes, mc.MCConfig(model="student_t", **base))
    g = mc.simulate(closes, mc.MCConfig(model="gbm", **base))
    lt, lg = np.log(t.terminal / t.start_price), np.log(g.terminal / g.start_price)

    def kurt(x):
        x = x - x.mean()
        return np.mean(x**4) / np.mean(x**2) ** 2 - 3

    assert t.est.t_df < 6
    assert kurt(lt) > kurt(lg) + 1
    assert abs(lt.std() / lg.std() - 1) < 0.05


def test_bootstrap_reuses_history_volatility():
    closes = gbm_closes(sigma=0.02)
    r = mc.simulate(closes, mc.MCConfig(model="bootstrap", horizon_days=1, n_paths=50000, seed=5, drift_mode="historical"))
    daily = np.log(r.terminal / r.start_price)
    assert abs(daily.std() / r.est.sigma - 1) < 0.05


def test_stats_are_consistent():
    r = mc.simulate(gbm_closes(), mc.MCConfig(n_paths=5000, horizon_days=63))
    s = r.stats
    assert s["p5"] < s["p25"] < s["p50"] < s["p75"] < s["p95"]
    assert 0 <= s["prob_up"] <= 1
    assert s["cvar95"] >= s["var95"]
    assert r.bands[5].shape == r.days.shape
    assert r.bands[5][0] == pytest.approx(r.start_price)
    assert (r.max_drawdowns >= 0).all()


def test_seed_reproduces_and_none_varies():
    closes = gbm_closes()
    a = mc.simulate(closes, mc.MCConfig(n_paths=1000, horizon_days=20, seed=11))
    b = mc.simulate(closes, mc.MCConfig(n_paths=1000, horizon_days=20, seed=11))
    assert np.array_equal(a.terminal, b.terminal)


def test_config_validation_messages():
    with pytest.raises(ValidationError, match="too much to hold"):
        mc.MCConfig(n_paths=200000, horizon_days=2520).validate()
    with pytest.raises(ValidationError, match="at least 100 paths"):
        mc.MCConfig(n_paths=10).validate()
    with pytest.raises(ValidationError, match="at least 60"):
        mc.simulate(gbm_closes(n=30), mc.MCConfig())


def test_analytic_quantile_median():
    assert mc.analytic_quantile(100, 0.001, 0.02, 252, 0.5) == pytest.approx(100 * np.exp(0.252))


def test_calibration_on_true_gbm_is_close_to_nominal():
    cal = mc.calibration(gbm_closes(n=2600, seed=8), horizon_days=21)
    assert cal is not None and cal.tests > 50
    nominal, observed = cal.coverage["10-90"]
    assert nominal == 0.8
    assert 0.65 < observed < 0.95
    assert ((cal.pit >= 0) & (cal.pit <= 1)).all()


def test_calibration_needs_history():
    assert mc.calibration(gbm_closes(n=300), horizon_days=252) is None
