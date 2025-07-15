import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext.tsx';
import ProtectedRoute from './components/ProtectedRoute.tsx';
import AuthLayout from './components/AuthLayout.tsx';
import Dashboard from './components/Dashboard.tsx';
import UserDashboard from './components/UserDashboard.tsx';
import ModelPredictions from './components/ModelPredictions.tsx';
import About from './components/About.tsx';
import Header from './components/Header.tsx';
import ErrorBoundary from './components/ErrorBoundary.tsx';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              {/* Public auth routes */}
              <Route path="/auth" element={<AuthLayout />} />
              
              {/* Protected dashboard route */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <>
                      <Header />
                      <main className="container mx-auto px-4 py-8">
                        <UserDashboard />
                      </main>
                    </>
                  </ProtectedRoute>
                }
              />
              
              {/* New analysis workflow */}
              <Route
                path="/new-analysis"
                element={
                  <ProtectedRoute>
                    <>
                      <Header />
                      <main className="container mx-auto px-4 py-8">
                        <Dashboard />
                      </main>
                    </>
                  </ProtectedRoute>
                }
              />
              
              {/* Model predictions */}
              <Route
                path="/predict/:modelId?"
                element={
                  <ProtectedRoute>
                    <>
                      <Header />
                      <main className="container mx-auto px-4 py-8">
                        <ModelPredictions />
                      </main>
                    </>
                  </ProtectedRoute>
                }
              />
              
              {/* About page */}
              <Route
                path="/about"
                element={
                  <ProtectedRoute>
                    <>
                      <Header />
                      <main className="container mx-auto px-4 py-8">
                        <About />
                      </main>
                    </>
                  </ProtectedRoute>
                }
              />
              
              {/* Redirect any unknown routes to dashboard */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#10B981',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#EF4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App; 