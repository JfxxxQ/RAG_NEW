import pymysql
import os
from dotenv import load_dotenv
# 解析.env文件，获取内容，通过os.getenv(key)方法获取值
load_dotenv()

class LoadMySQLConn:
    def __init__(self):
        self.conn = self.load_mysql_conn()

    # 加载mysql连接
    @staticmethod
    def load_mysql_conn():
        return pymysql.connect(
            host=os.getenv('MYSQL_HOST'),  # 数据库服务器的ip
            port=int(os.getenv('MYSQL_PORT')),
            user=os.getenv('MYSQL_USER'),  # 连接账号
            password=os.getenv('MYSQL_PASSWORD'),  # 连接密码 --- root账户对应的密码
            database=os.getenv('MYSQL_DATABASE'),  # 操作的数据库名称
            charset='utf8mb4',  # 字符编码
            cursorclass=pymysql.cursors.DictCursor  # 查询结果以字典的格式返回
        )

    # 关闭mysql连接
    @staticmethod
    def close_mysql_conn(cursor, conn):
        cursor.close()
        conn.close()