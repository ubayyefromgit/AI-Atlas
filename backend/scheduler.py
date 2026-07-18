import logging
import time
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from core.database import SessionLocal
from core.config import settings
from models.company import Company
from services.news.news_service import NewsService

logger = logging.getLogger("news_scheduler")

# Global scheduler instance
scheduler = BackgroundScheduler()

def refresh_news_job():
    """
    Daily job to refresh news for companies that need it.
    """
    logger.info("Starting scheduled news refresh job.")
    db = SessionLocal()
    try:
        # Determine threshold for refresh
        threshold_date = datetime.now(timezone.utc) - timedelta(days=settings.NEWS_REFRESH_DAYS)
        
        # Get companies that need refresh (never refreshed, older than threshold, or no news)
        companies_to_refresh = db.query(Company).filter(
            Company.is_deleted == False,
            (Company.news_last_refreshed == None) | 
            (Company.news_last_refreshed < threshold_date) |
            (~Company.news_articles.any())
        ).all()
        
        logger.info(f"Found {len(companies_to_refresh)} companies to refresh.")
        
        for company in companies_to_refresh:
            max_retries = 3
            backoff = 5 # seconds
            
            for attempt in range(max_retries):
                try:
                    stats = NewsService.refresh_company_news(db, company.slug)
                    logger.info(f"Successfully refreshed {company.name}: {stats}")
                    break # Success, move to next company
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {company.name}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(backoff)
                        backoff *= 2
                    else:
                        logger.error(f"All retries failed for {company.name}.")
                        
    except Exception as e:
        logger.error(f"Global error in news refresh job: {e}")
    finally:
        db.close()
        logger.info("Finished scheduled news refresh job.")

def start_scheduler():
    if not scheduler.running:
        # Run daily at 2:00 AM UTC
        scheduler.add_job(
            refresh_news_job,
            CronTrigger(hour=2, minute=0, timezone="UTC"),
            id="daily_news_refresh",
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler started with daily_news_refresh job.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
