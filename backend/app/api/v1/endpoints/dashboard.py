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

@router.get("/debug/user-info")
async def debug_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Debug endpoint to check user authentication and database access.
    """
    try:
        user_id = current_user["id"]
        email = current_user.get("email", "unknown")
        
        # Try to get user profile from database
        profile = await database_service.get_user_profile(user_id)
        
        # Try to get user's sessions
        sessions = await database_service.get_user_sessions(user_id)
        
        # Try to get user's models
        models = await database_service.get_user_models(user_id)
        
        return {
            "message": "User debug info retrieved successfully",
            "success": True,
            "auth_info": {
                "user_id": user_id,
                "email": email,
                "auth_data": current_user
            },
            "database_info": {
                "profile_exists": profile is not None,
                "profile": profile,
                "sessions_count": len(sessions),
                "models_count": len(models),
                "sessions": sessions[:3],  # First 3 sessions
                "models": models[:3]  # First 3 models
            }
        }
    except Exception as e:
        return {
            "message": "Error getting user debug info",
            "success": False,
            "error": str(e),
            "auth_info": {
                "user_id": current_user.get("id", "unknown"),
                "email": current_user.get("email", "unknown"),
                "auth_data": current_user
            }
        }

def infer_feature_schema_from_importance(feature_importance: dict) -> list:
    """
    Given a feature_importance dict, return a schema list with correct dtype and all possible categories for categorical features.
    """
    # First, collect all base columns and their categories
    base_to_categories = {}
    processed_base_columns = set()
    
    for feature_name in feature_importance.keys():
        if '_' in feature_name and not feature_name.replace('_', '').replace('.', '').isdigit():
            base_column = feature_name.split('_')[0]
            category_value = '_'.join(feature_name.split('_')[1:])
            base_to_categories.setdefault(base_column, set()).add(category_value)
        else:
            # This is a numerical feature, add it directly
            base_to_categories[feature_name] = set()
    
    schema = []
    for feature_name in feature_importance.keys():
        dtype = 'numerical'  # Default assumption
        sample_values = []
        display_name = feature_name  # Default to original name
        
        # Check if this is a one-hot encoded categorical feature
        if '_' in feature_name and not feature_name.replace('_', '').replace('.', '').isdigit():
            base_column = feature_name.split('_')[0]
            
            # Only process this feature if we haven't already processed this base column
            if base_column not in processed_base_columns:
                dtype = 'categorical'
                display_name = base_column  # Use base column name for display
                # All categories for this base column
                sample_values = sorted(list(base_to_categories.get(base_column, [])))
                processed_base_columns.add(base_column)
                
                # For grouped categorical features, use the base column name as the name
                schema.append({
                    'name': base_column,  # Use base column name for grouped features
                    'display_name': display_name,  # Add display name for frontend
                    'dtype': dtype,
                    'null_count': 0,
                    'null_percentage': 0.0,
                    'unique_count': len(sample_values) if sample_values else 0,
                    'is_constant': False,
                    'is_high_cardinality': False,
                    'sample_values': sample_values
                })
            else:
                # Skip this feature as we've already processed the base column
                continue
        else:
            # This is a numerical feature
            if feature_name not in processed_base_columns:
                processed_base_columns.add(feature_name)
                
                schema.append({
                    'name': feature_name,  # Keep original name for numerical features
                    'display_name': display_name,  # Add display name for frontend
                    'dtype': dtype,
                    'null_count': 0,
                    'null_percentage': 0.0,
                    'unique_count': len(sample_values) if sample_values else 0,
                    'is_constant': False,
                    'is_high_cardinality': False,
                    'sample_values': sample_values
                })
            else:
                # Skip duplicate numerical features
                continue
    
    return schema

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
        print(f"DEBUG: Features endpoint called - model_id={model_id}, user_id={current_user['id']}")
        
        # First try to get model with user_id
        model = await database_service.get_model_by_id(model_id, current_user["id"])
        
        # If not found, try without user_id constraint (for debugging)
        if not model:
            print(f"DEBUG: Model not found with user_id - trying without user constraint")
            try:
                # Try to get model without user constraint to see if it exists
                supabase = database_service._ensure_supabase_client()
                response = supabase.table('trained_models').select('*, analysis_sessions(file_name, session_id)').eq('model_id', model_id).execute()
                if response.data:
                    print(f"DEBUG: Model exists but not for this user - found {len(response.data)} models")
                    print(f"DEBUG: Model user_id: {response.data[0].get('user_id')}")
                    print(f"DEBUG: Current user_id: {current_user['id']}")
                else:
                    print(f"DEBUG: Model does not exist at all in database")
            except Exception as e:
                print(f"DEBUG: Error checking model without user constraint: {e}")
            
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        print(f"DEBUG: Model found - {model}")
        
        # Get the session ID from the model
        session_id = None
        if 'analysis_sessions' in model and model['analysis_sessions']:
            session_id = model['analysis_sessions']['session_id']
            print(f"DEBUG: Session ID from analysis_sessions: {session_id}")
        elif 'text_session_id' in model:
            session_id = model['text_session_id']
            print(f"DEBUG: Session ID from text_session_id: {session_id}")
        
        if not session_id:
            print(f"DEBUG: No session ID found in model")
            raise HTTPException(status_code=404, detail="Session not found for this model")
        
        # Get session info from database
        session_info = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session_info:
            print(f"DEBUG: Session not found - session_id={session_id}, user_id={current_user['id']}")
            # Try to get session without user constraint for debugging
            try:
                supabase = database_service._ensure_supabase_client()
                response = supabase.table('analysis_sessions').select('*').eq('session_id', session_id).execute()
                if response.data:
                    print(f"DEBUG: Session exists but not for this user - found {len(response.data)} sessions")
                    print(f"DEBUG: Session user_id: {response.data[0].get('user_id')}")
                    print(f"DEBUG: Current user_id: {current_user['id']}")
                else:
                    print(f"DEBUG: Session does not exist at all in database")
            except Exception as e:
                print(f"DEBUG: Error checking session without user constraint: {e}")
            
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
        
        print(f"DEBUG: Session found - {session_info}")
        
        # Get schema from session metadata
        metadata = session_info.get('metadata', {})
        feature_importance = model.get('feature_importance', {})
        if 'data_insights' not in metadata:
            # Try to get from data_insights table
            data_insights = await database_service.get_data_insights(session_id, current_user["id"])
            if not data_insights:
                print(f"DEBUG: No data insights found - creating basic schema from feature importance")
                schema = infer_feature_schema_from_importance(feature_importance)
            else:
                print(f"DEBUG: Data insights found from table")
                schema = infer_feature_schema_from_importance(feature_importance)
        else:
            print(f"DEBUG: Data insights found in metadata")
            schema = infer_feature_schema_from_importance(feature_importance)
        
        # Get target column and excluded columns
        target_column = model.get('target_column', '')
        excluded_columns = model.get('hyperparameters', {}).get('excluded_columns', [])
        
        print(f"DEBUG: Target column: {target_column}, Excluded columns: {excluded_columns}")
        
        # Filter schema to only include features used in the model
        # (exclude target column and excluded columns)
        model_features = []
        for column in schema:
            if (column['name'] != target_column and 
                column['name'] not in excluded_columns):
                
                # Use the data type from the schema (already frontend-friendly)
                frontend_dtype = column['dtype']
                
                model_features.append({
                    'name': column['name'],
                    'display_name': column.get('display_name', column['name']),  # Use display_name if available
                    'dtype': frontend_dtype,
                    'unique_count': column.get('unique_count', 0),
                    'sample_values': column.get('sample_values', [])[:5],  # Limit to 5 sample values
                    'null_percentage': column.get('null_percentage', 0.0)
                })
        
        print(f"DEBUG: Model features count: {len(model_features)}")
        
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
        print(f"DEBUG: Unexpected error in features endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model features: {str(e)}")
