/**
 * API client for communicating with the backend.
 */
import axios from 'axios';
import type {
  Property,
  PropertyFilters,
  MarketTrend,
  TrendSummary,
  AIQuestionRequest,
  AIAnswerResponse
} from '../types/property';
import type {
  PropertySummaryRequest,
  PropertySummaryResponse,
  RecommendationCriteria,
  PropertyRecommendationResponse,
  PropertyComparisonRequest,
  PropertyComparisonResponse,
  MarketAnalysisRequest,
  MarketAnalysisResponse
} from '../types/ai';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Properties API
export const propertiesApi = {
  /**
   * Get properties with optional filters and sorting.
   */
  async getProperties(filters?: PropertyFilters): Promise<Property[]> {
    const response = await api.get('/properties', { params: filters });
    return response.data;
  },

  /**
   * Get a specific property by ID.
   */
  async getProperty(id: number): Promise<Property> {
    const response = await api.get(`/properties/${id}`);
    return response.data;
  },

  /**
   * Upload properties via CSV file.
   */
  async uploadCSV(file: File): Promise<{ message: string; count: number }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/properties/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Quick-add a property with minimal data.
   */
  async quickAddProperty(data: {
    address: string;
    city?: string;
    price: number;
    beds?: number;
    baths?: number;
    sqft?: number;
    hoa_fee?: number;
    listing_url?: string;
    notes?: string;
  }): Promise<Property> {
    const response = await api.post('/properties/quick-add', data);
    return response.data;
  },

  /**
   * Import property data from a Zillow or Redfin URL.
   */
  async importFromUrl(url: string): Promise<{
    success: boolean;
    data: {
      address?: string;
      city?: string;
      price?: number;
      beds?: number;
      baths?: number;
      sqft?: number;
      hoa_fee?: number;
      listing_url?: string;
    };
    message: string;
  }> {
    const response = await api.post('/properties/import-from-url', { url });
    return response.data;
  },

  /**
   * Get detailed cost breakdown for a property.
   */
  async getPropertyCosts(id: number): Promise<any> {
    const response = await api.get(`/properties/${id}/costs`);
    return response.data;
  },
};

// Market Trends API
export const trendsApi = {
  /**
   * Get market trends with optional filters.
   */
  async getTrends(filters?: {
    region?: string;
    metric_name?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<MarketTrend[]> {
    const response = await api.get('/trends', { params: filters });
    return response.data;
  },

  /**
   * Get trend summary for a region.
   */
  async getTrendSummary(region: string = 'Salt Lake County'): Promise<TrendSummary[]> {
    const response = await api.get('/trends/summary', {
      params: { region },
    });
    return response.data;
  },

  /**
   * Add market trend data (batch insert).
   */
  async addTrendData(data: any[]): Promise<{ message: string; count: number }> {
    const response = await api.post('/trends', data);
    return response.data;
  },
};

// AI Chat API
export const aiApi = {
  /**
   * Ask a question about housing codes.
   */
  async askQuestion(request: AIQuestionRequest): Promise<AIAnswerResponse> {
    const response = await api.post('/ai/ask', request);
    return response.data;
  },

  /**
   * Search housing codes directly.
   */
  async searchCodes(query: string, jurisdiction?: string): Promise<any> {
    const response = await api.get('/ai/codes/search', {
      params: { query, jurisdiction },
    });
    return response.data;
  },

  /**
   * Check AI service health.
   */
  async healthCheck(): Promise<any> {
    const response = await api.get('/ai/health');
    return response.data;
  },
};

// Property AI API
export const propertyAiApi = {
  /**
   * Get AI-powered summary of properties.
   */
  async summarizeProperties(
    request: PropertySummaryRequest
  ): Promise<PropertySummaryResponse> {
    const response = await api.post('/property-ai/summarize', request);
    return response.data;
  },

  /**
   * Get AI-powered property recommendations.
   */
  async recommendProperties(
    criteria: RecommendationCriteria
  ): Promise<PropertyRecommendationResponse> {
    const response = await api.post('/property-ai/recommend', criteria);
    return response.data;
  },

  /**
   * Compare properties with AI insights.
   */
  async compareProperties(
    request: PropertyComparisonRequest
  ): Promise<PropertyComparisonResponse> {
    const response = await api.post('/property-ai/compare', request);
    return response.data;
  },

  /**
   * Get AI-powered market analysis.
   */
  async analyzeMarket(
    request: MarketAnalysisRequest
  ): Promise<MarketAnalysisResponse> {
    const response = await api.post('/property-ai/market-analysis', request);
    return response.data;
  },

  /**
   * Check Property AI service health.
   */
  async healthCheck(): Promise<any> {
    const response = await api.get('/property-ai/health');
    return response.data;
  },
};

export default api;
