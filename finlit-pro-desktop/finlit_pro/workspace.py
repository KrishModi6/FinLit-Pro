"""Everything loaded and computed for the ticker on screen.

Views fill this in as background jobs finish and read whatever is present.
Any field can be None: a missing piece is shown as missing, never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from finlit_pro.analytics.montecarlo import Calibration, MCResult
from finlit_pro.analytics.risk import RiskReport
from finlit_pro.analytics.valuation import Check, DCFInputs, DCFResult
from finlit_pro.data.filings import FilingText
from finlit_pro.data.models import DEMO, Fundamentals, NewsItem, PriceHistory, Source
from finlit_pro.model.evaluation import Evaluation
from finlit_pro.model.interface import Forecast


@dataclass
class Workspace:
    symbol: str
    history: PriceHistory | None = None
    benchmark: PriceHistory | None = None
    risk_free: float = 0.04
    risk_free_source: Source | None = None
    fundamentals: Fundamentals | None = None
    fundamentals_error: str | None = None
    ratios: dict[str, float] = field(default_factory=dict)
    piotroski: tuple[int, int, list[Check]] | None = None
    altman: tuple[float, str] | None = None
    dcf_inputs: DCFInputs | None = None
    dcf: DCFResult | None = None
    implied_growth: float | None = None
    forecast: Forecast | None = None
    forecast_error: str | None = None
    evaluation: Evaluation | None = None
    evaluation_error: str | None = None
    mc: MCResult | None = None
    mc_error: str | None = None
    calibration: Calibration | None = None
    risk: RiskReport | None = None
    risk_error: str | None = None
    filing_texts: list[FilingText] = field(default_factory=list)
    filing_problems: list[str] = field(default_factory=list)
    news: list[NewsItem] = field(default_factory=list)

    @property
    def is_demo(self) -> bool:
        return bool(self.history and self.history.status == DEMO)
