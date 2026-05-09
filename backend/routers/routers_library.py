from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.services_library import *

router = APIRouter(prefix="/libraries", tags=["libraries"])

@router.get("/acts")
def get_library_acts():
    acts = get_all_acts()
    if isinstance(acts, list):
        return acts
    return []

@router.get("/act/{act_id}")
def get_library_act_by_id(act_id: int):
    act = get_act_by_id(act_id)
    if isinstance(act, dict) and act.get("id"):
        return act
    raise HTTPException(status_code=404, detail="Act not found")

@router.get("/tags")
def get_library_tags():
    tags = get_tags()
    if isinstance(tags, list):
        return tags
    return []

@router.get("/acts/{act_id}/books")
def get_library_books(act_id: int):
    books = get_books_by_act(act_id)
    if isinstance(books, list):
        return books
    return []

@router.get("/books/{book_id}/groups")
def get_library_groups(book_id: int):
    groups = get_groups_by_book(book_id)
    if isinstance(groups, list):
        return groups
    return []

@router.get("/groups/{group_id}/super_sections")
def get_library_super_sections(group_id: int):
    super_sections = get_super_sections_by_group(group_id)
    if isinstance(super_sections, list):
        return super_sections
    return []

@router.get("/super_sections/{super_section_id}/sections")
def get_library_sections(super_section_id: int):
    sections = get_sections_by_super_section(super_section_id)
    if isinstance(sections, list):
        return sections
    return []

@router.get("/sections/{act_id}/{section_number}")
def get_library_sections_by_number(act_id: int, section_number: str):
    sections = get_sections_by_act_and_number(act_id, section_number)
    if isinstance(sections, list):
        return sections
    return []


@router.get("/super_sections/{super_section_id}/sections_stream")
def stream_library_sections(super_section_id: int):
    return StreamingResponse(stream_sections_by_super_section(super_section_id), media_type="application/x-ndjson")