"""Available prediction models. Register new ones here (see interface.py)."""

from __future__ import annotations

from finlit_pro.model.finlit_predictor import FinLitPredictor
from finlit_pro.model.interface import PredictionModel

MODELS: dict[str, PredictionModel] = {}


def register(model: PredictionModel) -> None:
    MODELS[model.key] = model


register(FinLitPredictor("original"))
register(FinLitPredictor("corrected"))

DEFAULT = "finlit-v1.0"


def get(key: str | None = None) -> PredictionModel:
    """The model registered under `key`, or the default when no key is given."""
    if not key:
        return MODELS[DEFAULT]
    if key not in MODELS:
        raise ValueError(f'No prediction model is registered as "{key}". Available: {", ".join(MODELS)}.')
    return MODELS[key]
