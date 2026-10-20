"""The contract a prediction model must meet to plug into FinLit Pro.

The Prediction view, the walk-forward evaluation and the research panel all
talk to models only through `PredictionModel`. To connect another model:

  1. Implement the protocol below: a name and version, the horizons and
     simulation counts it supports, a description of its inputs, and
     `predict(bars, horizon, simulations, seed)` returning a `Forecast`.
  2. `predict` must use only the bars it is given. The evaluation passes
     each origin's history truncated at that date, so a model that reads
     anything else would leak future data into its own track record.
  3. Register an instance in `model/registry.py`.

Nothing else in the application needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class InputSpec:
    name: str
    value: str
    description: str


@dataclass
class Signal:
    name: str
    reading: str
    score: int


@dataclass
class Forecast:
    model: str
    version: str
    as_of: pd.Timestamp
    horizon_days: int
    price: float  # the model's view of today's price (adjusted close)
    target: float  # the model's point forecast at the horizon
    verdict: str  # the model's own recommendation label
    score: int | None = None
    score_range: tuple[int, int] | None = None
    quantiles: dict[int, float] = field(default_factory=dict)  # percentile -> price at horizon
    prob_up: float | None = None
    components: dict[str, float] = field(default_factory=dict)  # named sub-forecasts
    weights: dict[str, float] = field(default_factory=dict)
    diagnostics: dict[str, float | str] = field(default_factory=dict)
    signals: list[Signal] = field(default_factory=list)
    band_days: np.ndarray | None = None  # day offsets for the fan chart
    bands: dict[int, np.ndarray] = field(default_factory=dict)
    inputs: list[InputSpec] = field(default_factory=list)

    @property
    def expected_return(self) -> float:
        return self.target / self.price - 1


class PredictionModel(Protocol):
    key: str
    name: str
    version: str
    description: str
    horizons: tuple[int, ...]
    simulations: tuple[int, ...]
    lookback_calendar_days: int
    bullish: tuple[str, ...]  # verdict labels that mean "own it"
    bearish: tuple[str, ...]

    def input_spec(self, horizon: int, simulations: int) -> list[InputSpec]: ...

    def predict(self, bars: pd.DataFrame, horizon: int, simulations: int, seed: int | None = 42) -> Forecast: ...
