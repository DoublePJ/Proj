from fastapi import APIRouter, HTTPException
from services.services_act import *

router = APIRouter(prefix="/acts", tags=["acts"])

@router.get("/by/act_id/{act_id}")
def read_act_by_id(act_id: int):
    act = get_act_by_id(act_id)
    if act:
        return act
    raise HTTPException(status_code=404, detail="Act not found")

@router.get("/")
def read_all_acts():
    acts = get_all_acts()
    if acts:
        return acts
    return []

@router.get("/by/act_name/{act_name}")
def read_act_by_name(act_name: str):
    act = get_act_by_name(act_name)
    if act:
        return act
    raise HTTPException(status_code=404, detail="Act not found with the given name")

@router.get("/search/{keyword}")
def search_acts(keyword: str):
    acts = search_acts_by_keyword(keyword)
    if acts:
        return acts
    return []

@router.get("/books/by/act_id/{act_id}")
def read_act_books(act_id: int):
    books = get_act_books(act_id)
    if books:
        return books
    return []

@router.get("/books/by/book_id/{book_id}")
def read_act_book_by_id(book_id: int):
    book = get_act_book_by_id(book_id)
    if book:
        return book
    raise HTTPException(status_code=404, detail="Book not found")

@router.get("/books/by/act_id/{act_id}/book_number/{book_number}")
def read_act_book_by_act_and_book_number(act_id: int, book_number: str):
    book = get_act_book_by_act_and_book_number(act_id, book_number)
    if book:
        return book
    raise HTTPException(status_code=404, detail="Book not found with the given act ID and book number")

@router.get("/books/search/{keyword}")
def search_books(keyword: str):
    books = search_books_by_keyword(keyword)
    if books:
        return books
    return []

@router.get("/groups/by/book_id/{book_id}")
def read_act_groups(book_id: int):
    groups = get_act_groups(book_id)
    if groups:
        return groups
    return []

@router.get("/groups/by/group_id/{group_id}")
def read_act_group_by_id(group_id: int):
    group = get_act_group_by_id(group_id)
    if group:
        return group
    raise HTTPException(status_code=404, detail="Group not found")

@router.get("/groups/by/act_id/{act_id}/group_number/{group_number}")
def read_act_group_by_act_and_group_number(act_id: int, group_number: str):
    group = get_act_group_by_act_and_group_number(act_id, group_number)
    if group:
        return group
    raise HTTPException(status_code=404, detail="Group not found with the given act ID and group number")

@router.get("/groups/search/{keyword}")
def search_groups(keyword: str):
    groups = search_groups_by_keyword(keyword)
    if groups:
        return groups
    return []

@router.get("/super_sections/by/act_id/{act_id}")
def read_act_super_sections_by_act_id(act_id: int):
    super_sections = get_act_super_sections_by_act_id(act_id)
    if super_sections:
        return super_sections
    return []

@router.get("/super_sections/by/group_id/{group_id}")
def read_act_super_sections(group_id: int):
    super_sections = get_act_super_sections_by_group_id(group_id)
    if super_sections:
        return super_sections
    return []

@router.get("/super_sections/by/super_section_id/{super_section_id}")
def read_act_super_section_by_id(super_section_id: int):
    super_section = get_act_super_section_by_id(super_section_id)
    if super_section:
        return super_section
    raise HTTPException(status_code=404, detail="Super section not found")

@router.get("/super_sections/by/act_id/{act_id}/super_section_number/{super_section_number}")
def read_act_super_section_by_act_and_super_section_number(act_id: int, super_section_number: str):
    super_section = get_act_super_section_by_act_and_super_section_number(act_id, super_section_number)
    if super_section:
        return super_section
    raise HTTPException(status_code=404, detail="Super section not found with the given act ID and super section number")

def search_act_super_sections(keyword: str):
    super_sections = search_groups_by_keyword(keyword)
    if super_sections:
        return super_sections
    return []