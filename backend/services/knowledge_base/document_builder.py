import hashlib
from typing import Dict, Any

class BaseTemplate:
    @classmethod
    def render(cls, data: Dict[str, Any]) -> str:
        raise NotImplementedError

class CompanyTemplate(BaseTemplate):
    @classmethod
    def render(cls, c: Dict[str, Any]) -> str:
        doc = f"{c.get('name', 'Unknown')} is a company based in {c.get('country', 'Unknown')}"
        if c.get("company_type"):
            doc += f" operating as a {c.get('company_type')}."
        else:
            doc += "."

        doc += f"\n\nAI Category: {c.get('ai_category', 'N/A')}."
        
        if c.get("segment_tags"):
            doc += f"\nSegments: {', '.join(c['segment_tags'])}"
            
        if c.get("use_cases"):
            doc += f"\nUse Cases:\n" + "\n".join([f"- {u}" for u in c["use_cases"]])

        if c.get("top_german_customers"):
            doc += f"\nGerman Customers:\n" + "\n".join([f"- {u}" for u in c["top_german_customers"]])

        if c.get("funding"):
            doc += f"\nFunding: {c['funding']}"
        if c.get("estimated_revenue"):
            doc += f"\nEstimated Revenue: {c['estimated_revenue']}"

        doc += f"\nMaturity: {c.get('maturity', 'N/A')}"
        doc += f"\nWebsite: {c.get('website', 'N/A')}"
        
        if c.get("deployment_evidence"):
            doc += f"\nEvidence: {c['deployment_evidence']}"

        return doc

class ProblemTemplate(BaseTemplate):
    @classmethod
    def render(cls, p: Dict[str, Any]) -> str:
        doc = f"Problem Category: {p.get('category', 'Unknown')}"
        if p.get("severity"):
            doc += f"\nSeverity: {p.get('severity')}"
        if p.get("ai_solution_use_case"):
            doc += f"\nAI Solution: {p.get('ai_solution_use_case')}"
        if p.get("affected_companies"):
            doc += f"\nAffected Companies: {p.get('affected_companies')}"
        if p.get("financial_impact"):
            doc += f"\nFinancial Impact: {p.get('financial_impact')}"
        if p.get("regulatory_triggers"):
            doc += f"\nRegulatory Triggers: {p.get('regulatory_triggers')}"
        return doc

class SectorTemplate(BaseTemplate):
    @classmethod
    def render(cls, s: Dict[str, Any]) -> str:
        doc = f"Sector: {s.get('name', 'Unknown')}"
        if s.get("definition"):
            doc += f"\nDefinition: {s.get('definition')}"
        if s.get("key_companies"):
            doc += f"\nKey Companies: {', '.join(s['key_companies'])}"
        if s.get("primary_ai_entry_points"):
            doc += f"\nAI Entry Points:\n" + "\n".join([f"- {u}" for u in s["primary_ai_entry_points"]])
        if s.get("ai_adoption"):
            doc += f"\nAI Adoption: {s.get('ai_adoption')}"
        if s.get("market_size"):
            doc += f"\nMarket Size: {s.get('market_size')}"
        if s.get("regulatory_complexity"):
            doc += f"\nRegulatory Complexity: {s.get('regulatory_complexity')}"
        return doc

class DocumentBuilder:
    @staticmethod
    def build_company_doc(company_dict: Dict[str, Any]) -> str:
        return CompanyTemplate.render(company_dict)

    @staticmethod
    def build_problem_doc(problem_dict: Dict[str, Any]) -> str:
        return ProblemTemplate.render(problem_dict)

    @staticmethod
    def build_sector_doc(sector_dict: Dict[str, Any]) -> str:
        return SectorTemplate.render(sector_dict)

    @staticmethod
    def hash_document(document: str) -> str:
        """Compute a SHA-256 hash of the generated document."""
        return hashlib.sha256(document.encode("utf-8")).hexdigest()
