"""Regression tests for the second round of quant fixes: the shared debt policy, ROE over the trailing year,
financial-company detection, CAGR gaps, flows and balances never taken from an older year, strategy ruin in the
walk-forward test, the IC flag's sign, implied volatility bounds, the Monte Carlo drift under a volatility
override, the evaluation and Monte Carlo messages, the calibration reason and the pipeline's symbol.

Nothing here touches the network.
"""

from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from conftest import bars_from, gbm_closes

from finlit_pro import pipeline
from finlit_pro.analytics import montecarlo as mc
from finlit_pro.analytics import options as opt
from finlit_pro.analytics import valuation as val
from finlit_pro.data import demo, prices, sec, yahoo
from finlit_pro.data.models import Fundamentals
from finlit_pro.model import evaluation
from finlit_pro.model.evaluation import walk_forward
from finlit_pro.model.finlit_predictor import FinLitPredictor
from finlit_pro.model.interface import Forecast
from finlit_pro.validation import ValidationError

NAN = float("nan")
YEARS = pd.to_datetime(["2024-12-31", "2025-12-31"])


def company(annual=None, latest=None, ttm=None, debt_status="reported", year_ago=None, sic="Services-Prepackaged Software", latest_period="2026-06-30"):
    a = {
        "revenue": [800.0, 1000.0], "net_income": [80.0, 100.0], "operating_income": [100.0, 130.0], "gross_profit": [400.0, 500.0],
        "operating_cash_flow": [120.0, 150.0], "capex": [20.0, 30.0], "pretax_income": [100.0, 125.0], "income_tax": [20.0, 25.0],
        "interest_expense": [5.0, 6.0], "equity": [400.0, 600.0], "total_assets": [900.0, 1100.0], "cash": [50.0, 60.0],
        "short_investments": [10.0, 20.0], "total_debt": [200.0, 180.0], "current_assets": [300.0, 350.0], "current_liabilities": [150.0, 160.0],
        "total_liabilities": [500.0, 500.0], "retained_earnings": [200.0, 300.0], "diluted_shares": [10.0, 10.0],
    }
    a.update(annual or {})
    q = {"equity": 800.0, "total_assets": 1300.0, "cash": 70.0, "short_investments": 30.0, "total_debt": 180.0,
         "current_assets": 400.0, "current_liabilities": 170.0, "total_liabilities": 500.0, "retained_earnings": 380.0}
    q.update(latest or {})
    t = {"revenue": 1100.0, "net_income": 140.0, "operating_income": 150.0, "gross_profit": 550.0, "operating_cash_flow": 170.0,
         "capex": 35.0, "pretax_income": 175.0, "income_tax": 35.0, "interest_expense": 7.0}
    t.update(ttm or {})
    t = {k: v for k, v in t.items() if v is not None}
    return Fundamentals(cik=1, name="Test Co", annual=pd.DataFrame(a, index=YEARS), ttm=t, latest=q, latest_period=latest_period,
                        shares_outstanding=10.0, sic_description=sic, debt_status=debt_status,
                        year_ago=year_ago or {}, year_ago_period="2025-06-30" if year_ago else None)


DEBT_RATIOS = ("enterprise_value", "ev_ebit", "ev_sales", "net_debt", "debt_to_equity", "roic")


# ------------------------------------------------------------------ debt policy (valuation side)


def test_none_debt_status_is_zero_debt_even_with_interest_expense_and_no_note_from_valuation():
    # TTD's shape: no debt, a little interest expense. sec.py decides "none" and sets 0.0.
    f = company(latest={"total_debt": 0.0}, ttm={"interest_expense": 0.7}, debt_status="none")
    r = val.ratios(f, price=100.0)
    assert r["debt_to_equity"] == 0.0 and r["net_debt"] == pytest.approx(-100.0)
    assert r["enterprise_value"] == pytest.approx(1000.0 - 100.0) and np.isfinite(r["ev_ebit"])
    assert f.notes == []
    assert val.default_inputs(f, r).net_cash == pytest.approx(100.0)


