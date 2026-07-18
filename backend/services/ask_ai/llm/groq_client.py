import logging
from typing import Any, Optional
from groq import Groq
from services.ask_ai.llm.base import LLMClient
from core.config import settings

logger = logging.getLogger(__name__)

class GroqClient(LLMClient):
    """
    Groq implementation of the LLM Client for ultra-fast inference.
    """
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured.")
            
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model_name = settings.GROQ_MODEL
        
    def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.0,
        response_schema: Optional[Any] = None,
        max_retries: int = 3
    ) -> str:
        
        logger.info(f"Calling Groq API using model: {self.model_name}")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Note: We omit response_schema for groq in this basic implementation
        # as it requires specific format handling depending on the model.
        
        import time
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "503" in error_msg:
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** attempt
                        logger.warning(f"Groq API Error ({error_msg}). Retrying in {sleep_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(sleep_time)
                        continue
                
                logger.error(f"Groq API Error: {error_msg}")
                raise Exception(f"LLM API failure: {error_msg}")
