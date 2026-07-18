import logging
import httpx
from typing import Any, Optional
from services.ask_ai.llm.base import LLMClient
from core.config import settings

logger = logging.getLogger(__name__)

class OllamaClient(LLMClient):
    """
    Ollama implementation of the LLM Client for local inference.
    """
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        self.model_name = settings.OLLAMA_MODEL
        
    def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.0,
        response_schema: Optional[Any] = None,
        max_retries: int = 3
    ) -> str:
        
        logger.info(f"Calling Ollama API using model: {self.model_name}")
        
        # Combine system and user prompt for standard /api/generate
        # Alternatively, we could use /api/chat, but generate is simpler.
        prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        import time
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(f"{self.base_url}/api/generate", json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return data.get("response", "")
                    
            except httpx.RequestError as e:
                error_msg = f"Network error connecting to Ollama: {str(e)}"
                logger.error(error_msg)
                if attempt == max_retries - 1:
                    raise Exception(f"LLM API failure: {error_msg}")
                time.sleep(2 ** attempt)
            except httpx.HTTPStatusError as e:
                error_msg = f"Ollama HTTP error {e.response.status_code}: {e.response.text}"
                logger.error(error_msg)
                if attempt == max_retries - 1:
                    raise Exception(f"LLM API failure: {error_msg}")
                time.sleep(2 ** attempt)
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Ollama API Error: {error_msg}")
                raise Exception(f"LLM API failure: {error_msg}")
