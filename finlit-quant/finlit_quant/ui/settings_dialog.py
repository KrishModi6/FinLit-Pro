"""Settings: AI provider and keys, SEC contact email, benchmark, risk-free fallback."""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from finlit_quant import validation
from finlit_quant.config import CLAUDE_MODELS, OPENAI_MODELS, Settings, settings_path
from finlit_quant.data import http
from finlit_quant.ui.widgets import Banner, label

PROVIDERS = [("auto", "Automatic (Claude, then OpenAI, then offline)"), ("claude", "Claude (Anthropic)"), ("openai", "OpenAI"), ("offline", "Offline rule-based analyst")]


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(620)
        self.result_settings: Settings | None = None
        self.original = settings
        root = QVBoxLayout(self)
        root.setSpacing(12)
        self.banner = Banner()
        root.addWidget(self.banner)

        root.addWidget(label("AI analyst", "H2"))
        ai = QFormLayout()
        self.provider = QComboBox()
        for key, name in PROVIDERS:
            self.provider.addItem(name, key)
        self.provider.setCurrentIndex(max(0, [k for k, _ in PROVIDERS].index(settings.ai_provider) if settings.ai_provider in dict(PROVIDERS) else 0))
        ai.addRow("Provider", self.provider)
        self.claude_key = QLineEdit(settings.anthropic_api_key)
        self.claude_key.setEchoMode(QLineEdit.Password)
        self.claude_key.setPlaceholderText("sk-ant-...  (or set ANTHROPIC_API_KEY)")
        ai.addRow("Anthropic API key", self.claude_key)
        self.claude_model = QComboBox()
        self.claude_model.setEditable(True)
        self.claude_model.addItems(CLAUDE_MODELS)
        self.claude_model.setCurrentText(settings.anthropic_model)
        ai.addRow("Claude model", self.claude_model)
        self.effort = QComboBox()
        self.effort.addItems(["low", "medium", "high", "xhigh"])
        self.effort.setCurrentText(settings.anthropic_effort)
        self.effort.setToolTip("How hard Claude thinks before writing. Higher is slower, deeper and costs more.")
        ai.addRow("Claude effort", self.effort)
        self.openai_key = QLineEdit(settings.openai_api_key)
        self.openai_key.setEchoMode(QLineEdit.Password)
        self.openai_key.setPlaceholderText("sk-...  (or set OPENAI_API_KEY)")
        ai.addRow("OpenAI API key", self.openai_key)
        self.openai_model = QComboBox()
        self.openai_model.setEditable(True)
        self.openai_model.addItems(OPENAI_MODELS)
        self.openai_model.setCurrentText(settings.openai_model)
        ai.addRow("OpenAI model", self.openai_model)
        root.addLayout(ai)
        root.addWidget(label(
            f"Keys are stored in {settings_path()} with owner-only permissions. Environment variables, if set, take priority and are never written to disk.",
            "Muted", wrap=True,
        ))

        root.addWidget(label("Data", "H2"))
        data = QFormLayout()
        self.email = QLineEdit(settings.sec_contact_email)
        self.email.setPlaceholderText("name@example.com")
        self.email.setToolTip("The SEC requires a contact email in the User-Agent of every EDGAR request.")
        data.addRow("SEC contact email", self.email)
        self.benchmark = QLineEdit(settings.benchmark)
        data.addRow("Default benchmark", self.benchmark)
        self.rf = QLineEdit(f"{settings.risk_free_rate_pct:g}")
        self.rf.setToolTip("Used only when the live 13-week T-bill yield cannot be fetched.")
        data.addRow("Fallback risk-free rate (%)", self.rf)
        root.addLayout(data)

        cache_row = QHBoxLayout()
        clear = QPushButton("Clear downloaded data cache")
        clear.clicked.connect(self._clear_cache)
        cache_row.addWidget(clear)
        cache_row.addStretch(1)
        root.addLayout(cache_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _clear_cache(self) -> None:
        n = http.cache().clear()
        QMessageBox.information(self, "Cache cleared", f"Removed {n} cached responses. The next load fetches fresh data.")

    def _save(self) -> None:
        try:
            claude_key = validation.api_key(self.claude_key.text(), "Anthropic")
            openai_key = validation.api_key(self.openai_key.text(), "OpenAI")
            email = validation.email(self.email.text()) if self.email.text().strip() else ""
            bench = validation.ticker(self.benchmark.text())
            rf = validation.number(self.rf.text(), "Fallback risk-free rate", 0, 20)
            claude_model = self.claude_model.currentText().strip()
            openai_model = self.openai_model.currentText().strip()
            if not claude_model or not openai_model:
                raise validation.ValidationError("Model names cannot be blank. Pick one from the list.")
        except validation.ValidationError as exc:
            self.banner.show_message(str(exc), "error")
            return
        provider = self.provider.currentData()
        if provider == "claude" and not (claude_key or self.original.claude_key()):
            self.banner.show_message("Claude is selected but there is no Anthropic key. Paste one, or choose Automatic or Offline.", "error")
            return
        if provider == "openai" and not (openai_key or self.original.openai_key()):
            self.banner.show_message("OpenAI is selected but there is no OpenAI key. Paste one, or choose Automatic or Offline.", "error")
            return
        self.result_settings = replace(
            self.original,
            ai_provider=provider,
            anthropic_api_key=claude_key,
            anthropic_model=claude_model,
            anthropic_effort=self.effort.currentText(),
            openai_api_key=openai_key,
            openai_model=openai_model,
            sec_contact_email=email,
            benchmark=bench,
            risk_free_rate_pct=rf,
        )
        self.accept()
