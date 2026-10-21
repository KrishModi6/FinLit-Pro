"""Data containers shared by every layer, each carrying its provenance."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd


class DataError(RuntimeError):
    """A data problem with a message fit to show the user as is."""


class NotFoundError(DataError):
    """The provider answered that the symbol or document does not exist. Asking another provider will not help."""


class NetworkError(DataError):
    """The provider could not be reached or did not answer in time. Its other hosts are likely unreachable too."""


# How a dataset was obtained.
LIVE, CACHE, STALE, DEMO, IMPORT = "live", "cache", "stale", "demo", "import"
STATUS_LABEL = {
    LIVE: "Live",
    CACHE: "Cached",
    STALE: "Offline copy",
    DEMO: "Simulated",
    IMPORT: "Imported file",
}


@dataclass
class Source:
    """Where a dataset came from, when, and as of what date."""

    name: str  # e.g. "Yahoo Finance chart API"
    url: str
    retrieved_at: datetime
    as_of: str | None = None  # the date the data describes
    status: str = LIVE
    detail: str = ""  # e.g. "10-Q filed 2026-07-31, period ended 2026-06-27"

    def label(self) -> str:
        parts = [self.name, STATUS_LABEL.get(self.status, self.status)]
        if self.as_of:
            parts.append(f"as of {self.as_of}")
        parts.append(f"retrieved {self.retrieved_at:%Y-%m-%d %H:%M}")
        return " | ".join(parts)


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
    source: Source
    dividends: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    # Split ratio (new shares per old share) by date, e.g. 4.0 for a 4-for-1.
    splits: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    attempts: list[str] = field(default_factory=list)  # providers that failed first

    @property
    def status(self) -> str:
        return self.source.status

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

    def window(self, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.DataFrame:
        b = self.bars
        if start is not None:
            b = b[b.index >= start]
        if end is not None:
            b = b[b.index <= end]
        return b


@dataclass
class Filing:
    form: str
    filed: str
    report_date: str
    description: str
    url: str  # primary document
    accession: str = ""
    index_url: str = ""  # the filing's index page on sec.gov


@dataclass
class NewsItem:
    title: str
    publisher: str
    published: datetime | None
    url: str


@dataclass
class FactRef:
    """The filing a single reported number came from."""

    form: str
    filed: str
    accession: str
    url: str


@dataclass
class Fundamentals:
    """What SEC EDGAR's XBRL company facts say about one company.

    `annual` has one row per fiscal year (index = fiscal year end), in USD
    except `eps_diluted` (USD per share) and share counts. `ttm` holds
    trailing-twelve-month flows where the latest 10-Q made them computable,
    `latest` the most recent balance sheet. `refs[metric][year_end]` names
    the filing each annual value was taken from, so every number can be
    traced and cited.
    """

    cik: int
    name: str
    annual: pd.DataFrame
    ttm: dict[str, float]
    latest: dict[str, float]
    latest_period: str | None
    shares_outstanding: float | None
    sources: list[Source] = field(default_factory=list)
    sic_description: str | None = None
    fiscal_year_end: str | None = None
    exchanges: list[str] = field(default_factory=list)
    filings: list[Filing] = field(default_factory=list)
    refs: dict[str, dict[pd.Timestamp, FactRef]] = field(default_factory=dict)
    ttm_refs: dict[str, FactRef] = field(default_factory=dict)
    shares_date: str | None = None
    split_notes: list[str] = field(default_factory=list)
    splits_applied: bool = False
    # Caveats about this company's data shown with the figures, e.g. XBRL lagging the latest filing.
    notes: list[str] = field(default_factory=list)

    KEY_FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A", "8-K", "DEF 14A", "S-1", "S-3", "SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A", "20-F", "6-K", "40-F")

    @property
    def status(self) -> str:
        return self.sources[0].status if self.sources else LIVE

    def key_filings(self) -> list[Filing]:
        return [f for f in self.filings if f.form in self.KEY_FORMS]

    def insider_filings(self, days: int = 90) -> int:
        """Form 4 filings (insider transactions) in the last `days` days."""
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return sum(1 for f in self.filings if f.form == "4" and f.filed >= cutoff)

    def latest_filing(self, *forms: str) -> Filing | None:
        return next((f for f in self.filings if f.form in forms), None)


@dataclass
class OptionQuote:
    contract: str
    kind: str  # "call" or "put"
    strike: float
    expiry: str  # YYYY-MM-DD
    bid: float | None
    ask: float | None
    last: float | None
    implied_vol: float | None
    volume: int | None
    open_interest: int | None

    @property
    def mid(self) -> float | None:
        if self.bid and self.ask and self.ask >= self.bid > 0:
            return (self.bid + self.ask) / 2
        return self.last if self.last and self.last > 0 else None


@dataclass
class OptionChain:
    symbol: str
    expiries: list[str]
    expiry: str
    calls: list[OptionQuote]
    puts: list[OptionQuote]
    underlying_price: float | None
    source: Source
