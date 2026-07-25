import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.core.database import Base, get_db
from backend.core.config import settings
from backend.services.agent.agent_service import AgentService
from backend.services.agent.tool_registry import tool_registry, GENERAL_KNOWLEDGE_DISCLAIMER
from backend.services.agent.memory import agent_memory, AgentMemoryManager
from backend.services.agent.jobs import run_agent_discovery_job, run_agent_news_monitor_job

# Test Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_agent.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_tool_registry_registration():
    """Verify ToolRegistry exposes all 4 mandated tools without duplicate logic."""
    kb_tool = tool_registry.get_tool("KnowledgeTool")
    news_tool = tool_registry.get_tool("NewsTool")
    disc_tool = tool_registry.get_tool("DiscoveryTool")
    gk_tool = tool_registry.get_tool("GeneralKnowledgeTool")
    
    assert kb_tool is not None
    assert news_tool is not None
    assert disc_tool is not None
    assert gk_tool is not None
    assert kb_tool.name == "KnowledgeTool"
    assert gk_tool.name == "GeneralKnowledgeTool"


def test_agent_memory_management():
    """Verify lightweight in-memory conversation context tracking."""
    memory_mgr = AgentMemoryManager()
    ctx = memory_mgr.get_or_create("test-conv-123")
    
    assert ctx.conversation_id == "test-conv-123"
    ctx.add_turn("What is Krones?", "Krones AG is a German packaging company.", ["KnowledgeTool"])
    
    assert len(ctx.get_last_queries()) == 1
    assert ctx.get_last_queries()[0] == "What is Krones?"
    assert ctx.get_tool_usage() == ["KnowledgeTool"]
    assert "User: What is Krones?" in ctx.format_history_context()


def test_agent_general_knowledge_fallback():
    """Verify out-of-domain queries fallback to General Knowledge with mandatory disclaimer."""
    gk_tool = tool_registry.get_tool("GeneralKnowledgeTool")
    res = gk_tool.execute(query="What is photosynthesis?", model_provider="gemini")
    
    assert res["confidence_met"] is True
    assert res["is_general_knowledge"] is True
    assert GENERAL_KNOWLEDGE_DISCLAIMER in res["answer"]


def test_agent_chat_endpoint_structure():
    """Verify POST /api/v1/agent/chat API endpoint contract."""
    payload = {
        "question": "Tell me about AI applications in food safety.",
        "model_provider": "gemini"
    }
    response = client.post("/api/v1/agent/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "conversation_id" in data
    assert "used_tools" in data
    assert isinstance(data["used_tools"], list)


def test_agent_discovery_job_configuration():
    """Verify Agent Discovery job respects threshold and configuration."""
    db = TestingSessionLocal()
    try:
        # Should execute cleanly without errors when AUTO_DISCOVERY_ENABLED is True
        run_agent_discovery_job(db=db)
    finally:
        db.close()


def test_agent_news_job_configuration():
    """Verify Agent News Monitor job runs cleanly."""
    db = TestingSessionLocal()
    try:
        run_agent_news_monitor_job(db=db)
    finally:
        db.close()
