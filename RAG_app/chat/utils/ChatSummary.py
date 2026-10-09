from RAG_app.common.LoadModel import LoadModel
from RAG_app.chat.dao.SummaryDao import SummaryMemory
from RAG_app.chat.dao.HistoryDao import query_short_history_list

def chat_summary(session_id, historyId):
    llm = LoadModel().llm
    history = SummaryMemory().load_memory(historyId)
    short_term = query_short_history_list(historyId)
    short_list = []
    for item in short_term:
        short_list.append(
            {"role": "user", "content": item["question"]},
        )
        short_list.append(
            {"role": "assistant", "content": item["answer"]}
        )
    summary_prompt = f"""
             一: 你是一个对话摘要助手
              你的任务：根据【历史摘要】和【最近聊天记录】生成新的摘要。
              【历史摘要】：{history}
              【最近聊天记录】：{short_list}
              要求：
              1、保留重要信息
              2、去掉闲聊内容
              3、避免重复
              4、控制在200字以内
              5、使用第三人称描述
              6、只返回新的摘要
              7、如果历史摘要和最近聊天记录为没有的时候，则返回0
        """
    summary = llm.invoke(summary_prompt).content
    if summary != "0":
        SummaryMemory().add_memory(session_id, summary)
    return ""

if __name__ == "__main__":
    print(chat_summary(1, 56))