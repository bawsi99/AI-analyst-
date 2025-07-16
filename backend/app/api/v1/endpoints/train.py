from app.services.data_service import data_service
from app.services.database_service import database_service
from app.services.summary_service import summary_service
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
    - **model_type**: classification or regression
    - **algorithm**: random_forest, xgboost, logistic_regression (optional)
    """
    try:
        # Validate model_type
        if request.model_type not in ['classification', 'regression']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model_type: {request.model_type}. Must be 'classification' or 'regression'"
            )
        
        # Get session info
        session_info = await database_service.get_session_by_id(session_id, current_user["id"])
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Load data
        df = data_service.load_data(session_id)
        
        # Validate target column
        if request.target_column not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target column '{request.target_column}' not found in dataset"
            )
        
        # Remove excluded columns before training
        excluded_columns = request.excluded_columns or []
        columns_to_remove = []
        for col in excluded_columns:
            if col in df.columns:
                columns_to_remove.append(col)
        
        if columns_to_remove:
            df = df.drop(columns=columns_to_remove)
            print(f"Removed columns during training: {columns_to_remove}")
        
        # Check for sufficient data
        if len(df) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient data for training (minimum 5 rows required)"
            )
        
        # Check target column distribution for classification
        if request.model_type == 'classification':
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
        
        # Train model with cleaned data (excluded columns already removed)
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
        
        # Generate and save summary and data insights
        try:
            # Generate complete summary including model summary
            summary_data = summary_service.generate_complete_summary(session_id, training_result['model_id'])
            
            # Save analysis summary to database
            await database_service.save_analysis_summary(
                user_id=current_user["id"],
                session_id=session_id,
                summary_data=summary_data,
                model_id=training_result['model_id']
            )
            
            # Generate and save data insights
            profile_data = data_service.profile_data(session_id)
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
            
            print(f"Summary and data insights saved for model {training_result['model_id']}")
            
        except Exception as e:
            print(f"Warning: Failed to save summary and data insights: {e}")
            # Continue with training response even if summary saving fails
        
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