"""Firebase Admin initialization and ID-token verification."""

import json
import logging
from functools import lru_cache
from threading import Lock
from typing import Any

import firebase_admin
from firebase_admin import auth, credentials

from app.config import get_settings

logger = logging.getLogger(__name__)
_firebase_init_lock = Lock()


class FirebaseConfigurationError(RuntimeError):
    """Raised when Firebase Admin credentials are unavailable or invalid."""


class InvalidFirebaseToken(ValueError):
    """Raised when a Firebase ID token cannot authenticate a user."""


@lru_cache(maxsize=1)
def get_firebase_app() -> firebase_admin.App:
    """Return the process-wide Firebase Admin app."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    with _firebase_init_lock:
        try:
            return firebase_admin.get_app()
        except ValueError:
            pass

        settings = get_settings()
        options = {"projectId": settings.firebase_project_id} if settings.firebase_project_id else None

        try:
            if settings.firebase_credentials_json:
                credential_data = json.loads(settings.firebase_credentials_json)
                credential = credentials.Certificate(credential_data)
            else:
                credential = credentials.ApplicationDefault()
            return firebase_admin.initialize_app(credential, options)
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            logger.exception("Firebase Admin initialization failed")
            raise FirebaseConfigurationError(
                "Firebase Admin is not configured correctly"
            ) from exc


def verify_firebase_id_token(id_token: str) -> dict[str, Any]:
    """Verify a Firebase ID token and return trusted claims."""
    if not id_token or not id_token.strip():
        raise InvalidFirebaseToken("Firebase ID token is required")

    try:
        decoded = auth.verify_id_token(
            id_token,
            app=get_firebase_app(),
            check_revoked=True,
        )
    except (
        auth.ExpiredIdTokenError,
        auth.InvalidIdTokenError,
        auth.RevokedIdTokenError,
        auth.UserDisabledError,
        ValueError,
    ) as exc:
        logger.warning("Firebase ID token verification failed: %s", type(exc).__name__)
        raise InvalidFirebaseToken("Invalid or expired Firebase ID token") from exc
    except FirebaseConfigurationError:
        raise
    except Exception as exc:
        logger.exception("Unexpected Firebase token verification failure")
        raise FirebaseConfigurationError("Firebase token verification is unavailable") from exc

    if not decoded.get("uid"):
        raise InvalidFirebaseToken("Firebase ID token has no uid")
    if decoded.get("email") and decoded.get("email_verified") is not True:
        raise InvalidFirebaseToken("Firebase email is not verified")
    return decoded
