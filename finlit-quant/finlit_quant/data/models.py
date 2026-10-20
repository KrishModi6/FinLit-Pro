"""Plain data containers shared by the data, analytics, AI and UI layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd


class DataError(RuntimeError):
    """A data problem with a message fit to show the user as is."""


@dataclass
class PriceHistory:
    symbol: str
    name: str
    currency: str
    exchange: str | None
    instrument_type: str | None
    price: float
    previous_close: float | None
    # Daily bars indexed by date: open, high, low, close, adjclose, volume.
    bars: pd.DataFrame
    dividends: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    # Split ratio (new shares per old share) by date, e.g. 4.0 for a 4-for-1.
    splits: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    # "live", "cache" (fresh enough), "stale" (offline fallback) or "demo".
    source: str = "live"
    fetched_at: datetime = field(default_factory=datetime.now)

    @property
    def closes(self) -> pd.Series:
        """Dividend- and split-adjusted closes: the right series for returns."""
        return self.bars["adjclose"]

    @property
    def day_change(self) -> float | None:
        if not self.previous_close:
            return None
        return self.price / self.previous_close - 1

    def trailing_dividends(self) -> float:
        if self.dividends.empty:
            return 0.0
        cutoff = self.bars.index[-1] - pd.Timedelta(days=365)
        return float(self.dividends[self.dividends.index > cutoff].sum())


@dataclass
class Filing:
    form: str
    filed: str
    report_date: str
    description: str
    url: str


@dataclass
class NewsItem:
    title: str
    publisher: str
    published: datetime | None
    url: str


@dataclass
class Fundamentals:
    """What SEC EDGAR's XBRL "company facts" say about one company.

    `annual` has one row per fiscal year (index = fiscal year end) and one
    column per metric, in USD except `eps_diluted` (USD per share) and the
    share counts. `ttm` holds trailing-twelve-month flows where the latest
    10-Q made them computable, and `latest` holds the most recent balance
    sheet values from either a 10-K or a 10-Q.
    """

    cik: int
    name: str
    annual: pd.DataFrame
    ttm: dict[str, float]
    latest: dict[str, float]
    latest_period: str | None
    shares_outstanding: float | None
    sic_description: str | None = None
    fiscal_year_end: str | None = None
    exchanges: list[str] = field(default_factory=list)
    filings: list[Filing] = field(default_factory=list)
    source: str = "live"
    # As-of date of the cover-page share count, and the filing date behind
    # each split-sensitive annual value: see sec.apply_splits.
    shares_date: str | None = None
    filed_dates: dict = field(default_factory=dict)
    split_notes: list[str] = field(default_factory=list)
    splits_applied: bool = False

    KEY_FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A", "8-K", "DEF 14A", "S-1", "S-3", "SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A", "20-F", "6-K", "40-F")

    def key_filings(self) -> list[Filing]:
        return [f for f in self.filings if f.form in self.KEY_FORMS]

    def insider_filings(self, days: int = 90) -> int:
        """Form 4 filings (insider trades) in the last `days` days."""
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return sum(1 for f in self.filings if f.form == "4" and f.filed >= cutoff)
