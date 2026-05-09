from langchain_openai import ChatOpenAI
from app.modules.AI.rag_service import get_rag_answer
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
    query = query.lower()
    if "delay" in query or "late" in query:
        query +=   "shipment delay reasons"
        docs = semantic_search(query)
        context = "\n\n".join([
            doc["context"][:300]
            for doc in docs[:3]
        ])
        return {"context": context}
    

async def generate_node(state:AgentState):
    messages = state['messages']
    messages.append({
    "role": "system",
    "content": """
    You are a logistics AI assistant.

    Use provided context to answer clearly.

    If answer is not found, say:
    'I don't know based on company data.'
    """
    })
    messages.append({
         "role": "user",
         "content": f"""
    Context:
    {state['context']}
    question:
    {state['question']}
    """
    })
    
    response = await llm.ainvoke(messages)
    logger.info("ai.answer.generated")

    return {
        "answer": response.content
    }


