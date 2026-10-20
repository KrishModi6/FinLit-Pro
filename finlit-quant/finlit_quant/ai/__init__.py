"""The AI analyst: Claude or OpenAI when a key is set, a rule-based analyst otherwise."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol

from finlit_quant.config import Settings


class AIError(RuntimeError):
    """An AI provider failure with a message fit to show the user."""


class Provider(Protocol):
    label: str
    served_model: str | None

    def stream(self, system: str, messages: list[dict]) -> Iterator[str]: ...


def make_provider(settings: Settings) -> Provider | None:
    """The configured provider, or None for the offline analyst."""
    choice = settings.resolved_provider()
    if choice == "claude":
        key = settings.claude_key()
        if not key:
            raise AIError("Claude is selected but no Anthropic API key is set. Add one in Settings, or switch the provider to Offline.")
        from finlit_quant.ai.claude import ClaudeProvider

        return ClaudeProvider(key, settings.anthropic_model, settings.anthropic_effort)
    if choice == "openai":
        key = settings.openai_key()
        if not key:
            raise AIError("OpenAI is selected but no OpenAI API key is set. Add one in Settings, or switch the provider to Offline.")
        from finlit_quant.ai.openai_provider import OpenAIProvider

        return OpenAIProvider(key, settings.openai_model)
    return None
