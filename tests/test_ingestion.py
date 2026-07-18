import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from backend.services.ingestion.cleaners import clean_string, parse_multi_value, normalize_url
from backend.services.ingestion.transformers import transform_company_row
from backend.services.ingestion.validators import validate_company
from backend.services.ingestion.loader import CSVLoader

def test_clean_string():
    assert clean_string("   test   ") == "test"
    assert clean_string("") is None
    assert clean_string("NaN") is None
    assert clean_string("none") is None
    assert clean_string(float('nan')) is None
    # Unicode space normalization
    assert clean_string("test   spacing") == "test spacing"

def test_parse_multi_value():
    assert parse_multi_value("a, b, c") == ["a", "b", "c"]
    assert parse_multi_value("a; b; c") == ["a", "b", "c"]
    assert parse_multi_value("a | b | c") == ["a", "b", "c"]
    # If mixed, it prefers semicolon if it exists
    assert parse_multi_value("a,b; c,d") == ["a,b", "c,d"]
    assert parse_multi_value("['a', 'b']") == ["a, b"] # Handled loosely

def test_normalize_url():
    assert normalize_url("google.com") == "https://google.com"
    assert normalize_url("http://google.com") == "http://google.com"
    assert normalize_url("https://google.com") == "https://google.com"
    assert normalize_url("") is None

def test_transform_company_row():
    row = pd.Series({
        "name": "Test Company",
        "segment_tags": "AI; ML",
        "maturity": "4.0",
        "website": "test.com"
    })
    transformed = transform_company_row(row)
    assert transformed["name"] == "Test Company"
    assert transformed["segment_tags"] == ["AI", "ML"]
    assert transformed["maturity"] == 4
    assert transformed["website"] == "https://test.com"

def test_validate_company_success():
    row_data = {
        "name": "Valid Company",
        "website": "https://valid.com",
        "maturity": 3,
        "source": "dataset",
        "status": "APPROVED"
    }
    company, warnings = validate_company(row_data)
    assert not warnings
    assert company is not None
    assert company.name == "Valid Company"

def test_validate_company_failure():
    # Missing name
    row_data = {"website": "https://valid.com"}
    company, warnings = validate_company(row_data)
    assert company is None
    assert len(warnings) == 1
    assert "Missing required field" in warnings[0]
    
    # Invalid URL
    row_data2 = {"name": "Test", "website": "not-a-url"}
    company2, warnings2 = validate_company(row_data2)
    assert company2 is None
    assert len(warnings2) > 0
    assert "website" in warnings2[0]

def test_csv_loader_missing_file():
    loader = CSVLoader("/invalid/path")
    with pytest.raises(FileNotFoundError):
        loader.load_csv("nonexistent.csv")
