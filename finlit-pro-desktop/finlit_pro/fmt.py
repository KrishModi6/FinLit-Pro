"""Number formatting shared by the UI, the research brief and reports."""

from __future__ import annotations

import math


def ok(v) -> bool:
    return v is not None and isinstance(v, (int, float)) and math.isfinite(v)


def _no_negative_zero(v: float, dp: int) -> float:
    """-0.001 printed to 2 dp reads "-0.00"; show it as 0.00."""
    return 0.0 if round(v, dp) == 0 else v


def pct(v, dp: int = 1, sign: bool = False) -> str:
    if not ok(v):
        return "n/a"
    v = _no_negative_zero(v, dp + 2)
    return f"{v * 100:+.{dp}f}%" if sign else f"{v * 100:.{dp}f}%"


def num(v, dp: int = 2, sign: bool = False) -> str:
    if not ok(v):
        return "n/a"
    v = _no_negative_zero(v, dp)
    return f"{v:+,.{dp}f}" if sign else f"{v:,.{dp}f}"


def money(v, currency: str = "USD") -> str:
    """Compact money: 1.2T, 340.5B, 12.3M."""
    if not ok(v):
        return "n/a"
    v = _no_negative_zero(v, 2)
    sign = "-" if v < 0 else ""
    a = abs(v)
    prefix = "$" if currency == "USD" else ""
    suffix = "" if currency == "USD" else f" {currency}"
    for size, unit in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if a >= size:
            return f"{sign}{prefix}{a / size:,.1f}{unit}{suffix}"
    return f"{sign}{prefix}{a:,.2f}{suffix}"


def dollars(v, sign: bool = False) -> str:
    """Exact dollars and cents, for position sizes: -$90.10, $1,085.00."""
    if not ok(v):
        return "n/a"
    v = _no_negative_zero(v, 2)
    lead = "-" if v < 0 else ("+" if sign else "")
    return f"{lead}${abs(v):,.2f}"


def price(v, currency: str = "USD") -> str:
    if not ok(v):
        return "n/a"
    symbol = {"USD": "$", "EUR": "€", "GBP": "£", "CAD": "C$", "JPY": "¥"}.get(currency, "")
    if currency == "GBp":
        return f"{v:,.2f}p"
    return f"{symbol}{v:,.2f}" + ("" if symbol else f" {currency}")
