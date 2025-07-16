import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import os
import uuid
from datetime import datetime
import json
from app.core.config import settings
from app.models.schemas import ColumnSchema, DataStatistics, DataInsights

class DataService:
    def __init__(self):
        self.sessions = {}  # In production, use database
        
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return session ID"""
        session_id = str(uuid.uuid4())
        file_path = os.path.join(settings.UPLOAD_STORAGE_PATH, f"{session_id}_{filename}")
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
            
        # Store session info
        self.sessions[session_id] = {
            'filename': filename,
            'file_path': file_path,
            'upload_time': datetime.utcnow(),
            'file_size': len(file_content),
            'status': 'uploaded'
        }
        
        return session_id
    
    def load_data(self, session_id: str) -> pd.DataFrame:
        """Load data from session"""
        if session_id not in self.sessions:
            # Try to reconstruct session info from file system
            self._reconstruct_session_from_file(session_id)
            
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        file_path = self.sessions[session_id]['file_path']
        return pd.read_csv(file_path)
    
    def _reconstruct_session_from_file(self, session_id: str):
        """Try to reconstruct session info from file system"""
        try:
            # Look for files that start with the session_id
            upload_dir = settings.UPLOAD_STORAGE_PATH
            if os.path.exists(upload_dir):
                for filename in os.listdir(upload_dir):
                    if filename.startswith(session_id + '_'):
                        file_path = os.path.join(upload_dir, filename)
                        if os.path.isfile(file_path):
                            # Extract original filename
                            original_filename = filename[len(session_id) + 1:]  # Remove session_id_ prefix
                            
                            # Get file stats
                            file_stats = os.stat(file_path)
                            
                            self.sessions[session_id] = {
                                'filename': original_filename,
                                'file_path': file_path,
                                'upload_time': datetime.fromtimestamp(file_stats.st_mtime),
                                'file_size': file_stats.st_size,
                                'status': 'uploaded'
                            }
                            print(f"Reconstructed session {session_id} from file: {filename}")
                            return
                            
            print(f"Could not find file for session {session_id}")
                
        except Exception as e:
            print(f"Error reconstructing session from file: {e}")
    

    
    def infer_schema(self, df: pd.DataFrame) -> List[ColumnSchema]:
        """Infer schema from DataFrame"""
        schema = []
        
        for column in df.columns:
            col_data = df[column]
            dtype = str(col_data.dtype)
            
            # Determine column type
            if dtype in ['object', 'string']:
                if col_data.nunique() <= 10:
                    col_type = 'categorical'
                else:
                    col_type = 'text'
            elif dtype in ['int64', 'float64']:
                if col_data.nunique() <= 2:
                    col_type = 'boolean'
                else:
                    col_type = 'numerical'
            elif 'datetime' in dtype:
                col_type = 'datetime'
            else:
                col_type = 'other'
            
            # Calculate statistics - convert numpy types to Python native types
            null_count = int(col_data.isnull().sum())
            null_percentage = float((null_count / len(col_data)) * 100)
            unique_count = int(col_data.nunique())
            is_constant = unique_count == 1
            is_high_cardinality = unique_count > len(col_data) * 0.5
            
            # Sample values - get unique values, up to 10 for categorical, 5 for others
            if col_type == 'categorical':
                # For categorical, get all unique values (up to 10)
                unique_values = col_data.dropna().unique()
                sample_values = sorted(unique_values[:10].astype(str).tolist())
            else:
                # For non-categorical, get first 5 unique values
                unique_values = col_data.dropna().unique()
                sample_values = sorted(unique_values[:5].astype(str).tolist())
            
            schema.append(ColumnSchema(
                name=column,
                dtype=col_type,
                null_count=null_count,
                null_percentage=null_percentage,
                unique_count=unique_count,
                is_constant=is_constant,
                is_high_cardinality=is_high_cardinality,
                sample_values=sample_values
            ))
            
        return schema
    
    def calculate_statistics(self, df: pd.DataFrame) -> DataStatistics:
        """Calculate basic statistics"""
        memory_usage = df.memory_usage(deep=True).sum()
        memory_usage_mb = f"{memory_usage / 1024 / 1024:.2f} MB"
        
        return DataStatistics(
            total_rows=len(df),
            total_columns=len(df.columns),
            memory_usage=memory_usage_mb,
            duplicate_rows=int(df.duplicated().sum()),
            missing_values=int(df.isnull().sum().sum())
        )
    
    def detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        outliers = {}
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            outliers[col] = {
                'count': int(outlier_count),
                'percentage': float((outlier_count / len(df)) * 100)
            }
            
        return outliers
    
    def calculate_skewness(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate skewness for numerical columns"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        skewness = {}
        
        for col in numerical_cols:
            skewness[col] = float(df[col].skew())
            
        return skewness
    
    def calculate_correlations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate pairwise correlations and return as list of unique pairs"""
        numerical_df = df.select_dtypes(include=[np.number])
        if len(numerical_df.columns) < 2:
            return []
            
        corr_matrix = numerical_df.corr()
        correlations = []
        
        # Get upper triangle indices
        upper_triangle = np.triu_indices_from(corr_matrix, k=1)
        
        for i, j in zip(upper_triangle[0], upper_triangle[1]):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            corr_value = float(corr_matrix.iloc[i, j])
            
            from app.models.schemas import CorrelationPair
            correlations.append(CorrelationPair(
                column1=col1,
                column2=col2,
                correlation=corr_value,
                strength=self._get_correlation_strength(corr_value)
            ))
        
        # Sort by absolute correlation value (highest first)
        correlations.sort(key=lambda x: abs(x.correlation), reverse=True)
        
        return correlations
    
    def _get_correlation_strength(self, corr_value: float) -> str:
        """Get correlation strength description"""
        abs_corr = abs(corr_value)
        if abs_corr >= 0.8:
            return 'very_strong'
        elif abs_corr >= 0.6:
            return 'strong'
        elif abs_corr >= 0.4:
            return 'moderate'
        elif abs_corr >= 0.2:
            return 'weak'
        else:
            return 'very_weak'
    
    def detect_imbalanced_columns(self, df: pd.DataFrame) -> List[str]:
        """Detect imbalanced categorical columns"""
        imbalanced = []
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            if len(value_counts) > 1:
                max_count = int(value_counts.max())
                min_count = int(value_counts.min())
                imbalance_ratio = max_count / min_count
                
                if imbalance_ratio > 10:  # Threshold for imbalance
                    imbalanced.append(col)
                    
        return imbalanced
    
    def detect_data_leakage(self, df: pd.DataFrame, target_col: str = None) -> List[str]:
        """Detect potential data leakage"""
        leakage = []
        numerical_df = df.select_dtypes(include=[np.number])
        
        if target_col and target_col in numerical_df.columns:
            target_correlations = numerical_df.corr()[target_col].abs()
            high_corr_features = target_correlations[target_correlations > 0.95].index.tolist()
            high_corr_features.remove(target_col)
            
            for feature in high_corr_features:
                leakage.append(f"High correlation with target: {feature} ({target_correlations[feature]:.3f})")
                
        return leakage
    
    def generate_insights(self, df: pd.DataFrame, target_col: str = None) -> DataInsights:
        """Generate comprehensive data insights"""
        outliers = self.detect_outliers(df)
        skewness = self.calculate_skewness(df)
        correlations = self.calculate_correlations(df)
        imbalanced_columns = self.detect_imbalanced_columns(df)
        data_leakage = self.detect_data_leakage(df, target_col)
        
        return DataInsights(
            outliers=outliers,
            skewness=skewness,
            correlations=correlations,
            imbalanced_columns=imbalanced_columns,
            data_leakage=data_leakage
        )
    
    def profile_data(self, session_id: str) -> Dict[str, Any]:
        """Complete data profiling"""
        df = self.load_data(session_id)
        
        schema = self.infer_schema(df)
        statistics = self.calculate_statistics(df)
        insights = self.generate_insights(df)
        
        # Update session status
        self.sessions[session_id]['status'] = 'profiled'
        
        return {
            'schema': schema,
            'statistics': statistics,
            'insights': insights,
            'metadata': {
                'columns': len(df.columns),
                'rows': len(df),
                'memory_usage': statistics.memory_usage
            }
        }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information"""
        if session_id not in self.sessions:
            # Try to reconstruct session info from file system
            self._reconstruct_session_from_file(session_id)
            
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        return self.sessions[session_id]
    
    def cleanup_session(self, session_id: str):
        """Clean up session data"""
        if session_id in self.sessions:
            file_path = self.sessions[session_id]['file_path']
            if os.path.exists(file_path):
                os.remove(file_path)
            del self.sessions[session_id]

# Global instance
data_service = DataService() 