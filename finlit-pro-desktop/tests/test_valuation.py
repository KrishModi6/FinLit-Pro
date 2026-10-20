import numpy as np
import pandas as pd
import pytest

from finlit_pro.analytics import valuation as val
from finlit_pro.data import sec
from finlit_pro.validation import ValidationError


def inputs(**kw):
    base = dict(base_fcf=100.0, growth=0.03, discount=0.08, terminal_growth=0.03, net_cash=0.0, shares=1.0)
    base.update(kw)
    return val.DCFInputs(**base)


def test_constant_growth_dcf_equals_gordon_growth():
    d = val.dcf(inputs())
    assert d.per_share == pytest.approx(100 * 1.03 / (0.08 - 0.03), rel=1e-9)


def test_net_cash_and_shares_scale_value():
    d = val.dcf(inputs(net_cash=500.0, shares=10.0))
    assert d.per_share == pytest.approx((100 * 1.03 / 0.05 + 500) / 10, rel=1e-9)


def test_reverse_dcf_round_trip():
    inp = inputs(growth=0.12, terminal_growth=0.025, discount=0.09)
    price = val.dcf(inp).per_share
    assert val.reverse_dcf(inputs(growth=0.0, terminal_growth=0.025, discount=0.09), price) == pytest.approx(0.12, abs=1e-6)


def test_reverse_dcf_out_of_range_is_none():
    assert val.reverse_dcf(inputs(), 1e12) is None


@pytest.mark.parametrize(
    "kw,fragment",
    [(dict(base_fcf=-5.0), "negative"), (dict(discount=0.03), "must be higher"), (dict(terminal_growth=0.06, discount=0.1), "outgrows"), (dict(shares=0.0), "share count")],
)
def test_dcf_validation_messages(kw, fragment):
    with pytest.raises(ValidationError, match=fragment):
        val.dcf(inputs(**kw))


def test_sensitivity_centre_is_the_base_case():
    inp = inputs(growth=0.08, terminal_growth=0.025, discount=0.09)
    rows, cols, grid = val.sensitivity(inp)
    assert grid[2, 2] == pytest.approx(val.dcf(inp).per_share)
    assert grid[0, 2] > grid[4, 2]  # lower discount rate, higher value


def test_monte_carlo_dcf_centres_on_the_point_estimate():
    inp = inputs(growth=0.08, terminal_growth=0.025, discount=0.09)
    sims = val.monte_carlo_dcf(inp, growth_sd=0.001, discount_sd=0.0001, tg_sd=0.0001)
    assert np.median(sims) == pytest.approx(val.dcf(inp).per_share, rel=0.01)


def improving_company():
    years = pd.to_datetime(["2021-12-31", "2022-12-31", "2023-12-31"])
    return pd.DataFrame(
        {
            "net_income": [5, 8, 12],
            "total_assets": [100, 102, 104],
            "operating_cash_flow": [7, 10, 15],
            "total_debt": [40, 35, 30],
            "current_assets": [30, 32, 36],
            "current_liabilities": [20, 20, 20],
            "gross_profit": [40, 44, 50],
            "revenue": [100, 105, 112],
            "diluted_shares": [10, 9.9, 9.8],
        },
        index=years,
    )


def test_piotroski_perfect_score():
    score, runnable, checks = val.piotroski(improving_company())
    assert (score, runnable) == (9, 9)
    assert all(c.passed for c in checks)


def test_piotroski_marks_missing_data_not_failed():
    df = improving_company().drop(columns=["current_assets"])
    score, runnable, checks = val.piotroski(df)
    assert runnable == 8
    assert [c for c in checks if c.passed is None][0].name == "Current ratio improved"


def test_ratios_and_quality_on_demo_fundamentals():
    f = sec.fundamentals("DEMO", "")
    r = val.ratios(f, price=50.0)
    assert r["market_cap"] == pytest.approx(50.0 * f.shares_outstanding)
    assert r["pe"] == pytest.approx(r["market_cap"] / f.ttm["net_income"])
    assert 0 < r["gross_margin"] < 1
    z, zone = val.altman_z(f, r["market_cap"])
    assert np.isfinite(z) and "zone" in zone
    inp = val.default_inputs(f, r)
    assert -0.05 <= inp.growth <= 0.15
    assert inp.base_fcf == pytest.approx(r["fcf"])
