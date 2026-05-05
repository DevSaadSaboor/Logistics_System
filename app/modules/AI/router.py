from fastapi import APIRouter,Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.AI.rag_service import get_rag_answer,semantic_search
from app.modules.AI.Langgraph.graph import build_graph
from app.modules.AI.schema import AssistantRequest, AssistantResponse
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

@router.post("/assistant", response_model=AssistantResponse)
async def assistant(payload:AssistantRequest , db:AsyncSession = Depends(get_db)):
    graph = build_graph(db)

    result = await graph.ainvoke({
        "question":payload.query,
        "session_id": payload.session_id or "default",
        "messages": []
    })

    return {
        "answer": result["answer"]
    }