/**
 * FilterPanel component - provides filtering controls for properties.
 */
import React, { useState } from 'react';
import type { PropertyFilters, SortOption } from '../types/property';

interface FilterPanelProps {
  onFilterChange: (filters: PropertyFilters) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ onFilterChange }) => {
  const [filters, setFilters] = useState<PropertyFilters>({
    sort_by: 'total_monthly_cost',
    sort_order: 'asc',
  });

  const handleChange = (field: keyof PropertyFilters, value: any) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleClear = () => {
    const clearedFilters: PropertyFilters = {
      sort_by: 'total_monthly_cost',
      sort_order: 'asc',
    };
    setFilters(clearedFilters);
    onFilterChange(clearedFilters);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Filters</h2>
        <button
          onClick={handleClear}
          className="text-sm text-primary-600 hover:text-primary-800 underline"
        >
          Clear All
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Price Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Price
          </label>
          <input
            type="number"
            placeholder="$0"
            value={filters.price_min || ''}
            onChange={(e) =>
              handleChange('price_min', e.target.value ? Number(e.target.value) : undefined)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max Price
          </label>
          <input
            type="number"
            placeholder="$1,000,000"
            value={filters.price_max || ''}
            onChange={(e) =>
              handleChange('price_max', e.target.value ? Number(e.target.value) : undefined)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Beds & Baths */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Beds
          </label>
          <select
            value={filters.beds || ''}
            onChange={(e) =>
              handleChange('beds', e.target.value ? Number(e.target.value) : undefined)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Any</option>
            <option value="1">1+</option>
            <option value="2">2+</option>
            <option value="3">3+</option>
            <option value="4">4+</option>
            <option value="5">5+</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Baths
          </label>
          <select
            value={filters.baths || ''}
            onChange={(e) =>
              handleChange('baths', e.target.value ? Number(e.target.value) : undefined)
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Any</option>
            <option value="1">1+</option>
            <option value="2">2+</option>
            <option value="3">3+</option>
            <option value="4">4+</option>
          </select>
        </div>

        {/* City */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            City
          </label>
          <input
            type="text"
            placeholder="Salt Lake City"
            value={filters.city || ''}
            onChange={(e) => handleChange('city', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sort By
          </label>
          <select
            value={filters.sort_by || 'total_monthly_cost'}
            onChange={(e) => handleChange('sort_by', e.target.value as SortOption)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="total_monthly_cost">Best Monthly Cost</option>
            <option value="price">Best Overall Price</option>
            <option value="seller_score">Best Seller Score</option>
            <option value="price_per_sqft">Best Price/SqFt</option>
            <option value="days_on_market">Days on Market</option>
          </select>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Order
          </label>
          <select
            value={filters.sort_order || 'asc'}
            onChange={(e) => handleChange('sort_order', e.target.value as 'asc' | 'desc')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="asc">Low to High</option>
            <option value="desc">High to Low</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;
