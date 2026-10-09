from fastapi import FastAPI
from contextlib import asynccontextmanager
from RAG_app.users.controller.UsersController import users_router
from RAG_app.users.dao.UserDao import QueryUser
from fastapi.middleware.cors import CORSMiddleware
from RAG_app.chat.controller.ChatController import chat_router
from RAG_app.chat.controller.HistoryController import history_router
from RAG_app.chat.service.ChatService import ChatService
from RAG_app.chat.controller.ChatController import ticket_router
from RAG_app.chat.utils.HybridRetrieval import HybridRetrieval
from RAG_app.common.LoadRerankerModel import LoadRerankerModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.hybrid_retrieval = HybridRetrieval()
    app.state.query_user = QueryUser()
    app.state.chat_service = ChatService(app.state.hybrid_retrieval)
    LoadRerankerModel.load_reranker_model()

    print("成功加载了各个模型")

    yield
    del app.state.hybrid_retrieval
    del app.state.query_user
    del app.state.chat_service
    print("成功清除了各个模型")


app = FastAPI(lifespan = lifespan)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

#注册子路由
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(history_router, prefix="/history", tags=["history"])
app.include_router(ticket_router, prefix="/ticket", tags=["ticket"])





# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        reload=False
    )
