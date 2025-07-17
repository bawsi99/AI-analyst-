import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://orthoaiassgnment.onrender.com/api/v1';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  message: string;
  user: {
    id: string;
    email: string;
  };
  access_token: string;
  refresh_token: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  created_at: string;
}

// Create axios instance for auth requests
const authApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
authApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await authApi.post('/auth/refresh', {
            refresh_token: refreshToken
          });
          
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return authApi(originalRequest);
        } catch (refreshError) {
          // Refresh failed, logout user
          logout();
          return Promise.reject(refreshError);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Helper function to extract error message
const extractErrorMessage = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

// Auth functions
export const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
  try {
    const response = await authApi.post('/auth/login', credentials);
    const data = response.data;
    
    // Store tokens
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
    }
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }
    
    return data;
  } catch (error: any) {
    const message = extractErrorMessage(error);
    throw new Error(message);
  }
};

export const register = async (userData: RegisterRequest): Promise<AuthResponse> => {
  try {
    const response = await authApi.post('/auth/register', userData);
    const data = response.data;
    
    // Store tokens
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
    }
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }
    
    return data;
  } catch (error: any) {
    const message = extractErrorMessage(error);
    throw new Error(message);
  }
};

export const logout = async (): Promise<void> => {
  try {
    await authApi.post('/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Clear tokens regardless of API call success
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_profile');
  }
};

export const getProfile = async (): Promise<UserProfile> => {
  try {
    const response = await authApi.get('/auth/profile');
    const profile = response.data;
    
    // Cache profile
    localStorage.setItem('user_profile', JSON.stringify(profile));
    
    return profile;
  } catch (error: any) {
    const message = extractErrorMessage(error);
    throw new Error(message);
  }
};

export const updateProfile = async (profileData: Partial<UserProfile>): Promise<void> => {
  try {
    await authApi.put('/auth/profile', profileData);
    
    // Update cached profile
    const currentProfile = JSON.parse(localStorage.getItem('user_profile') || '{}');
    const updatedProfile = { ...currentProfile, ...profileData };
    localStorage.setItem('user_profile', JSON.stringify(updatedProfile));
  } catch (error: any) {
    const message = extractErrorMessage(error);
    throw new Error(message);
  }
};

// Utility functions
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token');
};

export const getStoredProfile = (): UserProfile | null => {
  const profile = localStorage.getItem('user_profile');
  return profile ? JSON.parse(profile) : null;
};

export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
}; 