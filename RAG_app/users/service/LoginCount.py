"""
    用户登录账号
"""
from RAG_app.common.LoadReidsConn import LoadRedisConn
from RAG_app.users.dao.UserDao import QueryUser
from RAG_app.users.utils.Password import verify_password


def email_login(email, captcha):
    # 查看redis数据库有没有验证码
    redis_conn = LoadRedisConn().conn
    redis_captcha = redis_conn.get(email)
    # 验证码不存在
    if not redis_captcha:
        print("验证码已过期")
        return {
           "code": 500,
           "msg": "验证码已过期",
           "data": None
        }
    # 比较验证码是否正确
    print("验证码正确")
    if redis_captcha == captcha:
        return {
            "code": 200,
            "msg": "登录成功",
            "data": None
        }
    print("验证码错误")
    return {
        "code": 500,
        "msg": "验证码错误",
        "data": None
    }

def password_login(email, password):
    results = QueryUser().query_user(email)[0]
    user_password = results["password"]
    if not user_password:
        return {
            "code": 500,
            "msg": "用户不存在",
            "data": None
        }
    hash_password = verify_password(password, user_password)
    if not hash_password:
        return {
            "code": 500,
            "msg": "密码错误",
            "data": None
        }
    return {
        "code": 200,
        "msg": "登录成功",
        "data": {
            "nickname": results["nickname"],
            "usersId": results["users_id"]
        }
    }

if __name__ == "__main__":
    email_login("2841549870@qq.com", "1234")