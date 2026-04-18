# Load raw company knowledge from source files.
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


DOCS_FILE = Path(__file__).resolve().parents[3] / "data" / "logistics_docs.txt"


def load_documents():
    loader = TextLoader(str(DOCS_FILE))
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