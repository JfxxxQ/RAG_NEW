"""
    查询数据库用户信息
"""

from RAG_app.common.LoadMySQLConn import LoadMySQLConn

class QueryUser:

    def query_user(self, email):
        conn = LoadMySQLConn().conn
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE email = %s"
        cursor.execute(sql, [email])
        results = cursor.fetchall()
        LoadMySQLConn.close_mysql_conn(cursor, conn)
        return results

if __name__ == "__main__":
    user_email = "2841549870@qq.com"
    print(QueryUser().query_user(user_email)[0]["nickname"])