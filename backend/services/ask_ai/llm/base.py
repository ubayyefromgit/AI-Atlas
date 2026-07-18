from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMClient(ABC):
    """
    Abstract base class for all LLM providers.
    """
    
    @abstractmethod
    def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.0,
        response_schema: Optional[Any] = None
    ) -> str:
        """
        Generate a response given a system and user prompt.
        
        Args:
            system_prompt (str): The grounding instructions.
            user_prompt (str): The context and question.
            temperature (float): Generation temperature.
            
        Returns:
            str: The LLM's text response.
            
        Raises:
            Exception: If API fails or times out.
        """
        pass
