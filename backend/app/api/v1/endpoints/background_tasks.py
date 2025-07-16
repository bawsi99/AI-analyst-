from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from app.models.schemas import TrainingRequest, BackgroundTaskResponse, TaskStatusResponse
from app.services.data_service import data_service
from app.services.database_service import database_service
from app.tasks import (
    train_model_task, 
    generate_ai_analysis_task, 
    profile_data_task,
    batch_predict_task,
    cleanup_session_task,
    generate_summary_task
)
from app.core.auth import get_current_user
from typing import Dict, Any, List
import uuid

router = APIRouter()

@router.post("/train/{session_id}", response_model=BackgroundTaskResponse)
async def train_model_background(
    session_id: str, 
    request: TrainingRequest, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start background ML model training task.
    
    - **session_id**: Session ID from upload endpoint
    - **target_column**: Column to predict
    - **model_type**: classification or regression
    - **algorithm**: random_forest, xgboost, logistic_regression (optional)
    - Returns task ID for monitoring progress
    """
    try:
        # Validate session exists
        session_info = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Validate model_type
        if request.model_type not in ['classification', 'regression']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model_type: {request.model_type}. Must be 'classification' or 'regression'"
            )
        
        # Prepare training parameters
        training_params = {
            'target_column': request.target_column,
            'model_type': request.model_type,
            'algorithm': request.algorithm,
            'excluded_columns': request.excluded_columns or []
        }
        
        # Start background task
        task = train_model_task.delay(
            session_id=session_id,
            user_id=current_user["id"],
            training_params=training_params
        )
        
        # Update session status to training
        await database_service.update_session_status(
            session_id=session_id,
            user_id=current_user["id"],
            status='training',
            metadata={'task_id': task.id}
        )
        
        return BackgroundTaskResponse(
            message="Model training started in background",
            task_id=task.id,
            task_type="model_training",
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting training task: {str(e)}"
        )

@router.post("/ai-analysis/{session_id}", response_model=BackgroundTaskResponse)
async def generate_ai_analysis_background(
    session_id: str,
    model_id: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start background AI analysis task using Gemini LLM.
    
    - **session_id**: Session ID from upload endpoint
    - **model_id**: Optional model ID from training endpoint
    - Returns task ID for monitoring progress
    """
    try:
        # Validate session exists
        session_info = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Start background task
        task = generate_ai_analysis_task.delay(
            session_id=session_id,
            user_id=current_user["id"],
            model_id=model_id
        )
        
        return BackgroundTaskResponse(
            message="AI analysis started in background",
            task_id=task.id,
            task_type="ai_analysis",
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting AI analysis task: {str(e)}"
        )

@router.post("/profile/{session_id}", response_model=BackgroundTaskResponse)
async def profile_data_background(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start background data profiling task.
    
    - **session_id**: Session ID from upload endpoint
    - Returns task ID for monitoring progress
    """
    try:
        # Validate session exists
        session_info = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Start background task
        task = profile_data_task.delay(
            session_id=session_id,
            user_id=current_user["id"]
        )
        
        return BackgroundTaskResponse(
            message="Data profiling started in background",
            task_id=task.id,
            task_type="data_profiling",
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting data profiling task: {str(e)}"
        )

@router.post("/predict/{model_id}/batch", response_model=BackgroundTaskResponse)
async def batch_predict_background(
    model_id: str,
    data: List[Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start background batch prediction task.
    
    - **model_id**: Model ID from training endpoint
    - **data**: List of dictionaries with feature values
    - Returns task ID for monitoring progress
    """
    try:
        # Validate model exists
        model_info = await database_service.get_model_by_id(model_id, current_user["id"])
        if not model_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        # Start background task
        task = batch_predict_task.delay(
            model_id=model_id,
            user_id=current_user["id"],
            data=data
        )
        
        return BackgroundTaskResponse(
            message="Batch prediction started in background",
            task_id=task.id,
            task_type="batch_prediction",
            model_id=model_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting batch prediction task: {str(e)}"
        )

@router.post("/summary/{session_id}", response_model=BackgroundTaskResponse)
async def generate_summary_background(
    session_id: str,
    model_id: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start background summary generation task.
    
    - **session_id**: Session ID from upload endpoint
    - **model_id**: Optional model ID from training endpoint
    - Returns task ID for monitoring progress
    """
    try:
        # Validate session exists
        session_info = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Start background task
        task = generate_summary_task.delay(
            session_id=session_id,
            user_id=current_user["id"],
            model_id=model_id
        )
        
        return BackgroundTaskResponse(
            message="Summary generation started in background",
            task_id=task.id,
            task_type="summary_generation",
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting summary generation task: {str(e)}"
        )

@router.post("/cleanup/{session_id}", response_model=BackgroundTaskResponse)
async def cleanup_session_background(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start background session cleanup task.
    
    - **session_id**: Session ID to clean up
    - Returns task ID for monitoring progress
    """
    try:
        # Validate session exists
        session_info = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Start background task
        task = cleanup_session_task.delay(session_id=session_id)
        
        return BackgroundTaskResponse(
            message="Session cleanup started in background",
            task_id=task.id,
            task_type="session_cleanup",
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting cleanup task: {str(e)}"
        )

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a background task.
    
    - **task_id**: Task ID from any background task endpoint
    - Returns task status and result if completed
    """
    try:
        from app.celery import celery
        
        # Get task result
        task_result = celery.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'status': 'Task is pending...'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'status': task_result.info.get('status', ''),
                'progress': task_result.info.get('progress', 0)
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'result': task_result.result
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': task_result.state,
                'error': str(task_result.info)
            }
        
        return TaskStatusResponse(**response)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting task status: {str(e)}"
        ) 