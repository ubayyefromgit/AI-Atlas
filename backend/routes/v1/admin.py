from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from core.database import get_db
from core.auth import get_admin_token
from schemas.discovery import DiscoveryRequest, DiscoveryCandidateResponse, DiscoveryStatisticsResponse
from schemas.company import CompanyResponse
from models.discovery import DiscoveryCandidate, DiscoveryRunLog, DiscoveryStatus
from models.company import Company
from services.discovery.discovery_pipeline import DiscoveryPipeline
from services.discovery.approval_service import ApprovalService
from services.admin.eval_service import EvalService

router = APIRouter(dependencies=[Depends(get_admin_token)])

@router.post("/discover")
def trigger_discovery(request: DiscoveryRequest, db: Session = Depends(get_db)):
    pipeline = DiscoveryPipeline()
    run_log = pipeline.run(db, request.sector, request.country)
    
    if run_log.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Discovery Pipeline failed: {run_log.error_message}"
        )
        
    if run_log.candidates_retrieved == 0:
        return {"message": f"Pipeline finished successfully, but no valid candidates were found for {request.sector} in {request.country}."}
        
    return {"message": f"Pipeline finished successfully! Discovered {run_log.candidates_retrieved} new candidates."}

@router.get("/discovery", response_model=List[DiscoveryCandidateResponse])
def list_candidates(db: Session = Depends(get_db)):
    candidates = db.query(DiscoveryCandidate).all()
    return candidates

@router.get("/discovery/{candidate_id}", response_model=DiscoveryCandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(DiscoveryCandidate).filter(DiscoveryCandidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.put("/discovery/{candidate_id}", response_model=DiscoveryCandidateResponse)
def update_candidate(candidate_id: int, data: dict, db: Session = Depends(get_db)):
    candidate = db.query(DiscoveryCandidate).filter(DiscoveryCandidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if "name" in data:
        candidate.name = data["name"]
    if "website" in data:
        candidate.website = data["website"]
    if "ai_category" in data:
        candidate.ai_category = data["ai_category"]
    if "country" in data:
        candidate.country = data["country"]
        
    db.commit()
    db.refresh(candidate)
    return candidate

@router.post("/discovery/{candidate_id}/approve")
def approve_candidate(candidate_id: int, db: Session = Depends(get_db)):
    approval_service = ApprovalService()
    success = approval_service.approve_candidate(db, candidate_id)
    if not success:
        raise HTTPException(status_code=400, detail="Approval failed. Candidate might not be in PENDING state or does not exist.")
    return {"message": "Candidate approved and company created"}

@router.post("/discovery/{candidate_id}/reject")
def reject_candidate(candidate_id: int, db: Session = Depends(get_db)):
    approval_service = ApprovalService()
    success = approval_service.reject_candidate(db, candidate_id)
    if not success:
        raise HTTPException(status_code=400, detail="Rejection failed.")
    return {"message": "Candidate rejected"}

@router.get("/statistics", response_model=DiscoveryStatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    runs = db.query(DiscoveryRunLog).count()
    pending = db.query(DiscoveryCandidate).filter(DiscoveryCandidate.status == DiscoveryStatus.PENDING).count()
    approved = db.query(DiscoveryCandidate).filter(DiscoveryCandidate.status == DiscoveryStatus.APPROVED).count()
    rejected = db.query(DiscoveryCandidate).filter(DiscoveryCandidate.status == DiscoveryStatus.REJECTED).count()
    
    avg_conf = db.query(func.avg(DiscoveryCandidate.confidence_score)).scalar() or 0.0
    avg_runtime = db.query(func.avg(DiscoveryRunLog.duration_ms)).scalar() or 0.0
    
    # Calculate duplicates and verification success loosely
    # This assumes duplicate penalty is 1.0 and website verified is true
    # For a real implementation, you'd track these properly in DiscoveryRunLog
    
    total_candidates = pending + approved + rejected
    
    duplicate_count = db.query(func.count(DiscoveryCandidate.id)).filter(
        func.json_extract(DiscoveryCandidate.confidence_explanation, '$.duplicate_penalty') == 1.0
    ).scalar() or 0
    
    verification_success = db.query(func.count(DiscoveryCandidate.id)).filter(
        func.json_extract(DiscoveryCandidate.confidence_explanation, '$.website_verified') == 1
    ).scalar() or 0
    
    total_evidence = db.query(func.sum(func.json_array_length(DiscoveryCandidate.evidence))).scalar() or 0
            
    dup_percent = (duplicate_count / total_candidates * 100) if total_candidates > 0 else 0.0
    verification_percent = (verification_success / total_candidates * 100) if total_candidates > 0 else 0.0
    avg_evidence = total_evidence / total_candidates if total_candidates > 0 else 0.0
    
    return DiscoveryStatisticsResponse(
        discovery_runs=runs,
        pending_candidates=pending,
        approved_candidates=approved,
        rejected_candidates=rejected,
        average_confidence=float(avg_conf),
        average_runtime_ms=float(avg_runtime),
        duplicate_percentage=dup_percent,
        website_verification_success_rate=verification_percent,
        average_evidence_count=avg_evidence,
        average_verification_time_ms=100.0, # Mock placeholder for now
        average_extraction_time_ms=1000.0 # Mock placeholder for now
    )

@router.get("/eval")
def run_evaluation(db: Session = Depends(get_db)):
    results = EvalService.run_evaluation(db)
    return results
