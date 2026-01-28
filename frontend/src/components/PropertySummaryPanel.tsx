/**
 * PropertySummaryPanel component - AI-powered property analysis summary.
 * Displays insights, statistics, and recommendations for filtered properties.
 */
import React, { useState } from 'react';
import { propertyAiApi } from '../services/api';
import type { PropertyFilters } from '../types/property';
import type { PropertySummaryResponse } from '../types/ai';

interface PropertySummaryPanelProps {
  filters?: PropertyFilters;
  maxProperties?: number;
}

const PropertySummaryPanel: React.FC<PropertySummaryPanelProps> = ({
  filters,
  maxProperties = 50,
}) => {
  const [summary, setSummary] = useState<PropertySummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSummarize = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await propertyAiApi.summarizeProperties({
        filters,
        max_properties: maxProperties,
      });

      setSummary(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate summary');
      console.error('Summary error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceBadgeColor = (confidence: string) => {
    switch (confidence) {
      case 'high':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="mb-6">
      {/* Summarize Button */}
      {!summary && (
        <button
          onClick={handleSummarize}
          disabled={loading}
          className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin h-5 w-5 mr-3"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Analyzing Properties...
            </span>
          ) : (
            '✨ Summarize Current Results with AI'
          )}
        </button>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="font-medium">Error generating summary</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Summary Display */}
      {summary && (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          {/* Header with Confidence Badge */}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">AI Market Summary</h2>
            <div className="flex items-center gap-2">
              {summary.from_cache && (
                <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                  Cached
                </span>
              )}
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceBadgeColor(
                  summary.confidence
                )}`}
              >
                {summary.confidence.charAt(0).toUpperCase() + summary.confidence.slice(1)}{' '}
                Confidence
              </span>
            </div>
          </div>

          {/* Properties Analyzed */}
          <p className="text-gray-600 text-sm mb-4">
            Analysis based on {summary.properties_analyzed} properties
          </p>

          {/* Main Summary */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Overview</h3>
            <p className="text-gray-700 leading-relaxed">{summary.summary}</p>
          </div>

          {/* Key Insights */}
          {summary.key_insights.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Key Insights</h3>
              <ul className="space-y-2">
                {summary.key_insights.map((insight, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-primary-600 mr-2 mt-1">•</span>
                    <span className="text-gray-700">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Statistics */}
          {Object.keys(summary.statistics).length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Market Statistics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {summary.statistics.avg_price && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-500">Avg Price</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(summary.statistics.avg_price)}
                    </p>
                  </div>
                )}
                {summary.statistics.median_price && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-500">Median Price</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(summary.statistics.median_price)}
                    </p>
                  </div>
                )}
                {summary.statistics.avg_monthly_cost && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-500">Avg Monthly Cost</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(summary.statistics.avg_monthly_cost)}
                    </p>
                  </div>
                )}
                {summary.statistics.avg_price_per_sqft && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-500">Avg $/sqft</p>
                    <p className="text-lg font-semibold text-gray-900">
                      ${summary.statistics.avg_price_per_sqft.toFixed(2)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Buyer Recommendations */}
          {summary.buyer_recommendations &&
            Object.keys(summary.buyer_recommendations).length > 0 && (
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">
                  Recommendations by Buyer Type
                </h3>
                <div className="space-y-3">
                  {summary.buyer_recommendations.first_time_buyer && (
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-blue-900 mb-1">
                        First-Time Buyers
                      </h4>
                      <p className="text-blue-800 text-sm">
                        {summary.buyer_recommendations.first_time_buyer}
                      </p>
                    </div>
                  )}
                  {summary.buyer_recommendations.family && (
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-green-900 mb-1">Families</h4>
                      <p className="text-green-800 text-sm">
                        {summary.buyer_recommendations.family}
                      </p>
                    </div>
                  )}
                  {summary.buyer_recommendations.investor && (
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-purple-900 mb-1">Investors</h4>
                      <p className="text-purple-800 text-sm">
                        {summary.buyer_recommendations.investor}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t border-gray-200">
            <button
              onClick={handleSummarize}
              disabled={loading}
              className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:bg-gray-400"
            >
              Refresh Summary
            </button>
            <button
              onClick={() => setSummary(null)}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertySummaryPanel;
