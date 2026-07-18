from typing import List, Dict, Tuple
from core.config import settings

class ContextManager:
    """
    Manages the retrieved documents to build the final context string for the LLM.
    Ensures the prompt stays within maximum token and document limits.
    """
    
    def __init__(self):
        self.max_docs = settings.MAX_CONTEXT_DOCUMENTS
        self.max_tokens = settings.MAX_CONTEXT_TOKENS
        
    def _estimate_tokens(self, text: str) -> int:
        """
        Simple heuristic: 1 token is roughly 4 characters for English/German.
        """
        return len(text) // 4

    def prepare_context(self, retrieved_results: List) -> Tuple[str, List[Dict]]:
        """
        Takes raw retrieval results, filters them, and prepares the context block.
        
        Args:
            retrieved_results: List of RetrievalResult objects from KnowledgeBaseService.
            
        Returns:
            Tuple of (formatted_context_string, list_of_sources)
        """
        # 1. Deduplicate based on chunk_key
        seen_keys = set()
        deduped = []
        for res in retrieved_results:
            if res.chunk_key not in seen_keys:
                seen_keys.add(res.chunk_key)
                deduped.append(res)
                
        # 2. Sort by score descending (highest quality first)
        sorted_results = sorted(deduped, key=lambda x: x.score, reverse=True)
        
        # 3. Apply Thresholds (Score, Docs, Tokens)
        final_docs = []
        current_tokens = 0
        
        for res in sorted_results:
            if res.score < settings.MIN_RETRIEVAL_SCORE:
                continue
                
            if len(final_docs) >= self.max_docs:
                break
                
            # Estimate tokens for this document
            doc_tokens = self._estimate_tokens(res.content)
            
            if current_tokens + doc_tokens > self.max_tokens:
                # Can't fit this document, skip it or break
                continue
                
            current_tokens += doc_tokens
            final_docs.append(res)
            
        # 4. Format Context Strings and Mapping
        context_blocks = []
        sources = []
        
        for idx, doc in enumerate(final_docs, start=1):
            marker = f"S{idx}"
            
            # Format block
            block = f"[{marker}]\n{doc.content}\n"
            context_blocks.append(block)
            
            # Save mapping — use title from RetrievalResult for human-readable source display
            source_name = getattr(doc, 'title', None) or \
                f"{doc.source_type.value if hasattr(doc.source_type, 'value') else doc.source_type} (ID: {doc.source_id})"
            
            sources.append({
                "marker": marker,
                "source_type": doc.source_type.value if hasattr(doc.source_type, 'value') else str(doc.source_type),
                "source_id": doc.source_id,
                "source_name": source_name,
                "chunk_key": doc.chunk_key,
                "score": doc.score
            })
            
        formatted_context = "\n".join(context_blocks)
        
        return formatted_context, sources
