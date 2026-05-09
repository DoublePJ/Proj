import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from supabase.client import ClientOptions

# Lazy-initialized Supabase client. Calling get_supabase_client() will create
# and cache the client on first use. This avoids failing at import time if
# environment variables are not yet available.
_supabase_client: Optional[Client] = None

def _get_supabase_client_direct() -> Client:
    load_dotenv()

    url: Optional[str] = os.environ.get("SUPABASE_URL")
    key: Optional[str] = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    # Load environment variables from .env (if present)
    load_dotenv()

    url: Optional[str] = os.environ.get("SUPABASE_URL")
    key: Optional[str] = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment to use Supabase client")

    print(">>> Initializing Supabase client...")
    _supabase_client = create_client(url, key)
    print(">>> Supabase client initialized")
    return _supabase_client

def get_supabase_client_with_auth(token: str) -> Client:
    """สร้าง Supabase client ที่มีการตั้งค่า token สำหรับการตรวจสอบสิทธิ์"""
    
    load_dotenv()

    url: Optional[str] = os.environ.get("SUPABASE_URL")
    key: Optional[str] = os.environ.get("SUPABASE_KEY")
    
    client = create_client(url, key, options=ClientOptions())
    # supabase-py requires binding JWT to PostgREST session explicitly for RLS.
    client.postgrest.auth(token)
    return client