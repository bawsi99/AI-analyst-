from supabase import create_client, Client
from app.core.config import settings
import os

# Initialize Supabase client with service role key for backend operations
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY  # Use service role key for backend operations
)

def get_supabase_client() -> Client:
    """Get Supabase client instance with service role permissions"""
    return supabase

def get_supabase_anon_client() -> Client:
    """Get Supabase client instance with anon key for user operations"""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )

def get_user_id_from_token(token: str) -> str:
    """Extract user ID from JWT token"""
    try:
        # Use anon client for token verification
        anon_client = get_supabase_anon_client()
        user = anon_client.auth.get_user(token)
        return user.user.id
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")

def verify_user_session(token: str) -> dict:
    """Verify user session and return user info"""
    try:
        # Use anon client for token verification
        anon_client = get_supabase_anon_client()
        user = anon_client.auth.get_user(token)
        return {
            "id": user.user.id,
            "email": user.user.email,
            "created_at": user.user.created_at
        }
    except Exception as e:
        raise ValueError(f"Invalid session: {str(e)}") 