"""Monte Carlo price simulation: the engine behind the Predictor tab.

This is the FinLit Pro "AI Predictor", carried over from both earlier
versions (the Streamlit app's NumPy loop and the website's JavaScript GBM)
and rebuilt to run fully vectorised, so 10,000 paths over a year take well
under a second.

Three shock models:

  gbm        Normal daily log returns. The textbook geometric Brownian motion.
  student_t  Student-t log returns, rescaled to the same volatility. The
             degrees of freedom are fitted from the stock's own excess
             kurtosis, so a stock with violent days gets fatter tails.
  bootstrap  Resamples the stock's own historical daily returns in blocks of
             consecutive days, which keeps real fat tails and some of the
             volatility clustering a normal model throws away.

It is not a forecast. It shows the spread of outcomes a model with these
parameters produces, and `calibration()` below measures how honest that
spread has actually been for this stock.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import NormalDist

import numpy as np
import pandas as pd

from finlit_quant.analytics.indicators import log_returns
from finlit_quant.validation import ValidationError

MODELS = {
    "student_t": "Fat tails (Student-t)",
    "gbm": "Normal (GBM)",
    "bootstrap": "Historical bootstrap",
}
DRIFT_MODES = {
    "historical": "Historical drift",
    "zero": "Zero expected return",
    "custom": "Custom expected return",
}
PERCENTILES = (5, 10, 25, 50, 75, 90, 95)
TRADING_DAYS = 252
# paths x days. 20 million float32 cells is about 80 MB per matrix.
MAX_CELLS = 20_000_000
_N = NormalDist()


@dataclass
class MCConfig:
    horizon_days: int = 252
    n_paths: int = 10_000
    model: str = "student_t"
    drift_mode: str = "historical"
    # Annual arithmetic expected return, as a decimal, for drift_mode="custom".
    custom_return: float = 0.08
    lookback_days: int = 3 * TRADING_DAYS
    seed: int | None = 42
    block_days: int = 10

    def validate(self) -> None:
        if self.model not in MODELS:
            raise ValidationError(f"Unknown model {self.model!r}. Pick one of the options in the list.")
        if self.drift_mode not in DRIFT_MODES:
            raise ValidationError(f"Unknown drift mode {self.drift_mode!r}. Pick one of the options in the list.")
        if self.horizon_days < 1:
            raise ValidationError("The horizon must be at least 1 trading day.")
        if self.n_paths < 100:
            raise ValidationError("Use at least 100 paths, or the percentiles are mostly noise.")
        if self.n_paths * self.horizon_days > MAX_CELLS:
            most = MAX_CELLS // self.horizon_days
            raise ValidationError(
                f"{self.n_paths:,} paths over {self.horizon_days:,} days is too much to hold in memory. "
                f"At this horizon use at most {most:,} paths, or shorten the horizon."
            )
        if self.custom_return <= -1:
            raise ValidationError("A custom expected return of -100% or worse is not possible. Enter something above -100.")


@dataclass
class Estimates:
    mu: float  # mean daily log return actually used
    sigma: float  # daily log-return standard deviation
    hist_mu: float  # mean daily log return in the lookback window
    t_df: float  # fitted Student-t degrees of freedom
    excess_kurtosis: float
    samples: int
    returns: np.ndarray = field(repr=False)

    @property
    def drift_annual(self) -> float:
        """Annualised arithmetic expected return implied by mu and sigma."""
        return float(np.exp((self.mu + self.sigma**2 / 2) * TRADING_DAYS) - 1)

    @property
    def vol_annual(self) -> float:
        return float(self.sigma * np.sqrt(TRADING_DAYS))


@dataclass
class MCResult:
    config: MCConfig
    start_price: float
    est: Estimates
    days: np.ndarray  # day offsets the bands are reported at
    bands: dict[int, np.ndarray]  # percentile -> price at each of `days`
    terminal: np.ndarray
    sample_paths: np.ndarray
    max_drawdowns: np.ndarray
    stats: dict[str, float]


def estimate(closes: pd.Series, cfg: MCConfig) -> Estimates:
    r = log_returns(closes).to_numpy()[-cfg.lookback_days :]
    if len(r) < 60:
        raise ValidationError(
            f"Only {len(r)} days of history are available, and the model needs at least 60. "
            "Pick a stock that has traded for longer, or shorten the lookback."
        )
    hist_mu = float(r.mean())
    sigma = float(r.std(ddof=1))
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValidationError("This price series never moves, so there is no volatility to simulate.")

    centred = r - hist_mu
    kurt = float(np.mean(centred**4) / np.mean(centred**2) ** 2 - 3)
    # Excess kurtosis of a Student-t is 6 / (df - 4); invert it. Clamped to
    # [3, 30]: below 3 the variance is infinite, above 30 it is normal anyway.
    t_df = float(np.clip(4 + 6 / kurt, 3, 30)) if kurt > 0 else 30.0

    # First Version (FinLit Pro website): drift was the mean daily LOG return,
    # and the simulation then subtracted sigma^2/2 again as if it had been an
    # arithmetic mean. That applies the Ito correction twice and drags every
    # path down by sigma^2/2 a year: about 12.5% a year for a 50%-vol stock.
    # Current Version: a mean log return is already the log drift, so it is
    # used as is. The sigma^2/2 term appears only where an ARITHMETIC return
    # is converted into a log drift, which is the zero and custom modes.
    if cfg.drift_mode == "historical":
        mu = hist_mu
    elif cfg.drift_mode == "zero":
        # Expected price equals today's price: E[S_T] = S_0.
        mu = -(sigma**2) / 2
    else:
        mu = np.log1p(cfg.custom_return) / TRADING_DAYS - sigma**2 / 2

    return Estimates(mu=float(mu), sigma=sigma, hist_mu=hist_mu, t_df=t_df, excess_kurtosis=kurt, samples=len(r), returns=r)


def _shocks(cfg: MCConfig, est: Estimates, rng: np.random.Generator) -> np.ndarray:
    n, h = cfg.n_paths, cfg.horizon_days
    if cfg.model == "gbm":
        z = rng.standard_normal((n, h), dtype=np.float32)
        return est.mu + est.sigma * z
    if cfg.model == "student_t":
        df = est.t_df
        # A raw t has variance df / (df - 2); rescale to unit variance so the
        # volatility matches the stock's and only the tail shape changes.
        z = rng.standard_t(df, (n, h)).astype(np.float32) * np.float32(np.sqrt((df - 2) / df))
        return est.mu + est.sigma * z
    # Block bootstrap. Demeaned so the drift mode still controls the centre.
    pool = (est.returns - est.hist_mu).astype(np.float32)
    block = int(max(1, min(cfg.block_days, len(pool) // 4)))
    n_blocks = -(-h // block)
    starts = rng.integers(0, len(pool) - block + 1, size=(n, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n, n_blocks * block)[:, :h]
    return est.mu + pool[idx]


def simulate(closes: pd.Series, cfg: MCConfig, start_price: float | None = None) -> MCResult:
    cfg.validate()
    est = estimate(closes, cfg)
    s0 = float(start_price if start_price else closes.iloc[-1])
    rng = np.random.default_rng(cfg.seed)

    log_paths = np.cumsum(_shocks(cfg, est, rng), axis=1, dtype=np.float32)
    paths = np.empty((cfg.n_paths, cfg.horizon_days + 1), dtype=np.float32)
    paths[:, 0] = s0
    paths[:, 1:] = s0 * np.exp(log_paths)
    del log_paths

    terminal = paths[:, -1].astype(np.float64)
    running_peak = np.maximum.accumulate(paths, axis=1)
    max_dd = (1 - paths / running_peak).max(axis=1).astype(np.float64)
    del running_peak

    # Bands at no more than ~250 points: percentile over every day of a
    # 10-year horizon would cost seconds and draw no differently.
    days = np.unique(np.linspace(0, cfg.horizon_days, min(cfg.horizon_days + 1, 250)).round().astype(int))
    band_matrix = np.percentile(paths[:, days], PERCENTILES, axis=0)
    bands = {p: band_matrix[i].astype(np.float64) for i, p in enumerate(PERCENTILES)}

    rng_pick = np.random.default_rng(0 if cfg.seed is None else cfg.seed + 1)
    picks = rng_pick.choice(cfg.n_paths, size=min(60, cfg.n_paths), replace=False)
    sample_paths = paths[picks][:, days].astype(np.float64)
    del paths

    change = terminal / s0 - 1
    losses = -change
    var95 = float(np.percentile(losses, 95))
    stats = {
        "median": float(np.median(terminal)),
        "mean": float(terminal.mean()),
        **{f"p{p}": float(np.percentile(terminal, p)) for p in PERCENTILES},
        "prob_up": float((terminal > s0).mean()),
        "prob_gain_20": float((change >= 0.20).mean()),
        "prob_loss_20": float((change <= -0.20).mean()),
        "prob_loss_50": float((change <= -0.50).mean()),
        "var95": var95,
        "cvar95": float(losses[losses >= var95].mean()),
        "expected_max_dd": float(max_dd.mean()),
        "prob_dd_20": float((max_dd >= 0.20).mean()),
    }
    return MCResult(cfg, s0, est, days, bands, terminal, sample_paths, max_dd, stats)


def analytic_quantile(s0: float, mu: float, sigma: float, days: int, q: float) -> float:
    """Closed-form GBM price quantile: S0 * exp(mu*h + sigma*sqrt(h)*z_q)."""
    return float(s0 * np.exp(mu * days + sigma * np.sqrt(days) * _N.inv_cdf(q)))


@dataclass
class Calibration:
    horizon_days: int
    tests: int
    coverage: dict[str, tuple[float, float]]  # band -> (nominal, observed)
    pit: np.ndarray  # where each realised price fell in its forecast, 0..1
    verdict: str


def calibration(closes: pd.Series, horizon_days: int, lookback_days: int = 3 * TRADING_DAYS) -> Calibration | None:
    """Walk-forward test of the normal model's bands on this stock's own past.

    At regular dates in the past, estimate drift and volatility from the
    `lookback_days` before that date only, forecast `horizon_days` ahead, and
    check where the price actually ended up. A well calibrated 10-90 band
    contains the outcome about 80% of the time. Far less means the model's
    spread is too narrow for this stock, which is the usual finding.

    Origins overlap, so neighbouring tests are correlated and the coverage
    numbers are noisier than the test count suggests.
    """
    prices = closes[closes > 0].to_numpy(dtype=float)
    logs = np.log(prices)
    r = np.diff(logs)
    first = lookback_days
    last = len(prices) - 1 - horizon_days
    if last - first < 20:
        return None
    step = max(5, horizon_days // 4)
    origins = np.arange(first, last + 1, step)

    z_scores = []
    for t in origins:
        window = r[t - lookback_days : t]
        mu, sigma = window.mean(), window.std(ddof=1)
        if sigma <= 0:
            continue
        realised = logs[t + horizon_days] - logs[t]
        z_scores.append((realised - mu * horizon_days) / (sigma * np.sqrt(horizon_days)))
    if len(z_scores) < 10:
        return None
    z = np.asarray(z_scores)
    pit = np.array([_N.cdf(v) for v in z])

    coverage = {}
    for lo, hi in ((25, 75), (10, 90), (5, 95)):
        inside = float(((pit >= lo / 100) & (pit <= hi / 100)).mean())
        coverage[f"{lo}-{hi}"] = ((hi - lo) / 100, inside)

    nominal, observed = coverage["10-90"]
    if observed < nominal - 0.10:
        verdict = (
            f"Too narrow: the 10-90 band caught the real outcome {observed:.0%} of the time against "
            f"{nominal:.0%} promised. Treat the extremes on this stock as more likely than the chart shows."
        )
    elif observed > nominal + 0.10:
        verdict = (
            f"Too wide: the 10-90 band caught the outcome {observed:.0%} of the time against {nominal:.0%}. "
            "Recent volatility overstated what followed."
        )
    else:
        verdict = (
            f"Reasonably calibrated: the 10-90 band caught the outcome {observed:.0%} of the time against "
            f"{nominal:.0%} promised. That is about the model's past honesty, not a guarantee about the future."
        )
    return Calibration(horizon_days, len(z), coverage, pit, verdict)
