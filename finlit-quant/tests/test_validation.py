import pytest

from finlit_quant import validation as v
from finlit_quant.validation import ValidationError


@pytest.mark.parametrize("text,expected", [("aapl", "AAPL"), (" BRK-B ", "BRK-B"), ("^gspc", "^GSPC"), ("shop.to", "SHOP.TO")])
def test_ticker_accepts_real_shapes(text, expected):
    assert v.ticker(text) == expected


@pytest.mark.parametrize(
    "text,fragment",
    [("", "Type a ticker"), ("AA PL", "space"), ("AAPL!", "not a valid ticker"), ("12345", "no letters"), ("A" * 13, "not a valid ticker")],
)
def test_ticker_rejects_with_guidance(text, fragment):
    with pytest.raises(ValidationError, match=fragment):
        v.ticker(text)


@pytest.mark.parametrize(
    "text,fragment",
    [("", "empty"), ("abc", "contains letters"), ("12x", "contains letters"), ("0", "greater than zero"), ("-5", "greater than zero"), ("2.5", "whole number"), ("99999", "at most")],
)
def test_positive_int_rejects_zero_negative_letters(text, fragment):
    with pytest.raises(ValidationError, match=fragment):
        v.positive_int(text, "Paths", 1, 1000)


def test_positive_int_accepts_commas():
    assert v.positive_int("10,000", "Paths", 100, 20000) == 10000


def test_number_rules():
    assert v.number("8%", "Rate") == 8.0
    assert v.number("-3", "Growth", allow_negative=True) == -3.0
    with pytest.raises(ValidationError, match="cannot be negative"):
        v.number("-3", "Rate")
    with pytest.raises(ValidationError, match="cannot be zero"):
        v.number("0", "Shares", allow_zero=False)
    with pytest.raises(ValidationError, match="not one"):
        v.number("ten", "Rate")
    with pytest.raises(ValidationError, match="ordinary number"):
        v.number("nan", "Rate")


def test_ticker_list():
    assert v.ticker_list("aapl, msft spy") == ["AAPL", "MSFT", "SPY"]
    with pytest.raises(ValidationError, match="at least 2"):
        v.ticker_list("AAPL")
    with pytest.raises(ValidationError, match="twice"):
        v.ticker_list("AAPL, aapl")


def test_email_and_keys():
    assert v.email("me@example.com") == "me@example.com"
    with pytest.raises(ValidationError, match="name@example.com"):
        v.email("not-an-email")
    assert v.api_key("", "Anthropic") == ""
    with pytest.raises(ValidationError, match="spaces"):
        v.api_key("sk-ant- abc def ghi jkl mno", "Anthropic")
    with pytest.raises(ValidationError, match="too short"):
        v.api_key("sk-123", "OpenAI")
