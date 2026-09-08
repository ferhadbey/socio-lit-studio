from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ResearchQuery:
    title: str
    keywords: list[str]
    phrases: list[str] = field(default_factory=list)
    nearby_fields: list[str] = field(default_factory=list)
    research_question: str = ""
    contribution_claim: str = ""
    language: str = "tr"
    year_from: int = 2015
    per_page: int = 25

    @property
    def terms(self) -> list[str]:
        seen: list[str] = []
        for item in [*self.keywords, *self.phrases]:
            text = item.strip()
            if text and text.lower() not in {x.lower() for x in seen}:
                seen.append(text)
        return seen

    @property
    def search_blob(self) -> str:
        quoted = [f'"{p}"' if " " in p else p for p in self.terms[:8]]
        return " OR ".join(quoted) or "sociology"


def load_query(path: Path) -> ResearchQuery:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ResearchQuery(
        title=raw.get("title") or "Untitled inquiry",
        keywords=list(raw.get("keywords") or []),
        phrases=list(raw.get("phrases") or []),
        nearby_fields=list(raw.get("nearby_fields") or []),
        research_question=raw.get("research_question") or "",
        contribution_claim=raw.get("contribution_claim") or "",
        language=raw.get("language") or "tr",
        year_from=int(raw.get("year_from") or 2015),
        per_page=int(raw.get("per_page") or 25),
    )
