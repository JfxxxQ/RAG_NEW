from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma

load_dotenv()


class LoadChromaConn:
    _get_chroma_conn = None
    _embedding_model = None

    @staticmethod
    def load_embedding_model():
        if LoadChromaConn._embedding_model is None:
            LoadChromaConn._embedding_model = HuggingFaceEmbeddings(
                model_name=os.getenv("EMBEDDING_MODEL"),
                model_kwargs={
                    "device": "cpu",
                    "local_files_only": True
                }
            )
        return LoadChromaConn._embedding_model


    # 加载向量数据库连接对象
    @staticmethod
    def load_chroma_conn():
        if LoadChromaConn._get_chroma_conn is None:
            LoadChromaConn._get_chroma_conn = Chroma(
                persist_directory=os.getenv("CHROMA_DATA_PATH"),
                collection_name=os.getenv("COLLECTION_NAME"),
                embedding_function=LoadChromaConn.load_embedding_model(),
            )
        return LoadChromaConn._get_chroma_conn

    # def load_memory_chroma_conn(self):
    #     return Chroma(
    #         persist_directory=os.getenv("CHROMA_MEMORY_PATH"),
    #         collection_name=os.getenv("MEMORY_COLLECTION_NAME"),
    #         embedding_function=self.embedding_model,
    #     )