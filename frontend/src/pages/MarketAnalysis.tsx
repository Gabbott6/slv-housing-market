/**
 * MarketAnalysis page - AI-powered market analysis dashboard.
 */
import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { propertyAiApi } from '../services/api';
import type { MarketAnalysisRequest, MarketAnalysisResponse } from '../types/ai';

const MarketAnalysis: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<MarketAnalysisResponse | null>(null);
  const [region, setRegion] = useState<string>('');
  const [timePeriod, setTimePeriod] = useState<'7d' | '30d' | '90d'>('30d');

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    try {
      const request: MarketAnalysisRequest = {
        region: region || undefined,
        time_period: timePeriod,
      };

      const response = await propertyAiApi.analyzeMarket(request);
      setAnalysis(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze market');
      console.error('Market analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTemperatureColor = (temp?: string) => {
    switch (temp) {
      case 'hot':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'warm':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'cool':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'cold':
        return 'bg-indigo-100 text-indigo-800 border-indigo-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getTemperatureLabel = (temp?: string) => {
    switch (temp) {
      case 'hot':
        return "Seller's Market";
      case 'warm':
        return 'Balanced Market';
      case 'cool':
        return 'Buyer-Friendly';
      case 'cold':
        return "Buyer's Market";
      default:
        return 'Unknown';
    }
  };

  // Prepare DOM distribution chart data
  const domChartData = analysis?.dom_distribution
    ? [
        {
          name: 'Fast (<14 days)',
          value: analysis.dom_distribution.fast_moving || 0,
          color: '#10b981',
        },
        {
          name: 'Moderate (14-45 days)',
          value: analysis.dom_distribution.moderate || 0,
          color: '#f59e0b',
        },
        {
          name: 'Slow (>45 days)',
          value: analysis.dom_distribution.slow_moving || 0,
          color: '#ef4444',
        },
      ]
    : [];

  // Prepare city distribution chart data
  const cityChartData = analysis?.statistics?.city_distribution
    ? Object.entries(analysis.statistics.city_distribution)
        .map(([city, count]) => ({
          city,
          properties: count,
        }))
        .sort((a, b) => b.properties - a.properties)
        .slice(0, 5)
    : [];

  const formatCurrency = (value: number | undefined) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Market Analysis</h1>
          <p className="mt-2 text-gray-600">
            AI-powered market insights and trends for Salt Lake Valley
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Controls */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Analysis Settings
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Region / City
              </label>
              <input
                type="text"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                placeholder="All regions"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Period
              </label>
              <select
                value={timePeriod}
                onChange={(e) => setTimePeriod(e.target.value as '7d' | '30d' | '90d')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className={`w-full px-6 py-2 rounded-lg font-medium transition-colors ${
                  loading
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-primary-600 hover:bg-primary-700 text-white'
                }`}
              >
                {loading ? 'Analyzing...' : 'Analyze Market'}
              </button>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Analyzing market data...</p>
          </div>
        )}

        {/* Results */}
        {analysis && !loading && (
          <>
            {/* Market Temperature */}
            <div className="mb-6">
              <div
                className={`border-2 rounded-lg p-6 ${getTemperatureColor(
                  analysis.market_temperature
                )}`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Market Temperature</h3>
                    <p className="text-3xl font-bold">
                      {getTemperatureLabel(analysis.market_temperature)}
                    </p>
                    {analysis.statistics && (
                      <p className="text-sm mt-2 opacity-75">
                        Based on {analysis.statistics.total_properties} properties
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    {analysis.from_cache && (
                      <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                        Cached
                      </span>
                    )}
                    <div className="mt-2 text-sm opacity-75">
                      Confidence: {analysis.confidence}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Summary */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Market Overview
              </h3>
              <p className="text-gray-700 leading-relaxed">{analysis.analysis}</p>
            </div>

            {/* Key Statistics Grid */}
            {analysis.statistics && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="text-sm text-gray-500 mb-1">Average Price</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {formatCurrency(analysis.statistics.avg_price)}
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="text-sm text-gray-500 mb-1">Median Price</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {formatCurrency(analysis.statistics.median_price)}
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="text-sm text-gray-500 mb-1">Avg Monthly Cost</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {formatCurrency(analysis.statistics.avg_monthly_cost)}
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="text-sm text-gray-500 mb-1">Days on Market</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {analysis.statistics.avg_days_on_market?.toFixed(0) || 'N/A'} days
                  </div>
                </div>
              </div>
            )}

            {/* Trends */}
            {analysis.trends && analysis.trends.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Key Trends</h3>
                <ul className="space-y-2">
                  {analysis.trends.map((trend, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-primary-600 mr-2">▸</span>
                      <span className="text-gray-700">{trend}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* DOM Distribution Chart */}
              {domChartData.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    Days on Market Distribution
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={domChartData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label
                      >
                        {domChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* City Distribution Chart */}
              {cityChartData.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    Properties by City
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={cityChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="city" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="properties" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Buyer/Seller Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {analysis.buyer_opportunities && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-green-900 mb-3">
                    For Buyers
                  </h3>
                  <p className="text-green-800">{analysis.buyer_opportunities}</p>
                </div>
              )}
              {analysis.seller_considerations && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-blue-900 mb-3">
                    For Sellers
                  </h3>
                  <p className="text-blue-800">{analysis.seller_considerations}</p>
                </div>
              )}
            </div>

            {/* Price Outlook */}
            {analysis.price_outlook && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-purple-900 mb-3">
                  Price Outlook
                </h3>
                <p className="text-purple-800">{analysis.price_outlook}</p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default MarketAnalysis;
