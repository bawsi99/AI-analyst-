from app.services.data_service import data_service
from app.services.database_service import database_service
from app.core.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

router = APIRouter()

@router.get("/{session_id}", response_model=dict)
async def get_profile(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    from app.models.schemas import ProfileResponse
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
        
        # Save detailed insights to database
        insights_data = {
            'outliers': profile_data['insights'].outliers,
            'skewness': profile_data['insights'].skewness,
            'correlations': [
                {
                    'column1': corr.column1,
                    'column2': corr.column2,
                    'correlation': corr.correlation,
                    'strength': corr.strength
                } for corr in profile_data['insights'].correlations
            ],
            'imbalanced_columns': profile_data['insights'].imbalanced_columns,
            'data_leakage': profile_data['insights'].data_leakage
        }
        
        await database_service.save_data_insights(session_id, current_user["id"], insights_data)
        
        return {
            "message": "Data profile generated successfully",
            "success": True,
            "session_id": session_id,
            "metadata": profile_data['metadata'],
            "schema": profile_data['schema'],
            "statistics": profile_data['statistics'],
            "insights": profile_data['insights']
        }
        
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