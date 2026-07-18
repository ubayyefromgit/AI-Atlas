import pytest
from unittest.mock import MagicMock, patch

from backend.services.ask_ai.query_analyzer import QueryAnalyzer
from backend.services.ask_ai.context_manager import ContextManager
from backend.services.ask_ai.prompt_builder import PromptBuilder
from backend.services.ask_ai.citation_extractor import CitationExtractor
from backend.services.ask_ai.response_formatter import ResponseFormatter
from backend.services.ask_ai.ask_service import AskService
from backend.core.config import settings

def test_query_analyzer():
    analyzer = QueryAnalyzer()
    
    # Test comparison
    res = analyzer.analyze("Compare Krones and KHS")
    assert res["is_comparison"] is True
    assert res["is_news"] is False
    
    # Test news
    res = analyzer.analyze("What is the latest news about SIG?")
    assert res["is_news"] is True
    
    # Test general
    res = analyzer.analyze("What color is the sky?")
    assert res["is_general"] is True

def test_context_manager_dedup_and_sort():
    cm = ContextManager()
    
    class MockResult:
        def __init__(self, key, score, content="test"):
            self.chunk_key = key
            self.score = score
            self.content = content
            self.source_type = "company"
            self.source_id = 1
            
    # Two identical chunk keys, one has lower score
    results = [
        MockResult("C_1", 0.8, "Best"),
        MockResult("C_1", 0.4, "Duplicate"),
        MockResult("P_1", 0.9, "Highest"),
    ]
    
    ctx, sources = cm.prepare_context(results)
    
    # Should only be 2 sources (P_1 and C_1). P_1 should be first.
    assert len(sources) == 2
    assert sources[0]["chunk_key"] == "P_1"
    assert sources[1]["chunk_key"] == "C_1"

def test_prompt_builder():
    pb = PromptBuilder()
    sys = pb.build_system_prompt("MY_CONTEXT")
    assert "MY_CONTEXT" in sys
    assert "AI Atlas" in sys
    
    user = pb.build_user_prompt("MY_QUESTION")
    assert "MY_QUESTION" in user

def test_citation_extractor():
    extractor = CitationExtractor()
    text = "Krones is a company [S1]. KHS is another [S2]. Again [S1]."
    markers = extractor.extract_markers(text)
    assert markers == {"S1", "S2"}

def test_response_formatter():
    rf = ResponseFormatter()
    sources = [{"marker": "S1"}, {"marker": "S2"}]
    
    # Valid
    res = rf.format_response("Krones does bottling [S1].", sources)
    assert "Error" not in res["answer"]
    assert len(res["sources"]) == 1
    
    # Empty
    res = rf.format_response("", sources)
    assert "Error" in res["answer"]
    
    # Missing citations
    res = rf.format_response("Krones does bottling.", sources)
    assert "Error" in res["answer"]
    
    # Hallucinated citations
    res = rf.format_response("Krones does bottling [S99].", sources)
    assert "hallucinated" in res["answer"].lower()
    
    # Refusal
    res = rf.format_response("I don't have that information in my knowledge base.", sources)
    assert res["answer"] == "I don't have that information in my knowledge base."
    assert len(res["sources"]) == 0

@patch("backend.services.ask_ai.ask_service.LLMFactory.get_client")
def test_ask_service_refusal(mock_get_client):
    # Mock KB service to return low scores
    mock_kb = MagicMock()
    
    class MockResult:
        def __init__(self, key, score):
            self.chunk_key = key
            self.score = score
            self.content = "Low quality content"
            self.source_type = "company"
            self.source_id = 1
            
    mock_kb.search.return_value = [MockResult("C_1", 0.1)] # Below 0.3 threshold
    
    service = AskService(mock_kb)
    result = service.ask("Who is Krones?")
    
    # LLM should never be called
    mock_get_client.return_value.generate_response.assert_not_called()
    assert result["answer"] == "I don't have that information in my knowledge base."

@patch("backend.services.ask_ai.ask_service.LLMFactory.get_client")
def test_ask_service_success(mock_get_client):
    mock_kb = MagicMock()
    
    class MockResult:
        def __init__(self, key, score):
            self.chunk_key = key
            self.score = score
            self.content = "Krones is a company."
            self.source_type = "company"
            self.source_id = 1
            
    mock_kb.search.return_value = [MockResult("C_1", 0.9)]
    
    # Mock LLM returning a valid response with citation
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = "Krones is a company [S1]."
    mock_get_client.return_value = mock_llm
    
    service = AskService(mock_kb)
    result = service.ask("Who is Krones?")
    
    mock_llm.generate_response.assert_called_once()
    assert "Error" not in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["marker"] == "S1"
