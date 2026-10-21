"""Text of SEC filings: the latest 10-K and 10-Q, split into their key items.

Filings on EDGAR are inline-XBRL HTML. This module strips them to text and
cuts out the sections an analyst reads first:

  10-K  Item 1 Business, Item 1A Risk Factors, Item 7 MD&A
  10-Q  Part I Item 2 MD&A, Part II Item 1A Risk Factors

Every filing names each item twice, once in the table of contents and once
as the real heading, so for each item the longest span between its heading
and the next item's heading is taken; table-of-contents spans are a line long.
Headings start a line; the same words inside a sentence, usually in quotes
('see "Item 1A. Risk Factors" in Part I'), are cross-references and are skipped.
A heading may also follow its Part heading on the same line
("PART II. OTHER INFORMATION Item 1A. Risk Factors").
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

# Shortest text kept as a section. A 10-Q's Risk Factors item only has to say whether anything changed since the
# 10-K, so it is often a few sentences: JPM's 10-Q has 402 characters there.
MIN_SECTION_CHARS = 500
MIN_CHARS_FOR = {("10-Q", "Risk Factors"): 150}

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


# After a cross-reference's title comes its closing quote: "Item 7. Management's Discussion and Analysis ...".
_TITLE_THEN_QUOTE = re.compile(r"[\w \t&'\u2019\-\u2013\u2014:]{0,90}?[\"\u201d]")
_COMMA_OR_QUOTE = re.compile(r"[ \t]*(,|[.;:]?[ \t]*[\"\u201d])")


def _quoted(text: str, m: re.Match) -> bool:
    """A match inside quotation marks or followed by a comma: a cross-reference, not a heading."""
    before = text[max(0, m.start() - 4): m.start()]
    # An opening quote just before it on the same line, or a curly one ending the line above.
    if before.rsplit("\n", 1)[-1].rstrip(" \t").endswith(("\u201c", '"')) or before.rstrip().endswith("\u201c"):
        return True
    return bool(_COMMA_OR_QUOTE.match(text, m.end()) or _TITLE_THEN_QUOTE.match(text, m.end()))


def _headings(text: str, pattern: str) -> tuple[list[int], list[int]]:
    """Offsets of the pattern's matches: (at a line start and not quoted, anywhere and not quoted)."""
    line, loose = [], []
    for m in re.finditer(pattern, text, flags=re.IGNORECASE):
        if _quoted(text, m):
            continue
        loose.append(m.start())
        if m.start() == 0 or text[m.start() - 1] == "\n":
            line.append(m.start())
    return line, loose


# Text before an item heading on its line that makes it a heading: a Part heading such as "PART II. OTHER INFORMATION".
_PART_PREFIX = re.compile(r"\s*part\s+(?:i{1,3}|iv)\b[\s.:|\-\u2013\u2014]*(?:[a-z][a-z ,&]{0,40}?[\s.:|\-\u2013\u2014]*)?", re.IGNORECASE)


def _after_part_heading(text: str, offsets: list[int]) -> list[int]:
    """The offsets whose line holds only a Part heading before them."""
    return [p for p in offsets if _PART_PREFIX.fullmatch(text, text.rfind("\n", 0, p) + 1, p)]


def _contents(span: str) -> bool:
    """A table of contents: at least three bare page numbers, and a third or more of the lines are page numbers."""
    lines = [line for line in span.split("\n") if line.strip()]
    pages = sum(1 for line in lines if re.fullmatch(r"\s*\d{1,3}\s*", line))
    return pages >= 3 and pages * 3 >= len(lines)


def _longest(text: str, starts: list[int], ends: list[int], spare_ends: list[int] | None = None) -> str:
    # First Version: a heading found only in the table of contents (JPM's 10-Q names MD&A
    # "Item 2" only there) returned the contents listing as the section. Current Version:
    # spans that read as a table of contents are skipped.
    best = ""
    for s in starts:
        following = [e for e in ends if e > s + 20] or [e for e in spare_ends or [] if e > s + 20]
        stop = following[0] if following else len(text)
        span = text[s:stop].strip()
        if len(span) > len(best) and not _contents(span):
            best = span
    return best


