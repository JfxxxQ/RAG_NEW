import redis
import os
from dotenv import load_dotenv
# 解析.env文件，获取内容，通过os.getenv(key)方法获取值
load_dotenv()

class LoadRedisConn:
    def __init__(self):
        self.conn = self.load_redis_conn()

    # 加载redis连接
    @staticmethod
    def load_redis_conn():
        return redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            db=int(os.getenv('REDIS_DB')),
            decode_responses=True # 解码响应结果为字符串，否则是字节
        )

    # 关闭redis连接
    @staticmethod
    def close_redis_conn(conn):
        conn.close()