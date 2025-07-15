import React, { useState, useEffect } from 'react';
import { TrendingUp, ArrowRight, Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { makePrediction, getModelFeatures } from '../services/api.ts';
import { PredictionRequest, PredictionResponse, ModelFeature } from '../types/index.ts';

interface PredictionsProps {
  modelId: string;
  featureNames: string[];
  onComplete: () => void;
}

const Predictions: React.FC<PredictionsProps> = ({ modelId, featureNames, onComplete }) => {
  const [modelFeatures, setModelFeatures] = useState<ModelFeature[]>([]);
  const [inputData, setInputData] = useState<Record<string, any>[]>([
    featureNames.reduce((acc, feature) => ({ ...acc, [feature]: '' }), {})
  ]);
  const [isLoadingFeatures, setIsLoadingFeatures] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState<PredictionResponse | null>(null);

  useEffect(() => {
    loadModelFeatures();
  }, [modelId]);

  const loadModelFeatures = async () => {
    try {
      setIsLoadingFeatures(true);
      const response = await getModelFeatures(modelId);
      setModelFeatures(response.features);
      
      // Initialize input data with empty values for each feature
      const initialData = response.features.reduce((acc, feature) => ({ ...acc, [feature.name]: '' }), {});
      setInputData([initialData]);
    } catch (error: any) {
      toast.error('Failed to load model features');
      console.error('Load features error:', error);
      // Fallback to using featureNames if features can't be loaded
      const fallbackData = featureNames.reduce((acc, feature) => ({ ...acc, [feature]: '' }), {});
      setInputData([fallbackData]);
    } finally {
      setIsLoadingFeatures(false);
    }
  };

  const handleAddRow = () => {
    if (modelFeatures.length > 0) {
      const newRow = modelFeatures.reduce((acc, feature) => ({ ...acc, [feature.name]: '' }), {});
      setInputData([...inputData, newRow]);
    } else {
      const newRow = featureNames.reduce((acc, feature) => ({ ...acc, [feature]: '' }), {});
      setInputData([...inputData, newRow]);
    }
  };

  const handleRemoveRow = (index: number) => {
    if (inputData.length > 1) {
      setInputData(inputData.filter((_, i) => i !== index));
    }
  };

  const handleInputChange = (rowIndex: number, field: string, value: string) => {
    const newData = [...inputData];
    newData[rowIndex] = { ...newData[rowIndex], [field]: value };
    setInputData(newData);
  };

  const handlePredict = async () => {
    // Validate input data
    const hasEmptyFields = inputData.some(row => 
      Object.values(row).some(value => value === '')
    );
    
    if (hasEmptyFields) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      setIsPredicting(true);
      const request: PredictionRequest = { data: inputData };
      const result = await makePrediction(modelId, request);
      setPredictionResult(result);
      toast.success('Predictions generated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Prediction failed');
    } finally {
      setIsPredicting(false);
    }
  };

  const handleContinue = () => {
    onComplete();
  };

  const renderInputField = (featureName: string, rowIndex: number) => {
    const value = inputData[rowIndex]?.[featureName] || '';
    
    // Find the feature in modelFeatures to get its type
    const feature = modelFeatures.find(f => f.name === featureName);
    
    if (feature?.dtype === 'categorical' && feature.sample_values.length > 0) {
      return (
        <select
          value={value}
          onChange={(e) => handleInputChange(rowIndex, featureName, e.target.value)}
          className="input-field"
        >
          <option value="">Select {featureName}</option>
          {feature.sample_values.map((option, idx) => (
            <option key={idx} value={option}>
              {option}
            </option>
          ))}
        </select>
      );
    } else if (feature?.dtype === 'numerical') {
      return (
        <input
          type="number"
          value={value}
          onChange={(e) => handleInputChange(rowIndex, featureName, e.target.value)}
          className="input-field"
          placeholder={`Enter ${featureName}`}
          step="any"
        />
      );
    } else {
      return (
        <input
          type="text"
          value={value}
          onChange={(e) => handleInputChange(rowIndex, featureName, e.target.value)}
          className="input-field"
          placeholder={`Enter ${featureName}`}
        />
      );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Make Predictions</h3>
          <p className="text-gray-600">Input data to get predictions from your trained model</p>
        </div>
        {predictionResult && (
          <button
            onClick={handleContinue}
            className="btn-primary flex items-center"
          >
            View Summary
            <ArrowRight className="ml-2 h-4 w-4" />
          </button>
        )}
      </div>

      {!predictionResult ? (
        <div className="space-y-6">
          {/* Input Form */}
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
            ) : (
              <div className="space-y-4">
                {inputData.map((row, rowIndex) => (
                  <div key={rowIndex} className="overflow-x-auto">
                    <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg min-w-max">
                      {(modelFeatures.length > 0 ? modelFeatures.map(f => f.name) : featureNames).map((field) => {
                        const feature = modelFeatures.find(f => f.name === field);
                        return (
                          <div key={field} className="flex-1 min-w-[180px]">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              {field}
                              {feature && (
                                <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                                  feature.dtype === 'numerical' ? 'bg-blue-100 text-blue-800' :
                                  feature.dtype === 'categorical' ? 'bg-green-100 text-green-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {feature.dtype}
                                </span>
                              )}
                            </label>
                            {renderInputField(field, rowIndex)}
                            {feature?.dtype === 'categorical' && feature.sample_values.length > 0 && (
                              <p className="text-xs text-gray-500 mt-1">
                                {feature.unique_count} unique values
                              </p>
                            )}
                          </div>
                        );
                      })}
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
            )}

            {/* Prediction Button */}
            <div className="flex justify-center mt-6">
              <button
                onClick={handlePredict}
                disabled={isPredicting || isLoadingFeatures}
                className={`
                  btn-primary flex items-center px-8 py-3 text-lg
                  ${(isPredicting || isLoadingFeatures) ? 'opacity-50 cursor-not-allowed' : ''}
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
          </div>

          {/* Instructions */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-blue-900 mb-2">How to use:</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Select values for each feature to make predictions</li>
              <li>• Categorical features show dropdown menus with available options</li>
              <li>• Numerical features accept decimal values</li>
              <li>• Add multiple rows to get predictions for multiple samples</li>
              <li>• Make sure the feature names match your training data</li>
            </ul>
          </div>
        </div>
      ) : (
        /* Results Display */
        <div className="card">
          <div className="mb-6">
            <h4 className="text-lg font-medium text-gray-900 mb-2">Prediction Results</h4>
            <p className="text-gray-600">
              Successfully predicted {predictionResult.predictions.length} samples
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
              className="btn-secondary mr-4"
            >
              Make Another Prediction
            </button>
            <button
              onClick={handleContinue}
              className="btn-primary flex items-center"
            >
              View Summary
              <ArrowRight className="ml-2 h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Predictions; 