def test_unknown_debt_status_leaves_every_debt_ratio_and_the_dcf_net_cash_blank():
    # Even if a stale debt figure sits in the latest dict, "unknown" means n/a.
    f = company(latest={"total_debt": NAN}, debt_status="unknown")
    r = val.ratios(f, price=100.0)
    for key in DEBT_RATIOS:
        assert np.isnan(r[key]), key
    assert f.notes == []
    inp = val.default_inputs(f, r)
    with pytest.raises(ValidationError, match="no standard XBRL total captures"):
        val.dcf(inp)


def test_reported_debt_is_used_as_given_without_interest_expense():
    # DASH's shape: convertible notes reported, no interest expense tagged. Not called debt-free.
    f = company(latest={"total_debt": 2727.0}, ttm={"interest_expense": None}, annual={"interest_expense": [NAN, NAN]})
    r = val.ratios(f, price=100.0)
    assert r["debt_to_equity"] == pytest.approx(2727.0 / 800.0)
    assert f.notes == []


def test_valuation_no_longer_carries_debt_notes():
    assert not hasattr(val, "NO_DEBT_NOTE") and not hasattr(val, "DEBT_UNKNOWN_NOTE")


# ------------------------------------------------------------------ flows and balances: never an older year


def test_interest_coverage_never_uses_an_older_years_interest_expense():
    # PLTR's 759x: no TTM interest, none in the last fiscal year, some years ago.
    f = company(annual={"interest_expense": [3.5, NAN]}, ttm={"interest_expense": None})
    assert np.isnan(val.ratios(f, price=100.0)["interest_coverage"])
    f = company(ttm={"interest_expense": None})  # the last fiscal year reports it: used
    assert val.ratios(f, price=100.0)["interest_coverage"] == pytest.approx(150.0 / 6.0)


def test_balance_falls_back_to_the_last_fiscal_year_only():
    f = company(latest={"current_assets": NAN}, annual={"current_assets": [300.0, NAN]})
    assert np.isnan(val.balance(f, "current_assets"))
    assert val.balance(company(latest={"current_assets": NAN}), "current_assets") == 350.0


# ------------------------------------------------------------------ ROE and ROA over the trailing year


def test_roe_and_roa_average_the_latest_and_year_ago_balance_sheets():
    # NVDA's shape: equity more than doubled over the trailing year.
    f = company(latest={"equity": 229.0, "total_assets": 300.0}, ttm={"net_income": 193.0},
                year_ago={"equity": 100.1, "total_assets": 140.0})
    r = val.ratios(f, price=100.0)
    assert r["roe"] == pytest.approx(193.0 / ((229.0 + 100.1) / 2))  # 117.3%, yfinance's 117.2%
    assert r["roa"] == pytest.approx(193.0 / ((300.0 + 140.0) / 2))


def test_roe_without_a_year_ago_balance_sheet_keeps_the_previous_rule():
    r = val.ratios(company(), price=100.0)
    assert r["roe"] == pytest.approx(140.0 / ((800.0 + 600.0) / 2))


# ------------------------------------------------------------------ financial companies


@pytest.mark.parametrize(
    "sic,expected",
    [("Security & Commodity Brokers, Dealers, Exchanges & Services", True),  # CME, ICE, NDAQ
     ("Security Brokers, Dealers & Flotation Companies", True),  # GS, SCHW
     ("Commodity Contracts Brokers & Dealers", True), ("Loan Brokers", True), ("Finance Services", True),  # AXP, COIN
     ("Personal Credit Institutions", True), ("Mortgage Bankers & Loan Correspondents", True), ("State Commercial Banks", True),
     ("Insurance Agents, Brokers & Service", False),  # AON, AJG, WTW
     ("Services-Consumer Credit Reporting, Collection Agencies", False),  # SPGI, EFX
     ("Retail-Auto Dealers & Gasoline Stations", False), ("Real Estate Investment Trusts", False), ("Hospital & Medical Service Plans", False)],
)
def test_is_financial_covers_brokers_exchanges_and_lenders(sic, expected):
    assert val.is_financial(sic) is expected


