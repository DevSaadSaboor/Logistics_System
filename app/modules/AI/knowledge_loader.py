# Load raw company knowledge from source files.
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents():
    loader = TextLoader("data/logistics_docs.txt")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50
    )
    chunks = splitter.split_documents(docs)
    return chunks

# if __name__ == "__main__":
#     chunks = load_documents()

#     for i, chunk in enumerate(chunks):
#         print(f"\n--- Chunk {i} ---")
#         print(chunk.page_content)