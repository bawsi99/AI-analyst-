import React, { useState } from 'react';
import { Upload, BarChart3, Brain, TrendingUp, FileText, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import FileUpload from './FileUpload.tsx';
import DataProfile from './DataProfile.tsx';
import ModelTraining from './ModelTraining.tsx';
import Predictions from './Predictions.tsx';
import Summary from './Summary.tsx';
import AIAnalysis from './AIAnalysis.tsx';
import { AppState } from '../types/index.ts';

const Dashboard: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    sessionId: null,
    modelId: null,
    featureNames: [],
    currentStep: 'upload',
    isLoading: false,
    error: null,
  });

  const handleFileUploadSuccess = (sessionId: string) => {
    setAppState(prev => ({
      ...prev,
      sessionId,
      currentStep: 'profile',
      error: null,
    }));
    toast.success('File uploaded successfully!');
  };

  const handleProfileComplete = () => {
    setAppState(prev => ({
      ...prev,
      currentStep: 'train',
    }));
  };

  const handleTrainingComplete = (modelId: string, featureNames: string[]) => {
    setAppState(prev => ({
      ...prev,
      modelId,
      featureNames,
      currentStep: 'predict',
    }));
    toast.success('Model trained successfully!');
  };

  const handlePredictionComplete = () => {
    setAppState(prev => ({
      ...prev,
      currentStep: 'summary',
    }));
  };

  const handleSummaryComplete = () => {
    setAppState(prev => ({
      ...prev,
      currentStep: 'ai-analysis',
    }));
  };

  const resetApp = () => {
    setAppState({
      sessionId: null,
      modelId: null,
      featureNames: [],
      currentStep: 'upload',
      isLoading: false,
      error: null,
    });
  };

  const steps = [
    { id: 'upload', name: 'Upload Data', icon: Upload, description: 'Upload your CSV file' },
    { id: 'profile', name: 'Data Profile', icon: BarChart3, description: 'Analyze your data' },
    { id: 'train', name: 'Train Model', icon: Brain, description: 'Train ML model' },
    { id: 'predict', name: 'Predictions', icon: TrendingUp, description: 'Make predictions' },
    { id: 'summary', name: 'Summary', icon: FileText, description: 'View insights' },
    { id: 'ai-analysis', name: 'AI Analysis', icon: Sparkles, description: 'AI-powered insights' },
  ];

  const currentStepIndex = steps.findIndex(step => step.id === appState.currentStep);

  return (
    <div className="space-y-8">
      {/* Progress Steps */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">AI Data Analysis Pipeline</h2>
          <button
            onClick={resetApp}
            className="btn-secondary text-sm"
          >
            Start Over
          </button>
        </div>
        
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const StepIcon = step.icon;
            const isActive = step.id === appState.currentStep;
            const isCompleted = index < currentStepIndex;
            
            return (
              <div key={step.id} className="flex items-center">
                <div className="flex flex-col items-center">
                  <div
                    className={`
                      w-12 h-12 rounded-full flex items-center justify-center border-2 transition-colors
                      ${isActive 
                        ? 'bg-primary-600 border-primary-600 text-white' 
                        : isCompleted 
                        ? 'bg-green-100 border-green-500 text-green-600'
                        : 'bg-gray-100 border-gray-300 text-gray-400'
                      }
                    `}
                  >
                    <StepIcon className="w-6 h-6" />
                  </div>
                  <div className="mt-2 text-center">
                    <p className={`text-sm font-medium ${isActive ? 'text-primary-600' : 'text-gray-500'}`}>
                      {step.name}
                    </p>
                    <p className="text-xs text-gray-400">{step.description}</p>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-0.5 mx-4 ${isCompleted ? 'bg-green-500' : 'bg-gray-300'}`} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Error Display */}
      {appState.error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{appState.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="card">
        {appState.currentStep === 'upload' && (
          <FileUpload onUploadSuccess={handleFileUploadSuccess} />
        )}
        
        {appState.currentStep === 'profile' && appState.sessionId && (
          <DataProfile 
            sessionId={appState.sessionId}
            onComplete={handleProfileComplete}
          />
        )}
        
        {appState.currentStep === 'train' && appState.sessionId && (
          <ModelTraining 
            sessionId={appState.sessionId}
            onComplete={handleTrainingComplete}
          />
        )}
        
        {appState.currentStep === 'predict' && appState.modelId && (
          <Predictions 
            modelId={appState.modelId}
            featureNames={appState.featureNames}
            onComplete={handlePredictionComplete}
          />
        )}
        
        {appState.currentStep === 'summary' && appState.sessionId && (
          <Summary 
            sessionId={appState.sessionId}
            modelId={appState.modelId}
            onComplete={handleSummaryComplete}
          />
        )}
        
        {appState.currentStep === 'ai-analysis' && appState.sessionId && (
          <AIAnalysis 
            sessionId={appState.sessionId}
            modelId={appState.modelId}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard; 