import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Brain, TrendingUp, BarChart3, Clock, FileText, ArrowLeft } from 'lucide-react';
import { getModelDetails } from '../services/api.ts';
import toast from 'react-hot-toast';

interface ModelDetailsData {
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

const ModelDetails: React.FC = () => {
  const { modelId } = useParams<{ modelId: string }>();
  const navigate = useNavigate();
  const [modelDetails, setModelDetails] = useState<ModelDetailsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadModelDetails = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await getModelDetails(modelId!);
      console.log('Model details received:', data);
      console.log('Summary data:', data.summary);
      console.log('AI analysis data:', data.ai_analysis);
      console.log('Data insights:', data.data_insights);
      setModelDetails(data);
    } catch (error: any) {
      toast.error('Failed to load model details');
      console.error('Load model details error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [modelId]);

  useEffect(() => {
    if (modelId) {
      loadModelDetails();
    }
  }, [modelId, loadModelDetails]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPrimaryMetric = (model: any) => {
    const { model_type, algorithm, metrics } = model;
    
    if (!metrics) return { value: 0, label: 'N/A', color: 'text-gray-600' };
    
    if (model_type === 'classification') {
      if (algorithm === 'logistic_regression') {
        return {
          value: metrics.precision || 0,
          label: 'Precision',
          color: 'text-green-600'
        };
      } else if (algorithm === 'xgboost') {
        return {
          value: metrics.f1_score || 0,
          label: 'F1-Score',
          color: 'text-purple-600'
        };
      } else {
        return {
          value: metrics.accuracy || 0,
          label: 'Accuracy',
          color: 'text-blue-600'
        };
      }
    } else if (model_type === 'regression') {
      return {
        value: metrics.r2_score || 0,
        label: 'R² Score',
        color: 'text-orange-600'
      };
    }
    
    return {
      value: metrics.accuracy || 0,
      label: 'Accuracy',
      color: 'text-gray-600'
    };
  };

  const formatMetricValue = (value: number, label: string) => {
    if (label === 'R² Score' || label === 'RMSE') {
      return value.toFixed(3);
    }
    return (value * 100).toFixed(1) + '%';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading model details...</p>
        </div>
      </div>
    );
  }

  if (!modelDetails) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Model not found</p>
        <Link to="/" className="btn-primary mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const { model, predictions, summary, ai_analysis, data_insights } = modelDetails;
  const primaryMetric = getPrimaryMetric(model);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="btn-secondary"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Model Details</h1>
            <p className="text-gray-600">
              {model.analysis_sessions?.file_name || 'Unknown Dataset'}
            </p>
          </div>
        </div>
        <div className="flex space-x-3">
          <Link
            to={`/predict/${model.model_id}`}
            className="btn-primary"
          >
            <TrendingUp className="h-4 w-4 mr-2" />
            Make Predictions
          </Link>
        </div>
      </div>

      {/* Model Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Model Information */}
          <div className="card">
            <div className="flex items-center mb-4">
              <Brain className="h-5 w-5 text-gray-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Model Information</h3>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Model Type</p>
                <p className="font-medium text-gray-900 capitalize">{model.model_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Algorithm</p>
                <p className="font-medium text-gray-900 capitalize">{model.algorithm}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Target Column</p>
                <p className="font-medium text-gray-900">{model.target_column}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Training Time</p>
                <p className="font-medium text-gray-900">{model.training_time?.toFixed(2)}s</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Created</p>
                <p className="font-medium text-gray-900">{formatDate(model.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Model ID</p>
                <p className="font-medium text-gray-900 font-mono text-sm">{model.model_id}</p>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="card">
            <div className="flex items-center mb-4">
              <BarChart3 className="h-5 w-5 text-gray-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Performance Metrics</h3>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {model.model_type === 'classification' ? (
                <>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">
                      {(model.metrics?.accuracy * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-blue-700">Accuracy</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">
                      {(model.metrics?.precision * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-green-700">Precision</p>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <p className="text-2xl font-bold text-yellow-600">
                      {(model.metrics?.recall * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-yellow-700">Recall</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-2xl font-bold text-purple-600">
                      {(model.metrics?.f1_score * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-purple-700">F1-Score</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">
                      {model.metrics?.r2_score?.toFixed(3)}
                    </p>
                    <p className="text-sm text-blue-700">R² Score</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">
                      {model.metrics?.rmse?.toFixed(3)}
                    </p>
                    <p className="text-sm text-green-700">RMSE</p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Feature Importance */}
          {model.feature_importance && Object.keys(model.feature_importance).length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <TrendingUp className="h-5 w-5 text-gray-500 mr-2" />
                <h3 className="text-lg font-medium text-gray-900">Feature Importance</h3>
              </div>
              
              <div className="space-y-2">
                {Object.entries(model.feature_importance)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 10)
                  .map(([feature, importance]) => (
                    <div key={feature} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{feature}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${(importance * 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-500 w-12 text-right">
                          {(importance * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Primary Metric */}
          <div className="card text-center">
            <div className="mb-2">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <Brain className="h-8 w-8 text-gray-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900">Primary Metric</h3>
            </div>
            <div className={`text-3xl font-bold ${primaryMetric.color} mb-2`}>
              {formatMetricValue(primaryMetric.value, primaryMetric.label)}
            </div>
            <p className="text-sm text-gray-500 mb-2">{primaryMetric.label}</p>
            <div className="text-center">
              <div className="inline-flex items-center px-3 py-1 bg-gray-100 rounded-full">
                <TrendingUp className="h-4 w-4 text-gray-600 mr-2" />
                <span className="text-sm text-gray-700">Model Performance</span>
              </div>
            </div>
          </div>

          {/* Recent Predictions */}
          <div className="card">
            <div className="flex items-center mb-6">
              <Clock className="h-5 w-5 text-gray-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Recent Predictions</h3>
            </div>
            
            {predictions && predictions.length > 0 ? (
              <div className="space-y-4">
                {predictions.slice(0, 4).map((prediction, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        #{index + 1}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatDate(prediction.created_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {prediction.prediction}
                      </p>
                      {prediction.confidence && (
                        <p className="text-xs text-gray-500">
                          {(prediction.confidence * 100).toFixed(1)}%
                        </p>
                      )}
                    </div>
                  </div>
                ))}
                {predictions.length > 4 && (
                  <div className="text-center pt-2">
                    <Link
                      to={`/predict/${model.model_id}`}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      View all {predictions.length} predictions →
                    </Link>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <TrendingUp className="h-8 w-8 text-gray-400 mx-auto mb-3" />
                <p className="text-sm text-gray-500 mb-4">No predictions yet</p>
                <Link
                  to={`/predict/${model.model_id}`}
                  className="btn-primary"
                >
                  Make First Prediction
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Summary Section */}
      {summary && (
        <div className="space-y-6">
          {/* Data Summary */}
          <div className="card">
            <div className="flex items-center mb-4">
              <FileText className="h-5 w-5 text-blue-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Data Summary</h3>
            </div>
            <div className="prose prose-sm max-w-none">
              <p className="text-gray-700 leading-relaxed">{summary.data_summary}</p>
            </div>
          </div>

          {/* Model Summary */}
          {summary.model_summary && (
            <div className="card">
              <div className="flex items-center mb-4">
                <TrendingUp className="h-5 w-5 text-green-500 mr-2" />
                <h3 className="text-lg font-medium text-gray-900">Model Summary</h3>
              </div>
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 leading-relaxed">{summary.model_summary}</p>
              </div>
            </div>
          )}

          {/* Key Insights */}
          {summary.key_insights && summary.key_insights.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-yellow-500 mr-2">💡</div>
                <h3 className="text-lg font-medium text-gray-900">Key Insights</h3>
              </div>
              <div className="space-y-3">
                {summary.key_insights.map((insight, index) => (
                  <div key={index} className="flex items-start p-3 bg-yellow-50 rounded-lg">
                    <div className="h-4 w-4 text-yellow-600 mr-3 mt-0.5 flex-shrink-0">💡</div>
                    <p className="text-sm text-yellow-800">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {summary.recommendations && summary.recommendations.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-purple-500 mr-2">📋</div>
                <h3 className="text-lg font-medium text-gray-900">Recommendations</h3>
              </div>
              <div className="space-y-3">
                {summary.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start p-3 bg-purple-50 rounded-lg">
                    <div className="h-4 w-4 text-purple-600 mr-3 mt-0.5 flex-shrink-0">📋</div>
                    <p className="text-sm text-purple-800">{recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Data Analysis Section */}
      {data_insights && (
        <div className="space-y-6">
          <div className="flex items-center mb-6">
            <BarChart3 className="h-6 w-6 text-indigo-500 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900">Data Analysis</h2>
          </div>

          {/* Outliers */}
          {data_insights.outliers && Object.keys(data_insights.outliers).length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-red-500 mr-2">⚠️</div>
                <h3 className="text-lg font-medium text-gray-900">Outlier Detection</h3>
              </div>
              <div className="space-y-2">
                {Object.entries(data_insights.outliers).map(([column, info]: [string, any]) => (
                  <div key={column} className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                    <span className="font-medium text-gray-900">{column}</span>
                    <span className="text-sm text-red-600">
                      {info.count} outliers ({info.percentage.toFixed(1)}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Correlations */}
          {data_insights.correlations && data_insights.correlations.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-blue-500 mr-2">🔗</div>
                <h3 className="text-lg font-medium text-gray-900">Feature Correlations</h3>
              </div>
              <div className="space-y-2">
                {data_insights.correlations
                  .filter(corr => Math.abs(corr.correlation) > 0.5)
                  .slice(0, 10)
                  .map((corr, index) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-900">
                          {corr.column1} ↔ {corr.column2}
                        </span>
                        <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                          corr.strength === 'very_strong' ? 'bg-red-100 text-red-800' :
                          corr.strength === 'strong' ? 'bg-orange-100 text-orange-800' :
                          corr.strength === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {corr.strength.replace('_', ' ')}
                        </span>
                      </div>
                      <span className="text-sm text-blue-600">{corr.correlation.toFixed(3)}</span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Skewness */}
          {data_insights.skewness && Object.keys(data_insights.skewness).length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-green-500 mr-2">📊</div>
                <h3 className="text-lg font-medium text-gray-900">Data Distribution (Skewness)</h3>
              </div>
              <div className="space-y-2">
                {Object.entries(data_insights.skewness)
                  .filter(([_, skewness]) => Math.abs(skewness) > 1)
                  .slice(0, 8)
                  .map(([column, skewness]) => (
                    <div key={column} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <span className="font-medium text-gray-900">{column}</span>
                      <span className={`text-sm ${
                        Math.abs(skewness) > 2 ? 'text-red-600' :
                        Math.abs(skewness) > 1 ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {skewness > 0 ? 'Right-skewed' : 'Left-skewed'} ({skewness.toFixed(2)})
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Imbalanced Columns */}
          {data_insights.imbalanced_columns && data_insights.imbalanced_columns.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-yellow-500 mr-2">⚖️</div>
                <h3 className="text-lg font-medium text-gray-900">Imbalanced Features</h3>
              </div>
              <div className="space-y-2">
                {data_insights.imbalanced_columns.map((column) => (
                  <div key={column} className="flex items-center p-3 bg-yellow-50 rounded-lg">
                    <div className="h-4 w-4 text-yellow-600 mr-3">⚖️</div>
                    <span className="text-sm text-yellow-800">{column}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Leakage */}
          {data_insights.data_leakage && data_insights.data_leakage.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-red-500 mr-2">🚨</div>
                <h3 className="text-lg font-medium text-gray-900">Data Leakage Detection</h3>
              </div>
              <div className="space-y-2">
                {data_insights.data_leakage.map((leakage, index) => (
                  <div key={index} className="flex items-start p-3 bg-red-50 rounded-lg">
                    <div className="h-4 w-4 text-red-600 mr-3 mt-0.5 flex-shrink-0">🚨</div>
                    <p className="text-sm text-red-800">{leakage}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* AI Analysis Section */}
      {ai_analysis && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center mb-4">
              <div className="h-5 w-5 text-indigo-500 mr-2">🤖</div>
              <h3 className="text-lg font-medium text-gray-900">AI-Powered Analysis</h3>
            </div>
            <div className="prose prose-sm max-w-none">
              <p className="text-gray-700 leading-relaxed">{ai_analysis.ai_analysis}</p>
            </div>
          </div>

          {/* Enhanced Insights */}
          {ai_analysis.enhanced_insights && ai_analysis.enhanced_insights.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-indigo-500 mr-2">🔍</div>
                <h3 className="text-lg font-medium text-gray-900">Enhanced Insights</h3>
              </div>
              <div className="space-y-3">
                {ai_analysis.enhanced_insights.map((insight, index) => (
                  <div key={index} className="flex items-start p-3 bg-indigo-50 rounded-lg">
                    <div className="h-4 w-4 text-indigo-600 mr-3 mt-0.5 flex-shrink-0">🔍</div>
                    <p className="text-sm text-indigo-800">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Business Recommendations */}
          {ai_analysis.business_recommendations && ai_analysis.business_recommendations.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-green-500 mr-2">💼</div>
                <h3 className="text-lg font-medium text-gray-900">Business Recommendations</h3>
              </div>
              <div className="space-y-3">
                {ai_analysis.business_recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                    <div className="h-4 w-4 text-green-600 mr-3 mt-0.5 flex-shrink-0">💼</div>
                    <p className="text-sm text-green-800">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Technical Recommendations */}
          {ai_analysis.technical_recommendations && ai_analysis.technical_recommendations.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-blue-500 mr-2">⚙️</div>
                <h3 className="text-lg font-medium text-gray-900">Technical Recommendations</h3>
              </div>
              <div className="space-y-3">
                {ai_analysis.technical_recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg">
                    <div className="h-4 w-4 text-blue-600 mr-3 mt-0.5 flex-shrink-0">⚙️</div>
                    <p className="text-sm text-blue-800">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Assessment */}
          {ai_analysis.risk_assessment && ai_analysis.risk_assessment.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-red-500 mr-2">⚠️</div>
                <h3 className="text-lg font-medium text-gray-900">Risk Assessment</h3>
              </div>
              <div className="space-y-3">
                {ai_analysis.risk_assessment.map((risk, index) => (
                  <div key={index} className="flex items-start p-3 bg-red-50 rounded-lg">
                    <div className="h-4 w-4 text-red-600 mr-3 mt-0.5 flex-shrink-0">⚠️</div>
                    <p className="text-sm text-red-800">{risk}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Opportunities */}
          {ai_analysis.opportunities && ai_analysis.opportunities.length > 0 && (
            <div className="card">
              <div className="flex items-center mb-4">
                <div className="h-5 w-5 text-emerald-500 mr-2">🚀</div>
                <h3 className="text-lg font-medium text-gray-900">Opportunities</h3>
              </div>
              <div className="space-y-3">
                {ai_analysis.opportunities.map((opportunity, index) => (
                  <div key={index} className="flex items-start p-3 bg-emerald-50 rounded-lg">
                    <div className="h-4 w-4 text-emerald-600 mr-3 mt-0.5 flex-shrink-0">🚀</div>
                    <p className="text-sm text-emerald-800">{opportunity}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ModelDetails; 