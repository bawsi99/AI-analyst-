from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from app.models.schemas import UploadResponse
from app.services.data_service import data_service
from app.services.database_service import database_service
from app.core.config import settings
from app.core.auth import get_current_user
from typing import Dict, Any
import os

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Upload a CSV file for analysis.
    
    - **file**: CSV file to upload (max 50MB)
    - Returns session ID for further API access
    """
    # Validate file type
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
        )
    
    try:
        # Ensure user profile exists before creating analysis session
        user_id = current_user["id"]
        email = current_user["email"]
        full_name = current_user.get("full_name")
        
        # Try to ensure user profile exists
        try:
            profile = await database_service.ensure_user_profile(user_id, email, full_name)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile. Please try logging in again."
                )
        except Exception as profile_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User profile error: {str(profile_error)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size after reading
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )
        
        # Save file and get session ID
        session_id = data_service.save_uploaded_file(content, file.filename)
        
        # Save session to database
        session_data = {
            'session_id': session_id,
            'filename': file.filename,
            'file_path': f"uploads/{session_id}/{file.filename}",
            'file_size': len(content),
            'metadata': {
                'original_filename': file.filename,
                'content_type': file.content_type
            }
        }
        
        await database_service.create_analysis_session(
            user_id=user_id,
            session_data=session_data
        )
        print(f"DEBUG: Created session in DB with session_id={session_id}, user_id={user_id}")
        
        return UploadResponse(
            message="File uploaded successfully",
            session_id=session_id,
            filename=file.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        ) 