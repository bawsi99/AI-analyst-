from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

# Base schemas
class BaseResponse(BaseModel):
    message: str
    success: bool = True

# Upload schemas
class UploadResponse(BaseResponse):
    session_id: str
    filename: str

# Profile schemas
class ColumnSchema(BaseModel):
    name: str
    dtype: str
    null_count: int
    null_percentage: float
    unique_count: int
    is_constant: bool
    is_high_cardinality: bool
    sample_values: List[str]

class DataStatistics(BaseModel):
    total_rows: int
    total_columns: int
    memory_usage: str
    duplicate_rows: int
    missing_values: int

class CorrelationPair(BaseModel):
    column1: str
    column2: str
    correlation: float
    strength: str

class DataInsights(BaseModel):
    outliers: Dict[str, Any]
    skewness: Dict[str, float]
    correlations: List[CorrelationPair]
    imbalanced_columns: List[str]
    data_leakage: List[str]

class ProfileResponse(BaseResponse):
    model_config = ConfigDict(protected_namespaces=())
    session_id: str
    metadata: Dict[str, Any]
    schema: List[ColumnSchema]
    statistics: DataStatistics
    insights: DataInsights

# Training schemas
class TrainingRequest(BaseModel):
    target_column: str
    model_type: str = Field(default="auto", description="auto, classification, regression")
    algorithm: Optional[str] = Field(default=None, description="random_forest, xgboost, logistic_regression")
    excluded_columns: Optional[List[str]] = Field(default=None, description="List of columns to exclude from training")

class ModelMetrics(BaseModel):
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    rmse: Optional[float] = None
    r2_score: Optional[float] = None

class TrainingResponse(BaseResponse):
    model_config = ConfigDict(protected_namespaces=())
    model_id: str
    model_type: str
    target_column: str
    metrics: ModelMetrics
    feature_importance: Dict[str, float]
    training_time: float

# Prediction schemas
class PredictionRequest(BaseModel):
    data: List[Dict[str, Any]]

class PredictionResponse(BaseResponse):
    model_id: str
    predictions: List[Union[int, float, str]]
    confidence_scores: List[float]
    probabilities: Optional[List[List[float]]] = None

# Summary schemas
class SummaryResponse(BaseResponse):
    model_config = ConfigDict(protected_namespaces=())
    session_id: str
    data_summary: str
    model_summary: Optional[str] = None
    key_insights: List[str]
    recommendations: List[str]

# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Session schemas
class SessionInfo(BaseModel):
    session_id: str
    filename: str
    upload_time: datetime
    file_size: int
    status: str
    model_id: Optional[str] = None

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# User Profile Schemas
class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

# Authentication Schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class AuthResponse(BaseModel):
    message: str
    user: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_sessions: int
    total_models: int
    total_predictions: int
    recent_sessions: List[Dict[str, Any]]
    recent_models: List[Dict[str, Any]]

class PaginatedResponse(BaseModel):
    message: str
    data: List[Dict[str, Any]]
    pagination: Dict[str, Any]

# Background Task Schemas
class BackgroundTaskResponse(BaseModel):
    message: str
    task_id: str
    task_type: str
    session_id: Optional[str] = None
    model_id: Optional[str] = None

class TaskStatusResponse(BaseModel):
    task_id: str
    state: str
    status: Optional[str] = None
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# AI Analysis Schemas
class AIAnalysisResponse(BaseModel):
    message: str
    success: bool
    session_id: str
    model_id: Optional[str] = None
    ai_analysis: str
    enhanced_insights: List[str]
    business_recommendations: List[str]
    technical_recommendations: List[str]
    risk_assessment: List[str]
    opportunities: List[str]

class AIAnalysisStatusResponse(BaseModel):
    ai_analysis_available: bool
    message: str 