from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import TrainingRequest, TrainingResponse
from app.services.data_service import data_service
from app.services.database_service import database_service
from app.ml.pipeline import ml_pipeline
from app.core.auth import get_current_user
from typing import Dict, Any
import pandas as pd
import os

router = APIRouter()

@router.post("/{session_id}", response_model=TrainingResponse)
async def train_model(session_id: str, request: TrainingRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Train a machine learning model on the uploaded data.
    
    - **session_id**: Session ID from upload endpoint
    - **target_column**: Column to predict
    - **model_type**: auto, classification, or regression
    - **algorithm**: random_forest, xgboost, logistic_regression (optional)
    """
    try:
        # Get session info from database first
        print(f"DEBUG: Looking up session in DB with session_id={session_id}, user_id={current_user['id']}")
        
        # Debug: Get all sessions for this user
        all_sessions = await database_service.get_user_sessions(current_user["id"])
        print(f"DEBUG: All sessions for user: {all_sessions}")
        
        session_info = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Try to load data from data service (in-memory)
        try:
            df = data_service.load_data(session_id)
        except ValueError as e:
            # If session not in memory, try to load from file path
            file_path = session_info.get('file_path')
            if not file_path or not os.path.exists(file_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session data file not found"
                )
            df = pd.read_csv(file_path)
        
        # Remove excluded columns if specified
        if request.excluded_columns:
            # Validate excluded columns exist
            invalid_excluded = [col for col in request.excluded_columns if col not in df.columns]
            if invalid_excluded:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Excluded columns not found in dataset: {', '.join(invalid_excluded)}"
                )
            
            # Remove excluded columns
            df = df.drop(columns=request.excluded_columns)
        
        # Validate target column
        if request.target_column not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target column '{request.target_column}' not found in dataset"
            )
        
        # Check for sufficient data
        if len(df) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient data for training (minimum 5 rows required)"
            )
        
        # Check target column distribution for classification
        if request.model_type == 'classification' or request.model_type == 'auto':
            target_counts = df[request.target_column].value_counts()
            if len(target_counts) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Target column '{request.target_column}' has only {len(target_counts)} unique values. At least 2 classes are required for classification."
                )
            min_class_count = target_counts.min()
            if min_class_count < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Target column '{request.target_column}' has a class with no samples. Each class must have at least 1 sample."
                )
        
        # Check for missing values in target
        missing_target = df[request.target_column].isnull().sum()
        if missing_target > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target column has {missing_target} missing values"
            )
        
        # Train model
        training_result = ml_pipeline.train_model(
            df=df,
            target_col=request.target_column,
            model_type=request.model_type,
            algorithm=request.algorithm
        )
        
        # Session info already retrieved above
        
        # Save model to database
        model_data = {
            'model_id': training_result['model_id'],
            'model_path': f"models/{training_result['model_id']}.joblib",
            'model_type': training_result['model_type'],
            'target_column': training_result['target_column'],
            'algorithm': request.algorithm or 'default',
            'metrics': training_result['metrics'],
            'feature_importance': training_result['feature_importance'],
            'training_time': training_result['training_time'],
            'model_size': 0,  # Will be calculated if needed
            'excluded_columns': request.excluded_columns or []  # Store excluded columns
        }
        
        await database_service.create_trained_model(
            user_id=current_user["id"],
            session_id=session_info["session_id"],
            model_data=model_data
        )
        
        # Update session status
        await database_service.update_session_status(
            session_id=session_id,
            user_id=current_user["id"],
            status='trained',
            metadata={'model_id': training_result['model_id']}
        )
        
        return TrainingResponse(
            message="Model trained successfully",
            model_id=training_result['model_id'],
            model_type=training_result['model_type'],
            target_column=training_result['target_column'],
            metrics=training_result['metrics'],
            feature_importance=training_result['feature_importance'],
            training_time=training_result['training_time']
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error training model: {str(e)}"
        ) 