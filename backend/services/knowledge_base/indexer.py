import time
import logging
from sqlalchemy.orm import Session
from typing import List, Tuple

from models.company import Company
from models.problem import Problem
from models.sector import Sector
from models.kb_chunk import KBChunk
from models.enums import SourceType

from services.knowledge_base.document_builder import DocumentBuilder
from services.knowledge_base.embeddings import embedding_service
from services.knowledge_base.kb_service import kb_service

logger = logging.getLogger("indexing")

class KnowledgeBaseIndexer:
    def __init__(self, db: Session):
        self.db = db

    def _process_entity(self, source_type: SourceType, source_id: str, chunk_key: str, title: str, doc_str: str) -> bool:
        """Returns True if newly indexed, False if skipped (hash matched)"""
        doc_hash = DocumentBuilder.hash_document(doc_str)
        
        # Check for existing hash
        existing = self.db.query(KBChunk).filter(KBChunk.chunk_key == chunk_key).first()
        if existing and existing.document_hash == doc_hash and not existing.is_deleted:
            logger.debug(f"Skipping {chunk_key}: Hash unchanged.")
            return False
            
        # Generate Embedding
        start_t = time.time()
        embedding = embedding_service.get_embedding(doc_str)
        emb_time = time.time() - start_t
        logger.debug(f"Generated embedding for {chunk_key} in {emb_time:.3f}s")
        
        # Metadata
        metadata = {
            "source_type": source_type.value,
            "source_id": source_id,
            "chunk_key": chunk_key,
            "title": title
        }
        
        # Upsert
        kb_service.upsert_chunk(
            db=self.db,
            source_type=source_type,
            source_id=source_id,
            chunk_key=chunk_key,
            content=doc_str,
            document_hash=doc_hash,
            embedding=embedding,
            metadata_json=metadata
        )
        return True

    def index_company(self, c: Company) -> bool:
        """Returns True if newly indexed, False if skipped (hash matched)"""
        doc_dict = {col.name: getattr(c, col.name) for col in c.__table__.columns}
        doc_str = DocumentBuilder.build_company_doc(doc_dict)
        chunk_key = f"company_{c.id}"
        return self._process_entity(SourceType.COMPANY, str(c.id), chunk_key, getattr(c, "name", "Unknown"), doc_str)

    def index_companies(self) -> Tuple[int, int]:
        """Returns (indexed_count, skipped_count)"""
        companies = self.db.query(Company).filter(Company.is_deleted == False).all()
        indexed = 0
        skipped = 0
        for c in companies:
            doc_dict = {col.name: getattr(c, col.name) for col in c.__table__.columns}
            doc_str = DocumentBuilder.build_company_doc(doc_dict)
            chunk_key = f"company_{c.id}"
            if self._process_entity(SourceType.COMPANY, str(c.id), chunk_key, getattr(c, "name", "Unknown"), doc_str):
                indexed += 1
            else:
                skipped += 1
        return indexed, skipped

    def index_problems(self) -> Tuple[int, int]:
        problems = self.db.query(Problem).filter(Problem.is_deleted == False).all()
        indexed = 0
        skipped = 0
        for p in problems:
            doc_dict = {col.name: getattr(p, col.name) for col in p.__table__.columns}
            doc_str = DocumentBuilder.build_problem_doc(doc_dict)
            chunk_key = f"problem_{p.id}"
            if self._process_entity(SourceType.PROBLEM, str(p.id), chunk_key, getattr(p, "category", "Unknown"), doc_str):
                indexed += 1
            else:
                skipped += 1
        return indexed, skipped

    def index_sectors(self) -> Tuple[int, int]:
        sectors = self.db.query(Sector).filter(Sector.is_deleted == False).all()
        indexed = 0
        skipped = 0
        for s in sectors:
            doc_dict = {col.name: getattr(s, col.name) for col in s.__table__.columns}
            doc_str = DocumentBuilder.build_sector_doc(doc_dict)
            chunk_key = f"sector_{s.id}"
            if self._process_entity(SourceType.SECTOR, str(s.id), chunk_key, getattr(s, "name", "Unknown"), doc_str):
                indexed += 1
            else:
                skipped += 1
        return indexed, skipped
