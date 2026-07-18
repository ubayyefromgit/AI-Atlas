import time
import logging
from sqlalchemy.orm import Session

from models.news import NewsArticle
from models.company import Company
from models.kb_chunk import KBChunk
from models.enums import SourceType

from services.knowledge_base.document_builder import DocumentBuilder
from services.knowledge_base.embeddings import embedding_service
from services.knowledge_base.kb_service import kb_service
from services.news.news_document_builder import NewsDocumentBuilder

logger = logging.getLogger(__name__)

class NewsIndexer:
    """
    Responsible only for indexing news into the Knowledge Base.
    """
    
    @staticmethod
    def index_article(db: Session, article: NewsArticle, company: Company) -> bool:
        """
        Generates embedding and upserts chunk to KB.
        Returns True if newly indexed, False if skipped.
        """
        doc_str = NewsDocumentBuilder.build_news_doc(article, company)
        chunk_key = f"news_{article.id}"
        
        doc_hash = DocumentBuilder.hash_document(doc_str)
        
        # Check if hash changed
        existing = db.query(KBChunk).filter(KBChunk.chunk_key == chunk_key).first()
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
            "source_type": SourceType.NEWS.value,
            "source_id": str(article.id),
            "chunk_key": chunk_key,
            "title": article.headline,
            "company_id": company.id
        }
        
        kb_service.upsert_chunk(
            db=db,
            source_type=SourceType.NEWS,
            source_id=str(article.id),
            chunk_key=chunk_key,
            content=doc_str,
            document_hash=doc_hash,
            embedding=embedding,
            metadata_json=metadata
        )
        
        return True
