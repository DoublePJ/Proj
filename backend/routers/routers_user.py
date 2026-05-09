from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.services_user import *
from utils.supabase_auth import get_authenticated_user_id

router = APIRouter(prefix="/users", tags=["users"])

class CreateUserRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UpdateUserRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    detail: Optional[str] = None
    date_of_birth: Optional[str] = None
    job_description: Optional[str] = None
    start_work_date: Optional[str] = None
    job_type_description: Optional[str] = None


def _raise_user_error(message: str, default_status: int = 500):
    lowered = (message or "").lower()
    if "missing access token" in lowered or "unauthorized" in lowered or "invalid or expired access token" in lowered:
        raise HTTPException(status_code=401, detail=message)
    if "permission denied by rls" in lowered or "row-level security" in lowered:
        raise HTTPException(status_code=403, detail=message)
    raise HTTPException(status_code=default_status, detail=message)

# ===================== User Profile =====================

@router.post("/")
def create_user(request: CreateUserRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    """สร้างหรืออัพเดท user profile"""
    try:
        authenticated_user_id = get_authenticated_user_id(authorization)
    except Exception as e:
        _raise_user_error(str(e), default_status=401)

    if request.user_id and request.user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="user_id does not match authenticated user")

    result = create_or_update_user(
        user_id=authenticated_user_id,
        email=request.email,
        display_name=request.display_name,
        avatar_url=request.avatar_url,
        auth_token=authorization,
    )
    if isinstance(result, dict) and result.get("id"):
        return result
    _raise_user_error(result.get("message", "Failed to create/update user"), default_status=500)

@router.get("/{user_id}")
def get_user(user_id: str, authorization: Optional[str] = Header(None, alias="Authorization")):
    """ดึงข้อมูล user ตาม ID"""
    try:
        authenticated_user_id = get_authenticated_user_id(authorization)
    except Exception as e:
        _raise_user_error(str(e), default_status=401)

    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="cannot access another user's profile")

    result = get_user_by_id(user_id, auth_token=authorization)
    if isinstance(result, dict) and result.get("id"):
        return result
    detail = result.get("message", "User not found")
    if detail == "User not found":
        raise HTTPException(status_code=404, detail=detail)
    _raise_user_error(detail, default_status=500)

@router.put("/{user_id}")
def update_user(user_id: str, request: UpdateUserRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    """อัพเดทข้อมูล user profile"""
    try:
        authenticated_user_id = get_authenticated_user_id(authorization)
    except Exception as e:
        _raise_user_error(str(e), default_status=401)

    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="cannot update another user's profile")

    result = update_user_profile(
        user_id=authenticated_user_id,
        display_name=request.display_name,
        avatar_url=request.avatar_url,
        detail=request.detail,
        date_of_birth=request.date_of_birth,
        job_description=request.job_description,
        start_work_date=request.start_work_date,
        job_type_description=request.job_type_description,
        auth_token=authorization,
    )
    if isinstance(result, dict) and result.get("id"):
        return result
    _raise_user_error(result.get("message", "Failed to update user profile"), default_status=500)

@router.delete("/{user_id}")
def delete_user_profile(user_id: str, authorization: Optional[str] = Header(None, alias="Authorization")):
    """ลบ user profile"""
    try:
        authenticated_user_id = get_authenticated_user_id(authorization)
    except Exception as e:
        _raise_user_error(str(e), default_status=401)

    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="cannot delete another user's profile")

    result = delete_user(authenticated_user_id, auth_token=authorization)
    if isinstance(result, dict) and result.get("message") and "deleted" in result.get("message").lower():
        return {"detail": result.get("message")}
    _raise_user_error(result.get("message", "Failed to delete user"), default_status=500)

# ===================== Job & Job Type Options =====================

@router.get("/options/jobs")
def get_jobs():
    """ดึงรายชื่อ job ทั้งหมด"""
    return get_all_jobs()

@router.get("/options/job-types")
def get_job_types():
    """ดึงรายชื่อ job_type ทั้งหมด"""
    return get_all_job_types()