import logging
from typing import List
from services.ask_ai.llm.base import LLMClient

logger = logging.getLogger(__name__)

class FailoverClient(LLMClient):
    """
    Tries multiple LLM clients in order.
    Useful for falling back from a local instance (e.g. Ollama) to a cloud instance (e.g. Groq/Gemini).
    """
    
    def __init__(self, providers: List[str]):
        """
        providers: List of strings (e.g., ["ollama", "groq", "gemini"])
        """
        self.providers = providers
        # We lazily instantiate the clients to avoid failing at factory init if one is missing an API key.
        
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        from services.ask_ai.llm.factory import LLMFactory
        
        last_exception = None
        
        for provider_name in self.providers:
            try:
                logger.info(f"Attempting to generate response with provider: {provider_name}")
                client = LLMFactory.get_client(provider_name)
                response = client.generate_response(system_prompt, user_prompt)
                logger.info(f"Successfully generated response with provider: {provider_name}")
                return response
            except Exception as e:
                logger.warning(f"Provider '{provider_name}' failed with error: {e}")
                last_exception = e
                continue
                
        # If all failed, raise the last exception
        if last_exception:
            raise RuntimeError(f"All failover providers failed. Last error: {last_exception}")
        else:
            raise ValueError("No providers were configured for failover.")