def test_altman_and_piotroski_use_the_same_financial_test():
    aon = company(sic="Insurance Agents, Brokers & Service")
    z, zone = val.altman_z(aon, 1000.0)
    assert np.isfinite(z) and "zone" in zone
    assert val.piotroski(aon.annual, aon.sic_description)[2][0].name != val.NOT_MEANINGFUL
    cme = company(sic="Security & Commodity Brokers, Dealers, Exchanges & Services")
    assert val.altman_z(cme, 1000.0) == (pytest.approx(NAN, nan_ok=True), val.NOT_MEANINGFUL)
    assert val.piotroski(cme.annual, cme.sic_description)[2][0].name == val.NOT_MEANINGFUL
    reit = company(sic="Real Estate Investment Trusts")
    assert val.altman_z(reit, 1000.0)[1] == val.NOT_MEANINGFUL_REIT


def test_financial_wording_names_brokers_and_lenders():
    f = company(sic="Finance Services")
    r = val.ratios(f, price=100.0)
    assert f.notes == [val.FINANCIAL_NOTE.format(sic="Finance Services")]
    assert "financial companies (banks, insurers, brokers and lenders)" in f.notes[0] and "bank or insurer" not in f.notes[0]
    with pytest.raises(ValidationError, match=r"financial companies \(banks, insurers, brokers and lenders\)"):
        val.dcf(val.default_inputs(f, r))


# ------------------------------------------------------------------ CAGR


def growth_series(years=range(2016, 2027), rate=0.10):
    index = pd.to_datetime([f"{y}-12-31" for y in years])
    return pd.Series([100.0 * (1 + rate) ** i for i in range(len(index))], index=index)


def test_cagr_counts_fiscal_years_not_reported_values():
    s = growth_series()
    s.iloc[-4] = NAN  # a gap inside the five years
    assert val.cagr(s, 5) == pytest.approx(0.10)
    s = growth_series()
    s.iloc[-6] = NAN  # the start year itself is missing: NaN rather than a six-year span
    assert np.isnan(val.cagr(s, 5))
    s = growth_series()
    s.iloc[-1] = NAN  # the latest year missing: five real years to the last reported one
    assert val.cagr(s, 5) == pytest.approx(0.10)


def test_cagr_is_nan_when_a_fiscal_year_row_is_missing_altogether():
    s = growth_series().drop(pd.Timestamp("2023-12-31"))
    assert np.isnan(val.cagr(s, 5))


# ------------------------------------------------------------------ walk-forward evaluation


class Model:
    """A test model; `fn(history, full_bars)` gives the expected return of each forecast."""

    key, name, version, description = "test", "Test model", "0", "test"
    horizons, simulations = (5, 10, 20), (10,)
    bullish, bearish = ("BUY",), ("SELL",)
    lookback_calendar_days = 60

    def __init__(self, fn, verdict="SELL"):
        self.fn, self.verdict = fn, verdict

    def input_spec(self, horizon, simulations):
        return []

    def predict(self, bars, horizon, simulations, seed=42):
        p = float(bars["adjclose"].iloc[-1])
        ret = self.fn(bars, horizon)
        return Forecast("Test", "0", bars.index[-1], horizon, p, p * (1 + ret), self.verdict, -2, (-2, 2), {10: p * 0.9, 90: p * 1.1}, 0.4)


def test_short_strategy_wiped_out_stays_at_zero():
    # Price 10 -> 25 in one period, then 20: an always-SELL short loses everything in the jump (a -150% period).
    closes = pd.Series(np.r_[np.full(90, 10.0), np.full(40, 25.0), np.full(40, 20.0)], index=pd.bdate_range("2020-01-01", periods=170))
    ev = walk_forward(Model(lambda b, h: -0.01), bars_from(closes), 5)
    eq = ev.equity["Long/short"].to_numpy()
    assert eq.min() >= 0 and eq[-1] == 0.0
    ruin = int(np.flatnonzero(eq == 0)[0])
    assert (eq[ruin:] == 0).all()
    assert ev.metric("Long/short CAGR").value == -1.0 and ev.metric("Long/short CAGR").display == "-100.0%"
    assert ev.metric("Long/short max drawdown").value == pytest.approx(1.0)
    assert any(n.startswith("Long/short: the strategy lost all its capital") for n in ev.notes)


