"""
    负责发送验证码
"""

import os
from dotenv import load_dotenv
from RAG_app.users.utils.CreateCaptcha import CreateCapcha
from email.mime.text import MIMEText
import smtplib
from RAG_app.common.LoadReidsConn import LoadRedisConn


load_dotenv()


def send_captcha(email):
    send_email = os.getenv("SEND_EMAIL") # 发送人信息
    send_email_code = os.getenv("send_email_code") # 授权码信息
    subject = "欢迎使用新闻回溯问答助手" # 邮件主题
    code = CreateCapcha().code # 生成验证码
    content = f"验证码：{code}，过期时间为60s，转给他人将导致个人信息泄露，如非本人操作请忽略。"
    message = MIMEText(content, "plain", "utf-8")
    message["From"] = send_email
    message["To"] = email
    message["Subject"] = subject
    # 连接QQ邮箱服务器
    smtp_server = os.getenv("SMTP_SERVER")  # 邮箱服务器地址
    smtp_port = int(os.getenv("SMTP_PORT"))  # 邮件服务器端口
    smtp = smtplib.SMTP(smtp_server, smtp_port)  # 创建邮件发送实例
    smtp.starttls()  # 启动TLS加密 --- TLS对应的端口是587
    smtp.login(send_email, send_email_code)  # 校验发件人信息
    smtp.sendmail(send_email, email, message.as_string())  # 发送邮件
    smtp.quit()  # 关闭邮件连接
    # 把验证码存入数据库
    try:
        redis_conn = LoadRedisConn().conn
        redis_conn.setex(email, 60, code) # 存储数据
        LoadRedisConn.close_redis_conn(redis_conn)
        return {
            "code": 200,
            "msg": "验证码已发送",
            "data": None
        }
    except Exception as e:
        print(f"验证码发送失败：{e}")
        return {
            "code": 500,
            "msg": "验证码发送失败",
            "data": None
        }

if __name__ == "__main__":
    send_captcha("2841549870@qq.com")
