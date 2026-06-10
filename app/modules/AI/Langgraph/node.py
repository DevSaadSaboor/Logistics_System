from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.modules.shipments.repository import ShipmentRespository
from app.modules.AI.Langgraph.state import AgentState
from app.modules.AI.rag_service import semantic_search
from app.core.logging import logger
import re

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ---------------------------------------------------------------------------
# Intent classification
# ---------------------------------------------------------------------------

_SHIPMENT_KEYWORDS = {
    "shipment", "track", "tracking", "delivery", "deliver",
    "order", "package", "parcel", "status", "trk",
    "where is", "shipped", "dispatch",
}


def classify_node(state: AgentState):
    question = state["question"].lower()
    intent = (
        "shipment"
        if any(kw in question for kw in _SHIPMENT_KEYWORDS)
        else "policy"
    )
    logger.info("ai.intent.detected intent=%s", intent)
    return {"intent": intent}


def route_intent(state: AgentState):
    return state["intent"]


# ---------------------------------------------------------------------------
# Retrieval nodes
# ---------------------------------------------------------------------------

async def shipment_retriever_node(state: AgentState, db):
    logger.info("ai.retrieve.shipment")
    query = state["question"]

    match = re.search(r"TRK-[A-Z0-9]+", query, re.IGNORECASE)
    tracking_number = match.group(0).upper() if match else None

    if not tracking_number:
        return {"context": "No tracking number found in the question."}

    repo = ShipmentRespository(db)
    shipment = await repo.get_by_tracking_number(tracking_number)

    if not shipment:
        return {"context": f"No shipment found with tracking number {tracking_number}."}

    context = (
        f"Shipment Details:\n"
        f"  Tracking Number : {shipment.tracking_number}\n"
        f"  Status          : {shipment.status}\n"
        f"  Origin          : {shipment.origin}\n"
        f"  Destination     : {shipment.destination}\n"
        f"  Weight          : {shipment.weight}\n"
        f"  Recipient       : {shipment.recipient_name}\n"
    )
    return {"context": context}


async def policy_retrieve_node(state: AgentState, db):
    logger.info("ai.retrieve.rag")
    query = state.get("question") or ""
    lowered = query.lower()

    # Augment query for delay/late questions to improve retrieval recall
    if "delay" in lowered or "late" in lowered:
        query = query + " shipment delay reasons"

    # Bug fix: semantic_search is async — must be awaited
    docs = await semantic_search(query)

    context = "\n\n".join(doc["content"][:300] for doc in docs[:3])
    return {"context": context or "No relevant policy context found."}


# ---------------------------------------------------------------------------
# Generation node
# ---------------------------------------------------------------------------

async def generate_node(state: AgentState):
    context = state.get("context") or ""
    question = state.get("question") or ""
    history = state.get("messages") or []  # [{role, content}, ...]

    system = SystemMessage(
        content=(
            "You are a logistics AI assistant.\n\n"
            "Use the provided context to answer the user's question clearly and concisely.\n\n"
            "If the answer is not found in the context or conversation history, say:\n"
            "'I don't know based on company data.'"
        )
    )

    # Reconstruct conversation history as LangChain message objects
    history_messages = []
    for msg in history:
        role = (msg.get("role") or "").lower()
        content = msg.get("content") or ""
        if role == "user":
            history_messages.append(HumanMessage(content=content))
        elif role in ("assistant", "ai"):
            history_messages.append(AIMessage(content=content))

    # Current turn
    current = HumanMessage(
        content=f"Context:\n{context}\n\nQuestion:\n{question}"
    )

    messages = [system] + history_messages + [current]

    response = await llm.ainvoke(messages)
    logger.info("ai.answer.generated")
    return {"answer": response.content}
