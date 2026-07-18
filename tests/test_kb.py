import pytest
from unittest.mock import MagicMock, patch

from backend.services.knowledge_base.document_builder import DocumentBuilder, CompanyTemplate
from backend.services.knowledge_base.reranker import Reranker
from backend.services.knowledge_base.strategies.base import RetrievalResult

def test_document_builder_company_template():
    data = {
        "name": "Acme Corp",
        "country": "Germany",
        "company_type": "Startup",
        "segment_tags": ["AI", "FoodTech"],
        "maturity": 4,
        "website": "https://acme.com"
    }
    doc = DocumentBuilder.build_company_doc(data)
    assert "Acme Corp is a company based in Germany" in doc
    assert "Startup" in doc
    assert "AI, FoodTech" in doc
    assert "Maturity: 4" in doc

def test_document_hashing():
    doc1 = "Hello World"
    doc2 = "Hello World"
    doc3 = "Hello World!"
    
    assert DocumentBuilder.hash_document(doc1) == DocumentBuilder.hash_document(doc2)
    assert DocumentBuilder.hash_document(doc1) != DocumentBuilder.hash_document(doc3)

def test_reranker_exact_match():
    results = [
        RetrievalResult(chunk_key="1", source_type="company", source_id="1", title="Acme Inc", content="", score=0.5, matched_by="semantic"),
        RetrievalResult(chunk_key="2", source_type="company", source_id="2", title="Acme Corp", content="", score=0.6, matched_by="semantic"),
        RetrievalResult(chunk_key="3", source_type="company", source_id="3", title="Acme Corporation", content="", score=0.7, matched_by="semantic")
    ]
    
    # Reranking for query "Acme Corp"
    reranked = Reranker.rerank("Acme Corp", results)
    
    # "Acme Corp" should get +2.0 and jump to the top
    assert reranked[0].title == "Acme Corp"
    assert reranked[0].score == 2.6
    
    # "Acme Corporation" should get +1.0 for starting with "Acme Corp" 
    assert reranked[1].title == "Acme Corporation"
    assert reranked[1].score == 1.7
    
@patch("backend.services.knowledge_base.embeddings.EmbeddingService._load_model")
def test_embedding_service_singleton(mock_load):
    # Just testing singleton identity
    from backend.services.knowledge_base.embeddings import embedding_service, EmbeddingService
    another_instance = EmbeddingService()
    assert id(embedding_service) == id(another_instance)
