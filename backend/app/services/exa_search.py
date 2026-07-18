from __future__ import annotations

import re

from app.config import get_settings
from app.schemas import Citation

SEARCH_TRIGGERS = re.compile(
    r"("
    r"\?|"
    r"\b(can i|should i|is it safe|what should|what do|how (do|can|much|often)|"
    r"where (is|can|do)|nearest|hospital|clinic|pharmacy|"
    r"government scheme|ayushman|diabetes|blood pressure|bp medicine|"
    r"side effect|diet for|eat if|medication interaction|"
    r"trusted|doctor recommend|who to call)\b"
    r")",
    re.I,
)


def needs_search(message: str) -> bool:
    text = message.strip()
    if len(text) < 8:
        return False
    # Skip pure routine statements unless they ask a question
    routine_only = re.match(
        r"^(i take|i have|remind me|my (medicine|routine|name)|every day)\b",
        text,
        re.I,
    )
    if routine_only and "?" not in text:
        return False
    return bool(SEARCH_TRIGGERS.search(text))


def search_exa(query: str, num_results: int = 5) -> list[Citation]:
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
