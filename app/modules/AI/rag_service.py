# It handles:question -> retrieve docs -> send context to LLM  ->return answer
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.modules.AI.vector_store import COLLECTION_NAME,create_vector_store
load_dotenv()

CONNECTION_STRING = os.getenv("SYNC_DATABASE_URL")

def get_rag_answer(question:str):
    embedding = OpenAIEmbeddings(model = "text-embedding-3-small")
    vector_store = PGVector(
    connection_string=CONNECTION_STRING,
    embedding_function=embedding,
    collection_name=COLLECTION_NAME,
    use_jsonb=True
    )
    retriever = vector_store.as_retriever(search_kwargs = {"k" : 3})
    docs = retriever.invoke(question)
    print("DOC COUNT:", len(docs))
    for doc in docs:
        print("DOC:", doc.page_content)

    # print("DOCS FOUND:")
    # for doc in docs:
    #     print(doc.page_content)
    context = "\n\n".join([doc.page_content for doc in docs])
    sources = []
    for doc in docs:
        first_line = doc.page_content.split("\n")[0].replace("###", "").strip()
        sources.append(first_line)
    model = ChatOpenAI(model = "gpt-4o-mini")

    prompt = ChatPromptTemplate.from_template("""
    You are a logistics company assistant.
    Use ONLY the provided context.
    If the answer is not in the context, reply exactly:
    "I don't know based on company policy."
    Context:
    {context}
    Question:
    {question}
    Answer:
    """)

    chain = prompt | model
    response = chain.invoke(
        {
        "context":context,
        "question": question
        }
    )
    
    return {
        "answer": response.content,
        "sources": list(set(sources))
    }
def semantic_search(query: str):

    vector_store = create_vector_store()

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

    docs = retriever.invoke(query)

    results = []

    for doc in docs:
        source = doc.page_content.split("\n")[0].replace("###", "").strip()

        results.append({
            "source": source,
            "content": doc.page_content
        })

    return results

# if __name__ == "__main__":
#     print(get_rag_answer("What is delivery SLA?"))