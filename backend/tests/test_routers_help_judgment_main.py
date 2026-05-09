import sys
import types

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from routers import routers_help as help_router
from routers import routers_judgment as judgment_router


def build_help_client():
    app = FastAPI()
    app.include_router(help_router.router)
    return TestClient(app)


def build_judgment_client():
    app = FastAPI()
    app.include_router(judgment_router.router, prefix="/api")
    return TestClient(app)


def load_main_module(monkeypatch, state):
    database_package = types.ModuleType("database")
    database_package.__path__ = []
    supabase_module = types.ModuleType("database.supabase_client")

    def get_supabase_client():
        state["supabase_called"] = state.get("supabase_called", 0) + 1
        return object()

    def get_supabase_client_with_auth(_token):
        state["supabase_auth_called"] = state.get("supabase_auth_called", 0) + 1
        return object()

    supabase_module.get_supabase_client = get_supabase_client
    supabase_module.get_supabase_client_with_auth = get_supabase_client_with_auth
    monkeypatch.setitem(sys.modules, "database", database_package)
    monkeypatch.setitem(sys.modules, "database.supabase_client", supabase_module)

    llm_package = types.ModuleType("llm")
    llm_package.__path__ = []
    chatbot_llm_module = types.ModuleType("llm.chatbot_llm")

    def get_llm():
        state["llm_called"] = state.get("llm_called", 0) + 1
        return object()

    chatbot_llm_module.get_llm = get_llm

    chatbot_router_module = types.ModuleType("llm.chatbot_router")
    stub_router = APIRouter()

    @stub_router.post("/chat")
    def chat_stub():
        return {"answer": "stub", "sources": []}

    chatbot_router_module.router = stub_router
    monkeypatch.setitem(sys.modules, "llm", llm_package)
    monkeypatch.setitem(sys.modules, "llm.chatbot_llm", chatbot_llm_module)
    monkeypatch.setitem(sys.modules, "llm.chatbot_router", chatbot_router_module)

    monkeypatch.delitem(sys.modules, "main", raising=False)
    import main

    return main


def test_help_root_returns_overview():
    client = build_help_client()

    response = client.get("/help/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Thai Labour Law API - help"
    assert "/api" in payload["endpoints"]


def test_help_api_returns_api_groups():
    client = build_help_client()

    response = client.get("/help/api")

    assert response.status_code == 200
    assert "/api/acts" in response.json()["endpoints"]


def test_help_sections_returns_section_endpoints():
    client = build_help_client()

    response = client.get("/help/api/sections")

    assert response.status_code == 200
    endpoints = response.json()["endpoints"]
    assert "/api/sections/search/{keyword}" in endpoints


def test_help_acts_returns_act_endpoints():
    client = build_help_client()

    response = client.get("/help/api/acts")

    assert response.status_code == 200
    endpoints = response.json()["endpoints"]
    assert "/api/acts/search/{keyword}" in endpoints


def test_help_libraries_returns_library_endpoints():
    client = build_help_client()

    response = client.get("/help/api/libraries")

    assert response.status_code == 200
    endpoints = response.json()["endpoints"]
    assert "/api/libraries/super_sections/{super_section_id}/sections_stream" in endpoints


def test_help_conversations_returns_conversation_endpoints():
    client = build_help_client()

    response = client.get("/help/api/conversations")

    assert response.status_code == 200
    endpoints = response.json()["endpoints"]
    assert "/api/conversations/rooms/{room_id}/history [GET]" in endpoints


def test_help_users_returns_user_endpoints():
    client = build_help_client()

    response = client.get("/help/api/users")

    assert response.status_code == 200
    endpoints = response.json()["endpoints"]
    assert "/api/users/options/job-types [GET]" in endpoints


def test_help_llm_returns_llm_endpoints():
    client = build_help_client()

    response = client.get("/help/llm")

    assert response.status_code == 200
    endpoints = response.json()["endpoints"]
    assert "/llm/chat_stream [POST]" in endpoints


def test_get_all_judgments_success(monkeypatch):
    monkeypatch.setattr(
        judgment_router,
        "get_all_judgments",
        lambda: [{"id": 1, "title": "Judgment 1"}],
    )
    client = build_judgment_client()

    response = client.get("/api/judgments")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 1


def test_get_judgment_by_id_success(monkeypatch):
    monkeypatch.setattr(
        judgment_router,
        "get_judgment_by_id",
        lambda judgment_id: {"id": judgment_id, "title": "Judgment 1"},
    )
    client = build_judgment_client()

    response = client.get("/api/judgments/5")

    assert response.status_code == 200
    assert response.json()["id"] == 5


def test_get_judgment_by_id_returns_404_when_not_found(monkeypatch):
    monkeypatch.setattr(
        judgment_router,
        "get_judgment_by_id",
        lambda judgment_id: {"message": "Judgment not found"},
    )
    client = build_judgment_client()

    response = client.get("/api/judgments/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Judgment not found"


def test_root_health_and_utility_endpoints(monkeypatch):
    state = {}
    main_module = load_main_module(monkeypatch, state)
    client = TestClient(main_module.app)

    root_response = client.get("/")
    health_response = client.get("/health")
    warmup_response = client.get("/warmup")
    enable_response = client.get("/enable-llm-router")
    llm_response = client.post("/llm/chat", json={"question": "x", "history": []})

    assert root_response.status_code == 200
    assert root_response.json()["message"] == "Welcome to the Thai Labour Law API"
    assert health_response.json()["status"] == "ok"
    assert warmup_response.json()["status"] == "warmed up"
    assert enable_response.json()["status"] == "LLM router enabled"
    assert llm_response.status_code == 200
    assert llm_response.json()["answer"] == "stub"
    assert state["supabase_called"] >= 1
    assert state["llm_called"] >= 1
