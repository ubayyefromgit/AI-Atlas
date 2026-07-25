import logging
from sqlalchemy.orm import Session
from core.config import settings
from core.database import SessionLocal

from services.discovery.discovery_pipeline import DiscoveryPipeline
from services.discovery.approval_service import ApprovalService
from services.news.news_pipeline import NewsPipeline
from services.news.news_indexer import NewsIndexer
from models.enums import DiscoveryStatus

logger = logging.getLogger("agent.jobs")


def run_agent_discovery_job(db: Session = None):
    """
    PART 3: Scheduled Agent Discovery Job.
    Flow:
    Run Discovery -> Collect Evidence -> Calculate Confidence ->
    If confidence >= AUTO_DISCOVERY_THRESHOLD (0.90) -> Automatically create company & index -> Skip manual approval.
    Otherwise -> Store as PENDING_REVIEW.
    """
    if not settings.AUTO_DISCOVERY_ENABLED:
        logger.info("Agent Auto Discovery Job is disabled via config.")
        return

    logger.info("Starting Agent Auto-Discovery Job...")
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        pipeline = DiscoveryPipeline(db)
        # Execute discovery pipeline for configured sectors / search queries
        run_log = pipeline.execute_pipeline(sector_name="Artificial Intelligence")
        
        # Check newly extracted candidates
        approval_service = ApprovalService(db)
        pending_candidates = approval_service.get_pending_candidates()
        
        auto_approved_count = 0
        threshold = settings.AUTO_DISCOVERY_THRESHOLD
        
        for candidate in pending_candidates:
            if candidate.confidence_score and candidate.confidence_score >= threshold:
                logger.info(
                    f"Auto-approving candidate '{candidate.company_name}' "
                    f"(confidence: {candidate.confidence_score:.2f} >= threshold: {threshold:.2f})"
                )
                try:
                    # Automatically approve & index into Knowledge Base
                    approval_service.approve_candidate(
                        candidate_id=candidate.id,
                        admin_user="agent_auto_discovery"
                    )
                    auto_approved_count += 1
                except Exception as app_err:
                    logger.error(f"Error auto-approving candidate {candidate.id}: {app_err}")
            else:
                logger.info(
                    f"Candidate '{candidate.company_name}' confidence ({candidate.confidence_score}) "
                    f"is below threshold ({threshold}). Retaining in PENDING_REVIEW."
                )

        logger.info(
            f"Agent Auto-Discovery Job complete. Total candidates processed: {len(pending_candidates)}, "
            f"Auto-approved & indexed: {auto_approved_count}."
        )
    except Exception as e:
        logger.error(f"Error executing Agent Auto-Discovery Job: {e}", exc_info=True)
    finally:
        if close_db:
            db.close()


def run_agent_news_monitor_job(db: Session = None):
    """
    PART 4: Agent News Monitor Job.
    Flow:
    Scheduler -> Fetch News -> Map to Company -> Store -> Index into Knowledge Base -> Available through Ask AI.
    """
    if not settings.NEWS_MONITOR_ENABLED:
        logger.info("Agent News Monitor Job is disabled via config.")
        return

    logger.info("Starting Agent News Monitor Job...")
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        news_pipeline = NewsPipeline(db)
        news_indexer = NewsIndexer()
        
        # Execute news pipeline (fetches, deduplicates, maps to companies, saves to DB)
        summary = news_pipeline.run_pipeline()
        logger.info(f"News Pipeline executed: {summary}")
        
        # Index new articles into Knowledge Base so they are searchable in Ask AI
        indexed_count = news_indexer.index_articles(db=db)
        logger.info(f"Agent News Monitor indexed {indexed_count} new articles into Knowledge Base.")
        
    except Exception as e:
        logger.error(f"Error executing Agent News Monitor Job: {e}", exc_info=True)
    finally:
        if close_db:
            db.close()
