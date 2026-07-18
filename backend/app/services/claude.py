"""Claude conversation engine with routine extraction and optional Exa grounding."""

from __future__ import annotations

import json
import re
from typing import Any

import anthropic
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Message, Routine
from app.schemas import Citation
from app.services import memory as memory_service
from app.services.exa_search import needs_search, search_exa

SYSTEM_PROMPT = """You are Sahaay (सहाय), a warm AI care companion for elderly people and their caregivers in India.

Your purpose:
- Learn routines through natural conversation (medicines, appointments, bills, habits)
- Help users stay on track with gentle, personalized reminders
- Answer health/routine questions using provided search sources when available
- Never diagnose, prescribe, or replace a doctor — always suggest consulting a doctor for medical decisions

Tone:
- Warm, respectful, patient — like a caring family member
- Simple language, short sentences
- Non-judgmental (never shame forgetting)
- Prefer Hindi-English mix only if the user writes that way; otherwise match their language

Conversation style:
- Ask one clarifying question at a time when needed
- Confirm extracted routines clearly in a short bullet list
- When search sources are provided, ground your answer in them and mention you used trusted sources

Important:
- You are NOT ChatGPT, NOT a productivity app, NOT a surveillance tool
- Focus on elderly care and caregiver peace of mind
"""

EXTRACT_TOOL = {
    "name": "update_routines",
    "description": (
        "Extract or update structured daily routines mentioned by the user "
        "(medicines, appointments, bills, habits). Call when the user shares "
        "new or updated routine information."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "user_name": {
                "type": "string",
                "description": "User's name if newly learned",
            },
            "routines": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": ["medication", "appointment", "bill", "habit"],
                        },
                        "timing": {
                            "type": "string",
                            "description": "Preferred time like 08:00 or 'morning after breakfast'",
                        },
                        "frequency": {
                            "type": "string",
                            "description": "e.g. daily, twice daily, weekly, monthly on 5th",
                        },
                        "notes": {"type": "string"},
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "normal"],
                        },
                    },
                    "required": ["name", "type"],
                },
            },
        },
        "required": ["routines"],
    },
}

QUESTION_HINTS = re.compile(
    r"\b(what|how|can i|should i|where|when|is it|nearest|hospital|scheme|"
    r"diabetes|medicine|side effect|diet|eat|government|ayushman)\b",
    re.I,
)


def _routines_context(routines: list[Routine]) -> str:
    """Format known routines as context for the Claude system prompt."""
    if not routines:
        return "No routines stored yet."
    lines = []
    for r in routines:
        parts = [f"- {r.name} ({r.type})"]
        if r.timing:
            parts.append(f"at {r.timing}")
        parts.append(f"[{r.frequency}, priority={r.priority}]")
        if r.notes:
            parts.append(f"— {r.notes}")
        lines.append(" ".join(parts))
    return "Known routines:\n" + "\n".join(lines)


def _to_claude_messages(messages: list[Message]) -> list[dict[str, str]]:
    """Convert stored messages into Claude API message dicts."""
    return [{"role": m.role, "content": m.content} for m in messages if m.role in ("user", "assistant")]


def _detect_intent(user_message: str, routines_updated: list, citations: list) -> str:
    """Classify the turn as routine_update, question, or chat."""
    if routines_updated:
        return "routine_update"
    if citations or needs_search(user_message) or QUESTION_HINTS.search(user_message):
        return "question"
    return "chat"


def _client() -> anthropic.Anthropic:
    """Build an Anthropic client or raise if the API key is missing."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def process_chat(db: Session, session_id: str, user_message: str) -> dict[str, Any]:
    """Run the full chat pipeline: memory → optional Exa → Claude → extract routines."""
    settings = get_settings()
    memory_service.add_message(db, session_id, "user", user_message)

    history = memory_service.get_recent_messages(db, session_id, limit=20)
    routines = memory_service.get_routines(db, session_id)

    citations: list[Citation] = []
    search_block = ""
    if needs_search(user_message):
        citations = search_exa(user_message)
        if citations:
            lines = []
            for i, c in enumerate(citations, 1):
                snippet = c.snippet or ""
                lines.append(f"[{i}] {c.title}\nURL: {c.url}\n{snippet}")
            search_block = (
                "Trusted web sources from Exa (use these to ground your answer; "
                "cite by number when relevant):\n\n" + "\n\n".join(lines)
            )

    system_parts = [SYSTEM_PROMPT, _routines_context(routines)]
    if search_block:
        system_parts.append(search_block)
    system = "\n\n".join(system_parts)

    client = _client()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=system,
        tools=[EXTRACT_TOOL],
        messages=_to_claude_messages(history),
    )

    reply_parts: list[str] = []
    extracted_routines: list[dict] = []
    user_name: str | None = None

    for block in response.content:
        if block.type == "text":
            reply_parts.append(block.text)
        elif block.type == "tool_use" and block.name == "update_routines":
            tool_input = block.input or {}
            user_name = tool_input.get("user_name") or user_name
            extracted_routines.extend(tool_input.get("routines") or [])

    # If Claude used a tool but gave little/no text, do a follow-up for a natural reply
    if extracted_routines and not "".join(reply_parts).strip():
        follow = client.messages.create(
            model=settings.claude_model,
            max_tokens=512,
            system=system,
            messages=_to_claude_messages(history)
            + [
                {
                    "role": "assistant",
                    "content": f"I've updated these routines: {json.dumps(extracted_routines)}",
                },
                {
                    "role": "user",
                    "content": "Please confirm the routines warmly in a short message.",
                },
            ],
        )
        for block in follow.content:
            if block.type == "text":
                reply_parts.append(block.text)

    reply = "\n".join(reply_parts).strip() or (
        "I've noted that. Tell me more about your day whenever you're ready."
    )

    updated_models: list[Routine] = []
    if extracted_routines:
        updated_models = memory_service.upsert_routines(db, session_id, extracted_routines)
    if user_name:
        memory_service.set_user_name(db, session_id, user_name)

    memory_service.add_message(db, session_id, "assistant", reply)

    intent = _detect_intent(user_message, updated_models, citations)
    return {
        "reply": reply,
        "routines_updated": updated_models,
        "citations": citations,
        "intent": intent,
    }
