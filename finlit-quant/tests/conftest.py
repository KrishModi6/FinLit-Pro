import os

import numpy as np
import pandas as pd
import pytest

# Never touch the real user folders, and never open a real window.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("FINLIT_QUANT_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from finlit_quant.data import http
    from finlit_quant.data.cache import DiskCache

    http.set_cache(DiskCache(tmp_path / "cache"))
    yield


def gbm_closes(n=1500, mu=0.0004, sigma=0.015, seed=3, start=100.0) -> pd.Series:
    rng = np.random.default_rng(seed)
    r = rng.normal(mu, sigma, n)
    index = pd.bdate_range("2015-01-02", periods=n)
    return pd.Series(start * np.exp(np.cumsum(r)), index=index)


def bars_from(closes: pd.Series, volume=1e6) -> pd.DataFrame:
    prev = closes.shift().fillna(closes.iloc[0])
    return pd.DataFrame(
        {
            "open": prev,
            "high": np.maximum(prev, closes) * 1.005,
            "low": np.minimum(prev, closes) * 0.995,
            "close": closes,
            "adjclose": closes,
            "volume": np.full(len(closes), volume),
        },
        index=closes.index,
    )
