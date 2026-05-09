import json
from database.supabase_client import get_supabase_client

def get_tags():
    tags = get_supabase_client().table("tags").select(
        "id, name, description"
    ).order("id").execute().data
    if tags:
        return tags
    return {"message": "No tags found"}

def get_all_acts():
    acts = get_supabase_client().table("acts").select(
        "id, title, preface, updated_at"
    ).order("id").execute().data
    if acts:
        for idx in range(len(acts)):
            act_tags = get_supabase_client().table("act_tags").select(
                "tag_id"
            ).eq("act_id", acts[idx]["id"]).order("tag_id").execute().data
            acts[idx]["tags"] = [at["tag_id"] for at in act_tags]
            acts[idx]["key"] = "books"  # For frontend tree structure
        return acts
    return {"message": "No acts found"}

def get_act_by_id(act_id: int):
    act_rows = get_supabase_client().table("acts").select(
        "id, title, preface, updated_at"
    ).eq("id", act_id).limit(1).execute().data
    if act_rows and len(act_rows) > 0:
        act = act_rows[0]
        act_tags = get_supabase_client().table("act_tags").select(
            "tag_id"
        ).eq("act_id", act["id"]).order("tag_id").execute().data
        act["tags"] = [at["tag_id"] for at in act_tags]
        act["key"] = "books"  # For frontend tree structure
        return act
    return {"message": "Act not found"}

def get_books_by_act(act_id: int):
    books = get_supabase_client().table("act_books").select(
        "id, act_id, book_number, title:book_title"
    ).order("id").eq("act_id", act_id).execute().data
    if books:
        for idx in range(len(books)):
            books[idx]["key"] = "groups"  # For frontend tree structure
        return books
    return {"message": "No books found for the given act_id"}

def get_groups_by_book(book_id: int):
    groups = get_supabase_client().table("act_groups").select(
        "id, act_id, book_id, group_number, title:group_title"
    ).eq("book_id", book_id).order("id").execute().data
    if groups:
        for idx in range(len(groups)):
            groups[idx]["key"] = "super_sections"  # For frontend tree structure
        return groups
    return {"message": "No groups found for the given book_id"}

def get_super_sections_by_group(group_id: int):
    super_sections = get_supabase_client().table("act_super_sections").select(
        "id, act_id, group_id, super_number, title:super_title"
    ).eq("group_id", group_id).order("id").execute().data
    if super_sections:
        for idx in range(len(super_sections)):
            super_sections[idx]["key"] = "sections"  # For frontend tree structure
        return super_sections
    return {"message": "No super sections found for the given group_id"}

def get_sections_by_super_section(super_section_id: int):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, \
        section_number, sub_section, paragraph_number, item_order, \
        title:text_original, cross_references, external_citations"
    ).eq("super_id", super_section_id).order("id").execute().data
    if sections:
        for idx in range(len(sections)):
            citations = get_supabase_client().table("act_section_tags").select(
                "tag_id"
            ).eq("act_section_id", sections[idx]["id"]).order("tag_id").execute().data
            sections[idx]["tags"] = [c["tag_id"] for c in citations]
            sections[idx]["key"] = "section"  # For frontend tree structure
        return sections
    return {"message": "No sections found for the given super_section_id"}

def get_sections_by_act_and_number(act_id: int, section_number: str):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, \
        section_number, sub_section, paragraph_number, item_order, \
        title:text_original, cross_references, external_citations"
    ).eq("act_id", act_id).eq("section_number", section_number).execute().data
    if sections:
        for idx in range(len(sections)):
            citations = get_supabase_client().table("act_section_tags").select(
                "tag_id"
            ).eq("act_section_id", sections[idx]["id"]).execute().data
            sections[idx]["tags"] = [c["tag_id"] for c in citations]
            sections[idx]["key"] = "section"  # For frontend tree structure
        return sections
    return {"message": "No sections found for the given act_id and section_number"}

def stream_sections_by_super_section(super_section_id: int):
    sections = get_supabase_client().table("act_sections").select(
        "id, act_id, book_id, group_id, super_id, \
        section_number, sub_section, paragraph_number, item_order, \
        title:text_original, cross_references, external_citations"
    ).eq("super_id", super_section_id).order("id").execute().data or []

    for section in sections:
        citations = get_supabase_client().table("act_section_tags").select(
            "tag_id"
        ).eq("act_section_id", section["id"]).order("tag_id").execute().data
        section["tags"] = [c["tag_id"] for c in citations]
        section["key"] = "section"  # For frontend tree structure
        yield json.dumps({"type": "section", "parentId": super_section_id, "data": section}, ensure_ascii=False) + "\n"

    yield json.dumps({"type": "done"}) + "\n"