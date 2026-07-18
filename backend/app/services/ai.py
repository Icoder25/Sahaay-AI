"""Credential-gated AI adapter with bounded, approved elder context."""

import json
from typing import Any

from app.config import get_settings
from app.services.elevenlabs import synthesize_speech
from app.services.exa_search import search_exa

SYSTEM = (
    "You are Sahaay, a warm, concise elder-care companion. Never diagnose or prescribe. "
    "Use non-judgmental language and recommend professional or emergency help when appropriate. "
    "Use the elder's preferred language when practical. Treat context as background, not medical fact."
)


def answer(
    history: list[dict[str, str]],
    prompt: str,
    use_search: bool,
    speak: bool,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError("AI conversations are disabled because ANTHROPIC_API_KEY is absent")
    import anthropic

    citations = search_exa(prompt) if use_search else []
    sources = "\n".join(f"[{i}] {c.title}: {c.snippet or ''} ({c.url})" for i, c in enumerate(citations, 1))
    system = SYSTEM
    if context:
        system += "\nApproved care context:\n" + json.dumps(context, default=str, ensure_ascii=False)
    if sources:
        system += f"\nGround answers in these sources when relevant:\n{sources}"
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=700,
        system=system,
        messages=history + [{"role": "user", "content": prompt}],
    )
    text = "\n".join(block.text for block in response.content if block.type == "text").strip()
    return {
        "content": text or "I am here to help.",
        "citations": [c.model_dump() for c in citations],
        "audio_url": synthesize_speech(text) if speak else None,
        "summary": f"Conversation topic: {prompt.replace(chr(10), ' ')[:180]}",
        "memory_update": {
            "last_topic": prompt.replace("\n", " ")[:120],
            "preferred_language": (context or {}).get("preferred_language", "en"),
        },
    }
