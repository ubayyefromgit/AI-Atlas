import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from core.config import settings
from services.agent.tool_registry import tool_registry, GENERAL_KNOWLEDGE_DISCLAIMER
from services.agent.memory import agent_memory

logger = logging.getLogger("agent.service")

class AgentService:
    """
    Orchestrates AI Agent planner flow:
    User Query -> Intent Detection -> Tool Selection -> Tool Execution -> Response Merge -> Return Answer
    """
    def __init__(self, db: Session):
        self.db = db

    def _detect_intent(self, query: str) -> str:
        q_lower = query.lower()
        
        # Check for news intent
        if any(kw in q_lower for kw in ["news", "latest article", "trending", "headline", "media coverage"]):
            return "news"
            
        # Check for discovery / finding new companies intent
        if any(kw in q_lower for kw in ["discover", "find new company", "search web for", "new startups", "candidate"]):
            return "discovery"
            
        # Default to knowledge base search
        return "knowledge"

    def chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        model_provider: str = "gemini"
    ) -> Dict[str, Any]:
        """
        Main planner execution flow.
        """
        # 1. Initialize or load conversation memory
        ctx = agent_memory.get_or_create(conversation_id)
        conv_id = ctx.conversation_id
        history_context = ctx.format_history_context(max_turns=3)
        
        tools_used: List[str] = []
        is_general_knowledge = False
        
        # 2. Intent Detection & Tool Selection
        intent = self._detect_intent(query)
        logger.info(f"Agent Chat | conv_id: {conv_id} | detected intent: {intent} | query: '{query}'")
        
        final_answer = ""
        sources = []

        if intent == "news":
            news_tool = tool_registry.get_tool("NewsTool")
            if news_tool:
                tools_used.append(news_tool.name)
                res = news_tool.execute(query=query, db=self.db)
                final_answer = res.get("answer", "")
                
        elif intent == "discovery":
            discovery_tool = tool_registry.get_tool("DiscoveryTool")
            if discovery_tool:
                tools_used.append(discovery_tool.name)
                res = discovery_tool.execute(query=query, db=self.db)
                final_answer = res.get("answer", "")

        # Default or fallback to Knowledge Base RAG
        if not final_answer or intent == "knowledge":
            kb_tool = tool_registry.get_tool("KnowledgeTool")
            if kb_tool:
                tools_used.append(kb_tool.name)
                res = kb_tool.execute(query=query, db=self.db, model_provider=model_provider)
                
                # Check if knowledge base answered with confidence
                if res.get("confidence_met", False):
                    final_answer = res.get("answer", "")
                    sources = res.get("sources", [])
                else:
                    logger.info(f"KnowledgeTool low confidence/refusal for query: '{query}'. Checking General Knowledge fallback...")
                    # PART 2: General Knowledge Fallback
                    if settings.GENERAL_KNOWLEDGE_ENABLED:
                        gk_tool = tool_registry.get_tool("GeneralKnowledgeTool")
                        if gk_tool:
                            tools_used.append(gk_tool.name)
                            gk_res = gk_tool.execute(
                                query=query,
                                model_provider=model_provider,
                                history_context=history_context
                            )
                            final_answer = gk_res.get("answer", "")
                            sources = []
                            is_general_knowledge = True
                    else:
                        final_answer = res.get("answer", "")
                        sources = res.get("sources", [])

        # Ensure disclaimer is included if general knowledge fallback was triggered
        if is_general_knowledge and GENERAL_KNOWLEDGE_DISCLAIMER not in final_answer:
            final_answer = f"{final_answer}\n\n*{GENERAL_KNOWLEDGE_DISCLAIMER}*"

        # 3. Store interaction in conversation memory
        agent_memory.add_interaction(conv_id, query, final_answer, tools_used)

        return {
            "answer": final_answer,
            "sources": sources,
            "conversation_id": conv_id,
            "used_tools": tools_used,
            "is_general_knowledge": is_general_knowledge
        }
