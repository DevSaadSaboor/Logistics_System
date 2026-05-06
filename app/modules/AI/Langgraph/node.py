from langchain_openai import ChatOpenAI
from app.modules.AI.rag_service import get_rag_answer
from app.modules.shipments.repository import ShipmentRespository
from app.modules.AI.Langgraph.state import AgentState
from app.modules.AI.rag_service import semantic_search
from app.core.logging import logger

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


async def retriever_node(state:AgentState,db):
    intent = state["intent"]
    query = state["question"]

    if intent == "shipment":
        logger.info("ai_retrieve.shipment")
        import re
        match = re.search(r"TRK-[A-Z0-9]+", query)
        tracking_number = match.group(0) if match else None 
        print("QUESTION:", query)
        print("TRACKING:", tracking_number)
          

        if not tracking_number:
            return {
                "context":"no tracking number in the question"
            }
        
        repo = ShipmentRespository(db)
        shipment = await repo.get_by_tracking_number(tracking_number)
        print("SHIPMENT:", shipment)  

        if not shipment:
            return {
                "context": f"shipment not found with this tracking number {tracking_number}"
            }
        context = {
            f"""
        Shipment Details
        Tracking Number : {shipment.tracking_number}
        Status: {shipment.status}
        origin: {shipment.origin}
        Destination: {shipment.destination}
        Weight: {shipment.weight}
        Receipent: {shipment.recipient_name}
        """
        }
        
        return {
            "context": context
        }
    else:
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
    context = state["context"]
    question = state["question"]

    response =  llm.invoke([{
    "role": "system",
    "content": f"""
    You are a logistics AI assistant.

    If shipment data is provided, explain it clearly to the user.
    If policy data is provided, answer based on it.

    If answer is not found, say:
    "I don't know based on company data."
    """},
    {
    "role": "user",
    "content": f"""
    Context:
    {context}
    Question:    
    {question}
    """}
    ])

    logger.info("ai.answer.generate")
    return {"answer": response.content}


