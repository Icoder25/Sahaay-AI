"""Firebase authentication orchestration and Supabase login persistence."""

import logging
import uuid
from dataclasses import dataclass
from typing import Any

from app.services.supabase import get_supabase_admin_client

logger = logging.getLogger(__name__)


class AuthenticationStoreError(RuntimeError):
    """Raised when authenticated-user persistence fails."""


class AuthenticationConflict(ValueError):
    """Raised when a verified Firebase identity cannot be linked safely."""


@dataclass(frozen=True)
class LoginMetadata:
    device: str | None
    browser: str | None
    os: str | None
    ip_address: str | None
    user_agent: str | None


def _text(value: Any, limit: int = 1000) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned[:limit] if cleaned else None


def record_authenticated_login(
    claims: dict[str, Any],
    metadata: LoginMetadata,
) -> dict[str, Any]:
    """Atomically upsert a verified Firebase user and record the login."""
    firebase_uid = _text(claims.get("uid"), 128)
    if not firebase_uid:
        raise AuthenticationStoreError("Verified Firebase claims have no uid")

    session_id = str(uuid.uuid4())
    params = {
        "p_firebase_uid": firebase_uid,
        "p_email": _text(claims.get("email"), 320),
        "p_email_verified": claims.get("email_verified") is True,
        "p_name": _text(claims.get("name"), 500),
        "p_photo_url": _text(claims.get("picture"), 2048),
        "p_device": metadata.device,
        "p_browser": metadata.browser,
        "p_os": metadata.os,
        "p_ip_address": metadata.ip_address,
        "p_city": None,
        "p_country": None,
        "p_user_agent": metadata.user_agent,
        "p_session_id": session_id,
    }

    try:
        response = get_supabase_admin_client().rpc(
            "record_firebase_login",
            params,
        ).execute()
    except Exception as exc:
        if getattr(exc, "code", None) == "23505":
            logger.warning("Firebase account link conflict for uid=%s", firebase_uid)
            raise AuthenticationConflict("Firebase account cannot be linked") from exc
        logger.exception("Failed to persist Firebase login for uid=%s", firebase_uid)
        raise AuthenticationStoreError("Could not persist authenticated user") from exc

    if not isinstance(response.data, dict):
        logger.error("Unexpected login RPC response for uid=%s", firebase_uid)
        raise AuthenticationStoreError("Authentication store returned invalid data")

    logger.info("Firebase login recorded for uid=%s", firebase_uid)
    return response.data
