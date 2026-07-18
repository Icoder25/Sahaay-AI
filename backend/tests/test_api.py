from datetime import datetime, timedelta

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app import auth as auth_module
from app.auth import get_current_user
from app.db import SessionLocal
from app.main import app
from app.models import User
from app.routers import api_v1
from app.services import authentication as authentication_service
from app.services import firebase as firebase_service
from app.services.authentication import (
    AuthenticationConflict,
    LoginMetadata,
    record_authenticated_login,
)
from app.services.firebase import InvalidFirebaseToken, verify_firebase_id_token

PREFIX = "/api/v1"


def create_family_elder(client):
    family = client.post(f"{PREFIX}/families", json={"name": "Rathi Family"}).json()
    elder = client.post(
        f"{PREFIX}/families/{family['id']}/elders",
        json={
            "full_name": "Rajesh",
            "emergency_contact_phone": "+910000000000",
            "preferred_language": "en",
        },
    ).json()
    return family, elder


def test_health_and_auth_required(client):
    assert client.get("/health").status_code == 200
    app.dependency_overrides.clear()
    response = client.get(f"{PREFIX}/families")
    assert response.status_code == 401


def test_current_user_resolves_verified_firebase_identity(monkeypatch):
    db = SessionLocal()
    try:
        user = User(
            id="11111111-1111-1111-1111-111111111111",
            firebase_uid="firebase-user-1",
            email="owner@example.com",
            status="active",
        )
        db.add(user)
        db.commit()
        monkeypatch.setattr(
            auth_module,
            "verify_firebase_id_token",
            lambda _token: {
                "uid": "firebase-user-1",
                "email": "owner@example.com",
                "email_verified": True,
            },
        )
        authenticated = get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="firebase-token"),
            db,
        )
        assert authenticated.id == user.id
        assert authenticated.firebase_uid == "firebase-user-1"
    finally:
        db.close()


def test_profile_creation_uses_non_empty_display_name(client, as_user):
    assert client.get(f"{PREFIX}/profiles/me").json()["full_name"] == "owner"
    as_user("33333333-3333-3333-3333-333333333333", None)
    assert client.get(f"{PREFIX}/profiles/me").json()["full_name"] == "Sahaay User"


def test_firebase_authentication(client, monkeypatch):
    captured = {}

    monkeypatch.setattr(
        api_v1,
        "verify_firebase_id_token",
        lambda token: {
            "uid": "firebase-user-1",
            "email": "owner@example.com",
            "email_verified": True,
            "name": "Owner",
            "picture": "https://example.com/photo.jpg",
        },
    )

    def fake_record(claims, metadata):
        captured.update(claims=claims, metadata=metadata)
        return {
            "id": "11111111-1111-1111-1111-111111111111",
            "firebase_uid": claims["uid"],
            "email": claims["email"],
            "session_id": "session-1",
        }

    monkeypatch.setattr(api_v1, "record_authenticated_login", fake_record)
    response = client.post(
        f"{PREFIX}/auth/firebase",
        json={"id_token": "verified-firebase-token"},
        headers={
            "user-agent": "Test Browser",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        },
    )
    assert response.status_code == 200
    assert response.json()["user"]["firebase_uid"] == "firebase-user-1"
    assert response.json()["session"]["id"] == "session-1"
    assert captured["metadata"].device == "desktop"
    assert captured["metadata"].os == "Windows"


def test_firebase_authentication_rejects_invalid_token(client, monkeypatch):
    def reject(_token):
        raise InvalidFirebaseToken("Invalid or expired Firebase ID token")

    monkeypatch.setattr(api_v1, "verify_firebase_id_token", reject)
    response = client.post(
        f"{PREFIX}/auth/firebase",
        json={"id_token": "invalid-token"},
    )
    assert response.status_code == 401


def test_firebase_authentication_rejects_bad_request(client):
    response = client.post(f"{PREFIX}/auth/firebase", json={"id_token": ""})
    assert response.status_code == 400


def test_firebase_authentication_rejects_account_conflict(client, monkeypatch):
    monkeypatch.setattr(
        api_v1,
        "verify_firebase_id_token",
        lambda _token: {
            "uid": "firebase-user-1",
            "email": "owner@example.com",
            "email_verified": True,
        },
    )

    def reject_link(_claims, _metadata):
        raise AuthenticationConflict("Firebase account cannot be linked")

    monkeypatch.setattr(api_v1, "record_authenticated_login", reject_link)
    response = client.post(
        f"{PREFIX}/auth/firebase",
        json={"id_token": "verified-firebase-token"},
    )
    assert response.status_code == 400


