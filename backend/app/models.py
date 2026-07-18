"""ORM mapping for 20260718131000_rebuild_web_schema.sql."""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, Numeric, SmallInteger, String, Table, Text, Time, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, database_url

if database_url.startswith("sqlite"):
    AUTH_USER_FK = "profiles.id"
    PROFILE_AUTH_FK: tuple = ()
else:
    Table(
        "users", Base.metadata,
        Column("id", Uuid(as_uuid=False), primary_key=True),
        schema="auth",
    )
    AUTH_USER_FK = "auth.users.id"
    PROFILE_AUTH_FK = (ForeignKey(AUTH_USER_FK),)
JSON_TYPE = JSONB().with_variant(JSON(), "sqlite")
INET_TYPE = INET().with_variant(String(45), "sqlite")


def uid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), *PROFILE_AUTH_FK, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    account_type: Mapped[str] = mapped_column(Text, default="family")
    preferred_language: Mapped[str] = mapped_column(Text, default="en")
    timezone: Mapped[str] = mapped_column(Text, default="Asia/Kolkata")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Family(Base, TimestampMixin):
    __tablename__ = "families"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK), index=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(Text, default="Asia/Kolkata")


class Invitation(Base, TimestampMixin):
    __tablename__ = "invitations"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    family_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("families.id"), index=True)
    invited_by: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    email: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, default="member")
    token: Mapped[str] = mapped_column(Uuid(as_uuid=False), unique=True, default=uid)
    status: Mapped[str] = mapped_column(Text, default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class FamilyMember(Base, TimestampMixin):
    __tablename__ = "family_members"
    __table_args__ = (UniqueConstraint("family_id", "user_id"),)
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    family_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("families.id"), index=True)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK), index=True)
    invitation_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey("invitations.id"))
    role: Mapped[str] = mapped_column(Text, default="member")
    status: Mapped[str] = mapped_column(Text, default="active")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Elder(Base, TimestampMixin):
    __tablename__ = "elder_profiles"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    family_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("families.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK), unique=True)
    created_by: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK), index=True)
    full_name: Mapped[str] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(Text)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(Text)
    emergency_contact_name: Mapped[str | None] = mapped_column(Text)
    emergency_contact_phone: Mapped[str | None] = mapped_column(Text)
    emergency_contact_relationship: Mapped[str | None] = mapped_column(Text)
    medical_notes: Mapped[str | None] = mapped_column(Text)
    preferred_language: Mapped[str] = mapped_column(Text, default="en")
    timezone: Mapped[str] = mapped_column(Text, default="Asia/Kolkata")
    consent_to_family_monitoring: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Reminder(Base, TimestampMixin):
    __tablename__ = "reminders"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    elder_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("elder_profiles.id"), index=True)
    assigned_by: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    type: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    local_time: Mapped[Any] = mapped_column(Time)
    timezone: Mapped[str] = mapped_column(Text, default="Asia/Kolkata")
    start_date: Mapped[date] = mapped_column(Date, default=date.today)
    end_date: Mapped[date | None] = mapped_column(Date)
    frequency: Mapped[str] = mapped_column(Text, default="daily")
    repeat_rule: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)
    status: Mapped[str] = mapped_column(Text, default="active")
    escalation_after_minutes: Mapped[int] = mapped_column(Integer, default=60)
    max_retries: Mapped[int] = mapped_column(SmallInteger, default=2)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReminderCompletion(Base, TimestampMixin):
    __tablename__ = "reminder_completions"
    __table_args__ = (UniqueConstraint("reminder_id", "scheduled_for"),)
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    reminder_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("reminders.id"), index=True)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(Text, default="completed")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    response_text: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON_TYPE, default=dict)


class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    elder_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("elder_profiles.id"), index=True)
    actor_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    activity_type: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text, default="system")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON_TYPE, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class WellnessEntry(Base, TimestampMixin):
    __tablename__ = "wellness_checks"
    __table_args__ = (UniqueConstraint("elder_id", "check_date"),)
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    elder_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("elder_profiles.id"), index=True)
    recorded_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    check_date: Mapped[date] = mapped_column(Date, default=date.today)
    mood: Mapped[int | None] = mapped_column(SmallInteger)
    mood_label: Mapped[str | None] = mapped_column(Text)
    sleep_quality: Mapped[int | None] = mapped_column(SmallInteger)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    had_breakfast: Mapped[bool | None] = mapped_column(Boolean)
    pain_level: Mapped[int | None] = mapped_column(SmallInteger)
    drank_enough_water: Mapped[bool | None] = mapped_column(Boolean)
    notes: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Conversation(Base, TimestampMixin):
    __tablename__ = "ai_conversations"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    elder_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("elder_profiles.id"), index=True)
    started_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    title: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="active")
    summary: Mapped[str | None] = mapped_column(Text)
    memory: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Message(Base):
    __tablename__ = "ai_messages"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    conversation_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("ai_conversations.id"), index=True)
    sender_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    role: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON_TYPE, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DeviceToken(Base, TimestampMixin):
    __tablename__ = "device_tokens"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK), index=True)
    token: Mapped[str] = mapped_column(Text, unique=True)
    platform: Mapped[str] = mapped_column(Text)
    device_name: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK), index=True)
    elder_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey("elder_profiles.id"))
    type: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    data: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)
    status: Mapped[str] = mapped_column(Text, default="pending")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(Text)


class HealthScore(Base, TimestampMixin):
    __tablename__ = "health_scores"
    __table_args__ = (UniqueConstraint("elder_id", "score_date"),)
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    elder_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("elder_profiles.id"), index=True)
    score: Mapped[int] = mapped_column(SmallInteger)
    score_date: Mapped[date] = mapped_column(Date, default=date.today)
    medicine_score: Mapped[int | None] = mapped_column(SmallInteger)
    meal_score: Mapped[int | None] = mapped_column(SmallInteger)
    sleep_score: Mapped[int | None] = mapped_column(SmallInteger)
    mood_score: Mapped[int | None] = mapped_column(SmallInteger)
    activity_score: Mapped[int | None] = mapped_column(SmallInteger)
    adherence_score: Mapped[int | None] = mapped_column(SmallInteger)
    factors: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict)
    insights: Mapped[list[Any]] = mapped_column(JSON_TYPE, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SOSAlert(Base, TimestampMixin):
    __tablename__ = "sos_alerts"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    elder_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("elder_profiles.id"), index=True)
    triggered_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    status: Mapped[str] = mapped_column(Text, default="active")
    message: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    location_accuracy_meters: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    acknowledged_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON_TYPE, default=dict)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=uid)
    actor_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey(AUTH_USER_FK))
    family_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey("families.id"))
    elder_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), ForeignKey("elder_profiles.id"))
    action: Mapped[str] = mapped_column(Text)
    entity_type: Mapped[str] = mapped_column(Text)
    entity_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False))
    old_values: Mapped[dict[str, Any] | None] = mapped_column(JSON_TYPE)
    new_values: Mapped[dict[str, Any] | None] = mapped_column(JSON_TYPE)
    ip_address: Mapped[str | None] = mapped_column(INET_TYPE)
    user_agent: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
