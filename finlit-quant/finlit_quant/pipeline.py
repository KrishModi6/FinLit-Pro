"""Run the whole analysis without the window: for notebooks, scripts and tests.

    from finlit_quant.pipeline import analyze
    a = analyze("AAPL", email="you@example.com")
    a.mc.stats["p50"], a.ratios["pe"], a.risk.metrics["beta"]

The desktop app does the same steps, but in parallel background jobs so the
window stays responsive.
"""

from __future__ import annotations

from finlit_quant.analysis import Analysis
from finlit_quant.analytics import montecarlo, predictor, risk, valuation
from finlit_quant.data import demo, sec, yahoo
from finlit_quant.data.models import DataError
from finlit_quant.validation import ValidationError


def analyze(
    symbol: str,
    email: str = "",
    mc_config: montecarlo.MCConfig | None = None,
    benchmark: str = "SPY",
    risk_years: float = 3,
    fallback_risk_free: float = 0.04,
) -> Analysis:
    a = Analysis(symbol.upper())
    a.history = yahoo.history(symbol)
    bench_symbol = "DEMO-MKT" if demo.is_demo(symbol) else benchmark
    try:
        a.benchmark = yahoo.history(bench_symbol) if bench_symbol != a.history.symbol else None
    except DataError:
        a.benchmark = None
    rf = None if demo.is_demo(symbol) else yahoo.risk_free_rate()
    a.risk_free, a.risk_free_live = (rf, True) if rf is not None else (fallback_risk_free, False)

    a.risk = risk.report(a.history.closes, a.benchmark.closes if a.benchmark else None, a.risk_free, risk_years, bench_symbol)

    cfg = mc_config or montecarlo.MCConfig()
    a.mc = montecarlo.simulate(a.history.closes, cfg, start_price=a.history.price)
    a.predictor = predictor.run(a.history.bars, a.mc.stats["median"], cfg.horizon_days)
    a.calibration = montecarlo.calibration(a.history.closes, cfg.horizon_days, cfg.lookback_days)

    try:
        a.fundamentals = sec.fundamentals(symbol, email)
    except DataError as exc:
        a.fundamentals_error = str(exc)
    if a.fundamentals:
        f, h = a.fundamentals, a.history
        sec.apply_splits(f, h.splits)
        a.ratios = valuation.ratios(f, h.price, h.trailing_dividends())
        a.piotroski = valuation.piotroski(f.annual)
        a.altman = valuation.altman_z(f, a.ratios.get("market_cap", float("nan")))
        a.dcf_inputs = valuation.default_inputs(f, a.ratios)
        try:
            a.dcf = valuation.dcf(a.dcf_inputs)
            a.implied_growth = valuation.reverse_dcf(a.dcf_inputs, h.price)
        except ValidationError:
            a.dcf = None
    try:
        a.news = yahoo.news(symbol)
    except DataError:
        a.news = []
    return a
