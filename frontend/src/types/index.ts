// API Response Types
export interface UploadResponse {
  message: string;
  success: boolean;
  session_id: string;
  filename: string;
}

export interface ColumnSchema {
  name: string;
  dtype: string;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  is_constant: boolean;
  is_high_cardinality: boolean;
  sample_values: string[];
}

export interface DataStatistics {
  total_rows: number;
  total_columns: number;
  memory_usage: string;
  duplicate_rows: number;
  missing_values: number;
}

export interface CorrelationPair {
  column1: string;
  column2: string;
  correlation: number;
  strength: string;
}

export interface DataInsights {
  outliers: Record<string, any>;
  skewness: Record<string, number>;
  correlations: CorrelationPair[];
  imbalanced_columns: string[];
  data_leakage: string[];
}

export interface ProfileResponse {
  message: string;
  success: boolean;
  session_id: string;
  metadata: Record<string, any>;
  schema: ColumnSchema[];
  statistics: DataStatistics;
  insights: DataInsights;
}

export interface TrainingRequest {
  target_column: string;
  model_type: string;
  algorithm?: string;
  excluded_columns?: string[];
}

export interface ModelMetrics {
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  rmse?: number;
  r2_score?: number;
}

export interface TrainingResponse {
  message: string;
  success: boolean;
  model_id: string;
  model_type: string;
  target_column: string;
  metrics: ModelMetrics;
  feature_importance: Record<string, number>;
  training_time: number;
}

export interface PredictionRequest {
  data: Record<string, any>[];
}

export interface PredictionResponse {
  message: string;
  success: boolean;
  model_id: string;
  predictions: (number | string)[];
  confidence_scores: number[];
  probabilities?: number[][];
}

export interface SummaryResponse {
  message: string;
  success: boolean;
  session_id: string;
  data_summary: string;
  model_summary?: string;
  key_insights: string[];
  recommendations: string[];
}

export interface AIAnalysisResponse {
  message: string;
  success: boolean;
  session_id: string;
  model_id?: string;
  ai_analysis: string;
  enhanced_insights: string[];
  business_recommendations: string[];
  technical_recommendations: string[];
  risk_assessment: string[];
  opportunities: string[];
}

export interface AIAnalysisStatusResponse {
  ai_analysis_available: boolean;
  message: string;
}

// Application State Types
export interface AppState {
  sessionId: string | null;
  modelId: string | null;
  featureNames: string[];
  currentStep: 'upload' | 'profile' | 'train' | 'predict' | 'summary' | 'ai-analysis';
  isLoading: boolean;
  error: string | null;
}

export interface UploadState {
  file: File | null;
  isUploading: boolean;
  uploadProgress: number;
}

export interface ProfileState {
  data: ProfileResponse | null;
  isLoading: boolean;
}

export interface TrainingState {
  targetColumn: string;
  modelType: string;
  algorithm: string;
  isTraining: boolean;
  result: TrainingResponse | null;
}

export interface PredictionState {
  inputData: Record<string, any>[];
  isPredicting: boolean;
  result: PredictionResponse | null;
}

export interface ModelFeature {
  name: string;
  dtype: string;
  unique_count: number;
  sample_values: string[];
  null_percentage: number;
}

export interface ModelFeaturesResponse {
  message: string;
  model_id: string;
  target_column: string;
  features: ModelFeature[];
}

export interface SummaryState {
  data: SummaryResponse | null;
  isLoading: boolean;
}

export interface ModelDetails {
  model: {
    id: string;
    model_id: string;
    model_type: string;
    target_column: string;
    algorithm: string;
    metrics: any;
    training_time: number;
    created_at: string;
    feature_importance: Record<string, number>;
    hyperparameters: any;
    analysis_sessions: {
      file_name: string;
      session_id: string;
    };
  };
  predictions: any[];
  summary?: {
    data_summary: string;
    model_summary?: string;
    key_insights: string[];
    recommendations: string[];
  };
  ai_analysis?: {
    ai_analysis: string;
    enhanced_insights: string[];
    business_recommendations: string[];
    technical_recommendations: string[];
    risk_assessment: string[];
    opportunities: string[];
  };
  data_insights?: {
    outliers: Record<string, any>;
    skewness: Record<string, number>;
    correlations: Array<{
      column1: string;
      column2: string;
      correlation: number;
      strength: string;
    }>;
    imbalanced_columns: string[];
    data_leakage: string[];
  };
} 