import React, { useState, useEffect } from 'react';
import { TrendingUp, Brain, Plus, Trash2, Search } from 'lucide-react';
import { getUserModels, makePrediction, getModelFeatures } from '../services/api.ts';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { PredictionRequest, PredictionResponse, ModelFeature } from '../types/index.ts';

interface UserModel {
  id: string;
  model_id: string;
  model_type: string;
  target_column: string;
  algorithm: string;
  metrics: any;
  created_at: string;
  analysis_sessions: {
    file_name: string;
    session_id: string;
  };
}

const ModelPredictions: React.FC = () => {
  const [models, setModels] = useState<UserModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<UserModel | null>(null);
  const [modelFeatures, setModelFeatures] = useState<ModelFeature[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingFeatures, setIsLoadingFeatures] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [inputData, setInputData] = useState<Record<string, any>[]>([
    {}
  ]);
  const [predictionResult, setPredictionResult] = useState<PredictionResponse | null>(null);

  useEffect(() => {
    loadUserModels();
  }, []);

  const loadUserModels = async () => {
    try {
      setIsLoading(true);
      const response = await getUserModels();
      setModels(response.models);
    } catch (error: any) {
      toast.error('Failed to load your models');
      console.error('Load models error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadModelFeatures = async (modelId: string) => {
    try {
      setIsLoadingFeatures(true);
      const response = await getModelFeatures(modelId);
      setModelFeatures(response.features);
      
      // Initialize input data with empty values for each feature
      // For grouped features, we need to initialize all one-hot encoded columns
      const initialData = {};
      
      response.features.forEach(feature => {
        if (feature.dtype === 'categorical') {
          // For categorical features, initialize all one-hot encoded columns to '0'
          feature.sample_values.forEach(category => {
            const oneHotColumn = `${feature.name}_${category}`;
            initialData[oneHotColumn] = '0';
          });
        } else {
          // For numerical features, initialize with empty string
          initialData[feature.name] = '';
        }
      });
      
      setInputData([initialData]);
    } catch (error: any) {
      toast.error('Failed to load model features');
      console.error('Load features error:', error);
    } finally {
      setIsLoadingFeatures(false);
    }
  };

  const handleModelSelect = async (model: UserModel) => {
    setSelectedModel(model);
    setPredictionResult(null);
    setModelFeatures([]);
    setInputData([{}]);
    
    // Load features for the selected model
    await loadModelFeatures(model.model_id);
  };

  const handleAddRow = () => {
    if (modelFeatures.length > 0) {
      const newRow = {};
      
      modelFeatures.forEach(feature => {
        if (feature.dtype === 'categorical') {
          // For categorical features, initialize all one-hot encoded columns to '0'
          feature.sample_values.forEach(category => {
            const oneHotColumn = `${feature.name}_${category}`;
            newRow[oneHotColumn] = '0';
          });
        } else {
          // For numerical features, initialize with empty string
          newRow[feature.name] = '';
        }
      });
      
      setInputData([...inputData, newRow]);
    } else {
      setInputData([...inputData, {}]);
    }
  };

  const handleRemoveRow = (index: number) => {
    if (inputData.length > 1) {
      setInputData(inputData.filter((_, i) => i !== index));
    }
  };

  const handleInputChange = (rowIndex: number, field: string, value: string) => {
    const newData = [...inputData];
    const currentRow = { ...newData[rowIndex] };
    
    // Check if this is a categorical feature with one-hot encoding
    const feature = modelFeatures.find(f => f.name === field);
    if (feature && feature.dtype === 'categorical' && feature.sample_values.length > 0) {
      // This is a grouped categorical feature
      // For grouped features, we need to set the appropriate one-hot encoded columns
      const baseColumn = feature.name; // Use the base column name
      
      // Clear all related one-hot encoded columns first
      modelFeatures.forEach(f => {
        if (f.name.startsWith(baseColumn + '_')) {
          currentRow[f.name] = '0';
        }
      });
      
      // Set the selected category to 1
      if (value) {
        const oneHotColumn = `${baseColumn}_${value.replace(/ /g, '_')}`;
        currentRow[oneHotColumn] = '1';
      }
    } else {
      // Regular numerical or text field
      currentRow[field] = value;
    }
    
    newData[rowIndex] = currentRow;
    setInputData(newData);
  };

  const handlePredict = async () => {
    if (!selectedModel) {
      toast.error('Please select a model first');
      return;
    }

    // Validate input data
    const hasEmptyFields = inputData.some(row => 
      Object.keys(row).length === 0 || Object.values(row).some(value => value === '')
    );
    
    if (hasEmptyFields) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      setIsPredicting(true);
      const request: PredictionRequest = { data: inputData };
      const result = await makePrediction(selectedModel.model_id, request);
      setPredictionResult(result);
      toast.success('Predictions generated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Prediction failed');
    } finally {
      setIsPredicting(false);
    }
  };

  const filteredModels = models.filter(model =>
    model.analysis_sessions?.file_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    model.algorithm.toLowerCase().includes(searchTerm.toLowerCase()) ||
    model.target_column.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderInputField = (feature: ModelFeature, rowIndex: number) => {
    const value = inputData[rowIndex]?.[feature.name] || '';
    
    if (feature.dtype === 'categorical' && feature.sample_values.length > 0) {
      // For grouped categorical features, we need to determine the current selected value
      // by checking which one-hot encoded column is set to '1'
      const baseColumn = feature.name; // Use the base column name
      let selectedValue = '';
      
      // Find the currently selected category for this base column
      modelFeatures.forEach(f => {
        if (f.name.startsWith(baseColumn + '_') && inputData[rowIndex]?.[f.name] === '1') {
          // Extract the category value from the feature name
          // Remove the base column name and any remaining underscores
          const categoryValue = f.name.replace(`${baseColumn}_`, '').replace(/_/g, ' ');
          selectedValue = categoryValue;
        }
      });
      
      return (
        <select
          value={selectedValue}
          onChange={(e) => {
            const newValue = e.target.value;
            if (newValue) {
              // Set the selected category for the grouped feature
              handleInputChange(rowIndex, baseColumn, newValue);
            } else {
              // Clear all related one-hot encoded features
              modelFeatures.forEach(f => {
                if (f.name.startsWith(baseColumn + '_')) {
                  const newData = [...inputData];
                  newData[rowIndex] = { ...newData[rowIndex], [f.name]: '0' };
                  setInputData(newData);
                }
              });
            }
          }}
          className="input-field"
        >
          <option value="">Select {feature.display_name || feature.name}</option>
          {feature.sample_values.map((option, idx) => {
            // Clean up the option value for display (remove underscores, capitalize)
            const displayValue = option.replace(/_/g, ' ');
            return (
              <option key={idx} value={option}>
                {displayValue}
              </option>
            );
          })}
        </select>
      );
    } else if (feature.dtype === 'numerical') {
      return (
        <input
          type="number"
          value={value}
          onChange={(e) => handleInputChange(rowIndex, feature.name, e.target.value)}
          className="input-field"
          placeholder={`Enter ${feature.display_name || feature.name}`}
          step="any"
        />
      );
    } else {
      return (
        <input
          type="text"
          value={value}
          onChange={(e) => handleInputChange(rowIndex, feature.name, e.target.value)}
          className="input-field"
          placeholder={`Enter ${feature.display_name || feature.name}`}
        />
      );
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your models...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Model Predictions</h1>
        <p className="text-gray-600">Use your trained models to make predictions on new data</p>
      </div>

      {models.length === 0 ? (
        <div className="text-center py-12">
          <Brain className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No models found</h3>
          <p className="text-gray-600 mb-6">You haven't trained any models yet. Start by uploading data and training a model.</p>
          <Link to="/dashboard" className="btn-primary">
            Go to Dashboard
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Model Selection */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Select Model</h3>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search models..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredModels.map((model) => (
                <div
                  key={model.id}
                  onClick={() => handleModelSelect(model)}
                  className={`
                    p-4 border rounded-lg cursor-pointer transition-colors
                    ${selectedModel?.id === model.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 truncate">
                      {model.analysis_sessions?.file_name || 'Unknown Dataset'}
                    </h4>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      model.model_type === 'classification' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {model.model_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    Target: <span className="font-medium">{model.target_column}</span>
                  </p>
                  <p className="text-sm text-gray-600 mb-2">
                    Algorithm: <span className="font-medium">{model.algorithm}</span>
                  </p>
                  {(() => {
                    const getPrimaryMetric = (model: UserModel) => {
                      const { model_type, algorithm, metrics } = model;
                      
                      if (!metrics) return null;
                      
                      if (model_type === 'classification') {
                        if (algorithm === 'logistic_regression') {
                          return { value: metrics.precision || 0, label: 'Precision' };
                        } else if (algorithm === 'xgboost') {
                          return { value: metrics.f1_score || 0, label: 'F1-Score' };
                        } else {
                          return { value: metrics.accuracy || 0, label: 'Accuracy' };
                        }
                      } else if (model_type === 'regression') {
                        return { value: metrics.r2_score || 0, label: 'R² Score' };
                      }
                      
                      return { value: metrics.accuracy || 0, label: 'Accuracy' };
                    };

                    const formatMetricValue = (value: number, label: string) => {
                      if (label === 'R² Score' || label === 'RMSE') {
                        return value.toFixed(3);
                      }
                      return (value * 100).toFixed(1) + '%';
                    };

                    const metric = getPrimaryMetric(model);
                    return metric ? (
                      <p className="text-sm text-gray-600">
                        {metric.label}: <span className="font-medium">{formatMetricValue(metric.value, metric.label)}</span>
                      </p>
                    ) : null;
                  })()}
                </div>
              ))}
            </div>
          </div>

          {/* Prediction Interface */}
          {selectedModel && (
            <div className="space-y-6">
              {/* Model Info */}
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Make Predictions</h3>
                    <p className="text-gray-600">
                      Using {selectedModel.algorithm} model to predict {selectedModel.target_column}
                    </p>
                  </div>
                  {predictionResult && (
                    <button
                      onClick={() => setPredictionResult(null)}
                      className="btn-secondary flex items-center"
                    >
                      New Prediction
                      <Plus className="ml-2 h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>

              {!predictionResult ? (
                /* Input Form */
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-medium text-gray-900">Input Data</h4>
                    <button
                      onClick={handleAddRow}
                      className="btn-secondary flex items-center text-sm"
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      Add Row
                    </button>
                  </div>

                  {isLoadingFeatures ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="text-center">
                        <div className="loading-spinner mx-auto mb-4"></div>
                        <p className="text-gray-600">Loading model features...</p>
                      </div>
                    </div>
                  ) : modelFeatures.length > 0 ? (
                    <div className="space-y-4">
                      {inputData.map((row, rowIndex) => (
                        <div key={rowIndex} className="overflow-x-auto">
                          <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg min-w-max">
                            {(() => {
                              // Group features by display_name to avoid duplicates
                              const groupedFeatures = new Map();
                              modelFeatures.forEach(feature => {
                                const key = feature.display_name || feature.name;
                                if (!groupedFeatures.has(key)) {
                                  groupedFeatures.set(key, feature);
                                }
                              });
                              
                              return Array.from(groupedFeatures.values()).map((feature) => (
                                <div key={feature.name} className="flex-1 min-w-[280px]">
                                  <label className="block text-sm font-medium text-gray-700 mb-1 break-words">
                                    {feature.display_name || feature.name}
                                    <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                                      feature.dtype === 'numerical' ? 'bg-blue-100 text-blue-800' :
                                      feature.dtype === 'categorical' ? 'bg-green-100 text-green-800' :
                                      'bg-gray-100 text-gray-800'
                                    }`}>
                                      {feature.dtype}
                                    </span>
                                  </label>
                                  {renderInputField(feature, rowIndex)}
                                  {feature.dtype === 'categorical' && feature.sample_values.length > 0 && (
                                    <p className="text-xs text-gray-500 mt-1">
                                      {feature.unique_count} unique values
                                    </p>
                                  )}
                                </div>
                              ));
                            })()}
                            {inputData.length > 1 && (
                              <button
                                onClick={() => handleRemoveRow(rowIndex)}
                                className="mt-6 p-2 text-red-600 hover:text-red-800"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-600">No features found for this model</p>
                    </div>
                  )}

                  {/* Prediction Button */}
                  <div className="flex justify-center mt-6">
                    <button
                      onClick={handlePredict}
                      disabled={isPredicting || modelFeatures.length === 0}
                      className={`
                        btn-primary flex items-center px-8 py-3 text-lg
                        ${(isPredicting || modelFeatures.length === 0) ? 'opacity-50 cursor-not-allowed' : ''}
                      `}
                    >
                      {isPredicting ? (
                        <>
                          <div className="loading-spinner mr-3"></div>
                          Generating Predictions...
                        </>
                      ) : (
                        <>
                          <TrendingUp className="mr-2 h-5 w-5" />
                          Get Predictions
                        </>
                      )}
                    </button>
                  </div>

                  {/* Instructions */}
                  <div className="bg-blue-50 rounded-lg p-4 mt-6">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">How to use:</h4>
                    <ul className="text-sm text-blue-700 space-y-1">
                      <li>• Select values for each feature to make predictions</li>
                      <li>• Categorical features show dropdown menus with available options</li>
                      <li>• Numerical features accept decimal values</li>
                      <li>• Add multiple rows to get predictions for multiple samples</li>
                    </ul>
                  </div>
                </div>
              ) : (
                /* Results Display */
                <div className="card">
                  <div className="mb-6">
                    <h4 className="text-lg font-medium text-gray-900 mb-2">Prediction Results</h4>
                    <p className="text-gray-600">
                      Model: {selectedModel.algorithm} | Target: {selectedModel.target_column}
                    </p>
                  </div>

                  <div className="space-y-4">
                    {predictionResult.predictions.map((prediction, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <span className="text-sm font-medium text-gray-700">Sample {index + 1}:</span>
                          <span className="ml-2 text-lg font-semibold text-gray-900">
                            {typeof prediction === 'number' ? prediction.toFixed(4) : prediction}
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-sm text-gray-500">Confidence:</span>
                          <span className="ml-2 text-sm font-medium text-gray-900">
                            {(predictionResult.confidence_scores[index] * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-6 flex justify-center">
                    <button
                      onClick={() => setPredictionResult(null)}
                      className="btn-primary"
                    >
                      Make Another Prediction
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ModelPredictions; 