"""
    把召回内容进行重排序，返回排序后的内容
"""
from RAG_app.chat.utils.Print_log import print_log
from RAG_app.common.LoadRerankerModel import LoadRerankerModel

# 模块级单例
_reranker_model = None

def _get_reranker():
    global _reranker_model
    if _reranker_model is None:
        _reranker_model = LoadRerankerModel.load_reranker_model()
    return _reranker_model

def reranker_util(docs_dict: dict):
    question = docs_dict["question"]
    docs = docs_dict["docs"]
    # 加载重排序模型
    reranker_model = _get_reranker()
    # 打印召回的结果
    print_log(title="召回的结果", docs=docs)
    print("===========================================")
    # 构造QA对
    data = []
    for doc in docs:
        data.append(
            (question, doc.page_content)
        )
    reranker_scores = reranker_model.compute_score(data)
    # 分数排序
    index_docs = [i for i in range(len(reranker_scores))]
    reranker_docs = [docs[i] for i in sorted(index_docs, key=lambda x: reranker_scores[x], reverse=True)][:3]
    print_log(title="重排序后的结果", docs=reranker_docs)
    return reranker_docs