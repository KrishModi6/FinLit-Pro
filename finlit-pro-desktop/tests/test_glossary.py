"""Hover definitions: every term is defined, labels resolve to the right term, and the window shows them."""

import re
from types import SimpleNamespace

import pytest

from finlit_pro import glossary, research


def test_every_term_is_complete_and_plain():
    assert len(glossary.TERMS) > 300
    for key, t in glossary.TERMS.items():
        assert t.name and t.meaning and t.category in glossary.CATEGORIES, key
        for text in (t.name, t.meaning, t.reading, *t.aliases):
            assert "—" not in text, f"{key} contains an em dash"
    for text in glossary.ACTIONS.values():
        assert "—" not in text


@pytest.mark.parametrize(
    "label,name",
    [
        ("Bullish", "Bullish"),
        ("bearish", "Bearish"),
        ("STRONG BUY", "STRONG BUY"),
        ("Sharpe ratio", "Sharpe ratio"),
        ("P/E (TTM)", "P/E (price to earnings, TTM)"),
        ("EV / EBIT", "EV / EBIT"),
        ("FCF yield", "FCF yield"),
        ("ROIC", "ROIC (return on invested capital)"),
        ("Beta", "Beta"),
        ("1-day VaR 95% (historical)", "1-day VaR 95% (value at risk)"),
        ("Information coefficient", "Information coefficient (IC)"),
        ("P90", "Percentile"),
        ("FY2024", "Fiscal year (FY)"),
        ("Delta", "Delta"),
        ("Theta / day", "Theta (per day)"),
        ("Not worth it at 2.10  |  Buy 1 call 50.00 2026-11-20", "Not worth it"),
        ("Fat tails (Student-t)", "Return distribution"),
        ("10-K/A", "Amendment (/A)"),
        ("Offline copy", "Offline copy"),
        ("  sharpe   RATIO ", "Sharpe ratio"),
    ],
)
def test_labels_resolve_to_their_terms(label, name):
    assert glossary.lookup(label).name == name


def test_unknown_or_ambiguous_labels_get_no_guess():
    for label in ("", "Metric", "Value", "Jan", "1,000", "Result", "Price"):
        assert glossary.lookup(label) is None
    assert glossary.tip("Value") == ""
    assert glossary.tip("Value", "just this") == "just this"


def test_tooltips_are_escaped_and_carry_the_reading():
    tip = glossary.tip("Debt / equity", "Here: <b>0.78</b>")
    assert "How to read it" in tip and "&lt;b&gt;0.78&lt;/b&gt;" in tip
    assert "Bullish" in glossary.explain_text("Bullish crossover, accelerating")
    assert "Overbought" in glossary.explain_text("Approaching overbought (60.5)")
    assert glossary.explain_text("12.5") == ""


def test_every_alias_points_somewhere_real():
    for alias, key in glossary.ALIASES.items():
        assert key in glossary.TERMS, alias


# ------------------------------------------------------------------ in the window

pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")


@pytest.fixture
def loaded_window(qtbot, monkeypatch):
    from finlit_pro.config import Settings
    from finlit_pro.data import http
    from finlit_pro.ui.app import make_app

    monkeypatch.setattr(http, "_session", lambda: (_ for _ in ()).throw(AssertionError("network used")))
    make_app([])
    from finlit_pro.ui.main_window import MainWindow

    w = MainWindow(Settings(watchlist=["DEMO"], ai_provider="rules"))
    qtbot.addWidget(w)
    w.show()
    w.load("DEMO")
    qtbot.waitUntil(lambda: bool(w.ws and w.ws.forecast and w.ws.mc and w.ws.fundamentals and w.ws.risk), timeout=60000)  # None would count as ready
    yield w
    w.runner.wait(20000)


NUMERIC = re.compile(r"^[\s$+\-\d.,%/x()MBKT:]+$|^\d{4}(-\d\d-\d\d)?$")


def test_every_row_name_in_every_table_explains_itself(loaded_window, qtbot):
    from PySide6.QtWidgets import QTableWidget

    qtbot.waitUntil(lambda: loaded_window.ws.evaluation is not None, timeout=120000)
    missing = []
    for table in loaded_window.findChildren(QTableWidget):
        for i in range(table.rowCount()):
            item = table.item(i, 0)
            if item and item.text() and not NUMERIC.match(item.text()) and not item.toolTip():
                missing.append(item.text())
    assert missing == []


