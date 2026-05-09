
from fastapi import HTTPException
import json
from fastapi.responses import StreamingResponse
# import asyncio

from fastapi import APIRouter
router = APIRouter(prefix="", tags=["llm"])

# --- Import Data Models ---
from llm.chatbot_structure import ChatRequest, ChatResponse

# --- Import Chat Service Functions ---
from llm.chatbot_service import chat_service, chat_stream_service

# --- Main API Endpoint ---
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        return chat_service(request)

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat_stream")
async def chat_stream_endpoint(request: ChatRequest):
    try:
        return chat_stream_service(request)

    except Exception as e:
        print(f"Server Error: {e}")
        # กรณี Error หนักๆ ส่ง JSON Error กลับไป
        return StreamingResponse(
            iter([json.dumps({"type": "error", "message": str(e)}) + "\n"]),
            media_type="application/x-ndjson"
        )