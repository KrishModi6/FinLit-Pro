"""Option calculator: pricing identities, probabilities and the worth-it verdict."""

import math
from datetime import date, timedelta

import numpy as np
import pytest

from finlit_pro.analytics import options as opt
from finlit_pro.validation import ValidationError


def test_black_scholes_textbook_values():
    # Hull, S=100 K=100 T=1 r=5% vol=20%: call 10.45, put 5.57.
    assert opt.bsm("call", 100, 100, 1, 0.05, 0, 0.2)["price"] == pytest.approx(10.4506, abs=1e-4)
    assert opt.bsm("put", 100, 100, 1, 0.05, 0, 0.2)["price"] == pytest.approx(5.5735, abs=1e-4)


@pytest.mark.parametrize("s,k,t,r,q,vol", [(100, 90, 0.5, 0.04, 0.02, 0.3), (50, 60, 0.1, 0.0, 0.0, 0.6), (300, 300, 2, 0.05, 0.01, 0.15)])
def test_put_call_parity_with_dividends(s, k, t, r, q, vol):
    c = opt.bsm("call", s, k, t, r, q, vol)["price"]
    p = opt.bsm("put", s, k, t, r, q, vol)["price"]
    assert c - p == pytest.approx(s * math.exp(-q * t) - k * math.exp(-r * t), abs=1e-9)


def test_greeks_match_finite_differences():
    s, k, t, r, q, vol, h = 100.0, 105.0, 0.4, 0.03, 0.01, 0.25, 1e-3
    g = opt.bsm("call", s, k, t, r, q, vol)

    def price(**kw):
        args = {"s": s, "k": k, "t": t, "r": r, "q": q, "vol": vol} | kw
        return opt.bsm("call", args["s"], args["k"], args["t"], args["r"], args["q"], args["vol"])["price"]

    assert g["delta"] == pytest.approx((price(s=s + h) - price(s=s - h)) / (2 * h), rel=1e-5)
    assert g["gamma"] == pytest.approx((price(s=s + h) - 2 * price() + price(s=s - h)) / h**2, rel=1e-3)
    assert g["vega"] == pytest.approx((price(vol=vol + h) - price(vol=vol - h)) / (2 * h) / 100, rel=1e-5)
    assert g["rho"] == pytest.approx((price(r=r + h) - price(r=r - h)) / (2 * h) / 100, rel=1e-5)
    assert g["theta"] == pytest.approx(-(price(t=t + h) - price(t=t - h)) / (2 * h) / 365, rel=1e-4)


@pytest.mark.parametrize("kind", ["call", "put"])
def test_implied_volatility_round_trip(kind):
    premium = opt.bsm(kind, 120, 110, 0.3, 0.04, 0.005, 0.37)["price"]
    assert opt.implied_vol(kind, premium, 120, 110, 0.3, 0.04, 0.005) == pytest.approx(0.37, abs=1e-6)


def test_implied_volatility_rejects_impossible_premiums():
    assert opt.implied_vol("call", 5.0, 120, 100, 0.5, 0.04, 0) is None  # below intrinsic
    assert opt.implied_vol("call", 130.0, 120, 100, 0.5, 0.04, 0) is None  # above the share price


def test_lognormal_probabilities_and_expectations_agree_with_simulation():
    s, t, mu, vol = 100.0, 0.5, 0.08, 0.3
    rng = np.random.default_rng(1)
    st = s * np.exp((mu - 0.5 * vol**2) * t + vol * math.sqrt(t) * rng.standard_normal(1_000_000))
    assert opt.prob_above(s, 110, t, mu, vol) == pytest.approx((st > 110).mean(), abs=2e-3)
    assert opt.expected_payoff("call", s, 105, t, mu, vol) == pytest.approx(np.maximum(st - 105, 0).mean(), rel=5e-3)
    assert opt.expected_payoff("put", s, 95, t, mu, vol) == pytest.approx(np.maximum(95 - st, 0).mean(), rel=5e-3)
    # The median of a lognormal sits at s * exp((mu - vol^2/2) t).
    assert opt.prob_above(s, s * math.exp((mu - 0.5 * vol**2) * t), t, mu, vol) == pytest.approx(0.5)