def extract_section(text: str, start_pattern: str, end_pattern: str) -> str:
    """Longest span from a heading to the next end heading, headings being matches that start a line.

    First Version: the longest span from any match of the heading to the next end match. A
    cross-reference such as "see \u201cItem 1A. Risk Factors\u201d in Part I" with no end heading
    after it made the longest span, so KO's Risk Factors began inside MD&A and ran 389,000
    characters, and its MD&A was a 3,000-character cross-reference.
    Current Version: a heading must start its line and not be quoted or followed by a closing
    quote or a comma; end headings likewise (an end that is not at a line start is used only
    when no line-start end follows). The old rule applies only when no line-start heading exists.

    First Version (of that rule): line-start headings excluded every other match, so a real heading
    sharing its line with the Part heading ("PART II. OTHER INFORMATION Item 1A. Risk Factors") lost
    to the 24-character contents entry. Current Version: when every line-start span is shorter than
    MIN_SECTION_CHARS, headings that follow a Part heading on their line are tried too, and the
    longer span wins. Other mid-line matches stay excluded: JPM's 10-Q says "Refer to Part I, Item
    1A: Risk Factors on pages 9-31 of the 10-K" right after its real, short Risk Factors heading.
    """
    starts, loose_starts = _headings(text, start_pattern)
    ends, loose_ends = _headings(text, end_pattern)
    if starts:
        best = _longest(text, starts, ends, loose_ends)
        if len(best) < MIN_SECTION_CHARS:
            shared = _after_part_heading(text, [s for s in loose_starts if s not in starts])
            other = _longest(text, shared, ends, loose_ends) if shared else ""
            best = other if len(other) > len(best) else best
        return best
    if loose_starts:
        return _longest(text, loose_starts, loose_ends)
    every_start = [m.start() for m in re.finditer(start_pattern, text, flags=re.IGNORECASE)]
    every_end = [m.start() for m in re.finditer(end_pattern, text, flags=re.IGNORECASE)]
    return _longest(text, every_start, every_end)


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
        # First Version: a section under 500 characters was "not found", which dropped JPM's real 10-Q Risk Factors
        # (402 characters: no material changes, see the 10-K). Current Version: a 10-Q's Risk Factors needs 150.
        if len(body) < MIN_CHARS_FOR.get((base, name), MIN_SECTION_CHARS):
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


def _read_report(fund: Fundamentals, form: str, email: str, limit_chars: int, problems: list[str]) -> FilingText | None:
    """The newest plain filing of `form`, or a newer amendment of it when the amendment carries the sections.

    First Version: the newest of 10-K and 10-K/A was read. Many companies file a 10-K/A only to add
    Part III (directors and pay) a couple of months later, so SHOP's annual text came back with no
    Business, Risk Factors or MD&A. Current Version: the plain 10-K is preferred; a newer amendment
    is used only if it contains the sections, otherwise the plain filing is read and the reason noted.
    """
    plain, amended = fund.latest_filing(form), fund.latest_filing(form + "/A")
    why = None
    if amended and (plain is None or amended.filed > plain.filed):
        try:
            ft = read(amended, email, limit_chars)
            if ft.sections or plain is None:
                return ft
            why = f"The {amended.form} filed {amended.filed} does not contain these sections (it amends other items), so the {plain.form} filed {plain.filed} is read."
        except DataError as exc:
            if plain is None:
                problems.append(f"{amended.form} filed {amended.filed}: {exc}")
                return None
            why = f"The {amended.form} filed {amended.filed} could not be read, so the {plain.form} filed {plain.filed} is read. ({exc})"
    if plain is None:
        return None
    try:
        ft = read(plain, email, limit_chars)
    except DataError as exc:
        problems.append(f"{plain.form} filed {plain.filed}: {exc}")
        return None
    if why:
        ft.notes.insert(0, why)
    return ft


def latest_reports(fund: Fundamentals, email: str, limit_chars: int = 40_000) -> tuple[list[FilingText], list[str]]:
    """The most recent 10-K and, if newer, the most recent 10-Q. Failures become notes."""
    out, problems = [], []
    annual = fund.latest_filing("10-K") or fund.latest_filing("10-K/A")
    quarterly = fund.latest_filing("10-Q") or fund.latest_filing("10-Q/A")
    forms = [f.form.split("/")[0] for f in (annual, quarterly) if f is not None]
    if quarterly and annual and quarterly.filed < annual.filed:
        forms = ["10-K"]
    if forms:
        # First Version: a bad SEC contact email failed each filing separately, so the same message appeared once
        # for the 10-K and again for the 10-Q. Current Version: the email is checked once, before any request.
        try:
            sec_headers(email)
        except DataError as exc:
            return out, [str(exc)]
    for form in forms:
        ft = _read_report(fund, form, email, limit_chars, problems)
        if ft is not None:
            out.append(ft)
    if not forms:
        # First Version: "No 10-K or 10-Q" even for a foreign issuer whose 20-F was right there.
        # Current Version: says which annual form the company files and that it is not read.
        foreign = next((f for f in ("20-F", "40-F") if fund.latest_filing(f, f + "/A")), None)
        if foreign:
            problems.append(f"{fund.name} files annual reports on Form {foreign}; FinLit Pro reads 10-K and 10-Q text only.")
        elif fund.latest_filing("6-K"):
            problems.append(f"{fund.name} files reports on Form 6-K; FinLit Pro reads 10-K and 10-Q text only.")
        else:
            problems.append("No 10-K or 10-Q in the company's recent filings.")
    return out, problems
