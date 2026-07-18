from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.ask import AskRequest, AskResponse
from services.knowledge_base.kb_service import KnowledgeBaseService
from services.ask_ai.ask_service import AskService

router = APIRouter()

# Dependency for AskService
def get_ask_service(db: Session = Depends(get_db)) -> AskService:
    kb_service = KnowledgeBaseService()
    return AskService(kb_service, db)

@router.post("", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    ask_service: AskService = Depends(get_ask_service)
):
    """
    Ask a question to the Grounded RAG AI.
    It will answer ONLY using the retrieved knowledge base.
    """
    response = ask_service.ask(request.question, model_provider=request.model_provider)
    
    if "Error:" in response["answer"]:
        raise HTTPException(status_code=500, detail=response["answer"])
        
    return response
