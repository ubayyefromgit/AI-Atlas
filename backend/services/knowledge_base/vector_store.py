import os
import chromadb
from typing import List, Dict, Any, Optional

CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_db")

class VectorStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance
        
    def _init_client(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="ai_atlas",
            metadata={"hnsw:space": "cosine"}
        )

    def upsert(
        self, 
        id: str, 
        embedding: List[float], 
        document: str, 
        metadata: Dict[str, Any]
    ):
        self.collection.upsert(
            ids=[id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata]
        )

    def delete(self, id: str):
        self.collection.delete(ids=[id])
        
    def search(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where,
            include=['documents', 'metadatas', 'distances']
        )
        
        parsed_results = []
        if results['ids'] and len(results['ids']) > 0:
            for idx, doc_id in enumerate(results['ids'][0]):
                # ChromaDB cosine distance: 0 is identical, higher is further
                distance = results['distances'][0][idx] if results['distances'] else 0.0
                score = 1.0 - distance # rough conversion to similarity score 0-1
                
                parsed_results.append({
                    "id": doc_id,
                    "document": results['documents'][0][idx] if results['documents'] else "",
                    "metadata": results['metadatas'][0][idx] if results['metadatas'] else {},
                    "score": score
                })
                
        return parsed_results

# Singleton
vector_store = VectorStore()
