import anthropic

try:  # anthropic>=1.16 and openai>=3 build on httpx2
    import httpx2 as httpx
except ImportError:  # older SDKs used httpx
    import httpx
import openai
import pytest

from finlit_quant.ai import AIError, brief, make_provider, offline
from finlit_quant.ai.claude import FALLBACK_BETA, ClaudeProvider
from finlit_quant.ai.openai_provider import FALLBACK_MODEL, OpenAIProvider
from finlit_quant.analytics.montecarlo import MCConfig
from finlit_quant.config import Settings
from finlit_quant.pipeline import analyze


@pytest.fixture(scope="module")
def demo():
    return analyze("DEMO", mc_config=MCConfig(n_paths=2000, horizon_days=63))


def test_brief_contains_every_section(demo):
    text = brief.build(demo)
    for needle in ("SIMULATED demo data", "## Price", "## Fundamentals", "Piotroski", "Altman", "## Risk", "## Monte Carlo", "Calibration", "signal engine", "Reverse DCF"):
        assert needle in text, needle
    assert "\u2014" not in text  # no em dashes anywhere the model reads


def test_system_prompt_rules():
    assert "Never use em dashes" in brief.SYSTEM_PROMPT
    assert "Do not invent figures" in brief.SYSTEM_PROMPT


def test_offline_memo_has_a_verdict_and_labels_demo(demo):
    memo = offline.memo(demo)
    assert memo.startswith("> **Simulated demo data.**")
    assert "## Verdict" in memo and "## Monte Carlo read" in memo
    assert any(word in memo for word in ("**Bullish**", "**Neutral**", "**Bearish**"))


def test_provider_selection(monkeypatch):
    assert make_provider(Settings(ai_provider="offline")) is None
    assert make_provider(Settings(ai_provider="auto")) is None
    with pytest.raises(AIError, match="no Anthropic API key"):
        make_provider(Settings(ai_provider="claude"))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-0000000000000000")
    assert isinstance(make_provider(Settings(ai_provider="auto")), ClaudeProvider)


class FakeStream:
    def __init__(self, texts, stop="end_turn"):
        self.text_stream = iter(texts)
        self.stop = stop

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return type("Msg", (), {"stop_reason": self.stop, "model": "claude-opus-5-5"})()


class Recorder:
    def __init__(self, result):
        self.result = result
        self.kwargs = None

    def stream(self, **kwargs):
        self.kwargs = kwargs
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def make_claude(model, beta_result=None, plain_result=None):
    p = ClaudeProvider("sk-ant-test-0000000000000000", model, "high")
    beta, plain = Recorder(beta_result), Recorder(plain_result)
    p.client = type("C", (), {"beta": type("B", (), {"messages": beta})(), "messages": plain})()
    return p, beta, plain


def test_claude_streams_with_server_side_fallbacks():
    p, beta, _ = make_claude("claude-opus-5-5", beta_result=FakeStream(["Hello ", "PM"]))
    out = "".join(p.stream("sys", [{"role": "user", "content": "hi"}]))
    assert out == "Hello PM"
    assert beta.kwargs["fallbacks"] == "default"
    assert beta.kwargs["betas"] == [FALLBACK_BETA]
    assert beta.kwargs["output_config"] == {"effort": "high"}
    assert "thinking" not in beta.kwargs  # adaptive by default; never send a budget
    assert p.served_model == "claude-opus-5-5"


def test_claude_haiku_uses_plain_endpoint_and_reports_refusal():
    p, beta, plain = make_claude("claude-haiku-5-5", plain_result=FakeStream(["x"], stop="refusal"))
    out = "".join(p.stream("sys", [{"role": "user", "content": "hi"}]))
    assert beta.kwargs is None and "fallbacks" not in plain.kwargs
    assert "declined" in out


def _response(status):
    return httpx.Response(status, request=httpx.Request("POST", "https://api.test"))


def test_claude_errors_become_friendly():
    err = anthropic.AuthenticationError("bad key", response=_response(401), body=None)
    p, _, _ = make_claude("claude-opus-5-5", beta_result=err)
    with pytest.raises(AIError, match="rejected the API key"):
        list(p.stream("sys", []))


def test_openai_falls_back_when_model_unavailable():
    calls = []

    class Completions:
        def create(self, **kw):
            calls.append(kw["model"])
            if kw["model"] != FALLBACK_MODEL:
                raise openai.NotFoundError("no such model", response=_response(404), body=None)
            delta = type("D", (), {"content": "ok"})()
            choice = type("Ch", (), {"delta": delta})()
            return iter([type("Chunk", (), {"choices": [choice]})()])

    p = OpenAIProvider("sk-test-000000000000000000000", "gpt-5.6-luna")
    p.client = type("C", (), {"chat": type("Chat", (), {"completions": Completions()})()})()
    assert "".join(p.stream("sys", [{"role": "user", "content": "q"}])) == "ok"
    assert calls == ["gpt-5.6-luna", FALLBACK_MODEL]
    assert p.served_model == FALLBACK_MODEL
