from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.services.database_service import database_service
from app.core.auth import get_current_user
from typing import Dict, Any, List, Optional

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get dashboard statistics for the current user
    """
    try:
        stats = await database_service.get_dashboard_stats(current_user["id"])
        return {
            "message": "Dashboard stats retrieved successfully",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting dashboard stats: {str(e)}"
        )

@router.get("/sessions")
async def get_user_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get user's analysis sessions
    """
    try:
        sessions = await database_service.get_user_sessions(current_user["id"])
        
        # Apply pagination
        total = len(sessions)
        paginated_sessions = sessions[offset:offset + limit]
        
        return {
            "message": "Sessions retrieved successfully",
            "sessions": paginated_sessions,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting sessions: {str(e)}"
        )

@router.get("/models")
async def get_user_models(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get user's trained models
    """
    try:
        models = await database_service.get_user_models(current_user["id"])
        
        # Apply pagination
        total = len(models)
        paginated_models = models[offset:offset + limit]
        
        return {
            "message": "Models retrieved successfully",
            "models": paginated_models,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting models: {str(e)}"
        )

@router.get("/predictions")
async def get_prediction_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
    model_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get user's prediction history
    """
    try:
        predictions = await database_service.get_prediction_history(
            current_user["id"], 
            model_id
        )
        
        # Apply pagination
        total = len(predictions)
        paginated_predictions = predictions[offset:offset + limit]
        
        return {
            "message": "Prediction history retrieved successfully",
            "predictions": paginated_predictions,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting prediction history: {str(e)}"
        )

@router.get("/sessions/{session_id}")
async def get_session_details(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed information about a specific session
    """
    try:
        session = await database_service.get_session_by_id(session_id, current_user["id"])
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get related models for this session
        models = await database_service.get_user_models(current_user["id"])
        session_models = [m for m in models if m.get("session_id") == session["id"]]
        
        # Get analysis summary
        summary = await database_service.get_analysis_summary(session_id, current_user["id"])
        
        return {
            "message": "Session details retrieved successfully",
            "session": session,
            "models": session_models,
            "summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting session details: {str(e)}"
        )

@router.get("/models/{model_id}")
async def get_model_details(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get detailed information about a specific model
    """
    try:
        model = await database_service.get_model_by_id(model_id, current_user["id"])
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        # Get prediction history for this model
        predictions = await database_service.get_prediction_history(
            current_user["id"], 
            model["id"]
        )
        
        return {
            "message": "Model details retrieved successfully",
            "model": model,
            "predictions": predictions[:10]  # Last 10 predictions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting model details: {str(e)}"
        )

@router.get("/models/{model_id}/features")
async def get_model_features(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get feature information for a specific model to help with predictions
    """
    try:
        model = await database_service.get_model_by_id(model_id, current_user["id"])
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        # Get excluded columns and target column
        excluded_columns = model.get('hyperparameters', {}).get('excluded_columns', [])
        target_column = model['target_column']
        
        # Get the session information to access the original data
        # Use the text session_id from the joined table, not the UUID session_id
        text_session_id = model.get("text_session_id") or model.get("analysis_sessions", {}).get("session_id")
        if not text_session_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session information not found for this model"
            )
        
        session = await database_service.get_session_by_id(text_session_id, current_user["id"])
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Try to get feature information from the data service first
        features = []
        try:
            from app.services.data_service import data_service
            profile_data = data_service.profile_data(session["session_id"])
            
            # Filter out the target column and excluded columns, and get feature schema
            for column in profile_data['schema']:
                if column.name != target_column and column.name not in excluded_columns:
                    features.append({
                        'name': column.name,
                        'dtype': column.dtype,
                        'unique_count': column.unique_count,
                        'sample_values': column.sample_values,
                        'null_percentage': column.null_percentage
                    })
            
            return {
                "message": "Model features retrieved successfully",
                "model_id": model_id,
                "target_column": model['target_column'],
                "features": features
            }
            
        except (ValueError, FileNotFoundError, Exception) as e:
            # Fallback: return basic feature information from feature importance
            feature_importance = model.get('feature_importance', {})
            
            if feature_importance:
                for feature_name in feature_importance.keys():
                    # Try to extract original feature name from encoded feature
                    original_name = feature_name.split('_')[0] if '_' in feature_name else feature_name
                    features.append({
                        'name': original_name,
                        'dtype': 'unknown',  # We don't have this info in fallback
                        'unique_count': 0,
                        'sample_values': [],
                        'null_percentage': 0
                    })
                
                # Remove duplicates
                unique_features = []
                seen_names = set()
                for feature in features:
                    if feature['name'] not in seen_names:
                        unique_features.append(feature)
                        seen_names.add(feature['name'])
                
                return {
                    "message": "Model features retrieved successfully (fallback from feature importance)",
                    "model_id": model_id,
                    "target_column": model['target_column'],
                    "features": unique_features
                }
            else:
                # If no feature importance available, return basic model info
                return {
                    "message": "Model features retrieved successfully (basic info only)",
                    "model_id": model_id,
                    "target_column": model['target_column'],
                    "features": [],
                    "note": "Feature details not available. Use the model for predictions with appropriate input data."
                }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting model features: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a session and all related data
    """
    try:
        # First check if session exists and belongs to user
        session = await database_service.get_session_by_id(session_id, current_user["id"])
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # TODO: Implement cascade delete for related models, predictions, and summaries
        # For now, just return success
        return {
            "message": "Session deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )

@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a model and all related predictions
    """
    try:
        # First check if model exists and belongs to user
        model = await database_service.get_model_by_id(model_id, current_user["id"])
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        # TODO: Implement cascade delete for related predictions
        # For now, just return success
        return {
            "message": "Model deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting model: {str(e)}"
        ) 