"""Keys live in the OS credential store or the environment, never in the settings file."""

import json

import keyring
import pytest
from conftest import MemoryKeyring, _backend
from keyring.errors import KeyringError

from finlit_pro import credentials
from finlit_pro.config import Settings, load_settings, save_settings, settings_path


class BrokenKeyring(MemoryKeyring):
    def set_password(self, service, username, password):
        raise KeyringError("no backend")


@pytest.fixture
def memory_keyring():
    return keyring.get_keyring()  # conftest installs a fresh in-memory store for every test


def test_keys_go_to_the_credential_store_not_the_settings_file(memory_keyring):
    credentials.store("anthropic", "sk-ant-secret-123")
    assert memory_keyring.store[("FinLitPro", "anthropic")] == "sk-ant-secret-123"
    assert credentials.get("anthropic") == "sk-ant-secret-123"
    assert credentials.source("anthropic") == "credential store"
    save_settings(Settings(ai_provider="claude"))
    assert "sk-ant" not in settings_path().read_text(encoding="utf-8")
    credentials.store("anthropic", "")  # remove
    assert credentials.get("anthropic") == "" and credentials.source("anthropic") == "not set"
    credentials.store("anthropic", "")  # removing twice is harmless


def test_environment_variable_wins_and_is_never_stored(memory_keyring, monkeypatch):
    credentials.store("openai", "sk-stored")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    assert credentials.get("openai") == "sk-from-env"
    assert credentials.source("openai") == "environment variable OPENAI_API_KEY"
    assert "sk-from-env" not in str(memory_keyring.store)


def test_no_secure_store_means_no_save(monkeypatch, tmp_path):
    keyring.set_keyring(_backend(BrokenKeyring))
    with pytest.raises(credentials.CredentialError, match="ANTHROPIC_API_KEY"):
        credentials.store("anthropic", "sk-ant-secret")
    # Nothing fell back to a file anywhere under the app's folders.
    home = settings_path().parent.parent
    assert not any("sk-ant-secret" in p.read_text(errors="ignore") for p in home.rglob("*") if p.is_file())


def test_settings_survive_bad_or_hand_edited_files():
    path = settings_path()
    path.write_text("{not json", encoding="utf-8")
    assert load_settings() == Settings()
    path.write_text(json.dumps({"benchmark": "QQQ", "risk_free_rate_pct": "four", "watchlist": ["AAPL", 3, "MSFT"], "anthropic_api_key": "sk-old", "transaction_cost_bps": 7}), encoding="utf-8")
    s = load_settings()
    assert s.benchmark == "QQQ"
    assert s.risk_free_rate_pct == Settings().risk_free_rate_pct  # wrong type ignored
    assert s.watchlist == ["AAPL", "MSFT"]
    assert s.transaction_cost_bps == 7.0
    assert not hasattr(s, "anthropic_api_key")  # unknown fields, including old key fields, are dropped
