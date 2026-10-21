"""The research note: its JSON schema, parsing and citation checks.

The analysis engines must return exactly this structure, which keeps facts
(each tied to source IDs), interpretation (each with a confidence level),
risks, and uncertainty in separate fields. After parsing, every cited ID is
checked against the source registry: a fact citing an ID that does not
exist, or citing nothing, is kept but marked unverified, never silently
trusted.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from finlit_pro.research.sources import SourceRegistry

RECOMMENDATIONS = ["Buy", "Accumulate", "Hold", "Reduce", "Sell", "No recommendation"]
LEVELS = ["Low", "Medium", "High"]
TOPICS = ["Business", "Financial performance", "Balance sheet", "Cash flow and capital return", "Valuation", "Price and risk", "Model and simulation", "Filings and disclosures", "Other"]

_ids = {"type": "array", "items": {"type": "string"}, "description": "Source IDs from the brief, such as S3."}

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "recommendation", "conviction", "horizon", "facts", "interpretation", "risks", "uncertainties", "data_gaps"],
    "properties": {
        "summary": {"type": "string", "description": "Three to five sentences: the conclusion and the main reasons."},
        "recommendation": {"type": "string", "enum": RECOMMENDATIONS},
        "conviction": {"type": "string", "enum": LEVELS},
        "horizon": {"type": "string", "description": "Holding period the recommendation applies to, e.g. 6 to 12 months."},
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["topic", "statement", "sources"],
                "properties": {"topic": {"type": "string", "enum": TOPICS}, "statement": {"type": "string"}, "sources": _ids},
            },
        },
        "interpretation": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["statement", "confidence", "based_on"],
                "properties": {"statement": {"type": "string"}, "confidence": {"type": "string", "enum": LEVELS}, "based_on": _ids},
            },
        },
        "risks": {
            "type": "array",
            "items": {"type": "object", "additionalProperties": False, "required": ["risk", "sources"], "properties": {"risk": {"type": "string"}, "sources": _ids}},
        },
        "uncertainties": {
            "type": "array",
            "items": {"type": "object", "additionalProperties": False, "required": ["issue", "effect"], "properties": {"issue": {"type": "string"}, "effect": {"type": "string"}}},
        },
        "data_gaps": {"type": "array", "items": {"type": "string"}},
    },
}


@dataclass
class Fact:
    topic: str
    statement: str
    sources: list[str]
    verified: bool = True

    def __post_init__(self) -> None:
        self.sources = [s for s in dict.fromkeys(self.sources) if s]


@dataclass
class Interpretation:
    statement: str
    confidence: str
    based_on: list[str]

    def __post_init__(self) -> None:
        self.based_on = [s for s in dict.fromkeys(self.based_on) if s]


@dataclass
class Risk:
    risk: str
    sources: list[str]


@dataclass
class Uncertainty:
    issue: str
    effect: str


@dataclass
class Note:
    summary: str
    recommendation: str
    conviction: str
    horizon: str
    facts: list[Fact]
    interpretation: list[Interpretation]
    risks: list[Risk]
    uncertainties: list[Uncertainty]
    data_gaps: list[str]
    engine: str = ""
    warnings: list[str] = field(default_factory=list)


class NoteError(ValueError):
    pass


def _clean_ids(values, valid: set[str]) -> tuple[list[str], list[str]]:
    # First Version: "S1, S3" in one array item was read as a single unknown ID and the fact was marked
    # unverified. Current Version: each item is split on commas, semicolons and spaces first.
    good, bad = [], []
    for v in values or []:
        for part in re.split(r"[,;\s]+", str(v).strip().strip("[]")):
            sid = part.strip("[]").upper()
            if sid:
                (good if sid in valid else bad).append(sid)
    return list(dict.fromkeys(good)), bad


def from_dict(data: dict, registry: SourceRegistry, engine: str) -> Note:
    valid = registry.ids()
    warnings: list[str] = []
    try:
        facts = []
        for raw in data["facts"]:
            ids, bad = _clean_ids(raw.get("sources"), valid)
            if bad:
                warnings.append(f"A fact cited unknown source IDs {', '.join(bad)}; it is marked unverified.")
            facts.append(Fact(raw.get("topic") or "Other", raw["statement"], ids, verified=bool(ids) and not bad))
        # First Version: unknown IDs cited by interpretations and risks were dropped without a word.
        # Current Version: they are dropped and named in a warning, as for facts.
        interp = []
        for i in data["interpretation"]:
            ids, bad = _clean_ids(i.get("based_on"), valid)
            if bad:
                warnings.append(f"An interpretation cited unknown source IDs {', '.join(bad)}; they were removed.")
            interp.append(Interpretation(i["statement"], i.get("confidence") if i.get("confidence") in LEVELS else "Low", ids))
        risks = []
        for r in data["risks"]:
            ids, bad = _clean_ids(r.get("sources"), valid)
            if bad:
                warnings.append(f"A risk cited unknown source IDs {', '.join(bad)}; they were removed.")
            risks.append(Risk(r["risk"], ids))
        unc = [Uncertainty(u["issue"], u["effect"]) for u in data["uncertainties"]]
        rec = data["recommendation"] if data["recommendation"] in RECOMMENDATIONS else "No recommendation"
        conviction = data["conviction"] if data["conviction"] in LEVELS else "Low"
        note = Note(str(data["summary"]), rec, conviction, str(data.get("horizon") or ""), facts, interp, risks, unc, [str(g) for g in data["data_gaps"]], engine, warnings)
    except (KeyError, TypeError) as exc:
        raise NoteError(f"The analysis came back incomplete ({exc.__class__.__name__}: {exc}). Run it again.") from None
    unverified = sum(1 for f in note.facts if not f.verified)
    if unverified:
        note.warnings.append(f"{unverified} of {len(note.facts)} facts are not tied to a valid source and are marked unverified.")
    return note


def parse(text: str, registry: SourceRegistry, engine: str) -> Note:
    try:
        data = json.loads(text)
    except ValueError:
        raise NoteError("The analysis engine returned output that is not valid JSON. Run it again.") from None
    if not isinstance(data, dict):
        raise NoteError("The analysis engine returned an unexpected structure. Run it again.")
    return from_dict(data, registry, engine)
