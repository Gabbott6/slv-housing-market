/**
 * PropertyCard component - displays a single property listing.
 */
import React from 'react';
import type { Property } from '../types/property';

interface PropertyCardProps {
  property: Property;
  onClick?: () => void;
  selectable?: boolean;
  selected?: boolean;
  onSelectionChange?: (selected: boolean) => void;
}

const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  onClick,
  selectable = false,
  selected = false,
  onSelectionChange,
}) => {
  const formatCurrency = (value: number | null) => {
    if (value === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const handleSelectionClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onSelectionChange) {
      onSelectionChange(!selected);
    }
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 cursor-pointer border ${
        selected ? 'border-primary-500 border-2 bg-primary-50' : 'border-gray-200'
      }`}
      onClick={onClick}
    >
      {/* Selection Checkbox */}
      {selectable && (
        <div className="flex justify-end mb-2">
          <label className="flex items-center cursor-pointer" onClick={handleSelectionClick}>
            <input
              type="checkbox"
              checked={selected}
              onChange={(e) => {
                if (onSelectionChange) {
                  onSelectionChange(e.target.checked);
                }
              }}
              className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <span className="ml-2 text-sm text-gray-700">Compare</span>
          </label>
        </div>
      )}

      {/* Address */}
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        {property.address}
      </h3>
      <p className="text-gray-600 mb-4">{property.city || 'Salt Lake City'}, UT</p>

      {/* Price and Monthly Cost */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-500">Price</p>
          <p className="text-2xl font-bold text-primary-600">
            {formatCurrency(property.price)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Monthly Cost</p>
          <p className="text-2xl font-bold text-green-600">
            {formatCurrency(property.total_monthly_cost)}
          </p>
        </div>
      </div>

      {/* Property Details */}
      <div className="grid grid-cols-3 gap-2 mb-4 text-sm">
        <div>
          <span className="text-gray-500">Beds:</span>
          <span className="ml-2 font-medium">{property.beds || 'N/A'}</span>
        </div>
        <div>
          <span className="text-gray-500">Baths:</span>
          <span className="ml-2 font-medium">{property.baths || 'N/A'}</span>
        </div>
        <div>
          <span className="text-gray-500">Sqft:</span>
          <span className="ml-2 font-medium">
            {property.sqft ? property.sqft.toLocaleString() : 'N/A'}
          </span>
        </div>
      </div>

      {/* Cost Breakdown */}
      {property.monthly_mortgage && (
        <div className="border-t border-gray-200 pt-4 text-sm space-y-1">
          <div className="flex justify-between">
            <span className="text-gray-600">Mortgage:</span>
            <span className="font-medium">{formatCurrency(property.monthly_mortgage)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Taxes:</span>
            <span className="font-medium">{formatCurrency(property.monthly_taxes)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Insurance:</span>
            <span className="font-medium">{formatCurrency(property.monthly_insurance)}</span>
          </div>
          {property.monthly_hoa && property.monthly_hoa > 0 && (
            <div className="flex justify-between">
              <span className="text-gray-600">HOA:</span>
              <span className="font-medium">{formatCurrency(property.monthly_hoa)}</span>
            </div>
          )}
        </div>
      )}

      {/* Seller Score & Days on Market */}
      <div className="mt-4 flex justify-between items-center text-sm">
        {property.seller_score && (
          <div className="flex items-center">
            <span className="text-gray-500">Seller Score:</span>
            <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded font-medium">
              {property.seller_score.toFixed(0)}/100
            </span>
          </div>
        )}
        {property.days_on_market !== null && (
          <div className="text-gray-600">
            {property.days_on_market} days on market
          </div>
        )}
      </div>

      {/* Listing Link */}
      {property.listing_url && (
        <div className="mt-4">
          <a
            href={property.listing_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-600 hover:text-primary-800 underline text-sm"
            onClick={(e) => e.stopPropagation()}
          >
            View Original Listing →
          </a>
        </div>
      )}

      {/* Source Citation */}
      {property.price_source_name && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            Source: {property.price_source_name}
            {property.price_source_url && (
              <a
                href={property.price_source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-1 text-primary-600 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                (view)
              </a>
            )}
          </p>
        </div>
      )}
    </div>
  );
};

export default PropertyCard;
