from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
import logging

from models.discovery import DiscoveryCandidate, DiscoveryStatus
from models.company import Company
from models.enums import CompanyStatus, SourceType
from services.knowledge_base.kb_service import kb_service
from services.knowledge_base.embeddings import embedding_service

logger = logging.getLogger(__name__)

class ApprovalService:
    def approve_candidate(self, db: Session, candidate_id: int) -> bool:
        candidate = db.query(DiscoveryCandidate).filter(DiscoveryCandidate.id == candidate_id).first()
        if not candidate or candidate.status != DiscoveryStatus.PENDING:
            return False
            
        # 1. Create Company
        company = Company(
            slug=self._generate_slug(candidate.name),
            name=candidate.name,
            country=candidate.country,
            ai_category=candidate.ai_category,
            segment_tags=candidate.segment_tags,
            use_cases=candidate.use_cases,
            website=candidate.website,
            source="discovery",
            status=CompanyStatus.APPROVED
        )
        db.add(company)
        db.flush() # Flush to get company.id without committing
        
        # 2. Update Knowledge Base
        kb_text = f"{company.name} is an AI company in {company.country} focused on {company.ai_category}. Use cases: {', '.join(company.use_cases)}. Segment: {', '.join(company.segment_tags)}."
        embedding = embedding_service.get_embedding(kb_text)
        
        metadata = {
            "source_type": "company",
            "source_id": str(company.id),
            "chunk_key": f"company_{company.id}_discovery",
            "title": company.name,
            "company_id": company.id,
            "name": company.name,
            "category": company.ai_category,
            "source": "discovery"
        }
        
        kb_service.upsert_chunk(
            db=db,
            source_type=SourceType.COMPANY,
            source_id=str(company.id),
            chunk_key=f"company_{company.id}_discovery",
            content=kb_text,
            document_hash=str(hash(kb_text)),
            embedding=embedding,
            metadata_json=metadata
        )
        
        # 3. Mark candidate as approved
        candidate.status = DiscoveryStatus.APPROVED
        db.commit()
        db.refresh(company)
        
        return True
        
    def reject_candidate(self, db: Session, candidate_id: int) -> bool:
        candidate = db.query(DiscoveryCandidate).filter(DiscoveryCandidate.id == candidate_id).first()
        if not candidate or candidate.status != DiscoveryStatus.PENDING:
            return False
            
        candidate.status = DiscoveryStatus.REJECTED
        db.commit()
        return True

    def _generate_slug(self, name: str) -> str:
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        return slug.strip('-')
