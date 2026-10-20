import os

import numpy as np
import pandas as pd
import pytest

# Never touch the real user folders, and never open a real window.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class MemoryKeyring:
    """Stands in for the OS credential store so tests never read or write real keys."""

    priority = 1

    def __init__(self):
        self.store = {}

    def get_password(self, service, username):
        return self.store.get((service, username))

    def set_password(self, service, username, password):
        self.store[(service, username)] = password

    def delete_password(self, service, username):
        from keyring.errors import PasswordDeleteError

        if (service, username) not in self.store:
            raise PasswordDeleteError("missing")
        del self.store[(service, username)]


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("FINLIT_PRO_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import keyring

    from finlit_pro.data import http
    from finlit_pro.data.cache import DiskCache

    previous = keyring.get_keyring()
    keyring.set_keyring(_backend(MemoryKeyring))
    http.set_cache(DiskCache(tmp_path / "cache"))
    yield
    keyring.set_keyring(previous)


def _backend(cls):
    from keyring.backend import KeyringBackend

    return type(cls.__name__, (cls, KeyringBackend), {})()


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
