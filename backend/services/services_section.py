from database.supabase_client import get_supabase_client

def get_section_by_id(section_id: int) -> dict:
    section = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, section_number, sub_section, paragraph_number, item_order, text_processed, cross_references, external_citations"
        ).eq("id", section_id).single().execute().data
    if section:
        return section
    return {"message": "Section not found"}

def get_sections_by_act_id(act_id: int):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, section_number, sub_section, paragraph_number, item_order, text_processed, cross_references, external_citations"
        ).eq("act_id", act_id).execute().data
    if sections:
        return sections
    return {"message": "No sections found for this act"}

def get_sections_by_book_id(book_id: int):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, section_number, sub_section, paragraph_number, item_order, text_processed, cross_references, external_citations"
    ).eq("book_id", book_id).execute().data
    if sections:
        return sections
    return {"message": "No sections found for this book"}

def get_sections_by_group_id(group_id: int):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, section_number, sub_section, paragraph_number, item_order, text_processed, cross_references, external_citations"
    ).eq("group_id", group_id).execute().data
    if sections:
        return sections
    return {"message": "No sections found for this group"}

def get_sections_by_super_section_id(super_section_id: int):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, section_number, sub_section, paragraph_number, item_order, text_processed, cross_references, external_citations"
    ).eq("super_id", super_section_id).execute().data
    if sections:
        return sections
    return {"message": "No sections found for this super section"}

def get_section_by_act_and_section_number(act_id: int, section_number: str):
    section = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, section_number, sub_section, paragraph_number, item_order, text_processed, cross_references, external_citations"
    ).eq("act_id", act_id).eq("section_number", section_number).single().execute().data
    if section:
        return section
    return {"message": "Section not found with the given act ID and section number"}

def get_sections_by_act_and_keyword(act_id: int, keyword: str):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, section_number, sub_section, paragraph_number, item_order, text_processed, cross_references, external_citations"
    ).eq("act_id", act_id).ilike("text_processed", f"%{keyword}%").execute().data
    if sections:
        return sections
    return {"message": "No sections found matching the keyword in this act"}

def search_sections_by_keyword(keyword: str):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, section_number, sub_section, paragraph_number, item_order, text_processed, cross_references, external_citations"
    ).ilike("text_processed", f"%{keyword}%").execute().data
    if sections:
        return sections
    return {"message": "No sections found matching the keyword"}