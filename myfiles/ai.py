"""Azure, embedding, chroma"""
import os

import chromadb
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

CHAT_MODEL = "gpt-5-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
PRO_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

client = OpenAI(
    api_key=os.environ["api_key"],
    base_url=os.environ["base_url"],
)

pro = chromadb.PersistentClient(path=PRO_PATH)


def collection(name):
    """Get or add collections"""
    return pro.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def embed(texts, batch_size=100):
    """Convert texts to vectors in batches to keep requests manageable."""
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        vectors.extend(item.embedding for item in response.data)
    return vectors