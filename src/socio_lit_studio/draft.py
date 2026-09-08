from __future__ import annotations

from datetime import date
from typing import Any

from socio_lit_studio.query import ResearchQuery


def build_draft(
    query: ResearchQuery,
    works: list[dict[str, Any]],
    journals: list[dict[str, Any]],
    local_works: list[dict[str, Any]] | None = None,
) -> str:
    local_works = local_works or []
    catalog = [_catalog_line(w, origin="openalex") for w in works]
    catalog += [_catalog_line(w, origin="local_pdf") for w in local_works if w.get("cite_ok")]
    journal_lines = [
        f"- {j['name']} (fit {j['fit_score']}, scan ici {j['papers_in_scan']} makale)"
        for j in journals[:8]
    ]
    return f"""# {query.title}

> Taslak. Metin ici referans YOK.
> Yalnizca asagidaki katalogdaki kayitlara atif dusulebilir.
> Katalog disi yazar-yil uydurulmaz. Ampirik bulgu yazilmaz.

- Tarih: {date.today().isoformat()}
- Arastirma sorusu: {query.research_question or "(yazilmadi)"}
- Katki iddiasi: {query.contribution_claim or "(yazilmadi)"}

## 1. Giris iskeleti

Soru: {query.research_question or query.title}
Anahtarlar: {", ".join(query.keywords)}

Bu bolume kaynak ekleme. Kaynaklari yalnizca asagidaki katalog numaralariyla sonra sen yazacaksin.

## 2. Kaynak katalogu (atif evreni)

Bu liste tarama + senin PDF'lerin. Listede yoksa atif yok.

{chr(10).join(catalog) or "- Katalog bos. Once scan veya ingest calistir."}

## 3. Bosluk notu (atif degil)

Az eslesen ifadeler: {', '.join(_rare_phrases(query, works + local_works)) or 'yok'}.

## 4. Yontem (sen dolduracaksin)

- Tasarim:
- Veri:
- Analiz:
- Etik:

## 5. Beklenen katki

{query.contribution_claim or "Henuz yazilmadi."}

## 6. Olasi dergiler

{chr(10).join(journal_lines) or "- Dergi bulunamadi."}

## 7. Kurallar

- Metin ici (Author, yil) yok; henuz arguman yazilmadi
- Katalog disi kaynak ekleme
- PDF'den DOI cikmazsa bos birak; uydurma
- Her kaydi orijinalinden oku
"""


def _catalog_line(work: dict[str, Any], origin: str) -> str:
    authors = work.get("authors") or []
    lead = authors[0] if authors else "(yazar metadata yok)"
    year = work.get("year") or "(yil yok)"
    title = work.get("title") or work.get("filename") or "(baslik yok)"
    venue = work.get("venue") or ""
    doi = work.get("doi") or ""
    extra = work.get("filename") or work.get("path") or ""
    snippet = (work.get("abstract") or "").strip()
    if len(snippet) > 280:
        snippet = snippet[:277] + "..."
    note = snippet or "(ozet/metin yok; atif oncesi dosyayi oku)"
    return f"- [{origin}] {lead} ({year}). {title}. {venue} {doi} {extra}\n  {note}"


def _rare_phrases(query: ResearchQuery, works: list[dict[str, Any]]) -> list[str]:
    blob = " ".join((w.get("title") or "") + " " + (w.get("abstract") or "") for w in works).lower()
    return [p for p in query.phrases if p.lower() not in blob]
