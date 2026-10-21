"""The research note: brief tagging, citation checks, the rules engine, and both API engines with fake clients."""

import json
from types import SimpleNamespace

import pytest

from finlit_pro import credentials, pipeline, research
from finlit_pro.config import Settings
from finlit_pro.research import brief, note, prompt, render, rules
from finlit_pro.research.note import NoteError


@pytest.fixture(scope="module")
def demo_ws():
    return pipeline.load("DEMO", evaluate=True, read_filings=False)


def test_every_brief_line_with_a_figure_carries_a_source_tag(demo_ws):
    text, reg = brief.build(demo_ws)
    ids = reg.ids()
    assert {"S1", "S2"} <= ids
    body, sources = text.split("## Source list")
    checked = 0
    for line in body.splitlines():
        if line.strip() and not line.startswith(("#", "NOTE")):
            assert "[S" in line, line
            checked += 1
    assert checked > 20
    # The source list names every ID, with its provenance.
    for sid in ids:
        assert f"\n{sid}: " in sources


def good_note(reg):
    return {
        "summary": "A test summary.",
        "recommendation": "Hold",
        "conviction": "Medium",
        "horizon": "6 to 12 months",
        "facts": [
            {"topic": "Price and risk", "statement": "Price fact.", "sources": ["S1"]},
            {"topic": "Valuation", "statement": "Made-up fact.", "sources": ["S999"]},
            {"topic": "Other", "statement": "Uncited fact.", "sources": []},
        ],
        "interpretation": [{"statement": "A view.", "confidence": "Very high", "based_on": ["[s1]", "S1"]}],
        "risks": [{"risk": "A risk.", "sources": ["S2"]}],
        "uncertainties": [{"issue": "Small sample.", "effect": "Conclusions are tentative."}],
        "data_gaps": ["No filing text."],
    }


def test_citations_are_checked_and_unverified_facts_flagged(demo_ws):
    _, reg = brief.build(demo_ws)
    n = note.parse(json.dumps(good_note(reg)), reg, "test")
    assert [f.verified for f in n.facts] == [True, False, False]
    assert n.interpretation[0].based_on == ["S1"]  # brackets and case normalised, duplicates dropped
    assert n.interpretation[0].confidence == "Low"  # outside the schema's levels
    assert any("unverified" in w for w in n.warnings)


@pytest.mark.parametrize("text", ["not json", "[1, 2]", json.dumps({"summary": "only"})])
def test_malformed_engine_output_is_a_friendly_error(demo_ws, text):
    _, reg = brief.build(demo_ws)
    with pytest.raises(NoteError, match="Run it again"):
        note.parse(text, reg, "test")


def test_rules_engine_separates_facts_from_interpretation(demo_ws):
    _, reg = brief.build(demo_ws)
    n = rules.build_note(demo_ws, reg)
    assert n.recommendation in note.RECOMMENDATIONS and n.conviction in note.LEVELS
    assert n.facts and all(f.verified for f in n.facts)
    assert all(set(f.sources) <= reg.ids() for f in n.facts)
    assert n.interpretation and all(i.confidence in note.LEVELS for i in n.interpretation)
    assert any("filing text" in u.issue.lower() or "filing" in u.effect.lower() for u in n.uncertainties)
    html = render.to_html(n, reg, "DEMO")
    assert "Interpretation" in html or "INTERPRETATION" in html.upper()


def test_engine_selection_never_uses_a_missing_key(monkeypatch):
    monkeypatch.setattr(credentials, "get", lambda name: None)
    assert research.engine_for(Settings(ai_provider="auto")) is None
    with pytest.raises(research.AnalysisError, match="no Anthropic API key"):
        research.engine_for(Settings(ai_provider="claude"))
    with pytest.raises(research.AnalysisError, match="no OpenAI API key"):
        research.engine_for(Settings(ai_provider="openai"))


def test_prompt_states_the_ground_rules():
    s = prompt.SYSTEM
    assert "Every fact must cite" in s and "interpretation" in s and "unverified" in s and "No recommendation" in s
    assert "—" not in s


# --------------------------------------------------------------- Claude engine


class FakeStream:
    def __init__(self, text, stop_reason="end_turn", model="claude-opus-5-5"):
        self._text, self.stop_reason, self.model = text, stop_reason, model
        self.text_stream = [text[: len(text) // 2], text[len(text) // 2 :]]

    def __iter__(self):
        # The engine reads every stream event (text events carry the answer), as the SDK's MessageStream yields them.
        yield SimpleNamespace(type="message_start")
        for part in self.text_stream:
            yield SimpleNamespace(type="text", text=part)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return SimpleNamespace(stop_reason=self.stop_reason, model=self.model, content=[SimpleNamespace(type="text", text=self._text)])


def fake_anthropic(stream, calls):
    def make(**kwargs):
        calls.append(kwargs)
        return stream

    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=make)), messages=SimpleNamespace(stream=make))


