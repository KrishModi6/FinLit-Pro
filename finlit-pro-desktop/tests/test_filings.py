"""Filing text: HTML to text, and cutting the real sections out past the table of contents."""

import pytest

from finlit_pro.data import filings, http
from finlit_pro.data.models import LIVE, DataError, Filing, Fundamentals

BODY = "The company designs and sells widgets. " * 40
RISKS = "Demand for widgets may fall. " * 40
MDA = "Revenue rose because widget demand rose. " * 40

TEN_K = f"""<html><head><title>10-K</title></head><body>
<ix:header><ix:hidden>dei:EntityCentralIndexKey 0000000001</ix:hidden></ix:header>
<table><tr><td>Item 1.</td><td>Business</td><td>3</td></tr>
<tr><td>Item 1A.</td><td>Risk Factors</td><td>9</td></tr>
<tr><td>Item 7.</td><td>Management&#8217;s Discussion and Analysis</td><td>30</td></tr>
<tr><td>Item 8.</td><td>Financial Statements</td><td>40</td></tr></table>
<p>PART I</p>
<p><b>Item 1. Business</b></p><p>{BODY}</p>
<p><b>Item 1A. Risk Factors</b></p><p>{RISKS}</p>
<p><b>Item 1B. Unresolved Staff Comments</b></p><p>None.</p>
<p><b>Item 7&#160;&#8212; Management&#8217;s Discussion and Analysis of Financial Condition</b></p><p>{MDA}</p>
<p><b>Item 7A. Quantitative and Qualitative Disclosures</b></p><p>Rates.</p>
<p><b>Item 8. Financial Statements</b></p><p>Tables.</p>
<script>var x = 1;</script>
</body></html>"""


def test_html_to_text_drops_markup_scripts_and_hidden_xbrl():
    text = filings.html_to_text(TEN_K)
    assert "<" not in text and "var x" not in text and "EntityCentralIndexKey" not in text
    assert "Management’s Discussion" in text  # entities decoded
    assert "\n\n\n" not in text  # blank lines collapsed


def test_sections_skip_the_table_of_contents():
    text = filings.html_to_text(TEN_K)
    spec = {name: (start, end) for name, start, end in filings.SECTIONS["10-K"]}
    business = filings.extract_section(text, *spec["Business"])
    assert business.startswith("Item 1. Business") and BODY.strip()[:60] in business and "Demand for widgets" not in business
    risks = filings.extract_section(text, *spec["Risk Factors"])
    assert "Demand for widgets" in risks and "Unresolved" not in risks
    mda = filings.extract_section(text, *spec["MD&A"])  # em dash between number and title
    assert "widget demand rose" in mda and "Rates." not in mda


def test_truncate_cuts_on_a_line_break():
    text = "\n".join(["x" * 50] * 10)
    cut, was_cut = filings.truncate(text, 120)
    assert was_cut and len(cut) <= 120 and cut.endswith("x")
    assert filings.truncate("short", 100) == ("short", False)


def filing(form, filed, url="https://www.sec.gov/Archives/edgar/data/1/000000000126000001/doc.htm"):
    return Filing(form, filed, "2026-06-30", form, url, "0000000001-26-000001", "https://www.sec.gov/idx")


def test_read_extracts_sections_with_provenance(monkeypatch):
    monkeypatch.setattr(filings, "get_text", lambda url, **k: http.Fetched(TEN_K, LIVE, 1_760_000_000, url))
    ft = filings.read(filing("10-K", "2026-08-01"), "me@example.com", limit_chars=200)
    assert list(ft.sections) == ["Business", "Risk Factors", "MD&A"]
    assert all(ft.truncated.values()) and all(len(v) <= 200 for v in ft.sections.values())
    assert ft.full_chars["Business"] > 1000
    assert ft.source.url.endswith("doc.htm") and "accession 0000000001-26-000001" in ft.source.detail


def test_read_requires_a_document_link():
    with pytest.raises(DataError, match="no primary document"):
        filings.read(filing("10-K", "2026-08-01", url=""), "me@example.com")


def test_latest_reports_takes_the_10k_and_a_newer_10q(monkeypatch):
    read_forms = []
    monkeypatch.setattr(filings, "read", lambda f, email, limit: read_forms.append(f.form) or f.form)
    fund = Fundamentals(1, "Test", None, {}, {}, None, None, filings=[filing("10-Q", "2026-08-01"), filing("10-K", "2026-02-01"), filing("10-Q", "2025-11-01")])
    texts, problems = filings.latest_reports(fund, "me@example.com")
    assert read_forms == ["10-K", "10-Q"] and problems == []
    # A 10-Q older than the 10-K adds nothing.
    read_forms.clear()
    fund.filings = [filing("10-K", "2026-08-01"), filing("10-Q", "2026-05-01")]
    filings.latest_reports(fund, "me@example.com")
    assert read_forms == ["10-K"]


def test_latest_reports_turns_failures_into_notes(monkeypatch):
    def broken(*_a, **_k):
        raise DataError("SEC EDGAR took too long to respond.")

    monkeypatch.setattr(filings, "read", broken)
    fund = Fundamentals(1, "Test", None, {}, {}, None, None, filings=[filing("10-K", "2026-02-01")])
    texts, problems = filings.latest_reports(fund, "me@example.com")
    assert texts == [] and "took too long" in problems[0]
