from __future__ import annotations

from collections import Counter
from typing import Any

from socio_lit_studio.query import ResearchQuery


def _haystack(work: dict[str, Any]) -> str:
    parts = [work.get("title") or "", work.get("abstract") or "", " ".join(work.get("concepts") or [])]
    return " ".join(parts).lower()


def score_work(work: dict[str, Any], query: ResearchQuery) -> dict[str, Any]:
    text = _haystack(work)
    hits = [term for term in query.terms if term.lower() in text]
    score = len(hits) * 3 + min(work.get("cited_by_count") or 0, 200) / 50
    ranked = dict(work)
    ranked["match_score"] = round(score, 2)
    ranked["matched_terms"] = hits
    return ranked


def rank_works(works: list[dict[str, Any]], query: ResearchQuery) -> list[dict[str, Any]]:
    ranked = [score_work(w, query) for w in works]
    ranked.sort(key=lambda w: w["match_score"], reverse=True)
    return ranked


def rank_journals(
    journals: list[dict[str, Any]],
    works: list[dict[str, Any]],
    query: ResearchQuery,
) -> list[dict[str, Any]]:
    venue_hits = Counter(w.get("venue") for w in works if w.get("venue"))
    out = []
    for journal in journals:
        name = journal.get("display_name") or ""
        blob = f"{name} {journal.get('host_organization_name') or ''}".lower()
        term_hits = [t for t in query.terms if t.lower() in blob]
        field_hits = [f for f in query.nearby_fields if f.lower() in blob]
        from_scan = venue_hits.get(name, 0)
        score = from_scan * 5 + len(term_hits) * 2 + len(field_hits) + min(journal.get("cited_by_count") or 0, 50000) / 10000
        out.append(
            {
                "name": name,
                "id": journal.get("id"),
                "issn_l": journal.get("issn_l"),
                "publisher": journal.get("host_organization_name"),
                "works_count": journal.get("works_count"),
                "cited_by_count": journal.get("cited_by_count"),
                "is_oa": journal.get("is_oa"),
                "is_in_doaj": journal.get("is_in_doaj"),
                "homepage_url": journal.get("homepage_url"),
                "papers_in_scan": from_scan,
                "matched_terms": term_hits,
                "fit_score": round(score, 2),
            }
        )
    out.sort(key=lambda j: j["fit_score"], reverse=True)
    return out
