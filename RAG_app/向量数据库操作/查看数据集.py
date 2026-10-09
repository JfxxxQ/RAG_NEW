import chromadb

client = chromadb.PersistentClient(path="../chroma_data/lang_memory_data")
collections = client.list_collections()

"""
    获取所有的集合
"""

print(collections)