import sys
sys.path.append('c:/Users/BISON TECH/Desktop/AIML/Proj/AI-Atlas/backend')
from core.database import SessionLocal
from models.company import Company
from services.news.news_pipeline import NewsPipeline

def bulk_fetch():
    db = SessionLocal()
    try:
        companies = db.query(Company).filter(Company.is_deleted == False).all()
        print(f"Starting bulk news fetch for {len(companies)} companies...")

        for idx, c in enumerate(companies):
            print(f"[{idx+1}/{len(companies)}] Fetching for {c.name}...")
            try:
                stats = NewsPipeline.process_company(db, c)
                print(f"  -> Found {stats['relevant']} relevant, stored {stats['stored']}")
            except Exception as e:
                print(f"  -> Error: {e}")
                
        print("Done!")
    except Exception as e:
        print(f"Fatal Error in bulk fetch: {e}")
        from models.notification import Notification, NotificationType
        notif = Notification(
            message=f"News pipeline failed to execute: {str(e)[:200]}",
            type=NotificationType.SYSTEM
        )
        db.add(notif)
        db.commit()

if __name__ == "__main__":
    bulk_fetch()
