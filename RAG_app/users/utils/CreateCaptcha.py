"""
    验证码生成工具：只考虑数据验证码的生成
"""
import random

class CreateCapcha:
    def __init__(self):
        self.code = self.create_capcha()

    # 生成验证码
    @staticmethod
    def create_capcha():
        code = ""
        for i in range(4):
            code += str(int(random.random() * 10))
        return code
