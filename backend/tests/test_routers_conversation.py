from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers import routers_conversation as conversation_router


def build_client():
    app = FastAPI()
    app.include_router(conversation_router.router, prefix="/api")
    return TestClient(app)


def test_add_message_endpoint_success_and_forwards_token(monkeypatch):
    captured = {}

    def fake_add_message(room_id, sender, message, metadata, auth_token):
        captured["room_id"] = room_id
        captured["sender"] = sender
        captured["message"] = message
        captured["metadata"] = metadata
        captured["auth_token"] = auth_token
        return {"id": 501, "room_id": room_id, "sender": sender, "message": message}

    monkeypatch.setattr(conversation_router, "add_message", fake_add_message)
    client = build_client()

    response = client.post(
        "/api/conversations/rooms/12/messages",
        headers={"Authorization": "Bearer token-123"},
        json={"sender": "user", "message": "hello", "metadata": {"source": "web"}},
    )

    assert response.status_code == 200
    assert response.json()["id"] == 501
    assert captured["room_id"] == 12
    assert captured["auth_token"] == "Bearer token-123"


def test_get_room_returns_404_when_not_found(monkeypatch):
    monkeypatch.setattr(
        conversation_router,
        "get_chat_room_by_id",
        lambda room_id, auth_token=None: {"message": "Chat room not found"},
    )
    client = build_client()

    response = client.get("/api/conversations/rooms/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat room not found"


def test_get_room_messages_success(monkeypatch):
    monkeypatch.setattr(
        conversation_router,
        "get_messages",
        lambda room_id, limit=100, auth_token=None: [
            {"id": 1, "room_id": room_id, "sender": "user", "message": "A"},
            {"id": 2, "room_id": room_id, "sender": "bot", "message": "B"},
        ],
    )
    client = build_client()

    response = client.get("/api/conversations/rooms/13/messages?limit=2")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["sender"] == "user"


def test_add_message_endpoint_returns_500_when_service_fails(monkeypatch):
    monkeypatch.setattr(
        conversation_router,
        "add_message",
        lambda room_id, sender, message, metadata, auth_token: {"message": "db failed"},
    )
    client = build_client()

    response = client.post(
        "/api/conversations/rooms/12/messages",
        headers={"Authorization": "Bearer token-123"},
        json={"sender": "user", "message": "hello"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "db failed"


def test_get_room_messages_returns_500_when_service_fails(monkeypatch):
    monkeypatch.setattr(
        conversation_router,
        "get_messages",
        lambda room_id, limit=100, auth_token=None: {"message": "query failed"},
    )
    client = build_client()

    response = client.get("/api/conversations/rooms/13/messages?limit=2")

    assert response.status_code == 500
    assert response.json()["detail"] == "query failed"


def test_get_room_messages_forwards_limit_and_auth_token(monkeypatch):
    captured = {}

    def fake_get_messages(room_id, limit=100, auth_token=None):
        captured["room_id"] = room_id
        captured["limit"] = limit
        captured["auth_token"] = auth_token
        return []

    monkeypatch.setattr(conversation_router, "get_messages", fake_get_messages)
    client = build_client()

    response = client.get(
        "/api/conversations/rooms/55/messages?limit=5",
        headers={"Authorization": "Bearer abc"},
    )

    assert response.status_code == 200
    assert captured == {"room_id": 55, "limit": 5, "auth_token": "Bearer abc"}


def test_add_message_validation_fails_when_required_field_missing():
    client = build_client()

    response = client.post(
        "/api/conversations/rooms/12/messages",
        json={"sender": "user"},
    )

    assert response.status_code == 422


def test_create_room_success_and_forwards_auth(monkeypatch):
    captured = {}

    def fake_create_chat_room(user_id=None, title="การสนทนาใหม่", auth_token=None):
        captured["user_id"] = user_id
        captured["title"] = title
        captured["auth_token"] = auth_token
        return {"id": 7, "user_id": user_id, "title": title}

    monkeypatch.setattr(conversation_router, "create_chat_room", fake_create_chat_room)
    monkeypatch.setattr(conversation_router, "get_authenticated_user_id", lambda auth: "u-100")
    client = build_client()

    response = client.post(
        "/api/conversations/rooms",
        headers={"Authorization": "Bearer t-room"},
        json={"user_id": "u-100", "title": "ห้องหลัก"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == 7
    assert captured == {"user_id": "u-100", "title": "ห้องหลัก", "auth_token": "Bearer t-room"}


def test_create_room_returns_403_when_body_user_id_mismatches_auth_user(monkeypatch):
    monkeypatch.setattr(conversation_router, "get_authenticated_user_id", lambda auth: "u-owner")
    client = build_client()

    response = client.post(
        "/api/conversations/rooms",
        headers={"Authorization": "Bearer t-room"},
        json={"user_id": "u-other", "title": "ห้องหลัก"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "user_id does not match authenticated user"


def test_create_room_returns_500_when_service_fails(monkeypatch):
    monkeypatch.setattr(conversation_router, "get_authenticated_user_id", lambda auth: "u-1")
    monkeypatch.setattr(
        conversation_router,
        "create_chat_room",
        lambda user_id=None, title="การสนทนาใหม่", auth_token=None: {"message": "insert failed"},
    )
    client = build_client()

    response = client.post("/api/conversations/rooms", headers={"Authorization": "Bearer t-room"}, json={"title": "A"})

    assert response.status_code == 500
    assert response.json()["detail"] == "insert failed"


def test_create_room_returns_401_when_missing_token(monkeypatch):
    monkeypatch.setattr(conversation_router, "get_authenticated_user_id", lambda auth: (_ for _ in ()).throw(ValueError("Missing access token")))
    client = build_client()

    response = client.post("/api/conversations/rooms", json={"title": "A"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing access token"


def test_get_rooms_success_and_forwards_filters(monkeypatch):
    captured = {}

    def fake_get_chat_rooms(user_id=None, include_archived=False, auth_token=None):
        captured["user_id"] = user_id
        captured["include_archived"] = include_archived
        captured["auth_token"] = auth_token
        return [{"id": 1}, {"id": 2}]

    monkeypatch.setattr(conversation_router, "get_chat_rooms", fake_get_chat_rooms)
    monkeypatch.setattr(conversation_router, "get_authenticated_user_id", lambda auth: "u-1")
    client = build_client()

    response = client.get(
        "/api/conversations/rooms?user_id=u-1&include_archived=true",
        headers={"Authorization": "Bearer t-list"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert captured == {
        "user_id": "u-1",
        "include_archived": True,
        "auth_token": "Bearer t-list",
    }


def test_get_rooms_returns_403_for_other_user_filter(monkeypatch):
    monkeypatch.setattr(conversation_router, "get_authenticated_user_id", lambda auth: "u-owner")
    client = build_client()

    response = client.get(
        "/api/conversations/rooms?user_id=u-other&include_archived=false",
        headers={"Authorization": "Bearer t-list"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "cannot access another user's rooms"


def test_update_room_success(monkeypatch):
    monkeypatch.setattr(
        conversation_router,
        "update_chat_room",
        lambda room_id, title=None, is_archive=None, auth_token=None: {
            "id": room_id,
            "title": title,
            "is_archive": is_archive,
        },
    )
    client = build_client()

    response = client.put(
        "/api/conversations/rooms/5",
        headers={"Authorization": "Bearer t-update"},
        json={"title": "เปลี่ยนชื่อ", "is_archive": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 5
    assert payload["is_archive"] is True


def test_update_room_returns_500_when_service_fails(monkeypatch):
    monkeypatch.setattr(
        conversation_router,
        "update_chat_room",
        lambda room_id, title=None, is_archive=None, auth_token=None: {"message": "update failed"},
    )
    client = build_client()

    response = client.put("/api/conversations/rooms/5", json={"title": "X"})

    assert response.status_code == 500
    assert response.json()["detail"] == "update failed"


def test_delete_room_success(monkeypatch):
    monkeypatch.setattr(
        conversation_router,
        "delete_chat_room",
        lambda room_id, auth_token=None: {"message": "Chat room deleted successfully"},
    )
    client = build_client()

    response = client.delete("/api/conversations/rooms/5")

    assert response.status_code == 200
    assert "deleted" in response.json()["detail"].lower()


def test_delete_rooms_by_user_success(monkeypatch):
    monkeypatch.setattr(conversation_router, "get_authenticated_user_id", lambda auth: "u-10")
    monkeypatch.setattr(
        conversation_router,
        "delete_chat_rooms_by_user",
        lambda user_id, auth_token=None: {
            "message": "User chat rooms deleted successfully",
            "deleted_room_count": 3,
        },
    )
    client = build_client()

    response = client.delete("/api/conversations/rooms/by-user/u-10")

    assert response.status_code == 200
    assert response.json()["deleted_room_count"] == 3


def test_delete_rooms_by_user_returns_403_for_other_user(monkeypatch):
    monkeypatch.setattr(conversation_router, "get_authenticated_user_id", lambda auth: "u-owner")
    client = build_client()

    response = client.delete("/api/conversations/rooms/by-user/u-other", headers={"Authorization": "Bearer t-room"})

    assert response.status_code == 403
    assert response.json()["detail"] == "cannot delete another user's rooms"


def test_get_room_history_success(monkeypatch):
    monkeypatch.setattr(
        conversation_router,
        "get_chat_history",
        lambda room_id, auth_token=None: [{"role": "user", "content": "hello"}],
    )
    client = build_client()

    response = client.get("/api/conversations/rooms/2/history")

    assert response.status_code == 200
    assert response.json()[0]["role"] == "user"
