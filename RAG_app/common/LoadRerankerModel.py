import os
from FlagEmbedding import FlagReranker
from dotenv import load_dotenv

load_dotenv()


class LoadRerankerModel:
    _reranker_model = None

    @staticmethod
    def load_reranker_model():
        if LoadRerankerModel._reranker_model is None:
            LoadRerankerModel._reranker_model = FlagReranker(
                model_name_or_path=os.getenv("RERANKER_MODEL"),
                use_fp16=False
            )
        return LoadRerankerModel._reranker_model

