"""Simulated data for the DEMO tickers, so the app works with no network.

Nothing here describes a real company. The UI labels every DEMO view as
simulated. The prices are a seeded random walk with fat tails, a bear market
and a few jump days, which gives every tool something realistic to chew on;
DEMO-MKT is a matching "market" so the risk tab has a benchmark.
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

from finlit_pro.data.models import DEMO, Filing, Fundamentals, PriceHistory, Source

DEMO_TICKERS = {"DEMO", "DEMO-MKT"}
DEMO_NAME = "Demo Robotics Corp (simulated data)"


def is_demo(symbol: str) -> bool:
    return (symbol or "").upper() in DEMO_TICKERS


def _paths(years: int = 10, seed: int = 28) -> tuple[pd.DatetimeIndex, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    end = pd.Timestamp(datetime.now().date())
    index = pd.bdate_range(end=end, periods=252 * years)
    n = len(index)

    # Market: 8% a year, 16% vol, with a 2-year stretch that loses money.
    mkt_mu = np.full(n, 0.08 / 252)
    mkt_mu[int(n * 0.55) : int(n * 0.62)] = -0.35 / 252
    mkt_sigma = np.full(n, 0.16 / np.sqrt(252))
    mkt_sigma[int(n * 0.55) : int(n * 0.62)] *= 1.8
    t = rng.standard_t(4, n) / np.sqrt(2)  # unit variance at df=4
    mkt = mkt_mu + mkt_sigma * t

    # Stock: beta 1.3 to the market plus its own noise and a handful of
    # earnings-day jumps in both directions.
    idio = rng.standard_t(4, n) / np.sqrt(2) * (0.24 / np.sqrt(252))
    jumps = np.zeros(n)
    for day in rng.choice(n, 14, replace=False):
        jumps[day] = rng.choice([-1, 1]) * rng.uniform(0.06, 0.16)
    stock = 0.0002 + 1.3 * mkt + idio + jumps
    return index, stock, mkt


def _bars(index: pd.DatetimeIndex, log_returns: np.ndarray, start: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = start * np.exp(np.cumsum(log_returns))
    prev = np.concatenate([[start], close[:-1]])
    open_ = prev * np.exp(rng.normal(0, 0.004, len(close)))
    spread = np.abs(rng.normal(0, 0.012, len(close)))
    high = np.maximum(open_, close) * (1 + spread)
    low = np.minimum(open_, close) * (1 - spread * rng.uniform(0.3, 1, len(close)))
    volume = (2.5e6 * np.exp(rng.normal(0, 0.35, len(close))) * (1 + 25 * np.abs(log_returns))).round()
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "adjclose": close, "volume": volume},
        index=index,
    )


def history(symbol: str) -> PriceHistory:
    index, stock, mkt = _paths()
    if symbol.upper() == "DEMO-MKT":
        bars, name = _bars(index, mkt, 300.0, 11), "Demo Market Index (simulated data)"
    else:
        bars, name = _bars(index, stock, 18.0, 12), DEMO_NAME
    quarters = pd.date_range(index[0], index[-1], freq="QE")
    divs = pd.Series(0.12, index=[index[index.get_indexer([q], method="nearest")[0]] for q in quarters])
    return PriceHistory(
        symbol=symbol.upper(),
        name=name,
        currency="USD",
        exchange="Simulated",
        instrument_type="EQUITY",
        price=float(bars["close"].iloc[-1]),
        previous_close=float(bars["close"].iloc[-2]),
        bars=bars,
        source=Source("Simulated data (DEMO)", "", datetime.now(), str(bars.index[-1].date()), DEMO, "Seeded random walk; not a real security"),
        dividends=divs if symbol.upper() == "DEMO" else pd.Series(dtype=float),
    )


def fundamentals(symbol: str) -> Fundamentals:
    years = pd.to_datetime([f"{y}-12-31" for y in range(datetime.now().year - 10, datetime.now().year)])
    n = len(years)
    growth = np.linspace(0.24, 0.09, n)
    revenue = 1.2e9 * np.cumprod(1 + growth)
    gross_margin = np.linspace(0.52, 0.58, n)
    op_margin = np.linspace(0.08, 0.19, n)
    net_margin = op_margin * 0.78
    shares = np.linspace(410e6, 395e6, n)
    equity = np.cumsum(revenue * net_margin * 0.6) + 1.5e9
    annual = pd.DataFrame(
        {
            "revenue": revenue,
            "cost_of_revenue": revenue * (1 - gross_margin),
            "gross_profit": revenue * gross_margin,
            "operating_income": revenue * op_margin,
            "pretax_income": revenue * op_margin * 0.97,
            "income_tax": revenue * op_margin * 0.97 * 0.2,
            "net_income": revenue * net_margin,
            "eps_diluted": revenue * net_margin / shares,
            "operating_cash_flow": revenue * (net_margin + 0.06),
            "capex": revenue * 0.05,
            "rnd": revenue * 0.11,
            "sbc": revenue * 0.03,
            "interest_expense": np.full(n, 4.5e7),
            "dividends_paid": shares * 0.48,
            "buybacks": np.linspace(0, 6e8, n),
            "cash": revenue * 0.35,
            "short_investments": revenue * 0.1,
            "current_assets": revenue * 0.75,
            "total_assets": revenue * 1.6,
            "current_liabilities": revenue * 0.38,
            "total_liabilities": revenue * 1.6 - equity,
            "equity": equity,
            "retained_earnings": equity * 0.7,
            "total_debt": np.full(n, 1.1e9),
            "shares_outstanding": shares,
            "diluted_shares": shares * 1.01,
        },
        index=years,
    )
    latest = annual.iloc[-1].to_dict()
    ttm = {k: float(v) * 1.03 for k, v in latest.items() if k not in ("shares_outstanding", "diluted_shares")}
    return Fundamentals(
        cik=0,
        name=DEMO_NAME,
        annual=annual,
        ttm=ttm,
        latest={k: float(v) for k, v in latest.items()},
        latest_period=str(years[-1].date()),
        shares_outstanding=float(shares[-1]),
        sic_description="Simulated: industrial robotics",
        fiscal_year_end="1231",
        exchanges=["Simulated"],
        sources=[Source("Simulated fundamentals (DEMO)", "", datetime.now(), str(years[-1].date()), DEMO, "Not a real company")],
        filings=[
            Filing("10-K", str(years[-1].date()), str(years[-1].date()), "Simulated annual report (no document)", ""),
        ],
    )
