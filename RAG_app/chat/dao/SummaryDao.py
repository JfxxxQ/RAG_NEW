"""
    摘要记忆数据库连接
"""
from RAG_app.pggresql.pggresql_pool import pool

class SummaryMemory:

    def __init__(self):
        self.pool = pool
    #添加记忆
    def add_memory(self,session_id,summary):
      with self.pool.connection() as con:
          with con.cursor() as cursor:
              sql = f"insert into conversation_summary (session_id,summary) VALUES('{session_id}','{summary}') on conflict (session_id) do UPDATE  set summary = EXCLUDED.summary, update_time = NOW(),create_time = NOW()"
              #执行sql
              cursor.execute(sql)
              #事务提交
              con.commit()
    #查询记忆
    def load_memory(self,session_id):
        with self.pool.connection() as con:
            with con.cursor() as cursor:
                sql = f"select summary from  conversation_summary where session_id='{session_id}' "
                # 执行sql
                cursor.execute(sql)
                # 获取结果
                rs = cursor.fetchone()
                if rs:
                    return rs[0]
                else:
                    return ""

    def delete_memory(self, session_id):
        with self.pool.connection() as con:
            with con.cursor() as cursor:
                sql = f"delete from conversation_summary where session_id='{session_id}' "
                # 执行sql
                cursor.execute(sql)
                # 事务提交
                con.commit()