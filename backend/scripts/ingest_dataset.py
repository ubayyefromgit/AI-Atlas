import os
import sys
import time
import argparse
import logging
from logging.handlers import RotatingFileHandler

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine
from models.company import Company
from models.problem import Problem
from models.sector import Sector
from models.mapping import ProblemCompanyMapping

from services.ingestion.loader import CSVLoader
from services.ingestion.importer import DataImporter
from services.ingestion.report import ImportReport
from services.ingestion.manifest import EXPECTED_COUNTS

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "atlas_dataset")
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")

def setup_logging():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
        
    log_file = os.path.join(LOGS_DIR, "ingestion.log")
    
    logger = logging.getLogger("ingestion")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if script is run multiple times in same python process
    if not logger.handlers:
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
        console_handler = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

def parse_args():
    parser = argparse.ArgumentParser(description="Ingest AI Atlas Dataset")
    parser.add_argument("--dry-run", action="store_true", help="Validate data only. Do not write to database.")
    parser.add_argument("--reset", action="store_true", help="Reset existing dataset tables before importing.")
    parser.add_argument("--force", action="store_true", help="Skip confirmation for --reset.")
    return parser.parse_args()

def handle_reset(db, force: bool):
    if not force:
        confirm = input("Are you sure you want to delete all dataset tables (Companies, Problems, Sectors, Mappings)? [y/N]: ")
        if confirm.lower() != 'y':
            print("Reset aborted.")
            sys.exit(0)
            
    print("Resetting dataset tables...")
    try:
        # We only delete rows, not drop tables, to preserve schema.
        # Order matters for foreign keys if we had strict constraints, but we can just delete.
        db.query(ProblemCompanyMapping).delete()
        db.query(Company).delete()
        db.query(Problem).delete()
        db.query(Sector).delete()
        db.commit()
        print("Dataset tables reset successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error resetting tables: {e}")
        sys.exit(1)

def verify_counts(db):
    print("\n--- Verifying Counts ---")
    counts = {
        "companies": db.query(Company).count(),
        "problems": db.query(Problem).count(),
        "sectors": db.query(Sector).count(),
        "mappings": db.query(ProblemCompanyMapping).count()
    }
    
    mismatches = False
    for table, expected in EXPECTED_COUNTS.items():
        actual = counts[table]
        if actual != expected:
            print(f"MISMATCH for {table}: expected {expected}, got {actual}")
            mismatches = True
        else:
            print(f"MATCH for {table}: {actual}")
            
    if mismatches:
        print("WARNING: Final database counts do not match manifest.")
    else:
        print("SUCCESS: All row counts match manifest.")

def main():
    args = parse_args()
    logger = setup_logging()
    
    logger.info("Starting Dataset Ingestion Pipeline")
    if args.dry_run:
        logger.info("Running in DRY-RUN mode.")
        
    db = SessionLocal()
    
    try:
        if args.reset:
            handle_reset(db, args.force)
            
        loader = CSVLoader(data_dir=DATA_DIR)
        
        # 1. Load Data
        df_sectors = loader.load_csv("sectors_reference.csv")
        df_companies = loader.load_csv("companies_germany.csv")
        df_problems = loader.load_csv("problems_germany.csv")
        df_mappings = loader.load_csv("problem_company_mapping.csv")
        
        report = ImportReport()
        importer = DataImporter(db=db, report=report, dry_run=args.dry_run)
        
        start_time = time.time()
        
        # 2. Process Data inside a single transaction
        try:
            logger.info("Importing Sectors...")
            importer.import_sectors(df_sectors)
            
            logger.info("Importing Companies...")
            importer.import_companies(df_companies)
            
            logger.info("Importing Problems...")
            importer.import_problems(df_problems)
            
            logger.info("Importing Mappings...")
            importer.import_mappings(df_mappings)
            
            if not args.dry_run:
                db.commit()
                logger.info("Transaction committed successfully.")
            else:
                db.rollback()
                logger.info("Dry-run complete. Transaction rolled back.")
                
        except Exception as e:
            db.rollback()
            logger.error(f"Fatal error during import transaction. Rolling back. {e}")
            raise
            
        # 3. Finalize Report
        report.duration_seconds = time.time() - start_time
        report.generate_console_summary()
        
        json_path = os.path.join(LOGS_DIR, "import_summary.json")
        report.write_json_summary(json_path)
        
        if not args.dry_run:
            verify_counts(db)
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
