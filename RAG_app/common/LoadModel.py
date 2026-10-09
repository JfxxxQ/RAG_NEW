from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv
load_dotenv()



class LoadModel:
    """
        初始化方法：目的是加载各个模型
    """
    def __init__(self):
        self.llm = self.load_llm()
        self.local_llm = self.load_local_llm()

    # 加载大模型
    @staticmethod
    def load_llm():
        return ChatOpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model=os.getenv("LLM_NAME"),
            streaming=True,
        )

    # 加载本地大模型
    @staticmethod
    def load_local_llm():
        return ChatOllama(
            base_url=os.getenv("LOCAL_URL"),
            model=os.getenv("LOCAL_LLM_NAME")
        )

if __name__ == "__main__":
    model = LoadModel.load_local_llm()
    res = model.invoke(input="你好")
    print(res)