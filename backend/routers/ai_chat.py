from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import AIChatRequest, AIChatResponse
from backend.services.ai_chat_service import AIChatService

router = APIRouter(prefix="/api/ai-chat", tags=["AI Conversational Assistant"])

@router.post("", response_model=AIChatResponse, summary="Ask OmniPulse AI a natural language question about live platform data")
def ask_ai(req: AIChatRequest, db: Session = Depends(get_db)):
    return AIChatService.answer_query(db, req.query)
