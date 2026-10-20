"""Text of SEC filings: the latest 10-K and 10-Q, split into their key items.

Filings on EDGAR are inline-XBRL HTML. This module strips them to text and
cuts out the sections an analyst reads first:

  10-K  Item 1 Business, Item 1A Risk Factors, Item 7 MD&A
  10-Q  Part I Item 2 MD&A, Part II Item 1A Risk Factors

Every filing names each item twice, once in the table of contents and once
as the real heading, so for each item the longest span between its heading
and the next item's heading is taken; table-of-contents spans are a line long.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from html import unescape
from html.parser import HTMLParser

from finlit_pro.data.http import get_text
from finlit_pro.data.models import DataError, Filing, Fundamentals, Source

DASH = r"[\s\.\-:" + "\u2013\u2014" + r"]*"  # hyphen, colon, en and em dash between item number and title
APOS = "['\u2019]"

SECTIONS = {
    "10-K": [
        ("Business", rf"item\s*1{DASH}business\b", rf"item\s*1a{DASH}risk"),
        ("Risk Factors", rf"item\s*1a{DASH}risk\s+factors", rf"item\s*1b{DASH}|item\s*1c{DASH}|item\s*2{DASH}properties"),
        ("MD&A", rf"item\s*7{DASH}management{APOS}s\s+discussion", rf"item\s*7a{DASH}|item\s*8{DASH}financial\s+statements"),
    ],
    "10-Q": [
        ("MD&A", rf"item\s*2{DASH}management{APOS}s\s+discussion", rf"item\s*3{DASH}quantitative|item\s*4{DASH}controls"),
        ("Risk Factors", rf"item\s*1a{DASH}risk\s+factors", rf"item\s*2{DASH}unregistered|item\s*5{DASH}other|item\s*6{DASH}exhibits"),
    ],
}

BLOCK_TAGS = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section"}
SKIP_TAGS = {"script", "style", "head", "ix:header", "title"}


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")
        elif tag == "td":
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    parser = _Text()
    parser.feed(html)
    parser.close()
    text = unescape("".join(parser.parts)).replace("\xa0", " ")
    lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip() for line in text.split("\n")]
    out, blank = [], False
    for line in lines:
        if line:
            out.append(line)
            blank = False
        elif not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip()


def extract_section(text: str, start_pattern: str, end_pattern: str) -> str:
    """Longest span from a heading match to the next end-heading match."""
    starts = [m.start() for m in re.finditer(start_pattern, text, flags=re.IGNORECASE)]
    ends = [m.start() for m in re.finditer(end_pattern, text, flags=re.IGNORECASE)]
    best = ""
    for s in starts:
        following = [e for e in ends if e > s + 20]
        stop = following[0] if following else len(text)
        span = text[s:stop].strip()
        if len(span) > len(best):
            best = span
    return best


def truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    cut = text.rfind("\n", 0, limit)
    return text[: cut if cut > limit * 0.6 else limit].rstrip(), True


@dataclass
class FilingText:
    filing: Filing
    sections: dict[str, str]
    truncated: dict[str, bool]
    full_chars: dict[str, int]
    source: Source
    notes: list[str] = field(default_factory=list)


def sec_headers(email: str) -> dict[str, str]:
    from finlit_pro.data.sec import _headers

    headers = _headers(email)
    headers["Accept"] = "text/html,application/xhtml+xml"
    return headers


def read(filing: Filing, email: str, limit_chars: int = 40_000) -> FilingText:
    if not filing.url:
        raise DataError(f"The {filing.form} filed {filing.filed} has no primary document link.")
    fetched = get_text(filing.url, headers=sec_headers(email), service="SEC EDGAR")
    text = html_to_text(fetched.value)
    base = filing.form.split("/")[0]
    sections, cut, sizes, notes = {}, {}, {}, []
    for name, start, end in SECTIONS.get(base, []):
        body = extract_section(text, start, end)
        if len(body) < 500:
            notes.append(f"{name} not found in the {filing.form}; the filing may incorporate it by reference.")
            continue
        sizes[name] = len(body)
        sections[name], cut[name] = truncate(body, limit_chars)
    source = Source(
        f"SEC EDGAR {filing.form}",
        filing.url,
        datetime.fromtimestamp(fetched.saved_at),
        filing.report_date or None,
        fetched.status,
        f"Filed {filing.filed}, accession {filing.accession}",
    )
    return FilingText(filing, sections, cut, sizes, source, notes)


def latest_reports(fund: Fundamentals, email: str, limit_chars: int = 40_000) -> tuple[list[FilingText], list[str]]:
    """The most recent 10-K and, if newer, the most recent 10-Q. Failures become notes."""
    out, problems = [], []
    annual = fund.latest_filing("10-K", "10-K/A")
    quarterly = fund.latest_filing("10-Q", "10-Q/A")
    picks = [f for f in (annual, quarterly) if f is not None]
    if quarterly and annual and quarterly.filed < annual.filed:
        picks = [annual]
    for filing in picks:
        try:
            out.append(read(filing, email, limit_chars))
        except DataError as exc:
            problems.append(f"{filing.form} filed {filing.filed}: {exc}")
    if not picks:
        problems.append("No 10-K or 10-Q in the company's recent filings.")
    return out, problems
