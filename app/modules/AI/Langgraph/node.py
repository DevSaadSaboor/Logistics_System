from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.modules.shipments.repository import ShipmentRespository
from app.modules.AI.Langgraph.state import AgentState
from app.modules.AI.rag_service import semantic_search
from app.core.logging import logger
import re

llm = ChatOpenAI(model= "gpt-4o-mini", temperature=0)

def simple_rerank(query:str,docs):
    query_words = set(query.lower().split())
    def score(doc):
        content_words = set(doc["content"].lower().split())
        return len(query_words & content_words)
    return sorted(docs,key=score, reverse=True)

def classify_node(state:AgentState):
    question = state["question"].lower()

    if "shipment" in question or "track" in question or "delievery" in question:
        intent = "shipment"
    
    else:
        intent = "policy"
    
    logger.info("ai.intent.detected intent= %s", intent)

    return {"intent":intent}
def route_intent(state):
    return state["intent"]


async def shipment_retriever_node(state:AgentState,db):
    logger.info("ai_retrieve.shipment")
    query = state["question"]

    match = re.search(r"TRK-[A-Z0-9]+", query)
    tracking_number = match.group(0) if match else None 
          

    if not tracking_number:
            return {"context":"no tracking number in the question"}
        
    repo = ShipmentRespository(db)
    shipment = await repo.get_by_tracking_number(tracking_number)  

    if not shipment:
            return {"context": f"shipment not found with this tracking number {tracking_number}"}
    
    context = f"""
    Shipment Details:
    Tracking Number: {shipment.tracking_number}
    Status: {shipment.status}
    Origin: {shipment.origin}
    Destination: {shipment.destination}
    Weight: {shipment.weight}
    Recipient: {shipment.recipient_name}
    """
    return {"context": context}

async def policy_retrieve_node(state:AgentState,db):
    logger.info("ai.retreive.rag")
    query = (state.get("question") or "").lower()
    if "delay" in query or "late" in query:
        query +=   "shipment delay reasons"
        docs = semantic_search(query)
        context = "\n\n".join([
            doc["content"][:300]
            for doc in docs[:3]
        ])
        return {"context": context}
    # Default: still retrieve something useful for general policy questions.
    docs = semantic_search(query)
    context = "\n\n".join([doc["content"][:300] for doc in docs[:3]])
    return {"context": context or "No relevant policy context found."}
    

async def generate_node(state:AgentState):
    context = state.get("context") or ""
    question = state.get("question") or ""

    messages = [
        SystemMessage(
            content=(
                "You are a logistics AI assistant.\n\n"
                "Use provided context to answer clearly.\n\n"
                "If answer is not found, say:\n"
                "'I don't know based on company data.'"
            )
        ),
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion:\n{question}\n"
        ),
    ]

    response = await llm.ainvoke(messages)
    logger.info("ai.answer.generated")

    return {
        "answer": response.content
    }


