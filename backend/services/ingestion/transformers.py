# backend/services/ingestion/transformers.py
from typing import Dict, Any
import re
import pandas as pd
from services.ingestion.cleaners import clean_string, parse_multi_value, safe_int, normalize_url

# ── Column name aliases: maps CSV headers → internal field names ──────────────
COMPANY_COLUMN_MAP = {
    "Vendor Name": "name",
    "Country": "country",
    "AI Category": "ai_category",
    "Seg Tags": "segment_tags",
    "F&B AI Use Case": "use_cases",
    "Top Germany F&B Customers": "top_german_customers",
    "Germany Presence": "germany_presence",
    "Company Type": "company_type",
    "Funding": "funding_raw",
    "Est. Revenue": "estimated_revenue_raw",
    "Maturity": "maturity_raw",
    "Top Deployment Evidence": "deployment_evidence",
    "Website": "website",
}

SECTOR_COLUMN_MAP = {
    "Segment Name": "name",
    "Definition": "definition",
    "Key Germany Companies": "key_companies",
    "Primary AI Entry Point": "primary_ai_entry_points",
    "AI Adoption": "ai_adoption",
    "DE Market Size": "market_size",
    "Regulatory Complexity": "regulatory_complexity",
}

PROBLEM_COLUMN_MAP = {
    "Problem Statement": "category",
    "Severity": "severity",
    "AI Use Case Solution": "ai_solution_use_case",
    "Affected Germany Companies": "affected_companies",
    "Financial Impact (€)": "financial_impact",
    "Regulatory Trigger": "regulatory_triggers",
}

MAPPING_COLUMN_MAP = {
    "Problem Statement": "problem_statement",
    "Germany Vendors (ranked)": "vendors_ranked",
    "Seg Tags": "segment_name",
    "ROI Benchmark": "evidence",
}

def _remap(row: pd.Series, col_map: dict) -> Dict[str, Any]:
    """Remap a pandas row using the given column alias map."""
    out: Dict[str, Any] = {}
    for csv_col, field in col_map.items():
        out[field] = row.get(csv_col)
    return out

def transform_company_row(row: pd.Series) -> Dict[str, Any]:
    r = _remap(row, COMPANY_COLUMN_MAP)
    # Maturity field: CSV has values like "4 — Mature", extract the leading digit
    maturity_raw = clean_string(r.get("maturity_raw"))
    maturity_int = None
    if maturity_raw:
        m = re.match(r"(\d+)", maturity_raw)
        maturity_int = int(m.group(1)) if m else None

    return {
        "name": clean_string(r.get("name")),
        "country": clean_string(r.get("country")),
        "ai_category": clean_string(r.get("ai_category")),
        "segment_tags": parse_multi_value(r.get("segment_tags")),
        "use_cases": parse_multi_value(r.get("use_cases")),
        "top_german_customers": parse_multi_value(r.get("top_german_customers")),
        "germany_presence": clean_string(r.get("germany_presence")),
        "company_type": clean_string(r.get("company_type")),
        "funding": clean_string(r.get("funding_raw")),
        "estimated_revenue": clean_string(r.get("estimated_revenue_raw")),
        "maturity": maturity_int,
        "deployment_evidence": clean_string(r.get("deployment_evidence")),
        "website": normalize_url(r.get("website")),
        "source": "dataset",
        "status": "APPROVED",
    }

def transform_problem_row(row: pd.Series) -> Dict[str, Any]:
    r = _remap(row, PROBLEM_COLUMN_MAP)
    return {
        "category": clean_string(r.get("category")),
        "severity": clean_string(r.get("severity")),
        "ai_solution_use_case": clean_string(r.get("ai_solution_use_case")),
        "affected_companies": clean_string(r.get("affected_companies")),
        "financial_impact": clean_string(r.get("financial_impact")),
        "regulatory_triggers": clean_string(r.get("regulatory_triggers")),
    }

def transform_sector_row(row: pd.Series) -> Dict[str, Any]:
    r = _remap(row, SECTOR_COLUMN_MAP)
    return {
        "name": clean_string(r.get("name")),
        "definition": clean_string(r.get("definition")),
        "key_companies": parse_multi_value(r.get("key_companies")),
        "primary_ai_entry_points": parse_multi_value(r.get("primary_ai_entry_points")),
        "ai_adoption": clean_string(r.get("ai_adoption")),
        "market_size": clean_string(r.get("market_size")),
        "regulatory_complexity": clean_string(r.get("regulatory_complexity")),
    }

def transform_mapping_row(row: pd.Series) -> Dict[str, Any]:
    """
    The mapping CSV links problem statements to vendor lists.
    We now extract ALL vendors from the ranked list.
    Returns company_names as a list.
    """
    r = _remap(row, MAPPING_COLUMN_MAP)
    # The "Germany Vendors (ranked)" field looks like:
    #   "1. Cognex  2. Keyence  3. SICK AG  4. Krones  5. Agilx"
    vendors_raw = clean_string(r.get("vendors_ranked"))
    company_names = []
    if vendors_raw:
        # Split on rank pattern: "1. ", "2. ", etc.
        parts = re.split(r'\d+\.\s*', vendors_raw)
        for part in parts:
            name = part.strip().rstrip(",").strip()
            if name:
                company_names.append(name)

    return {
        "company_names": company_names,           # list of all vendors
        "problem_category": clean_string(r.get("problem_statement")),
        "segment_name": clean_string(r.get("segment_name")),
        "evidence": clean_string(r.get("evidence")),
    }


