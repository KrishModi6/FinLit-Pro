"""Regression tests for the ratio, financial-company, evaluation and pipeline fixes found by live testing.

Every Fundamentals here is built by hand, so nothing touches the network.
"""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from conftest import bars_from, gbm_closes

from finlit_pro import pipeline
from finlit_pro.analytics import valuation as val
from finlit_pro.data import prices, sec
from finlit_pro.data.models import Fundamentals
from finlit_pro.model.evaluation import walk_forward
from finlit_pro.model.interface import Forecast
from finlit_pro.validation import ValidationError

NAN = float("nan")
YEARS = pd.to_datetime(["2024-12-31", "2025-12-31"])


def company(annual=None, latest=None, ttm=None, latest_period="2026-06-30", sic="Services-Prepackaged Software", shares=10.0, debt_status="reported"):
    """Two fiscal years and, by default, a 10-Q six months after the last fiscal year end."""
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
                        shares_outstanding=shares, sic_description=sic, debt_status=debt_status)


# ------------------------------------------------------------------ ROE and ROA periods


def test_roe_and_roa_pair_ttm_income_with_the_latest_quarter_and_fiscal_year_end():
    r = val.ratios(company(), price=100.0)
    assert r["roe"] == pytest.approx(140.0 / ((800.0 + 600.0) / 2))
    assert r["roa"] == pytest.approx(140.0 / ((1300.0 + 1100.0) / 2))


def test_roe_and_roa_use_the_fiscal_year_when_no_quarter_followed_it():
    f = company(latest={"equity": 600.0, "total_assets": 1100.0}, ttm={"net_income": 100.0}, latest_period="2025-12-31")
    r = val.ratios(f, price=100.0)
    assert r["roe"] == pytest.approx(100.0 / ((600.0 + 400.0) / 2))
    assert r["roa"] == pytest.approx(100.0 / ((1100.0 + 900.0) / 2))


def test_roe_falls_back_to_the_fiscal_year_when_ttm_income_is_missing():
    r = val.ratios(company(ttm={"net_income": None}), price=100.0)
    assert r["roe"] == pytest.approx(100.0 / 500.0)


# ------------------------------------------------------------------ ROIC and debt


def test_roic_is_nan_with_a_note_when_cash_exceeds_most_of_the_capital():
    # PLTR's shape: equity 9.77B, cash and short-term investments 9.41B, and sec.py found no debt of any kind.
    # Current Version (debt policy): sec.py decides "none" and sets 0.0; valuation uses it and adds no debt note.
    f = company(annual={"total_debt": [0.0, NAN], "interest_expense": [3.5, NAN]},
                latest={"equity": 9774.0, "cash": 2030.0, "short_investments": 7379.0, "total_debt": 0.0}, ttm={"interest_expense": None},
                debt_status="none")
    r = val.ratios(f, price=100.0)
    assert np.isnan(r["roic"])
    assert any(n.startswith("ROIC is not shown") and "under 10%" in n for n in f.notes)
    assert not any("debt is reported" in n.lower() for n in f.notes)
    assert r["debt_to_equity"] == 0.0 and r["net_debt"] == pytest.approx(-9409.0)
    assert r["enterprise_value"] == pytest.approx(1000.0 - 9409.0)


def test_roic_on_debt_plus_equity_less_cash_otherwise():
    f = company()
    r = val.ratios(f, price=100.0)
    assert r["roic"] == pytest.approx(150.0 * (1 - 0.2) / (180.0 + 800.0 - 100.0))
    assert not any("ROIC" in n or "debt" in n.lower() for n in f.notes)


def test_unknown_debt_leaves_debt_ratios_blank():
    # Current Version (debt policy): "unknown" comes from sec.py with its own note; valuation adds none.
    f = company(annual={"total_debt": [NAN, NAN]}, latest={"total_debt": NAN}, debt_status="unknown")
    r = val.ratios(f, price=100.0)
    for key in ("enterprise_value", "ev_ebit", "ev_sales", "net_debt", "debt_to_equity", "roic"):
        assert np.isnan(r[key]), key
    assert np.isfinite(r["pe"]) and np.isfinite(r["roe"])
    assert f.notes == []
    inp = val.default_inputs(f, r)
    assert np.isnan(inp.net_cash)
    with pytest.raises(ValidationError, match="Net cash is unknown"):
        val.dcf(inp)
    assert val.dcf(replace(inp, net_cash=-80.0)).per_share > 0  # the user can enter it


# ------------------------------------------------------------------ banks and insurers


@pytest.mark.parametrize(
    "sic,expected",
    [("National Commercial Banks", True), ("Savings Institution, Federally Chartered", True), ("Fire, Marine & Casualty Insurance", True),
     ("Security Brokers, Dealers & Flotation Companies", True), ("Finance Services", True), ("Insurance Agents, Brokers & Service", False),
     ("Services-Prepackaged Software", False), ("Semiconductors & Related Devices", False), (None, False)],
)
def test_is_financial(sic, expected):
    assert val.is_financial(sic) is expected


