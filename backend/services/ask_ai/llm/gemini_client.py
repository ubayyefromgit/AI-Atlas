import logging
from typing import Any, Optional
from google import genai
from google.genai import types
from services.ask_ai.llm.base import LLMClient
from core.config import settings

logger = logging.getLogger(__name__)

class GeminiClient(LLMClient):
    """
    Google Gemini implementation of the LLM Client using the modern google.genai SDK.
    """
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")
            
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        
        # Configure safety settings to be permissive for business context
        # to avoid false positive blocks on standard industry text.
        self.safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ]

    def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.0,
        response_schema: Optional[Any] = None,
        max_retries: int = 3
    ) -> str:
        
        logger.info(f"Calling Gemini API using model: {self.model_name}")
        
        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_prompt,
            safety_settings=self.safety_settings
        )
        
        if response_schema:
            config.response_mime_type = "application/json"
            config.response_schema = response_schema
            
        import time
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=config
                )
                
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                # Check for rate limits (429) or service unavailable (503)
                if "503" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s...
                        logger.warning(f"Gemini API Error ({error_msg}). Retrying in {sleep_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(sleep_time)
                        continue
                
                logger.error(f"Gemini API Error: {error_msg}")
                raise Exception(f"LLM API failure: {error_msg}")
