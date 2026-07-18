// Fields match backend schemas/news.py NewsResponse
export interface NewsItem {
  id: number;
  company_id: number;
  headline: string;       // backend field name (not 'title')
  summary: string | null; // backend field name (not 'snippet' or 'ai_summary')
  source: string | null;  // backend field name (not 'source_provider')
  url: string | null;
  published_at: string | null;
  provider: string | null;
  retrieved_at: string | null;
  relevance_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface NewsRunLog {
  id: number;
  started_at: string;
  completed_at: string | null;
  articles_fetched: number;
  articles_stored: number;
  provider: string | null;
  company_name: string | null;
  status: string;
  error_message: string | null;
}

export interface NewsStatisticsResponse {
  total_articles: number;
  articles_last_24h: number;
  articles_by_provider: Record<string, number>;
  articles_by_company: Record<string, number>;
  recent_runs: NewsRunLog[];
}

export interface NewsHealthResponse {
  provider_status: string;
  scheduler_status: string;
  last_refresh_time: string | null;
  last_failure: string | null;
  pending_jobs: number;
}
