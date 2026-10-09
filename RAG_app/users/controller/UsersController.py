import json
from fastapi import APIRouter
from pydantic import Field, BaseModel
from RAG_app.users.utils.SendCaptcha import send_captcha
from RAG_app.users.service import LoginCount, RegisterCount
from fastapi import Request
from RAG_app.users.utils.JwtUtil import create_token


users_router = APIRouter()

class LoginUsers(BaseModel):
    email: str = Field(..., description="邮箱号")
    captcha: str = Field(..., description="验证码")

class RegisterUsers(BaseModel):
    email: str = Field(..., description="创建的邮箱号")
    password: str = Field(..., description="创建账号的密码")
    nickname: str = Field(..., description="账号昵称")
    captcha: str = Field(..., description="验证码")

class PasswordLoginUsers(BaseModel):
    email: str = Field(..., description="邮箱号")
    password: str = Field(..., description="密码")

@users_router.get("/loginSendCaptcha")
def login_send_captcha(email: str, req: Request):
    user = req.app.state.query_user.query_user(email)
    if not user:
        return {
            "code": 400,
            "msg": "用户不存在，请先注册",
            "data": None
        }
    send_captcha(email)
    return {
        "code": 200,
        "msg": "验证码已发送",
        "data": {
            "nickname": user[0]["nickname"],
            "usersId": user[0]["users_id"]
        }
    }

@users_router.get("/registerSendCaptcha")
def register_send_captcha(email: str, req: Request):
    user = req.app.state.query_user.query_user(email)
    if user:
        return {
            "code": 400,
            "msg": "用户已存在，请直接登录",
            "data": None
        }
    send_captcha(email)
    return {
        "code": 200,
        "msg": "验证码已发送",
        "data": None
    }

@users_router.post("/login")
def login(user: LoginUsers):
    result = LoginCount.email_login(user.email, user.captcha)
    # 登录成功
    if result["code"] == 200:
        # 生成token
        token = create_token({"email": user.email})
        result["data"] = token
    return result

@users_router.post("/passwordLogin")
def password_login(user: PasswordLoginUsers):
    result = LoginCount.password_login(user.email, user.password)
    if result["code"] == 200:
        # 生成token
        token = create_token({"email": user.email})
        result["data"]["token"] = token
    return result


@users_router.post("/register")
def register(user: RegisterUsers):
    result = RegisterCount.register_count(user.email, user.password, user.nickname, user.captcha)
    # 注册成功
    if result["code"] == 200:
        # 生成token
        token = create_token({"email": user.email})
        result["data"]["token"] = token
    return result