def test_firebase_authentication_rejects_unverified_email(monkeypatch):
    monkeypatch.setattr(firebase_service, "get_firebase_app", lambda: object())
    monkeypatch.setattr(
        firebase_service.auth,
        "verify_id_token",
        lambda *_args, **_kwargs: {
            "uid": "firebase-user-1",
            "email": "owner@example.com",
            "email_verified": False,
        },
    )
    with pytest.raises(InvalidFirebaseToken, match="email is not verified"):
        verify_firebase_id_token("firebase-token")


def test_login_persistence_passes_verified_email_to_rpc(monkeypatch):
    captured = {}

    class RpcCall:
        def execute(self):
            return type("Response", (), {"data": {"id": "user-1", "session_id": "session-1"}})()

    class Client:
        def rpc(self, name, params):
            captured.update(name=name, params=params)
            return RpcCall()

    monkeypatch.setattr(
        authentication_service,
        "get_supabase_admin_client",
        lambda: Client(),
    )
    result = record_authenticated_login(
        {
            "uid": "firebase-user-1",
            "email": "owner@example.com",
            "email_verified": True,
        },
        LoginMetadata(None, None, None, None, None),
    )
    assert result["id"] == "user-1"
    assert captured["name"] == "record_firebase_login"
    assert captured["params"]["p_email_verified"] is True


def test_profile_family_and_elder_crud(client):
    profile = client.patch(f"{PREFIX}/profiles/me", json={"full_name": "Atharva"}).json()
    assert profile["full_name"] == "Atharva"
    family, elder = create_family_elder(client)
    assert client.get(f"{PREFIX}/families/{family['id']}").status_code == 200
    assert client.get(f"{PREFIX}/elders/{elder['id']}").json()["full_name"] == "Rajesh"
    updated = client.patch(f"{PREFIX}/elders/{elder['id']}", json={"medical_notes": "Diabetes"}).json()
    assert updated["medical_notes"] == "Diabetes"
    assert client.delete(f"{PREFIX}/elders/{elder['id']}").status_code == 204
    assert client.delete(f"{PREFIX}/families/{family['id']}").status_code == 204


def test_invitation_and_rbac(client, as_user):
    family = client.post(f"{PREFIX}/families", json={"name": "Care Circle"}).json()
    invitation = client.post(
        f"{PREFIX}/families/{family['id']}/invitations",
        json={"email": "viewer@example.com", "role": "member"},
    ).json()
    as_user("22222222-2222-2222-2222-222222222222", "viewer@example.com")
    accepted = client.post(f"{PREFIX}/invitations/accept", json={"token": invitation["token"]})
    assert accepted.status_code == 200
    assert accepted.json()["invitation_id"] == invitation["id"]
    denied = client.post(
        f"{PREFIX}/families/{family['id']}/invitations",
        json={"email": "other@example.com", "role": "member"},
    )
    assert denied.status_code == 403
    assert client.post(
        f"{PREFIX}/families/{family['id']}/elders", json={"full_name": "Read only"}
    ).status_code == 403


def test_reminder_completion_calendar_and_score(client):
    _, elder = create_family_elder(client)
    scheduled = datetime.now() + timedelta(hours=1)
    reminder = client.post(
        f"{PREFIX}/elders/{elder['id']}/reminders",
        json={
            "title": "BP medicine",
            "type": "medicine",
            "local_time": scheduled.time().isoformat(),
            "start_date": scheduled.date().isoformat(),
            "frequency": "daily",
            "next_run_at": scheduled.isoformat(),
        },
    ).json()
    completion = client.post(f"{PREFIX}/reminders/{reminder['id']}/complete").json()
    assert completion["completion"]["status"] == "completed"
    assert completion["reminder"]["status"] == "active"
    assert completion["reminder"]["next_run_at"] != reminder["next_run_at"]
    month = datetime.now().date().isoformat()
    calendar = client.get(f"{PREFIX}/elders/{elder['id']}/calendar", params={"month": month})
    assert calendar.status_code == 200
    score = client.get(f"{PREFIX}/elders/{elder['id']}/health-score").json()
    assert 0 <= score["score"] <= 100
    assert score["factors"]["method"] == "weighted_average_of_available_components"
    assert "missing_data" in score["factors"]


