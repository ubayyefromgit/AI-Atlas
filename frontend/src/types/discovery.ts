export interface EvidenceItem {
  url: string;
  title: string;
  snippet: string;
  retrieved_at: string;
}

export interface ConfidenceExplanation {
  website_verified: boolean;
  evidence_count: number;
  field_completeness: number;
  duplicate_penalty: number;
  final_confidence: number;
}

export interface DiscoveryCandidate {
  id: number;
  name: string;
  country: string;
  ai_category: string | null;
  segment_tags: string[];
  use_cases: string[];
  website: string | null;
  evidence: EvidenceItem[];
  confidence_score: number;
  confidence_explanation: ConfidenceExplanation;
  validation_result: {
    is_valid: boolean;
    reasons: string[];
  };
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

export interface DiscoveryRequest {
  sector: string;
  country: string;
}

export interface DiscoveryStatistics {
  discovery_runs: number;
  pending_candidates: number;
  approved_candidates: number;
  rejected_candidates: number;
  average_confidence: number;
  average_runtime_ms: number;
  duplicate_percentage: number;
  website_verification_success_rate: number;
  average_evidence_count: number;
  average_verification_time_ms: number;
  average_extraction_time_ms: number;
}
