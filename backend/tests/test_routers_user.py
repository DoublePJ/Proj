from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers import routers_user as user_router


def build_client():
    app = FastAPI()
    app.include_router(user_router.router, prefix="/api")
    return TestClient(app)


def test_create_user_success_and_forwards_auth(monkeypatch):
    captured = {}

    def fake_create_or_update_user(user_id, email=None, display_name=None, avatar_url=None, auth_token=None):
        captured["user_id"] = user_id
        captured["email"] = email
        captured["display_name"] = display_name
        captured["avatar_url"] = avatar_url
        captured["auth_token"] = auth_token
        return {"id": user_id, "display_name": display_name}

    monkeypatch.setattr(user_router, "create_or_update_user", fake_create_or_update_user)
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-1")
    client = build_client()

    response = client.post(
        "/api/users/",
        headers={"Authorization": "Bearer u-create"},
        json={"user_id": "u-1", "email": "u@example.com", "display_name": "User One"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == "u-1"
    assert captured["auth_token"] == "Bearer u-create"


def test_create_user_returns_403_when_body_user_id_mismatches_auth_user(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-actual")
    client = build_client()

    response = client.post(
        "/api/users/",
        headers={"Authorization": "Bearer u-create"},
        json={"user_id": "u-other", "email": "u@example.com", "display_name": "User One"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "user_id does not match authenticated user"


def test_create_user_returns_401_when_missing_token(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: (_ for _ in ()).throw(ValueError("Missing access token")))
    client = build_client()

    response = client.post(
        "/api/users/",
        json={"email": "u@example.com", "display_name": "User One"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing access token"


def test_get_user_success_and_forwards_auth(monkeypatch):
    captured = {}

    def fake_get_user_by_id(user_id, auth_token=None):
        captured["user_id"] = user_id
        captured["auth_token"] = auth_token
        return {"id": user_id, "display_name": "X"}

    monkeypatch.setattr(user_router, "get_user_by_id", fake_get_user_by_id)
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-2")
    client = build_client()

    response = client.get("/api/users/u-2", headers={"Authorization": "Bearer u-get"})

    assert response.status_code == 200
    assert response.json()["id"] == "u-2"
    assert captured == {"user_id": "u-2", "auth_token": "Bearer u-get"}


def test_get_user_returns_404_when_not_found(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "missing")
    monkeypatch.setattr(
        user_router,
        "get_user_by_id",
        lambda user_id, auth_token=None: {"message": "User not found"},
    )
    client = build_client()

    response = client.get("/api/users/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_returns_403_for_other_user(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-owner")
    client = build_client()

    response = client.get("/api/users/u-other", headers={"Authorization": "Bearer u-get"})

    assert response.status_code == 403
    assert response.json()["detail"] == "cannot access another user's profile"


def test_update_user_success(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-3")
    monkeypatch.setattr(
        user_router,
        "update_user_profile",
        lambda user_id, **kwargs: {"id": user_id, "display_name": kwargs.get("display_name")},
    )
    client = build_client()

    response = client.put(
        "/api/users/u-3",
        headers={"Authorization": "Bearer u-update"},
        json={"display_name": "New Name", "job_description": "Developer"},
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "New Name"


def test_update_user_returns_500_when_service_fails(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-4")
    monkeypatch.setattr(
        user_router,
        "update_user_profile",
        lambda user_id, **kwargs: {"message": "update failed"},
    )
    client = build_client()

    response = client.put("/api/users/u-4", headers={"Authorization": "Bearer u-update"}, json={"display_name": "X"})

    assert response.status_code == 500
    assert response.json()["detail"] == "update failed"


def test_update_user_returns_403_for_other_user(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-owner")
    client = build_client()

    response = client.put(
        "/api/users/u-other",
        headers={"Authorization": "Bearer u-update"},
        json={"display_name": "X"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "cannot update another user's profile"


def test_delete_user_success(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-5")
    monkeypatch.setattr(
        user_router,
        "delete_user",
        lambda user_id, auth_token=None: {"message": "User deleted successfully"},
    )
    client = build_client()

    response = client.delete("/api/users/u-5", headers={"Authorization": "Bearer u-delete"})

    assert response.status_code == 200
    assert "deleted" in response.json()["detail"].lower()


def test_delete_user_returns_500_when_service_fails(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-6")
    monkeypatch.setattr(
        user_router,
        "delete_user",
        lambda user_id, auth_token=None: {"message": "cannot delete"},
    )
    client = build_client()

    response = client.delete("/api/users/u-6", headers={"Authorization": "Bearer u-delete"})

    assert response.status_code == 500
    assert response.json()["detail"] == "cannot delete"


def test_delete_user_returns_403_for_other_user(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-owner")
    client = build_client()

    response = client.delete("/api/users/u-other", headers={"Authorization": "Bearer u-delete"})

    assert response.status_code == 403
    assert response.json()["detail"] == "cannot delete another user's profile"


def test_create_user_accepts_missing_body_user_id(monkeypatch):
    monkeypatch.setattr(user_router, "get_authenticated_user_id", lambda auth: "u-7")
    monkeypatch.setattr(
        user_router,
        "create_or_update_user",
        lambda user_id, **kwargs: {"id": user_id, "display_name": kwargs.get("display_name")},
    )
    client = build_client()

    response = client.post(
        "/api/users/",
        headers={"Authorization": "Bearer u-create"},
        json={"display_name": "Missing user_id"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == "u-7"


def test_get_jobs_and_job_types_success(monkeypatch):
    monkeypatch.setattr(user_router, "get_all_jobs", lambda: [{"id": 1, "description": "Dev"}])
    monkeypatch.setattr(user_router, "get_all_job_types", lambda: [{"id": 2, "description": "Full-time"}])
    client = build_client()

    jobs_response = client.get("/api/users/options/jobs")
    job_types_response = client.get("/api/users/options/job-types")

    assert jobs_response.status_code == 200
    assert job_types_response.status_code == 200
    assert jobs_response.json()[0]["description"] == "Dev"
    assert job_types_response.json()[0]["description"] == "Full-time"
