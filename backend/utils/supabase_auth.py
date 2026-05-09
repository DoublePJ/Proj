from typing import Optional

from database.supabase_client import get_supabase_client, get_supabase_client_with_auth


def normalize_token(auth_token: Optional[str]) -> Optional[str]:
    if not auth_token:
        return None
    if auth_token.lower().startswith("bearer "):
        return auth_token[7:].strip()
    return auth_token


def get_user_client(auth_token: Optional[str]):
    token = normalize_token(auth_token)
    if not token:
        raise ValueError("Missing access token")
    return get_supabase_client_with_auth(token)


def get_authenticated_user_id(auth_token: Optional[str]) -> str:
    token = normalize_token(auth_token)
    if not token:
        raise ValueError("Missing access token")

    user_client = get_supabase_client_with_auth(token)
    auth_user = user_client.auth.get_user(token)

    user = getattr(auth_user, "user", None)
    if user is None and isinstance(auth_user, dict):
        user = auth_user.get("user")

    user_id = getattr(user, "id", None) if user is not None else None
    if user_id is None and isinstance(user, dict):
        user_id = user.get("id")

    if not user_id:
        raise ValueError("Unauthorized: invalid or expired access token")

    return str(user_id)
