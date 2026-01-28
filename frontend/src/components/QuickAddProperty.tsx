/**
 * QuickAddProperty component - Simple form for manually adding properties.
 * Perfect for copying details from Zillow/Redfin.
 */
import React, { useState } from 'react';
import { propertiesApi } from '../services/api';

interface QuickAddPropertyProps {
  onClose: () => void;
  onSuccess: () => void;
}

const QuickAddProperty: React.FC<QuickAddPropertyProps> = ({ onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [urlImportUrl, setUrlImportUrl] = useState('');
  const [urlImportLoading, setUrlImportLoading] = useState(false);
  const [urlImportError, setUrlImportError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    address: '',
    city: '',
    price: '',
    beds: '',
    baths: '',
    sqft: '',
    hoa_fee: '',
    listing_url: '',
    notes: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const requestData = {
        address: formData.address,
        city: formData.city || undefined,
        price: parseFloat(formData.price),
        beds: formData.beds ? parseInt(formData.beds) : undefined,
        baths: formData.baths ? parseFloat(formData.baths) : undefined,
        sqft: formData.sqft ? parseInt(formData.sqft) : undefined,
        hoa_fee: formData.hoa_fee ? parseFloat(formData.hoa_fee) : undefined,
        listing_url: formData.listing_url || undefined,
        notes: formData.notes || undefined,
      };

      await propertiesApi.quickAddProperty(requestData);
      setSuccess(true);

      // Show success briefly then close
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add property');
      console.error('Quick add error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAnother = () => {
    setFormData({
      address: '',
      city: '',
      price: '',
      beds: '',
      baths: '',
      sqft: '',
      hoa_fee: '',
      listing_url: '',
      notes: '',
    });
    setSuccess(false);
    setError(null);
  };

  const handleImportFromUrl = async () => {
    if (!urlImportUrl.trim()) {
      setUrlImportError('Please enter a URL');
      return;
    }

    setUrlImportLoading(true);
    setUrlImportError(null);
    setError(null);

    try {
      const response = await propertiesApi.importFromUrl(urlImportUrl);

      if (response.success && response.data) {
        // Auto-fill form with imported data
        setFormData({
          address: response.data.address || '',
          city: response.data.city || '',
          price: response.data.price ? response.data.price.toString() : '',
          beds: response.data.beds ? response.data.beds.toString() : '',
          baths: response.data.baths ? response.data.baths.toString() : '',
          sqft: response.data.sqft ? response.data.sqft.toString() : '',
          hoa_fee: response.data.hoa_fee ? response.data.hoa_fee.toString() : '',
          listing_url: response.data.listing_url || urlImportUrl,
          notes: '',
        });

        // Clear URL input after successful import
        setUrlImportUrl('');
      }
    } catch (err: any) {
      setUrlImportError(
        err.response?.data?.detail || 'Failed to import property from URL'
      );
      console.error('URL import error:', err);
    } finally {
      setUrlImportLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Quick Add Property</h2>
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

          {/* URL Import Section */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800 mb-3">
              <strong>Quick Import:</strong> Paste a Zillow or Redfin URL below to auto-fill property details!
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={urlImportUrl}
                onChange={(e) => setUrlImportUrl(e.target.value)}
                placeholder="https://www.zillow.com/homedetails/..."
                className="flex-1 px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                disabled={urlImportLoading}
              />
              <button
                onClick={handleImportFromUrl}
                disabled={urlImportLoading || !urlImportUrl.trim()}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                  urlImportLoading || !urlImportUrl.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {urlImportLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Importing...
                  </div>
                ) : (
                  'Import'
                )}
              </button>
            </div>
            {urlImportError && (
              <p className="text-sm text-red-600 mt-2">{urlImportError}</p>
            )}
          </div>

          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
              Property added successfully!
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <div className="space-y-4">
              {/* Address (Required) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  required
                  placeholder="123 Main St"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {/* City */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  placeholder="Sandy, Draper, Provo, etc."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {/* Price (Required) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Price <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  required
                  placeholder="425000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {/* Beds and Baths Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bedrooms
                  </label>
                  <input
                    type="number"
                    name="beds"
                    value={formData.beds}
                    onChange={handleChange}
                    placeholder="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bathrooms
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    name="baths"
                    value={formData.baths}
                    onChange={handleChange}
                    placeholder="2.5"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              {/* Square Feet and HOA Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Square Feet
                  </label>
                  <input
                    type="number"
                    name="sqft"
                    value={formData.sqft}
                    onChange={handleChange}
                    placeholder="1850"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    HOA Fee (monthly)
                  </label>
                  <input
                    type="number"
                    name="hoa_fee"
                    value={formData.hoa_fee}
                    onChange={handleChange}
                    placeholder="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              {/* Listing URL */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Listing URL
                </label>
                <input
                  type="url"
                  name="listing_url"
                  value={formData.listing_url}
                  onChange={handleChange}
                  placeholder="https://www.zillow.com/..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={3}
                  placeholder="Optional notes about this property..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 mt-6">
              <button
                type="submit"
                disabled={loading || !formData.address || !formData.price}
                className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
                  loading || !formData.address || !formData.price
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-primary-600 hover:bg-primary-700 text-white'
                }`}
              >
                {loading ? 'Adding...' : 'Add Property'}
              </button>
              {success && (
                <button
                  type="button"
                  onClick={handleAddAnother}
                  className="px-6 py-3 border-2 border-primary-600 text-primary-600 rounded-lg font-medium hover:bg-primary-50 transition-colors"
                >
                  Add Another
                </button>
              )}
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default QuickAddProperty;
