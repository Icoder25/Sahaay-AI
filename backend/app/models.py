"""ORM models for sessions, users, families, and care data."""

import secrets
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _invite_code() -> str:
    return secrets.token_urlsafe(6).upper()[:8]


class User(Base):
    """Registered account (family member or elder)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(30), default="family_member")
    locale: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    family_memberships: Mapped[list["FamilyMember"]] = relationship(back_populates="user")
    elder_profile: Mapped["ElderProfile | None"] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    device_tokens: Mapped[list["DeviceToken"]] = relationship(back_populates="user")


class Family(Base):
    """A family group caring for one or more elders."""

    __tablename__ = "families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    invite_code: Mapped[str] = mapped_column(String(12), unique=True, default=_invite_code)
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    members: Mapped[list["FamilyMember"]] = relationship(back_populates="family")
    elder_profiles: Mapped[list["ElderProfile"]] = relationship(back_populates="family")


class FamilyMember(Base):
    """Links a user to a family with a role."""

    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("families.id"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(30), default="member")
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    family: Mapped["Family"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="family_memberships")


class ElderProfile(Base):
    """An elderly person being cared for within a family."""

    __tablename__ = "elder_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("families.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    display_name: Mapped[str] = mapped_column(String(120))
    session_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    emergency_contact: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    family: Mapped["Family"] = relationship(back_populates="elder_profiles")
    user: Mapped["User | None"] = relationship(back_populates="elder_profile")
    activities: Mapped[list["Activity"]] = relationship(back_populates="elder_profile")
    wellness_checks: Mapped[list["WellnessCheck"]] = relationship(back_populates="elder_profile")
    health_scores: Mapped[list["HealthScore"]] = relationship(back_populates="elder_profile")


class ChatSession(Base):
    """A chat session keyed by client-provided or profile UUID."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    messages: Mapped[list["Message"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    routines: Mapped[list["Routine"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """A single user or assistant message within a session."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")


class Routine(Base):
    """A structured routine extracted from conversation."""

    __tablename__ = "routines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(50), default="habit")
    timing: Mapped[str | None] = mapped_column(String(50), nullable=True)
    frequency: Mapped[str] = mapped_column(String(50), default="daily")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    session: Mapped["ChatSession"] = relationship(back_populates="routines")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="routine")


class Reminder(Base):
    """A reminder linked to a session and optional routine."""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), index=True)
    elder_profile_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("elder_profiles.id"), nullable=True, index=True
    )
    routine_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("routines.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    scheduled_time: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="reminders")
    routine: Mapped["Routine | None"] = relationship(back_populates="reminders")
    elder_profile: Mapped["ElderProfile | None"] = relationship()


class Activity(Base):
    """Timeline event for family dashboard."""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elder_profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("elder_profiles.id"), index=True)
    activity_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    elder_profile: Mapped["ElderProfile"] = relationship(back_populates="activities")


class WellnessCheck(Base):
    """Daily wellness response from elder."""

    __tablename__ = "wellness_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elder_profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("elder_profiles.id"), index=True)
    mood: Mapped[str] = mapped_column(String(30))
    appetite: Mapped[str] = mapped_column(String(30))
    sleep_quality: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    elder_profile: Mapped["ElderProfile"] = relationship(back_populates="wellness_checks")


class HealthScore(Base):
    """Computed wellness score for an elder."""

    __tablename__ = "health_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    elder_profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("elder_profiles.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    summary: Mapped[str] = mapped_column(Text)
    factors: Mapped[str | None] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    elder_profile: Mapped["ElderProfile"] = relationship(back_populates="health_scores")


class Notification(Base):
    """In-app and push notification record."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    elder_profile_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("elder_profiles.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    notification_type: Mapped[str] = mapped_column(String(50), default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_via_fcm: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="notifications")


class DeviceToken(Base):
    """FCM device token for push notifications."""

    __tablename__ = "device_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(512), unique=True)
    platform: Mapped[str] = mapped_column(String(30), default="web")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="device_tokens")


def new_session_id() -> str:
    return str(uuid.uuid4())
