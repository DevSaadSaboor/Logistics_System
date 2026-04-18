# It handles:question -> retrieve docs -> send context to LLM  ->return answer
from dotenv import load_dotenv
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()

CONNECTION_STRING = "postgresql+psycopg2://postgres:1234@localhost:5432/logistics"

def get_rag_answer(question:str):
    embedding = OpenAIEmbeddings(model = "text-embedding-3-small")
    vector_store = PGVector(
        connection_string=CONNECTION_STRING, 
        embedding_function=embedding,         
        collection_name="logistics_docs_v3",
        use_jsonb=True 
    )
    retriever = vector_store.as_retriever(search_kwargs = {"k" : 5})
    docs = retriever.invoke(question)
    print("DOCS FOUND:")
    for doc in docs:
        print(doc.page_content)
    context = "\n".join([doc.page_content for doc in docs])
    model = ChatOpenAI(model = "gpt-4o-mini")

    prompt = ChatPromptTemplate.from_template("""
    You are a logistics company assistant.

    Use the context to answer the question clearly.
    If exact wording differs, infer the meaning logically.

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
    return response.content

# if __name__ == "__main__":
#     print(get_rag_answer("What is delivery SLA?"))