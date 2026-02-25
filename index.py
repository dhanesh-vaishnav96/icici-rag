from pathlib import Path

# Document loader
from langchain_community.document_loaders import PyPDFLoader

# Text splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embedding
from langchain_huggingface import HuggingFaceEmbeddings

# Qdrant
from langchain_qdrant import QdrantVectorStore

# Config
from config import QDRANT_PATH, COLLECTION_NAME



pdf_path = Path(__file__).parent / "icic.pdf"

# Debug check (prevents file error crash)
if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found at {pdf_path}")

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()

print(f"✅ Loaded {len(docs)} pages")



text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(docs)

print(f"✅ Created {len(chunks)} chunks")



embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)



print(f"🔗 Qdrant Path: {QDRANT_PATH}")
print(f"📦 Collection: {COLLECTION_NAME}")


vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    path=QDRANT_PATH,
    collection_name=COLLECTION_NAME
)

print("✅ Indexing Complete in Qdrant Cloud.")