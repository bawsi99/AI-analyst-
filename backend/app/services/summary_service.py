import pandas as pd
from typing import Dict, List, Any
from services.data_service import data_service
from ml.pipeline import ml_pipeline

class SummaryService:
    def __init__(self):
        pass
    
    def generate_data_summary(self, session_id: str) -> str:
        """Generate natural language summary of the dataset"""
        try:
            df = data_service.load_data(session_id)
            profile = data_service.profile_data(session_id)
            
            rows = len(df)
            cols = len(df.columns)
            
            # Basic dataset info
            summary = f"This dataset contains {rows:,} rows and {cols} columns. "
            
            # Data types
            numerical_cols = df.select_dtypes(include=['number']).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numerical_cols) > 0:
                summary += f"There are {len(numerical_cols)} numerical features. "
            if len(categorical_cols) > 0:
                summary += f"There are {len(categorical_cols)} categorical features. "
            
            # Missing data
            missing_total = df.isnull().sum().sum()
            if missing_total > 0:
                missing_percentage = (missing_total / (rows * cols)) * 100
                summary += f"The dataset has {missing_total:,} missing values ({missing_percentage:.1f}% of all data). "
            
            # Duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                summary += f"There are {duplicates:,} duplicate rows. "
            
            # Outliers
            outliers = profile['insights'].outliers
            if outliers:
                outlier_cols = list(outliers.keys())
                summary += f"Outliers were detected in {len(outlier_cols)} numerical columns. "
            
            # Imbalanced columns
            imbalanced = profile['insights'].imbalanced_columns
            if imbalanced:
                summary += f"Imbalanced categorical features were found in {len(imbalanced)} columns. "
            
            return summary
            
        except Exception as e:
            return f"Error generating data summary: {str(e)}"
    
    def generate_model_summary(self, model_id: str) -> str:
        """Generate natural language summary of the trained model"""
        try:
            model_info = ml_pipeline.get_model_info(model_id)
            
            model_type = model_info['model_type']
            algorithm = model_info['algorithm']
            target_col = model_info['target_column']
            metrics = model_info['metrics']
            training_time = model_info['training_time']
            
            summary = f"A {model_type} model was trained using {algorithm} algorithm "
            summary += f"to predict the '{target_col}' column. "
            
            if model_type == 'classification':
                accuracy = metrics.get('accuracy', 0)
                f1 = metrics.get('f1_score', 0)
                summary += f"The model achieved {accuracy:.1%} accuracy and {f1:.1%} F1-score. "
            else:  # regression
                r2 = metrics.get('r2_score', 0)
                rmse = metrics.get('rmse', 0)
                summary += f"The model achieved R² score of {r2:.3f} and RMSE of {rmse:.3f}. "
            
            summary += f"Training took {training_time:.2f} seconds. "
            
            # Feature importance
            feature_importance = model_info['feature_importance']
            if feature_importance:
                top_features = list(feature_importance.keys())[:5]
                summary += f"The top 5 most important features are: {', '.join(top_features)}. "
            
            return summary
            
        except Exception as e:
            return f"Error generating model summary: {str(e)}"
    
    def generate_key_insights(self, session_id: str, model_id: str = None) -> List[str]:
        """Generate key insights from data and model"""
        insights = []
        
        try:
            df = data_service.load_data(session_id)
            profile = data_service.profile_data(session_id)
            
            # Data quality insights
            missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_percentage > 10:
                insights.append(f"High missing data rate: {missing_percentage:.1f}% of values are missing")
            
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                insights.append(f"Dataset contains {duplicates} duplicate rows that should be removed")
            
            # Outlier insights
            outliers = profile['insights'].outliers
            for col, outlier_info in outliers.items():
                if outlier_info['percentage'] > 5:
                    insights.append(f"Column '{col}' has {outlier_info['percentage']:.1f}% outliers")
            
            # Correlation insights
            correlations = profile['insights'].correlations
            high_corr_pairs = []
            
            # Handle both old format (dict) and new format (list of CorrelationPair objects)
            if isinstance(correlations, dict):
                # Old format - convert to new format
                for col1 in correlations:
                    for col2, corr in correlations[col1].items():
                        if abs(corr) > 0.8:
                            high_corr_pairs.append((col1, col2, corr))
            else:
                # New format - list of CorrelationPair objects
                for corr_obj in correlations:
                    if abs(corr_obj.correlation) > 0.8:
                        high_corr_pairs.append((
                            corr_obj.column1, 
                            corr_obj.column2, 
                            corr_obj.correlation
                        ))
            
            if high_corr_pairs:
                insights.append(f"Found {len(high_corr_pairs)} pairs of highly correlated features (|r| > 0.8)")
            
            # Model insights
            if model_id:
                model_info = ml_pipeline.get_model_info(model_id)
                metrics = model_info['metrics']
                
                if model_info['model_type'] == 'classification':
                    if metrics.get('accuracy', 0) < 0.7:
                        insights.append("Model accuracy is below 70%, consider feature engineering or different algorithms")
                    elif metrics.get('accuracy', 0) > 0.95:
                        insights.append("Very high accuracy might indicate overfitting or data leakage")
                
                feature_importance = model_info['feature_importance']
                if feature_importance:
                    top_feature = list(feature_importance.keys())[0]
                    top_importance = list(feature_importance.values())[0]
                    insights.append(f"'{top_feature}' is the most important feature with {top_importance:.3f} importance")
            
        except Exception as e:
            insights.append(f"Error generating insights: {str(e)}")
        
        return insights
    
    def generate_recommendations(self, session_id: str, model_id: str = None) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            df = data_service.load_data(session_id)
            profile = data_service.profile_data(session_id)
            
            # Data quality recommendations
            missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_percentage > 10:
                recommendations.append("Consider imputation strategies for missing values")
            
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                recommendations.append("Remove duplicate rows to improve data quality")
            
            # Feature engineering recommendations
            numerical_cols = df.select_dtypes(include=['number']).columns
            if len(numerical_cols) > 10:
                recommendations.append("Consider feature selection to reduce dimensionality")
            
            # Outlier recommendations
            outliers = profile['insights'].outliers
            outlier_cols = [col for col, info in outliers.items() if info['percentage'] > 5]
            if outlier_cols:
                recommendations.append(f"Handle outliers in columns: {', '.join(outlier_cols)}")
            
            # Model recommendations
            if model_id:
                model_info = ml_pipeline.get_model_info(model_id)
                metrics = model_info['metrics']
                
                if model_info['model_type'] == 'classification':
                    if metrics.get('accuracy', 0) < 0.7:
                        recommendations.append("Try ensemble methods or hyperparameter tuning to improve performance")
                    elif metrics.get('recall', 0) < 0.6:
                        recommendations.append("Low recall indicates missed positive cases, consider class balancing")
                
                feature_importance = model_info['feature_importance']
                if feature_importance:
                    low_importance_features = [f for f, imp in feature_importance.items() if imp < 0.01]
                    if low_importance_features:
                        recommendations.append(f"Consider removing low-importance features: {', '.join(low_importance_features[:3])}")
            
            # General recommendations
            recommendations.append("Validate model performance on unseen data")
            recommendations.append("Monitor model performance over time for concept drift")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def generate_complete_summary(self, session_id: str, model_id: str = None) -> Dict[str, Any]:
        """Generate complete summary with all components"""
        return {
            'data_summary': self.generate_data_summary(session_id),
            'model_summary': self.generate_model_summary(model_id) if model_id else None,
            'key_insights': self.generate_key_insights(session_id, model_id),
            'recommendations': self.generate_recommendations(session_id, model_id)
        }

# Global instance
summary_service = SummaryService() 