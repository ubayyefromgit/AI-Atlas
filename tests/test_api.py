import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.core.database import get_db, Base

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

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data
    assert "environment" in data

def test_database_table_creation(test_db):
    from backend.models.company import Company
    # Should not throw an exception
    companies = test_db.query(Company).all()
    assert isinstance(companies, list)

def test_create_company():
    response = client.post("/api/v1/companies/", json={
        "name": "Test Company",
        "website": "https://test.com",
        "maturity": 3
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Company"
    assert data["slug"] == "test-company"
    assert data["website"] == "https://test.com/"

def test_duplicate_company_rejection():
    # Attempt to create the same company name
    response = client.post("/api/v1/companies/", json={
        "name": "Test Company",
        "website": "https://anothertest.com",
        "maturity": 4
    })
    assert response.status_code == 400
    
    # Attempt to create with same website
    response2 = client.post("/api/v1/companies/", json={
        "name": "Another Company",
        "website": "https://test.com",
        "maturity": 4
    })
    assert response2.status_code == 400

def test_invalid_maturity():
    response = client.post("/api/v1/companies/", json={
        "name": "Invalid Maturity Company",
        "maturity": 6 # Invalid, must be <= 5
    })
    assert response.status_code == 422 # Validation Error

def test_invalid_url():
    response = client.post("/api/v1/companies/", json={
        "name": "Invalid URL Company",
        "website": "not-a-url"
    })
    assert response.status_code == 422 # Validation Error

def test_unknown_slug_returns_404():
    response = client.get("/api/v1/companies/unknown-slug-1234")
    assert response.status_code == 404
