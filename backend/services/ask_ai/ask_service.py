import hashlib
import logging
import time
from typing import Dict, Any

from services.knowledge_base.kb_service import KnowledgeBaseService
from services.ask_ai.query_analyzer import QueryAnalyzer
from services.ask_ai.context_manager import ContextManager
from services.ask_ai.prompt_builder import PromptBuilder
from services.ask_ai.llm.factory import LLMFactory
from services.ask_ai.response_formatter import ResponseFormatter

# Dedicated secure logger
secure_logger = logging.getLogger("ask_ai")
secure_logger.setLevel(logging.INFO)
# In a real app, we'd add a FileHandler pointing to logs/ask_ai.log

class AskService:
    """
    Orchestrates the entire Ask AI Grounded RAG Pipeline.
    """
    def __init__(self, kb_service: KnowledgeBaseService, db):
        self.kb_service = kb_service
        self.db = db
        self.query_analyzer = QueryAnalyzer()
        self.context_manager = ContextManager()
        self.prompt_builder = PromptBuilder()
        self.response_formatter = ResponseFormatter()
        
    def _hash_question(self, question: str) -> str:
        return hashlib.sha256(question.encode('utf-8')).hexdigest()[:16]

    def ask(self, question: str, model_provider: str = "gemini") -> Dict[str, Any]:
        start_time = time.time()
        q_hash = self._hash_question(question)
        secure_logger.info(f"Ask Request started | hash: {q_hash} | model: {model_provider}")
        
        try:
            llm_client = LLMFactory.get_client(model_provider)
        except Exception as e:
            secure_logger.error(f"Ask Request failed | hash: {q_hash} | error: {str(e)}")
            return {
                "answer": f"Error initializing LLM client: {str(e)}",
                "sources": []
            }
        
        try:
            # 1. Analyze query
            analysis = self.query_analyzer.analyze(question)
            
            # 2. Retrieve from KB
            retrieved_results = self.kb_service.search(
                db=self.db,
                query=analysis["optimized_query"],
                limit=20 # Fetch plenty, ContextManager will pare down
            )
            
            secure_logger.info(f"Retrieved {len(retrieved_results)} results from kb_service")
            for i, r in enumerate(retrieved_results[:3]):
                secure_logger.info(f"Top {i} score: {r.score} key: {r.chunk_key}")
            
            # 3. Manage Context
            context_string, sources = self.context_manager.prepare_context(retrieved_results)
            secure_logger.info(f"Context string length: {len(context_string)}")
            
            # Refusal Behavior: If no context met the threshold, abort immediately.
            if not context_string:
                secure_logger.info(f"Ask Request refused (low confidence) | hash: {q_hash} | count: 0")
                return {
                    "answer": self.prompt_builder.get_refusal_prompt(),
                    "sources": []
                }
                
            # 4. Build Prompts
            system_prompt = self.prompt_builder.build_system_prompt(context_string)
            user_prompt = self.prompt_builder.build_user_prompt(question)
            
            # 5. Call LLM
            llm_start = time.time()
            raw_response = llm_client.generate_response(system_prompt, user_prompt)
            llm_duration = time.time() - llm_start
            
            # 6. Format and Validate
            final_response = self.response_formatter.format_response(raw_response, sources)
            
            # 7. Secure Logging
            total_duration = time.time() - start_time
            secure_logger.info(
                f"Ask Request success | hash: {q_hash} | "
                f"docs_used: {len(sources)} | llm_time: {llm_duration:.2f}s | "
                f"total_time: {total_duration:.2f}s | status: OK"
            )
            
            return final_response
            
        except Exception as e:
            secure_logger.error(f"Ask Request failed | hash: {q_hash} | error: {str(e)}")
            return {
                "answer": f"Error: The selected AI provider ({model_provider}) encountered an issue: {str(e)}. Please try selecting a different provider.",
                "sources": []
            }
