from pydantic import BaseModel, Field
from typing import List, Optional
from schemas.ask import AskSource

class AgentAskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="The natural language query to ask the AI Agent.")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to maintain lightweight multi-turn memory context.")
    model_provider: str = Field("gemini", description="The LLM model provider to use (gemini, groq, ollama)")

class AgentAskResponse(BaseModel):
    answer: str
    sources: List[AskSource] = []
    conversation_id: str
    used_tools: List[str] = []
    is_general_knowledge: bool = False