def test_max_drawdown_counts_a_loss_in_the_first_period():
    assert evaluation._max_drawdown(np.array([0.0, 0.0])) == pytest.approx(1.0)
    assert evaluation._max_drawdown(np.array([0.5, 1.0])) == pytest.approx(0.5)


def test_walk_forward_with_no_forecast_raises_its_message_not_a_key_error():
    def refuse(bars, h):
        raise ValueError("no")

    with pytest.raises(ValueError, match="produced a forecast"):
        walk_forward(Model(refuse), bars_from(gbm_closes(400)), 5)


def test_significantly_negative_ic_is_flagged():
    closes = gbm_closes(800, seed=9)
    full = closes.to_numpy()

    def backwards(bars, h):  # peeks at the future only to build a model that ranks outcomes backwards
        i = len(bars) - 1
        return -(full[i + h] / full[i] - 1) if i + h < len(full) else 0.0

    ev = walk_forward(Model(backwards), bars_from(closes), 5)
    ic = ev.metric("Information coefficient")
    assert ic.value < -0.5 and ic.flag == "negative: forecasts rank outcomes backwards"


def test_shorter_horizon_advice_uses_only_the_models_horizons():
    model = FinLitPredictor("original")
    b = bars_from(gbm_closes(560, seed=4))
    with pytest.raises(ValueError) as info:
        walk_forward(model, b, 30)
    message = str(info.value)
    # The DEMO-like case was told "4 days", which the model does not offer.
    assert "a shorter horizon would not fit 8 either" in message or any(f"horizon of {h} days" in message for h in model.horizons)
    assert "4 days" not in message


def test_young_listing_message_says_test_forecast_and_reads_well():
    model = FinLitPredictor("original")
    for n, span in ((5, "less than a month"), (25, "about 1 month"), (520, "just under 2 years")):
        b = bars_from(gbm_closes(n, seed=4))
        with pytest.raises(ValueError) as info:
            walk_forward(model, b, 30)
        message = str(info.value)
        assert "before its first test forecast" in message
        assert f"({span}, {(b.index[-1] - b.index[0]).days} calendar days)" in message
        assert "about 0 months" not in message and "about 1 months" not in message


def test_span_wording():
    assert evaluation._span(10) == "less than a month"
    assert evaluation._span(31) == "about 1 month"
    assert evaluation._span(456) == "about 15 months"
    assert evaluation._span(730) == "about 2 years"


# ------------------------------------------------------------------ the FinLit AI Predictor on a flat price


def flat_bars(n=300):
    return bars_from(pd.Series(1.0, index=pd.bdate_range("2023-01-02", periods=n)))


def test_v10_refuses_a_constant_price_with_a_value_error():
    with pytest.raises(ValueError, match="RSI is undefined"):
        FinLitPredictor("original").predict(flat_bars(), 30, 500)
    assert FinLitPredictor("corrected").predict(flat_bars(), 30, 500).verdict  # v1.1's Wilder RSI is defined


def test_walk_forward_on_a_constant_price_gives_a_message():
    with pytest.raises(ValueError, match="produced a forecast"):
        walk_forward(FinLitPredictor("original"), flat_bars(1500), 30)


# ------------------------------------------------------------------ options


def test_implied_vol_is_none_when_no_volatility_in_range_reaches_the_premium():
    assert opt.implied_vol("call", 30.0, 100, 100, 7 / 365, 0.04, 0.0) is None  # 500% gives 27.11
    assert opt.implied_vol("call", 95.0, 100, 100, 1.0, 0.10, 0.10) is None  # above S e^(-qt) = 90.48
    assert opt.implied_vol("put", 95.0, 100, 100, 1.0, 0.10, 0.10) is None  # above K e^(-rt) = 90.48
    assert opt.implied_vol("call", 2.0, 100, 100, 7 / 365, 0.04, 0.0) == pytest.approx(0.3552, abs=1e-3)


