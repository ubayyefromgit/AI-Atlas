from typing import Dict, Any, List
from sqlalchemy.orm import Session
from services.ask_ai.ask_service import AskService
from services.knowledge_base.kb_service import kb_service
import logging

logger = logging.getLogger(__name__)

EVAL_CASES = [
    {
        "question": "What is GEA Group AG's estimated revenue?",
        "expected_keywords": ["5.3B", "billion", "5.3"],
        "expect_refusal": False,
        "description": "Round-trip fidelity check (Data Retrieval)"
    },
    {
        "question": "What is the phone number of GEA's CEO?",
        "expected_keywords": [],
        "expect_refusal": True,
        "description": "Out-of-dataset question (Anti-Hallucination)"
    },
    {
        "question": "Who are the top customers for Marel?",
        "expected_keywords": ["PHW", "Wiesenhof", "Vion", "Bell"],
        "expect_refusal": False,
        "description": "Round-trip fidelity check (Customer Extraction)"
    },
    {
        "question": "Give me a recipe for chocolate chip cookies.",
        "expected_keywords": [],
        "expect_refusal": True,
        "description": "Irrelevant general knowledge (Anti-Hallucination)"
    },
    {
        "question": "Which company focuses on Meat, Poultry & Fish Processing AI?",
        "expected_keywords": ["Marel"],
        "expect_refusal": False,
        "description": "Semantic search based on use case"
    },
    {
        "question": "What is Marel's maturity level?",
        "expected_keywords": ["4", "Mature", "four"],
        "expect_refusal": False,
        "description": "Round-trip fidelity check (Numeric data)"
    },
    {
        "question": "List some food delivery companies operating on Mars.",
        "expected_keywords": [],
        "expect_refusal": True,
        "description": "Absurd location (Anti-Hallucination)"
    },
    {
        "question": "Is Siemens involved in the F&B sector?",
        "expected_keywords": ["Yes", "Siemens", "automation", "PLC"],
        "expect_refusal": False,
        "description": "General dataset knowledge"
    },
    {
        "question": "What is the funding for GEA Group AG?",
        "expected_keywords": ["Public", "MDAX"],
        "expect_refusal": False,
        "description": "Round-trip fidelity check (Funding)"
    },
    {
        "question": "Who won the 1998 FIFA World Cup?",
        "expected_keywords": [],
        "expect_refusal": True,
        "description": "Historical trivia (Anti-Hallucination)"
    }
]

class EvalService:
    @staticmethod
    def run_evaluation(db: Session) -> Dict[str, Any]:
        ask_service = AskService(kb_service, db)
        
        import time
        
        passed_count = 0
        total = len(EVAL_CASES)
        results = []
        
        for idx, case in enumerate(EVAL_CASES, 1):
            if idx > 1:
                logger.info("Sleeping for 2 seconds to be safe...")
                time.sleep(2)
                
            question = case["question"]
            logger.info(f"Running eval test {idx}: {case['description']}")
            
            try:
                result = ask_service.ask(question, model_provider="groq")
                answer = result.get("answer", "")
                
                passed = False
                if case["expect_refusal"]:
                    refusal_phrases = ["I don't have that information", "I don't have", "knowledge base"]
                    passed = any(phrase.lower() in answer.lower() for phrase in refusal_phrases)
                else:
                    passed = any(keyword.lower() in answer.lower() for keyword in case["expected_keywords"])
                    
                if passed:
                    passed_count += 1
                
                results.append({
                    "id": idx,
                    "description": case["description"],
                    "question": question,
                    "answer": answer,
                    "passed": passed,
                    "expected_keywords": case["expected_keywords"],
                    "expect_refusal": case["expect_refusal"],
                    "error": None
                })
            except Exception as e:
                logger.error(f"Eval test {idx} failed with error: {e}")
                results.append({
                    "id": idx,
                    "description": case["description"],
                    "question": question,
                    "answer": "",
                    "passed": False,
                    "expected_keywords": case["expected_keywords"],
                    "expect_refusal": case["expect_refusal"],
                    "error": str(e)
                })
                
        return {
            "total_tests": total,
            "passed_count": passed_count,
            "results": results,
            "score_percentage": (passed_count / total) * 100 if total > 0 else 0
        }
