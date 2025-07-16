from celery import current_task
from celery import celery
from ml.pipeline import ml_pipeline
from services.data_service import data_service
from services.summary_service import summary_service
from services.ai_analysis_service import ai_analysis_service
from services.database_service import database_service
from typing import Dict, Any, List
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

@celery.task(bind=True)
def train_model_task(self, session_id: str, user_id: str, training_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Background task for training ML models
    """
    try:
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Loading data...', 'progress': 10}
        )
        
        # Load data
        df = data_service.load_data(session_id)
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Preparing features...', 'progress': 30}
        )
        
        # Remove excluded columns if specified
        excluded_columns = training_params.get('excluded_columns', [])
        columns_to_remove = [col for col in excluded_columns if col in df.columns]
        if columns_to_remove:
            df = df.drop(columns=columns_to_remove)
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Training model...', 'progress': 60}
        )
        
        # Train model
        training_result = ml_pipeline.train_model(
            df=df,
            target_col=training_params['target_column'],
            model_type=training_params['model_type'],
            algorithm=training_params.get('algorithm')
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Saving model and generating summary...', 'progress': 80}
        )
        
        # Save model to database
        model_data = {
            'model_id': training_result['model_id'],
            'model_path': f"models/{training_result['model_id']}.joblib",
            'model_type': training_result['model_type'],
            'target_column': training_result['target_column'],
            'algorithm': training_params.get('algorithm', 'default'),
            'metrics': training_result['metrics'],
            'feature_importance': training_result['feature_importance'],
            'training_time': training_result['training_time'],
            'model_size': 0,
            'excluded_columns': training_params.get('excluded_columns', [])
        }
        
        # Note: In a real implementation, you would need to handle async database operations
        # For now, we'll use synchronous database calls or implement proper async handling
        # This is a simplified version - in production, consider using sync_to_async or similar
        
        # Save model to database (simplified - would need proper async handling)
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create trained model
            loop.run_until_complete(
                database_service.create_trained_model(
                    user_id=user_id,
                    session_id=session_id,
                    model_data=model_data
                )
            )
            
            # Generate and save summary
            summary_data = summary_service.generate_complete_summary(session_id, training_result['model_id'])
            loop.run_until_complete(
                database_service.save_analysis_summary(
                    user_id=user_id,
                    session_id=session_id,
                    summary_data=summary_data,
                    model_id=training_result['model_id']
                )
            )
            
            # Update session status
            loop.run_until_complete(
                database_service.update_session_status(
                    session_id=session_id,
                    user_id=user_id,
                    status='trained',
                    metadata={'model_id': training_result['model_id']}
                )
            )
            
            loop.close()
        except Exception as db_error:
            logger.error(f"Database operation failed: {db_error}")
            # Continue with the task even if database operations fail
        
        return {
            'status': 'SUCCESS',
            'model_id': training_result['model_id'],
            'metrics': training_result['metrics'],
            'training_time': training_result['training_time']
        }
        
    except Exception as e:
        logger.error(f"Error in train_model_task: {str(e)}")
        # Update session status to failed
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                database_service.update_session_status(
                    session_id=session_id,
                    user_id=user_id,
                    status='failed',
                    metadata={'error': str(e)}
                )
            )
            loop.close()
        except:
            pass
        
        raise

@celery.task(bind=True)
def generate_ai_analysis_task(self, session_id: str, user_id: str, model_id: str = None) -> Dict[str, Any]:
    """
    Background task for generating AI analysis using Gemini LLM
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Initializing AI analysis...', 'progress': 20}
        )
        
        # Check if AI analysis is available
        if not ai_analysis_service.is_available():
            return {
                'status': 'FAILED',
                'error': 'AI analysis is not available. Please configure the Gemini API key.'
            }
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Generating AI insights...', 'progress': 50}
        )
        
        # Generate AI analysis
        ai_analysis_data = ai_analysis_service.generate_ai_analysis(session_id, model_id)
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Saving AI analysis...', 'progress': 80}
        )
        
        # Save AI analysis to database (you might want to add this to database_service)
        # For now, we'll return the analysis data
        return {
            'status': 'SUCCESS',
            'ai_analysis': ai_analysis_data['ai_analysis'],
            'enhanced_insights': ai_analysis_data['enhanced_insights'],
            'business_recommendations': ai_analysis_data['business_recommendations'],
            'technical_recommendations': ai_analysis_data['technical_recommendations'],
            'risk_assessment': ai_analysis_data['risk_assessment'],
            'opportunities': ai_analysis_data['opportunities']
        }
        
    except Exception as e:
        logger.error(f"Error in generate_ai_analysis_task: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e)
        }

