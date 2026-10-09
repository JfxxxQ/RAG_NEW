import jieba
from rank_bm25 import BM25Okapi
from RAG_app.common.LoadChromaConn import LoadChromaConn
from langchain_core.documents import Document

# 定义停顿词（忽略的语气词）
STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
    "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
    "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它", "们",
    "这个", "那个", "什么", "哪", "怎么", "吗", "呢", "吧", "啊", "哦",
    "还", "被", "把", "让", "从", "对", "与", "但", "而", "或", "所",
    "为", "以", "及", "可", "可以", "能", "能够", "应该", "需要", "已经",
    "虽然", "如果", "因为", "所以", "只是", "还是", "不过", "然后",
    "之", "其", "中", "等", "等等", "即", "使", "向", "将", "按", "当",
    "于", "由", "比", "除了", "关于", "以及", "并且", "此外", "另外",
    "过", "着", "来", "去", "做", "作", "像", "如", "如同", "由于",
])

class HybridRetrieval:
    def __init__(self):
        self.bm25, self.bm25_docs = self.build_bm25_index()


    # 定义分词函数
    def tokenize(self, text):
        return [item for item in list(jieba.cut(text))
                if item not in STOP_WORDS and len(item.strip()) > 0]

    def build_bm25_index(self):
        # 向量数据库连接
        vector = LoadChromaConn.load_chroma_conn()
        # 获取所有的docs
        all_data = vector.get()
        ids = all_data['ids']
        documents = all_data['documents']
        metadatas = all_data['metadatas']
        # 处理数据的格式为List[Document]
        bm25_docs = [Document(id=ids[index], page_content=documents[index], metadata=metadatas[index])
                     for index in range(len(ids))]

        # 分词处理
        tokenizer_results = [self.tokenize(doc) for doc in documents]
        # 创建BM25对象
        bm25 = BM25Okapi(tokenizer_results)
        return bm25, bm25_docs

    def bm25_retriever(self, question):
        bm25, bm25_docs = self.build_bm25_index()
        # question = "2014年洲际国奥男篮争霸赛发生了什么？"
        # 问题分词处理
        question_tokens = self.tokenize(question)
        # 调用get_scores方法计算结果
        bm25_scores = bm25.get_scores(question_tokens)
        # 排序筛选top10
        bm25_top10_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:10]
        # 取出数据
        bm25_results_docs = [bm25_docs[index] for index in bm25_top10_indices] # List[Document]
        # print("BM25检索结果：")
        # for index, item in enumerate(bm25_results_docs, start=1):
        #     print(f"第{index}个结果：{item.page_content}")
        # 向量检索
        # 检索器
        return bm25_results_docs

    def rrf_retriever(self, question: str):
        vector = LoadChromaConn.load_chroma_conn()
        vector_retriever = vector.as_retriever(search_kwargs={"k": 10})
        vector_results_docs = vector_retriever.invoke(question) # List[Document]
        # print("向量检索结果：")
        # for index, item in enumerate(vector_results_docs, start=1):
        #     print(f"第{index}个结果：{item.page_content}")

        """
            rrf 融合：不考虑分支问题，只考虑排名问题 --- 公式：rrf = 求和 1 / (rank + 60)
        """
        """
            先处理向量检索结果、在处理BM25检索结果 --- 结果以id作为key，rrf计算结果作为value
            核心思路：id相同、key相同，结果就相加、否则单独存入
        """
        scores_list = {} # rrf分数
        docs_list = {} # 文档
        for index, item in enumerate(vector_results_docs, start=1):
            scores_list[item.id] = 1 / (index + 60) # rrf分数
            docs_list[item.id] = item   # 文档

        for index, item in enumerate(self.bm25_retriever(question), start=1):
            scores_list[item.id] = scores_list.get(item.id, 0) + 1 / (index + 60) # rrf分数
            docs_list[item.id] = item   # 文档

        # print("rrf融合检索结果：")
        # for index, (key, value) in enumerate(scores_list.items(), start=1):
        #     print(f"第{index}个结果：{docs_list[key].page_content}，分数：{value}")
        # print("================================================")

        # 取出rrf融合检索中的top10
        top10_docs = sorted(scores_list.items(), key=lambda item: item[1], reverse=True)[:10]
        return [docs_list[key] for key, value in top10_docs]


if __name__ == "__main__":
    q = HybridRetrieval().rrf_retriever("2014年洲际国奥男篮争霸赛发生了什么？")
    for item in q:
        print(item)
