"""User settings and on-disk locations.

Settings live in one JSON file in the platform's per-user config folder.
API keys can come from the environment instead (ANTHROPIC_API_KEY,
OPENAI_API_KEY), and the environment always wins, so a key never has to be
written to disk at all.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

APP_DIR_NAME = "FinLitQuant"


def _base_dir(kind: str) -> Path:
    """Per-user folder for 'config' or 'cache', following each OS's convention."""
    override = os.environ.get("FINLIT_QUANT_HOME")
    if override:
        return Path(override) / kind

    home = Path.home()
    if sys.platform.startswith("win"):
        root = Path(os.environ.get("LOCALAPPDATA" if kind == "cache" else "APPDATA", home))
        return root / APP_DIR_NAME / kind
    if sys.platform == "darwin":
        sub = "Caches" if kind == "cache" else "Application Support"
        return home / "Library" / sub / APP_DIR_NAME
    xdg = "XDG_CACHE_HOME" if kind == "cache" else "XDG_CONFIG_HOME"
    default = home / (".cache" if kind == "cache" else ".config")
    return Path(os.environ.get(xdg, default)) / "finlit-quant"


def config_dir() -> Path:
    path = _base_dir("config")
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_dir() -> Path:
    path = _base_dir("cache")
    path.mkdir(parents=True, exist_ok=True)
    return path


CLAUDE_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
OPENAI_MODELS = ["gpt-5.6-luna", "gpt-5.4-nano"]


@dataclass
class Settings:
    # "auto" picks Claude if a Claude key exists, then OpenAI, then offline.
    ai_provider: str = "auto"
    anthropic_api_key: str = ""
    anthropic_model: str = CLAUDE_MODELS[0]
    anthropic_effort: str = "high"
    openai_api_key: str = ""
    openai_model: str = OPENAI_MODELS[0]
    # SEC asks every client to identify itself with a contact email.
    sec_contact_email: str = ""
    benchmark: str = "SPY"
    # Used only when the live 13-week T-bill yield cannot be fetched.
    risk_free_rate_pct: float = 4.0
    default_range: str = "1y"
    watchlist: list[str] = field(default_factory=lambda: ["AAPL", "MSFT", "NVDA", "SPY", "DEMO"])
    last_symbol: str = "AAPL"

    # Resolved keys: the environment wins over the file.
    def claude_key(self) -> str:
        return os.environ.get("ANTHROPIC_API_KEY", "").strip() or self.anthropic_api_key.strip()

    def openai_key(self) -> str:
        return os.environ.get("OPENAI_API_KEY", "").strip() or self.openai_api_key.strip()

    def resolved_provider(self) -> str:
        if self.ai_provider in ("claude", "openai", "offline"):
            return self.ai_provider
        if self.claude_key():
            return "claude"
        if self.openai_key():
            return "openai"
        return "offline"


def settings_path() -> Path:
    return config_dir() / "settings.json"


def load_settings() -> Settings:
    path = settings_path()
    if not path.exists():
        return Settings()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A corrupt file should cost the user their preferences, not the app.
        return Settings()
    known = {f.name for f in fields(Settings)}
    return Settings(**{k: v for k, v in raw.items() if k in known})


def save_settings(settings: Settings) -> None:
    path = settings_path()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
    # The file can hold API keys, so keep it readable by this user only.
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(path)
