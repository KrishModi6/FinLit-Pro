"""Risk and performance statistics, alone and against a benchmark.

All on daily simple returns of dividend-adjusted closes, annualised with 252
trading days. Sharpe, Sortino and alpha subtract the risk-free rate, which
the app reads live from the 13-week T-bill yield when it can.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from finlit_pro.analytics.indicators import drawdown_series

TD = 252
# Calendar-day windows behind the 1M ... 10Y ranges. The window, the research brief and the
# rules engine all use this one table so their figures agree.
RANGE_DAYS = {"1M": 31, "3M": 92, "6M": 183, "1Y": 365, "3Y": 1096, "5Y": 1826, "10Y": 3653}


@dataclass
class RiskReport:
    metrics: dict[str, float]
    benchmark: str | None
    drawdown: pd.Series
    rolling_vol: pd.Series
    rolling_beta: pd.Series | None
    growth: pd.Series
    bench_growth: pd.Series | None
    returns: pd.Series
    notes: list[str] = field(default_factory=list)


def _cagr(values: pd.Series) -> float:
    years = (values.index[-1] - values.index[0]).days / 365.25
    if years <= 0 or values.iloc[0] <= 0:
        return float("nan")
    return float((values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1)


def _longest_drawdown_days(values: pd.Series) -> int:
    """Longest stretch, in calendar days, spent below a previous high."""
    peak = values.cummax()
    under = values < peak
    longest, start = 0, None
    for when, is_under in under.items():
        if is_under and start is None:
            start = when
        elif not is_under and start is not None:
            longest = max(longest, (when - start).days)
            start = None
    if start is not None:
        longest = max(longest, (values.index[-1] - start).days)
    return longest


def report(
    closes: pd.Series,
    bench: pd.Series | None,
    rf_annual: float,
    years: float | None = 3,
    bench_symbol: str | None = None,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
) -> RiskReport:
    """Statistics over [start, end], or over the last `years` if no start is given."""
    end = end or closes.index[-1]
    cutoff = start if start is not None else end - pd.Timedelta(days=int((years or 3) * 365.25))
    s = closes[(closes.index >= cutoff) & (closes.index <= end)].dropna()
    notes: list[str] = []
    if len(s) < 60:
        raise ValueError("Fewer than 60 trading days in the selected range. Choose a longer date range.")
    if s.index[0] > cutoff + pd.Timedelta(days=10):
        notes.append(f"History starts {s.index[0].date()}, after the start of the selected range.")

    r = s.pct_change().dropna()
    rf_d = (1 + rf_annual) ** (1 / TD) - 1
    excess = r - rf_d
    vol = float(r.std(ddof=1) * np.sqrt(TD))
    downside = excess[excess < 0]
    downside_dev = float(np.sqrt((downside**2).sum() / len(excess)) * np.sqrt(TD))
    dd = drawdown_series(s)
    max_dd = float(-dd.min())
    cagr = _cagr(s)
    var95 = float(-np.percentile(r, 5))
    var99 = float(-np.percentile(r, 1))

    metrics: dict[str, float] = {
        "total_return": float(s.iloc[-1] / s.iloc[0] - 1),
        "cagr": cagr,
        "volatility": vol,
        "sharpe": float(excess.mean() * TD / vol) if vol > 0 else float("nan"),
        "sortino": float(excess.mean() * TD / downside_dev) if downside_dev > 0 else float("nan"),
        "max_drawdown": max_dd,
        "longest_drawdown_days": float(_longest_drawdown_days(s)),
        "calmar": float(cagr / max_dd) if max_dd > 0 else float("nan"),
        "var95_1d": var95,
        "var99_1d": var99,
        "cvar95_1d": float(-r[r <= -var95].mean()),
        "parametric_var95_1d": float(-(r.mean() - 1.6449 * r.std(ddof=1))),
        "skew": float(r.skew()),
        "excess_kurtosis": float(r.kurt()),
        "best_day": float(r.max()),
        "worst_day": float(r.min()),
        "positive_days": float((r > 0).mean()),
        "risk_free": rf_annual,
    }

    rolling_vol = r.rolling(63).std() * np.sqrt(TD)
    growth = s / s.iloc[0]
    rolling_beta = bench_growth = None

    if bench is not None and len(bench) > 60:
        b = bench[(bench.index >= cutoff) & (bench.index <= end)].dropna()
        joined = pd.concat([s.rename("s"), b.rename("b")], axis=1, join="inner").dropna()
        if len(joined) > 60:
            rs = joined["s"].pct_change().dropna()
            rb = joined["b"].pct_change().dropna()
            cov = float(np.cov(rs, rb, ddof=1)[0, 1])
            var_b = float(rb.var(ddof=1))
            beta = cov / var_b if var_b > 0 else float("nan")
            corr = float(rs.corr(rb))
            active = rs - rb
            te = float(active.std(ddof=1) * np.sqrt(TD))
            up, down = rb > 0, rb < 0
            metrics.update(
                {
                    "beta": beta,
                    "alpha": float(((rs.mean() - rf_d) - beta * (rb.mean() - rf_d)) * TD),
                    "correlation": corr,
                    "r_squared": corr**2,
                    "tracking_error": te,
                    "information_ratio": float(active.mean() * TD / te) if te > 0 else float("nan"),
                    "up_capture": float(rs[up].mean() / rb[up].mean()) if up.any() else float("nan"),
                    "down_capture": float(rs[down].mean() / rb[down].mean()) if down.any() else float("nan"),
                    "bench_cagr": _cagr(joined["b"]),
                    "bench_total_return": float(joined["b"].iloc[-1] / joined["b"].iloc[0] - 1),
                    "bench_volatility": float(rb.std(ddof=1) * np.sqrt(TD)),
                    "bench_sharpe": float((rb.mean() - rf_d) * TD / (rb.std(ddof=1) * np.sqrt(TD))) if rb.std() > 0 else float("nan"),
                    "bench_max_drawdown": float(-drawdown_series(joined["b"]).min()),
                    "bench_var95_1d": float(-np.percentile(rb, 5)),
                    "bench_worst_day": float(rb.min()),
                }
            )
            window = 126
            rolling_beta = rs.rolling(window).cov(rb) / rb.rolling(window).var()
            bench_growth = joined["b"] / joined["b"].iloc[0]
        else:
            notes.append("The stock and benchmark share too few trading days to compare.")
    elif bench_symbol:
        notes.append(f"Benchmark {bench_symbol} could not be loaded, so beta and alpha are missing.")

    return RiskReport(
        metrics=metrics,
        benchmark=bench_symbol,
        drawdown=dd,
        rolling_vol=rolling_vol,
        rolling_beta=rolling_beta,
        growth=growth,
        bench_growth=bench_growth,
        returns=r,
        notes=notes,
    )
