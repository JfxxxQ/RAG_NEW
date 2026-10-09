import chromadb
import os
from dotenv import load_dotenv
load_dotenv()

def collection_conn():
    client = chromadb.PersistentClient(path=os.getenv("CHROMA_MEMORY_PATH"))
    collection = client.get_collection(name=os.getenv("MEMORY_COLLECTION_NAME"))
    return collection