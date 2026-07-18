import os
import sys
import time
import argparse
import logging
from logging.handlers import RotatingFileHandler

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from services.knowledge_base.indexer import KnowledgeBaseIndexer
from models.company import Company
from models.problem import Problem
from models.sector import Sector
from models.kb_chunk import KBChunk

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")

def setup_logging():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
        
    log_file = os.path.join(LOGS_DIR, "indexing.log")
    
    logger = logging.getLogger("indexing")
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
        console_handler = logging.StreamHandler()
        
        file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

def parse_args():
    parser = argparse.ArgumentParser(description="Build AI Atlas Knowledge Base Index")
    parser.add_argument("--all", action="store_true", help="Index all entities.")
    parser.add_argument("--companies", action="store_true", help="Index companies.")
    parser.add_argument("--problems", action="store_true", help="Index problems.")
    parser.add_argument("--sectors", action="store_true", help="Index sectors.")
    parser.add_argument("--verify", action="store_true", help="Verify SQLite records against KBChunk and ChromaDB.")
    parser.add_argument("--dry-run", action="store_true", help="Generate documents without writing to ChromaDB or SQLite.")
    parser.add_argument("--reset", action="store_true", help="Reset existing index (not implemented yet, deletes chroma_db).")
    return parser.parse_args()

def run_verification(db):
    logger = logging.getLogger("indexing")
    logger.info("--- Running Verification ---")
    
    comp_count = db.query(Company).filter(Company.is_deleted == False).count()
    prob_count = db.query(Problem).filter(Problem.is_deleted == False).count()
    sec_count = db.query(Sector).filter(Sector.is_deleted == False).count()
    total_expected = comp_count + prob_count + sec_count
    
    kb_count = db.query(KBChunk).filter(KBChunk.is_deleted == False).count()
    
    logger.info(f"SQLite Records: {total_expected} ({comp_count} Companies, {prob_count} Problems, {sec_count} Sectors)")
    logger.info(f"KBChunk Records: {kb_count}")
    
    if total_expected != kb_count:
        logger.warning("Inconsistency: SQLite row count does not match KBChunk count.")
    else:
        logger.info("Consistency Check Passed: SQLite and KBChunk match.")
        
    # Checking ChromaDB
    from services.knowledge_base.vector_store import vector_store
    try:
        chroma_count = vector_store.collection.count()
        logger.info(f"ChromaDB Records: {chroma_count}")
        if chroma_count != kb_count:
            logger.warning("Inconsistency: ChromaDB count does not match KBChunk count.")
        else:
            logger.info("Consistency Check Passed: ChromaDB and KBChunk match.")
    except Exception as e:
        logger.error(f"Could not query ChromaDB count: {e}")

def main():
    args = parse_args()
    logger = setup_logging()
    
    if not any([args.all, args.companies, args.problems, args.sectors, args.verify, args.reset]):
        logger.error("Must specify at least one action: --all, --companies, --problems, --sectors, --verify, or --reset")
        sys.exit(1)
        
    if args.dry_run:
        logger.info("DRY RUN MODE: No changes will be written.")

    db = SessionLocal()
    indexer = KnowledgeBaseIndexer(db)

    try:
        start_time = time.time()
        
        # We wrap in a transaction for SQLite part, but ChromaDB operations are immediate.
        # So rollback only affects KBChunk. 
        if args.all or args.sectors:
            logger.info("Indexing Sectors...")
            if not args.dry_run:
                indexed, skipped = indexer.index_sectors()
                logger.info(f"Sectors: {indexed} indexed, {skipped} skipped.")
            
        if args.all or args.companies:
            logger.info("Indexing Companies...")
            if not args.dry_run:
                indexed, skipped = indexer.index_companies()
                logger.info(f"Companies: {indexed} indexed, {skipped} skipped.")
                
        if args.all or args.problems:
            logger.info("Indexing Problems...")
            if not args.dry_run:
                indexed, skipped = indexer.index_problems()
                logger.info(f"Problems: {indexed} indexed, {skipped} skipped.")
                
        if args.verify:
            run_verification(db)
            
        logger.info(f"Indexing process finished in {time.time() - start_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Fatal error during indexing: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
