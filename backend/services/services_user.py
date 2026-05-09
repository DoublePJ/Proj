from typing import Optional

from database.supabase_client import get_supabase_client
from utils.supabase_auth import get_user_client
from datetime import datetime

def create_or_update_user(
    user_id: str,
    email: str = None,
    display_name: str = None,
    avatar_url: str = None,
    auth_token: Optional[str] = None,
):
    """สร้างหรืออัพเดท user profile"""
    try:
        user_client = get_user_client(auth_token)
        # ตรวจสอบว่ามี user อยู่แล้วหรือไม่
        existing_user = user_client.table("users").select("*").eq("id", user_id).limit(1).execute()
        
        if existing_user.data and len(existing_user.data) > 0:
            # อัพเดท user ที่มีอยู่แล้ว
            update_data = {
                "updated_at": datetime.now().isoformat()
            }
            
            if display_name is not None:
                update_data["display_name"] = display_name
            
            if avatar_url is not None:
                update_data["avatar_url"] = avatar_url
            
            result = user_client.table("users").update(update_data).eq("id", user_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return {"message": "Failed to update user"}
        else:
            # สร้าง user ใหม่
            user_data = {
                "id": user_id,
                "display_name": display_name or email or "ผู้ใช้",
                "avatar_url": avatar_url,
                "role": "user",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = user_client.table("users").insert(user_data).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return {"message": "Failed to create user"}
    except Exception as e:
        print(f"Error creating/updating user: {e}")
        return {"message": f"Error: {str(e)}"}

def get_user_by_id(user_id: str, auth_token: Optional[str] = None):
    """ดึงข้อมูล user ตาม ID"""
    try:
        user_client = get_user_client(auth_token)
        result = user_client.table("users").select("*").eq("id", user_id).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            result.data[0]["job_description"] = get_supabase_client().table("job").select("description").eq("id", result.data[0].get("job_id")).limit(1).execute().data[0]["description"] if result.data[0].get("job_id") else None
            result.data[0]["job_type_description"] = get_supabase_client().table("job_type").select("description").eq("id", result.data[0].get("job_type_id")).limit(1).execute().data[0]["description"] if result.data[0].get("job_type_id") else None
            return result.data[0]
        return {"message": "User not found"}
    except Exception as e:
        print(f"Error getting user: {e}")
        return {"message": f"Error: {str(e)}"}

def get_or_create_job(description: str):
    """ดึงหรือสร้าง job ตามชื่อ"""
    try:
        if not description:
            return None
        
        # ค้นหา job ที่มีอยู่
        result = get_supabase_client().table("job").select("*").eq("description", description).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        # สร้าง job ใหม่
        new_job = {
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        create_result = get_supabase_client().table("job").insert(new_job).execute()
        
        if create_result.data and len(create_result.data) > 0:
            return create_result.data[0]["id"]
        return None
    except Exception as e:
        print(f"Error getting/creating job: {e}")
        return None

def get_or_create_job_type(description: str):
    """ดึงหรือสร้าง job_type ตามชื่อ"""
    try:
        if not description:
            return None
        
        # ค้นหา job_type ที่มีอยู่
        result = get_supabase_client().table("job_type").select("*").eq("description", description).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        # สร้าง job_type ใหม่
        new_job_type = {
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        create_result = get_supabase_client().table("job_type").insert(new_job_type).execute()
        
        if create_result.data and len(create_result.data) > 0:
            return create_result.data[0]["id"]
        return None
    except Exception as e:
        print(f"Error getting/creating job_type: {e}")
        return None

def update_user_profile(
    user_id: str,
    display_name: str = None,
    avatar_url: str = None,
    detail: str = None,
    date_of_birth: str = None,
    job_description: str = None,
    start_work_date: str = None,
    job_type_description: str = None,
    auth_token: Optional[str] = None,
):
    """อัพเดทข้อมูล user profile"""
    try:
        user_client = get_user_client(auth_token)
        update_data = {
            "updated_at": datetime.now().isoformat()
        }
        
        if display_name is not None:
            update_data["display_name"] = display_name
        
        if avatar_url is not None:
            update_data["avatar_url"] = avatar_url
        
        if detail is not None:
            update_data["detail"] = detail
        
        if date_of_birth is not None:
            update_data["date_of_birth"] = date_of_birth
        
        if start_work_date is not None:
            update_data["start_work_date"] = start_work_date
        
        # Handle job_description
        if job_description is not None:
            job_id = get_or_create_job(job_description)
            if job_id is not None:
                update_data["job_id"] = job_id
        
        # Handle job_type_description
        if job_type_description is not None:
            job_type_id = get_or_create_job_type(job_type_description)
            if job_type_id is not None:
                update_data["job_type_id"] = job_type_id
        
        result = user_client.table("users").update(update_data).eq("id", user_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return {"message": "Failed to update user profile"}
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return {"message": f"Error: {str(e)}"}

def delete_user(user_id: str, auth_token: Optional[str] = None):
    """ลบ user (ควรใช้อย่างระมัดระวัง)"""
    try:
        user_client = get_user_client(auth_token)
        result = user_client.table("users").delete().eq("id", user_id).execute()
        return {"message": "User deleted successfully"}
    except Exception as e:
        print(f"Error deleting user: {e}")
        return {"message": f"Error: {str(e)}"}

def get_all_jobs():
    """ดึงรายชื่อ job ทั้งหมด"""
    try:
        result = get_supabase_client().table("job").select("id, description").order("id").execute()
        if result.data:
            return result.data
        return []
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def get_all_job_types():
    """ดึงรายชื่อ job_type ทั้งหมด"""
    try:
        result = get_supabase_client().table("job_type").select("id, description").order("id").execute()
        if result.data:
            return result.data
        return []
    except Exception as e:
        print(f"Error fetching job types: {e}")
        return []
