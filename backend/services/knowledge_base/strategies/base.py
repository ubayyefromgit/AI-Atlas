from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

class RetrievalResult:
    def __init__(self, chunk_key: str, source_type: str, source_id: str, title: str, content: str, score: float, matched_by: str, last_indexed: Optional[str] = None):
        self.chunk_key = chunk_key
        self.source_type = source_type
        self.source_id = source_id
        self.title = title
        self.content = content
        self.score = score
        self.matched_by = matched_by
        self.last_indexed = last_indexed

class BaseRetrievalStrategy:
    def retrieve(self, db: Session, query: str, limit: int = 10) -> List[RetrievalResult]:
        raise NotImplementedError
