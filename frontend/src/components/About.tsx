import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, Database, Cpu, Shield, Zap, Target, TrendingUp, Globe, Code, FileText, PieChart, Activity } from 'lucide-react';

const About: React.FC = () => {
  const navigate = useNavigate();

  const handleStartAnalysis = () => {
    navigate('/new-analysis');
  };

  const handleViewDocumentation = () => {
    // For now, just navigate to the main dashboard
    navigate('/');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-primary-100 rounded-full">
            <Brain className="h-12 w-12 text-primary-600" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">About AI Analyst</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          An intelligent data analysis platform that empowers users to build, train, and deploy machine learning models with ease.
        </p>
      </div>

      {/* Platform Overview */}
      <div className="grid md:grid-cols-2 gap-8 mb-16">
        <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center mb-4">
            <Zap className="h-6 w-6 text-primary-600 mr-3" />
            <h2 className="text-2xl font-semibold text-gray-900">What We Do</h2>
          </div>
          <p className="text-gray-600 mb-4">
            AI Analyst transforms raw data into actionable insights through automated machine learning. 
            Our platform handles the entire ML pipeline from data preprocessing to model deployment.
          </p>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-center">
              <div className="w-2 h-2 bg-primary-600 rounded-full mr-3"></div>
              Automated data profiling and analysis
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-primary-600 rounded-full mr-3"></div>
              Intelligent model selection and training
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-primary-600 rounded-full mr-3"></div>
              Real-time predictions and insights
            </li>
            <li className="flex items-center">
              <div className="w-2 h-2 bg-primary-600 rounded-full mr-3"></div>
              Comprehensive model evaluation
            </li>
          </ul>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center mb-4">
            <Target className="h-6 w-6 text-primary-600 mr-3" />
            <h2 className="text-2xl font-semibold text-gray-900">Our Mission</h2>
          </div>
          <p className="text-gray-600 mb-4">
            To democratize machine learning by making advanced analytics accessible to everyone, 
            regardless of their technical background.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 mb-1">100%</div>
              <div className="text-sm text-gray-600">Automated</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 mb-1">3+</div>
              <div className="text-sm text-gray-600">ML Algorithms</div>
            </div>
          </div>
        </div>
      </div>

      {/* Data Processing Pipeline */}
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 mb-16">
        <div className="flex items-center mb-6">
          <Database className="h-6 w-6 text-primary-600 mr-3" />
          <h2 className="text-2xl font-semibold text-gray-900">Data Processing Pipeline</h2>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">1. Data Upload</h3>
            <p className="text-sm text-gray-600">
              Upload CSV files up to 50MB. Automatic data validation and format detection.
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <PieChart className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">2. Data Profiling</h3>
            <p className="text-sm text-gray-600">
              Comprehensive analysis including schema detection, statistics, and data quality insights.
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Cpu className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">3. Model Training</h3>
            <p className="text-sm text-gray-600">
              Automated preprocessing, feature engineering, and model training with validation.
            </p>
          </div>
        </div>

        <div className="bg-gray-50 p-6 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-4">Data Preprocessing Details</h4>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h5 className="font-medium text-gray-900 mb-2">Numerical Features</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Median imputation for missing values</li>
                <li>• StandardScaler normalization (zero mean, unit variance)</li>
                <li>• Outlier detection and handling</li>
              </ul>
            </div>
            <div>
              <h5 className="font-medium text-gray-900 mb-2">Categorical Features</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Constant imputation with 'missing' value</li>
                <li>• OneHotEncoder for categorical variables</li>
                <li>• Unknown category handling</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Machine Learning Models */}
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 mb-16">
        <div className="flex items-center mb-6">
          <Brain className="h-6 w-6 text-primary-600 mr-3" />
          <h2 className="text-2xl font-semibold text-gray-900">Machine Learning Models</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Classification Models */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Target className="h-5 w-5 text-blue-600 mr-2" />
              Classification Models
            </h3>
            <div className="space-y-4">
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Random Forest</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Ensemble method using 100 decision trees for robust classification.
                </p>
                <div className="text-xs text-gray-500">
                  <strong>Parameters:</strong> n_estimators=100, random_state=42
                </div>
              </div>
              
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">XGBoost</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Gradient boosting framework optimized for performance and accuracy.
                </p>
                <div className="text-xs text-gray-500">
                  <strong>Parameters:</strong> Default XGBoost settings with random_state=42
                </div>
              </div>
              
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Logistic Regression</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Linear model for binary and multi-class classification problems.
                </p>
                <div className="text-xs text-gray-500">
                  <strong>Parameters:</strong> max_iter=1000, random_state=42
                </div>
              </div>
            </div>
          </div>

          {/* Regression Models */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
              Regression Models
            </h3>
            <div className="space-y-4">
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Random Forest Regressor</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Ensemble regression using 100 decision trees for continuous predictions.
                </p>
                <div className="text-xs text-gray-500">
                  <strong>Parameters:</strong> n_estimators=100, random_state=42
                </div>
              </div>
              
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">XGBoost Regressor</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Gradient boosting for regression with automatic feature selection.
                </p>
                <div className="text-xs text-gray-500">
                  <strong>Parameters:</strong> Default XGBoost settings with random_state=42
                </div>
              </div>
              
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">Linear Regression</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Simple linear model for continuous value prediction.
                </p>
                <div className="text-xs text-gray-500">
                  <strong>Parameters:</strong> Standard linear regression settings
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Training Process */}
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 mb-16">
        <div className="flex items-center mb-6">
          <Activity className="h-6 w-6 text-primary-600 mr-3" />
          <h2 className="text-2xl font-semibold text-gray-900">Training Process</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Splitting Strategy</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-sm font-medium text-gray-900">Training Set</span>
                <span className="text-sm font-bold text-blue-600">80%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm font-medium text-gray-900">Test Set</span>
                <span className="text-sm font-bold text-green-600">20%</span>
              </div>
            </div>
            <p className="text-sm text-gray-600 mt-4">
              For classification tasks, we use stratified sampling to maintain class distribution in both sets.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Evaluation</h3>
            <div className="space-y-3">
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-1">Classification Metrics</h4>
                <div className="text-sm text-gray-600 space-y-1">
                  <div>• Accuracy: Overall prediction correctness</div>
                  <div>• Precision: True positives / (True positives + False positives)</div>
                  <div>• Recall: True positives / (True positives + False negatives)</div>
                  <div>• F1-Score: Harmonic mean of precision and recall</div>
                </div>
              </div>
              
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-1">Regression Metrics</h4>
                <div className="text-sm text-gray-600 space-y-1">
                  <div>• RMSE: Root Mean Square Error</div>
                  <div>• R² Score: Coefficient of determination</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Architecture */}
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 mb-16">
        <div className="flex items-center mb-6">
          <Code className="h-6 w-6 text-primary-600 mr-3" />
          <h2 className="text-2xl font-semibold text-gray-900">System Architecture</h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center p-6 border border-gray-200 rounded-lg">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Globe className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Frontend</h3>
            <p className="text-sm text-gray-600">
              React.js with TypeScript, Tailwind CSS for responsive design, and real-time updates.
            </p>
          </div>
          
          <div className="text-center p-6 border border-gray-200 rounded-lg">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Cpu className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Backend</h3>
            <p className="text-sm text-gray-600">
              FastAPI with Python, scikit-learn for ML, and comprehensive data processing pipeline.
            </p>
          </div>
          
          <div className="text-center p-6 border border-gray-200 rounded-lg">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Database className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Database</h3>
            <p className="text-sm text-gray-600">
              Supabase (PostgreSQL) for user management, session storage, and model metadata.
            </p>
          </div>
        </div>
      </div>

      {/* Security & Privacy */}
      <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 mb-16">
        <div className="flex items-center mb-6">
          <Shield className="h-6 w-6 text-primary-600 mr-3" />
          <h2 className="text-2xl font-semibold text-gray-900">Security & Privacy</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Protection</h3>
            <ul className="space-y-3 text-gray-600">
              <li className="flex items-start">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3 mt-2"></div>
                <span>Secure file upload with size and format validation</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3 mt-2"></div>
                <span>JWT-based authentication with secure token management</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3 mt-2"></div>
                <span>User data isolation with row-level security policies</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3 mt-2"></div>
                <span>Automatic session cleanup and data retention policies</span>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Privacy Features</h3>
            <ul className="space-y-3 text-gray-600">
              <li className="flex items-start">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3 mt-2"></div>
                <span>No data sharing between users</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3 mt-2"></div>
                <span>Local model storage with user-specific access</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3 mt-2"></div>
                <span>Transparent data processing with detailed logging</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3 mt-2"></div>
                <span>User control over data deletion and model management</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Contact & Support */}
      <div className="bg-gradient-to-r from-primary-50 to-blue-50 p-8 rounded-lg">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Ready to Get Started?</h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Join thousands of users who are already leveraging AI Analyst to transform their data into actionable insights.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={handleStartAnalysis}
              className="btn-primary px-8 py-3"
            >
              Start New Analysis
            </button>
            <button 
              onClick={handleViewDocumentation}
              className="btn-secondary px-8 py-3"
            >
              View Documentation
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About; 