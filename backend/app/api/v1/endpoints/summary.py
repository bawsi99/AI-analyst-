from app.services.data_service import data_service
from app.services.summary_service import summary_service

router = APIRouter()

@router.get("/{session_id}", response_model=SummaryResponse)
async def get_summary(
    session_id: str,
    model_id: str = Query(None, description="Optional model ID to include model summary")
):
    """
    Get natural language summary of data and model insights.
    
    - **session_id**: Session ID from upload endpoint
    - **model_id**: Optional model ID from training endpoint
    - Returns comprehensive summary with insights and recommendations
    """
    try:
        # Check if session exists
        session_info = data_service.get_session_info(session_id)
        
        # Generate complete summary
        summary_data = summary_service.generate_complete_summary(session_id, model_id)
        
        return SummaryResponse(
            message="Summary generated successfully",
            session_id=session_id,
            data_summary=summary_data['data_summary'],
            model_summary=summary_data['model_summary'],
            key_insights=summary_data['key_insights'],
            recommendations=summary_data['recommendations']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        ) 