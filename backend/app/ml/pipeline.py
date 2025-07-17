import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, classification_report
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import xgboost as xgb
import joblib
import os
import uuid
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import shap
from app.core.config import settings

class MLPipeline:
    def __init__(self):
        self.models = {}  # In production, use database
        self.preprocessors = {}
    
    def prepare_features(self, df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target"""
        # Remove target column
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        return X, y
    
    def create_preprocessor(self, X: pd.DataFrame) -> ColumnTransformer:
        """Create preprocessing pipeline"""
        # Separate numerical and categorical columns
        numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
        
        # Numerical preprocessing
        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # Categorical preprocessing
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        # Combine transformers
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_cols),
                ('cat', categorical_transformer, categorical_cols)
            ],
            remainder='drop'
        )
        
        return preprocessor
    
    def get_model(self, model_type: str, algorithm: str = None) -> Any:
        """Get model based on type and algorithm"""
        if model_type == 'classification':
            if algorithm == 'random_forest':
                return RandomForestClassifier(n_estimators=100, random_state=settings.RANDOM_STATE)
            elif algorithm == 'xgboost':
                return xgb.XGBClassifier(random_state=settings.RANDOM_STATE)
            elif algorithm == 'logistic_regression':
                return LogisticRegression(random_state=settings.RANDOM_STATE, max_iter=1000)
            else:
                # Default to RandomForest
                return RandomForestClassifier(n_estimators=100, random_state=settings.RANDOM_STATE)
        else:  # regression
            if algorithm == 'random_forest':
                return RandomForestRegressor(n_estimators=100, random_state=settings.RANDOM_STATE)
            elif algorithm == 'xgboost':
                return xgb.XGBRegressor(random_state=settings.RANDOM_STATE)
            elif algorithm == 'linear_regression':
                return LinearRegression()
            else:
                # Default to RandomForest
                return RandomForestRegressor(n_estimators=100, random_state=settings.RANDOM_STATE)
    
    def train_model(self, df: pd.DataFrame, target_col: str, model_type: str, 
                   algorithm: str = None) -> Dict[str, Any]:
        """Train a machine learning model"""
        start_time = datetime.now()
        
        # Clean target column data
        df[target_col] = df[target_col].astype(str).str.strip()
        
        # Validate model_type
        if model_type not in ['classification', 'regression']:
            raise ValueError(f"Invalid model_type: {model_type}. Must be 'classification' or 'regression'")
        
        # Prepare data
        X, y = self.prepare_features(df, target_col)
        
        # Check if stratification is possible
        can_stratify = False
        if model_type == 'classification':
            # Check if we have enough samples per class for stratification
            class_counts = y.value_counts()
            min_samples_per_class = min(class_counts)
            can_stratify = min_samples_per_class >= 2 and len(class_counts) >= 2
        
        # Split data
        if can_stratify:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=settings.TEST_SIZE, random_state=settings.RANDOM_STATE,
                stratify=y
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=settings.TEST_SIZE, random_state=settings.RANDOM_STATE
            )
        
        # Create preprocessor
        preprocessor = self.create_preprocessor(X_train)
        
        # Get model
        model = self.get_model(model_type, algorithm)
        
        # Create full pipeline
        full_pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        
        # Train model
        full_pipeline.fit(X_train, y_train)
        
        # Make predictions
        y_pred = full_pipeline.predict(X_test)
        
        # Calculate metrics
        metrics = self.calculate_metrics(y_test, y_pred, model_type)
        
        # Calculate feature importance
        feature_importance = self.calculate_feature_importance(
            full_pipeline, X_train, model_type
        )
        
        # Generate model ID and save
        model_id = str(uuid.uuid4())
        
        # Ensure model storage directory exists
        os.makedirs(settings.MODEL_STORAGE_PATH, exist_ok=True)
        
        model_path = os.path.join(settings.MODEL_STORAGE_PATH, f"{model_id}.joblib")
        
        # Save pipeline with error handling
        try:
            joblib.dump(full_pipeline, model_path)
        except Exception as e:
            print(f"Error saving model to {model_path}: {e}")
            # Try alternative location if primary fails
            alt_path = os.path.join("/tmp", f"{model_id}.joblib")
            print(f"Trying alternative path: {alt_path}")
            joblib.dump(full_pipeline, alt_path)
            model_path = alt_path
        
        # Store model info
        training_time = (datetime.now() - start_time).total_seconds()
        
        self.models[model_id] = {
            'model_path': model_path,
            'model_type': model_type,
            'target_column': target_col,
            'algorithm': algorithm or 'default',
            'training_time': training_time,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'created_at': datetime.now(),
            'preprocessor': preprocessor
        }
        
        return {
            'model_id': model_id,
            'model_type': model_type,
            'target_column': target_col,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'training_time': training_time
        }
    
    def calculate_metrics(self, y_true: pd.Series, y_pred: np.ndarray, model_type: str) -> Dict[str, float]:
        """Calculate model metrics"""
        if model_type == 'classification':
            return {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='weighted'),
                'recall': recall_score(y_true, y_pred, average='weighted'),
                'f1_score': f1_score(y_true, y_pred, average='weighted')
            }
        else:  # regression
            return {
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'r2_score': r2_score(y_true, y_pred)
            }
    
    def calculate_feature_importance(self, pipeline: Pipeline, X_train: pd.DataFrame, 
                                   model_type: str) -> Dict[str, float]:
        """Calculate feature importance"""
        try:
            # Get feature names after preprocessing
            preprocessor = pipeline.named_steps['preprocessor']
            model = pipeline.named_steps['classifier']
            
            # Transform training data to get feature names
            X_transformed = preprocessor.transform(X_train)
            
            # Get feature names
            feature_names = []
            for name, trans, cols in preprocessor.transformers_:
                if name == 'num':
                    feature_names.extend(cols)
                elif name == 'cat':
                    # For categorical features, get encoded feature names
                    try:
                        # Check if the transformer has been fitted
                        if hasattr(trans, 'named_steps') and 'onehot' in trans.named_steps:
                            onehot = trans.named_steps['onehot']
                            if hasattr(onehot, 'get_feature_names_out') and hasattr(onehot, 'categories_'):
                                # Only call get_feature_names_out if the encoder has been fitted
                                if onehot.categories_ is not None:
                                    cat_features = onehot.get_feature_names_out(cols)
                                    feature_names.extend(cat_features)
                                else:
                                    # Fallback: create feature names manually
                                    feature_names.extend([f"{col}_encoded" for col in cols])
                            else:
                                # Fallback for older sklearn versions
                                feature_names.extend([f"{col}_encoded" for col in cols])
                        else:
                            # Fallback if transformer structure is different
                            feature_names.extend([f"{col}_encoded" for col in cols])
                    except Exception as cat_error:
                        print(f"Warning: Error processing categorical features: {cat_error}")
                        # Fallback: create simple feature names
                        feature_names.extend([f"{col}_encoded" for col in cols])
            
            # Get feature importance
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importances = np.abs(model.coef_)
                if len(importances.shape) > 1:
                    importances = np.mean(importances, axis=0)
            else:
                print("Warning: Model does not have feature_importances_ or coef_ attributes")
                return {}
            
            # Create feature importance dictionary
            feature_importance = {}
            for i, feature in enumerate(feature_names):
                if i < len(importances):
                    feature_importance[feature] = float(importances[i])
            
            # Sort by importance
            feature_importance = dict(sorted(
                feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            return feature_importance
            
        except Exception as e:
            print(f"Error calculating feature importance: {e}")
            # Return empty dict instead of raising error
            return {}
    
    def predict(self, model_id: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make predictions using a trained model"""
        # Try to get model info from memory first
        model_info = None
        if model_id in self.models:
            model_info = self.models[model_id]
            model_path = model_info['model_path']
        else:
            # Try to load from file
            model_path = os.path.join(settings.MODEL_STORAGE_PATH, f"{model_id}.joblib")
            if not os.path.exists(model_path):
                # Try alternative location
                alt_path = os.path.join("/tmp", f"{model_id}.joblib")
                if os.path.exists(alt_path):
                    model_path = alt_path
                else:
                    raise ValueError(f"Model {model_id} not found in {settings.MODEL_STORAGE_PATH} or /tmp")
            
            # Load basic model info from database or create default
            model_info = {
                'model_type': 'classification',  # Default, could be improved
                'target_column': 'unknown'
            }
        
        # Load model with error handling
        try:
            pipeline = joblib.load(model_path)
        except Exception as e:
            print(f"Error loading model from {model_path}: {e}")
            raise ValueError(f"Failed to load model {model_id}: {str(e)}")
        
        # Convert data to DataFrame
        try:
            df = pd.DataFrame(data)
        except Exception as e:
            raise ValueError(f"Failed to convert input data to DataFrame: {str(e)}")
        
        # Make predictions with error handling
        try:
            predictions = pipeline.predict(df)
        except Exception as e:
            print(f"Error making predictions: {e}")
            raise ValueError(f"Failed to make predictions: {str(e)}")
        
        # Get probabilities for classification
        probabilities = None
        if model_info and model_info.get('model_type') == 'classification':
            try:
                probabilities = pipeline.predict_proba(df).tolist()
            except Exception as e:
                print(f"Warning: Could not get probabilities: {e}")
                pass
        
        # Calculate confidence scores (for classification, use max probability)
        confidence_scores = []
        if probabilities:
            confidence_scores = [max(prob) for prob in probabilities]
        else:
            # For regression, use a default confidence
            confidence_scores = [0.8] * len(predictions)

        # Ensure probabilities is always a list for serialization
        if probabilities is None:
            probabilities = []

        return {
            'predictions': predictions.tolist(),
            'confidence_scores': confidence_scores,
            'probabilities': probabilities
        }
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get model information"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        return self.models[model_id]
    
    def cleanup_model(self, model_id: str):
        """Clean up model files"""
        if model_id in self.models:
            model_path = self.models[model_id]['model_path']
            if os.path.exists(model_path):
                os.remove(model_path)
            del self.models[model_id]

# Global instance
ml_pipeline = MLPipeline() 