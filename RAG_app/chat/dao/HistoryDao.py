# 历史记录操作
from RAG_app.common.LoadMySQLConn import LoadMySQLConn
from RAG_app.chat.utils.CollectionConn import collection_conn


# 查询历史记录菜单
def query_history_menu(usersId):
    conn = LoadMySQLConn().conn
    cursor = conn.cursor()
    sql = "SELECT * FROM `history` WHERE parent_id=0 AND users_id=%s;"
    cursor.execute(sql, [usersId])
    results = cursor.fetchall()
    LoadMySQLConn().close_mysql_conn(cursor, conn)
    return results

# 根据会话id查询完整历史对话记录
def query_history_list(historyId):
    conn = LoadMySQLConn().conn
    cursor = conn.cursor()
    sql = "SELECT * FROM `history` WHERE history_id=%s or parent_id=%s ORDER BY history_id ASC;"
    cursor.execute(sql, [historyId, historyId])
    results = cursor.fetchall()
    LoadMySQLConn().close_mysql_conn(cursor, conn)
    return results

# 保存对话结果
def save_chat_result(saveResultEntity):
    conn = LoadMySQLConn().conn
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO history VALUES(NULL,%s,%s,%s,%s,now())"
        cursor.execute(sql, [
            saveResultEntity.usersId,
            saveResultEntity.question,
            saveResultEntity.answer,
            saveResultEntity.parentId
        ])
        conn.commit() # 提交事务，只有提交了才会生效【成功提交失败回滚】
        return cursor.lastrowid # 返回插入数据的id
    except Exception as e:
        print(e)
        conn.rollback() # 回滚事务
        raise 0
    finally:
        LoadMySQLConn().close_mysql_conn(cursor, conn)

# 根据会话id查询近5轮对话的内容
def query_short_history_list(historyId):
    conn = LoadMySQLConn().conn
    cursor = conn.cursor()
    sql = "SELECT * FROM `history` WHERE history_id=%s or parent_id=%s ORDER BY history_id DESC LIMIT 5;"
    cursor.execute(sql, [historyId, historyId])
    results = cursor.fetchall()
    LoadMySQLConn().close_mysql_conn(cursor, conn)
    return results

# 根据用户需求查询长期记忆
# def query_lang_history(question: str, usersId: int):
#     collection = collection_conn()
#     results = collection.query(
#         query_texts=[question],
#         n_results=3,
#         where={"user_id": str(usersId)}
#     )
#     # results = collection.get(include=["embeddings", "documents", "metadatas"])
#     # print(f"集合中的所有数据内容：{results}")
#     return results

# 删除会话历史记录
def delete_history(usersId, historyId):
    conn = LoadMySQLConn().conn
    cursor = conn.cursor()
    sql = "DELETE FROM `history` WHERE users_id = %s AND (history_id = %s OR parent_id = %s);"
    cursor.execute(sql, [usersId, historyId, historyId])
    conn.commit()
    LoadMySQLConn().close_mysql_conn(cursor, conn)
    return cursor.rowcount

# 在向量数据库中删除长期记忆会话历史记录
def delete_lang_history():
    collection = collection_conn()
    collection.delete(
        ids="059db8b3-079f-4134-a8f0-d786c2b20104"
    )
    print("删除成功")

if __name__ == "__main__":
    # print(query_short_history_list(49))
    q = "我叫什么？"
    # print(query_lang_history(q, 1))
    # query_lang_history(q, 1)
    # delete_history()