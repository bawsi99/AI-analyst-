import os
from typing import Dict, List, Any, Optional
from core.config import settings
from services.data_service import data_service
from services.summary_service import summary_service
from ml.pipeline import ml_pipeline
import pandas as pd
import json
from google import genai

class AIAnalysisService:
    def __init__(self):
        self.client = None
        self.model_name = 'gemini-2.0-flash'
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini client if API key is available"""
        try:
            if settings.GEMINI_LLM_API_KEY:
                # Set the API key as an environment variable
                os.environ['GOOGLE_API_KEY'] = settings.GEMINI_LLM_API_KEY
                self.client = genai.Client()
            else:
                print("Warning: GEMINI_LLM_API_KEY not configured. AI analysis will be disabled.")
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.client is not None
    
    def generate_ai_analysis(self, session_id: str, model_id: str = None) -> Dict[str, Any]:
        """Generate AI-powered analysis using Gemini LLM"""
        if not self.is_available():
            return {
                'ai_analysis': "AI analysis is not available. Please configure the Gemini API key.",
                'enhanced_insights': [],
                'business_recommendations': [],
                'technical_recommendations': [],
                'risk_assessment': [],
                'opportunities': []
            }
        
        try:
            # Get data and summary information
            df = data_service.load_data(session_id)
            profile_data = data_service.profile_data(session_id)
            summary_data = summary_service.generate_complete_summary(session_id, model_id)
            
            # Prepare context for AI analysis
            context = self._prepare_analysis_context(df, profile_data, summary_data, model_id)
            
            # Generate AI analysis
            ai_analysis = self._generate_ai_insights(context)
            
            return ai_analysis
            
        except Exception as e:
            return {
                'ai_analysis': f"Error generating AI analysis: {str(e)}",
                'enhanced_insights': [],
                'business_recommendations': [],
                'technical_recommendations': [],
                'risk_assessment': [],
                'opportunities': []
            }
    
    def _prepare_analysis_context(self, df: pd.DataFrame, profile_data: Dict, 
                                summary_data: Dict, model_id: str = None) -> str:
        """Prepare comprehensive context for AI analysis"""
        context_parts = []
        
        # Dataset overview
        context_parts.append(f"Dataset Overview:")
        context_parts.append(f"- Rows: {len(df):,}")
        context_parts.append(f"- Columns: {len(df.columns)}")
        context_parts.append(f"- Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # Column information
        context_parts.append(f"\nColumn Information:")
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            unique_count = df[col].nunique()
            context_parts.append(f"- {col}: {dtype}, {null_count} nulls ({null_pct:.1f}%), {unique_count} unique values")
        
        # Data quality insights
        context_parts.append(f"\nData Quality Insights:")
        context_parts.append(summary_data.get('data_summary', ''))
        
        # Key insights
        if summary_data.get('key_insights'):
            context_parts.append(f"\nKey Insights:")
            for insight in summary_data['key_insights']:
                context_parts.append(f"- {insight}")
        
        # Model information if available
        if model_id:
            try:
                model_info = ml_pipeline.get_model_info(model_id)
                context_parts.append(f"\nModel Information:")
                context_parts.append(f"- Type: {model_info['model_type']}")
                context_parts.append(f"- Algorithm: {model_info['algorithm']}")
                context_parts.append(f"- Target: {model_info['target_column']}")
                context_parts.append(f"- Metrics: {json.dumps(model_info['metrics'], indent=2)}")
                context_parts.append(f"- Training time: {model_info['training_time']:.2f} seconds")
                
                if model_info.get('feature_importance'):
                    context_parts.append(f"- Top features: {list(model_info['feature_importance'].keys())[:5]}")
            except Exception as e:
                context_parts.append(f"\nModel Information: Error retrieving model info - {str(e)}")
        
        # Recommendations
        if summary_data.get('recommendations'):
            context_parts.append(f"\nCurrent Recommendations:")
            for rec in summary_data['recommendations']:
                context_parts.append(f"- {rec}")
        
        return "\n".join(context_parts)
    
    def _generate_ai_insights(self, context: str) -> Dict[str, Any]:
        """Generate AI insights using Gemini (user's exact implementation)"""
        try:
            prompt = f"""
You are an expert data scientist and business analyst. Based on the following dataset analysis, provide:

1. **AI Analysis**: A comprehensive, natural language analysis of the dataset and model performance (if available). Focus on patterns, trends, and business implications.

2. **Enhanced Insights**: 3-5 deeper insights that go beyond basic statistics, including potential hidden patterns or relationships.

3. **Business Recommendations**: 3-5 actionable business recommendations based on the data insights.

4. **Technical Recommendations**: 3-5 technical recommendations for improving the model or data quality.

5. **Risk Assessment**: 2-3 potential risks or concerns identified from the analysis.

6. **Opportunities**: 2-3 business opportunities or areas for further investigation.

Dataset Analysis Context:
{context}

Please provide your analysis in a structured, professional manner. Focus on practical insights that would be valuable for business decision-making.
"""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            ai_text = response.text
            sections = self._parse_ai_response(ai_text)
            return {
                'ai_analysis': sections.get('ai_analysis', ai_text),
                'enhanced_insights': sections.get('enhanced_insights', []),
                'business_recommendations': sections.get('business_recommendations', []),
                'technical_recommendations': sections.get('technical_recommendations', []),
                'risk_assessment': sections.get('risk_assessment', []),
                'opportunities': sections.get('opportunities', [])
            }
        except Exception as e:
            return {
                'ai_analysis': f"Error generating AI insights: {str(e)}",
                'enhanced_insights': [],
                'business_recommendations': [],
                'technical_recommendations': [],
                'risk_assessment': [],
                'opportunities': []
            }
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        sections = {
            'ai_analysis': '',
            'enhanced_insights': [],
            'business_recommendations': [],
            'technical_recommendations': [],
            'risk_assessment': [],
            'opportunities': []
        }
        lines = response_text.split('\n')
        current_section = 'ai_analysis'
        current_content = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            lower_line = line.lower()
            if 'enhanced insights' in lower_line or 'deeper insights' in lower_line:
                if current_content:
                    sections[current_section] = '\n'.join(current_content) if current_section == 'ai_analysis' else current_content
                current_section = 'enhanced_insights'
                current_content = []
            elif 'business recommendations' in lower_line:
                if current_content:
                    sections[current_section] = '\n'.join(current_content) if current_section == 'ai_analysis' else current_content
                current_section = 'business_recommendations'
                current_content = []
            elif 'technical recommendations' in lower_line:
                if current_content:
                    sections[current_section] = '\n'.join(current_content) if current_section == 'ai_analysis' else current_content
                current_section = 'technical_recommendations'
                current_content = []
            elif 'risk assessment' in lower_line or 'risks' in lower_line:
                if current_content:
                    sections[current_section] = '\n'.join(current_content) if current_section == 'ai_analysis' else current_content
                current_section = 'risk_assessment'
                current_content = []
            elif 'opportunities' in lower_line:
                if current_content:
                    sections[current_section] = '\n'.join(current_content) if current_section == 'ai_analysis' else current_content
                current_section = 'opportunities'
                current_content = []
            else:
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    if current_section != 'ai_analysis':
                        current_content.append(line.lstrip('-•* ').strip())
                else:
                    if current_section == 'ai_analysis':
                        current_content.append(line)
        if current_content:
            sections[current_section] = '\n'.join(current_content) if current_section == 'ai_analysis' else current_content
        return sections

ai_analysis_service = AIAnalysisService() 