import os
from pathlib import Path
from RAG_app.common.LoadChromaConn import LoadChromaConn

chroma_data_path = os.path.join(Path(os.path.dirname(__file__)).parent, "chroma_data", "new_data")
collection_name = "new"
vector = LoadChromaConn().conn

results = vector.get(where_document={"$contains": "国奥男篮争霸赛"})
print(results)