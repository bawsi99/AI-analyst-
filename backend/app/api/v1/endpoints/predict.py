from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import PredictionRequest, PredictionResponse
from ml.pipeline import ml_pipeline
from services.database_service import database_service
from core.auth import get_current_user
from typing import Dict, Any
import pandas as pd

router = APIRouter()

@router.post("/{model_id}", response_model=PredictionResponse)
async def predict(model_id: str, request: PredictionRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Make predictions using a trained model.
    
    - **model_id**: Model ID from training endpoint
    - **data**: List of dictionaries with feature values
    - Returns predictions and confidence scores
    """
    try:
        # Validate input data
        if not request.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for prediction"
            )
        
        # Check if all records have the same keys
        if len(request.data) > 1:
            first_keys = set(request.data[0].keys())
            for i, record in enumerate(request.data[1:], 1):
                if set(record.keys()) != first_keys:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Record {i} has different features than the first record"
                    )
        
        # Get model info from database
        model_info = await database_service.get_model_by_id(model_id, current_user["id"])
        if not model_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
        
        # Convert input data to DataFrame for easier manipulation
        df = pd.DataFrame(request.data)
        input_columns = set(df.columns)
        
        # Get target column from model info
        target_column = model_info.get('target_column')
        
        # Remove target column if it exists in the data (excluded columns should already be excluded during training)
        if target_column in df.columns:
            df = df.drop(columns=[target_column])
            print(f"Removed target column: {target_column}")
        
        # Check if we have any data left
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid features remaining after removing target column"
            )
        
        # Convert back to list of dictionaries
        processed_data = df.to_dict('records')
        
        print(f"Input columns: {input_columns}")
        print(f"Target column: {target_column}")
        print(f"Final columns: {list(df.columns)}")
        
        # Make predictions
        prediction_result = ml_pipeline.predict(model_id, processed_data)
        print('Prediction result:', prediction_result)
        
        # Save prediction to database
        prediction_data = {
            'input_data': request.data,
            'predictions': prediction_result['predictions'],
            'confidence_scores': prediction_result['confidence_scores']
        }
        
        await database_service.save_prediction(
            user_id=current_user["id"],
            model_id=model_id,  # Pass the text model_id, not the UUID id
            prediction_data=prediction_data
        )
        
        response = PredictionResponse(
            message="Predictions generated successfully",
            model_id=model_id,
            predictions=prediction_result['predictions'],
            confidence_scores=prediction_result['confidence_scores'],
            probabilities=prediction_result['probabilities']
        )
        print('PredictionResponse:', response.dict())
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error making predictions: {str(e)}"
        ) 