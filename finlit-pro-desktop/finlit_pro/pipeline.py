"""The full analysis without the window, for scripts, notebooks and tests.

    from finlit_pro.pipeline import load
    ws = load("AAPL", email="you@example.com")
    ws.forecast.verdict, ws.evaluation.metric("Skill vs no-change").display

The desktop app runs the same steps as parallel background jobs.
"""

from __future__ import annotations

from finlit_pro.analytics import montecarlo, risk, valuation
from finlit_pro.data import demo, filings, prices, sec, yahoo
from finlit_pro.data.models import DataError
from finlit_pro.model import registry
from finlit_pro.model.evaluation import walk_forward
from finlit_pro.validation import ValidationError
from finlit_pro.workspace import Workspace


def load_prices(ws: Workspace, benchmark: str = "SPY", fallback_rf: float = 0.04, force: bool = False) -> None:
    ws.history = prices.load_history(ws.symbol, force=force)
    bench = "DEMO-MKT" if demo.is_demo(ws.symbol) else benchmark
    try:
        ws.benchmark = prices.load_history(bench) if bench != ws.history.symbol else None
    except (DataError, ValidationError):
        ws.benchmark = None
    rf = None if demo.is_demo(ws.symbol) else yahoo.risk_free_rate()
    if rf:
        ws.risk_free, ws.risk_free_source = rf
    else:
        ws.risk_free, ws.risk_free_source = fallback_rf, None


def compute_risk(ws: Workspace, years: float = 3) -> None:
    ws.risk = risk.report(ws.history.closes, ws.benchmark.closes if ws.benchmark else None, ws.risk_free, years, ws.benchmark.symbol if ws.benchmark else None)


def compute_fundamentals(ws: Workspace) -> None:
    f, h = ws.fundamentals, ws.history
    sec.apply_splits(f, h.splits)
    ws.ratios = valuation.ratios(f, h.price, h.trailing_dividends())
    ws.piotroski = valuation.piotroski(f.annual)
    ws.altman = valuation.altman_z(f, ws.ratios.get("market_cap", float("nan")))
    ws.dcf_inputs = valuation.default_inputs(f, ws.ratios)
    try:
        ws.dcf = valuation.dcf(ws.dcf_inputs)
        ws.implied_growth = valuation.reverse_dcf(ws.dcf_inputs, h.price)
    except ValidationError:
        ws.dcf, ws.implied_growth = None, None


def load(
    symbol: str,
    email: str = "",
    model_key: str = registry.DEFAULT,
    horizon: int = 30,
    simulations: int = 1000,
    evaluate: bool = True,
    mc_config: montecarlo.MCConfig | None = None,
    read_filings: bool = True,
    filing_chars: int = 40_000,
) -> Workspace:
    ws = Workspace(symbol.upper())
    load_prices(ws)
    compute_risk(ws)
    model = registry.get(model_key)
    ws.forecast = model.predict(ws.history.bars, horizon, simulations)
    if evaluate:
        try:
            ws.evaluation = walk_forward(model, ws.history.bars, horizon)
        except ValueError:
            ws.evaluation = None
    cfg = mc_config or montecarlo.MCConfig()
    ws.mc = montecarlo.simulate(ws.history.closes, cfg, start_price=ws.history.price)
    ws.calibration = montecarlo.calibration(ws.history.closes, cfg.horizon_days, cfg.lookback_days)
    try:
        ws.fundamentals = sec.fundamentals(symbol, email)
    except (DataError, ValidationError) as exc:
        ws.fundamentals_error = str(exc)
    if ws.fundamentals:
        compute_fundamentals(ws)
        if read_filings and not ws.is_demo:
            ws.filing_texts, ws.filing_problems = filings.latest_reports(ws.fundamentals, email, filing_chars)
    if not ws.is_demo:
        try:
            ws.news = yahoo.news(symbol)
        except DataError:
            ws.news = []
    return ws
