import os
import sys
sys.path.append('C:\\Users\\BISON TECH\\Desktop\\AIML\\Proj\\AI-Atlas\\backend')

from core.database import SessionLocal
from models.kb_chunk import KBChunk
from services.knowledge_base.vector_store import vector_store

db = SessionLocal()
kb_chunks = db.query(KBChunk).all()
kb_ids = {chunk.chunk_key for chunk in kb_chunks}

chroma_data = vector_store.collection.get(include=[])
chroma_ids = set(chroma_data['ids'])

diff = chroma_ids - kb_ids
print(f'IDs in ChromaDB but not in KBChunk: {diff}')
