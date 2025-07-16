import React, { useState, useEffect } from 'react';
import { FileText, Lightbulb, TrendingUp, CheckCircle, AlertTriangle, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { getSummary } from '../services/api.ts';
import { SummaryResponse } from '../types/index.ts';

interface SummaryProps {
  sessionId: string;
  modelId: string | null;
  onComplete?: () => void;
}

const Summary: React.FC<SummaryProps> = ({ sessionId, modelId, onComplete }) => {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, [sessionId, modelId]);

  const loadSummary = async () => {
    try {
      setIsLoading(true);
      const data = await getSummary(sessionId, modelId || undefined);
      setSummary(data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load summary');
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinueToAI = () => {
    if (onComplete) {
      onComplete();
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Generating comprehensive summary...</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Failed to load summary</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Analysis Summary</h3>
        <p className="text-gray-600">Comprehensive insights and recommendations</p>
      </div>

      {/* Data Summary */}
      <div className="card">
        <div className="flex items-center mb-4">
          <FileText className="h-5 w-5 text-blue-500 mr-2" />
          <h4 className="text-lg font-medium text-gray-900">Data Summary</h4>
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
            <h4 className="text-lg font-medium text-gray-900">Model Summary</h4>
          </div>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed">{summary.model_summary}</p>
          </div>
        </div>
      )}

      {/* Key Insights */}
      {summary.key_insights.length > 0 && (
        <div className="card">
          <div className="flex items-center mb-4">
            <Lightbulb className="h-5 w-5 text-yellow-500 mr-2" />
            <h4 className="text-lg font-medium text-gray-900">Key Insights</h4>
          </div>
          <div className="space-y-3">
            {summary.key_insights.map((insight, index) => (
              <div key={index} className="flex items-start p-3 bg-yellow-50 rounded-lg">
                <Lightbulb className="h-4 w-4 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-yellow-800">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {summary.recommendations.length > 0 && (
        <div className="card">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
            <h4 className="text-lg font-medium text-gray-900">Recommendations</h4>
          </div>
          <div className="space-y-3">
            {summary.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                <CheckCircle className="h-4 w-4 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-green-800">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Steps */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start">
          <AlertTriangle className="h-5 w-5 text-blue-600 mr-3 mt-0.5" />
          <div>
            <h4 className="text-lg font-medium text-blue-900 mb-2">Next Steps</h4>
            <div className="space-y-2 text-sm text-blue-700">
              <p>• Review the insights and recommendations above</p>
              <p>• Consider implementing the suggested improvements</p>
              <p>• Validate model performance on new data</p>
              <p>• Monitor model performance over time for concept drift</p>
              <p>• Consider retraining the model with additional data</p>
            </div>
          </div>
        </div>
      </div>

      {/* Continue to AI Analysis */}
      {onComplete && (
        <div className="flex justify-center">
          <button
            onClick={handleContinueToAI}
            className="btn-primary flex items-center"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Continue to AI Analysis
          </button>
        </div>
      )}
    </div>
  );
};

export default Summary; 