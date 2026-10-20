"""The real window, offscreen, on the DEMO ticker (no network, no API keys)."""

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")

from finlit_pro.config import Settings  # noqa: E402


@pytest.fixture
def window(qtbot, monkeypatch):
    from finlit_pro.data import http
    from finlit_pro.ui.app import make_app

    # DEMO must never reach a provider; fail loudly if anything tries.
    monkeypatch.setattr(http, "_session", lambda: (_ for _ in ()).throw(AssertionError("network used")))
    make_app([])
    from finlit_pro.ui.main_window import MainWindow

    w = MainWindow(Settings(watchlist=["DEMO"], ai_provider="rules"))
    qtbot.addWidget(w)
    w.show()
    yield w
    w.runner.wait(20000)


def loaded(w):
    ws = w.ws
    return ws is not None and ws.mc is not None and ws.forecast is not None and ws.fundamentals is not None and ws.risk is not None


def test_demo_loads_into_every_view(window, qtbot, tmp_path):
    window.load("demo")
    qtbot.waitUntil(lambda: loaded(window), timeout=60000)
    ws = window.ws
    assert ws.symbol == "DEMO" and ws.is_demo
    assert "DEMO" in window.windowTitle()
    # Prediction view: the owner's model, its inputs, outputs and signals.
    assert window.prediction.inputs.rowCount() >= 6
    assert window.prediction.signals.rowCount() == 6
    assert window.prediction.quantiles.rowCount() == 5
    qtbot.waitUntil(lambda: window.ws.evaluation is not None, timeout=120000)
    assert window.prediction.ev_metrics.rowCount() > 10
    # Monte Carlo, returns and fundamentals.
    assert window.mc_view.pct_table.rowCount() == 8
    assert window.returns.metrics.rowCount() > 15
    assert window.fundamentals.table.rowCount() > 10
    # Every dataset in use is listed with its status, and DEMO is marked simulated.
    statuses = {window.sources.item(r, 2).text() for r in range(window.sources.rowCount())}
    assert statuses == {"Simulated"}

    window.run_research()
    qtbot.waitUntil(lambda: window.research.html() != "", timeout=60000)
    html = window.research.html()
    assert "Facts" in html or "FACTS" in html.upper()
    assert ">S1<" in html and "Sources" in html  # citations rendered and listed

    path = window.export_report(str(tmp_path / "report.html"))
    report = open(path, encoding="utf-8").read()
    assert "DEMO research report" in report and "data:image/png;base64" in report and "Simulated" in report


def test_range_presets_and_custom_dates(window, qtbot):
    window.load("DEMO")
    qtbot.waitUntil(lambda: loaded(window), timeout=60000)
    window.range_box.setCurrentText("3M")
    n3m = len(window.chart._frame)
    window.range_box.setCurrentText("5Y")
    assert len(window.chart._frame) > n3m * 10
    window.range_box.setCurrentText("Custom")
    window.date_from.setDate(window.date_to.date().addDays(5))
    assert not window.notice.isHidden()
    assert "start date must be before" in window.notice.text.text()


@pytest.mark.parametrize("value", ["abc", "0", "-5", "2.5", ""])
def test_monte_carlo_form_rejects_bad_simulation_counts(window, value):
    view = window.mc_view
    view.paths.set_text(value)
    assert view.config() is None
    assert not view.paths.error.isHidden()
    assert not view.notice.isHidden()


def test_bad_ticker_shows_a_friendly_message(window):
    window.load("NOT A TICKER")
    assert not window.notice.isHidden()
    assert "space" in window.notice.text.text()


def test_valuation_form_rejects_impossible_assumptions(window, qtbot):
    window.load("DEMO")
    qtbot.waitUntil(lambda: loaded(window), timeout=60000)
    view = window.fundamentals.valuation
    view.f_disc.set_text("2")
    view.f_term.set_text("3")
    view._calculate()
    assert "must be higher" in view.banner.text.text()
    view.f_shares.set_text("zero")
    assert view.read_inputs() is None
    assert not view.f_shares.error.isHidden()


@pytest.mark.parametrize("field,value", [("premium", ""), ("premium", "-1"), ("strike", "abc"), ("contracts", "0"), ("contracts", "1.5")])
def test_options_calculator_validates_every_input(window, qtbot, field, value):
    window.load("DEMO")
    qtbot.waitUntil(lambda: loaded(window), timeout=60000)
    view = window.options
    view.premium.set_text("2.00")
    getattr(view, field).set_text(value)
    view.analyze()
    assert not getattr(view, field).error.isHidden()
    assert "highlighted" in view.calc_notice.text.text()
    assert view.res_frame.isHidden()


def test_options_calculator_gives_a_verdict(window, qtbot):
    window.load("DEMO")
    qtbot.waitUntil(lambda: loaded(window), timeout=60000)
    view = window.options
    view.premium.set_text("2.00")
    view.analyze()
    assert view.verdict.text().split(" at ")[0] in ("Worth it", "Not worth it", "Marginal")
    assert view.scenarios.rowCount() == 3  # market-implied, your assumptions, fat-tailed Monte Carlo


class PointModel:
    """The smallest model the integration point accepts: a point forecast, no bands, no score."""

    key, name, version, description = "test-point", "Point model", "0.1", "Last close plus 1%."
    horizons, simulations = (5, 30), (1,)
    lookback_calendar_days = 30
    bullish, bearish = ("UP",), ("DOWN",)

    def input_spec(self, horizon, simulations):
        from finlit_pro.model.interface import InputSpec

        return [InputSpec("Price history", "last close", "Only the latest adjusted close")]

    def predict(self, bars, horizon, simulations, seed=42):
        from finlit_pro.model.interface import Forecast

        p = float(bars["adjclose"].iloc[-1])
        return Forecast(self.name, self.version, bars.index[-1], horizon, p, p * 1.01, "UP")


def test_a_connected_model_plugs_in_without_other_changes(window, qtbot):
    from finlit_pro.model import registry

    registry.register(PointModel())
    try:
        window.prediction.model.addItem("Point model v0.1", "test-point")
        window.load("DEMO")
        qtbot.waitUntil(lambda: loaded(window), timeout=60000)
        window.prediction.model.setCurrentIndex(window.prediction.model.findData("test-point"))
        window.run_model(*window.prediction.selection())
        qtbot.waitUntil(lambda: window.ws.forecast.model == "Point model", timeout=30000)
        qtbot.waitUntil(lambda: window.ws.evaluation is not None and window.ws.evaluation.model_key == "test-point", timeout=60000)
        assert window.prediction.kpis.kpi("score").value.text() == "n/a"
        assert window.ws.evaluation.metric("Directional hit rate") is not None
    finally:
        registry.MODELS.pop("test-point", None)
