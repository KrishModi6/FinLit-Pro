"""Regression tests for the second round of research, validation and settings fixes (see docs/FIXLOG.md)."""

import copy
import dataclasses
import json
import re
from types import SimpleNamespace

import anthropic
import openai
import pandas as pd
import pytest

from finlit_pro import config, credentials, fmt, pipeline, research, validation
from finlit_pro.analytics.risk import RANGE_DAYS
from finlit_pro.research import brief, note, rules


@pytest.fixture(scope="module")
def demo_ws():
    return pipeline.load("DEMO", evaluate=False, read_filings=False)


def _response(status=200):
    return SimpleNamespace(status_code=status, headers={}, request=None)


# --------------------------------------------------------------- Claude engine


class EventStream:
    """A stand-in for the SDK's MessageStream: yields events, then gives the final message."""

    def __init__(self, blocks, stop_reason="end_turn", events=None, error=None):
        self.blocks, self.stop_reason, self.error = blocks, stop_reason, error
        self.events = events if events is not None else [SimpleNamespace(type="text", text=b) for b in blocks]
        self.seen = 0
        self.closed = False

    def __iter__(self):
        for e in self.events:
            self.seen += 1
            yield e
        if self.error:
            raise self.error

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.closed = True
        return False

    def get_final_message(self):
        content = [SimpleNamespace(type="thinking", thinking="...")] + [SimpleNamespace(type="text", text=b) for b in self.blocks]
        return SimpleNamespace(stop_reason=self.stop_reason, model="claude-opus-4-8", content=content)


def _claude(stream):
    from finlit_pro.research.claude import ClaudeEngine

    engine = ClaudeEngine("sk-ant-test", "claude-opus-5-5")
    make = lambda **kw: stream  # noqa: E731
    engine.client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=make)), messages=SimpleNamespace(stream=make))
    return engine


def test_claude_keeps_every_text_block_after_a_mid_stream_fallback():
    # First Version kept only the first block, so the note was cut in half and failed to parse.
    whole = json.dumps({"summary": "x" * 200, "ok": True})
    engine = _claude(EventStream([whole[:90], whole[90:]]))
    assert engine.run("s", "u") == whole
    assert engine.served_model == "claude-opus-4-8"


def test_claude_cancel_works_during_thinking_before_any_text():
    thinking = [SimpleNamespace(type="thinking", thinking="hmm")] * 50
    stream = EventStream(["{}"], events=thinking)
    with pytest.raises(research.AnalysisError, match="cancelled"):
        _claude(stream).run("s", "u", cancelled=lambda: True)
    assert stream.seen == 1 and stream.closed  # stopped at the first event and closed the stream


def test_claude_mid_stream_errors_name_the_error_not_status_200():
    err = anthropic.APIStatusError("Overloaded", response=_response(200), body={"error": {"type": "overloaded_error"}})
    with pytest.raises(research.AnalysisError, match="overloaded") as exc:
        _claude(EventStream(["{}"], error=err)).run("s", "u")
    assert "200" not in str(exc.value)
    err = anthropic.APIStatusError("Odd", response=_response(200), body={"error": {"type": "api_error"}})
    with pytest.raises(research.AnalysisError, match=r"\(api_error\)"):
        _claude(EventStream(["{}"], error=err)).run("s", "u")


@pytest.mark.parametrize(
    "stop,message",
    [("model_context_window_exceeded", "context window"), ("max_tokens", "Lower the effort"), ("refusal", "declined")],
)
def test_claude_stop_reasons_say_what_to_do(stop, message):
    with pytest.raises(research.AnalysisError, match=message):
        _claude(EventStream(['{"a":'], stop_reason=stop)).run("s", "u")


# --------------------------------------------------------------- OpenAI engine


def _openai(create):
    from finlit_pro.research.openai_provider import OpenAIEngine

    engine = OpenAIEngine("sk-test", "gpt-5.6-luna")
    engine.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    return engine


def _reply(content, finish="stop"):
    return SimpleNamespace(choices=[SimpleNamespace(finish_reason=finish, message=SimpleNamespace(content=content, refusal=None))])


def test_openai_cancel_discards_a_note_that_finished_afterwards():
    engine = _openai(lambda **k: _reply('{"ok": 1}'))
    with pytest.raises(research.AnalysisError, match="cancelled"):
        engine.run("s", "u", cancelled=lambda: True)


