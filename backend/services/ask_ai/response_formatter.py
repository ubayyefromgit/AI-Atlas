from typing import List, Dict, Any
from services.ask_ai.citation_extractor import CitationExtractor

class ResponseFormatter:
    """
    Validates the LLM response and constructs the final structured payload.
    """
    def __init__(self):
        self.extractor = CitationExtractor()
        
    def format_response(self, answer: str, provided_sources: List[Dict]) -> Dict[str, Any]:
        """
        Validates the answer and maps it to the used sources.
        """
        answer = answer.strip()
        
        # 1. Validation: not empty
        if not answer:
            return {
                "answer": "Error: The model returned an empty response.",
                "sources": []
            }
            
        # Refusal check - if it's the exact refusal string, just return it without sources
        if "I don't have that information in my knowledge base" in answer:
             return {
                "answer": "I don't have that information in my knowledge base.",
                "sources": []
            }
            
        # 2. Extract citations used in the text
        used_markers = self.extractor.extract_markers(answer)
        
        # 3. Validation: Citations exist
        if not used_markers:
            return {
                "answer": "Error: The model failed to provide citations to the knowledge base.",
                "sources": []
            }
            
        # 4. Map markers to the actual provided source metadata
        final_sources = []
        valid_provided_markers = {s["marker"] for s in provided_sources}
        
        for marker in used_markers:
            # 5. Validation: every citation must map to a retrieved document
            if marker not in valid_provided_markers:
                return {
                    "answer": f"Error: The model hallucinated a citation ({marker}) that was not in the context.",
                    "sources": []
                }
                
            # Find the source
            source = next(s for s in provided_sources if s["marker"] == marker)
            final_sources.append(source)
            
        return {
            "answer": answer,
            "sources": final_sources
        }
