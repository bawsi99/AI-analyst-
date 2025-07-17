from typing import Dict, List, Any, Optional
from app.core.supabase import get_supabase_client
from datetime import datetime
import uuid
import asyncio
import time

class DatabaseService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def _retry_operation(self, operation, max_retries=3, delay=1.0):
        """Retry database operations with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # Log retry attempt
                print(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Exponential backoff
                wait_time = delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
    
    async def _execute_with_retry(self, operation, max_retries=3):
        """Execute database operation with retry logic"""
        def db_operation():
            return operation()
        
        return await self._retry_operation(db_operation, max_retries)
    
    # User Profile Operations
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user ID"""
        try:
            response = self.supabase.table('user_profiles').select('*').eq('id', user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    async def create_user_profile(self, user_id: str, email: str, full_name: Optional[str] = None) -> bool:
        """Create a new user profile"""
        try:
            profile_data = {
                'id': user_id,
                'email': email,
                'full_name': full_name
            }
            
            # Check if profile already exists
            existing_profile = await self.get_user_profile(user_id)
            if existing_profile:
                return True  # Profile already exists
            
            # Create new profile
            self.supabase.table('user_profiles').insert(profile_data).execute()
            return True
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False
    
    async def ensure_user_profile(self, user_id: str, email: str, full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Ensure user profile exists, create if it doesn't"""
        try:
            # Try to get existing profile
            profile = await self.get_user_profile(user_id)
            
            if profile:
                return profile
            
            # Create profile if it doesn't exist
            success = await self.create_user_profile(user_id, email, full_name)
            if success:
                return await self.get_user_profile(user_id)
            
            return None
        except Exception as e:
            print(f"Error ensuring user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            self.supabase.table('user_profiles').update(profile_data).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    # Analysis Sessions Operations
    async def create_analysis_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create a new analysis session"""
        try:
            session_record = {
                'user_id': user_id,
                'session_id': session_data['session_id'],
                'session_name': session_data.get('session_name', session_data['filename']),  # Use filename as session name if not provided
                'file_name': session_data['filename'],  # Changed from 'filename' to 'file_name' to match schema
                'file_path': session_data['file_path'],
                'file_size': session_data['file_size'],
                'status': 'uploaded',
                'metadata': session_data.get('metadata', {})
            }
            
            response = self.supabase.table('analysis_sessions').insert(session_record).execute()
            return response.data[0]['id']
        except Exception as e:
            print(f"Error creating analysis session: {e}")
            raise
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all analysis sessions for a user"""
        try:
            response = self.supabase.table('analysis_sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    async def get_session_by_id(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis session by session ID"""
        try:
            print(f"DEBUG: Database query - session_id={session_id}, user_id={user_id}")
            response = self.supabase.table('analysis_sessions').select('*').eq('session_id', session_id).eq('user_id', user_id).execute()
            print(f"DEBUG: Database response - data count: {len(response.data) if response.data else 0}")
            if response.data:
                print(f"DEBUG: Found session: {response.data[0]}")
                return response.data[0]
            print(f"DEBUG: No session found in database")
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    async def update_session_status(self, session_id: str, user_id: str, status: str, metadata: Optional[Dict] = None) -> bool:
        """Update analysis session status"""
        try:
            update_data = {'status': status}
            if metadata:
                update_data['metadata'] = metadata
            
            self.supabase.table('analysis_sessions').update(update_data).eq('session_id', session_id).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating session status: {e}")
            return False
    
    async def save_data_insights(self, session_id: str, user_id: str, insights_data: Dict[str, Any]) -> bool:
        """Save detailed data insights to session metadata"""
        try:
            # Get current session metadata
            session_info = await self.get_session_by_id(session_id, user_id)
            if not session_info:
                raise ValueError(f"Session with session_id {session_id} not found")
            
            current_metadata = session_info.get('metadata', {})
            
            # Add insights data to metadata
            current_metadata['data_insights'] = insights_data
            
            # Update session with new metadata
            self.supabase.table('analysis_sessions').update({
                'metadata': current_metadata,
                'status': 'profiled'
            }).eq('session_id', session_id).eq('user_id', user_id).execute()
            
            return True
        except Exception as e:
            print(f"Error saving data insights: {e}")
            return False
    
    async def get_data_insights(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed data insights from session metadata"""
        try:
            session_info = await self.get_session_by_id(session_id, user_id)
            if not session_info:
                return None
            
            metadata = session_info.get('metadata', {})
            return metadata.get('data_insights')
        except Exception as e:
            print(f"Error getting data insights: {e}")
            return None
    
    # Trained Models Operations
    async def create_trained_model(self, user_id: str, session_id: str, model_data: Dict[str, Any]) -> str:
        """Create a new trained model record"""
        try:
            # First, get the session to get its UUID id
            session_info = await self.get_session_by_id(session_id, user_id)
            if not session_info:
                raise ValueError(f"Session with session_id {session_id} not found")
            
            # Use the UUID id from the session, not the text session_id
            session_uuid = session_info['id']
            
            # Generate a descriptive model name if not provided
            model_name = model_data.get('model_name')
            if not model_name:
                # Create a descriptive name based on model type, algorithm, and target
                model_type = model_data.get('model_type', 'unknown')
                algorithm = model_data.get('algorithm', 'unknown')
                target_column = model_data.get('target_column', 'unknown')
                model_name = f"{model_type.title()} - {algorithm.replace('_', ' ').title()} - {target_column}"
            
            model_record = {
                'user_id': user_id,
                'session_id': session_uuid,  # Use the UUID id from analysis_sessions
                'model_id': model_data['model_id'],
                'model_name': model_name,  # Add the required model_name field
                'model_path': model_data['model_path'],
                'model_type': model_data['model_type'],
                'target_column': model_data['target_column'],
                'algorithm': model_data['algorithm'],
                'metrics': model_data['metrics'],
                'feature_importance': model_data.get('feature_importance', {}),
                'training_time': model_data.get('training_time', 0),
                'model_size': model_data.get('model_size', 0),
                'hyperparameters': {
                    'excluded_columns': model_data.get('excluded_columns', [])
                }
            }
            
            # Use retry logic for critical database operation
            def insert_model():
                response = self.supabase.table('trained_models').insert(model_record).execute()
                return response.data[0]['id']
            
            return await self._execute_with_retry(insert_model, max_retries=3)
        except Exception as e:
            print(f"Error creating trained model: {e}")
            raise
    
    async def get_user_models(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all trained models for a user"""
        try:
            response = self.supabase.table('trained_models').select('*, analysis_sessions(file_name, session_id)').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting user models: {e}")
            return []
    
    async def get_model_by_id(self, model_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get trained model by model ID"""
        try:
            response = self.supabase.table('trained_models').select('*, analysis_sessions(file_name, session_id)').eq('model_id', model_id).eq('user_id', user_id).execute()
            if response.data:
                model_data = response.data[0]
                # Add the text session_id from the joined analysis_sessions table
                if 'analysis_sessions' in model_data and model_data['analysis_sessions']:
                    model_data['text_session_id'] = model_data['analysis_sessions']['session_id']
                return model_data
            return None
        except Exception as e:
            print(f"Error getting model: {e}")
            return None
    
    # Predictions History Operations
    async def save_prediction(self, user_id: str, model_id: str, prediction_data: Dict[str, Any]) -> str:
        """Save a prediction to history"""
        try:
            # First, get the model to get its UUID id
            model_info = await self.get_model_by_id(model_id, user_id)
            if not model_info:
                raise ValueError(f"Model with model_id {model_id} not found")
            
            # Use the UUID id from the model, not the text model_id
            model_uuid = model_info['id']
            
            prediction_record = {
                'user_id': user_id,
                'model_id': model_uuid,  # Use the UUID id from trained_models
                'input_data': prediction_data['input_data'],
                'predictions': prediction_data['predictions'],
                'prediction_result': prediction_data['predictions'],  # Add prediction_result field
                'confidence_scores': prediction_data.get('confidence_scores', [])
            }
            
            response = self.supabase.table('prediction_history').insert(prediction_record).execute()
            return response.data[0]['id']
        except Exception as e:
            print(f"Error saving prediction: {e}")
            raise
    
    async def get_prediction_history(self, user_id: str, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get prediction history for a user"""
        try:
            query = self.supabase.table('prediction_history').select('*, trained_models(model_id, model_type, target_column)').eq('user_id', user_id)
            if model_id:
                query = query.eq('model_id', model_id)
            
            response = query.order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting prediction history: {e}")
            return []
    
    # Analysis Summaries Operations
    async def save_analysis_summary(self, user_id: str, session_id: str, summary_data: Dict[str, Any], model_id: Optional[str] = None) -> str:
        """Save analysis summary"""
        try:
            # First, get the session to get its UUID id
            session_info = await self.get_session_by_id(session_id, user_id)
            if not session_info:
                raise ValueError(f"Session with session_id {session_id} not found")
            
            # Use the UUID id from the session, not the text session_id
            session_uuid = session_info['id']
            
            # If model_id is provided, get the UUID id from trained_models table
            model_uuid = None
            if model_id:
                # Try to get the model by text model_id first with retry logic
                try:
                    model_info = await self.get_model_by_id(model_id, user_id)
                    if model_info:
                        model_uuid = model_info['id']  # Use the UUID id from trained_models
                    else:
                        # If not found, try a direct query to get the UUID id with retry
                        def lookup_model():
                            response = self.supabase.table('trained_models').select('id').eq('model_id', model_id).eq('user_id', user_id).execute()
                            if response.data:
                                return response.data[0]['id']
                            return None
                        
                        model_uuid = await self._execute_with_retry(lookup_model, max_retries=2)
                        
                except Exception as lookup_error:
                    print(f"Warning: Could not find model {model_id} for summary: {lookup_error}")
                    # Continue without model_id if lookup fails
            
            summary_record = {
                'user_id': user_id,
                'session_id': session_uuid,  # Use the UUID id from analysis_sessions
                'summary_type': 'complete',  # Add the required summary_type field
                'content': summary_data['data_summary'],  # Add the required content field
                'data_summary': summary_data['data_summary'],
                'model_summary': summary_data.get('model_summary'),
                'key_insights': summary_data['key_insights'],
                'recommendations': summary_data['recommendations']
            }
            
            # Only add model_id if we successfully found the model UUID
            if model_uuid:
                summary_record['model_id'] = model_uuid
            else:
                # If model lookup failed, add a small delay to ensure model is committed
                if model_id:
                    print(f"Model lookup failed for {model_id}, adding delay before summary creation")
                    await asyncio.sleep(0.5)  # 500ms delay
            
            # Use retry logic for summary creation
            def insert_summary():
                response = self.supabase.table('analysis_summaries').insert(summary_record).execute()
                return response.data[0]['id']
            
            return await self._execute_with_retry(insert_summary, max_retries=3)
        except Exception as e:
            print(f"Error saving analysis summary: {e}")
            raise
    
    async def get_analysis_summary(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis summary for a session"""
        try:
            # First, get the session to get its UUID id
            session_info = await self.get_session_by_id(session_id, user_id)
            if not session_info:
                return None
            
            # Use the UUID id from the session, not the text session_id
            session_uuid = session_info['id']
            
            response = self.supabase.table('analysis_summaries').select('*').eq('session_id', session_uuid).eq('user_id', user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting analysis summary: {e}")
            return None
    
    # Dashboard Statistics
    async def get_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard statistics for a user"""
        try:
            # Get sessions count and data
            sessions_response = self.supabase.table('analysis_sessions').select('id', count='exact').eq('user_id', user_id).execute()
            recent_sessions = self.supabase.table('analysis_sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()
            
            # Get user's models by getting all models and filtering by session ownership
            all_models = await self.get_user_models(user_id)
            total_models = len(all_models)
            recent_models = all_models[:5]  # Get first 5 models
            
            # Get predictions count for the current user
            try:
                predictions_response = self.supabase.table('prediction_history').select('id', count='exact').eq('user_id', user_id).execute()
                total_predictions = predictions_response.count or 0
            except:
                total_predictions = 0
            
            return {
                'total_sessions': sessions_response.count or 0,
                'total_models': total_models,
                'total_predictions': total_predictions,
                'recent_sessions': recent_sessions.data,
                'recent_models': recent_models
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_sessions': 0,
                'total_models': 0,
                'total_predictions': 0,
                'recent_sessions': [],
                'recent_models': []
            }

# Global instance
database_service = DatabaseService() 