/**
 * Home page - displays property listings with filters.
 */
import React, { useState, useEffect } from 'react';
import PropertyCard from '../components/PropertyCard';
import FilterPanel from '../components/FilterPanel';
import PropertySummaryPanel from '../components/PropertySummaryPanel';
import PropertyRecommendations from '../components/PropertyRecommendations';
import PropertyComparison from '../components/PropertyComparison';
import QuickAddProperty from '../components/QuickAddProperty';
import { propertiesApi } from '../services/api';
import type { Property, PropertyFilters } from '../types/property';

const Home: React.FC = () => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<PropertyFilters>({});
  const [selectedPropertyIds, setSelectedPropertyIds] = useState<number[]>([]);
  const [showComparison, setShowComparison] = useState(false);
  const [showQuickAdd, setShowQuickAdd] = useState(false);

  useEffect(() => {
    fetchProperties();
  }, [filters]);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await propertiesApi.getProperties(filters);
      setProperties(data);
    } catch (err) {
      setError('Failed to load properties. Please try again later.');
      console.error('Error fetching properties:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setLoading(true);
      const result = await propertiesApi.uploadCSV(file);
      alert(`Successfully uploaded ${result.count} properties!`);
      fetchProperties();
    } catch (err) {
      alert('Failed to upload CSV file. Please check the format and try again.');
      console.error('Error uploading CSV:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePropertySelection = (propertyId: number, selected: boolean) => {
    if (selected) {
      // Add to selection (max 5)
      if (selectedPropertyIds.length < 5) {
        setSelectedPropertyIds([...selectedPropertyIds, propertyId]);
      }
    } else {
      // Remove from selection
      setSelectedPropertyIds(selectedPropertyIds.filter((id) => id !== propertyId));
    }
  };

  const handleCompareClick = () => {
    if (selectedPropertyIds.length >= 2) {
      setShowComparison(true);
    }
  };

  const handleCloseComparison = () => {
    setShowComparison(false);
    setSelectedPropertyIds([]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              Salt Lake Valley Housing Market
            </h1>
            <div className="flex gap-3">
              <button
                onClick={() => setShowQuickAdd(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                + Quick Add
              </button>
              <label className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 cursor-pointer">
                Upload CSV
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Filters */}
        <FilterPanel onFilterChange={setFilters} />

        {/* AI Summary Panel */}
        {!loading && properties.length > 0 && (
          <PropertySummaryPanel filters={filters} maxProperties={50} />
        )}

        {/* AI Property Recommendations */}
        <PropertyRecommendations />

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">Loading properties...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {/* Properties Grid */}
        {!loading && !error && (
          <>
            <div className="flex items-center justify-between mb-4">
              <div className="text-gray-600">Found {properties.length} properties</div>
              {properties.length > 0 && (
                <button
                  onClick={handleCompareClick}
                  disabled={selectedPropertyIds.length < 2}
                  className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                    selectedPropertyIds.length >= 2
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  📊 Compare Selected ({selectedPropertyIds.length}/5)
                </button>
              )}
            </div>
            {properties.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow-md">
                <p className="text-gray-600 text-lg">No properties found.</p>
                <p className="text-gray-500 mt-2">
                  Try adjusting your filters or upload a CSV file to add properties.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {properties.map((property) => (
                  <PropertyCard
                    key={property.id}
                    property={property}
                    selectable={true}
                    selected={selectedPropertyIds.includes(property.id)}
                    onSelectionChange={(selected) =>
                      handlePropertySelection(property.id, selected)
                    }
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* Comparison Modal */}
        {showComparison && (
          <PropertyComparison
            selectedPropertyIds={selectedPropertyIds}
            onClose={handleCloseComparison}
          />
        )}

        {/* Quick Add Modal */}
        {showQuickAdd && (
          <QuickAddProperty
            onClose={() => setShowQuickAdd(false)}
            onSuccess={() => fetchProperties()}
          />
        )}
      </main>
    </div>
  );
};

export default Home;