def contract(kind="call", side="long", strike=100.0, premium=4.0, days=60):
    return opt.Contract(kind, side, strike, premium, date.today() + timedelta(days=days))


def test_market_implied_scenario_has_zero_expected_value():
    t, r, q = 60 / 365, 0.04, 0.01
    fair = opt.bsm("call", 100, 100, t, r, q, 0.3)["price"]
    res = opt.analyze(contract(premium=fair), 100, t, r, q, model_vol=0.25, model_return=0.08)
    market = res.scenarios[0]
    assert market.label == "Market-implied" and res.implied_vol == pytest.approx(0.3, abs=1e-6)
    assert market.expected_pnl == pytest.approx(0.0, abs=1e-6)


def test_verdicts_follow_expected_value_under_your_assumptions():
    t, r = 60 / 365, 0.04
    fair = opt.bsm("call", 100, 100, t, r, 0, 0.25)["price"]  # what your volatility says it is worth (at a risk-free drift)
    cheap = opt.analyze(contract(premium=fair * 0.7), 100, t, r, 0, 0.25, r)
    rich = opt.analyze(contract(premium=fair * 1.3), 100, t, r, 0, 0.25, r)
    near = opt.analyze(contract(premium=fair * 1.01), 100, t, r, 0, 0.25, r)
    assert cheap.verdict == "Worth it" and rich.verdict == "Not worth it" and near.verdict == "Marginal"
    # Selling the rich option is the mirror image.
    short = opt.analyze(contract(side="short", premium=fair * 1.3), 100, t, r, 0, 0.25, r)
    assert short.verdict == "Worth it"
    assert short.scenarios[-1].expected_pnl == pytest.approx(-rich.scenarios[-1].expected_pnl)


def test_probability_of_profit_and_payoff_shape():
    res = opt.analyze(contract(premium=3.0), 100, 60 / 365, 0.04, 0, 0.3, 0.04)
    mine = res.scenarios[-1]
    assert res.breakeven == 103.0 and res.max_loss == 3.0 and res.max_profit is None
    assert 0 < mine.prob_profit < mine.prob_itm < 1  # finishing above the strike is not enough to profit
    assert opt.position_pnl(res.contract, [90, 103, 110]).tolist() == [-3.0, 0.0, 7.0]
    put = opt.analyze(contract("put", premium=3.0), 100, 60 / 365, 0.04, 0, 0.3, 0.04)
    assert put.breakeven == 97.0 and put.max_profit == 97.0


def test_simulated_scenario_uses_the_given_distribution():
    terminal = np.array([90.0, 100.0, 110.0, 120.0])
    sc = opt.simulated_scenario("sim", contract(premium=5.0), terminal, t=0.0, r=0.0)
    assert sc.prob_itm == 0.5 and sc.prob_profit == 0.5
    assert sc.expected_pnl == pytest.approx((0 + 0 + 10 + 20) / 4 - 5)


@pytest.mark.parametrize("bad", [dict(premium=0.0), dict(premium=-1.0), dict(strike=0.0), dict(kind="straddle"), dict(side="both")])
def test_contract_inputs_are_validated(bad):
    with pytest.raises(ValidationError):
        opt.analyze(contract(**bad), 100, 0.2, 0.04, 0, 0.3, 0.05)


def test_expiry_must_be_in_the_future():
    with pytest.raises(ValidationError, match="future"):
        opt.years_to(date.today())
    with pytest.raises(ValidationError, match="Volatility"):
        opt.analyze(contract(), 100, 0.2, 0.04, 0, 0.0, 0.05)
