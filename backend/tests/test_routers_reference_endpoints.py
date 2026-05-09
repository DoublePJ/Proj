import importlib.util
import sys
import types
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from routers import routers_act as act_router
from routers import routers_library as library_router
from routers import routers_section as section_router


def load_llm_router():
    if "llm.chatbot_router" in sys.modules:
        return sys.modules["llm.chatbot_router"]

    llm_package = types.ModuleType("llm")
    llm_package.__path__ = []
    sys.modules["llm"] = llm_package

    structure_module = types.ModuleType("llm.chatbot_structure")

    class ChatRequest(BaseModel):
        question: str
        history: list[dict[str, str]] = []

    class ChatResponse(BaseModel):
        answer: str
        sources: list[str]

    structure_module.ChatRequest = ChatRequest
    structure_module.ChatResponse = ChatResponse
    sys.modules["llm.chatbot_structure"] = structure_module

    service_module = types.ModuleType("llm.chatbot_service")

    def chat_service(request):
        raise NotImplementedError

    def chat_stream_service(request):
        raise NotImplementedError

    service_module.chat_service = chat_service
    service_module.chat_stream_service = chat_stream_service
    sys.modules["llm.chatbot_service"] = service_module

    router_path = Path(__file__).resolve().parents[1] / "llm" / "chatbot_router.py"
    spec = importlib.util.spec_from_file_location("llm.chatbot_router", router_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["llm.chatbot_router"] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def build_client():
    llm_router = load_llm_router()
    app = FastAPI()
    app.include_router(act_router.router, prefix="/api")
    app.include_router(section_router.router, prefix="/api")
    app.include_router(library_router.router, prefix="/api")
    app.include_router(llm_router.router, prefix="/llm")
    return TestClient(app)


def valid_section(section_id=1, act_id=10):
    return {
        "id": section_id,
        "act_id": act_id,
        "book_id": 1,
        "group_id": 2,
        "super_id": 3,
        "section_number": 5,
        "sub_section": None,
        "paragraph_number": 1,
        "item_order": None,
        "text_processed": "ข้อความมาตรา",
        "cross_references": None,
        "external_citations": None,
    }


def test_read_section_by_id_success(monkeypatch):
    monkeypatch.setattr(section_router, "get_section_by_id", lambda section_id: valid_section(section_id))
    client = build_client()

    response = client.get("/api/sections/by/section_id/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_read_section_by_id_returns_404_when_not_found(monkeypatch):
    monkeypatch.setattr(section_router, "get_section_by_id", lambda section_id: None)
    client = build_client()

    response = client.get("/api/sections/by/section_id/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Section not found"


def test_read_sections_by_act_id_returns_list(monkeypatch):
    monkeypatch.setattr(
        section_router,
        "get_sections_by_act_id",
        lambda act_id: [valid_section(1, act_id), valid_section(2, act_id)],
    )
    client = build_client()

    response = client.get("/api/sections/by/act_id/10")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_sections_by_keyword_returns_list(monkeypatch):
    monkeypatch.setattr(
        section_router,
        "search_sections_by_keyword",
        lambda keyword: [valid_section(3, 10)],
    )
    client = build_client()

    response = client.get("/api/sections/search/เลิกจ้าง")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 3


def test_search_sections_by_act_and_keyword_returns_list(monkeypatch):
    monkeypatch.setattr(
        section_router,
        "get_sections_by_act_and_keyword",
        lambda act_id, keyword: [valid_section(4, act_id)],
    )
    client = build_client()

    response = client.get("/api/sections/by/act_id/10/search/ค่าชดเชย")

    assert response.status_code == 200
    assert response.json()[0]["act_id"] == 10


def test_read_sections_by_book_id_returns_list(monkeypatch):
    monkeypatch.setattr(
        section_router,
        "get_sections_by_book_id",
        lambda book_id: [valid_section(8, 10)],
    )
    client = build_client()

    response = client.get("/api/sections/by/book_id/2")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 8


def test_read_sections_by_group_id_returns_list(monkeypatch):
    monkeypatch.setattr(
        section_router,
        "get_sections_by_group_id",
        lambda group_id: [valid_section(9, 10)],
    )
    client = build_client()

    response = client.get("/api/sections/by/group_id/3")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 9


def test_read_sections_by_super_section_id_returns_list(monkeypatch):
    monkeypatch.setattr(
        section_router,
        "get_sections_by_super_section_id",
        lambda super_section_id: [valid_section(10, 10)],
    )
    client = build_client()

    response = client.get("/api/sections/by/super_section_id/4")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 10


def test_read_section_by_act_and_section_number_returns_section(monkeypatch):
    monkeypatch.setattr(
        section_router,
        "get_section_by_act_and_section_number",
        lambda act_id, section_number: valid_section(11, act_id),
    )
    client = build_client()

    response = client.get("/api/sections/by/act_id/10/section_number/5")

    assert response.status_code == 200
    assert response.json()["id"] == 11


def test_read_act_by_id_success(monkeypatch):
    monkeypatch.setattr(act_router, "get_act_by_id", lambda act_id: {"id": act_id, "name": "Act A"})
    client = build_client()

    response = client.get("/api/acts/by/act_id/10")

    assert response.status_code == 200
    assert response.json()["id"] == 10


def test_read_act_by_id_returns_404_when_not_found(monkeypatch):
    monkeypatch.setattr(act_router, "get_act_by_id", lambda act_id: None)
    client = build_client()

    response = client.get("/api/acts/by/act_id/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Act not found"


def test_read_all_acts_returns_list(monkeypatch):
    monkeypatch.setattr(act_router, "get_all_acts", lambda: [{"id": 1, "name": "Act A"}])
    client = build_client()

    response = client.get("/api/acts/")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Act A"


def test_search_acts_returns_list(monkeypatch):
    monkeypatch.setattr(act_router, "search_acts_by_keyword", lambda keyword: [{"id": 2, "title": "Act Search"}])
    client = build_client()

    response = client.get("/api/acts/search/แรงงาน")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Act Search"


def test_get_act_books_returns_list(monkeypatch):
    monkeypatch.setattr(act_router, "get_act_books", lambda act_id: [{"id": 11, "act_id": act_id, "title": "Book 1"}])
    client = build_client()

    response = client.get("/api/acts/books/by/act_id/10")

    assert response.status_code == 200
    assert response.json()[0]["act_id"] == 10


def test_read_act_by_name_returns_list(monkeypatch):
    monkeypatch.setattr(act_router, "get_act_by_name", lambda act_name: [{"id": 13, "title": act_name}])
    client = build_client()

    response = client.get("/api/acts/by/act_name/แรงงาน")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 13


def test_read_book_by_id_returns_book(monkeypatch):
    monkeypatch.setattr(act_router, "get_act_book_by_id", lambda book_id: {"id": book_id, "title": "Book A"})
    client = build_client()

    response = client.get("/api/acts/books/by/book_id/20")

    assert response.status_code == 200
    assert response.json()["id"] == 20


def test_read_book_by_act_and_book_number_returns_book(monkeypatch):
    monkeypatch.setattr(
        act_router,
        "get_act_book_by_act_and_book_number",
        lambda act_id, book_number: {"id": 21, "act_id": act_id, "book_number": book_number},
    )
    client = build_client()

    response = client.get("/api/acts/books/by/act_id/10/book_number/1")

    assert response.status_code == 200
    assert response.json()["book_number"] == "1"


def test_search_books_returns_list(monkeypatch):
    monkeypatch.setattr(act_router, "search_books_by_keyword", lambda keyword: [{"id": 12, "title": "Book Search"}])
    client = build_client()

    response = client.get("/api/acts/books/search/สัญญาจ้าง")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Book Search"


def test_get_act_groups_returns_list(monkeypatch):
    monkeypatch.setattr(act_router, "get_act_groups", lambda book_id: [{"id": 21, "book_id": book_id, "title": "Group 1"}])
    client = build_client()

    response = client.get("/api/acts/groups/by/book_id/7")

    assert response.status_code == 200
    assert response.json()[0]["book_id"] == 7


def test_read_group_by_id_returns_group(monkeypatch):
    monkeypatch.setattr(act_router, "get_act_group_by_id", lambda group_id: {"id": group_id, "title": "Group A"})
    client = build_client()

    response = client.get("/api/acts/groups/by/group_id/30")

    assert response.status_code == 200
    assert response.json()["id"] == 30


def test_read_group_by_act_and_group_number_returns_group(monkeypatch):
    monkeypatch.setattr(
        act_router,
        "get_act_group_by_act_and_group_number",
        lambda act_id, group_number: {"id": 31, "act_id": act_id, "group_number": group_number},
    )
    client = build_client()

    response = client.get("/api/acts/groups/by/act_id/10/group_number/2")

    assert response.status_code == 200
    assert response.json()["group_number"] == "2"


def test_search_groups_returns_list(monkeypatch):
    monkeypatch.setattr(act_router, "search_groups_by_keyword", lambda keyword: [{"id": 22, "title": "Group Search"}])
    client = build_client()

    response = client.get("/api/acts/groups/search/วันหยุด")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Group Search"


def test_get_act_super_sections_returns_list(monkeypatch):
    monkeypatch.setattr(act_router, "get_act_super_sections_by_act_id", lambda act_id: [{"id": 31, "act_id": act_id, "title": "Super 1"}])
    client = build_client()

    response = client.get("/api/acts/super_sections/by/act_id/10")

    assert response.status_code == 200
    assert response.json()[0]["act_id"] == 10


def test_read_super_sections_by_group_id_returns_list(monkeypatch):
    monkeypatch.setattr(
        act_router,
        "get_act_super_sections_by_group_id",
        lambda group_id: [{"id": 32, "group_id": group_id}],
    )
    client = build_client()

    response = client.get("/api/acts/super_sections/by/group_id/12")

    assert response.status_code == 200
    assert response.json()[0]["group_id"] == 12


def test_read_super_section_by_id_returns_item(monkeypatch):
    monkeypatch.setattr(
        act_router,
        "get_act_super_section_by_id",
        lambda super_section_id: {"id": super_section_id, "title": "Super A"},
    )
    client = build_client()

    response = client.get("/api/acts/super_sections/by/super_section_id/40")

    assert response.status_code == 200
    assert response.json()["id"] == 40


def test_read_super_section_by_act_and_number_returns_item(monkeypatch):
    monkeypatch.setattr(
        act_router,
        "get_act_super_section_by_act_and_super_section_number",
        lambda act_id, super_section_number: {
            "id": 41,
            "act_id": act_id,
            "super_section_number": super_section_number,
        },
    )
    client = build_client()

    response = client.get("/api/acts/super_sections/by/act_id/10/super_section_number/3")

    assert response.status_code == 200
    assert response.json()["super_section_number"] == "3"


def test_get_library_acts_returns_list(monkeypatch):
    monkeypatch.setattr(library_router, "get_all_acts", lambda: [{"id": 1, "name": "Act A"}])
    client = build_client()

    response = client.get("/api/libraries/acts")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 1


def test_get_library_tags_returns_list(monkeypatch):
    monkeypatch.setattr(library_router, "get_tags", lambda: [{"id": 1, "name": "สำคัญ"}])
    client = build_client()

    response = client.get("/api/libraries/tags")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "สำคัญ"


def test_get_library_books_returns_list(monkeypatch):
    monkeypatch.setattr(library_router, "get_books_by_act", lambda act_id: [{"id": 3, "act_id": act_id, "key": "groups"}])
    client = build_client()

    response = client.get("/api/libraries/acts/10/books")

    assert response.status_code == 200
    assert response.json()[0]["act_id"] == 10


def test_get_library_groups_returns_list(monkeypatch):
    monkeypatch.setattr(library_router, "get_groups_by_book", lambda book_id: [{"id": 4, "book_id": book_id, "key": "super_sections"}])
    client = build_client()

    response = client.get("/api/libraries/books/8/groups")

    assert response.status_code == 200
    assert response.json()[0]["book_id"] == 8


def test_get_library_super_sections_returns_list(monkeypatch):
    monkeypatch.setattr(library_router, "get_super_sections_by_group", lambda group_id: [{"id": 5, "group_id": group_id, "key": "sections"}])
    client = build_client()

    response = client.get("/api/libraries/groups/9/super_sections")

    assert response.status_code == 200
    assert response.json()[0]["group_id"] == 9


def test_get_library_sections_returns_list(monkeypatch):
    monkeypatch.setattr(library_router, "get_sections_by_super_section", lambda super_section_id: [valid_section(6, 10)])
    client = build_client()

    response = client.get("/api/libraries/super_sections/11/sections")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 6


def test_get_library_sections_by_number_returns_list(monkeypatch):
    monkeypatch.setattr(library_router, "get_sections_by_act_and_number", lambda act_id, section_number: [valid_section(7, act_id)])
    client = build_client()

    response = client.get("/api/libraries/sections/10/5")

    assert response.status_code == 200
    assert response.json()[0]["section_number"] == 5


def test_get_library_act_by_id_returns_404_when_not_found(monkeypatch):
    monkeypatch.setattr(library_router, "get_act_by_id", lambda act_id: {"message": "missing"})
    client = build_client()

    response = client.get("/api/libraries/act/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Act not found"


def test_get_library_act_by_id_success(monkeypatch):
    monkeypatch.setattr(library_router, "get_act_by_id", lambda act_id: {"id": act_id, "title": "Act B"})
    client = build_client()

    response = client.get("/api/libraries/act/99")

    assert response.status_code == 200
    assert response.json()["id"] == 99


def test_stream_library_sections_returns_ndjson(monkeypatch):
    async def fake_stream_sections_by_super_section(super_section_id):
        yield "{\"type\":\"content\",\"data\":\"a\"}\n"

    monkeypatch.setattr(library_router, "stream_sections_by_super_section", fake_stream_sections_by_super_section)
    client = build_client()

    response = client.get("/api/libraries/super_sections/7/sections_stream")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")
    assert "content" in response.text


def test_chat_endpoint_success(monkeypatch):
    llm_router = load_llm_router()
    monkeypatch.setattr(llm_router, "chat_service", lambda request: {"answer": "ok", "sources": ["มาตรา 1"]})
    client = build_client()

    response = client.post("/llm/chat", json={"question": "ถามอะไร", "history": []})

    assert response.status_code == 200
    assert response.json()["answer"] == "ok"


def test_chat_endpoint_returns_500_when_service_fails(monkeypatch):
    llm_router = load_llm_router()

    def boom(_request):
        raise RuntimeError("llm failed")

    monkeypatch.setattr(llm_router, "chat_service", boom)
    client = build_client()

    response = client.post("/llm/chat", json={"question": "ถามอะไร", "history": []})

    assert response.status_code == 500
    assert response.json()["detail"] == "llm failed"


def test_chat_stream_endpoint_success(monkeypatch):
    llm_router = load_llm_router()
    from fastapi.responses import StreamingResponse

    async def generator():
        yield "{\"type\":\"content\",\"data\":\"hello\"}\n"

    monkeypatch.setattr(llm_router, "chat_stream_service", lambda request: StreamingResponse(generator(), media_type="application/x-ndjson"))
    client = build_client()

    response = client.post("/llm/chat_stream", json={"question": "ถามอะไร", "history": []})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")
    assert "hello" in response.text


def test_chat_stream_endpoint_returns_error_stream_when_service_raises(monkeypatch):
    llm_router = load_llm_router()

    def boom(_request):
        raise RuntimeError("stream failed")

    monkeypatch.setattr(llm_router, "chat_stream_service", boom)
    client = build_client()

    response = client.post("/llm/chat_stream", json={"question": "ถามอะไร", "history": []})

    assert response.status_code == 200
    assert "stream failed" in response.text
