from RAG_app.common.LoadModel import LoadModel
from RAG_app.common.LoadChromaConn import LoadChromaConn
from RAG_app.chat.utils.IntentRecognition import intent_recognition
from RAG_app.chat.dao.HistoryDao import query_short_history_list
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from RAG_app.chat.utils.RerankerUtil import reranker_util
from RAG_app.chat.dao.SummaryDao import SummaryMemory
from RAG_app.chat.utils.RewriteQuestion import re_question
# 输出解析器
from langchain_core.output_parsers import StrOutputParser


class ChatService:

    def __init__(self, retriever):
        self.llm = LoadModel().llm
        self.retriever = retriever
        self.vector = LoadChromaConn.load_chroma_conn()

    def chat(self, question, historyId: int):
        # 判断是否为新对话
        if historyId == 0:
            history_list = []
        else:
            history_data = query_short_history_list(historyId)
            history_list = []
            for item in history_data:
                history_list.append(
                    {"role": "user", "content": item["question"]},
                )
                history_list.append(
                    {"role": "assistant", "content": item["answer"]}
                )
            summary = SummaryMemory().load_memory(historyId)
            history_list.append(summary)
        intent = intent_recognition(question, history_list[-4:])
        rewritten_question = re_question(question, history_list)
        if intent == "news":
            # 与新闻相关
            qa_prompt = """
                你是一个基于知识库的AI助手。请根据RAG检索内容回答用户问题。
                规则：
                    - 仅基于提供的知识回答，不使用外部知识补充。
                    - 检索内容不足时，说明信息不足，不要猜测。
                    - 禁止直接复制粘贴参考资料原文，请用你自己的话进行总结提炼。
                    - 优先提炼关键答案，避免冗长解释。
                    - 保持回答自然、简洁、有帮助。
                    - 输出结果的时候，不允许输出根据提供的参考资料这样的内容
                    - 输出结果的时候，如果没有参考的上下文信息，请给出一个友好的回复信息
                    注意：回答时必须结合历史记录中的上下文理解当前问题的指代、省略或延续意图，不得忽略历史信息。
                历史记录：
                    {history}
                参考资料：
                    {context}
                问题：
                    {question}
                答案：
            """
            docs = self.retriever.rrf_retriever(rewritten_question)
            prompt = PromptTemplate(template=qa_prompt, input_variables=["history", "context", "question"])
            # 构造qa链
            qa_chan = (
                RunnableParallel({
                    "history": RunnableLambda(lambda _: history_list),
                    "context": RunnableLambda(lambda _: {
                        "docs": docs,
                        "question": rewritten_question
                    }) | RunnableLambda(reranker_util),
                    "question": RunnableLambda(lambda _: rewritten_question), # 传递问题走作为question的值 --- 透明传递
                })
                | prompt
                | self.llm
                | StrOutputParser()
            )
            # 执行
            for chunk in qa_chan.stream(rewritten_question):
                if chunk:
                    yield chunk

        else:
            # 与新闻不相关
            prompt = f"""你是一位温和、亲切、善于倾听的日常聊天助手。你的名字叫“小暖”（你可以根据实际情况改名）。
                    你不需要拘泥于任何资料或设定，请像一位真诚的朋友一样，用自然、温暖、口语化的语气和用户聊天。
                    在对话时，请遵循以下原则：
                    1. 自然地结合你自身的知识，以及下方提供的【历史对话记录】，理解用户当前问题中的指代、省略或延续意图。
                    2. 不要生硬地说“根据历史记录……”或“根据我的知识……”，而是把这些信息内化成你自己的记忆和想法，自然地融入对话。
                    3. 回答时以温和、共情、友善的语气为主，可以适当使用一些轻松的语气词，像朋友聊天一样。
                    4. 如果用户表达了负面情绪，请先给予理解和安慰，再温和地给出你的看法或建议。
                    5. 如果某件事你确实不知道，可以坦诚地说“这个我不太清楚呢”，也可以和用户一起探讨，不要编造事实。
                    6. 回答长度适中，不要写成冷冰冰的论文或报告，尽量像日常对话一样自然流畅。
                    【历史对话记录】
                    {history_list}
                    【当前问题】
                    {question}
                    现在，请以“coco”的身份，温和自然地回复用户：
            """
            for chunk in self.llm.stream(prompt):
                if chunk.content:
                    yield chunk.content


