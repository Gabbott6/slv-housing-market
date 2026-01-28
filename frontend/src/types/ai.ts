/**
 * TypeScript types for AI-powered property analysis.
 * Mirrors backend Pydantic models for type safety.
 */

export interface PropertyFilters {
  price_min?: number;
  price_max?: number;
  beds?: number;
  baths?: number;
  city?: string;
}

export interface PropertySummaryRequest {
  filters?: PropertyFilters;
  max_properties?: number;
  focus_areas?: string[];
}

export interface BuyerRecommendations {
  first_time_buyer?: string;
  family?: string;
  investor?: string;
}

export interface PropertySummaryResponse {
  summary: string;
  key_insights: string[];
  buyer_recommendations: BuyerRecommendations;
  statistics: {
    count?: number;
    avg_price?: number;
    median_price?: number;
    min_price?: number;
    max_price?: number;
    avg_monthly_cost?: number;
    avg_price_per_sqft?: number;
    most_common_city?: string;
    cities?: string[];
  };
  properties_analyzed: number;
  confidence: 'low' | 'medium' | 'high';
  from_cache: boolean;
  error?: string;
}

export interface RecommendationCriteria {
  budget_max: number;
  beds_min?: number;
  baths_min?: number;
  priorities?: {
    monthly_cost?: number;
    location?: number;
    value?: number;
    space?: number;
  };
  lifestyle?: 'first_time_buyer' | 'family' | 'investor' | 'downsizer';
  city_preference?: string;
}

export interface PropertyRecommendation {
  property_id: number;
  address: string;
  city?: string;
  price: number;
  match_score: number;
  match_explanation: string;
  pros: string[];
  cons: string[];
}

export interface PropertyRecommendationResponse {
  message: string;
  recommended_properties: number[];
  recommendations: PropertyRecommendation[];
  confidence: 'low' | 'medium' | 'high';
  from_cache: boolean;
  error?: string;
}

export interface PropertyComparisonRequest {
  property_ids: number[];
  aspects?: string[];
}

export interface WinnerInfo {
  property_letter: string;
  reason: string;
}

export interface PropertyDetail {
  property_id: number;
  property_letter: string;
  address: string;
  city?: string;
  price: number;
  monthly_cost?: number;
  sqft?: number;
  price_per_sqft?: number;
}

export interface PropertyComparisonResponse {
  summary: string;
  winners: {
    [key: string]: WinnerInfo;
  };
  overall_recommendation: WinnerInfo;
  properties: PropertyDetail[];
  confidence: 'low' | 'medium' | 'high';
  from_cache: boolean;
  error?: string;
}

export interface MarketAnalysisRequest {
  region?: string;
  time_period?: '7d' | '30d' | '90d';
  focus?: string;
}

export interface MarketAnalysisResponse {
  analysis: string;
  trends: string[];
  buyer_opportunities?: string;
  seller_considerations?: string;
  price_outlook?: string;
  statistics?: {
    total_properties?: number;
    avg_price?: number;
    median_price?: number;
    min_price?: number;
    max_price?: number;
    avg_monthly_cost?: number;
    avg_price_per_sqft?: number;
    avg_days_on_market?: number;
    median_days_on_market?: number;
    city_distribution?: { [key: string]: number };
  };
  market_temperature?: 'hot' | 'warm' | 'cool' | 'cold';
  dom_distribution?: {
    avg_dom?: number;
    fast_moving?: number;
    moderate?: number;
    slow_moving?: number;
    fast_moving_pct?: number;
    market_temperature?: string;
    total_analyzed?: number;
  };
  confidence: 'low' | 'medium' | 'high';
  from_cache: boolean;
  error?: string;
}
