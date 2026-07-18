import json
import re
from typing import List, Dict, Any, Optional
from schemas.discovery import EvidenceItem, DiscoveryCandidateBase
from services.ask_ai.llm.factory import LLMFactory
import logging

logger = logging.getLogger(__name__)

def _extract_json_array(text: str) -> Optional[list]:
    """
    Robustly extracts a JSON array from any LLM response text.
    Handles markdown fences, leading prose, trailing text, etc.
    """
    if not text:
        return None

    # 1. Try stripping markdown code fences first
    fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text, re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    # 2. Try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        # If it's a dict with an array inside (e.g. {"companies": [...]})
        for val in parsed.values():
            if isinstance(val, list):
                return val
    except json.JSONDecodeError:
        pass

    # 3. Find the first [...] block in the text
    bracket_match = re.search(r'\[.*\]', text, re.DOTALL)
    if bracket_match:
        try:
            parsed = json.loads(bracket_match.group(0))
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    return None


class CompanyExtractionResult(DiscoveryCandidateBase):
    evidence_urls: List[str] = []

class Extractor:
    def __init__(self):
        self.llm_primary = LLMFactory.get_client("gemini")
        self.llm_secondary = LLMFactory.get_client("groq")
        self.llm_tertiary = LLMFactory.get_client("ollama")
        
        self.schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "country": {"type": "string"},
                    "ai_category": {"type": "string"},
                    "segment_tags": {"type": "array", "items": {"type": "string"}},
                    "use_cases": {"type": "array", "items": {"type": "string"}},
                    "website": {"type": "string"},
                    "evidence_urls": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["name", "country", "website", "evidence_urls"]
            }
        }
        
        self.system_prompt = """
You are an expert AI data extraction system. You MUST respond with ONLY a valid JSON array and nothing else.
Do NOT include any explanation, markdown, or code fences.

You will receive a list of search result snippets (evidence).
Your task is to identify real AI, automation, or machine vision companies from this evidence.
Do NOT invent any companies. Only extract a company if there is clear evidence it exists and fits the criteria.
Extract the company name, country (if apparent), AI category, segment tags, use cases, and official website URL.
Map the exact 'url' from the evidence into 'evidence_urls'.

Your entire response must be a raw JSON array, like:
[{"name": "...", "country": "...", "ai_category": "...", "segment_tags": [], "use_cases": [], "website": "...", "evidence_urls": ["..."]}]

If no companies are found, respond with an empty array: []
"""

    def extract(self, sector: str, country: str, evidence: List[EvidenceItem]) -> List[Dict[str, Any]]:
        if not evidence:
            return []
            
        # Format evidence for the LLM
        evidence_text = "EVIDENCE ITEMS:\n\n"
        for i, item in enumerate(evidence):
            evidence_text += f"[{i+1}] URL: {item.url}\nTitle: {item.title}\nSnippet: {item.snippet}\n\n"
            
        user_prompt = f"Find AI/automation companies for sector '{sector}' in '{country}'.\n\n{evidence_text}"
        
        response_text = None
        try:
            logger.info("Attempting extraction with Primary LLM (Gemini)...")
            response_text = self.llm_primary.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.0,
                response_schema=self.schema
            )
        except Exception as e:
            logger.warning(f"Primary LLM failed ({e}). Falling back to Secondary LLM (Groq)...")
            try:
                response_text = self.llm_secondary.generate_response(
                    system_prompt=self.system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.0,
                    response_schema=self.schema
                )
            except Exception as e2:
                logger.warning(f"Secondary LLM failed ({e2}). Falling back to Tertiary LLM (Ollama)...")
                try:
                    response_text = self.llm_tertiary.generate_response(
                        system_prompt=self.system_prompt,
                        user_prompt=user_prompt,
                        temperature=0.0,
                        response_schema=self.schema
                    )
                except Exception as e3:
                    logger.error(f"Tertiary LLM also failed: {e3}")
                    return []
                
        if not response_text:
            logger.warning("No response text from any LLM.")
            return []

        result = _extract_json_array(response_text)
        if result is None:
            logger.error(f"Failed to extract JSON array from LLM response. Raw text: {response_text[:200]}")
            return []

        return result
