import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app
from core.database import get_db, Base
from models.company import Company
from models.news import NewsArticle
from models.kb_chunk import KBChunk
from services.news.news_service import NewsService
from services.news.provider import NewsProvider

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

class MockProvider(NewsProvider):
    def fetch_news(self, company_name, website=None):
        return [
            {
                "title": f"Great news about {company_name}",
                "description": f"{company_name} just launched a new product.",
                "url": "https://example.com/news1",
                "published_at": datetime.now(timezone.utc),
                "source": "Mock News"
            },
            {
                "title": "Unrelated title",
                "description": "Unrelated description.",
                "url": "https://example.com/news2",
                "published_at": datetime.now(timezone.utc),
                "source": "Mock News"
            }
        ]

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    c1 = Company(name="NewsCo", slug="newsco", website="https://newsco.com")
    db.add(c1)
    db.commit()
    
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@patch("services.news.news_pipeline.NewsProviderFactory.get_provider")
@patch("services.news.summarizer.Summarizer.summarize")
def test_manual_refresh_and_relevance(mock_summarize, mock_get_provider, test_db):
    mock_get_provider.return_value = MockProvider()
    mock_summarize.return_value = "Mocked summary."
    
    res = client.post("/api/v1/news/companies/newsco/news/refresh")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    stats = data["stats"]
    assert stats["fetched"] == 2
    assert stats["relevant"] == 1 # Only the first one is relevant
    assert stats["stored"] == 1
    assert stats["indexed"] == 1
    
    # Verify DB
    articles = test_db.query(NewsArticle).all()
    assert len(articles) == 1
    assert articles[0].headline == "Great news about NewsCo"
    
    # Verify KB Chunk
    chunks = test_db.query(KBChunk).filter(KBChunk.source_type == "news").all()
    assert len(chunks) == 1

@patch("services.news.news_pipeline.NewsProviderFactory.get_provider")
@patch("services.news.summarizer.Summarizer.summarize")
def test_deduplication(mock_summarize, mock_get_provider, test_db):
    mock_get_provider.return_value = MockProvider()
    mock_summarize.return_value = "Mocked summary."
    
    # Run again, should fetch 2, relevant 1, but stored 0 due to dedup
    res = client.post("/api/v1/news/companies/newsco/news/refresh")
    assert res.status_code == 200
    stats = res.json()["stats"]
    assert stats["fetched"] == 2
    assert stats["relevant"] == 1
    assert stats["duplicates_removed"] == 1
    assert stats["stored"] == 0

def test_get_company_news(test_db):
    res = client.get("/api/v1/news/companies/newsco/news")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["headline"] == "Great news about NewsCo"

def test_get_statistics(test_db):
    res = client.get("/api/v1/news/statistics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_articles"] == 1
    assert data["companies_with_news"] == 1

def test_get_health():
    res = client.get("/api/v1/news/health")
    assert res.status_code == 200
    data = res.json()
    assert "provider_status" in data
    assert "scheduler_status" in data