def test_bank_cash_flow_and_leverage_measures_are_not_shown():
    f = company(sic="National Commercial Banks", annual={"current_assets": [NAN, NAN]}, latest={"current_assets": NAN, "total_debt": NAN})
    r = val.ratios(f, price=100.0, dividends_ttm=3.0)
    val.ratios(f, price=101.0, dividends_ttm=3.0)  # recomputed when the price moves: still one note
    for key in ("fcf", "fcf_yield", "enterprise_value", "ev_ebit", "net_debt", "debt_to_equity", "roic"):
        assert np.isnan(r[key]), key
    for key in ("pe", "pb", "roe", "dividend_yield"):
        assert np.isfinite(r[key]) and r[key] > 0, key
    assert len(f.notes) == 1 and "financial companies (banks, insurers, brokers and lenders)" in f.notes[0] and "National Commercial Banks" in f.notes[0]

    with pytest.raises(ValidationError, match="does not value financial companies"):
        val.dcf(val.default_inputs(f, r))
    score, runnable, checks = val.piotroski(f.annual, f.sic_description)
    assert (score, runnable) == (0, 0) and checks[0].name == val.NOT_MEANINGFUL and checks[0].passed is None
    # The industry is checked before the missing current assets.
    z, zone = val.altman_z(f, r["market_cap"])
    assert np.isnan(z) and zone == val.NOT_MEANINGFUL


def test_insurer_with_full_data_is_still_not_scored():
    f = company(sic="Fire, Marine & Casualty Insurance")
    z, zone = val.altman_z(f, 1000.0)
    assert np.isnan(z) and zone == val.NOT_MEANINGFUL
    assert val.piotroski(f.annual, f.sic_description)[1] == 0


def test_operating_company_keeps_its_scores_and_dcf():
    f = company()
    r = val.ratios(f, price=100.0)
    z, zone = val.altman_z(f, r["market_cap"])
    assert np.isfinite(z) and "zone" in zone
    inp = val.default_inputs(f, r)
    assert inp.refusal == "" and inp.net_cash == pytest.approx(100.0 - 180.0)
    assert val.dcf(inp).per_share > 0


# ------------------------------------------------------------------ evaluation messages


class Stub:
    key, name, version, description = "stub", "Stub model", "0", "test"
    horizons, simulations = (3, 5), (10,)  # only offered horizons are suggested
    bullish, bearish = ("BUY",), ("SELL",)

    def __init__(self, lookback_calendar_days):
        self.lookback_calendar_days = lookback_calendar_days

    def input_spec(self, horizon, simulations):
        return []

    def predict(self, bars, horizon, simulations, seed=42):
        p = float(bars["adjclose"].iloc[-1])
        return Forecast("Stub", "0", bars.index[-1], horizon, p, p * 1.01, "BUY", 1, (-1, 1), {10: p * 0.9, 90: p * 1.1}, 0.6)


def bars(n):
    return bars_from(gbm_closes(n, seed=5))


@pytest.mark.parametrize("horizon", [30, 7])
def test_young_listing_is_told_when_the_first_test_becomes_possible(horizon):
    b = bars(300)  # about 14 months, against a two-year lookback
    with pytest.raises(ValueError) as info:
        walk_forward(Stub(730), b, horizon)
    message = str(info.value)
    first_test = (b.index[0] + pd.Timedelta(days=730) + pd.offsets.BDay(horizon)).date()
    assert "needs about 2 years of history (730 calendar days)" in message
    assert f"This history has 300 sessions from {b.index[0].date()}" in message
    assert f"first test becomes possible around {first_test}" in message
    assert "shorter" not in message and "choose a horizon" not in message


def test_shorter_horizon_advice_only_when_it_would_fit_eight():
    with pytest.raises(ValueError, match="choose a horizon of 3 days or shorter"):
        walk_forward(Stub(60), bars(70), 5)
    with pytest.raises(ValueError) as info:
        walk_forward(Stub(60), bars(48), 5)
    assert "a shorter horizon would not fit 8 either" in str(info.value) and "choose a horizon" not in str(info.value)


# ------------------------------------------------------------------ pipeline.load


def test_load_cleans_the_symbol():
    ws = pipeline.load(" demo ", evaluate=False, read_filings=False, simulations=50)
    assert ws.symbol == "DEMO" == ws.history.symbol


def test_load_survives_a_listing_too_short_for_risk_and_the_model(monkeypatch):
    real = prices.load_history

    def short(symbol, force=False):
        h = real(symbol, force=force)
        return replace(h, bars=h.bars.iloc[-40:]) if h.symbol == "DEMO" else h

    monkeypatch.setattr(prices, "load_history", short)
    ws = pipeline.load("DEMO", read_filings=False, simulations=50)
    assert len(ws.history.bars) == 40 and ws.fundamentals is not None and ws.ratios
    assert ws.risk is None and ws.risk_error.startswith("This listing has 40 sessions; risk statistics need at least 60.")
    assert ws.forecast is None and "at least 60" in ws.forecast_error
    assert ws.evaluation is None and "first test becomes possible" in ws.evaluation_error
    assert ws.mc is None and ws.mc_error


def test_load_skips_sec_for_a_fund(monkeypatch):
    real = prices.load_history
    monkeypatch.setattr(prices, "load_history", lambda symbol, force=False: replace(real(symbol, force=force), instrument_type="ETF"))

    def no_sec(*args, **kwargs):
        raise AssertionError("SEC must not be asked about a fund")

    monkeypatch.setattr(sec, "fundamentals", no_sec)
    ws = pipeline.load("DEMO", evaluate=False, read_filings=False, simulations=50)
    assert ws.fundamentals is None and ws.fundamentals_error == sec.not_a_company("ETF", ws.history.name)
    assert ws.forecast is not None and ws.risk is not None
