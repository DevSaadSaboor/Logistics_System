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
    query = state["question"].lower()
    if "delay" in query or "late" in query:
        query += " shipment delay reason"
    docs = semantic_search(query)
    docs = simple_rerank(query,docs)
    context = "\n\n".join([
        doc["content"][:300]
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

    Use the provided context to answer the question.

    If the answer is partially available, answer as best as possible.
    If completely missing, say:
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


