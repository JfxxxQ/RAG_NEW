import json
from fastapi import APIRouter, Request, Depends
from starlette.responses import StreamingResponse
from RAG_app.users.utils.JwtUtil import get_current_user
chat_router = APIRouter()
ticket_router = APIRouter()



# 聊天
@chat_router.get("/chat")
def chat(question: str, historyId: str, request: Request, current_user: dict = Depends(get_current_user)):
    def generator():
        try:
            for item in request.app.state.chat_service.chat(question, int(historyId)):
                yield f"data: {json.dumps({'content': item}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'content': '[DONE]'}, ensure_ascii=False)}\n\n"  # [DONE]结束标识
        except Exception as e:
            print(f"聊天流式异常：{e}")
            error_msg = str(e)
            yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'content': '[DONE]'}, ensure_ascii=False)}\n\n"
        finally:
            return ""

    return StreamingResponse(
        content=generator(),
        media_type="text/event-stream",
    )

