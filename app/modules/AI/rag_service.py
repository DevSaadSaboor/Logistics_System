# Handles: question -> retrieve docs -> send context to LLM -> return answer
import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.core.logging import logger
from app.modules.AI.vector_store import COLLECTION_NAME, create_vector_store

load_dotenv(override=True)

CONNECTION_STRING = os.getenv("SYNC_DATABASE_URL")


# ---------------------------------------------------------------------------
# Singletons — created once on first use, reused for every request.
# Avoids opening a new DB connection and re-loading the embedding model
# on every call to /ask or /search.
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model="text-embedding-3-small")


@lru_cache(maxsize=1)
def _get_vector_store() -> PGVector:
    return PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=_get_embeddings(),
        collection_name=COLLECTION_NAME,
        use_jsonb=True,
    )


@lru_cache(maxsize=1)
def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4o-mini")


# ---------------------------------------------------------------------------
# RAG answer
# ---------------------------------------------------------------------------

async def get_rag_answer(question: str) -> dict:
    vector_store = _get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = await retriever.ainvoke(question)

    logger.debug("rag.retrieved doc_count=%d question=%r", len(docs), question[:80])
    for i, doc in enumerate(docs):
        logger.debug("rag.doc[%d] content=%r", i, doc.page_content[:120])

    context = "\n\n".join(doc.page_content for doc in docs)
    sources = list({
        doc.page_content.split("\n")[0].replace("###", "").strip()
        for doc in docs
    })

    prompt = ChatPromptTemplate.from_template(
        "You are a logistics company assistant.\n"
        "Use ONLY the provided context.\n"
        "If the answer is not in the context, reply exactly:\n"
        "\"I don't know based on company policy.\"\n\n"
        "Context:\n{context}\n\n"
        "Question:\n{question}\n\n"
        "Answer:"
    )

    chain = prompt | _get_llm()
    response = await chain.ainvoke({"context": context, "question": question})

    return {
        "answer": response.content,
        "sources": sources,
    }


# ---------------------------------------------------------------------------
# Semantic / MMR search
# ---------------------------------------------------------------------------

async def semantic_search(query: str) -> list[dict]:
    vector_store = _get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 10},
    )
    docs = await retriever.ainvoke(query)

    logger.debug("rag.search doc_count=%d query=%r", len(docs), query[:80])

    return [
        {
            "source": doc.page_content.split("\n")[0].replace("###", "").strip(),
            "content": doc.page_content,
        }
        for doc in docs
    ]