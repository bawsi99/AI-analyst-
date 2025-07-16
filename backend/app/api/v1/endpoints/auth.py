from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
from app.core.auth import get_current_user
from app.core.supabase import get_supabase_anon_client
from app.services.database_service import database_service
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register")
async def register_user(request: RegisterRequest):
    """
    Register a new user
    """
    try:
        logger.info(f"Attempting to register user: {request.email}")
        # Use anon client for auth operations
        supabase_auth = get_supabase_anon_client()
        
        # Create user with Supabase Auth
        auth_response = supabase_auth.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name
                }
            }
        })
        
        logger.info(f"Supabase auth response: {auth_response}")
        
        if auth_response.user:
            # Ensure user profile exists in database using service role client
            user_id = auth_response.user.id
            email = auth_response.user.email
            
            # Try to ensure user profile exists
            try:
                profile = await database_service.ensure_user_profile(user_id, email, request.full_name)
                logger.info(f"User profile ensured during registration: {profile is not None}")
            except Exception as profile_error:
                logger.warning(f"Failed to ensure user profile during registration: {profile_error}")
                # Continue with registration even if profile creation fails
            
            # Check if email confirmation is required
            if not auth_response.user.email_confirmed_at:
                return {
                    "message": "User registered successfully. Please check your email to confirm your account before logging in.",
                    "user": {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "email_confirmed": False
                    },
                    "access_token": None,
                    "refresh_token": None,
                    "requires_email_confirmation": True
                }
            else:
                return {
                    "message": "User registered successfully",
                    "user": {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "email_confirmed": True
                    },
                    "access_token": auth_response.session.access_token if auth_response.session else None,
                    "refresh_token": auth_response.session.refresh_token if auth_response.session else None,
                    "requires_email_confirmation": False
                }
        else:
            logger.error("Registration failed: No user returned from Supabase")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login")
async def login_user(request: LoginRequest):
    """
    Login user and return session
    """
    try:
        logger.info(f"Attempting to login user: {request.email}")
        # Use anon client for auth operations
        supabase_auth = get_supabase_anon_client()
        
        # Sign in with Supabase Auth
        auth_response = supabase_auth.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        logger.info(f"Supabase login response: {auth_response}")
        
        if auth_response.user and auth_response.session:
            # Ensure user profile exists in database using service role client
            user_id = auth_response.user.id
            email = auth_response.user.email
            full_name = auth_response.user.user_metadata.get('full_name') if auth_response.user.user_metadata else None
            
            # Try to ensure user profile exists
            try:
                profile = await database_service.ensure_user_profile(user_id, email, full_name)
                logger.info(f"User profile ensured: {profile is not None}")
            except Exception as profile_error:
                logger.warning(f"Failed to ensure user profile: {profile_error}")
                # Continue with login even if profile creation fails
            
            return {
                "message": "Login successful",
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "email_confirmed": auth_response.user.email_confirmed_at is not None
                },
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token
            }
        else:
            logger.error("Login failed: Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        error_message = str(e)
        
        # Provide more specific error messages
        if "Email not confirmed" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not confirmed. Please check your email and click the confirmation link before logging in."
            )
        elif "Invalid login credentials" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Login failed: {error_message}"
            )

@router.post("/resend-confirmation")
async def resend_confirmation_email(request: LoginRequest):
    """
    Resend email confirmation
    """
    try:
        logger.info(f"Attempting to resend confirmation email: {request.email}")
        # Use anon client for auth operations
        supabase_auth = get_supabase_anon_client()
        
        # Resend confirmation email
        auth_response = supabase_auth.auth.resend_signup_confirmation({
            "email": request.email
        })
        
        return {
            "message": "Confirmation email sent successfully. Please check your email."
        }
        
    except Exception as e:
        logger.error(f"Resend confirmation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to resend confirmation email: {str(e)}"
        )

@router.post("/logout")
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout user
    """
    try:
        # Use anon client for auth operations
        supabase_auth = get_supabase_anon_client()
        supabase_auth.auth.sign_out()
        
        return {
            "message": "Logout successful"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/profile")
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile
    """
    try:
        # Try to get profile from database first
        profile = await database_service.get_user_profile(current_user["id"])
        
        if profile:
            return {
                "id": profile["id"],
                "email": profile["email"],
                "full_name": profile.get("full_name"),
                "avatar_url": profile.get("avatar_url"),
                "created_at": profile["created_at"]
            }
        else:
            # If no profile in database, try to create one
            try:
                user_id = current_user["id"]
                email = current_user["email"]
                full_name = current_user.get("full_name")
                
                profile = await database_service.ensure_user_profile(user_id, email, full_name)
                
                if profile:
                    return {
                        "id": profile["id"],
                        "email": profile["email"],
                        "full_name": profile.get("full_name"),
                        "avatar_url": profile.get("avatar_url"),
                        "created_at": profile["created_at"]
                    }
            except Exception as create_error:
                logger.warning(f"Failed to create user profile: {create_error}")
            
            # If profile creation fails, return basic profile from auth data
            return {
                "id": current_user["id"],
                "email": current_user["email"],
                "full_name": current_user.get("full_name"),
                "avatar_url": None,
                "created_at": current_user.get("created_at", "")
            }
            
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        # If database service fails, return basic profile from auth data
        return {
            "id": current_user["id"],
            "email": current_user["email"],
            "full_name": current_user.get("full_name"),
            "avatar_url": None,
            "created_at": current_user.get("created_at", "")
        }

@router.put("/profile")
async def update_profile(
    profile_update: dict,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    from app.models.schemas import UserProfileUpdate
    """
    Update current user profile
    """
    try:
        update_data = profile_update.dict(exclude_unset=True)
        success = await database_service.update_user_profile(current_user["id"], update_data)
        
        if success:
            return {
                "message": "Profile updated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token
    """
    try:
        supabase = get_supabase_client()
        
        # Refresh the session
        auth_response = supabase.auth.refresh_session(request.refresh_token)
        
        if auth_response.session:
            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        ) 