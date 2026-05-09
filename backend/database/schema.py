from pydantic import BaseModel, EmailStr
from typing import Optional
class ActSection(BaseModel):
    id: int
    act_id: int
    book_id: int | None
    group_id: int | None
    super_id: int | None
    section_number: int
    sub_section: str | None
    paragraph_number: int
    item_order: str | None
    text_processed: str
    cross_references: dict | None
    external_citations: dict | None
