from __future__ import annotations

import json
from pathlib import Path

import typer

from socio_lit_studio.bibtex import to_bibtex
from socio_lit_studio.draft import build_draft
from socio_lit_studio.openalex import OpenAlexClient
from socio_lit_studio.query import load_query
from socio_lit_studio.rank import rank_journals, rank_works

app = typer.Typer(help="Sosyoloji literatür tarama ve taslak asistanı")


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
def draft(
    query: Path = typer.Option(..., exists=True),
    scan: Path = typer.Option(..., exists=True),
    out: Path = typer.Option(Path("outputs/draft.md")),
) -> None:
    q = load_query(query)
    payload = _load_scan(scan)
    text = build_draft(q, payload.get("works") or [], payload.get("journals") or [])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    typer.echo(str(out))


@app.command()
def bibtex(scan: Path = typer.Option(..., exists=True), out: Path = typer.Option(Path("outputs/refs.bib"))) -> None:
    payload = _load_scan(scan)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_bibtex(payload.get("works") or []), encoding="utf-8")
    typer.echo(str(out))


if __name__ == "__main__":
    app()
