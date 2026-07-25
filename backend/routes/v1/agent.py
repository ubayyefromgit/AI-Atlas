from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.agent import AgentAskRequest, AgentAskResponse
from services.agent.agent_service import AgentService

router = APIRouter()

def get_agent_service(db: Session = Depends(get_db)) -> AgentService:
    return AgentService(db)

@router.post("/chat", response_model=AgentAskResponse)
def agent_chat(
    request: AgentAskRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    AI Agent Chat Endpoint.
    Uses AgentService planner flow, tool selection, lightweight conversation memory,
    and fallback to general knowledge reasoning when retrieval confidence is low.
    """
    response = agent_service.chat(
        query=request.question,
        conversation_id=request.conversation_id,
        model_provider=request.model_provider
    )
    
    if "Error:" in response.get("answer", ""):
        raise HTTPException(status_code=500, detail=response["answer"])
        
    return response
