import React, { useState, useEffect, useCallback } from 'react';
import { Brain, Settings, ArrowRight, TrendingUp, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getProfile, trainModel } from '../services/api.ts';
import { ProfileResponse, TrainingRequest, TrainingResponse } from '../types/index.ts';
import toast from 'react-hot-toast';

interface ModelTrainingProps {
  sessionId: string;
  onComplete: (modelId: string, featureNames: string[]) => void;
}

const ModelTraining: React.FC<ModelTrainingProps> = ({ sessionId, onComplete }) => {
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<TrainingResponse | null>(null);
  const [targetColumn, setTargetColumn] = useState('');
  const [modelType, setModelType] = useState('classification');
  const [algorithm, setAlgorithm] = useState('random_forest');
  const [excludedColumns, setExcludedColumns] = useState<string[]>([]);

  const loadProfile = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await getProfile(sessionId);
      setProfile(data);
      
      // Auto-select target column if it has common target names
      const targetNames = ['target', 'label', 'class', 'churn', 'survived', 'price', 'sales'];
      const autoTarget = data.schema.find(col => 
        targetNames.some(name => col.name.toLowerCase().includes(name))
      );
      if (autoTarget) {
        setTargetColumn(autoTarget.name);
      }
      
      // Auto-exclude common non-predictive columns
      const nonPredictiveColumns = ['id', 'customer_id', 'user_id', 'uid', 'uuid', 'index', 'row_id'];
      const autoExcluded = data.schema
        .filter(col => nonPredictiveColumns.some(name => col.name.toLowerCase().includes(name)))
        .map(col => col.name);
      setExcludedColumns(autoExcluded);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const handleTrain = async () => {
    if (!targetColumn) {
      toast.error('Please select a target column');
      return;
    }

    try {
      setIsTraining(true);
      const request: TrainingRequest = {
        target_column: targetColumn,
        model_type: modelType,
        algorithm: algorithm,
        excluded_columns: excludedColumns,
      };

      const result = await trainModel(sessionId, request);
      setTrainingResult(result);
      toast.success('Model trained successfully!');
    } catch (error: any) {
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        toast.error('Training timed out. This can happen with large datasets. Please try again or use a smaller dataset.');
      } else {
        toast.error(error.response?.data?.detail || 'Training failed');
      }
    } finally {
      setIsTraining(false);
    }
  };

  const handleContinue = () => {
    if (trainingResult) {
      // Get feature names (all columns except target column and excluded columns)
      const featureNames = profile?.schema
        .filter(col => col.name !== targetColumn && !excludedColumns.includes(col.name))
        .map(col => col.name);
      onComplete(trainingResult.model_id, featureNames || []);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading data profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Failed to load data profile</p>
      </div>
    );
  }

  const { schema } = profile;
  const numericalColumns = schema.filter(col => col.dtype === 'numerical').map(col => col.name);
  const categoricalColumns = schema.filter(col => col.dtype === 'categorical').map(col => col.name);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Train Machine Learning Model</h3>
          <p className="text-gray-600">Configure and train your model</p>
        </div>
        {trainingResult && (
          <button
            onClick={handleContinue}
            className="btn-primary flex items-center"
          >
            Continue to Predictions
            <ArrowRight className="ml-2 h-4 w-4" />
          </button>
        )}
      </div>

      {!trainingResult ? (
        <div className="space-y-6">
          {/* Configuration */}
          <div className="card">
            <div className="flex items-center mb-4">
              <Settings className="h-5 w-5 text-gray-500 mr-2" />
              <h4 className="text-lg font-medium text-gray-900">Model Configuration</h4>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Target Column */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Column *
                </label>
                <select
                  value={targetColumn}
                  onChange={(e) => setTargetColumn(e.target.value)}
                  className="input-field"
                >
                  <option value="">Select target column</option>
                  {schema.map((column) => (
                    <option key={column.name} value={column.name}>
                      {column.name} ({column.dtype})
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Choose the column you want to predict
                </p>
              </div>

              {/* Model Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model Type
                </label>
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="input-field"
                >
                  <option value="classification">Classification</option>
                  <option value="regression">Regression</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Choose the type of prediction task
                </p>
              </div>

              {/* Algorithm */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Algorithm
                </label>
                <select
                  value={algorithm}
                  onChange={(e) => setAlgorithm(e.target.value)}
                  className="input-field"
                >
                  <option value="random_forest">Random Forest</option>
                  <option value="xgboost">XGBoost</option>
                  <option value="logistic_regression">Logistic Regression</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Choose the machine learning algorithm
                </p>
              </div>

              {/* Data Summary */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Summary
                </label>
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Numerical columns:</span> {numericalColumns.length}
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Categorical columns:</span> {categoricalColumns.length}
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Total rows:</span> {profile.statistics.total_rows.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Column Selection */}
          <div className="card">
            <div className="flex items-center mb-4">
              <Settings className="h-5 w-5 text-gray-500 mr-2" />
              <h4 className="text-lg font-medium text-gray-900">Feature Selection</h4>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-3">
                Select which columns to exclude from training. Columns like IDs, UIDs, or other unique identifiers 
                should typically be excluded as they don't provide predictive value.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {schema.map((column) => (
                  <div key={column.name} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`exclude-${column.name}`}
                      checked={excludedColumns.includes(column.name)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setExcludedColumns([...excludedColumns, column.name]);
                        } else {
                          setExcludedColumns(excludedColumns.filter(col => col !== column.name));
                        }
                      }}
                      disabled={column.name === targetColumn}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label 
                      htmlFor={`exclude-${column.name}`}
                      className={`ml-2 text-sm ${
                        column.name === targetColumn 
                          ? 'text-gray-400 cursor-not-allowed' 
                          : 'text-gray-700 cursor-pointer'
                      }`}
                    >
                      {column.name} ({column.dtype})
                      {column.name === targetColumn && ' (Target)'}
                    </label>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 p-3 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-700">
                  <span className="font-medium">Features to use:</span> {
                    schema
                      .filter(col => col.name !== targetColumn && !excludedColumns.includes(col.name))
                      .length
                  } columns
                </p>
                <p className="text-sm text-blue-700">
                  <span className="font-medium">Excluded:</span> {excludedColumns.length} columns
                </p>
              </div>
            </div>
          </div>

          {/* Training Button */}
          <div className="flex justify-center">
            <button
              onClick={handleTrain}
              disabled={!targetColumn || isTraining}
              className={`
                btn-primary flex items-center px-8 py-3 text-lg
                ${(!targetColumn || isTraining) ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {isTraining ? (
                <>
                  <div className="loading-spinner mr-3"></div>
                  Training Model... (This may take a few minutes)
                </>
              ) : (
                <>
                  <Brain className="mr-2 h-5 w-5" />
                  Train Model
                </>
              )}
            </button>
          </div>
          
          {isTraining && (
            <div className="text-center mt-4">
              <p className="text-sm text-gray-600">
                Model training is in progress. Please wait - this can take several minutes for larger datasets.
              </p>
            </div>
          )}
        </div>
      ) : (
        /* Training Results */
        <div className="space-y-6">
          <div className="card bg-green-50 border-green-200">
            <div className="flex items-center">
              <CheckCircle className="h-6 w-6 text-green-600 mr-3" />
              <div>
                <h4 className="text-lg font-medium text-green-900">Training Complete!</h4>
                <p className="text-green-700">
                  Model trained successfully in {trainingResult.training_time.toFixed(2)} seconds
                </p>
              </div>
            </div>
          </div>

          {/* Model Metrics */}
          <div className="card">
            <div className="flex items-center mb-4">
              <TrendingUp className="h-5 w-5 text-gray-500 mr-2" />
              <h4 className="text-lg font-medium text-gray-900">Model Performance</h4>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {trainingResult.model_type === 'classification' ? (
                <>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">
                      {(trainingResult.metrics.accuracy! * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-blue-700">Accuracy</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">
                      {(trainingResult.metrics.precision! * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-green-700">Precision</p>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <p className="text-2xl font-bold text-yellow-600">
                      {(trainingResult.metrics.recall! * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-yellow-700">Recall</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-2xl font-bold text-purple-600">
                      {(trainingResult.metrics.f1_score! * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-purple-700">F1-Score</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">
                      {trainingResult.metrics.r2_score!.toFixed(3)}
                    </p>
                    <p className="text-sm text-blue-700">R² Score</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">
                      {trainingResult.metrics.rmse!.toFixed(3)}
                    </p>
                    <p className="text-sm text-green-700">RMSE</p>
                  </div>
                </>
              )}
            </div>

            {/* Feature Importance */}
            {Object.keys(trainingResult.feature_importance).length > 0 && (
              <div>
                <h5 className="text-md font-medium text-gray-900 mb-4">Feature Importance</h5>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={Object.entries(trainingResult.feature_importance)
                        .slice(0, 10)
                        .map(([feature, importance]) => ({
                          feature: feature.length > 20 ? feature.substring(0, 20) + '...' : feature,
                          importance,
                        }))
                        .sort((a, b) => b.importance - a.importance)
                      }
                      layout="horizontal"
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="feature" type="category" width={120} />
                      <Tooltip />
                      <Bar dataKey="importance" fill="#3B82F6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelTraining; 