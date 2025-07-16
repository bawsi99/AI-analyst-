from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from app.core.auth import get_current_user
from app.services.ai_analysis_service import ai_analysis_service
from app.services.database_service import database_service
from app.models.schemas import AIAnalysisResponse, AIAnalysisStatusResponse

router = APIRouter()

@router.get("/{session_id}", response_model=AIAnalysisResponse)
async def get_ai_analysis(
    session_id: str,
    model_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get AI-powered analysis for a session.
    
    Args:
    - session_id: The session ID to analyze
    - model_id: Optional model ID to include model-specific insights
    
    Returns:
    - AI analysis with enhanced insights, recommendations, and assessments
    """
    try:
        # Verify session belongs to user
        session = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate AI analysis
        ai_analysis_data = ai_analysis_service.generate_ai_analysis(session_id, model_id)
        
        return AIAnalysisResponse(
            message="AI analysis generated successfully",
            success=True,
            session_id=session_id,
            model_id=model_id,
            ai_analysis=ai_analysis_data['ai_analysis'],
            enhanced_insights=ai_analysis_data['enhanced_insights'],
            business_recommendations=ai_analysis_data['business_recommendations'],
            technical_recommendations=ai_analysis_data['technical_recommendations'],
            risk_assessment=ai_analysis_data['risk_assessment'],
            opportunities=ai_analysis_data['opportunities']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI analysis: {str(e)}")

@router.get("/status/health", response_model=AIAnalysisStatusResponse)
async def check_ai_analysis_status():
    """
    Check if AI analysis service is available and healthy.
    
    Returns:
    - Status of AI analysis service availability
    """
    try:
        is_available = ai_analysis_service.is_available()
        
        return AIAnalysisStatusResponse(
            ai_analysis_available=is_available,
            message="AI analysis service is available" if is_available else "AI analysis service is not available. Please configure the Gemini API key."
        )
        
    except Exception as e:
        return AIAnalysisStatusResponse(
            ai_analysis_available=False,
            message=f"AI analysis service error: {str(e)}"
        )
