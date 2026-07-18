"""Pydantic request and response schemas for the Sahaay API."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message for a demo session."""

    session_id: str = Field(..., description="Client-generated UUID for the demo session")
    message: str = Field(..., min_length=1)
    speak: bool = Field(default=True, description="Generate ElevenLabs audio for the reply")


class Citation(BaseModel):
    """A grounded web source returned with an Exa-backed answer."""

    title: str
    url: str
    snippet: str | None = None


class RoutineOut(BaseModel):
    """Serialized routine for API responses."""

    id: int | None = None
    name: str
    type: str
    timing: str | None = None
    frequency: str = "daily"
    notes: str | None = None
    priority: str = "normal"

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Assistant reply plus optional routines, citations, and audio."""

    reply: str
    session_id: str
    routines_updated: list[RoutineOut] = []
    citations: list[Citation] = []
    audio_url: str | None = None
    intent: Literal["routine_update", "question", "chat"] = "chat"


class ReminderCreate(BaseModel):
    """Payload to create a reminder for a session."""

    session_id: str
    routine_id: int | None = None
    message: str | None = None
    scheduled_time: str | None = None


class ReminderOut(BaseModel):
    """Serialized reminder record."""

    id: int
    session_id: str
    routine_id: int | None
    message: str
    scheduled_time: str | None
    is_demo: bool

    model_config = {"from_attributes": True}


class ReminderDemoResponse(BaseModel):
    """Proactive companion reminder used in the hackathon demo."""

    message: str
    routine: RoutineOut | None = None
    audio_url: str | None = None
    reminder: ReminderOut | None = None


class VoiceSpeakRequest(BaseModel):
    """Text-to-speech request body."""

    text: str = Field(..., min_length=1)
    session_id: str | None = None


class VoiceSpeakResponse(BaseModel):
    """Text-to-speech response with a public audio path."""

    audio_url: str
    text: str


class HealthResponse(BaseModel):
    """Liveness payload including which external services are configured."""

    status: str
    services: dict[str, bool]
