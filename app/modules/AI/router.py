import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_tenant_user
from app.modules.AI.rag_service import get_rag_answer, semantic_search
from app.modules.AI.Langgraph.graph import build_graph
from app.modules.AI.Langgraph.memory import load_messages, save_messages
from app.modules.AI.schema import AssistantRequest, AssistantResponse

router = APIRouter(prefix="/ai", tags=["AI"])


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]


class SearchRequest(BaseModel):
    query: str


@router.post("/ask", response_model=AnswerResponse)
async def ask(
    payload: QuestionRequest,
    current_user=Depends(get_current_tenant_user),
):
    return await get_rag_answer(payload.question)


@router.post("/search")
async def search(
    payload: SearchRequest,
    current_user=Depends(get_current_tenant_user),
):
    return await semantic_search(payload.query)


@router.post("/assistant", response_model=AssistantResponse)
async def assistant(
    payload: AssistantRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_tenant_user),
):
    graph = build_graph(db)

    # Swagger/OpenAPI often sends the placeholder "string" unless user edits it.
    # Treat common placeholder/empty values as "no session provided".
    raw_session_id = (payload.session_id or "").strip()
    session_id = (
        raw_session_id
        if raw_session_id and raw_session_id.lower() != "string"
        else str(uuid.uuid4())
    )

    messages = await load_messages(db, session_id)

    # Save the user's message BEFORE invoking the graph so that if the
    # assistant errors out, the user turn is still recorded.
    await save_messages(db, session_id, "user", payload.query)

    result = await graph.ainvoke(
        {
            "question": payload.query,
            "session_id": session_id,
            "messages": messages,
        }
    )

    await save_messages(db, session_id, "assistant", result["answer"])

    return {
        "session_id": session_id,
        "answer": result["answer"],
    }