"""
    判断用户对话是否需要存入向量数据库进行长期记忆
"""
from RAG_app.common.LoadModel import LoadModel
from RAG_app.chat.utils.CollectionConn import collection_conn
import json
import uuid
import time



def chroma_save_judge(question, answer):
    local_model = LoadModel().local_llm
    prompt = f"""
            你是一个判断对话是否需要长期记忆的助手。
            请判断下面这段对话是否包含值得长期记忆的信息（如用户的偏好、身份、重要事件、长期目标等）。
            只输出 True 或 False。
            
            对话：
            用户：{question}
            助手：{answer}
    """
    return local_model.invoke(prompt).content

def chroma_save_data(user_id: int, question: str, answer: str):
    collection = collection_conn()
    llm = LoadModel().llm
    summary_prompt = f"""
            你是一个长期记忆存储助手，需要从对话中提取值得长期记忆的信息，并以 JSON 格式输出。
            请阅读下面这轮对话：
            用户：{question}
            助手：{answer}
            要求：
            1. 提取一句话摘要，概括这轮对话中最值得长期记住的信息。
            2. 提取关键实体，包括人物、地点、项目、组织、产品、时间等。
            3. 判断信息类别，只能从以下四项中选择一个：偏好、事实、事件、目标。
            4. 评估重要性，范围为 1-10，10 表示最重要。
            5. 只输出 JSON，不要输出解释、Markdown 代码块或多余文字。
            输出格式：
            {{
              "summary": "一句话摘要",
              "entities": ["人物", "地点", "项目名"],
              "category": "偏好/事实/事件/目标",
              "importance": 1
            }}
    """
    summary = json.loads(llm.invoke(summary_prompt).content)
    # 存入摘要记忆
    collection.add(
        ids=[str(uuid.uuid4())],
        documents=[summary["summary"]],
        metadatas=[{
            "user_id": str(user_id),
            "entities": ",".join(summary["entities"]),
            "category": summary["category"],
            "importance": summary["importance"],
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }]
    )

if __name__ == "__main__":
    q = "你好，我叫jfxxx"
    a = "好的jfxxx，我是coco助手，有问题可以问我"
    q1 = "你好，今天天气不错"
    a1 = "今天天气不错，想去哪里玩呢？"
    # print(chroma_save_judge(q, a))
    # print(chroma_save_judge(q1, a1))
    # print(chroma_save_data(1, q, a))