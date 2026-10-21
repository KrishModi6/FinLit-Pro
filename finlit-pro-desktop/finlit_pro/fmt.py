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
    suffix = "" if currency == "USD" or not currency else f" {currency}"
    # First Version picked the unit before rounding, so 999,960 printed as "$1,000.0K".
    # Current Version: when rounding reaches 1,000 of a unit, the next unit up is used ("$1.0M").
    units = ((1e3, "K"), (1e6, "M"), (1e9, "B"), (1e12, "T"))
    if round(a, 2) < 1e3:
        return f"{sign}{prefix}{a:,.2f}{suffix}"
    k = max((i for i, (size, _) in enumerate(units) if a >= size), default=0)
    if k + 1 < len(units) and round(a / units[k][0], 1) >= 1000:
        k += 1
    size, unit = units[k]
    return f"{sign}{prefix}{a / size:,.1f}{unit}{suffix}"


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
    # First Version: an unknown currency printed "262.63 None" or left a trailing space. Current Version: omitted.
    return f"{symbol}{v:,.2f}" + ("" if symbol or not currency else f" {currency}")
