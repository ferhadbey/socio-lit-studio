from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def ingest_pdf_dir(pdf_dir: Path, out_path: Path) -> list[dict[str, Any]]:
    """Parse PDFs already on disk. Does not invent titles, authors, or DOIs."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF destegi icin: pip install pypdf") from exc

    records: list[dict[str, Any]] = []
    for path in sorted(pdf_dir.glob("*.pdf")):
        records.append(_read_pdf(path, PdfReader))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return records


def load_local(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _read_pdf(path: Path, reader_cls) -> dict[str, Any]:
    reader = reader_cls(str(path))
    meta = reader.metadata or {}
    title = _clean(getattr(meta, "title", None) or "")
    author = _clean(getattr(meta, "author", None) or "")
    pages = []
    for page in reader.pages[:20]:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            continue
    text = "\n".join(pages).strip()
    doi = _find_doi(text)
    return {
        "source_type": "local_pdf",
        "path": str(path),
        "filename": path.name,
        "title": title or path.stem,
        "authors": [author] if author else [],
        "year": None,
        "venue": "",
        "doi": doi,
        "abstract": text[:1500],
        "text_chars": len(text),
        "matched_terms": [],
        "cite_ok": bool(text),
    }


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _find_doi(text: str) -> str:
    match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, flags=re.I)
    return match.group(0).rstrip(".") if match else ""
