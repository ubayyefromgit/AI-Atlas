import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import logging

from core.config import settings
from models.discovery import DiscoveryCandidate, DiscoveryRunLog, DiscoveryStatus
from services.discovery.evidence_collector import EvidenceCollector
from services.discovery.extractor import Extractor
from services.discovery.validator import Validator
from services.discovery.confidence import ConfidenceScorer
from services.discovery.deduplicator import Deduplicator

logger = logging.getLogger(__name__)

class DiscoveryPipeline:
    def __init__(self):
        self.collector = EvidenceCollector()
        self.extractor = Extractor()
        self.validator = Validator(timeout=settings.DISCOVERY_TIMEOUT)
        self.scorer = ConfidenceScorer()
        self.deduplicator = Deduplicator()
        
    def run(self, db: Session, sector: str, country: str):
        start_time = time.time()
        start_dt = datetime.now(timezone.utc)
        
        run_log = DiscoveryRunLog(
            sector=sector,
            country=country,
            provider=settings.DISCOVERY_PROVIDER,
            started_at=start_dt,
            status="running"
        )
        db.add(run_log)
        db.commit()
        
        try:
            # 1. Collect
            evidence_items = self.collector.collect(sector, country, max_results_per_query=settings.DISCOVERY_MAX_RESULTS)
            
            # 2. Extract
            extracted_companies = self.extractor.extract(sector, country, evidence_items)
            
            candidates_retrieved = 0
            
            # 3. Process each candidate
            for c_dict in extracted_companies:
                # 4. Validate
                is_valid, reasons, website_verified = self.validator.validate(c_dict)
                
                # 5. Score
                final_confidence, explanation = self.scorer.score(c_dict, website_verified)
                
                # 6. Deduplicate
                is_duplicate = self.deduplicator.check_duplicate(db, c_dict.get("name", ""), c_dict.get("website", ""))
                if is_duplicate:
                    is_valid = False
                    reasons.append("Duplicate company found in system")
                    explanation.duplicate_penalty = 1.0
                    final_confidence = 0.0
                    explanation.final_confidence = 0.0
                
                # Check confidence threshold
                if final_confidence < settings.DISCOVERY_MIN_CONFIDENCE and is_valid:
                    is_valid = False
                    reasons.append(f"Confidence score {final_confidence:.2f} is below threshold {settings.DISCOVERY_MIN_CONFIDENCE}")

                if not is_valid:
                    run_log.candidates_rejected += 1
                    continue
                    
                # 7. Persist Valid Candidate
                evidence_json = []
                # Map extracted URLs to their evidence objects
                for url in c_dict.get("evidence_urls", []):
                    for ev in evidence_items:
                        if url in ev.url:
                            evidence_json.append(ev.dict())
                            break
                            
                candidate = DiscoveryCandidate(
                    name=c_dict.get("name", ""),
                    country=c_dict.get("country"),
                    ai_category=c_dict.get("ai_category"),
                    segment_tags=c_dict.get("segment_tags", []),
                    use_cases=c_dict.get("use_cases", []),
                    website=c_dict.get("website"),
                    evidence=evidence_json,
                    confidence_score=final_confidence,
                    confidence_explanation=explanation.dict(),
                    validation_result={"is_valid": is_valid, "reasons": reasons},
                    status=DiscoveryStatus.PENDING
                )
                db.add(candidate)
                candidates_retrieved += 1
                
            db.commit()
            
            run_log.candidates_retrieved = candidates_retrieved
            run_log.status = "success"
            
        except Exception as e:
            logger.error(f"Discovery Pipeline failed: {e}", exc_info=True)
            run_log.status = "failed"
            run_log.error_message = str(e)
        finally:
            run_log.completed_at = datetime.now(timezone.utc)
            run_log.duration_ms = int((time.time() - start_time) * 1000)
            db.commit()

        return run_log