def test_wellness_activity_dashboard_and_sos(client):
    family, elder = create_family_elder(client)
    assert client.post(
        f"{PREFIX}/elders/{elder['id']}/wellness",
        json={"mood": 4, "sleep_hours": 7.5, "drank_enough_water": True},
    ).status_code == 201
    alert = client.post(
        f"{PREFIX}/elders/{elder['id']}/sos",
        json={"message": "Need help", "latitude": 18.52, "longitude": 73.85},
    ).json()
    assert client.post(f"{PREFIX}/sos/{alert['id']}/acknowledge").json()["status"] == "acknowledged"
    assert client.post(f"{PREFIX}/sos/{alert['id']}/resolve").json()["status"] == "resolved"
    assert client.get(f"{PREFIX}/elders/{elder['id']}/activities").json()
    dashboard = client.get(f"{PREFIX}/families/{family['id']}/dashboard")
    assert dashboard.status_code == 200
    analytics = client.get(f"{PREFIX}/families/{family['id']}/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["adherence_percent"] == 100.0


def test_integrations_disabled_safely(client):
    _, elder = create_family_elder(client)
    conversation = client.post(
        f"{PREFIX}/conversations", json={"elder_id": elder["id"], "title": "Check in"}
    ).json()
    response = client.post(
        f"{PREFIX}/conversations/{conversation['id']}/messages",
        json={"content": "How are you?", "speak": False},
    )
    assert response.status_code == 503
    assert "disabled" in response.json()["detail"]
    token = client.post(
        f"{PREFIX}/devices", json={"token": "test-device-token-long", "platform": "web"}
    )
    assert token.status_code == 201


def test_linked_elder_self_service_and_isolation(client, as_user):
    family = client.post(f"{PREFIX}/families", json={"name": "Self Service"}).json()
    elder_user_id = "44444444-4444-4444-4444-444444444444"
    other_user_id = "55555555-5555-5555-5555-555555555555"
    elder = client.post(
        f"{PREFIX}/families/{family['id']}/elders",
        json={"full_name": "Linked Elder", "user_id": elder_user_id},
    ).json()
    other = client.post(
        f"{PREFIX}/families/{family['id']}/elders",
        json={"full_name": "Other Elder", "user_id": other_user_id},
    ).json()
    due = datetime.now() + timedelta(hours=1)
    reminder = client.post(
        f"{PREFIX}/elders/{elder['id']}/reminders",
        json={
            "type": "medicine",
            "title": "Self-service medicine",
            "local_time": due.time().isoformat(),
            "start_date": due.date().isoformat(),
            "frequency": "daily",
            "next_run_at": due.isoformat(),
        },
    ).json()

    as_user(elder_user_id, "elder@example.com")
    assert client.get(f"{PREFIX}/elders/me").json()["id"] == elder["id"]
    assert client.get(f"{PREFIX}/elders/{elder['id']}").status_code == 200
    assert client.get(f"{PREFIX}/elders/{other['id']}").status_code == 403
    assert client.get(f"{PREFIX}/elders/{elder['id']}/reminders").status_code == 200
    assert client.post(f"{PREFIX}/reminders/{reminder['id']}/complete").status_code == 200
    assert client.post(
        f"{PREFIX}/elders/{elder['id']}/wellness", json={"mood": 4}
    ).status_code == 201
    assert client.post(
        f"{PREFIX}/conversations", json={"elder_id": elder["id"], "title": "My chat"}
    ).status_code == 201
    assert client.post(
        f"{PREFIX}/elders/{elder['id']}/sos", json={"message": "Please help"}
    ).status_code == 201

    assert client.patch(
        f"{PREFIX}/elders/{elder['id']}", json={"full_name": "Forbidden edit"}
    ).status_code == 403
    assert client.post(
        f"{PREFIX}/elders/{elder['id']}/reminders",
        json={
            "type": "other",
            "title": "Forbidden reminder",
            "local_time": "09:00:00",
        },
    ).status_code == 403
    assert client.delete(f"{PREFIX}/reminders/{reminder['id']}").status_code == 403
    assert client.post(
        f"{PREFIX}/elders/{other['id']}/sos", json={"message": "Not my profile"}
    ).status_code == 403