def test_values_explain_themselves(loaded_window):
    metrics = loaded_window.returns.metrics
    row = next(i for i in range(metrics.rowCount()) if metrics.item(i, 0).text() == "Sharpe ratio")
    assert "Sharpe ratio" in metrics.item(row, 1).toolTip()  # the number, not just its label
    kpis = loaded_window.prediction.kpis
    assert "verdict" in kpis.kpi("verdict").toolTip().lower()
    verdict = kpis.kpi("verdict").value
    assert verdict.text() in glossary.TERMS[verdict.text().lower().replace(" ", "_")].name
    assert "six signals" in verdict.toolTip()
    fundamentals = loaded_window.fundamentals.kpis
    for key in fundamentals.items:
        assert fundamentals.items[key].toolTip(), key


def test_settings_and_choices_explain_themselves(loaded_window):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QCheckBox

    boxes = {c.text(): c for c in loaded_window.chart.findChildren(QCheckBox)}
    for name in ("SMA 50", "Bollinger 20,2", "RSI 14", "MACD 12,26,9", "Volume", "Log scale"):
        assert boxes[name].toolTip(), name
    dist = loaded_window.mc_view.findChildren(type(loaded_window.range_box))
    tips = [b.itemData(i, Qt.ToolTipRole) for b in dist for i in range(b.count())]
    assert any(t and "fat" in t.lower() for t in tips)
    for i in range(loaded_window.views.count()):
        assert loaded_window.views.tabToolTip(i)


def test_signal_readings_define_bullish_and_bearish(loaded_window):
    table = loaded_window.prediction.signals
    readings = [(table.item(i, 1).text(), table.item(i, 1).toolTip()) for i in range(table.rowCount())]
    for text, tip in readings:
        if re.search(r"bullish|bearish|overbought|oversold", text, re.I):
            assert tip, text


def test_research_note_terms_have_hover_titles(loaded_window, qtbot):
    loaded_window.run_research()
    qtbot.waitUntil(lambda: loaded_window.research.html() != "", timeout=60000)
    html = loaded_window.research.html()
    assert 'title="Conviction:' in html and 'title="Facts:' in html and "How to read it" in html


def test_glossary_dialog_finds_terms(loaded_window):
    from finlit_pro.ui.glossary_dialog import GlossaryDialog

    dlg = GlossaryDialog(loaded_window, "bullish")
    assert dlg.tree.currentItem().text(0) == "Bullish"
    assert "buyers are in control" in dlg.body.toPlainText()
    dlg.search.setText("zzzz-no-such-term")
    assert "No term matches" in dlg.body.toPlainText()


# ------------------------------------------------------------------ API key check


def test_key_check_reports_success_and_rejection(monkeypatch):
    import anthropic

    from finlit_pro.research import claude

    class FakeModels:
        def __init__(self, error=None):
            self.error = error

        def retrieve(self, model):
            if self.error:
                raise self.error
            return SimpleNamespace(id=model, display_name="Claude Opus 5.5")

    def client(error=None):
        return lambda **kw: SimpleNamespace(models=FakeModels(error))

    monkeypatch.setattr(claude.anthropic, "Anthropic", client())
    assert "Key works" in research.check_key("anthropic", "sk-ant-test", "claude-opus-5-5")
    denied = anthropic.AuthenticationError("bad key", response=SimpleNamespace(status_code=401, headers={}, request=None), body=None)
    monkeypatch.setattr(claude.anthropic, "Anthropic", client(denied))
    with pytest.raises(research.AnalysisError, match="rejected this key"):
        research.check_key("anthropic", "sk-ant-test", "claude-opus-5-5")
    with pytest.raises(research.AnalysisError, match="No key to test"):
        research.check_key("anthropic", "", "claude-opus-5-5")


def test_settings_test_button_shows_the_result(qtbot, monkeypatch):
    from finlit_pro.config import Settings
    from finlit_pro.ui.app import make_app

    make_app([])
    from finlit_pro.ui.settings_dialog import SettingsDialog

    monkeypatch.setattr(research, "check_key", lambda provider, key, model: f"Key works. {model} is available.")
    dlg = SettingsDialog(Settings())
    qtbot.addWidget(dlg)
    dlg.claude_key.edit.setText("sk-ant-api03-" + "x" * 40)
    dlg.claude_key.test()
    qtbot.waitUntil(lambda: "Key works" in dlg.claude_key.result.text(), timeout=10000)
    dlg.openai_key.edit.setText("not a key")
    dlg.openai_key.test()
    assert dlg.openai_key.result.text() and "Key works" not in dlg.openai_key.result.text()


def test_rich_text_notes_are_not_escaped_twice():
    note = glossary.explain_text("Bullish crossover, accelerating")
    combined = glossary.tip_for(glossary.lookup("MACD"), note)
    assert "&lt;table" not in combined and "<b>Bullish</b>" in combined
