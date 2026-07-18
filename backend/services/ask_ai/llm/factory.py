from services.ask_ai.llm.base import LLMClient
from services.ask_ai.llm.gemini_client import GeminiClient

class LLMFactory:
    """
    Factory to instantiate the configured LLM client.
    """
    
    @staticmethod
    def get_client(provider: str = "gemini") -> LLMClient:
        provider = provider.lower()
        if provider == "gemini":
            return GeminiClient()
        elif provider == "groq":
            from services.ask_ai.llm.groq_client import GroqClient
            return GroqClient()
        elif provider == "ollama":
            from services.ask_ai.llm.ollama_client import OllamaClient
            return OllamaClient()
        elif provider == "failover":
            from services.ask_ai.llm.failover_client import FailoverClient
            from core.config import settings
            # We use getattr in case LLM_FALLBACK_ORDER is not yet defined
            fallback_order = getattr(settings, "LLM_FALLBACK_ORDER", ["ollama", "groq", "gemini"])
            return FailoverClient(providers=fallback_order)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
