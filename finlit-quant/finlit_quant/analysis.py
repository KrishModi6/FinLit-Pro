"""Everything computed for one ticker, gathered in one place.

The UI fills this in piece by piece as background jobs finish (prices first,
then SEC data, then the Monte Carlo run), and the AI analyst and the report
exporter read whatever is there. Any field can be None: a missing piece is
reported as missing, never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from finlit_quant.analytics.montecarlo import Calibration, MCResult
from finlit_quant.analytics.predictor import PredictorResult
from finlit_quant.analytics.risk import RiskReport
from finlit_quant.analytics.valuation import Check, DCFInputs, DCFResult
from finlit_quant.data.models import Fundamentals, NewsItem, PriceHistory


@dataclass
class Analysis:
    symbol: str
    history: PriceHistory | None = None
    benchmark: PriceHistory | None = None
    risk_free: float = 0.04
    risk_free_live: bool = False
    fundamentals: Fundamentals | None = None
    fundamentals_error: str | None = None
    ratios: dict[str, float] = field(default_factory=dict)
    piotroski: tuple[int, int, list[Check]] | None = None
    altman: tuple[float, str] | None = None
    dcf_inputs: DCFInputs | None = None
    dcf: DCFResult | None = None
    implied_growth: float | None = None
    mc: MCResult | None = None
    predictor: PredictorResult | None = None
    calibration: Calibration | None = None
    risk: RiskReport | None = None
    news: list[NewsItem] = field(default_factory=list)

    @property
    def is_demo(self) -> bool:
        return bool(self.history and self.history.source == "demo")
