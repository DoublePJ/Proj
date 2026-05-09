from database.supabase_client import get_supabase_client

def get_all_judgments():
    judgments = get_supabase_client().table("judgments").select(
        "id, title, case_number, summary, detail, created_at, updated_at"
    ).order("id", desc=True).execute().data
    if judgments:
        for idx in range(len(judgments)):
            judgment_tags = get_supabase_client().table("judgment_tags").select(
                "tag_id"
            ).eq("judgment_id", judgments[idx]["id"]).order("tag_id").execute().data
            judgments[idx]["tags"] = [jt["tag_id"] for jt in judgment_tags]
        return judgments
    return {"message": "No judgments found"}

def get_judgment_by_id(judgment_id: int):
    judgment_rows = get_supabase_client().table("judgments").select(
        "id, title, case_number, summary, detail, created_at, updated_at"
    ).eq("id", judgment_id).limit(1).execute().data
    if judgment_rows and len(judgment_rows) > 0:
        judgment = judgment_rows[0]
        judgment_tags = get_supabase_client().table("judgment_tags").select(
            "tag_id"
        ).eq("judgment_id", judgment["id"]).order("tag_id").execute().data
        judgment["tags"] = [jt["tag_id"] for jt in judgment_tags]
        return judgment
    return {"message": "Judgment not found"}
