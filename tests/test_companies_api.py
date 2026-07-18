import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app
from core.database import get_db, Base
from models.company import Company
from models.problem import Problem
from models.mapping import ProblemCompanyMapping

from sqlalchemy.pool import StaticPool

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Seed data
    c1 = Company(name="Alpha", slug="alpha", country="Germany", ai_category="CV", segment_tags=["A", "B"], maturity=5, estimated_revenue=100.0)
    c2 = Company(name="Beta", slug="beta", country="USA", ai_category="NLP", segment_tags=["B", "C"], maturity=3)
    c3 = Company(name="Gamma", slug="gamma", country="Germany", ai_category="CV", segment_tags=["C"], maturity=4)
    db.add_all([c1, c2, c3])
    db.commit()
    
    p1 = Problem(ai_solution_use_case="Slow Logistics", category="Logistics", severity="High")
    db.add(p1)
    db.commit()
    db.refresh(c1)
    db.refresh(p1)
    
    m1 = ProblemCompanyMapping(problem_id=p1.id, company_id=c1.id, roi_benchmark="10%")
    db.add(m1)
    db.commit()

    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_get_companies_pagination(test_db):
    res = client.get("/api/v1/companies?limit=2&skip=0")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["has_next"] is True
    assert "execution_ms" in data

def test_get_companies_filtering(test_db):
    # Filter by country
    res = client.get("/api/v1/companies?country=Germany")
    data = res.json()
    assert data["total"] == 2
    
    # Filter by AI Category
    res = client.get("/api/v1/companies?ai_category=NLP")
    assert res.json()["total"] == 1
    
    # Filter by Segment
    res = client.get("/api/v1/companies?segment=B")
    assert res.json()["total"] == 2

def test_get_companies_sorting(test_db):
    res = client.get("/api/v1/companies?sort_by=name&sort_order=desc")
    data = res.json()
    assert data["items"][0]["name"] == "Gamma"
    assert data["items"][-1]["name"] == "Alpha"

def test_get_statistics(test_db):
    res = client.get("/api/v1/companies/statistics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_companies"] == 3
    assert data["country_distribution"]["Germany"] == 2
    assert data["country_distribution"]["USA"] == 1
    assert data["average_maturity"] == 4.0
    assert data["average_revenue"] == 100.0

def test_get_filters(test_db):
    res = client.get("/api/v1/companies/filters")
    assert res.status_code == 200
    data = res.json()
    
    # Check ai_categories format
    cats = {item["value"]: item["count"] for item in data["ai_categories"]}
    assert cats["CV"] == 2
    assert cats["NLP"] == 1
    
    # Check segments
    segs = {item["value"]: item["count"] for item in data["segments"]}
    assert segs["A"] == 1
    assert segs["B"] == 2
    assert segs["C"] == 2

def test_search_autocomplete(test_db):
    res = client.get("/api/v1/companies/search?q=alph")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "Alpha"
    assert data[0]["score"] > 0

def test_get_company_summary(test_db):
    res = client.get("/api/v1/companies/alpha/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Alpha"
    assert "segment_tags" not in data # Should be lightweight

def test_post_summaries(test_db):
    res = client.post("/api/v1/companies/summaries", json={"slugs": ["alpha", "beta"]})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2

def test_get_company_problems(test_db):
    res = client.get("/api/v1/companies/alpha/problems")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["problem_name"] == "Slow Logistics"
    assert data[0]["roi_benchmark"] == "10%"

def test_404_handling(test_db):
    res = client.get("/api/v1/companies/does-not-exist")
    assert res.status_code == 404
    
    res = client.get("/api/v1/companies/does-not-exist/summary")
    assert res.status_code == 404
