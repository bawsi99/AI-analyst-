import React, { useState, useEffect } from 'react';
import { Brain, Plus, BarChart3, TrendingUp, Clock, FileText, Upload, Users, Activity } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext.tsx';
import { getUserStats, getUserModels, getUserSessions } from '../services/api.ts';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';

interface DashboardStats {
  total_sessions: number;
  total_models: number;
  total_predictions: number;
  recent_sessions: any[];
  recent_models: any[];
}

interface UserModel {
  id: string;
  model_id: string;
  model_type: string;
  target_column: string;
  algorithm: string;
  metrics: any;
  created_at: string;
  analysis_sessions: {
    filename: string;
    session_id: string;
  };
}

interface UserSession {
  id: string;
  session_id: string;
  filename: string;
  status: string;
  created_at: string;
}

const UserDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [models, setModels] = useState<UserModel[]>([]);
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'models' | 'sessions'>('overview');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [statsData, modelsData, sessionsData] = await Promise.all([
        getUserStats(),
        getUserModels(),
        getUserSessions()
      ]);
      
      setStats(statsData.stats);
      setModels(modelsData.models);
      setSessions(sessionsData.sessions);
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
      console.error('Dashboard load error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'trained': return 'bg-blue-100 text-blue-800';
      case 'profiled': return 'bg-yellow-100 text-yellow-800';
      case 'uploaded': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user?.full_name || user?.email}!
            </h1>
            <p className="text-gray-600 mt-1">
              Manage your AI models and analysis sessions
            </p>
          </div>
          <Link
            to="/new-analysis"
            className="btn-primary flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Analysis
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-4">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.total_sessions}</p>
            <p className="text-sm text-gray-600">Analysis Sessions</p>
          </div>
          
          <div className="card text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-4">
              <Brain className="h-6 w-6 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.total_models}</p>
            <p className="text-sm text-gray-600">Trained Models</p>
          </div>
          
          <div className="card text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-4">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.total_predictions}</p>
            <p className="text-sm text-gray-600">Predictions Made</p>
          </div>
          
          <div className="card text-center">
            <div className="flex items-center justify-center w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-4">
              <Activity className="h-6 w-6 text-orange-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {models.filter(m => new Date(m.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length}
            </p>
            <p className="text-sm text-gray-600">Models This Week</p>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('models')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'models'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              My Models ({models.length})
            </button>
            <button
              onClick={() => setActiveTab('sessions')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'sessions'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Sessions ({sessions.length})
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="mt-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Recent Models */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Models</h3>
                {models.slice(0, 5).length > 0 ? (
                  <div className="space-y-3">
                    {models.slice(0, 5).map((model) => (
                      <div key={model.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Brain className="h-5 w-5 text-green-600" />
                          <div>
                                                     <p className="font-medium text-gray-900">
                           {model.analysis_sessions?.file_name || 'Unknown Dataset'}
                         </p>
                            <p className="text-sm text-gray-500">
                              {model.algorithm} • {model.target_column}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">{formatDate(model.created_at)}</p>
                          <p className="text-sm font-medium text-green-600">
                            {(model.metrics?.accuracy * 100).toFixed(1)}% accuracy
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 mb-6">No models yet. Start your first analysis!</p>
                    <Link to="/new-analysis" className="btn-primary">
                      Create First Model
                    </Link>
                  </div>
                )}
              </div>

              {/* Recent Sessions */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Sessions</h3>
                {sessions.slice(0, 5).length > 0 ? (
                  <div className="space-y-3">
                    {sessions.slice(0, 5).map((session) => (
                      <div key={session.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-blue-600" />
                          <div>
                            <p className="font-medium text-gray-900">{session.filename}</p>
                            <p className="text-sm text-gray-500">Session {session.session_id}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">{formatDate(session.created_at)}</p>
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(session.status)}`}>
                            {session.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No analysis sessions yet.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'models' && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-medium text-gray-900">All Models</h3>
                <Link to="/new-analysis" className="btn-secondary">
                  <Plus className="h-4 w-4 mr-2" />
                  Train New Model
                </Link>
              </div>
              
              {models.length > 0 ? (
                <div className="space-y-4">
                  {models.map((model) => (
                    <div key={model.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <Brain className="h-6 w-6 text-green-600" />
                          <div>
                                                         <h4 className="text-lg font-medium text-gray-900">
                               {model.analysis_sessions?.file_name || 'Unknown Dataset'}
                             </h4>
                            <p className="text-sm text-gray-500">
                              {model.algorithm} • Target: {model.target_column}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">{formatDate(model.created_at)}</p>
                          <p className="text-lg font-bold text-green-600">
                            {(model.metrics?.accuracy * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600">
                            {(model.metrics?.precision * 100).toFixed(1)}%
                          </p>
                          <p className="text-xs text-gray-500">Precision</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-600">
                            {(model.metrics?.recall * 100).toFixed(1)}%
                          </p>
                          <p className="text-xs text-gray-500">Recall</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-orange-600">
                            {(model.metrics?.f1_score * 100).toFixed(1)}%
                          </p>
                          <p className="text-xs text-gray-500">F1 Score</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-gray-600">
                            {model.training_time?.toFixed(1)}s
                          </p>
                          <p className="text-xs text-gray-500">Training Time</p>
                        </div>
                      </div>
                      
                      <div className="flex space-x-3">
                        <Link
                          to={`/predict/${model.model_id}`}
                          className="btn-primary flex-1 text-center"
                        >
                          <TrendingUp className="h-4 w-4 mr-2" />
                          Make Predictions
                        </Link>
                        <button className="btn-secondary">
                          <BarChart3 className="h-4 w-4 mr-2" />
                          View Details
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Brain className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No models yet</h3>
                  <p className="text-gray-500 mb-6">Start by uploading data and training your first model.</p>
                  <Link to="/new-analysis" className="btn-primary">
                    <Upload className="h-4 w-4 mr-2" />
                    Start First Analysis
                  </Link>
                </div>
              )}
            </div>
          )}

          {activeTab === 'sessions' && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-medium text-gray-900">All Sessions</h3>
                <Link to="/new-analysis" className="btn-secondary">
                  <Plus className="h-4 w-4 mr-2" />
                  New Session
                </Link>
              </div>
              
              {sessions.length > 0 ? (
                <div className="space-y-4">
                  {sessions.map((session) => (
                    <div key={session.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-6 w-6 text-blue-600" />
                          <div>
                            <h4 className="text-lg font-medium text-gray-900">{session.filename}</h4>
                            <p className="text-sm text-gray-500">Session ID: {session.session_id}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">{formatDate(session.created_at)}</p>
                          <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(session.status)}`}>
                            {session.status}
                          </span>
                        </div>
                      </div>
                      
                      <div className="mt-4 flex space-x-3">
                        <Link
                          to={`/session/${session.session_id}`}
                          className="btn-primary flex-1 text-center"
                        >
                          <BarChart3 className="h-4 w-4 mr-2" />
                          View Analysis
                        </Link>
                        <button className="btn-secondary">
                          <Clock className="h-4 w-4 mr-2" />
                          Continue
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No sessions yet</h3>
                  <p className="text-gray-500 mb-6">Start your first data analysis session.</p>
                  <Link to="/new-analysis" className="btn-primary">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Data
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserDashboard; 