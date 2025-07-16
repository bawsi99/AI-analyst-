from fastapi import APIRouter, HTTPException, status, Query
from services.ai_analysis_service import ai_analysis_service
from services.data_service import data_service
from typing import Optional

router = APIRouter()

@router.get("/{session_id}")
async def get_ai_analysis(
    session_id: str,
    model_id: str = Query(None, description="Optional model ID to include model analysis")
):
    """
    Get AI-powered analysis using Gemini LLM.
    
    - **session_id**: Session ID from upload endpoint
    - **model_id**: Optional model ID from training endpoint
    - Returns comprehensive AI analysis with enhanced insights and recommendations
    """
    try:
        # Check if session exists
        session_info = data_service.get_session_info(session_id)
        
        # Check if AI analysis is available
        if not ai_analysis_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI analysis is not available. Please configure the Gemini API key."
            )
        
        # Generate AI analysis
        ai_analysis_data = ai_analysis_service.generate_ai_analysis(session_id, model_id)
        
        return {
            "message": "AI analysis generated successfully",
            "success": True,
            "session_id": session_id,
            "model_id": model_id,
            "ai_analysis": ai_analysis_data['ai_analysis'],
            "enhanced_insights": ai_analysis_data['enhanced_insights'],
            "business_recommendations": ai_analysis_data['business_recommendations'],
            "technical_recommendations": ai_analysis_data['technical_recommendations'],
            "risk_assessment": ai_analysis_data['risk_assessment'],
            "opportunities": ai_analysis_data['opportunities']
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating AI analysis: {str(e)}"
        )

@router.get("/status/health")
async def check_ai_analysis_status():
    """
    Check if AI analysis service is available.
    
    Returns the status of the AI analysis service.
    """
    is_available = ai_analysis_service.is_available()
    
    return {
        "ai_analysis_available": is_available,
        "message": "AI analysis service is available" if is_available else "AI analysis service is not available. Please configure the Gemini API key."
    } 