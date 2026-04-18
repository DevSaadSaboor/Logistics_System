from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.AI.rag_service import get_rag_answer

router = APIRouter(prefix="/ai", tags=["AI"])

class QuestionRequest(BaseModel):
    question:str

class AnswerResponse(BaseModel):
    answer:str


@router.post("/ask",response_model=AnswerResponse)

async def ask_question(payload:QuestionRequest):
    answer = get_rag_answer(payload.question)
    return{"answer":answer}
