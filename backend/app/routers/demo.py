"""Unauthenticated demo endpoints for the hackathon frontend (`/chat`, routines, reminder demo)."""

from __future__ import annotations

import re
from threading import Lock
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services.ai import answer
from app.services.exa_search import needs_search
from app.services.elevenlabs import synthesize_speech

router = APIRouter(tags=["demo"])

_lock = Lock()
# session_id -> { "name": str|None, "messages": [...], "routines": {name_lower: Routine} }
_sessions: dict[str, dict[str, Any]] = {}

EXTRACT_TOOL = {
    "name": "update_routines",
    "description": "Extract medicines, appointments, bills, or habits the user mentioned.",
    "input_schema": {
        "type": "object",
        "properties": {
            "user_name": {"type": "string"},
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
                        "timing": {"type": "string"},
                        "frequency": {"type": "string"},
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


class DemoChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1)
    speak: bool = True


class DemoCitation(BaseModel):
    title: str
    url: str
    snippet: str | None = None


class DemoRoutine(BaseModel):
    id: int | None = None
    name: str
    type: str
    timing: str | None = None
    frequency: str = "daily"
    notes: str | None = None
    priority: str = "normal"


class DemoChatResponse(BaseModel):
    reply: str
    session_id: str
    routines_updated: list[DemoRoutine] = []
    citations: list[DemoCitation] = []
    audio_url: str | None = None
    intent: Literal["routine_update", "question", "chat"] = "chat"


class DemoReminderOut(BaseModel):
    id: int
    session_id: str
    routine_id: int | None
    message: str
    scheduled_time: str | None
    is_demo: bool


class DemoReminderResponse(BaseModel):
    message: str
    routine: DemoRoutine | None = None
    audio_url: str | None = None
    reminder: DemoReminderOut | None = None


def _session(session_id: str) -> dict[str, Any]:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "name": None,
            "messages": [],
            "routines": {},
            "next_routine_id": 1,
            "next_reminder_id": 1,
        }
    return _sessions[session_id]


def _upsert_routines(session: dict[str, Any], items: list[dict]) -> list[DemoRoutine]:
    updated: list[DemoRoutine] = []
    for item in items:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        key = name.lower()
        existing = session["routines"].get(key)
        if existing:
            existing.update(
                {
                    "type": item.get("type") or existing["type"],
                    "timing": item.get("timing") or existing.get("timing"),
                    "frequency": item.get("frequency") or existing.get("frequency", "daily"),
                    "notes": item.get("notes") if item.get("notes") is not None else existing.get("notes"),
                    "priority": item.get("priority") or existing.get("priority", "normal"),
                }
            )
            routine = existing
        else:
            routine = {
                "id": session["next_routine_id"],
                "name": name,
                "type": item.get("type") or "habit",
                "timing": item.get("timing"),
                "frequency": item.get("frequency") or "daily",
                "notes": item.get("notes"),
                "priority": item.get("priority") or "normal",
            }
            session["next_routine_id"] += 1
            session["routines"][key] = routine
        updated.append(DemoRoutine(**routine))
    return updated


def _extract_routines(user_message: str, history: list[dict[str, str]]) -> tuple[list[dict], str | None]:
    settings = get_settings()
    if not settings.anthropic_api_key:
        return [], None
    if not re.search(
        r"\b(medicine|medication|pill|tablet|appointment|bill|remind|routine|every day|daily|am|pm)\b",
        user_message,
        re.I,
    ):
        return [], None

    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=512,
        system=(
            "Extract any routines from the latest user message. "
            "If none, call update_routines with an empty routines list."
        ),
        tools=[EXTRACT_TOOL],
        messages=history + [{"role": "user", "content": user_message}],
    )
    routines: list[dict] = []
    user_name: str | None = None
    for block in response.content:
        if block.type == "tool_use" and block.name == "update_routines":
            payload = block.input or {}
            user_name = payload.get("user_name") or user_name
            routines.extend(payload.get("routines") or [])
    return routines, user_name


def _detect_intent(user_message: str, routines_updated: list, citations: list) -> str:
    if routines_updated:
        return "routine_update"
    if citations or needs_search(user_message):
        return "question"
    return "chat"


@router.post("/chat", response_model=DemoChatResponse)
def demo_chat(body: DemoChatRequest) -> DemoChatResponse:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY is not configured.",
        )

    with _lock:
        session = _session(body.session_id)
        history = list(session["messages"])[-20:]

    extracted, user_name = _extract_routines(body.message.strip(), history)

    try:
        result = answer(
            history,
            body.message.strip(),
            use_search=needs_search(body.message),
            speak=False,
            context={
                "demo_session": True,
                "known_routines": list(_session(body.session_id)["routines"].values()),
                "user_name": _session(body.session_id).get("name"),
            },
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI request failed: {exc}") from exc

    reply = result["content"]
    citations = [DemoCitation(**c) if isinstance(c, dict) else DemoCitation.model_validate(c) for c in result.get("citations") or []]

    with _lock:
        session = _session(body.session_id)
        if user_name:
            session["name"] = user_name.strip()
        updated = _upsert_routines(session, extracted) if extracted else []
        session["messages"].append({"role": "user", "content": body.message.strip()})
        session["messages"].append({"role": "assistant", "content": reply})
        if updated and "Got it" not in reply and "noted" not in reply.lower():
            # Keep natural reply from answer(); routines already stored
            pass

    audio_url = synthesize_speech(reply) if body.speak else None
    intent = _detect_intent(body.message, updated, citations)

    return DemoChatResponse(
        reply=reply,
        session_id=body.session_id,
        routines_updated=updated,
        citations=citations,
        audio_url=audio_url,
        intent=intent,  # type: ignore[arg-type]
    )


@router.get("/routines/{session_id}", response_model=list[DemoRoutine])
def list_demo_routines(session_id: str) -> list[DemoRoutine]:
    with _lock:
        session = _session(session_id)
        return [DemoRoutine(**r) for r in session["routines"].values()]


@router.get("/reminders/demo", response_model=DemoReminderResponse)
def reminder_demo(session_id: str, speak: bool = True) -> DemoReminderResponse:
    with _lock:
        session = _session(session_id)
        routines = list(session["routines"].values())
        name = session.get("name") or "there"

        meds = [r for r in routines if r.get("type") == "medication"]
        critical = [r for r in meds if r.get("priority") == "critical"]
        routine = (critical or meds or routines or [None])[0]

        if routine is None:
            message = (
                f"Good morning {name}. "
                "I'm here whenever you need a gentle reminder about your routine."
            )
            routine_out = None
            routine_id = None
            scheduled = None
        else:
            time_bit = f" (usually around {routine['timing']})" if routine.get("timing") else ""
            if routine.get("type") == "medication":
                message = f"Good morning {name}. It's time for your {routine['name']}{time_bit}."
            else:
                message = f"Hi {name}. Gentle nudge for {routine['name']}{time_bit}."
            routine_out = DemoRoutine(**routine)
            routine_id = routine.get("id")
            scheduled = routine.get("timing")

        reminder_id = session["next_reminder_id"]
        session["next_reminder_id"] += 1
        reminder = DemoReminderOut(
            id=reminder_id,
            session_id=session_id,
            routine_id=routine_id,
            message=message,
            scheduled_time=scheduled,
            is_demo=True,
        )

    audio_url = synthesize_speech(message) if speak else None
    return DemoReminderResponse(
        message=message,
        routine=routine_out,
        audio_url=audio_url,
        reminder=reminder,
    )
