import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from services.knowledge_base.kb_service import KnowledgeBaseService
from services.ask_ai.ask_service import AskService
from services.news.news_service import NewsService
from services.discovery.quick_discovery import QuickDiscoveryService
from services.ask_ai.llm.factory import LLMFactory
from core.config import settings

logger = logging.getLogger("agent.tools")

GENERAL_KNOWLEDGE_DISCLAIMER = "This answer is based on general knowledge and not the project knowledge base."

class BaseTool:
    name: str
    description: str

    def execute(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()


class KnowledgeTool(BaseTool):
    name = "KnowledgeTool"
    description = "Searches the AI Atlas Knowledge Base (companies, problems, sectors, and internal docs) using Grounded RAG."

    def __init__(self, kb_service: Optional[KnowledgeBaseService] = None):
        self.kb_service = kb_service or KnowledgeBaseService()

    def execute(self, query: str, db: Session, model_provider: str = "gemini", **kwargs) -> Dict[str, Any]:
        logger.info(f"Executing KnowledgeTool for query: {query}")
        ask_service = AskService(self.kb_service, db)
        res = ask_service.ask(query, model_provider=model_provider)
        # Determine if context met confidence threshold
        has_sources = len(res.get("sources", [])) > 0
        refusal_marker = "do not have enough information" in res.get("answer", "").lower() or "outside my knowledge" in res.get("answer", "").lower()
        res["confidence_met"] = has_sources and not refusal_marker
        res["tool_name"] = self.name
        return res


class NewsTool(BaseTool):
    name = "NewsTool"
    description = "Retrieves recent news articles, industry trends, and company updates."

    def __init__(self, news_service: Optional[NewsService] = None):
        self.news_service = news_service or NewsService()

    def execute(self, query: str, db: Session, limit: int = 5, **kwargs) -> Dict[str, Any]:
        logger.info(f"Executing NewsTool for query: {query}")
        try:
            articles = self.news_service.get_recent_news(db=db, limit=limit)
            formatted_articles = []
            for art in articles:
                formatted_articles.append(f"- [{art.title}] ({art.url}): {art.summary or art.content[:200]}")
            
            summary = "\n".join(formatted_articles) if formatted_articles else "No recent news articles found."
            return {
                "answer": f"Recent News Summary:\n{summary}",
                "articles": [art.to_dict() if hasattr(art, 'to_dict') else {"title": art.title, "url": art.url} for art in articles],
                "confidence_met": len(articles) > 0,
                "tool_name": self.name
            }
        except Exception as e:
            logger.error(f"NewsTool execution error: {e}")
            return {
                "answer": f"Unable to fetch news articles: {str(e)}",
                "articles": [],
                "confidence_met": False,
                "tool_name": self.name
            }


class DiscoveryTool(BaseTool):
    name = "DiscoveryTool"
    description = "Performs automated discovery for new AI companies and market intelligence."

    def __init__(self, quick_discovery: Optional[QuickDiscoveryService] = None):
        self.quick_discovery = quick_discovery or QuickDiscoveryService()

    def execute(self, query: str, db: Session, **kwargs) -> Dict[str, Any]:
        logger.info(f"Executing DiscoveryTool for query: {query}")
        try:
            results = self.quick_discovery.search(query=query)
            return {
                "answer": f"Discovery search completed for '{query}'. Found {len(results)} potential candidates.",
                "candidates": results,
                "confidence_met": len(results) > 0,
                "tool_name": self.name
            }
        except Exception as e:
            logger.error(f"DiscoveryTool execution error: {e}")
            return {
                "answer": f"Discovery execution error: {str(e)}",
                "candidates": [],
                "confidence_met": False,
                "tool_name": self.name
            }


class GeneralKnowledgeTool(BaseTool):
    name = "GeneralKnowledgeTool"
    description = "Answers out-of-domain general knowledge questions using Gemini/Groq general reasoning."

    def execute(self, query: str, model_provider: str = "gemini", history_context: str = "", **kwargs) -> Dict[str, Any]:
        logger.info(f"Executing GeneralKnowledgeTool for query: {query}")
        try:
            llm_client = LLMFactory.get_client(model_provider)
            system_prompt = (
                "You are an AI assistant providing general knowledge reasoning.\n"
                "IMPORTANT: Answer the user's question concisely, accurately, and politely based on general knowledge.\n"
                "Do NOT invent or hallucinate project-specific companies, products, or metadata."
            )
            
            user_prompt = query
            if history_context:
                user_prompt = f"Previous conversation context:\n{history_context}\n\nCurrent question: {query}"
                
            raw_answer = llm_client.generate_response(system_prompt, user_prompt)
            
            # Mandated prefix/suffix disclaimer
            disclaimer = GENERAL_KNOWLEDGE_DISCLAIMER
            final_answer = f"{raw_answer.strip()}\n\n*{disclaimer}*"
            
            return {
                "answer": final_answer,
                "sources": [],
                "confidence_met": True,
                "is_general_knowledge": True,
                "tool_name": self.name
            }
        except Exception as e:
            logger.error(f"GeneralKnowledgeTool execution error: {e}")
            return {
                "answer": f"General knowledge reasoning encountered an error: {str(e)}\n\n*{GENERAL_KNOWLEDGE_DISCLAIMER}*",
                "sources": [],
                "confidence_met": False,
                "is_general_knowledge": True,
                "tool_name": self.name
            }


class ToolRegistry:
    """
    Registry that exposes existing application services as Agent Tools.
    Follows Open-Closed principle without duplicating business logic.
    """
    def __init__(self):
        self.knowledge_tool = KnowledgeTool()
        self.news_tool = NewsTool()
        self.discovery_tool = DiscoveryTool()
        self.general_knowledge_tool = GeneralKnowledgeTool()

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        tools = {
            "KnowledgeTool": self.knowledge_tool,
            "NewsTool": self.news_tool,
            "DiscoveryTool": self.discovery_tool,
            "GeneralKnowledgeTool": self.general_knowledge_tool,
        }
        return tools.get(tool_name)

tool_registry = ToolRegistry()