@pytest.mark.parametrize("content", ["", '{"summary": "cut o'])
def test_openai_length_stop_is_reported_as_the_output_limit(content):
    with pytest.raises(research.AnalysisError, match="output limit"):
        _openai(lambda **k: _reply(content, "length")).run("s", "u")


def test_openai_400_keeps_the_reason():
    def create(**k):
        raise openai.BadRequestError("This model's maximum context length is 400000 tokens.", response=_response(400), body=None)

    with pytest.raises(research.AnalysisError, match="maximum context length"):
        _openai(create).run("s", "u")


# --------------------------------------------------------------- note checks


def _registry(demo_ws):
    _, reg = brief.build(demo_ws)
    return reg


def _note(**over):
    data = {
        "summary": "s", "recommendation": "Hold", "conviction": "Medium", "horizon": "1y",
        "facts": [{"topic": "Other", "statement": "Combined.", "sources": ["S1, S2"]}],
        "interpretation": [{"statement": "A view.", "confidence": "High", "based_on": ["S1", "S42"]}],
        "risks": [{"risk": "A risk.", "sources": ["S77"]}],
        "uncertainties": [], "data_gaps": [],
    }
    data.update(over)
    return data


def test_combined_citation_is_two_valid_ids(demo_ws):
    n = note.from_dict(_note(), _registry(demo_ws), "test")
    assert n.facts[0].sources == ["S1", "S2"] and n.facts[0].verified
    assert not any("fact cited" in w for w in n.warnings)


def test_unknown_ids_in_interpretations_and_risks_are_named(demo_ws):
    n = note.from_dict(_note(), _registry(demo_ws), "test")
    assert n.interpretation[0].based_on == ["S1"] and n.risks[0].sources == []
    assert any("interpretation cited unknown source IDs S42" in w for w in n.warnings)
    assert any("risk cited unknown source IDs S77" in w for w in n.warnings)


# --------------------------------------------------------------- brief and rules


def test_brief_returns_use_the_same_calendar_windows_as_the_screen(demo_ws):
    text, _ = brief.build(demo_ws)
    closes = demo_ws.history.closes
    base = closes[closes.index <= closes.index[-1] - pd.Timedelta(days=RANGE_DAYS["1Y"])]
    expected = fmt.pct(closes.iloc[-1] / base.iloc[-1] - 1, 1, True)
    assert f"1Y {expected}" in text
    reg = rules.build_note(demo_ws, _registry(demo_ws))
    assert any(expected in f.statement for f in reg.facts)  # the rules note states the same figure


def test_short_history_range_is_not_called_52_week(demo_ws):
    ws = copy.copy(demo_ws)
    ws.history = dataclasses.replace(demo_ws.history, bars=demo_ws.history.bars.iloc[-80:])
    text, _ = brief.build(ws)
    assert "52-week range" not in text and f"Range since {ws.history.bars.index[0].date()}" in text
    full, _ = brief.build(demo_ws)
    assert "52-week range" in full


def test_dcf_lines_cite_both_the_price_and_the_filings(demo_ws):
    text, reg = brief.build(demo_ws)
    for start in ("DCF value", "Reverse DCF"):
        line = next(ln for ln in text.splitlines() if ln.startswith(start))
        tags = re.search(r"\[([^\]]+)\]$", line).group(1).split(", ")
        assert len(tags) >= 3, line  # price, facts and the computation


def test_unknown_currency_is_left_out_not_printed_as_none(demo_ws):
    ws = copy.copy(demo_ws)
    ws.history = dataclasses.replace(demo_ws.history, currency=None)
    text, reg = brief.build(ws)
    assert "None" not in text.split("## Market data")[1].splitlines()[1]
    n = rules.build_note(ws, reg)
    assert "None" not in n.facts[0].statement


def test_rules_wording_for_cash_burn_and_operating_losses(demo_ws):
    ws = copy.copy(demo_ws)
    ws.ratios = dict(demo_ws.ratios, fcf_yield=-0.031, fcf=-1.2e9, interest_coverage=-3.2)
    _, reg = brief.build(ws)
    n = rules.build_note(ws, reg)
    said = " ".join(i.statement for i in n.interpretation) + " " + " ".join(r.risk for r in n.risks)
    assert "prices in substantial growth" not in said and "consuming cash" in said
    assert "covers interest -3.2" not in said and "does not cover interest" in said


