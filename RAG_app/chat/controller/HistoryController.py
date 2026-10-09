from RAG_app.chat.service import HistoryService
from pydantic import Field, BaseModel
from fastapi import APIRouter, Depends, Request
from RAG_app.users.utils.JwtUtil import get_current_user

history_router = APIRouter()

class SaveResultEntity(BaseModel):
    usersId: int = Field(..., description="用户id")
    question: str = Field(..., description="用户问题")
    answer: str = Field(..., description="AI回复")
    parentId: int = Field(..., description="对话保存哪个父级对话")

# 查询历史记录菜单
@history_router.get("/queryHistoryMenu/{usersId}")
def query_history_menu(usersId):
    return HistoryService.query_history_menu(usersId)

# 根据会话id查询完整历史对话记录
@history_router.get("/queryHistoryList/{historyId}")
def query_history_list(historyId: str):
    return HistoryService.query_history_list(int(historyId))

# 保存对话结果
@history_router.post("/saveChatResult")
def save_result(saveResultEntity: SaveResultEntity):
    return HistoryService.save_chat_result(saveResultEntity)

# 删除会话历史记录
@history_router.delete("/deleteHistory/{historyId}")
def delete_history(historyId: str, request: Request, current_user: dict = Depends(get_current_user)):
    email = current_user["email"]
    user = request.app.state.query_user.query_user(email)
    usersId = user[0]["users_id"]
    return HistoryService.delete_history(usersId, historyId)
