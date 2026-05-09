from pydantic import BaseModel
from typing import List, Dict

# --- Data Models (รูปแบบข้อมูลที่รับ-ส่ง) ---
class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, str]] = []  # รับประวัติการคุยมาด้วย (Context Awareness)

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]                  # ส่งรายการมาตราที่อ้างอิงกลับไป (Citation)