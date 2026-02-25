import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_PATH = "local_qdrant"
COLLECTION_NAME = "learning_rag"
