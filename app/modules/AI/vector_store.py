# Connect docs to the vector database.
import os
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from app.modules.AI.knowledge_loader import load_documents
from dotenv import load_dotenv
load_dotenv(override=True)


CONNECTION_STRING = os.getenv("SYNC_DATABASE_URL")
COLLECTION_NAME = "logistics_docs"

def create_vector_store():
   embedding = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )

   return PGVector(
    connection_string=CONNECTION_STRING,
    embedding_function=embedding,
    collection_name=COLLECTION_NAME,
    use_jsonb=True
    )

    # vector_store.add_documents(documents)
    # print(f"Vector store created successfully with {len(documents)} chunks.")


def ensure_vector_store_initialized():
    """Ingest RAG docs when enabled. Skipped in production unless INIT_VECTOR_STORE=true."""
    app_env = os.getenv("APP_ENV", "").strip().lower()
    init_flag = os.getenv("INIT_VECTOR_STORE", "").strip().lower()
    if app_env == "production" and init_flag not in ("1", "true", "yes"):
        return
    if not os.getenv("OPENAI_API_KEY", "").strip():
        return
    if not CONNECTION_STRING:
        return

    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embedding,
        collection_name=COLLECTION_NAME,
        use_jsonb=True,
    )

    existing_docs = vector_store.similarity_search("policy", k=1)
    if existing_docs:
        # print("Vector store already initialized.")
        return

    documents = load_documents()
    if not documents:
        # print("No documents found to ingest.")
        return

    vector_store.add_documents(documents)
    # print(f"Vector store initialized with {len(documents)} chunks.")

# if __name__ == "__main__":
#     create_vector_store()
#     print("Vector store created successfully!")