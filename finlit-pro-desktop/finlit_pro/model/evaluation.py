"""Point-in-time, out-of-sample evaluation of any PredictionModel.

The original predictor reported no evaluation at all. This module measures
it the way a model is reviewed before capital is allocated to it:

* Walk-forward: at each origin date the model sees only the bars up to that
  date (the history is truncated before `predict` is called), forecasts the
  horizon, and is scored against what happened next. Nothing is fitted or
  tuned on the evaluation period; the model's parameters are its own.
* Non-overlapping by default: origins step by the horizon, so each outcome
  is used once and the significance tests are not inflated.
* Against baselines: directional accuracy is compared with always calling
  "up", and forecast error with the naive no-change forecast.
* As a strategy: positions taken from the verdict, with transaction costs,
  against buy-and-hold over the same periods.

Every number is computed from the selected ticker's own history at run
time. Nothing here is a claim about how the model performs in general.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from finlit_pro.model.interface import PredictionModel


@dataclass
class Metric:
    name: str
    value: float
    display: str
    definition: str
    benchmark: str = ""  # what to compare it with
    flag: str = ""  # e.g. "not significant"


@dataclass
class Evaluation:
    model_key: str
    horizon: int
    step: int
    records: pd.DataFrame
    metrics: list[Metric]
    buckets: pd.DataFrame
    equity: pd.DataFrame  # strategy and buy-and-hold growth of 1
    notes: list[str] = field(default_factory=list)

    def metric(self, name: str) -> Metric | None:
        return next((m for m in self.metrics if m.name == name), None)


def _norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def _max_drawdown(growth: np.ndarray) -> float:
    """Largest fall from a running peak, measured from the starting value of 1.

    First Version: the peak started at the first period's value, so a strategy wiped out in its first period
    read 0/0. Current Version: the series is prefixed with 1, the capital before the first period.
    """
    if not len(growth):
        return 0.0
    g = np.r_[1.0, growth]
    peak = np.maximum.accumulate(g)
    return float((1 - g / peak).max())


def _equity(rets: np.ndarray) -> tuple[np.ndarray, int | None]:
    """Growth of 1 from period returns, held at 0 from the first period that loses all the capital.

    First Version: cumprod(1 + returns) had no floor, so a short position in a stock that more than doubled
    (GME, AMC) took the equity below zero, after which it kept compounding and flipped sign: drawdowns of
    1294%, a CAGR of "+nan%", or a finite CAGR after a wipe-out. Current Version: capital that is gone stays
    gone, so the drawdown is 100% and the CAGR -100%. Returns (equity, index of the ruinous period or None).
    """
    growth = np.cumprod(1 + rets)
    ruin = np.flatnonzero(growth <= 0)
    if len(ruin):
        growth[ruin[0]:] = 0.0
        return growth, int(ruin[0])
    return growth, None


MIN_ORIGINS = 8


def _span(days: float) -> str:
    """Calendar days as a span a reader can picture: about 2 years, about 15 months, about 1 month.

    First Version: "about 0 months" and "about 1 months". Current Version: "less than a month" and "about 1 month".
    """
    months = round(days / 30.44)
    if months < 1:
        return "less than a month"
    if months == 1:
        return "about 1 month"
    return f"about {months // 12} years" if months >= 24 and months % 12 == 0 else f"about {months} months"


def _history_span(days: float, lookback_days: int) -> str:
    """The history's span, never worded the same as the longer lookback it falls short of.

    First Version: 520 sessions read "(about 2 years)" right after "needs about 2 years". Current Version:
    "just under 2 years, 728 calendar days".
    """
    span = _span(days)
    if days < lookback_days and span == _span(lookback_days):
        span = "just under " + span.removeprefix("about ")
    return f"{span}, {int(days)} calendar days"


def _origin_count(n_bars: int, first: int, horizon: int, step: int) -> int:
    return len(range(first, n_bars - horizon, step))


def _too_few_message(model: PredictionModel, bars: pd.DataFrame, horizon: int, step: int, fixed_step: bool, first: int, found: int) -> str:
    """Why the evaluation cannot run yet, and what would change that.

    First Version: every shortfall advised "choose a shorter horizon", even for a listing younger than the
    model's two-year lookback (FIG, KLAR, CRCL), where no horizon fits a single test. Current Version: that
    case names the history the model needs, the history there is, and when the first test becomes possible;
    the shorter-horizon advice is given only when a shorter horizon would fit at least 8 forecasts.
    First Version: the advice searched every whole number of days, so TEM was told "11 days or shorter" and a
    short DEMO "4 days", which the model does not offer (7, 14, 30, 60, 90), and the lookback was "needed before
    its first forecast" although the model forecasts today. Current Version: only the model's own horizons are
    searched, and the lookback is needed before the first test forecast.
    """
    n, index = len(bars), bars.index
    start = index[first] if first < n else index[0] + pd.Timedelta(days=model.lookback_calendar_days)
    eighth = (start + pd.offsets.BDay(step * (MIN_ORIGINS - 1) + horizon)).date()
    if first > n - 2:
        # No origin at any horizon: the history is shorter than the lookback plus one session to score.
        first_test = (start + pd.offsets.BDay(horizon)).date()
        return (
            f"The {model.name} needs {_span(model.lookback_calendar_days)} of history ({model.lookback_calendar_days} calendar days) "
            f"before its first test forecast, plus {horizon} sessions to score it. This history has {n} sessions from {index[0].date()} "
            f"({_history_span((index[-1] - index[0]).days, model.lookback_calendar_days)}), so no out-of-sample test fits yet at any horizon. "
            f"The first test becomes possible around {first_test}, and the {MIN_ORIGINS} the evaluation needs around {eighth}."
        )
    offered = sorted((h for h in getattr(model, "horizons", ()) if h < horizon), reverse=True)
    shorter = next((h for h in offered if _origin_count(n, first, h, step if fixed_step else h) >= MIN_ORIGINS), None)
    head = f"Only {found} out-of-sample forecasts fit in this history at a {horizon}-day horizon. The evaluation needs at least {MIN_ORIGINS}; "
    if shorter:
        return head + f"choose a horizon of {shorter} days or shorter, or a ticker with a longer history."  # one the model offers
    return head + f"a shorter horizon would not fit {MIN_ORIGINS} either. At this horizon they fit around {eighth}; until then, choose a ticker with a longer history."


def walk_forward(
    model: PredictionModel,
    bars: pd.DataFrame,
    horizon: int,
    simulations: int = 500,
    step: int | None = None,
    cost_bps: float = 5.0,
    max_origins: int = 250,
    progress: Callable[[int, int], None] | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> Evaluation:
    fixed_step = bool(step)
    step = max(1, step or horizon)
    closes = bars["adjclose"].to_numpy(dtype=float)
    index = bars.index
    # The first origin needs a full lookback window behind it.
    first = int(np.searchsorted(index, index[0] + pd.Timedelta(days=model.lookback_calendar_days)))
    last = len(bars) - 1 - horizon
    origins = list(range(first, last + 1, step))
    notes: list[str] = []
    if len(origins) > max_origins:
        origins = origins[-max_origins:]
        notes.append(f"Limited to the most recent {max_origins} origins.")
    if len(origins) < MIN_ORIGINS:
        raise ValueError(_too_few_message(model, bars, horizon, step, fixed_step, first, len(origins)))

    rows = []
    for n, i in enumerate(origins):
        if cancelled and cancelled():
            raise InterruptedError("Evaluation cancelled.")
        history = bars.iloc[: i + 1]  # point in time: nothing after the origin
        try:
            f = model.predict(history, horizon, simulations, seed=42)
        except ValueError:
            continue
        realized_price_ratio = closes[i + horizon] / closes[i]
        lo, hi = f.quantiles.get(10), f.quantiles.get(90)
        rows.append(
            {
                "date": index[i],
                "price": f.price,
                "target": f.target,
                "pred_return": f.expected_return,
                "realized_return": realized_price_ratio - 1,
                "realized_price": f.price * realized_price_ratio,
                "verdict": f.verdict,
                "score": f.score,
                "p10": lo,
                "p90": hi,
                "prob_up": f.prob_up,
            }
        )
        if progress:
            progress(n + 1, len(origins))
    # First Version: with no forecast produced at all, DataFrame([]).set_index("date") raised a KeyError before
    # this check. Current Version: the rows are counted first, so the message below is what the user sees.
    if len(rows) < MIN_ORIGINS:
        raise ValueError(
            f"Only {len(rows)} of {len(origins)} test dates produced a forecast (the model refused the others, usually because "
            f"its window held too little or unchanging history), and the evaluation needs at least {MIN_ORIGINS}. Choose a ticker with a longer, "
            "regularly traded history."
        )
    rec = pd.DataFrame(rows).set_index("date")

    n = len(rec)
    pred, real = rec["pred_return"].to_numpy(), rec["realized_return"].to_numpy()
    metrics: list[Metric] = []
    overlapping = step < horizon
    if overlapping:
        notes.append("Origins overlap, so neighbouring outcomes are correlated and significance is overstated.")

    # Direction
    up_share = float((real > 0).mean())
    hits = np.sign(pred) == np.sign(real)
    hit = float(hits.mean())
    naive = max(up_share, 1 - up_share)
    se = math.sqrt(max(naive * (1 - naive), 1e-9) / n)
    p_value = _norm_sf((hit - naive) / se) if se > 0 else float("nan")
    metrics.append(Metric("Directional hit rate", hit, f"{hit:.1%}", "Share of forecasts whose sign matched the realised return.", f"Always calling the majority direction: {naive:.1%}", "" if p_value < 0.05 else "not significantly better than the naive call"))
    metrics.append(Metric("Hit-rate p-value", p_value, f"{p_value:.3f}", "One-sided test that the hit rate beats the naive majority call (normal approximation).", "Below 0.05 is conventionally significant"))

    # Error versus naive
    err = np.abs(rec["target"] - rec["realized_price"]) / rec["price"]
    naive_err = np.abs(rec["price"] - rec["realized_price"]) / rec["price"]
    mae, mae_naive = float(err.mean()), float(naive_err.mean())
    skill = 1 - mae / mae_naive if mae_naive > 0 else float("nan")
    metrics.append(Metric("Mean absolute error", mae, f"{mae:.2%}", "Average |forecast - outcome| as a share of the starting price.", f"No-change forecast: {mae_naive:.2%}"))
    metrics.append(Metric("Skill vs no-change", skill, f"{skill:+.1%}", "1 - MAE / MAE of the no-change forecast. Positive means more accurate than assuming no move.", "0% means no better than naive", "" if skill > 0 else "worse than the naive forecast"))
    rmse = float(np.sqrt(np.mean(((rec["target"] - rec["realized_price"]) / rec["price"]) ** 2)))
    metrics.append(Metric("Root mean squared error", rmse, f"{rmse:.2%}", "Penalises large misses more than MAE."))

    # Ranking skill
    ic = _spearman(pred, real)
    t_ic = ic * math.sqrt((n - 2) / max(1 - ic**2, 1e-9)) if np.isfinite(ic) else float("nan")
    # First Version: the flag cleared whenever |t| >= 2, so a significantly NEGATIVE IC (forecasts ranking outcomes
    # backwards) was shown unflagged and passed the rules engine. Current Version: only t >= 2 clears it.
    if np.isfinite(t_ic) and t_ic >= 2:
        ic_flag = ""
    elif np.isfinite(t_ic) and t_ic <= -2:
        ic_flag = "negative: forecasts rank outcomes backwards"
    else:
        ic_flag = "not significant (|t| < 2)"
    metrics.append(Metric("Information coefficient", ic, f"{ic:+.3f}", "Spearman rank correlation between forecast and realised returns.", "Above 0.05 is considered useful in equity research", ic_flag))
    metrics.append(Metric("IC t-statistic", t_ic, f"{t_ic:+.2f}", "Significance of the information coefficient."))

    # Uncertainty calibration
    if rec["p10"].notna().all() and rec["p90"].notna().all():
        inside = float(((rec["realized_price"] >= rec["p10"]) & (rec["realized_price"] <= rec["p90"])).mean())
        metrics.append(Metric("10-90 band coverage", inside, f"{inside:.1%}", "Share of outcomes inside the model's 10th-90th percentile range.", "A calibrated band covers 80%", "" if abs(inside - 0.8) <= 0.1 else ("band too narrow" if inside < 0.8 else "band too wide")))
    if rec["prob_up"].notna().all():
        brier = float(np.mean((rec["prob_up"] - (real > 0)) ** 2))
        base_brier = float(np.mean((up_share - (real > 0)) ** 2))
        metrics.append(Metric("Brier score (P up)", brier, f"{brier:.3f}", "Mean squared error of the model's probability of a rise. Lower is better.", f"Constant base-rate probability: {base_brier:.3f}"))

    # Strategy from the verdict
    periods_per_year = 252 / horizon
    cost = cost_bps / 10_000
    bull = rec["verdict"].isin(model.bullish).to_numpy()
    bear = rec["verdict"].isin(model.bearish).to_numpy()
    positions = {"Long/flat": np.where(bull, 1.0, 0.0), "Long/short": np.where(bull, 1.0, np.where(bear, -1.0, 0.0))}
    equity = {}
    if overlapping:
        notes.append("Strategy figures assume non-overlapping holds; with overlapping origins they are indicative only.")
    for name, pos in positions.items():
        turnover = np.abs(np.diff(np.concatenate([[0.0], pos])))
        rets = pos * real - turnover * cost
        growth, ruin = _equity(rets)
        if ruin is not None:
            # Nothing is left to trade after the wipe-out: that period loses 100% and later periods return 0.
            rets = rets.copy()
            rets[ruin], rets[ruin + 1:] = -1.0, 0.0
            notes.append(f"{name}: the strategy lost all its capital in the period from {rec.index[ruin].date()}, so its equity stays at zero after it.")
        equity[name] = growth
        years = n / periods_per_year
        cagr = (growth[-1] ** (1 / years) - 1 if growth[-1] > 0 else -1.0) if years > 0 else float("nan")
        vol = float(np.std(rets, ddof=1) * math.sqrt(periods_per_year))
        sharpe = float(np.mean(rets) * periods_per_year / vol) if vol > 0 else float("nan")
        metrics.append(Metric(f"{name} CAGR", cagr, f"{cagr:+.1%}", f"Annualised return holding the {name.lower()} position from each verdict for the horizon, after {cost_bps:g} bp per trade."))
        metrics.append(Metric(f"{name} Sharpe", sharpe, f"{sharpe:.2f}", "Annualised mean / volatility of the strategy's period returns (no risk-free deduction)."))
        metrics.append(Metric(f"{name} max drawdown", _max_drawdown(growth), f"-{_max_drawdown(growth):.1%}", "Largest peak-to-trough fall of the strategy's equity."))
        metrics.append(Metric(f"{name} exposure", float(np.mean(pos != 0)), f"{np.mean(pos != 0):.0%}", "Share of periods with a position."))
    bh = np.cumprod(1 + real)
    equity["Buy and hold"] = bh
    years = n / periods_per_year
    bh_cagr = bh[-1] ** (1 / years) - 1 if years > 0 and bh[-1] > 0 else float("nan")
    bh_vol = float(np.std(real, ddof=1) * math.sqrt(periods_per_year))
    metrics.append(Metric("Buy and hold CAGR", bh_cagr, f"{bh_cagr:+.1%}", "Holding the stock over the same evaluation periods."))
    metrics.append(Metric("Buy and hold Sharpe", float(np.mean(real) * periods_per_year / bh_vol) if bh_vol > 0 else float("nan"), f"{np.mean(real) * periods_per_year / bh_vol:.2f}" if bh_vol > 0 else "n/a", "Same definition as the strategy Sharpe."))
    metrics.append(Metric("Buy and hold max drawdown", _max_drawdown(bh), f"-{_max_drawdown(bh):.1%}", "Largest peak-to-trough fall."))

    buckets = (
        rec.assign(hit=hits)
        .groupby("verdict")
        .agg(forecasts=("realized_return", "size"), mean_return=("realized_return", "mean"), hit_rate=("hit", "mean"), mean_forecast=("pred_return", "mean"))
    )
    order = ["STRONG SELL", "SELL", "HOLD", "BUY", "STRONG BUY"]
    buckets = buckets.reindex([v for v in order if v in buckets.index] + [v for v in buckets.index if v not in order])

    notes.append(
        f"{n} forecasts from {rec.index[0].date()} to {rec.index[-1].date()}, one ticker. "
        "A single stock's history is a small sample: treat these as a check on the model, not proof of skill."
    )
    return Evaluation(model.key, horizon, step, rec, metrics, buckets, pd.DataFrame(equity, index=rec.index), notes)
