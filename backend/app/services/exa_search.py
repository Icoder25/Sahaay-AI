"""Exa search helpers for grounded health and routine answers."""

from __future__ import annotations

from app.config import get_settings
from app.schemas import Citation

def search_exa(query: str, num_results: int = 5) -> list[Citation]:
    """Search Exa and return citation objects; empty list if unavailable."""
    settings = get_settings()
    if not settings.exa_api_key:
        return []

    try:
        from exa_py import Exa

        exa = Exa(api_key=settings.exa_api_key)
        # Prefer trusted health / India public sources when possible
        result = exa.search_and_contents(
            query,
            type="auto",
            num_results=num_results,
            text={"max_characters": 800},
            highlights={"num_sentences": 2},
        )
    except Exception:
        return []

    citations: list[Citation] = []
    for item in getattr(result, "results", []) or []:
        title = getattr(item, "title", None) or "Source"
        url = getattr(item, "url", None) or ""
        if not url:
            continue
        text = getattr(item, "text", None) or ""
        highlights = getattr(item, "highlights", None) or []
        snippet = " ".join(highlights) if highlights else (text[:300] if text else None)
        citations.append(Citation(title=title, url=url, snippet=snippet))
    return citations