def test_claude_engine_requests_structured_output_with_fallbacks(demo_ws, monkeypatch):
    from finlit_pro.research.claude import ClaudeEngine

    text, reg = brief.build(demo_ws)
    payload = json.dumps(good_note(reg))
    calls, progress = [], []
    engine = ClaudeEngine("sk-ant-test", "claude-opus-5-5", "high")
    engine.client = fake_anthropic(FakeStream(payload), calls)
    out = engine.run(prompt.SYSTEM, prompt.user_message(text), progress.append)
    assert out == payload and progress[-1] == len(payload)
    sent = calls[0]
    assert sent["model"] == "claude-opus-5-5" and sent["betas"] == ["server-side-fallback-2026-07-01"] and sent["fallbacks"] == "default"
    assert sent["output_config"]["format"]["schema"] is note.SCHEMA and sent["output_config"]["effort"] == "high"
    assert "thinking" not in sent  # adaptive thinking is the default


def test_claude_engine_without_server_fallback_uses_the_plain_stream(demo_ws):
    from finlit_pro.research.claude import ClaudeEngine

    calls = []
    engine = ClaudeEngine("sk-ant-test", "claude-haiku-5-5")
    engine.client = fake_anthropic(FakeStream("{}", model="claude-haiku-5-5"), calls)
    engine.run("s", "u")
    assert "betas" not in calls[0] and "fallbacks" not in calls[0]


@pytest.mark.parametrize("stop,message", [("refusal", "declined"), ("max_tokens", "output limit")])
def test_claude_engine_reports_stops(stop, message):
    from finlit_pro.research.claude import ClaudeEngine

    engine = ClaudeEngine("sk-ant-test", "claude-opus-5-5")
    engine.client = fake_anthropic(FakeStream("{}", stop_reason=stop), [])
    with pytest.raises(research.AnalysisError, match=message):
        engine.run("s", "u")


def test_claude_engine_can_be_cancelled():
    from finlit_pro.research.claude import ClaudeEngine

    engine = ClaudeEngine("sk-ant-test", "claude-opus-5-5")
    engine.client = fake_anthropic(FakeStream("{}" * 10), [])
    with pytest.raises(research.AnalysisError, match="cancelled"):
        engine.run("s", "u", cancelled=lambda: True)


def test_run_end_to_end_with_a_fake_claude(demo_ws, monkeypatch):
    from finlit_pro.research import claude

    text, reg = brief.build(demo_ws)
    payload = json.dumps(good_note(reg))
    monkeypatch.setattr(credentials, "get", lambda name: "sk-ant-test" if name == "anthropic" else None)
    monkeypatch.setattr(claude.ClaudeEngine, "run", lambda self, *a, **k: setattr(self, "served_model", "claude-opus-5-5") or payload)
    n, registry, brief_text = research.run(demo_ws, Settings(ai_provider="auto"))
    assert n.engine == "Claude claude-opus-5-5" and n.recommendation == "Hold"
    assert brief_text == text


# --------------------------------------------------------------- OpenAI engine


def test_openai_engine_uses_strict_json_schema_and_falls_back(monkeypatch):
    import openai

    from finlit_pro.research.openai_provider import FALLBACK_MODEL, OpenAIEngine

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        if kwargs["model"] != FALLBACK_MODEL:
            raise openai.NotFoundError("no such model", response=SimpleNamespace(status_code=404, headers={}, request=None), body=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": 1}', refusal=None))])

    engine = OpenAIEngine("sk-test", "gpt-5.6-luna")
    engine.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    assert engine.run("s", "u") == '{"ok": 1}'
    assert [c["model"] for c in calls] == ["gpt-5.6-luna", FALLBACK_MODEL] and engine.served_model == FALLBACK_MODEL
    fmt = calls[0]["response_format"]
    assert fmt["type"] == "json_schema" and fmt["json_schema"]["strict"] is True and fmt["json_schema"]["schema"] is note.SCHEMA


def test_openai_engine_reports_refusals():
    from finlit_pro.research.openai_provider import OpenAIEngine

    engine = OpenAIEngine("sk-test", "gpt-5.6-luna")
    engine.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **k: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None, refusal="no"))]))))
    with pytest.raises(research.AnalysisError, match="declined"):
        engine.run("s", "u")
