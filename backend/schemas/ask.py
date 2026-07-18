from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="The natural language question to ask.")
    model_provider: str = Field("gemini", description="The LLM provider to use (gemini, groq, ollama)")

class AskSource(BaseModel):
    marker: str
    source_type: str
    source_id: str
    chunk_key: str
    score: float

class AskResponse(BaseModel):
    answer: str
    sources: List[AskSource]
