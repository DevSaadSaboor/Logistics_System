from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.AI.rag_service import get_rag_answer,semantic_search

router = APIRouter(prefix="/ai", tags=["AI"])

class QuestionRequest(BaseModel):
    question:str

class AnswerResponse(BaseModel):
    answer:str
    sources:list[str]
class SearchRequest(BaseModel):
    query: str


@router.post("/ask")
async def ask(payload: QuestionRequest):
    return get_rag_answer(payload.question)


@router.post("/search")
async def search(payload: SearchRequest):
    return semantic_search(payload.query)