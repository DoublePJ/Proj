from fastapi import APIRouter, Header, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.services_conversation import *
from utils.supabase_auth import get_authenticated_user_id

router = APIRouter(prefix="/conversations", tags=["conversations"])

class CreateRoomRequest(BaseModel):
    user_id: Optional[str] = None
    title: str = "การสนทนาใหม่"

class UpdateRoomRequest(BaseModel):
    title: Optional[str] = None
    is_archive: Optional[bool] = None

class AddMessageRequest(BaseModel):
    sender: str  # 'user' หรือ 'bot'
    message: str
    metadata: Optional[dict] = None


def _raise_conversation_error(message: str, default_status: int = 500):
    lowered = (message or "").lower()
    if "missing access token" in lowered or "unauthorized" in lowered or "invalid or expired access token" in lowered:
        raise HTTPException(status_code=401, detail=message)
    if "permission denied by rls" in lowered or "row-level security" in lowered:
        raise HTTPException(status_code=403, detail=message)
    raise HTTPException(status_code=default_status, detail=message)


# ===================== Chat Rooms =====================

@router.post("/rooms")
def create_room(request: CreateRoomRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    """สร้างห้องสนทนาใหม่"""
    try:
        authenticated_user_id = get_authenticated_user_id(authorization)
    except Exception as e:
        _raise_conversation_error(str(e), default_status=401)

    if request.user_id and request.user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="user_id does not match authenticated user")

    result = create_chat_room(user_id=authenticated_user_id, title=request.title, auth_token=authorization)
    if isinstance(result, dict) and result.get("id"):
        return result
    _raise_conversation_error(result.get("message", "Failed to create chat room"), default_status=500)

@router.get("/rooms")
def get_rooms(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    include_archived: bool = Query(False, description="Include archived rooms"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """ดึงรายการห้องสนทนาทั้งหมด"""
    try:
        authenticated_user_id = get_authenticated_user_id(authorization)
    except Exception as e:
        _raise_conversation_error(str(e), default_status=401)

    if user_id and user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="cannot access another user's rooms")

    effective_user_id = user_id or authenticated_user_id
    result = get_chat_rooms(user_id=effective_user_id, include_archived=include_archived, auth_token=authorization)
    if isinstance(result, list):
        return result
    _raise_conversation_error(result.get("message", "Failed to fetch chat rooms"), default_status=500)

@router.get("/rooms/{room_id}")
def get_room(room_id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    """ดึงข้อมูลห้องสนทนาตาม ID"""
    result = get_chat_room_by_id(room_id, auth_token=authorization)
    if isinstance(result, dict) and result.get("id"):
        return result
    # If service returns an error message, map it to 404 when appropriate
    message = result.get("message") if isinstance(result, dict) else None
    if message and "not found" in message.lower():
        raise HTTPException(status_code=404, detail=message)
    _raise_conversation_error(message or "Failed to fetch chat room", default_status=500)

@router.put("/rooms/{room_id}")
def update_room(room_id: int, request: UpdateRoomRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    """อัพเดทข้อมูลห้องสนทนา"""
    result = update_chat_room(room_id=room_id, title=request.title, is_archive=request.is_archive, auth_token=authorization)
    if isinstance(result, dict) and result.get("id"):
        return result
    _raise_conversation_error(result.get("message", "Failed to update chat room"), default_status=500)

@router.delete("/rooms/{room_id}")
def delete_room(room_id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    """ลบห้องสนทนา"""
    result = delete_chat_room(room_id, auth_token=authorization)
    if isinstance(result, dict) and result.get("message") and "deleted" in result.get("message").lower():
        return {"detail": result.get("message")}
    _raise_conversation_error(result.get("message", "Failed to delete chat room"), default_status=500)

@router.delete("/rooms/by-user/{user_id}")
def delete_rooms_by_user(user_id: str, authorization: Optional[str] = Header(None, alias="Authorization")):
    """ลบห้องสนทนาทั้งหมดของผู้ใช้"""
    try:
        authenticated_user_id = get_authenticated_user_id(authorization)
    except Exception as e:
        _raise_conversation_error(str(e), default_status=401)

    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="cannot delete another user's rooms")

    result = delete_chat_rooms_by_user(authenticated_user_id, auth_token=authorization)
    if isinstance(result, dict) and result.get("message") and ("deleted" in result.get("message").lower() or result.get("deleted_room_count") is not None):
        return result
    _raise_conversation_error(result.get("message", "Failed to delete user chat rooms"), default_status=500)

# ===================== Messages =====================

@router.post("/rooms/{room_id}/messages")
def add_message_to_room(
    room_id: int,
    request: AddMessageRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """เพิ่มข้อความในห้องสนทนา"""
    result = add_message(
        room_id=room_id,
        sender=request.sender,
        message=request.message,
        metadata=request.metadata,
        auth_token=authorization,
    )
    # inserted message should have an `id`
    if isinstance(result, dict) and result.get("id"):
        return result
    _raise_conversation_error(result.get("message", "Failed to add message"), default_status=500)

@router.get("/rooms/{room_id}/messages")
def get_room_messages(
    room_id: int,
    limit: int = Query(100, description="Maximum number of messages to return"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """ดึงข้อความทั้งหมดในห้องสนทนา"""
    result = get_messages(room_id=room_id, limit=limit, auth_token=authorization)
    if isinstance(result, list):
        return result
    _raise_conversation_error(result.get("message", "Failed to fetch messages"), default_status=500)

@router.get("/rooms/{room_id}/history")
def get_room_history(room_id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    """ดึงประวัติการสนทนาในรูปแบบที่พร้อมใช้กับ LLM"""
    result = get_chat_history(room_id, auth_token=authorization)
    if isinstance(result, list):
        return result
    _raise_conversation_error("Failed to fetch chat history", default_status=500)
