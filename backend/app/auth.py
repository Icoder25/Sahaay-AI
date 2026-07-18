"""Supabase bearer-token verification and authenticated profile dependency."""

from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import Profile

bearer = HTTPBearer(auto_error=False)
_jwks_clients: dict[str, PyJWKClient] = {}


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str | None = None


def _jwks_client(issuer: str) -> PyJWKClient:
    client = _jwks_clients.get(issuer)
    if client is None:
        client = PyJWKClient(f"{issuer}/.well-known/jwks.json", cache_keys=True)
        _jwks_clients[issuer] = client
    return client


def _decode(token: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.supabase_url:
        raise HTTPException(503, "Supabase authentication is not configured")
    issuer = settings.supabase_url.rstrip("/") + "/auth/v1"
    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg", "RS256")
        key = _jwks_client(issuer).get_signing_key_from_jwt(token).key
        # leeway absorbs clock skew vs Supabase (iat/nbf/exp).
        # verify_iat=False avoids ImmatureSignatureError when Supabase clocks
        # are slightly ahead of the API host.
        return jwt.decode(
            token,
            key,
            algorithms=[algorithm],
            audience=settings.supabase_jwt_audience,
            issuer=issuer,
            leeway=300,
            options={"verify_iat": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(401, "Invalid or expired access token") from exc
    except Exception as exc:
        raise HTTPException(503, "Authentication key service unavailable") from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> AuthUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    claims = _decode(credentials.credentials)
    subject = claims.get("sub")
    if not subject:
        raise HTTPException(401, "Token has no subject")
    return AuthUser(id=str(subject), email=claims.get("email"))


def get_current_profile(
    user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> Profile:
    profile = db.get(Profile, user.id)
    if profile is None:
        default_name = (user.email or "Sahaay User").split("@", 1)[0].strip() or "Sahaay User"
        profile = Profile(id=user.id, email=user.email, full_name=default_name[:150])
        db.add(profile)
        db.commit()
        db.refresh(profile)
    elif user.email and profile.email != user.email:
        profile.email = user.email
        db.commit()
    return profile
