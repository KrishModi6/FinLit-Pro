"""Smoke test of the real window, offscreen, on the DEMO ticker (no network)."""

import pytest

pytest.importorskip("PySide6")

from finlit_quant.config import Settings  # noqa: E402


@pytest.fixture
def window(qtbot):
    from finlit_quant.ui.app import make_app

    make_app([])
    from finlit_quant.ui.main_window import MainWindow

    w = MainWindow(Settings(watchlist=["DEMO"]))
    qtbot.addWidget(w)
    w.show()
    yield w
    w.runner.wait(10000)


def loaded(w):
    a = w.analysis
    return a is not None and a.mc is not None and a.fundamentals is not None and a.risk is not None


def test_demo_loads_into_every_tab(window, qtbot, tmp_path):
    window.load("DEMO")
    qtbot.waitUntil(lambda: loaded(window), timeout=60000)
    assert "Demo Robotics" in window.h_name.text()
    assert window.predictor_tab.pct_table.rowCount() == 7
    assert window.predictor_tab.sig_table.rowCount() == 6
    assert window.fund_tab.table.rowCount() > 10
    assert window.val_tab.sens.rowCount() == 5
    assert window.risk_tab.table.rowCount() > 15

    window.generate_memo()
    assert "## Verdict" in window.ai_tab.markdown()

    path = window.export_report(str(tmp_path / "report.html"))
    html = open(path, encoding="utf-8").read()
    assert "DEMO research report" in html and "data:image/png;base64" in html


@pytest.mark.parametrize("value", ["abc", "0", "-5", "2.5", ""])
def test_predictor_form_rejects_bad_paths(window, value):
    tab = window.predictor_tab
    tab.paths.set_text(value)
    assert tab.config() is None
    assert not tab.paths.error.isHidden()
    assert not tab.banner.isHidden()


def test_bad_ticker_shows_a_friendly_banner(window):
    window.load("NOT A TICKER")
    assert not window.banner.isHidden()
    assert "space" in window.banner.text.text()


def test_valuation_form_rejects_impossible_assumptions(window, qtbot):
    window.load("DEMO")
    qtbot.waitUntil(lambda: loaded(window), timeout=60000)
    tab = window.val_tab
    tab.f_disc.set_text("2")
    tab.f_term.set_text("3")
    tab._calculate()
    assert "must be higher" in tab.banner.text.text()
    tab.f_shares.set_text("zero")
    assert tab.read_inputs() is None
    assert not tab.f_shares.error.isHidden()


def test_compare_validates_ticker_list(window):
    window.compare_tab.tickers.set_text("DEMO")
    window.compare_tab._submit()
    assert "at least 2" in window.compare_tab.tickers.error.text()
