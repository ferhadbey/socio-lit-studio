from __future__ import annotations

from typing import Any


def to_bibtex(works: list[dict[str, Any]]) -> str:
    blocks = []
    for i, work in enumerate(works, start=1):
        key = f"scan{i:03d}"
        authors = " and ".join(work.get("authors") or ["Unknown"])
        title = _esc(work.get("title") or "Untitled")
        year = work.get("year") or ""
        journal = _esc(work.get("venue") or "")
        doi = (work.get("doi") or "").replace("https://doi.org/", "")
        blocks.append(
            "\n".join(
                [
                    f"@article{{{key},",
                    f"  author = {{{authors}}},",
                    f"  title = {{{title}}},",
                    f"  journal = {{{journal}}},",
                    f"  year = {{{year}}},",
                    f"  doi = {{{doi}}}",",
                    "}",
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def _esc(text: str) -> str:
    return text.replace("{", "\\{").replace("}", "\\}")
