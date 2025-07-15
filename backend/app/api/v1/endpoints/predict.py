from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import PredictionRequest, PredictionResponse
from app.ml.pipeline import ml_pipeline
from app.services.database_service import database_service
from app.core.auth import get_current_user
from typing import Dict, Any

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
        
        # Apply the same excluded columns that were used during training
        excluded_columns = model_info.get('hyperparameters', {}).get('excluded_columns', [])
        if excluded_columns:
            # Convert input data to DataFrame for easier column manipulation
            import pandas as pd
            df = pd.DataFrame(request.data)
            
            # Remove excluded columns if they exist in the data
            columns_to_remove = [col for col in excluded_columns if col in df.columns]
            if columns_to_remove:
                df = df.drop(columns=columns_to_remove)
                print(f"Removed excluded columns: {columns_to_remove}")
            
            # Convert back to list of dictionaries
            processed_data = df.to_dict('records')
        else:
            processed_data = request.data
        
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error making predictions: {str(e)}"
        ) 