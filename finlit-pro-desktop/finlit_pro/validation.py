"""Input validation with messages that tell the user what to do next.

Every field in the app goes through one of these before it reaches the
analytics. Each failure raises ValidationError carrying a sentence that names
the field, says what was wrong, and gives a valid example, so the UI can show
the message as is.
"""

from __future__ import annotations

import re


class ValidationError(ValueError):
    """Raised with a user-facing message."""


# Letters, digits, dot, dash, caret (indices like ^GSPC), equals (futures).
# The same pattern the FinLit Pro web proxy uses.
_TICKER_RE = re.compile(r"^[A-Z0-9.\-^=]{1,12}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def ticker(text: str) -> str:
    value = (text or "").strip().upper()
    if not value:
        raise ValidationError("Type a ticker symbol first, for example AAPL or MSFT.")
    if " " in value:
        raise ValidationError(
            f'"{value}" has a space in it. Enter one ticker at a time, like AAPL.'
        )
    if not _TICKER_RE.match(value):
        raise ValidationError(
            f'"{value}" is not a valid ticker. Use 1 to 12 letters, digits, dots or dashes, '
            "like AAPL, BRK-B or ^GSPC."
        )
    if not any(ch.isalpha() for ch in value):
        raise ValidationError(
            f'"{value}" has no letters in it. Tickers contain letters, like NVDA.'
        )
    return value


def ticker_list(text: str, minimum: int = 2, maximum: int = 8) -> list[str]:
    parts = [p for p in re.split(r"[,\s]+", (text or "").strip()) if p]
    if len(parts) < minimum:
        raise ValidationError(
            f"Enter at least {minimum} tickers separated by commas, for example AAPL, MSFT, SPY."
        )
    if len(parts) > maximum:
        raise ValidationError(
            f"That is {len(parts)} tickers. Compare at most {maximum} at once so the charts stay readable."
        )
    out: list[str] = []
    for part in parts:
        sym = ticker(part)
        if sym in out:
            raise ValidationError(f"{sym} is listed twice. Remove the duplicate and try again.")
        out.append(sym)
    return out


# Commas are accepted only as thousands separators: 1,000 or 12,345.5 (optionally with a % sign).
_THOUSANDS_RE = re.compile(r"[+-]?\d{1,3}(,\d{3})+(\.\d*)?%?")


def _fmt(x: float) -> str:
    """A bound or entry as people write it: 1,000,000 rather than 1e+06."""
    return f"{x:,.10g}"


def _number_text(text: str, name: str) -> str:
    # First Version: every comma was deleted, so "102,5" (a decimal comma, or a slip of the comma key)
    # was silently read as 1025. Current Version: commas must be thousands separators; anything else
    # is refused with a message.
    value = (text if isinstance(text, str) else str(text)).strip()
    if not value:
        raise ValidationError(f"{name} is empty. Enter a number.")
    if "," in value:
        if not _THOUSANDS_RE.fullmatch(value):
            raise ValidationError(f'{name}: "{value}" has a comma in the wrong place. Use a dot for decimals, like 102.5, and commas only between thousands, like 1,000.')
        value = value.replace(",", "")
    return value


def positive_int(text: str, name: str, lo: int = 1, hi: int | None = None) -> int:
    """Whole number in [lo, hi]. Rejects blanks, letters, decimals, zero and negatives."""
    value = _number_text(text, name)
    if re.fullmatch(r"[+-]?\d+\.\d*|[+-]?\.\d+", value):
        # First Version suggested values the same check then refused (-3 for "-3.5", 150000 above a 100,000 cap).
        # Current Version: the suggestion is clamped to the allowed range.
        guess = max(int(float(value)), lo)
        if hi is not None:
            guess = min(guess, hi)
        raise ValidationError(f"{name} must be a whole number. Try {guess:,} instead of {value}.")
    if not re.fullmatch(r"[+-]?\d+", value):
        raise ValidationError(f'{name} must be a number, but "{value}" contains letters or symbols. Enter digits only, like {lo}.')
    number = int(value)
    if number <= 0:
        raise ValidationError(f"{name} must be greater than zero. Enter a positive whole number like {max(lo, 1)}.")
    if number < lo:
        raise ValidationError(f"{name} must be at least {lo:,}. You entered {number:,}.")
    if hi is not None and number > hi:
        raise ValidationError(f"{name} can be at most {hi:,}. You entered {number:,}; try a smaller number.")
    return number


def number(
    text: str,
    name: str,
    lo: float | None = None,
    hi: float | None = None,
    allow_zero: bool = True,
    allow_negative: bool = False,
) -> float:
    """A decimal number. Percent signs are accepted and stripped ("8%" -> 8.0)."""
    value = _number_text(text, name).rstrip("%").strip()
    try:
        result = float(value)
    except ValueError:
        raise ValidationError(f'{name} must be a number, but "{value}" is not one. Enter something like 8 or 2.5.') from None
    if result != result or result in (float("inf"), float("-inf")):
        raise ValidationError(f"{name} must be an ordinary number like 8 or 2.5.")
    if result < 0 and not allow_negative:
        # First Version always said "Enter zero or a positive number", even where zero is refused.
        if lo is not None and lo > 0:
            hint = f"Enter a number of at least {_fmt(lo)}."
        elif not allow_zero:
            hint = "Enter a number greater than zero."
        else:
            hint = "Enter zero or a positive number."
        raise ValidationError(f"{name} cannot be negative. {hint}")
    if result == 0 and not allow_zero:
        raise ValidationError(f"{name} cannot be zero. Enter a number greater than zero.")
    if lo is not None and result < lo:
        raise ValidationError(f"{name} must be at least {_fmt(lo)}. You entered {_fmt(result)}.")
    if hi is not None and result > hi:
        raise ValidationError(f"{name} can be at most {_fmt(hi)}. You entered {_fmt(result)}.")
    return result


def email(text: str) -> str:
    value = (text or "").strip()
    if not value:
        raise ValidationError("Enter an email address. The SEC asks every app to include one so they can contact you about heavy usage.")
    # First Version accepted invisible characters (a zero-width space pasted from a web page), which then
    # crashed the HTTP layer. Current Version: only plain printable characters are allowed.
    if not (value.isascii() and value.isprintable()):
        raise ValidationError("That email address contains a hidden or non-standard character. Type it again by hand, like name@example.com.")
    if not _EMAIL_RE.match(value):
        raise ValidationError(f'"{value}" does not look like an email address. Use the form name@example.com.')
    return value


def api_key(text: str, provider: str) -> str:
    """Light shape check only: the provider is the real judge of a key."""
    value = (text or "").strip()
    if not value:
        return ""
    if any(ch.isspace() for ch in value):
        raise ValidationError(f"The {provider} key contains spaces. Copy it again without extra characters.")
    if not (value.isascii() and value.isprintable()):
        # First Version: invisible characters passed and later crashed the OpenAI and SEC requests.
        raise ValidationError(f"The {provider} key contains hidden or non-standard characters. Copy it again from your {provider} dashboard.")
    if len(value) < 20:
        raise ValidationError(f"That {provider} key looks too short. Paste the full key from your {provider} dashboard.")
    return value
