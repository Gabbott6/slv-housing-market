/**
 * PropertyRecommendations component - AI-powered personalized property recommendations.
 * Users input their criteria and receive tailored property suggestions with match scores.
 */
import React, { useState } from 'react';
import { propertyAiApi } from '../services/api';
import type { RecommendationCriteria, PropertyRecommendationResponse } from '../types/ai';

const PropertyRecommendations: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<PropertyRecommendationResponse | null>(null);

  // Form state
  const [budget, setBudget] = useState<number>(500000);
  const [beds, setBeds] = useState<number>(3);
  const [baths, setBaths] = useState<number>(2);
  const [lifestyle, setLifestyle] = useState<string>('family');
  const [city, setCity] = useState<string>('');
  const [monthlyCostPriority, setMonthlyCostPriority] = useState<number>(40);
  const [locationPriority, setLocationPriority] = useState<number>(30);
  const [valuePriority, setValuePriority] = useState<number>(20);
  const [spacePriority, setSpacePriority] = useState<number>(10);

  const handleGetRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      const criteria: RecommendationCriteria = {
        budget_max: budget,
        beds_min: beds,
        baths_min: baths,
        lifestyle: lifestyle as any,
        city_preference: city || undefined,
        priorities: {
          monthly_cost: monthlyCostPriority,
          location: locationPriority,
          value: valuePriority,
          space: spacePriority,
        },
      };

      const response = await propertyAiApi.recommendProperties(criteria);
      setRecommendations(response);
      setShowForm(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get recommendations');
      console.error('Recommendations error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
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

  return (
    <div className="mb-6">
      {/* Get Recommendations Button */}
      {!showForm && !recommendations && (
        <button
          onClick={() => setShowForm(true)}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
        >
          🎯 Get Personalized Property Recommendations
        </button>
      )}

      {/* Criteria Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Tell Us What You're Looking For
          </h2>

          <div className="space-y-4">
            {/* Budget */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Maximum Budget: {formatCurrency(budget)}
              </label>
              <input
                type="range"
                min="100000"
                max="1000000"
                step="10000"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Beds and Baths */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Bedrooms
                </label>
                <select
                  value={beds}
                  onChange={(e) => setBeds(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="1">1+</option>
                  <option value="2">2+</option>
                  <option value="3">3+</option>
                  <option value="4">4+</option>
                  <option value="5">5+</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Bathrooms
                </label>
                <select
                  value={baths}
                  onChange={(e) => setBaths(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="1">1+</option>
                  <option value="1.5">1.5+</option>
                  <option value="2">2+</option>
                  <option value="2.5">2.5+</option>
                  <option value="3">3+</option>
                </select>
              </div>
            </div>

            {/* Lifestyle */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Buyer Type
              </label>
              <select
                value={lifestyle}
                onChange={(e) => setLifestyle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="first_time_buyer">First-Time Buyer</option>
                <option value="family">Family</option>
                <option value="investor">Investor</option>
                <option value="downsizer">Downsizer</option>
              </select>
            </div>

            {/* City Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City Preference (Optional)
              </label>
              <input
                type="text"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="e.g., Sandy, Draper..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            {/* Priorities */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                What Matters Most? (Adjust priorities)
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-700 mb-1">
                    Monthly Cost: {monthlyCostPriority}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={monthlyCostPriority}
                    onChange={(e) => setMonthlyCostPriority(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-700 mb-1">
                    Location: {locationPriority}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={locationPriority}
                    onChange={(e) => setLocationPriority(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-700 mb-1">
                    Value (Price/sqft): {valuePriority}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={valuePriority}
                    onChange={(e) => setValuePriority(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-700 mb-1">
                    Space: {spacePriority}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={spacePriority}
                    onChange={(e) => setSpacePriority(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-4">
              <button
                onClick={handleGetRecommendations}
                disabled={loading}
                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
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
                    Finding Matches...
                  </span>
                ) : (
                  'Get Recommendations'
                )}
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              <p className="font-medium">Error getting recommendations</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}
        </div>
      )}

      {/* Recommendations Display */}
      {recommendations && (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Your Personalized Recommendations
            </h2>
            <div className="flex items-center gap-2">
              {recommendations.from_cache && (
                <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                  Cached
                </span>
              )}
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceBadgeColor(
                  recommendations.confidence
                )}`}
              >
                {recommendations.confidence.charAt(0).toUpperCase() +
                  recommendations.confidence.slice(1)}{' '}
                Confidence
              </span>
            </div>
          </div>

          <p className="text-gray-600 mb-6">{recommendations.message}</p>

          {/* Recommendations List */}
          <div className="space-y-6">
            {recommendations.recommendations.map((rec, index) => (
              <div
                key={rec.property_id}
                className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">
                      #{index + 1} - {rec.address}
                    </h3>
                    <p className="text-gray-600">{rec.city}</p>
                    <p className="text-2xl font-bold text-primary-600 mt-1">
                      {formatCurrency(rec.price)}
                    </p>
                  </div>
                  <div
                    className={`px-4 py-2 rounded-lg font-bold text-lg ${getScoreColor(
                      rec.match_score
                    )}`}
                  >
                    {rec.match_score.toFixed(0)}% Match
                  </div>
                </div>

                {/* Match Explanation */}
                <div className="bg-purple-50 p-4 rounded-lg mb-4">
                  <p className="text-purple-900">{rec.match_explanation}</p>
                </div>

                {/* Pros and Cons */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Pros */}
                  <div>
                    <h4 className="font-semibold text-green-800 mb-2">✅ Pros</h4>
                    <ul className="space-y-1">
                      {rec.pros.map((pro, i) => (
                        <li key={i} className="text-sm text-gray-700 flex items-start">
                          <span className="text-green-600 mr-2">•</span>
                          <span>{pro}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Cons */}
                  <div>
                    <h4 className="font-semibold text-orange-800 mb-2">⚠️ Cons</h4>
                    <ul className="space-y-1">
                      {rec.cons.map((con, i) => (
                        <li key={i} className="text-sm text-gray-700 flex items-start">
                          <span className="text-orange-600 mr-2">•</span>
                          <span>{con}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-6 mt-6 border-t border-gray-200">
            <button
              onClick={() => setShowForm(true)}
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Adjust Criteria
            </button>
            <button
              onClick={() => setRecommendations(null)}
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

export default PropertyRecommendations;
