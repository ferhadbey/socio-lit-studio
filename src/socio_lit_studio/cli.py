from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from socio_lit_studio.bibtex import to_bibtex
from socio_lit_studio.draft import build_draft
from socio_lit_studio.openalex import OpenAlexClient
from socio_lit_studio.pdfs import ingest_pdf_dir, load_local
from socio_lit_studio.query import load_query
from socio_lit_studio.rank import rank_journals, rank_works

app = typer.Typer(help="Sosyoloji literatur tarama ve taslak asistani")


def _dump(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_scan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@app.command()
def scan(query: Path = typer.Option(..., exists=True), out: Path = typer.Option(Path("outputs/scan.json"))) -> None:
    q = load_query(query)
    client = OpenAlexClient()
    works = rank_works(client.search_works(q), q)
    journals = rank_journals(client.search_journals(q), works, q)
    payload = {"query": q.title, "works": works, "journals": journals}
    _dump(out, payload)
    typer.echo(f"{len(works)} makale, {len(journals)} dergi -> {out}")


@app.command()
def journals(query: Path = typer.Option(..., exists=True), out: Path = typer.Option(Path("outputs/journals.json"))) -> None:
    q = load_query(query)
    client = OpenAlexClient()
    works = rank_works(client.search_works(q), q)
    ranked = rank_journals(client.search_journals(q), works, q)
    _dump(out, ranked)
    for row in ranked[:10]:
        typer.echo(f"{row['fit_score']:>6}  {row['name']}")
    typer.echo(str(out))


@app.command()
def ingest(
    pdf_dir: Path = typer.Option(Path("data/pdfs"), exists=True, file_okay=False),
    out: Path = typer.Option(Path("outputs/local.json")),
) -> None:
    """Read local PDFs. Does not upload them to GitHub."""
    records = ingest_pdf_dir(pdf_dir, out)
    typer.echo(f"{len(records)} PDF -> {out}")


@app.command()
def draft(
    query: Path = typer.Option(..., exists=True),
    scan: Path = typer.Option(..., exists=True),
    local: Optional[Path] = typer.Option(None),
    out: Path = typer.Option(Path("outputs/draft.md")),
) -> None:
    q = load_query(query)
    payload = _load_scan(scan)
    local_works = load_local(local) if local else []
    text = build_draft(
        q,
        payload.get("works") or [],
        payload.get("journals") or [],
        local_works,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    typer.echo(str(out))


@app.command()
def bibtex(
    scan: Path = typer.Option(..., exists=True),
    local: Optional[Path] = typer.Option(None),
    out: Path = typer.Option(Path("outputs/refs.bib")),
) -> None:
    payload = _load_scan(scan)
    works = list(payload.get("works") or [])
    if local:
        works.extend(load_local(local))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_bibtex(works), encoding="utf-8")
    typer.echo(str(out))


if __name__ == "__main__":
    app()
