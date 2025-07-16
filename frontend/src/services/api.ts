import axios from 'axios';
import {
  UploadResponse,
  ProfileResponse,
  TrainingRequest,
  TrainingResponse,
  PredictionRequest,
  PredictionResponse,
  SummaryResponse,
  AIAnalysisResponse,
  AIAnalysisStatusResponse,
} from '../types/index.ts';
import { getAccessToken } from './auth.ts';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    
    // Add auth token if available
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401) {
      // Clear auth tokens and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_profile');
      window.location.href = '/auth';
    }
    
    return Promise.reject(error);
  }
);

export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getProfile = async (sessionId: string): Promise<ProfileResponse> => {
  const response = await api.get(`/profile/${sessionId}`);
  return response.data;
};

export const trainModel = async (
  sessionId: string,
  request: TrainingRequest
): Promise<TrainingResponse> => {
  const response = await api.post(`/train/${sessionId}`, request, {
    timeout: 300000, // 5 minutes timeout for model training
  });
  return response.data;
};

export const makePrediction = async (
  modelId: string,
  request: PredictionRequest
): Promise<PredictionResponse> => {
  const response = await api.post(`/predict/${modelId}`, request);
  return response.data;
};

export const getSummary = async (
  sessionId: string,
  modelId?: string
): Promise<SummaryResponse> => {
  const params = modelId ? { model_id: modelId } : {};
  const response = await api.get(`/summary/${sessionId}`, { params });
  return response.data;
};

export const getAIAnalysis = async (
  sessionId: string,
  modelId?: string
): Promise<AIAnalysisResponse> => {
  const params = modelId ? { model_id: modelId } : {};
  const response = await api.get(`/ai-analysis/${sessionId}`, { params });
  return response.data;
};

export const checkAIAnalysisStatus = async (): Promise<AIAnalysisStatusResponse> => {
  const response = await api.get('/ai-analysis/status/health');
  return response.data;
};

export const exportReport = async (sessionId: string, modelId?: string): Promise<void> => {
  const params = modelId ? { model_id: modelId } : {};
  
  try {
    const response = await api.get(`/export/report/${sessionId}`, { 
      params,
      responseType: 'blob'
    });
    
    // Check if the response is actually an error (JSON error response)
    const contentType = response.headers['content-type'];
    if (contentType && contentType.includes('application/json')) {
      // This is an error response, not a file
      const text = await response.data.text();
      const errorData = JSON.parse(text);
      throw new Error(errorData.detail || 'Export failed');
    }
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `analysis_report_${sessionId}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    if (error.response?.status === 404) {
      throw new Error('Session not found. Please upload data and complete the analysis first.');
    }
    throw error;
  }
};

export const downloadModel = async (modelId: string): Promise<void> => {
  try {
    const response = await api.get(`/export/model/${modelId}`, {
      responseType: 'blob'
    });
    
    // Check if the response is actually an error (JSON error response)
    const contentType = response.headers['content-type'];
    if (contentType && contentType.includes('application/json')) {
      // This is an error response, not a file
      const text = await response.data.text();
      const errorData = JSON.parse(text);
      throw new Error(errorData.detail || 'Download failed');
    }
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `model_${modelId}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.joblib`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    if (error.response?.status === 404) {
      throw new Error('Model not found. Please train a model first.');
    }
    throw error;
  }
};

export const shareResults = async (sessionId: string, modelId?: string): Promise<void> => {
  const params = modelId ? { model_id: modelId } : {};
  
  try {
    const response = await api.get(`/export/share/${sessionId}`, {
      params,
      responseType: 'blob'
    });
    
    // Check if the response is actually an error (JSON error response)
    const contentType = response.headers['content-type'];
    if (contentType && contentType.includes('application/json')) {
      // This is an error response, not a file
      const text = await response.data.text();
      const errorData = JSON.parse(text);
      throw new Error(errorData.detail || 'Share failed');
    }
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `analysis_results_${sessionId}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.zip`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    if (error.response?.status === 404) {
      throw new Error('Session not found. Please upload data and complete the analysis first.');
    }
    throw error;
  }
};

// Dashboard API functions
export const getUserStats = async () => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

export const getUserModels = async (limit: number = 50, offset: number = 0) => {
  const response = await api.get('/dashboard/models', {
    params: { limit, offset }
  });
  return response.data;
};

export const getUserSessions = async (limit: number = 50, offset: number = 0) => {
  const response = await api.get('/dashboard/sessions', {
    params: { limit, offset }
  });
  return response.data;
};

export const getPredictionHistory = async (modelId?: string, limit: number = 50, offset: number = 0) => {
  const params: any = { limit, offset };
  if (modelId) params.model_id = modelId;
  
  const response = await api.get('/dashboard/predictions', { params });
  return response.data;
};

export const getSessionDetails = async (sessionId: string) => {
  const response = await api.get(`/dashboard/sessions/${sessionId}`);
  return response.data;
};

export const getModelDetails = async (modelId: string) => {
  const response = await api.get(`/dashboard/models/${modelId}`);
  return response.data;
};

export const getModelFeatures = async (modelId: string) => {
  const response = await api.get(`/dashboard/models/${modelId}/features`);
  return response.data;
};

export default api; 