from pydantic import BaseModel
from typing import Optional


class ActSummary(BaseModel):
    id: int
    title: str
    slug: str


class ActDetail(BaseModel):
    id: int
    title: str
    slug: str
    content: Optional[str]


class ActSection(BaseModel):
    id: int
    act_id: int
    title: str
    content: Optional[str]
