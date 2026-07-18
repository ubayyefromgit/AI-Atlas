export interface Company {
  id: number;
  name: string;
  slug: string;
  country: string;
  ai_category: string | null;
  company_type: string | null;
  maturity: number | null;
  website: string | null;
  segment_tags: string[];
  use_cases: string[];
  funding: number | null;
  estimated_revenue: number | null;
  top_german_customers: string[];
  deployment_evidence: string | null;
  germany_presence: string | null;
  status: string;
  source: string;
  created_at: string;
  updated_at: string;
}

// Matches backend schemas/company.py PaginatedResponse
export interface CompanyListResponse {
  items: Company[];
  total: number;
  offset: number;
  limit: number;
  has_next: boolean;
  returned: number;
  execution_ms: number;
}

export interface CompanyStatistics {
  total_companies: number;
  companies_per_segment: Record<string, number>;
  companies_per_ai_category: Record<string, number>;
  companies_per_company_type: Record<string, number>;
  maturity_distribution: Record<string, number>;
  country_distribution: Record<string, number>;
  problem_counts: Record<string, number>;
  average_maturity: number;
  average_revenue: number | null;
}

export interface Problem {
  id: number;
  company_id: number;
  problem_name: string;
  category: string;
  severity: string | null;
  roi_benchmark: string | null;
  payback_period: string | null;
}