# --------------------------------------------------------------- validation


@pytest.mark.parametrize("text", ["102,5", "15,5", "1,2,3", "1.000,5", "1,0"])
def test_a_misplaced_comma_is_refused_not_read_as_a_bigger_number(text):
    with pytest.raises(validation.ValidationError, match="comma in the wrong place"):
        validation.number(text, "Strike")


@pytest.mark.parametrize("text,value", [("1,000", 1000.0), ("12,345.5", 12345.5), ("1,000%", 1000.0), ("-1,250", -1250.0)])
def test_thousands_separators_still_work(text, value):
    assert validation.number(text, "X", allow_negative=True) == value


def test_whole_number_suggestions_are_inside_the_allowed_range():
    with pytest.raises(validation.ValidationError, match="Try 1 instead"):
        validation.positive_int("-3.5", "Paths")
    with pytest.raises(validation.ValidationError, match="Try 100,000 instead"):
        validation.positive_int("150000.5", "Simulations", 100, 100_000)


def test_negative_message_matches_the_range_and_bounds_are_written_out():
    with pytest.raises(validation.ValidationError, match="at least 1") as exc:
        validation.number("-2", "Volatility", 1, 300, allow_zero=False)
    assert "zero or a positive" not in str(exc.value)
    with pytest.raises(validation.ValidationError, match="at most 1,000,000. You entered 2,500,000"):
        validation.number("2500000", "X", 0, 1_000_000)


@pytest.mark.parametrize("text", ["​test@example.com", "test@exa­mple.com", "tést@example.com"])
def test_email_with_hidden_or_non_ascii_characters_is_refused(text):
    with pytest.raises(validation.ValidationError, match="hidden or non-standard"):
        validation.email(text)


def test_key_with_hidden_characters_is_refused():
    with pytest.raises(validation.ValidationError, match="hidden or non-standard"):
        validation.api_key("sk-ant-api03-" + "x" * 30 + "​", "Anthropic")
    assert validation.api_key("sk-ant-api03-" + "x" * 30, "Anthropic")


# --------------------------------------------------------------- settings, credentials, formatting


def test_out_of_range_settings_fall_back_to_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "settings_path", lambda: tmp_path / "settings.json")
    (tmp_path / "settings.json").write_text(json.dumps({
        "ai_provider": "anthropic", "anthropic_effort": "extreme", "filing_section_chars": -200,
        "risk_free_rate_pct": float("nan"), "transaction_cost_bps": -5000.0, "benchmark": "QQQ",
    }))
    s, d = config.load_settings(), config.Settings()
    assert (s.ai_provider, s.anthropic_effort, s.filing_section_chars) == (d.ai_provider, d.anthropic_effort, d.filing_section_chars)
    assert s.risk_free_rate_pct == d.risk_free_rate_pct and s.transaction_cost_bps == d.transaction_cost_bps
    assert s.benchmark == "QQQ"  # valid values are still loaded


def test_backend_says_unavailable_without_a_secure_store(monkeypatch):
    import keyring
    from keyring.backends.fail import Keyring as FailKeyring

    monkeypatch.setattr(keyring, "get_keyring", lambda: FailKeyring())
    assert credentials.backend() == "unavailable"


@pytest.mark.parametrize(
    "value,text",
    [(999.996, "$1.0K"), (999_949, "$999.9K"), (999_960, "$1.0M"), (999_999, "$1.0M"), (999_960_000, "$1.0B"),
     (999_960_000_000, "$1.0T"), (1_000_000, "$1.0M"), (960, "$960.00"), (-999_960, "-$1.0M")],
)
def test_money_never_prints_1000_of_a_unit(value, text):
    assert fmt.money(value) == text


@pytest.mark.parametrize("currency", ["", None])
def test_unknown_currency_leaves_no_none_or_trailing_space(currency):
    assert fmt.price(262.63, currency) == "262.63"
    assert fmt.money(5e9, currency) == "5.0B"
    assert fmt.price(1, "CHF") == "1.00 CHF"
