/**
 * TypeScript interfaces for the SLV Housing Market application.
 */

export interface Source {
  name: string;
  url: string;
  date?: string;
}

export interface Property {
  id: number;
  address: string;
  city: string | null;
  price: number;
  beds: number | null;
  baths: number | null;
  sqft: number | null;
  price_per_sqft: number | null;
  property_type: string | null;
  hoa_fee: number | null;

  // Calculated monthly costs
  monthly_mortgage: number | null;
  monthly_taxes: number | null;
  monthly_insurance: number | null;
  monthly_hoa: number | null;
  total_monthly_cost: number | null;

  // Listing details
  days_on_market: number | null;
  listing_url: string | null;
  seller_score: number | null;

  // Sources
  price_source_name: string | null;
  price_source_url: string | null;
}

export interface PropertyFilters {
  price_min?: number;
  price_max?: number;
  beds?: number;
  baths?: number;
  city?: string;
  sort_by?: SortOption;
  sort_order?: 'asc' | 'desc';
}

export type SortOption =
  | 'total_monthly_cost'
  | 'price'
  | 'seller_score'
  | 'price_per_sqft'
  | 'days_on_market';

export interface MarketTrend {
  id: number;
  date: string;
  region: string;
  metric_name: string;
  value: number;
  metric_type: string | null;
  unit: string | null;
  source_name: string | null;
}

export interface TrendSummary {
  metric_name: string;
  region: string;
  current_value: number;
  previous_value: number | null;
  change_percent: number | null;
  data_points: number;
}

export interface AIQuestionRequest {
  question: string;
  jurisdiction?: string;
}

export interface AIAnswerResponse {
  answer: string;
  sources: CodeSource[];
  confidence: 'low' | 'medium' | 'high' | 'error';
  codes_found: number;
}

export interface CodeSource {
  code_section: string;
  title: string;
  jurisdiction: string;
  source_name: string;
  source_url: string;
  last_updated: string | null;
}
