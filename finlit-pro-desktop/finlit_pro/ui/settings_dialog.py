"""Settings: data sources, analysis engine and credentials."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from finlit_pro import credentials, research, validation
from finlit_pro.config import CLAUDE_MODELS, OPENAI_MODELS, Settings, settings_path
from finlit_pro.data import http
from finlit_pro.ui import theme
from finlit_pro.ui.widgets import Notice, install_tooltips, label
from finlit_pro.ui.workers import Job, Runner

PROVIDERS = [("auto", "Automatic: Claude, then OpenAI, then rules engine"), ("claude", "Claude (Anthropic)"), ("openai", "OpenAI"), ("rules", "Rules engine (no API key)")]


class KeyRow(QWidget):
    """Write-only key entry: shows whether a key is stored, never the key, and can test it."""

    def __init__(self, name: str, placeholder: str, model: Callable[[], str]) -> None:
        super().__init__()
        self.name = name
        self.model = model
        self.runner = Runner()
        self._test_id = 0
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        row = QHBoxLayout()
        self.edit = QLineEdit()
        self.edit.setEchoMode(QLineEdit.Password)
        self.edit.setPlaceholderText(placeholder)
        self.test_btn = QPushButton("Test key")
        self.test_btn.setToolTip("Checks the key typed here (or the stored one) and the selected model with the provider's Models API. No tokens are used.")
        self.test_btn.clicked.connect(self.test)
        row.addWidget(self.edit, 1)
        row.addWidget(self.test_btn)
        self.remove = QCheckBox("Remove the stored key")
        self.status = label("", "Small", wrap=True)
        self.result = label("", "Small", wrap=True)
        lay.addLayout(row)
        lay.addWidget(self.remove)
        lay.addWidget(self.status)
        lay.addWidget(self.result)
        self.refresh()

    def refresh(self) -> None:
        where = credentials.source(self.name)
        self.status.setText(f"Current key: {where}." + (" Leave blank to keep it." if where != "not set" else ""))
        self.remove.setVisible(where == "credential store")

    def test(self) -> None:
        typed = self.edit.text().strip()
        try:
            key = validation.api_key(typed, "Anthropic" if self.name == "anthropic" else "OpenAI") if typed else credentials.get(self.name)
        except validation.ValidationError as exc:
            self._show(str(exc), False)
            return
        self._test_id += 1
        self.test_btn.setEnabled(False)
        self.result.setStyleSheet(f"color: {theme.MUTED};")
        self.result.setText("Testing...")
        self.runner.start(Job(self._test_id, research.check_key, self.name, key, self.model()), lambda _r, msg: self._show(msg, True), lambda _r, msg: self._show(msg, False))

    def _show(self, message: str, ok: bool) -> None:
        self.test_btn.setEnabled(True)
        self.result.setStyleSheet(f"color: {theme.UP if ok else theme.DOWN};")
        self.result.setText(message)


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(620)
        self.original = settings
        self.result_settings: Settings | None = None
        root = QVBoxLayout(self)
        self.notice = Notice()
        root.addWidget(self.notice)
        tabs = QTabWidget()
        root.addWidget(tabs)

        data = QWidget()
        form = QFormLayout(data)
        self.email = QLineEdit(settings.sec_contact_email)
        self.email.setPlaceholderText("name@example.com")
        form.addRow("SEC contact email", self.email)
        form.addRow("", label("Required by the SEC in the User-Agent of every EDGAR request; sent only to sec.gov.", "Small", wrap=True))
        self.benchmark = QLineEdit(settings.benchmark)
        form.addRow("Default benchmark", self.benchmark)
        self.rf = QLineEdit(f"{settings.risk_free_rate_pct:g}")
        form.addRow("Fallback risk-free rate (%)", self.rf)
        self.cost = QLineEdit(f"{settings.transaction_cost_bps:g}")
        form.addRow("Transaction cost (bp per trade)", self.cost)
        clear = QPushButton("Clear downloaded data")
        clear.clicked.connect(self._clear_cache)
        form.addRow("Cache", clear)
        tabs.addTab(data, "Data")

        ana = QWidget()
        form = QFormLayout(ana)
        self.provider = QComboBox()
        for key, name in PROVIDERS:
            self.provider.addItem(name, key)
        self.provider.setCurrentIndex(next((i for i, (k, _) in enumerate(PROVIDERS) if k == settings.ai_provider), 0))
        form.addRow("Engine", self.provider)
        self.claude_model = QComboBox()
        self.claude_model.setEditable(True)
        self.claude_model.addItems(CLAUDE_MODELS)
        self.claude_model.setCurrentText(settings.anthropic_model)
        self.claude_key = KeyRow("anthropic", "Paste a new Anthropic key to store it", lambda: self.claude_model.currentText().strip() or CLAUDE_MODELS[0])
        form.addRow("Anthropic API key", self.claude_key)
        form.addRow("Claude model", self.claude_model)
        self.effort = QComboBox()
        self.effort.addItems(["low", "medium", "high", "xhigh"])
        self.effort.setCurrentText(settings.anthropic_effort)
        form.addRow("Claude effort", self.effort)
        self.openai_model = QComboBox()
        self.openai_model.setEditable(True)
        self.openai_model.addItems(OPENAI_MODELS)
        self.openai_model.setCurrentText(settings.openai_model)
        self.openai_key = KeyRow("openai", "Paste a new OpenAI key to store it", lambda: self.openai_model.currentText().strip() or OPENAI_MODELS[0])
        form.addRow("OpenAI API key", self.openai_key)
        form.addRow("OpenAI model", self.openai_model)
        self.chars = QLineEdit(str(settings.filing_section_chars))
        form.addRow("Filing excerpt length (characters per section)", self.chars)
        form.addRow("", label(f"Keys are kept in the system credential store ({credentials.backend()}), never in {settings_path().name}. "
                              "ANTHROPIC_API_KEY and OPENAI_API_KEY environment variables take precedence.", "Small", wrap=True))
        tabs.addTab(ana, "Analysis")

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        install_tooltips(self)

    def _clear_cache(self) -> None:
        n = http.cache().clear()
        QMessageBox.information(self, "Cache cleared", f"Removed {n} cached responses.")

    def _save(self) -> None:
        try:
            email = validation.email(self.email.text()) if self.email.text().strip() else ""
            bench = validation.ticker(self.benchmark.text())
            rf = validation.number(self.rf.text(), "Fallback risk-free rate", 0, 25)
            cost = validation.number(self.cost.text(), "Transaction cost", 0, 200)
            chars = validation.positive_int(self.chars.text(), "Filing excerpt length", 2_000, 400_000)
            new_keys = {
                "anthropic": validation.api_key(self.claude_key.edit.text(), "Anthropic"),
                "openai": validation.api_key(self.openai_key.edit.text(), "OpenAI"),
            }
        except validation.ValidationError as exc:
            self.notice.show_message(str(exc), "error")
            return
        try:
            for row in (self.claude_key, self.openai_key):
                if new_keys[row.name]:
                    credentials.store(row.name, new_keys[row.name])
                elif row.remove.isChecked():
                    credentials.store(row.name, "")
        except credentials.CredentialError as exc:
            self.notice.show_message(str(exc), "error")
            return
        provider = self.provider.currentData()
        if provider == "claude" and not credentials.get("anthropic"):
            self.notice.show_message("Claude is selected but no Anthropic key is stored.", "error")
            return
        if provider == "openai" and not credentials.get("openai"):
            self.notice.show_message("OpenAI is selected but no OpenAI key is stored.", "error")
            return
        self.result_settings = replace(
            self.original,
            sec_contact_email=email,
            benchmark=bench,
            risk_free_rate_pct=rf,
            transaction_cost_bps=cost,
            ai_provider=provider,
            anthropic_model=self.claude_model.currentText().strip() or CLAUDE_MODELS[0],
            anthropic_effort=self.effort.currentText(),
            openai_model=self.openai_model.currentText().strip() or OPENAI_MODELS[0],
            filing_section_chars=chars,
        )
        self.accept()
