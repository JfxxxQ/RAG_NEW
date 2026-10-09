from RAG_app.chat.dao import HistoryDao
from RAG_app.chat.utils.ChatSummary import chat_summary
from RAG_app.chat.dao.SummaryDao import SummaryMemory

# 查询历史记录菜单
def query_history_menu(usersId):
    results = HistoryDao.query_history_menu(usersId)
    # 存储历史记录的列表
    data = []
    for item in results:
        data.append(
            {
                "historyId": item['history_id'],
                'question': item['question'],
                'answer': item['answer'],
                'createTime': item['create_time'].strftime('%Y-%m-%d %H:%M:%S')
            }
        )
    return {
        "code": 200,
        "msg": "查询成功",
        "data": data
    }

# 根据会话id查询完整历史对话记录
def query_history_list(historyId):
    results = HistoryDao.query_history_list(historyId)
    data = []
    for item in results:
        # 添加用户问题
        data.append({
            "role": "user",
            "content": item['question']
        })
        # 添加AI回答
        data.append({
            "role": "assistant",
            "content": item['answer']
        })
    return {
        "code": 200,
        "msg": "查询成功",
        "data": data
    }

# 保存对话结果
def save_chat_result(saveResultEntity):
    # save_judge = chroma_save_judge(saveResultEntity.question, saveResultEntity.answer)
    # if save_judge:
    #     chroma_save_data(saveResultEntity.usersId, saveResultEntity.question, saveResultEntity.answer)
    results = HistoryDao.save_chat_result(saveResultEntity)
    # 聊天摘要
    if saveResultEntity.parentId == 0:
        session_id = results
    else:
        session_id = saveResultEntity.parentId
    chat_summary(str(session_id), saveResultEntity.parentId)
    if results > 0:
        return {
            "code": 200,
            "msg": "保存成功",
            "data": results
        }
    else:
        return {
            "code": 500,
            "msg": "保存失败",
            "data": None
        }


# 删除历史记录
def delete_history(usersId, historyId):
    results = HistoryDao.delete_history(usersId, historyId)
    SummaryMemory().delete_memory(str(historyId))
    if results > 0:
        return {
            "code": 200,
            "msg": "删除成功",
            "data": results
        }
    else:
        return {
            "code": 500,
            "msg": "删除失败",
            "data": None
        }



if __name__ == "__main__":
    print(query_history_list(49))
