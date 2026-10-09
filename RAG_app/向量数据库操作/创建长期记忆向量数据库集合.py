import chromadb
from RAG_app.common.LoadChromaConn import LoadChromaConn


def get_chromadb_conn(path):
    return chromadb.PersistentClient(path = path)

embedding_functions = LoadChromaConn().embedding_model
vector = get_chromadb_conn(path="../chroma_data/lang_memory_data")
"""
    创建集合
"""
collection = vector.create_collection(
    name="lang_memory", # 集合名称
    embedding_function=embedding_functions, # 嵌入函数
)

print(collection)