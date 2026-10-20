"""User settings and on-disk locations.

Settings hold preferences only. API keys are never written here: they live
in the operating system's credential store (see `credentials.py`). On
Windows that is Credential Manager, so keys are encrypted with the user's
login and never appear in a file in the app's folders.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

APP_DIR_NAME = "FinLitPro"


def _base_dir(kind: str) -> Path:
    """Per-user folder for 'config', 'cache' or 'data', following each OS's convention."""
    override = os.environ.get("FINLIT_PRO_HOME")
    if override:
        return Path(override) / kind
    home = Path.home()
    if sys.platform.startswith("win"):
        # %LOCALAPPDATA% for caches (not roamed), %APPDATA% for settings.
        root = Path(os.environ.get("LOCALAPPDATA" if kind == "cache" else "APPDATA", home))
        return root / APP_DIR_NAME / kind
    if sys.platform == "darwin":
        return home / "Library" / ("Caches" if kind == "cache" else "Application Support") / APP_DIR_NAME / kind
    xdg = {"cache": "XDG_CACHE_HOME", "config": "XDG_CONFIG_HOME", "data": "XDG_DATA_HOME"}[kind]
    default = home / {"cache": ".cache", "config": ".config", "data": ".local/share"}[kind]
    return Path(os.environ.get(xdg, default)) / "finlit-pro"


def app_dir(kind: str) -> Path:
    path = _base_dir(kind)
    path.mkdir(parents=True, exist_ok=True)
    return path


CLAUDE_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
OPENAI_MODELS = ["gpt-5.6-luna", "gpt-5.4-nano"]


@dataclass
class Settings:
    # Analysis provider: "auto" uses Claude if its key is stored, then OpenAI,
    # then the built-in rules engine.
    ai_provider: str = "auto"
    anthropic_model: str = CLAUDE_MODELS[0]
    anthropic_effort: str = "high"
    openai_model: str = OPENAI_MODELS[0]
    # Characters of each filing section passed to the analysis (about 4 per token).
    filing_section_chars: int = 40_000
    # SEC asks every client to identify itself with a contact email.
    sec_contact_email: str = ""
    benchmark: str = "SPY"
    risk_free_rate_pct: float = 4.0  # used only when the live T-bill yield is unavailable
    transaction_cost_bps: float = 5.0  # per side, for the model's strategy backtest
    default_range: str = "1Y"
    watchlist: list[str] = field(default_factory=lambda: ["AAPL", "MSFT", "NVDA", "SPY"])
    last_symbol: str = "AAPL"
    window_state: str = ""  # Qt saveState, hex encoded


def settings_path() -> Path:
    return app_dir("config") / "settings.json"


def load_settings() -> Settings:
    path = settings_path()
    if not path.exists():
        return Settings()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Settings()
    if not isinstance(raw, dict):
        return Settings()
    # Keep only known fields whose type matches the default, so a hand-edited or
    # older settings file can never put a string where a number belongs.
    defaults = Settings()
    clean = {}
    for f in fields(Settings):
        if f.name not in raw:
            continue
        value, expected = raw[f.name], type(getattr(defaults, f.name))
        if expected is float and isinstance(value, int) and not isinstance(value, bool):
            value = float(value)
        if isinstance(value, expected) and not (expected is not bool and isinstance(value, bool)):
            clean[f.name] = value
    if "watchlist" in clean:
        clean["watchlist"] = [s for s in clean["watchlist"] if isinstance(s, str)][:50]
    return Settings(**clean)


def save_settings(settings: Settings) -> None:
    path = settings_path()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
    tmp.replace(path)
