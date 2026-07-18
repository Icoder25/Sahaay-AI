import os

os.environ["DATABASE_URL"] = "sqlite:///./test_sahaay.db"
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_PUBLISHABLE_KEY"] = ""
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["FIREBASE_CREDENTIALS_JSON"] = ""

import pytest
from fastapi.testclient import TestClient

from app.auth import AuthUser, get_current_user
from app.db import Base, engine
from app.main import app

identity = {"id": "11111111-1111-1111-1111-111111111111", "email": "owner@example.com"}


def fake_user() -> AuthUser:
    return AuthUser(**identity)


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    identity.update(id="11111111-1111-1111-1111-111111111111", email="owner@example.com")
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = fake_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def as_user():
    def switch(user_id: str, email: str | None):
        identity.update(id=user_id, email=email)
    return switch
