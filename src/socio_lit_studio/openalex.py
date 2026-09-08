from __future__ import annotations

from typing import Any

import httpx

from socio_lit_studio.config import Settings, settings
from socio_lit_studio.query import ResearchQuery

# OpenAlex sociology concept (legacy concepts still useful as a soft filter).
SOCIOLOGY_CONCEPT = "C144024400"


class OpenAlexClient:
    def __init__(self, cfg: Settings | None = None) -> None:
        self.cfg = cfg or settings

    def _params(self, extra: dict[str, Any]) -> dict[str, Any]:
        params = {"mailto": self.cfg.openalex_mailto, **extra}
        return {k: v for k, v in params.items() if v is not None}

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.cfg.openalex_base_url}{path}"
        headers = {"User-Agent": f"socio-lit-studio (mailto:{self.cfg.openalex_mailto})"}
        with httpx.Client(timeout=45.0, headers=headers) as client:
            response = client.get(url, params=self._params(params))
            response.raise_for_status()
            return response.json()

    def search_works(self, query: ResearchQuery) -> list[dict[str, Any]]:
        filters = [
            f"from_publication_date:{query.year_from}-01-01",
            "type:article",
            f"concepts.id:{SOCIOLOGY_CONCEPT}|concepts.id:C162324750",  # sociology | social science
        ]
        data = self._get(
            "/works",
            {
                "search": query.search_blob,
                "filter": ",".join(filters),
                "sort": "relevance_score:desc",
                "per_page": min(query.per_page, 50),
                "select": "id,doi,display_name,publication_year,authorships,primary_location,abstract_inverted_index,cited_by_count,concepts",
            },
        )
        works = []
        for item in data.get("results", []):
            works.append(self._normalize_work(item))
        return works

    def search_journals(self, query: ResearchQuery) -> list[dict[str, Any]]:
        blob = " ".join(["sociology", *query.keywords[:5], *query.nearby_fields[:3]])
        data = self._get(
            "/sources",
            {
                "search": blob,
                "filter": "type:journal,has_issn:true",
                "sort": "cited_by_count:desc",
                "per_page": 25,
                "select": "id,display_name,issn_l,issn,host_organization_name,works_count,cited_by_count,is_oa,is_in_doaj,homepage_url,type",
            },
        )
        return data.get("results", [])

    @staticmethod
    def _normalize_work(item: dict[str, Any]) -> dict[str, Any]:
        authors = []
        for auth in item.get("authorships") or []:
            name = (auth.get("author") or {}).get("display_name")
            if name:
                authors.append(name)
        source = ((item.get("primary_location") or {}).get("source") or {})
        return {
            "id": item.get("id"),
            "doi": item.get("doi"),
            "title": item.get("display_name"),
            "year": item.get("publication_year"),
            "authors": authors,
            "venue": source.get("display_name"),
            "venue_id": source.get("id"),
            "cited_by_count": item.get("cited_by_count") or 0,
            "abstract": invert_abstract(item.get("abstract_inverted_index")),
            "concepts": [c.get("display_name") for c in (item.get("concepts") or [])[:8] if c.get("display_name")],
        }


def invert_abstract(index: dict | None) -> str:
    if not index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, spots in index.items():
        for spot in spots:
            positions.append((int(spot), word))
    positions.sort()
    return " ".join(word for _, word in positions)
