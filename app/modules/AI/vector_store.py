# Connect docs to the vector database.
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from app.modules.AI.knowledge_loader import load_documents
from dotenv import load_dotenv
load_dotenv()


CONNECTION_STRING = "postgresql+psycopg2://postgres:1234@localhost:5432/logistics"

def create_vector_store():
    embedding  = OpenAIEmbeddings(
        model="text-embedding-3-small",
    )
    docments = load_documents()

    vector_store = PGVector.from_documents(
        documents=docments,
        embedding=embedding,
        connection_string = CONNECTION_STRING,
        collection_name="logictics_docs"
    )
    return vector_store

# if __name__ == "__main__":
#     create_vector_store()
#     print("Vector store created successfully!")