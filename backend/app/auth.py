"""Firebase bearer-token verification and authenticated profile dependency."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Profile, User
from app.services.firebase import (
    FirebaseConfigurationError,
    InvalidFirebaseToken,
    verify_firebase_id_token,
)

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str | None = None
    firebase_uid: str | None = None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> AuthUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = verify_firebase_id_token(credentials.credentials)
        firebase_uid = str(claims["uid"])
        user = db.query(User).filter_by(firebase_uid=firebase_uid).first()
    except InvalidFirebaseToken as exc:
        raise HTTPException(401, str(exc), headers={"WWW-Authenticate": "Bearer"}) from exc
    except (FirebaseConfigurationError, SQLAlchemyError) as exc:
        raise HTTPException(500, "Authentication service unavailable") from exc

    if user is None:
        raise HTTPException(401, "Firebase user has not completed backend authentication")
    if user.status != "active":
        raise HTTPException(401, "User account is not active")
    return AuthUser(
        id=str(user.id),
        email=user.email,
        firebase_uid=firebase_uid,
    )


def get_current_profile(
    user: AuthUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> Profile:
    profile = db.get(Profile, user.id)
    if profile is None:
        default_name = (user.email or "Sahaay User").split("@", 1)[0].strip() or "Sahaay User"
        if db.get(User, user.id) is None:
            db.add(User(
                id=user.id,
                firebase_uid=user.firebase_uid or f"test:{user.id}",
                email=user.email,
                name=default_name[:150],
            ))
        profile = Profile(id=user.id, email=user.email, full_name=default_name[:150])
        db.add(profile)
        db.commit()
        db.refresh(profile)
    elif user.email and profile.email != user.email:
        profile.email = user.email
        db.commit()
    return profile
