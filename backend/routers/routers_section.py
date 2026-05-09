from fastapi import APIRouter, HTTPException
from database.schema import ActSection
from services.services_section import *

router = APIRouter(prefix="/sections", tags=["act_sections"])

@router.get("/by/section_id/{section_id}", response_model=ActSection)
def read_section(section_id: int):
    section = get_section_by_id(section_id)
    if section:
        return section
    raise HTTPException(status_code=404, detail="Section not found")

@router.get("/by/act_id/{act_id}", response_model=list[ActSection])
def read_sections_by_act_id(act_id: int):
    sections = get_sections_by_act_id(act_id)
    if sections:
        return sections
    return []

@router.get("/by/book_id/{book_id}", response_model=list[ActSection])
def read_sections_by_book_id(book_id: int):
    sections = get_sections_by_book_id(book_id)
    if sections:
        return sections
    return []

@router.get("/by/group_id/{group_id}", response_model=list[ActSection])
def read_sections_by_group_id(group_id: int):
    sections = get_sections_by_group_id(group_id)
    if sections:
        return sections
    return []

@router.get("/by/super_section_id/{super_section_id}", response_model=list[ActSection])
def read_sections_by_super_section_id(super_section_id: int):
    sections = get_sections_by_super_section_id(super_section_id)
    if sections:
        return sections
    return []

@router.get("/by/act_id/{act_id}/section_number/{section_number}", response_model=ActSection)
def read_section_by_act_and_section_number(act_id: int, section_number: str):
    section = get_section_by_act_and_section_number(act_id, section_number)
    if section:
        return section
    raise HTTPException(status_code=404, detail="Section not found with the given act ID and section number")

@router.get("/by/act_id/{act_id}/search/{keyword}", response_model=list[ActSection])
def read_sections_by_act_and_keyword(act_id: int, keyword: str):
    sections = get_sections_by_act_and_keyword(act_id, keyword)
    if sections:
        return sections
    return []

@router.get("/search/{keyword}", response_model=list[ActSection])
def search_sections(keyword: str):
    sections = search_sections_by_keyword(keyword)
    if sections:
        return sections
    return []