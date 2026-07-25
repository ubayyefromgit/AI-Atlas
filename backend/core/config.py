from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Atlas"
    API_V1_STR: str = "/api/v1"
    
    # Environment variables are loaded automatically by pydantic_settings
    DATABASE_URL: str = "sqlite:///./database/ai_atlas.db"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    MAX_CONTEXT_DOCUMENTS: int = 8
    MAX_CONTEXT_TOKENS: int = 30000
    MIN_RETRIEVAL_SCORE: float = 0.15
    REQUEST_TIMEOUT: int = 30
    
    NEWS_API_KEY: str = ""
    NEWS_PROVIDER: str = "gnews"
    NEWS_REFRESH_DAYS: int = 7
    NEWS_MAX_RESULTS: int = 10
    NEWS_TIMEOUT: int = 15
    NEWS_RELEVANCE_THRESHOLD: float = 0.5
    
    TAVILY_API_KEY: str = ""
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    ADMIN_PASSWORD: str = ""
    ADMIN_TOKEN: str = "admin1234"
    
    DISCOVERY_PROVIDER: str = "tavily"
    DISCOVERY_MAX_RESULTS: int = 20
    DISCOVERY_TIMEOUT: int = 15
    DISCOVERY_MIN_CONFIDENCE: float = 0.5
    
    # Agent Enhancements Configuration
    AGENT_ENABLED: bool = True
    GENERAL_KNOWLEDGE_ENABLED: bool = True
    AUTO_DISCOVERY_ENABLED: bool = True
    AUTO_DISCOVERY_THRESHOLD: float = 0.90
    NEWS_MONITOR_ENABLED: bool = True
    
    class Config:
        import os
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
        extra = "ignore"

settings = Settings()

if __name__ == "__main__":
    print(f"Loaded Gemini Model: {settings.GEMINI_MODEL}")
    print(f"Gemini Key Found: {bool(settings.GEMINI_API_KEY)} (Should be True)")
    print(f"Groq Key Found: {bool(settings.GROQ_API_KEY)} (Should be True)")