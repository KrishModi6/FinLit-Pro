"""Multi-ticker comparison and a random-portfolio efficient frontier."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from finlit_quant.analytics.indicators import max_drawdown

TD = 252


@dataclass
class Comparison:
    closes: pd.DataFrame  # aligned, inner join on dates
    growth: pd.DataFrame  # each column rebased to 100
    returns: pd.DataFrame
    correlation: pd.DataFrame
    stats: pd.DataFrame  # one row per ticker


def compare(closes: dict[str, pd.Series], years: float, rf_annual: float) -> Comparison:
    frame = pd.concat({k: v for k, v in closes.items()}, axis=1, join="inner").dropna()
    cutoff = frame.index[-1] - pd.Timedelta(days=int(years * 365.25))
    frame = frame[frame.index >= cutoff]
    if len(frame) < 60:
        raise ValueError("These tickers share fewer than 60 trading days in that window. Try a shorter period or different tickers.")
    rets = frame.pct_change().dropna()
    span_years = (frame.index[-1] - frame.index[0]).days / 365.25
    rows = {}
    for sym in frame.columns:
        s = frame[sym]
        vol = float(rets[sym].std(ddof=1) * np.sqrt(TD))
        cagr = float((s.iloc[-1] / s.iloc[0]) ** (1 / span_years) - 1) if span_years > 0 else np.nan
        rows[sym] = {
            "Total return": float(s.iloc[-1] / s.iloc[0] - 1),
            "CAGR": cagr,
            "Volatility": vol,
            "Sharpe": (cagr - rf_annual) / vol if vol > 0 else np.nan,
            "Max drawdown": max_drawdown(s),
        }
    return Comparison(
        closes=frame,
        growth=frame / frame.iloc[0] * 100,
        returns=rets,
        correlation=rets.corr(),
        stats=pd.DataFrame(rows).T,
    )


@dataclass
class Frontier:
    returns: np.ndarray
    vols: np.ndarray
    sharpes: np.ndarray
    weights: np.ndarray
    symbols: list[str]
    max_sharpe: int
    min_vol: int


def frontier(rets: pd.DataFrame, rf_annual: float, n: int = 5000, seed: int = 11) -> Frontier:
    """Random long-only portfolios plotted in risk/return space.

    Expected returns are each asset's historical mean, which is the noisiest
    input in finance, so the "best" portfolio here is the best one for the
    PAST. The minimum-volatility point relies only on the covariance matrix
    and is far more stable.
    """
    mean = rets.mean().to_numpy() * TD
    cov = rets.cov().to_numpy() * TD
    rng = np.random.default_rng(seed)
    w = rng.dirichlet(np.ones(len(mean)), n)
    port_ret = w @ mean
    port_vol = np.sqrt(np.einsum("ij,jk,ik->i", w, cov, w))
    sharpe = (port_ret - rf_annual) / port_vol
    return Frontier(port_ret, port_vol, sharpe, w, list(rets.columns), int(np.argmax(sharpe)), int(np.argmin(port_vol)))
