"""
    用户创建账号
"""

from RAG_app.common.LoadMySQLConn import LoadMySQLConn
from RAG_app.common.LoadReidsConn import LoadRedisConn
from RAG_app.users.dao.UserDao import QueryUser
from RAG_app.users.utils.Password import hash_password


def register_count(email, password, nickname, captcha):
    conn = LoadRedisConn().conn
    redis_captcha = conn.get(email)
    if not redis_captcha:
        return {
            "code": 500,
            "msg": "验证码已过期",
            "data": None
        }
    if redis_captcha == captcha:
        try:
            password = hash_password(password)
            conn = LoadMySQLConn().conn
            cursor = conn.cursor()
            sql = "INSERT INTO users (email, password, nickname, create_time) VALUES (%s, %s, %s, NOW())"
            cursor.execute(sql, (email, password, nickname))
            conn.commit()
            results = QueryUser().query_user(email)
            # print("插入成功，新用户ID：", cursor.lastrowid)
            # print("插入成功，新用户ID：", results[0]["nickname"])
            # print("插入成功，新用户ID：", results[0]["users_id"])
            return {
                "code": 200,
                "msg": "注册成功",
                "data": {
                    "nickname": results[0]["nickname"],
                    "usersId": results[0]["users_id"]
                }
            }
        except Exception as e:
            print(f"注册失败：{e}")
            return {
                "code": 500,
                "msg": "注册失败",
                "data": None
            }
        finally:
            LoadMySQLConn.close_mysql_conn(cursor, conn)
    # print("验证码错误")
    return {
        "code": 500,
        "msg": "验证码错误",
        "data": None
    }


if __name__ == "__main__":
    register_count("123456789@qq.com", "123456", "test", "1234")
