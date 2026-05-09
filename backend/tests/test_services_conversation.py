from types import SimpleNamespace

from services import services_conversation as svc


class FakeTable:
    def __init__(self, name, state):
        self.name = name
        self.state = state
        self.operation = None
        self.payload = None
        self.filters = []
        self.ordering = None
        self.limit_value = None

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        return self

    def delete(self):
        self.operation = "delete"
        return self

    def select(self, *_args):
        self.operation = "select"
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def order(self, field, desc=False):
        self.ordering = (field, desc)
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def execute(self):
        self.state["calls"].append(
            {
                "table": self.name,
                "operation": self.operation,
                "payload": self.payload,
                "filters": list(self.filters),
                "ordering": self.ordering,
                "limit": self.limit_value,
            }
        )

        key = f"{self.name}_{self.operation}_result"
        return SimpleNamespace(data=self.state.get(key, []))


class FakeClient:
    def __init__(self, state):
        self.state = state

    def table(self, name):
        return FakeTable(name, self.state)


def test_create_chat_room_with_user_id(monkeypatch):
    state = {
        "calls": [],
        "chat_rooms_insert_result": [{"id": 7, "title": "ห้องใหม่", "user_id": "u-1"}],
    }
    fake_client = FakeClient(state)
    monkeypatch.setattr(svc, "get_user_client", lambda _token: fake_client)

    result = svc.create_chat_room(user_id="u-1", title="ห้องใหม่", auth_token="Bearer token")

    assert result["id"] == 7
    insert_call = next(c for c in state["calls"] if c["table"] == "chat_rooms" and c["operation"] == "insert")
    assert insert_call["payload"]["user_id"] == "u-1"
    assert insert_call["payload"]["title"] == "ห้องใหม่"
    assert insert_call["payload"]["is_archive"] is False


def test_add_message_updates_room_timestamp(monkeypatch):
    state = {
        "calls": [],
        "chat_messages_insert_result": [
            {"id": 99, "room_id": 10, "sender": "user", "message": "ทดสอบ"}
        ],
        "chat_rooms_update_result": [{"id": 10}],
    }
    fake_client = FakeClient(state)
    monkeypatch.setattr(svc, "get_user_client", lambda _token: fake_client)

    result = svc.add_message(
        room_id=10,
        sender="user",
        message="ทดสอบ",
        metadata={"source": "ui"},
        auth_token="Bearer token",
    )

    assert result["id"] == 99
    message_insert = next(
        c for c in state["calls"] if c["table"] == "chat_messages" and c["operation"] == "insert"
    )
    room_update = next(
        c for c in state["calls"] if c["table"] == "chat_rooms" and c["operation"] == "update"
    )
    assert message_insert["payload"]["metadata"] == {"source": "ui"}
    assert ("id", 10) in room_update["filters"]


def test_get_chat_history_maps_role_and_content(monkeypatch):
    monkeypatch.setattr(
        svc,
        "get_messages",
        lambda room_id, limit=100, auth_token=None: [
            {"sender": "user", "message": "สวัสดี", "metadata": {"m": 1}},
            {"sender": "bot", "message": "สวัสดีครับ", "metadata": None},
        ],
    )

    history = svc.get_chat_history(room_id=20, auth_token="Bearer token")

    assert history == [
        {"role": "user", "content": "สวัสดี", "metadata": {"m": 1}},
        {"role": "bot", "content": "สวัสดีครับ", "metadata": None},
    ]
