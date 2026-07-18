from typing import Dict, Any, Tuple
from schemas.discovery import ConfidenceExplanation

class ConfidenceScorer:
    def score(self, candidate: Dict[str, Any], website_verified: bool) -> Tuple[float, ConfidenceExplanation]:
        evidence_urls = candidate.get("evidence_urls", [])
        evidence_count = len(evidence_urls)
        
        # Calculate completeness (out of 6 core fields)
        core_fields = ["name", "country", "ai_category", "segment_tags", "use_cases", "website"]
        filled_fields = sum(1 for f in core_fields if candidate.get(f))
        field_completeness = filled_fields / len(core_fields)
        
        duplicate_penalty = 0.0 # Handled in deduplicator, but initialized here
        
        # Base weights
        # Evidence: up to 0.4 (maxed at 4 items)
        evidence_score = min(evidence_count * 0.1, 0.4)
        
        # Verification: 0.4
        verification_score = 0.4 if website_verified else 0.0
        
        # Completeness: 0.2
        completeness_score = field_completeness * 0.2
        
        final_confidence = evidence_score + verification_score + completeness_score
        
        explanation = ConfidenceExplanation(
            website_verified=website_verified,
            evidence_count=evidence_count,
            field_completeness=field_completeness,
            duplicate_penalty=duplicate_penalty,
            final_confidence=final_confidence
        )
        
        return final_confidence, explanation
