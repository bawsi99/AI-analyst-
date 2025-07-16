import React, { useState, useEffect, useCallback } from 'react';
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import toast from 'react-hot-toast';
import { getProfile } from '../services/api.ts';
import { ProfileResponse } from '../types/index.ts';

interface DataProfileProps {
  sessionId: string;
  onComplete: () => void;
}

const DataProfile: React.FC<DataProfileProps> = ({ sessionId, onComplete }) => {
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'schema' | 'insights'>('overview');

  const loadProfile = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await getProfile(sessionId);
      setProfile(data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing your data...</p>
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

  const { statistics, schema, insights } = profile;

  // Prepare data for charts
  const dataTypesData = schema.reduce((acc, col) => {
    acc[col.dtype] = (acc[col.dtype] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const chartData = Object.entries(dataTypesData).map(([type, count]) => ({
    name: type,
    value: count,
  }));

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Data Profile</h3>
          <p className="text-gray-600">Comprehensive analysis of your dataset</p>
        </div>
        <button
          onClick={onComplete}
          className="btn-primary flex items-center"
        >
          Continue to Training
          <ArrowRight className="ml-2 h-4 w-4" />
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: BarChart3 },
            { id: 'schema', name: 'Schema', icon: TrendingUp },
            { id: 'insights', name: 'Insights', icon: AlertTriangle },
          ].map((tab) => {
            const TabIcon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  flex items-center py-2 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <TabIcon className="mr-2 h-4 w-4" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="card">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Rows</p>
                    <p className="text-2xl font-semibold text-gray-900">{statistics.total_rows.toLocaleString()}</p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Total Columns</p>
                    <p className="text-2xl font-semibold text-gray-900">{statistics.total_columns}</p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <AlertTriangle className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Missing Values</p>
                    <p className="text-2xl font-semibold text-gray-900">{statistics.missing_values.toLocaleString()}</p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <CheckCircle className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Memory Usage</p>
                    <p className="text-2xl font-semibold text-gray-900">{statistics.memory_usage}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Data Types Chart */}
            <div className="card">
              <h4 className="text-lg font-medium text-gray-900 mb-4">Data Types Distribution</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'schema' && (
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-gray-900">Column Schema</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Column Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Null %
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Unique Values
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Issues
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {schema.map((column) => (
                    <tr key={column.name}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {column.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          column.dtype === 'numerical' ? 'bg-blue-100 text-blue-800' :
                          column.dtype === 'categorical' ? 'bg-green-100 text-green-800' :
                          column.dtype === 'datetime' ? 'bg-purple-100 text-purple-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {column.dtype}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {column.null_percentage.toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {column.unique_count.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex space-x-1">
                          {column.is_constant && (
                            <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">Constant</span>
                          )}
                          {column.is_high_cardinality && (
                            <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">High Cardinality</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-6">
            {/* Outliers */}
            {Object.keys(insights.outliers).length > 0 && (
              <div className="card">
                <h4 className="text-lg font-medium text-gray-900 mb-4">Outlier Detection</h4>
                <div className="space-y-2">
                  {Object.entries(insights.outliers).map(([column, info]: [string, any]) => (
                    <div key={column} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="font-medium">{column}</span>
                      <span className="text-sm text-gray-600">
                        {info.count} outliers ({info.percentage.toFixed(1)}%)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Imbalanced Columns */}
            {insights.imbalanced_columns.length > 0 && (
              <div className="card">
                <h4 className="text-lg font-medium text-gray-900 mb-4">Imbalanced Columns</h4>
                <div className="space-y-2">
                  {insights.imbalanced_columns.map((column) => (
                    <div key={column} className="flex items-center p-3 bg-yellow-50 rounded">
                      <AlertTriangle className="h-4 w-4 text-yellow-600 mr-2" />
                      <span className="text-sm">{column}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Data Leakage */}
            {insights.data_leakage.length > 0 && (
              <div className="card">
                <h4 className="text-lg font-medium text-gray-900 mb-4">Potential Data Leakage</h4>
                <div className="space-y-2">
                  {insights.data_leakage.map((leakage, index) => (
                    <div key={index} className="flex items-center p-3 bg-red-50 rounded">
                      <AlertTriangle className="h-4 w-4 text-red-600 mr-2" />
                      <span className="text-sm">{leakage}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* High Correlations */}
            {insights.correlations.length > 0 && (
              <div className="card">
                <h4 className="text-lg font-medium text-gray-900 mb-4">High Correlations</h4>
                <div className="space-y-2">
                  {insights.correlations
                    .filter(corr => Math.abs(corr.correlation) > 0.8)
                    .slice(0, 5)
                    .map((corr) => (
                      <div key={`${corr.column1}-${corr.column2}`} className="flex justify-between items-center p-3 bg-blue-50 rounded">
                        <div className="flex items-center">
                          <span className="text-sm font-medium">{corr.column1} ↔ {corr.column2}</span>
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
          </div>
        )}
      </div>
    </div>
  );
};

export default DataProfile; 