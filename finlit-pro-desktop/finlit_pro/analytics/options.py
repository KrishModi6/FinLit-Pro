"""Single-leg option analysis: fair value, Greeks, probabilities and expected value.

Two sets of assumptions are always shown side by side:

* Market-implied: volatility is the option's own implied volatility and the
  drift is risk-neutral (r - q). Under these assumptions a fairly priced
  option has zero expected value by construction, so this column answers
  "what does the market think?", not "is it worth it?".
* Model: your volatility (historical by default) and your expected return.
  This is the column that can say an option is worth buying or selling,
  and only to the extent that your assumptions are better than the market's.

Probabilities and expected values come from a lognormal terminal price
(closed form) and, optionally, from the Monte Carlo engine's fat-tailed or
bootstrapped distribution at the same horizon.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

import numpy as np

from finlit_pro.validation import ValidationError

SQRT2 = math.sqrt(2.0)
CONTRACT = 100  # shares per US equity option contract


def ncdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / SQRT2))


def npdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


@dataclass(frozen=True)
class Contract:
    kind: str  # "call" or "put"
    side: str  # "long" or "short"
    strike: float
    premium: float  # per share
    expiry: date

    def validate(self) -> None:
        if self.kind not in ("call", "put"):
            raise ValidationError("Option type must be call or put.")
        if self.side not in ("long", "short"):
            raise ValidationError("Position must be long (buy) or short (sell).")
        if not np.isfinite(self.strike) or self.strike <= 0:
            raise ValidationError("Strike must be greater than zero.")
        if not np.isfinite(self.premium) or self.premium <= 0:
            raise ValidationError("Premium must be greater than zero. Use the mid of bid and ask if there is no last trade.")


def years_to(expiry: date, today: date | None = None) -> float:
    days = (expiry - (today or date.today())).days
    if days <= 0:
        raise ValidationError("The expiry date must be in the future.")
    return days / 365.0


def bsm(kind: str, s: float, k: float, t: float, r: float, q: float, vol: float) -> dict[str, float]:
    """Black-Scholes-Merton price and Greeks with a continuous dividend yield.

    Theta is per calendar day, vega and rho per one percentage point.
    """
    if vol <= 0 or t <= 0:
        intrinsic = max(s - k, 0.0) if kind == "call" else max(k - s, 0.0)
        return {"price": intrinsic, "delta": float(intrinsic > 0) * (1 if kind == "call" else -1), "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}
    sq = vol * math.sqrt(t)
    d1 = (math.log(s / k) + (r - q + 0.5 * vol * vol) * t) / sq
    d2 = d1 - sq
    disc_q, disc_r = math.exp(-q * t), math.exp(-r * t)
    if kind == "call":
        price = s * disc_q * ncdf(d1) - k * disc_r * ncdf(d2)
        delta = disc_q * ncdf(d1)
        theta = -s * disc_q * npdf(d1) * vol / (2 * math.sqrt(t)) - r * k * disc_r * ncdf(d2) + q * s * disc_q * ncdf(d1)
        rho = k * t * disc_r * ncdf(d2)
    else:
        price = k * disc_r * ncdf(-d2) - s * disc_q * ncdf(-d1)
        delta = -disc_q * ncdf(-d1)
        theta = -s * disc_q * npdf(d1) * vol / (2 * math.sqrt(t)) + r * k * disc_r * ncdf(-d2) - q * s * disc_q * ncdf(-d1)
        rho = -k * t * disc_r * ncdf(-d2)
    gamma = disc_q * npdf(d1) / (s * sq)
    vega = s * disc_q * npdf(d1) * math.sqrt(t)
    return {"price": price, "delta": delta, "gamma": gamma, "theta": theta / 365, "vega": vega / 100, "rho": rho / 100}


def implied_vol(kind: str, price: float, s: float, k: float, t: float, r: float, q: float) -> float | None:
    """Volatility that reproduces `price`, by bisection on [0.1%, 500%]. None if no solution."""
    lo, hi = 1e-3, 5.0
    intrinsic = max(s * math.exp(-q * t) - k * math.exp(-r * t), 0.0) if kind == "call" else max(k * math.exp(-r * t) - s * math.exp(-q * t), 0.0)
    if price <= intrinsic + 1e-9 or price >= (s if kind == "call" else k):
        return None
    for _ in range(100):
        mid = (lo + hi) / 2
        if bsm(kind, s, k, t, r, q, mid)["price"] > price:
            hi = mid
        else:
            lo = mid
        if hi - lo < 1e-7:
            break
    return (lo + hi) / 2


def payoff(kind: str, k: float, s_t):
    s_t = np.asarray(s_t, dtype=float)
    return np.maximum(s_t - k, 0.0) if kind == "call" else np.maximum(k - s_t, 0.0)


def position_pnl(c: Contract, s_t):
    """Per-share P&L at expiry."""
    value = payoff(c.kind, c.strike, s_t)
    return value - c.premium if c.side == "long" else c.premium - value


def breakeven(c: Contract) -> float:
    return c.strike + c.premium if c.kind == "call" else c.strike - c.premium


def prob_above(s: float, x: float, t: float, mu: float, vol: float) -> float:
    """P(S_T > x) for a lognormal price with continuous drift mu (price appreciation)."""
    if x <= 0:
        return 1.0
    d = (math.log(s / x) + (mu - 0.5 * vol * vol) * t) / (vol * math.sqrt(t))
    return ncdf(d)


def expected_payoff(kind: str, s: float, k: float, t: float, mu: float, vol: float) -> float:
    """E[payoff at expiry] under a lognormal price with drift mu (undiscounted)."""
    sq = vol * math.sqrt(t)
    fwd = s * math.exp(mu * t)
    d1 = (math.log(fwd / k) + 0.5 * vol * vol * t) / sq
    d2 = d1 - sq
    if kind == "call":
        return fwd * ncdf(d1) - k * ncdf(d2)
    return k * ncdf(-d2) - fwd * ncdf(-d1)


@dataclass
class Scenario:
    """Probabilities and value of the position under one set of assumptions."""

    label: str
    vol: float
    mu: float  # continuous annual price drift
    prob_profit: float
    prob_itm: float
    expected_pnl: float  # per share, discounted to today
    fair_premium: float  # premium at which expected P&L is zero, per share
    method: str = "lognormal"


@dataclass
class OptionAnalysis:
    contract: Contract
    spot: float
    t_years: float
    r: float
    q: float
    implied_vol: float | None
    greeks: dict[str, float]
    breakeven: float
    max_profit: float | None  # per share; None = unlimited
    max_loss: float | None
    scenarios: list[Scenario]
    verdict: str
    verdict_reason: str
    notes: list[str] = field(default_factory=list)


def _scenario(label: str, c: Contract, s: float, t: float, r: float, mu: float, vol: float) -> Scenario:
    be = breakeven(c)
    p_above_be = prob_above(s, be, t, mu, vol)
    p_above_k = prob_above(s, c.strike, t, mu, vol)
    if c.kind == "call":
        long_profit, itm = p_above_be, p_above_k
    else:
        long_profit, itm = 1 - p_above_be, 1 - p_above_k
    pv_payoff = math.exp(-r * t) * expected_payoff(c.kind, s, c.strike, t, mu, vol)
    if c.side == "long":
        prob_profit, pnl = long_profit, pv_payoff - c.premium
    else:
        prob_profit, pnl = 1 - long_profit, c.premium - pv_payoff
    return Scenario(label, vol, mu, prob_profit, itm, pnl, pv_payoff)


def simulated_scenario(label: str, c: Contract, terminal: np.ndarray, t: float, r: float) -> Scenario:
    """The same figures from a simulated distribution of terminal prices."""
    pnl = position_pnl(c, terminal)
    value = payoff(c.kind, c.strike, terminal)
    itm = float((value > 0).mean())
    pv_payoff = math.exp(-r * t) * float(value.mean())
    expected = pv_payoff - c.premium if c.side == "long" else c.premium - pv_payoff
    return Scenario(label, float("nan"), float("nan"), float((pnl > 0).mean()), itm, expected, pv_payoff, method="simulation")


def analyze(
    c: Contract,
    spot: float,
    t_years: float,
    r: float,
    q: float,
    model_vol: float,
    model_return: float,
    market_iv: float | None = None,
    simulated_terminal: np.ndarray | None = None,
    sim_label: str = "Monte Carlo",
    edge_threshold: float = 0.05,
) -> OptionAnalysis:
    """`model_return` is the expected annual price return as a decimal (e.g. 0.08)."""
    c.validate()
    if not np.isfinite(spot) or spot <= 0:
        raise ValidationError("The underlying price is missing or not positive.")
    if not np.isfinite(model_vol) or model_vol <= 0:
        raise ValidationError("Volatility must be greater than zero.")
    if model_return <= -1:
        raise ValidationError("Expected return must be above -100%.")
    notes: list[str] = []
    iv = market_iv if market_iv and market_iv > 0 else implied_vol(c.kind, c.premium, spot, c.strike, t_years, r, q)
    if iv is None:
        notes.append("No implied volatility reproduces this premium (it is at or below intrinsic value, or above the maximum possible). Check the price entered.")
    greek_vol = iv or model_vol
    greeks = bsm(c.kind, spot, c.strike, t_years, r, q, greek_vol)
    sign = 1 if c.side == "long" else -1
    greeks = {k: sign * v for k, v in greeks.items() if k != "price"} | {"model price": bsm(c.kind, spot, c.strike, t_years, r, q, model_vol)["price"]}

    scenarios = []
    if iv:
        scenarios.append(_scenario("Market-implied", c, spot, t_years, r, r - q, iv))
    mu = math.log1p(model_return)
    scenarios.append(_scenario("Your assumptions", c, spot, t_years, r, mu, model_vol))
    if simulated_terminal is not None and len(simulated_terminal) > 0:
        scenarios.append(simulated_scenario(sim_label, c, np.asarray(simulated_terminal, dtype=float), t_years, r))

    if c.side == "long":
        max_loss, max_profit = c.premium, (None if c.kind == "call" else c.strike - c.premium)
    else:
        max_profit, max_loss = c.premium, (None if c.kind == "call" else c.strike - c.premium)

    model = next(s for s in scenarios if s.label == "Your assumptions")
    edge = model.expected_pnl / c.premium
    action = "buy" if c.side == "long" else "sell"
    if edge >= edge_threshold:
        verdict = "Worth it"
        reason = f"Expected value {model.expected_pnl:+.2f} per share ({edge:+.0%} of the premium) under your assumptions; fair premium {model.fair_premium:.2f} vs {c.premium:.2f}."
    elif edge <= -edge_threshold:
        verdict = "Not worth it"
        reason = f"Expected value {model.expected_pnl:+.2f} per share ({edge:+.0%} of the premium) under your assumptions; fair premium {model.fair_premium:.2f} vs {c.premium:.2f}. Better to not {action} at this price."
    else:
        verdict = "Marginal"
        reason = f"Expected value is within {edge_threshold:.0%} of the premium ({edge:+.0%}): the price is close to fair under your assumptions."
    if iv and model_vol:
        rich = iv / model_vol - 1
        if abs(rich) >= 0.1:
            notes.append(f"Implied volatility {iv:.1%} is {abs(rich):.0%} {'above' if rich > 0 else 'below'} your volatility {model_vol:.1%}: the option is {'expensive' if rich > 0 else 'cheap'} relative to your view of how much the stock moves.")
    if model.prob_profit < 0.25 and c.side == "long":
        notes.append(f"Only a {model.prob_profit:.0%} chance of finishing in profit: most of the expected value comes from a minority of large moves.")
    return OptionAnalysis(c, spot, t_years, r, q, iv, greeks, breakeven(c), max_profit, max_loss, scenarios, verdict, reason, notes)
