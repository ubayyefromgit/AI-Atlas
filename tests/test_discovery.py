import pytest
from unittest.mock import patch, MagicMock

from services.discovery.tavily_provider import TavilyProvider
from schemas.discovery import EvidenceItem
from services.discovery.evidence_collector import EvidenceCollector
from services.discovery.extractor import Extractor
from services.discovery.validator import Validator
from services.discovery.confidence import ConfidenceScorer

def test_tavily_provider_mock():
    provider = TavilyProvider()
    provider.api_key = "" # Force mock
    results = provider.search("test")
    assert len(results) == 1
    assert "Example AI Company" in results[0].title

@patch("services.discovery.evidence_collector.DiscoveryProviderFactory.get_provider")
def test_evidence_collector(mock_get_provider):
    mock_provider = MagicMock()
    mock_provider.search.return_value = [
        EvidenceItem(url="https://test.com", title="Test", snippet="snippet", retrieved_at="2023-01-01T00:00:00Z"),
        EvidenceItem(url="https://test.com/", title="Test2", snippet="snippet2", retrieved_at="2023-01-01T00:00:00Z")
    ]
    mock_get_provider.return_value = mock_provider
    
    collector = EvidenceCollector()
    results = collector.collect("Finance", "USA")
    
    # Assert deduplication (test.com and test.com/ are merged if norm works, wait - evidence collector strips trailing slashes)
    assert len(results) == 1
    assert results[0].url == "https://test.com"

@patch("services.discovery.extractor.LLMFactory.get_client")
def test_extractor(mock_get_client):
    mock_llm = MagicMock()
    mock_llm.generate_response.return_value = '[{"name": "AI Corp", "country": "USA", "website": "https://aicorp.com", "evidence_urls": ["https://test.com"]}]'
    mock_get_client.return_value = mock_llm
    
    extractor = Extractor()
    evidence = [EvidenceItem(url="https://test.com", title="Test", snippet="snippet", retrieved_at="2023-01-01T00:00:00Z")]
    results = extractor.extract("Finance", "USA", evidence)
    
    assert len(results) == 1
    assert results[0]["name"] == "AI Corp"

@patch("services.discovery.validator.httpx.Client")
def test_validator(mock_client):
    mock_response = MagicMock()
    mock_response.text = "<html><title>AI Corp Home</title></html>"
    
    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value.get.return_value = mock_response
    mock_client.return_value = mock_client_instance
    
    validator = Validator()
    is_valid, reasons, verified = validator.validate({
        "name": "AI Corp",
        "country": "USA",
        "website": "https://aicorp.com",
        "evidence_urls": ["https://test.com"]
    })
    
    assert is_valid is True
    assert verified is True

def test_confidence_scorer():
    scorer = ConfidenceScorer()
    conf, explanation = scorer.score({
        "name": "AI Corp",
        "country": "USA",
        "website": "https://aicorp.com",
        "evidence_urls": ["https://test.com", "https://test2.com"]
    }, website_verified=True)
    
    assert explanation.evidence_count == 2
    assert explanation.website_verified is True
    assert explanation.field_completeness == 0.5 # 3 out of 6
    assert conf > 0.6
