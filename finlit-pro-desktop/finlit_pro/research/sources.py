"""Numbered sources for the research note.

Every dataset and filing the analysis may rely on gets a stable ID (S1, S2,
...). The brief tags each figure with the ID of the record it came from,
the analysis engine must cite those IDs, and the rendered note links each
ID to its URL with its report date and retrieval time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from finlit_pro.data.models import FactRef, Source


@dataclass
class SourceEntry:
    id: str
    title: str
    url: str
    as_of: str | None
    retrieved: datetime | None
    detail: str = ""
    kind: str = "data"  # data, filing, computation, headline


@dataclass
class SourceRegistry:
    entries: list[SourceEntry] = field(default_factory=list)
    _by_key: dict[str, str] = field(default_factory=dict)

    def _add(self, key: str, **kw) -> str:
        if key in self._by_key:
            return self._by_key[key]
        sid = f"S{len(self.entries) + 1}"
        self.entries.append(SourceEntry(id=sid, **kw))
        self._by_key[key] = sid
        return sid

    def dataset(self, src: Source) -> str:
        return self._add(
            f"src:{src.name}:{src.url}",
            title=src.name,
            url=src.url,
            as_of=src.as_of,
            retrieved=src.retrieved_at,
            detail=" ".join(x for x in (src.detail, f"({src.status})") if x),
        )

    def filing(self, ref: FactRef, company: str) -> str:
        return self._add(
            f"acc:{ref.accession}",
            title=f"{company} {ref.form}",
            url=ref.url,
            as_of=None,
            retrieved=None,
            detail=f"Filed {ref.filed}, accession {ref.accession}",
            kind="filing",
        )

    def filing_record(self, filing, company: str) -> str:
        """A filing from the company's filing index (shares IDs with `filing`)."""
        return self._add(
            f"acc:{filing.accession}",
            title=f"{company} {filing.form}",
            url=filing.index_url or filing.url,
            as_of=filing.report_date or None,
            retrieved=None,
            detail=f"Filed {filing.filed}, accession {filing.accession}",
            kind="filing",
        )

    def filing_section(self, src: Source, section: str) -> str:
        return self._add(
            f"sec:{src.url}:{section}",
            title=f"{src.name}: {section}",
            url=src.url,
            as_of=src.as_of,
            retrieved=src.retrieved_at,
            detail=src.detail,
            kind="filing",
        )

    def computation(self, name: str, detail: str) -> str:
        return self._add(f"calc:{name}", title=f"FinLit Pro computation: {name}", url="", as_of=None, retrieved=datetime.now(), detail=detail, kind="computation")

    def headline(self, title: str, url: str, publisher: str, published: datetime | None) -> str:
        return self._add(f"news:{url or title}", title=f"Headline ({publisher}): {title}", url=url, as_of=published.strftime("%Y-%m-%d") if published else None, retrieved=None, detail="Unverified news headline; title only", kind="headline")

    def ids(self) -> set[str]:
        return {e.id for e in self.entries}

    def get(self, sid: str) -> SourceEntry | None:
        return next((e for e in self.entries if e.id == sid), None)
