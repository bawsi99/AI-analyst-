import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserProfile, login as authLogin, register as authRegister, logout as authLogout, getProfile, getStoredProfile, isAuthenticated } from '../services/auth.ts';
import toast from 'react-hot-toast';

interface AuthContextType {
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication status on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (isAuthenticated()) {
          // Try to get cached profile first
          const cachedProfile = getStoredProfile();
          if (cachedProfile) {
            setUser(cachedProfile);
          }
          
          // Fetch fresh profile from server
          try {
            const profile = await getProfile();
            setUser(profile);
          } catch (error) {
            console.error('Failed to fetch profile:', error);
            // If profile fetch fails, clear auth state
            await authLogout();
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await authLogin({ email, password });
      
      // Fetch user profile
      const profile = await getProfile();
      setUser(profile);
      
      toast.success('Login successful!');
      
      // Redirect to dashboard after successful login
      window.location.href = '/';
    } catch (error: any) {
      console.error('Login error:', error);
      let message = 'Login failed';
      
      if (error.response?.data?.detail) {
        message = String(error.response.data.detail);
      } else if (error.message) {
        message = String(error.message);
      }
      
      toast.error(message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    try {
      setIsLoading(true);
      const response = await authRegister({ email, password, full_name: fullName });
      
      // Fetch user profile
      const profile = await getProfile();
      setUser(profile);
      
      toast.success('Registration successful!');
      
      // Redirect to dashboard after successful registration
      window.location.href = '/';
    } catch (error: any) {
      console.error('Registration error:', error);
      let message = 'Registration failed';
      
      if (error.response?.data?.detail) {
        message = String(error.response.data.detail);
      } else if (error.message) {
        message = String(error.message);
      }
      
      toast.error(message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      await authLogout();
      setUser(null);
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      // Clear state even if API call fails
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    try {
      if (isAuthenticated()) {
        const profile = await getProfile();
        setUser(profile);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // If refresh fails, logout user
      await logout();
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 