from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from app.core.auth import get_current_user
from app.services.database_service import database_service

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get dashboard statistics for the current user.
    
    Returns:
    - total_sessions: Number of analysis sessions
    - total_models: Number of trained models
    - total_predictions: Number of predictions made
    - recent_sessions: List of recent sessions
    - recent_models: List of recent models
    """
    try:
        stats = await database_service.get_dashboard_stats(current_user["id"])
        return {
            "message": "Dashboard stats retrieved successfully",
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/models")
async def get_user_models(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's trained models with pagination.
    
    Args:
    - limit: Number of models to return (max 100)
    - offset: Number of models to skip
    
    Returns:
    - models: List of trained models
    - total: Total number of models
    """
    try:
        models = await database_service.get_user_models(current_user["id"])
        
        # Apply pagination
        total = len(models)
        paginated_models = models[offset:offset + limit]
        
        return {
            "message": "User models retrieved successfully",
            "success": True,
            "models": paginated_models,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user models: {str(e)}")

@router.get("/sessions")
async def get_user_sessions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's analysis sessions with pagination.
    
    Args:
    - limit: Number of sessions to return (max 100)
    - offset: Number of sessions to skip
    
    Returns:
    - sessions: List of analysis sessions
    - total: Total number of sessions
    """
    try:
        sessions = await database_service.get_user_sessions(current_user["id"])
        
        # Apply pagination
        total = len(sessions)
        paginated_sessions = sessions[offset:offset + limit]
        
        return {
            "message": "User sessions retrieved successfully",
            "success": True,
            "sessions": paginated_sessions,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user sessions: {str(e)}")

@router.get("/predictions")
async def get_prediction_history(
    model_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's prediction history with optional model filtering and pagination.
    
    Args:
    - model_id: Optional model ID to filter predictions
    - limit: Number of predictions to return (max 100)
    - offset: Number of predictions to skip
    
    Returns:
    - predictions: List of predictions
    - total: Total number of predictions
    """
    try:
        predictions = await database_service.get_prediction_history(current_user["id"], model_id)
        
        # Apply pagination
        total = len(predictions)
        paginated_predictions = predictions[offset:offset + limit]
        
        return {
            "message": "Prediction history retrieved successfully",
            "success": True,
            "predictions": paginated_predictions,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prediction history: {str(e)}")

@router.get("/sessions/{session_id}")
async def get_session_details(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed information about a specific analysis session.
    
    Args:
    - session_id: The session ID to retrieve
    
    Returns:
    - session: Detailed session information
    """
    try:
        session = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "message": "Session details retrieved successfully",
            "success": True,
            "session": session
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session details: {str(e)}")

@router.get("/models/{model_id}")
async def get_model_details(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed information about a specific trained model.
    
    Args:
    - model_id: The model ID to retrieve
    
    Returns:
    - model: Detailed model information
    """
    try:
        model = await database_service.get_model_by_id(model_id, current_user["id"])
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return {
            "message": "Model details retrieved successfully",
            "success": True,
            "model": model
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model details: {str(e)}")

@router.get("/models/{model_id}/features")
async def get_model_features(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get feature information for a specific trained model.
    
    Args:
    - model_id: The model ID to retrieve features for
    
    Returns:
    - features: Model feature information
    """
    try:
        model = await database_service.get_model_by_id(model_id, current_user["id"])
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get the session ID from the model
        session_id = None
        if 'analysis_sessions' in model and model['analysis_sessions']:
            session_id = model['analysis_sessions']['session_id']
        elif 'text_session_id' in model:
            session_id = model['text_session_id']
        
        if not session_id:
            raise HTTPException(status_code=404, detail="Session not found for this model")
        
        # Get data profile from the session
        from app.services.data_service import data_service
        try:
            profile_data = data_service.profile_data(session_id)
            schema = profile_data['schema']
        except Exception as e:
            # Fallback: try to get from database metadata
            session_info = await database_service.get_session_by_id(session_id, current_user["id"])
            if not session_info or 'metadata' not in session_info:
                raise HTTPException(status_code=404, detail="Data profile not found")
            
            # Try to get schema from metadata
            metadata = session_info.get('metadata', {})
            if 'data_insights' not in metadata:
                raise HTTPException(status_code=404, detail="Data profile not found")
            
            # Create basic schema from available data
            schema = []
            # This is a fallback - we'll create basic feature info
            feature_importance = model.get('feature_importance', {})
            for feature_name in feature_importance.keys():
                schema.append({
                    'name': feature_name,
                    'dtype': 'numerical',  # Default assumption
                    'null_count': 0,
                    'null_percentage': 0.0,
                    'unique_count': 0,
                    'is_constant': False,
                    'is_high_cardinality': False,
                    'sample_values': []
                })
        
        # Get target column and excluded columns
        target_column = model.get('target_column', '')
        excluded_columns = model.get('hyperparameters', {}).get('excluded_columns', [])
        
        # Filter schema to only include features used in the model
        # (exclude target column and excluded columns)
        model_features = []
        for column in schema:
            if (column['name'] != target_column and 
                column['name'] not in excluded_columns):
                
                # Determine data type for frontend
                dtype = column['dtype']
                if dtype in ['int64', 'float64', 'int32', 'float32']:
                    frontend_dtype = 'numerical'
                else:
                    frontend_dtype = 'categorical'
                
                model_features.append({
                    'name': column['name'],
                    'dtype': frontend_dtype,
                    'unique_count': column.get('unique_count', 0),
                    'sample_values': column.get('sample_values', [])[:5],  # Limit to 5 sample values
                    'null_percentage': column.get('null_percentage', 0.0)
                })
        
        # Sort features by importance if available
        feature_importance = model.get('feature_importance', {})
        if feature_importance:
            # Sort by importance (descending)
            model_features.sort(
                key=lambda x: feature_importance.get(x['name'], 0),
                reverse=True
            )
        
        return {
            "message": "Model features retrieved successfully",
            "success": True,
            "model_id": model_id,
            "target_column": target_column,
            "features": model_features
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model features: {str(e)}")
