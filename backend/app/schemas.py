"""Request/response contracts for API v1."""

from datetime import date, datetime, time
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class Citation(BaseModel):
    title: str
    url: str
    snippet: str | None = None


class FirebaseAuthRequest(BaseModel):
    id_token: str = Field(min_length=1)


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=150)
    phone: str | None = None
    avatar_url: str | None = None
    account_type: Literal["family", "elder", "both"] | None = None
    preferred_language: Literal["en", "hi", "gu"] | None = None
    timezone: str | None = Field(None, max_length=64)


class FamilyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    timezone: str = "Asia/Kolkata"


class FamilyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = None
    timezone: str | None = None


class InvitationCreate(BaseModel):
    email: EmailStr
    role: Literal["admin", "caregiver", "member"] = "member"


class InvitationAccept(BaseModel):
    token: str


class ReminderSnooze(BaseModel):
    scheduled_for: datetime
    minutes: int = Field(ge=5, le=1440)


class MemberRoleUpdate(BaseModel):
    role: Literal["admin", "caregiver", "member"]


class ElderCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    user_id: str | None = None
    photo_url: str | None = None
    date_of_birth: date | None = None
    gender: Literal["female", "male", "non_binary", "other", "prefer_not_to_say"] | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    emergency_contact_relationship: str | None = None
    medical_notes: str | None = None
    preferred_language: Literal["en", "hi", "gu"] = "en"
    timezone: str = "Asia/Kolkata"
    consent_to_family_monitoring: bool = True


class ElderUpdate(BaseModel):
    full_name: str | None = None
    photo_url: str | None = None
    date_of_birth: date | None = None
    gender: Literal["female", "male", "non_binary", "other", "prefer_not_to_say"] | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    emergency_contact_relationship: str | None = None
    medical_notes: str | None = None
    preferred_language: Literal["en", "hi", "gu"] | None = None
    timezone: str | None = None
    consent_to_family_monitoring: bool | None = None
    is_active: bool | None = None


class ReminderCreate(BaseModel):
    type: Literal["medicine", "meal", "sleep", "appointment", "exercise", "hydration", "other"]
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    note: str | None = None
    local_time: time
    timezone: str = "Asia/Kolkata"
    start_date: date = Field(default_factory=date.today)
    end_date: date | None = None
    frequency: Literal["once", "daily", "weekly", "monthly", "custom"] = "daily"
    repeat_rule: dict[str, Any] = Field(default_factory=dict)
    escalation_after_minutes: int = Field(60, ge=0, le=10080)
    max_retries: int = Field(2, ge=0, le=20)
    next_run_at: datetime | None = None


class ReminderUpdate(BaseModel):
    type: Literal["medicine", "meal", "sleep", "appointment", "exercise", "hydration", "other"] | None = None
    title: str | None = None
    description: str | None = None
    note: str | None = None
    local_time: time | None = None
    timezone: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    frequency: Literal["once", "daily", "weekly", "monthly", "custom"] | None = None
    repeat_rule: dict[str, Any] | None = None
    status: Literal["active", "paused", "completed", "archived"] | None = None
    escalation_after_minutes: int | None = Field(None, ge=0, le=10080)
    max_retries: int | None = Field(None, ge=0, le=20)
    next_run_at: datetime | None = None


class ReminderCompletionCreate(BaseModel):
    status: Literal["completed", "skipped"] = "completed"
    response_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WellnessCreate(BaseModel):
    check_date: date = Field(default_factory=date.today)
    mood: int | None = Field(None, ge=1, le=5)
    mood_label: str | None = None
    sleep_quality: int | None = Field(None, ge=1, le=5)
    sleep_hours: float | None = Field(None, ge=0, le=24)
    had_breakfast: bool | None = None
    pain_level: int | None = Field(None, ge=0, le=10)
    drank_enough_water: bool | None = None
    notes: str | None = None


class ConversationCreate(BaseModel):
    elder_id: str
    title: str = "New conversation"


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    use_search: bool = True
    speak: bool = False


class DeviceTokenCreate(BaseModel):
    token: str = Field(min_length=21)
    platform: Literal["android", "ios", "web"] = "web"
    device_name: str | None = None


class NotificationCreate(BaseModel):
    user_id: str
    elder_id: str | None = None
    type: Literal["reminder", "family_alert", "sos", "appointment", "daily_summary", "emergency", "wellness"] = "family_alert"
    title: str
    body: str
    data: dict[str, Any] = Field(default_factory=dict)


class SOSCreate(BaseModel):
    message: str = "Emergency assistance requested"
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    location_accuracy_meters: float | None = Field(None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    database: str
    services: dict[str, bool]