def test_analyze_drops_the_market_implied_row_for_an_impossible_premium():
    c = opt.Contract("call", "long", 100.0, 30.0, date.today() + timedelta(days=7))
    res = opt.analyze(c, 100.0, 7 / 365, 0.04, 0.0, 0.3, 0.08)
    assert res.implied_vol is None and [s.label for s in res.scenarios] == ["Your assumptions"]
    assert res.notes[0].startswith("No implied volatility reproduces this premium")


# ------------------------------------------------------------------ Monte Carlo


def test_volatility_override_keeps_the_historical_arithmetic_return():
    closes = gbm_closes(1500, mu=0.0006, sigma=0.016, seed=2)
    base = mc.estimate(closes, mc.MCConfig(model="gbm"))
    for vol in (0.5, 1.0):
        est = mc.estimate(closes, mc.MCConfig(model="gbm", vol_override=vol))
        assert est.drift_annual == pytest.approx(base.drift_annual, abs=1e-9)
        assert est.mu < base.mu  # the median falls as the spread widens
    assert base.mu == pytest.approx(base.hist_mu)  # no override: the log drift as is


def test_short_history_message_does_not_advise_shortening_the_lookback():
    with pytest.raises(ValidationError) as info:
        mc.simulate(gbm_closes(40), mc.MCConfig())
    assert "shorten" not in str(info.value) and "21 more trading sessions" in str(info.value)
    with pytest.raises(ValidationError, match="Lengthen the lookback"):
        mc.simulate(gbm_closes(500), mc.MCConfig(lookback_days=30))


def test_calibration_reason_matches_when_calibration_cannot_run():
    closes = gbm_closes(900)
    assert mc.calibration(closes, 252, 756) is None
    reason = mc.calibration_reason(closes, 252, 756)
    needed = 756 + 252 + 1 + 63 * 9
    assert f"{needed} sessions in all" in reason and f"after about {needed - 900} more trading sessions" in reason
    long = gbm_closes(needed)
    assert mc.calibration(long, 252, 756) is not None and mc.calibration(gbm_closes(needed - 1), 252, 756) is None


# ------------------------------------------------------------------ pipeline


def test_pipeline_records_the_calibration_reason(monkeypatch):
    real = prices.load_history
    monkeypatch.setattr(prices, "load_history", lambda symbol, force=False: replace(h := real(symbol, force=force), bars=h.bars.iloc[-400:]) if symbol == "DEMO" else real(symbol, force=force))
    ws = pipeline.load("DEMO", evaluate=False, read_filings=False, simulations=50)
    assert ws.mc is not None and ws.mc_error is None
    assert ws.calibration is None and ws.calibration_error.startswith("The calibration check needs")


def test_pipeline_adopts_the_yahoo_spelling_of_the_symbol(monkeypatch):
    real = prices.load_history
    asked = {}

    def load(symbol, force=False):
        h = real("DEMO-MKT" if symbol == "SPY" else "DEMO", force=force)
        return replace(h, symbol="BRK-B") if symbol == "BRK.B" else h

    def fundamentals(symbol, email):
        asked["sec"] = symbol
        return demo.fundamentals("DEMO")

    monkeypatch.setattr(prices, "load_history", load)
    monkeypatch.setattr(yahoo, "risk_free_rate", lambda: None)
    monkeypatch.setattr(sec, "fundamentals", fundamentals)
    ws = pipeline.load("brk.b", email="test@example.com", evaluate=False, read_filings=False, simulations=50)
    assert ws.symbol == "BRK-B" == ws.history.symbol and asked["sec"] == "BRK-B"  # (DEMO prices: no headlines are asked for)


def test_algorithms_doc_describes_the_regression_step_as_the_code_does():
    text = (Path(__file__).resolve().parents[1] / "docs" / "ALGORITHMS.md").read_text(encoding="utf-8")
    assert "evaluated h steps past the last point (x = 119 + h)" in text and "h - 1 steps" not in text
