from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from socio_lit_studio.config import settings
from socio_lit_studio.query import ResearchQuery


def build_draft(
    query: ResearchQuery,
    works: list[dict[str, Any]],
    journals: list[dict[str, Any]],
) -> str:
    top_works = works[:12]
    top_journals = journals[:8]
    bullets = []
    for work in top_works:
        cite = _cite(work)
        snippet = (work.get("abstract") or "").strip()
        if len(snippet) > 320:
            snippet = snippet[:317] + "..."
        if snippet:
            bullets.append(f"- {cite}: {snippet}")
        else:
            bullets.append(f"- {cite}")
    journal_lines = []
    for journal in top_journals:
        journal_lines.append(
            f"- {journal['name']} (fit {journal['fit_score']}, scan içi {journal['papers_in_scan']} makale)"
        )
    body = f"""# {query.title}

> Taslak. Kaynaklar OpenAlex taramasından gelir. Atıfları DOI ile doğrula.
> Ampirik bulgu üretilmez. Yöntem ve veri sana ait.

- Tarih: {date.today().isoformat()}
- Araştırma sorusu: {query.research_question or "(yazılmadı)"}
- Katkı iddiası: {query.contribution_claim or "(yazılmadı)"}

## 1. Giriş

Bu çalışma şu soruya yönelir: {query.research_question or query.title}.
Anahtar odaklar: {", ".join(query.keywords)}.

## 2. Literatür (taramadan)

{chr(10).join(bullets) or "- Tarama sonuç vermedi."}

## 3. Boşluk notu

Taramada sık geçen terimler ile senin cümlelerin kesişiyor olabilir; az eşleşen ifade boşluk adayıdır.
Az eşleşen ifadeler: {', '.join(_rare_phrases(query, works)) or 'yok'}.

## 4. Yöntem (sen dolduracaksın)

- Tasarım:
- Veri:
- Analiz:
- Etik:

## 5. Beklenen katkı

{query.contribution_claim or "Henüz yazılmadı."}

## 6. Olası dergiler

{chr(10).join(journal_lines) or "- Dergi bulunamadı."}

## 7. Göndermeden önce

- Her kaynağı oku
- Uydurma alıntı yok
- Derginin aims & scope sayfasını kontrol et
- Yöntem ve bulguları sen yaz
"""
    return polish_optional(body)


def _cite(work: dict[str, Any]) -> str:
    authors = work.get("authors") or []
    lead = authors[0] if authors else "Anon"
    year = work.get("year") or "n.d."
    title = work.get("title") or "Untitled"
    venue = work.get("venue") or ""
    doi = work.get("doi") or ""
    return f"{lead} ({year}). {title}. {venue} {doi}".strip()


def _rare_phrases(query: ResearchQuery, works: list[dict[str, Any]]) -> list[str]:
    blob = " ".join((w.get("title") or "") + " " + (w.get("abstract") or "") for w in works).lower()
    return [p for p in query.phrases if p.lower() not in blob]


def polish_optional(text: str) -> str:
    if not settings.xai_api_key:
        return text
    payload = {
        "model": settings.xai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Akademik Türkçe düzenle. Yeni kaynak, veri veya bulgu ekleme. "
                    "Var olan DOI/künyeleri değiştirme. Taslak olduğunu koru."
                ),
            },
            {"role": "user", "content": text},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.xai_api_key}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=90.0) as client:
            response = client.post(f"{settings.xai_base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return text
