import logging
from typing import List

# We delay import of sentence_transformers until needed to speed up fast API startups
logger = logging.getLogger("ingestion")

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            logger.info("Loading sentence-transformers all-MiniLM-L6-v2 model into memory...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully.")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        # Ensure it returns a list of float lists (ChromaDB requirement)
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
        
    def get_embedding(self, text: str) -> List[float]:
        return self.get_embeddings([text])[0]

    @property
    def dimension(self) -> int:
        return 384 # Known dimension for all-MiniLM-L6-v2

# Singleton instance
embedding_service = EmbeddingService()
