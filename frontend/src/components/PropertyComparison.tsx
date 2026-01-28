/**
 * PropertyComparison component - AI-powered side-by-side property comparison.
 * Displays comparison results with winner identification by category.
 */
import React, { useState } from 'react';
import { propertyAiApi } from '../services/api';
import type { PropertyComparisonRequest, PropertyComparisonResponse } from '../types/ai';

interface PropertyComparisonProps {
  selectedPropertyIds: number[];
  onClose: () => void;
}

const PropertyComparison: React.FC<PropertyComparisonProps> = ({
  selectedPropertyIds,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [comparison, setComparison] = useState<PropertyComparisonResponse | null>(null);

  React.useEffect(() => {
    if (selectedPropertyIds.length >= 2) {
      handleCompare();
    }
  }, [selectedPropertyIds]);

  const handleCompare = async () => {
    setLoading(true);
    setError(null);

    try {
      const request: PropertyComparisonRequest = {
        property_ids: selectedPropertyIds,
      };

      const response = await propertyAiApi.compareProperties(request);
      setComparison(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to compare properties');
      console.error('Comparison error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number | null | undefined) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
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

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'monthly_budget':
        return '💰';
      case 'space_value':
        return '📏';
      case 'investment':
        return '📈';
      case 'location':
        return '📍';
      default:
        return '🏆';
    }
  };

  const getCategoryName = (category: string) => {
    switch (category) {
      case 'monthly_budget':
        return 'Monthly Budget';
      case 'space_value':
        return 'Space & Value';
      case 'investment':
        return 'Investment Potential';
      case 'location':
        return 'Location & Lifestyle';
      default:
        return category;
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md">
          <div className="flex flex-col items-center">
            <svg
              className="animate-spin h-12 w-12 text-primary-600 mb-4"
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
            <p className="text-lg font-medium text-gray-900">
              Analyzing Properties...
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Comparing {selectedPropertyIds.length} properties
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            <p className="font-medium">Error comparing properties</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
          <button
            onClick={onClose}
            className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  if (!comparison) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full my-8">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-3xl font-bold text-gray-900">Property Comparison</h2>
            <div className="flex items-center gap-2">
              {comparison.from_cache && (
                <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                  Cached
                </span>
              )}
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceBadgeColor(
                  comparison.confidence
                )}`}
              >
                {comparison.confidence.charAt(0).toUpperCase() +
                  comparison.confidence.slice(1)}{' '}
                Confidence
              </span>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <p className="text-blue-900">{comparison.summary}</p>
          </div>

          {/* Comparison Table */}
          <div className="overflow-x-auto mb-6">
            <table className="min-w-full border border-gray-200">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                    Attribute
                  </th>
                  {comparison.properties.map((prop) => (
                    <th
                      key={prop.property_id}
                      className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b border-l"
                    >
                      <div className="flex items-center gap-2">
                        <span className="bg-primary-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold">
                          {prop.property_letter}
                        </span>
                        <div>
                          <div className="font-bold">{prop.address}</div>
                          <div className="text-xs text-gray-500">{prop.city}</div>
                        </div>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {/* Price */}
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-700 border-b">
                    Price
                  </td>
                  {comparison.properties.map((prop) => (
                    <td
                      key={prop.property_id}
                      className="px-4 py-3 text-sm text-gray-900 border-b border-l"
                    >
                      {formatCurrency(prop.price)}
                    </td>
                  ))}
                </tr>

                {/* Monthly Cost */}
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-700 border-b">
                    Monthly Cost
                  </td>
                  {comparison.properties.map((prop) => (
                    <td
                      key={prop.property_id}
                      className="px-4 py-3 text-sm text-gray-900 border-b border-l"
                    >
                      {formatCurrency(prop.monthly_cost)}
                    </td>
                  ))}
                </tr>

                {/* Square Feet */}
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-700 border-b">
                    Square Feet
                  </td>
                  {comparison.properties.map((prop) => (
                    <td
                      key={prop.property_id}
                      className="px-4 py-3 text-sm text-gray-900 border-b border-l"
                    >
                      {prop.sqft ? prop.sqft.toLocaleString() : 'N/A'} sqft
                    </td>
                  ))}
                </tr>

                {/* Price per sqft */}
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-700 border-b">
                    Price / sqft
                  </td>
                  {comparison.properties.map((prop) => (
                    <td
                      key={prop.property_id}
                      className="px-4 py-3 text-sm text-gray-900 border-b border-l"
                    >
                      {prop.price_per_sqft
                        ? `$${prop.price_per_sqft.toFixed(2)}`
                        : 'N/A'}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>

          {/* Winners by Category */}
          <div className="mb-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Winners by Category</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(comparison.winners).map(([category, winner]) => (
                <div
                  key={category}
                  className="bg-green-50 border border-green-200 rounded-lg p-4"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">{getCategoryIcon(category)}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-green-900">
                          {getCategoryName(category)}
                        </h4>
                        <span className="bg-green-600 text-white px-2 py-0.5 rounded-full text-sm font-bold">
                          {winner.property_letter}
                        </span>
                      </div>
                      <p className="text-sm text-green-800">{winner.reason}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Overall Recommendation */}
          <div className="bg-primary-50 border-2 border-primary-300 rounded-lg p-6 mb-6">
            <div className="flex items-start gap-4">
              <span className="text-4xl">🏆</span>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-2xl font-bold text-primary-900">
                    Overall Recommendation
                  </h3>
                  <span className="bg-primary-600 text-white px-3 py-1 rounded-full text-lg font-bold">
                    Property {comparison.overall_recommendation.property_letter}
                  </span>
                </div>
                <p className="text-lg text-primary-800">
                  {comparison.overall_recommendation.reason}
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              Close Comparison
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyComparison;
