from database.supabase_client import get_supabase_client

def get_act_by_id(act_id: int):
    act = get_supabase_client().table("acts").select("*").eq("id", act_id).single().execute().data
    if act:
        return act
    return {"message": "Act not found"}

def get_all_acts():
    acts = get_supabase_client().table("acts").select("*").execute().data
    if acts:
        return acts
    return {"message": "No acts found"}

def get_act_by_name(act_name: str):
    act = get_supabase_client().table("acts").select("*").ilike("title", f"%{act_name}%").execute().data
    if act:
        return act
    return {"message": "Act not found with the given name"}

def search_acts_by_keyword(keyword: str):
    acts = get_supabase_client().table("acts").select("*").ilike("preface", f"%{keyword}%").execute().data
    if acts:
        return acts
    return {"message": "No acts found matching the keyword"}

def get_act_books(act_id: int):
    books = get_supabase_client().table("act_books").select("*").eq("act_id", act_id).execute().data
    if books:
        return books
    return {"message": "No books found for this act"}

def get_act_book_by_id(book_id: int):
    book = get_supabase_client().table("act_books").select("*").eq("id", book_id).single().execute().data
    if book:
        return book
    return {"message": "Book not found"}

def get_act_book_by_act_and_book_number(act_id: int, book_number: str):
    book = get_supabase_client().table("act_books").select("*").eq("act_id", act_id).eq("book_number", book_number).single().execute().data
    if book:
        return book
    return {"message": "Book not found with the given act ID and book number"}

def search_books_by_keyword(keyword: str):
    books = get_supabase_client().table("act_books").select("*").ilike("title", f"%{keyword}%").execute().data
    if books:
        return books
    return {"message": "No books found matching the keyword"}

def get_act_groups(book_id: int):
    groups = get_supabase_client().table("act_groups").select("*").eq("book_id", book_id).execute().data
    if groups:
        return groups
    return {"message": "No groups found for this book"}

def get_act_group_by_id(group_id: int):
    group = get_supabase_client().table("act_groups").select("*").eq("id", group_id).single().execute().data
    if group:
        return group
    return {"message": "Group not found"}

def get_act_groups_by_book_id(book_id: int):
    groups = get_supabase_client().table("act_groups").select("*").eq("book_id", book_id).execute().data
    if groups:
        return groups
    return {"message": "No groups found for this book"}

def get_act_group_by_act_and_group_number(act_id: int, group_number: str):
    group = get_supabase_client().table("act_groups").select("*").eq("act_id", act_id).eq("group_number", group_number).single().execute().data
    if group:
        return group
    return {"message": "Group not found with the given act ID and group number"}

def search_groups_by_keyword(keyword: str):
    groups = get_supabase_client().table("act_groups").select("*").ilike("title", f"%{keyword}%").execute().data
    if groups:
        return groups
    return {"message": "No groups found matching the keyword"}

def get_act_super_sections_by_act_id(act_id: int):
    super_sections = get_supabase_client().table("act_super_sections").select("*").eq("act_id", act_id).execute().data
    if super_sections:
        return super_sections
    return {"message": "No super sections found for this act"}

def get_act_super_sections_by_group_id(group_id: int):
    super_sections = get_supabase_client().table("act_super_sections").select("*").eq("group_id", group_id).execute().data
    if super_sections:
        return super_sections
    return {"message": "No super sections found for this group"}

def get_act_super_section_by_id(super_section_id: int):
    super_section = get_supabase_client().table("act_super_sections").select("*").eq("id", super_section_id).single().execute().data
    if super_section:
        return super_section
    return {"message": "Super section not found"}

def get_act_super_section_by_act_and_super_section_number(act_id: int, super_section_number: str):
    super_section = get_supabase_client().table("act_super_sections").select("*").eq("act_id", act_id).eq("super_section_number", super_section_number).single().execute().data
    if super_section:
        return super_section
    return {"message": "Super section not found with the given act ID and super section number"}

def search_super_sections_by_keyword(keyword: str):
    super_sections = get_supabase_client().table("act_super_sections").select("*").ilike("title", f"%{keyword}%").execute().data
    if super_sections:
        return super_sections
    return {"message": "No super sections found matching the keyword"}