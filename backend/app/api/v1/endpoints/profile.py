from fastapi import APIRouter, HTTPException, status
from app.models.schemas import ProfileResponse
from app.services.data_service import data_service

router = APIRouter()

@router.get("/{session_id}", response_model=ProfileResponse)
async def get_profile(session_id: str):
    """
    Get comprehensive data profile for uploaded CSV.
    
    - **session_id**: Session ID from upload endpoint
    - Returns schema, statistics, and insights
    """
    try:
        # Check if session exists
        session_info = data_service.get_session_info(session_id)
        
        # Generate profile
        profile_data = data_service.profile_data(session_id)
        
        return ProfileResponse(
            message="Data profile generated successfully",
            session_id=session_id,
            metadata=profile_data['metadata'],
            schema=profile_data['schema'],
            statistics=profile_data['statistics'],
            insights=profile_data['insights']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating profile: {str(e)}"
        ) 