@celery.task(bind=True)
def profile_data_task(self, session_id: str, user_id: str) -> Dict[str, Any]:
    """
    Background task for comprehensive data profiling
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Loading data...', 'progress': 20}
        )
        
        # Load and profile data
        profile_data = data_service.profile_data(session_id)
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Generating insights...', 'progress': 60}
        )
        
        # Save insights to database
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
        
        # Save insights to database (simplified async handling)
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                database_service.save_data_insights(session_id, user_id, insights_data)
            )
            loop.close()
        except Exception as db_error:
            logger.error(f"Failed to save data insights: {db_error}")
        
        return {
            'status': 'SUCCESS',
            'metadata': profile_data['metadata'],
            'schema': profile_data['schema'],
            'statistics': profile_data['statistics'],
            'insights': insights_data
        }
        
    except Exception as e:
        logger.error(f"Error in profile_data_task: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e)
        }

@celery.task(bind=True)
def batch_predict_task(self, model_id: str, user_id: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Background task for batch predictions
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Loading model...', 'progress': 20}
        )
        
        # Make predictions
        prediction_result = ml_pipeline.predict(model_id, data)
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Saving predictions...', 'progress': 80}
        )
        
        # Save predictions to database
        prediction_data = {
            'input_data': data,
            'predictions': prediction_result['predictions'],
            'confidence_scores': prediction_result['confidence_scores']
        }
        
        # Save predictions to database (simplified async handling)
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                database_service.save_prediction(
                    user_id=user_id,
                    model_id=model_id,
                    prediction_data=prediction_data
                )
            )
            loop.close()
        except Exception as db_error:
            logger.error(f"Failed to save prediction: {db_error}")
        
        return {
            'status': 'SUCCESS',
            'predictions': prediction_result['predictions'],
            'confidence_scores': prediction_result['confidence_scores'],
            'probabilities': prediction_result['probabilities']
        }
        
    except Exception as e:
        logger.error(f"Error in batch_predict_task: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e)
        }

@celery.task(bind=True)
def cleanup_session_task(self, session_id: str) -> Dict[str, Any]:
    """
    Background task for cleaning up session data and files
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Cleaning up session data...', 'progress': 30}
        )
        
        # Clean up data service session
        data_service.cleanup_session(session_id)
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Cleaning up files...', 'progress': 70}
        )
        
        # Clean up uploaded files
        session_info = data_service.get_session_info(session_id)
        if session_info and 'file_path' in session_info:
            file_path = session_info['file_path']
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return {
            'status': 'SUCCESS',
            'message': f'Session {session_id} cleaned up successfully'
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_session_task: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e)
        }

@celery.task(bind=True)
def generate_summary_task(self, session_id: str, user_id: str, model_id: str = None) -> Dict[str, Any]:
    """
    Background task for generating comprehensive analysis summary
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Generating summary...', 'progress': 50}
        )
        
        # Generate complete summary
        summary_data = summary_service.generate_complete_summary(session_id, model_id)
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Saving summary...', 'progress': 80}
        )
        
        # Save to database (simplified async handling)
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                database_service.save_analysis_summary(
                    user_id=user_id,
                    session_id=session_id,
                    summary_data=summary_data,
                    model_id=model_id
                )
            )
            loop.close()
        except Exception as db_error:
            logger.error(f"Failed to save analysis summary: {db_error}")
        
        return {
            'status': 'SUCCESS',
            'summary': summary_data
        }
        
    except Exception as e:
        logger.error(f"Error in generate_summary_task: {str(e)}")
        return {
            'status': 'FAILED',
            'error': str(e)
        } 