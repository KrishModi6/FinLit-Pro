"""Regression tests for the second round of window fixes (see docs/FIXLOG.md)."""

import pandas as pd
import pytest

from datetime import datetime

from finlit_pro.data.models import PriceHistory, Source
from finlit_pro.workspace import Workspace

pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")


def _history(currency):
    idx = pd.to_datetime(["2026-10-19", "2026-10-20"])
    bars = pd.DataFrame(
        {"open": [1234.567, 1240.0], "high": [1250.5, 1251.0], "low": [1230.25, 1235.0], "close": [1245.125, 1248.875],
         "adjclose": [1245.125, 1248.875], "volume": [51_234_567.0, 48_000_001.0]},
        index=idx,
    )
    return PriceHistory("BIG", "Big Co", currency, None, None, 1248.875, 1245.125, bars, Source("test", "", datetime(2026, 10, 20)))


def test_price_csv_keeps_whole_volumes_and_full_prices():
    from finlit_pro.ui import report

    ws = Workspace("BIG")
    ws.history = _history("USD")
    text = report.price_csv(ws)
    assert "51234567" in text and "e+07" not in text  # First Version wrote 5.12346e+07
    assert "1234.567" in text  # First Version rounded to 1234.57


def test_report_never_prints_none_for_an_unknown_currency():
    from finlit_pro.ui import report

    ws = Workspace("BIG")
    ws.history = _history(None)
    html = report.build_html(ws, {}, "")
    row = html[html.index("Last price"):][:120]
    assert "1,248.88 (2026-10-20)" in row or "1248.88 (2026-10-20)" in row, row
    assert "None" not in row


@pytest.fixture
def fake_store(monkeypatch):
    from finlit_pro import credentials

    stored = {}
    calls = []
    for var in credentials.ENV_VARS.values():
        monkeypatch.delenv(var, raising=False)

    def store(name, value):
        calls.append((name, value))
        if value:
            stored[name] = value
        else:
            stored.pop(name, None)

    monkeypatch.setattr(credentials, "store", store)
    monkeypatch.setattr(credentials, "get", lambda name: stored.get(name, ""))
    monkeypatch.setattr(credentials, "source", lambda name: "credential store" if name in stored else "not set")
    return stored, calls


def _dialog(qtbot):
    from finlit_pro.config import Settings
    from finlit_pro.ui.app import make_app

    make_app([])
    from finlit_pro.ui.settings_dialog import SettingsDialog

    dlg = SettingsDialog(Settings())
    qtbot.addWidget(dlg)
    return dlg


def _choose(dlg, provider):
    dlg.provider.setCurrentIndex(dlg.provider.findData(provider))


def test_removing_the_only_key_for_the_chosen_engine_is_refused_before_anything_changes(qtbot, fake_store):
    stored, calls = fake_store
    stored["anthropic"] = "sk-ant-api03-" + "x" * 40
    dlg = _dialog(qtbot)
    _choose(dlg, "claude")
    dlg.claude_key.remove.setChecked(True)
    dlg._save()
    # First Version deleted the key and then refused to save, leaving Claude selected with no key.
    assert calls == [] and "anthropic" in stored
    assert dlg.result_settings is None and "would be stored" in dlg.notice.text.text()


def test_a_new_key_is_stored_and_the_row_shows_where_it_is(qtbot, fake_store):
    stored, calls = fake_store
    dlg = _dialog(qtbot)
    _choose(dlg, "claude")
    dlg.claude_key.edit.setText("sk-ant-api03-" + "y" * 40)
    dlg._save()
    assert calls == [("anthropic", "sk-ant-api03-" + "y" * 40)]
    assert "credential store" in dlg.claude_key.status.text()
    assert dlg.result_settings.ai_provider == "claude"


def test_a_failed_load_keeps_showing_the_symbol_that_did_load(qtbot, monkeypatch):
    from finlit_pro.config import Settings
    from finlit_pro.data import http
    from finlit_pro.ui.app import make_app

    monkeypatch.setattr(http, "_session", lambda: (_ for _ in ()).throw(AssertionError("network used")))
    make_app([])
    from finlit_pro.ui import main_window
    from finlit_pro.ui.main_window import MainWindow

    w = MainWindow(Settings(watchlist=["DEMO"], ai_provider="rules"))
    qtbot.addWidget(w)
    w.show()
    w.load("DEMO")
    qtbot.waitUntil(lambda: bool(w.ws and w.ws.history and w.ws.forecast), timeout=60000)

    def fail(*_a, **_k):
        raise main_window.DataError("No price data for ZZZZ. Check the symbol.")

    monkeypatch.setattr(main_window, "_fetch_prices", fail)
    w.load("ZZZZ")
    qtbot.waitUntil(lambda: "Still showing" in w.notice.text.text(), timeout=20000)
    assert w.ws.symbol == "DEMO" and w.symbol.text() == "DEMO"
    w.runner.wait(20000)
