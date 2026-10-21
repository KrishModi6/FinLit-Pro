"""The research panel: a cited note on the filings and financial data.

    brief, registry = brief.build(workspace)
    note = research.run(workspace, settings)

Engines: Claude or OpenAI when a key is stored (structured JSON output), or
the built-in rules engine. All three return the same `Note`.
"""

from __future__ import annotations

from collections.abc import Callable


class AnalysisError(RuntimeError):
    """An analysis failure with a message fit to show the user."""


def engine_for(settings):
    """The configured language-model engine, or None for the rules engine."""
    from finlit_pro import credentials

    choice = settings.ai_provider
    claude_key, openai_key = credentials.get("anthropic"), credentials.get("openai")
    if choice == "auto":
        choice = "claude" if claude_key else ("openai" if openai_key else "rules")
    if choice == "claude":
        if not claude_key:
            raise AnalysisError("Claude is selected but no Anthropic API key is stored. Add one in Settings > Analysis, or choose the rules engine.")
        from finlit_pro.research.claude import ClaudeEngine

        return ClaudeEngine(claude_key, settings.anthropic_model, settings.anthropic_effort)
    if choice == "openai":
        if not openai_key:
            raise AnalysisError("OpenAI is selected but no OpenAI API key is stored. Add one in Settings > Analysis, or choose the rules engine.")
        from finlit_pro.research.openai_provider import OpenAIEngine

        return OpenAIEngine(openai_key, settings.openai_model)
    return None


def run(workspace, settings, progress: Callable[[int], None] | None = None, cancelled: Callable[[], bool] | None = None):
    """Build the brief, run the engine, return (note, registry, brief)."""
    from finlit_pro.research import brief as brief_mod
    from finlit_pro.research import note as note_mod
    from finlit_pro.research import prompt, rules

    text, registry = brief_mod.build(workspace)
    engine = engine_for(settings)
    if engine is None:
        return rules.build_note(workspace, registry), registry, text
    raw = engine.run(prompt.SYSTEM, prompt.user_message(text), progress, cancelled)
    label = engine.label + (f" (served by {engine.served_model})" if engine.served_model and engine.served_model not in engine.label else "")
    return note_mod.parse(raw, registry, label), registry, text


def check_key(provider: str, api_key: str, model: str) -> str:
    """A one-line result of testing a key against its provider's Models API. Raises AnalysisError on failure."""
    if not api_key:
        raise AnalysisError("No key to test. Paste one in the box, or store one first.")
    if provider == "anthropic":
        from finlit_pro.research.claude import check_access
    else:
        from finlit_pro.research.openai_provider import check_access
    return check_access(api_key, model)
