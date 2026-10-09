<template>
  <main class="login-shell">
    <section class="login-visual">
      <div class="visual-content">
        <div class="brand-row">
          <div class="brand-mark">R</div>
          <div>
            <div class="brand-name">RAG Chat</div>
            <div class="brand-desc">知识库问答助手</div>
          </div>
        </div>

        <div class="visual-card">
          <p class="eyebrow">Retrieval Augmented Generation</p>
          <h1>让陈旧的历史信息，变成可以连续获取的答案。</h1>
          <p class="summary">
            使用邮箱验证码登录后，即可进入专属会话空间，了解历史新闻信息并获得coco解答。
          </p>
        </div>

        <div class="signal-board">
          <div class="signal-card active">
            <span>01</span>
            <strong>邮箱验证</strong>
            <em>快速进入系统</em>
          </div>
          <div class="signal-card">
            <span>02</span>
            <strong>知识检索</strong>
            <em>结合上下文回答</em>
          </div>
          <div class="signal-card">
            <span>03</span>
            <strong>历史会话</strong>
            <em>随时继续追问</em>
          </div>
        </div>
      </div>
    </section>

    <section class="login-panel">
      <div class="login-card">
        <div class="panel-header">
          <el-tag class="panel-tag" effect="plain" round>Secure Login</el-tag>
          <h2>登录到 RAG Chat</h2>
          <p>请输入邮箱获取验证码，然后完成登录。</p>
        </div>

        <el-form class="login-form" label-position="top" @submit.prevent>
          <el-form-item label="邮箱账号">
            <el-input
                    v-model="email"
                    :disabled="isSend"
                    size="large"
                    placeholder="请输入邮箱账号"
                    clearable
            />
          </el-form-item>

          <el-form-item label="验证码">
            <el-input
                    v-model="captcha"
                    :disabled="!isSend"
                    size="large"
                    placeholder="请输入邮箱验证码"
                    clearable
            />
          </el-form-item>

          <div class="action-grid">
            <el-button
                    class="captcha-btn"
                    type="primary"
                    size="large"
                    :disabled="isSend"
                    @click="sendLoginCaptcha"
            >
              发送验证码
            </el-button>
            <el-button
                    class="login-btn"
                    type="primary"
                    size="large"
                    :disabled="!isSend"
                    @click="login"
            >
            登录
            </el-button>
          </div>

          <div class="login-divider">
            <span>或使用密码登录</span>
          </div>

          <div class="password-login">
            <el-form-item label="登录密码">
              <el-input
                      v-model="password"
                      size="large"
                      type="password"
                      placeholder="请输入登录密码"
                      show-password
                      clearable
              />
            </el-form-item>

            <el-button
                    class="password-login-btn"
                    type="primary"
                    size="large"
                    @click="passwordLogin"
            >
              密码登录
            </el-button>
          </div>

          <el-button class="register-btn" text @click="register">
            还没有账号？立即注册
          </el-button>
        </el-form>
      </div>
    </section>
  </main>
</template>

<script setup>
import {ref, getCurrentInstance, onMounted} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";

let router = new useRouter();
let proxy = getCurrentInstance().proxy;
let isSend = ref(false);
let email = ref("");
let captcha = ref("");
let password = ref("");


// 发送登录验证码
function sendLoginCaptcha() {
  isSend.value = !isSend.value;
  proxy.$axios({
    url: "users/loginSendCaptcha",
    method: 'get',
    params: {
      email: email.value,
    }
  }).then(res => {
    if (res.data.code === 200) {
      ElMessage.success("验证码已发送，请查收！");
      sessionStorage.setItem('nickname', res.data.data.nickname);
      sessionStorage.setItem('usersId', res.data.data.usersId);
    } else {
      ElMessage.error(res.data.msg);
    }
  })
}

// 邮箱登录登录
function login() {
  proxy.$axios({
    url: "users/login",
    method: 'post',
    data: JSON.stringify({
      email: email.value,
      captcha: captcha.value,
    }),
  }).then(res => {
     if (res.data.code === 200) {
      ElMessage.success("登录成功！");
      sessionStorage.setItem('token', res.data.data);
      setTimeout(() => {
        router.push("/chat");
      }, 1000)
    } else {
      ElMessage.error(res.data.msg);
   }
  })
}

// 密码登录
function passwordLogin() {
  proxy.$axios({
    url: "users/passwordLogin",
    method: 'post',
    data: JSON.stringify({
      email: email.value,
      password: password.value,
    }),
  }).then(res => {
    if (res.data.code === 200) {
      ElMessage.success("登录成功！");
      sessionStorage.setItem('nickname', res.data.data.nickname);
      sessionStorage.setItem('usersId', res.data.data.usersId);
      sessionStorage.setItem('token', res.data.data.token);
      setTimeout(() => {
        router.push("/chat");
      }, 1000)
    } else {
      ElMessage.error(res.data.msg);
    }
  })
}

// 注册
function register() {
  router.push("/register");
}
</script>

<style scoped>
.login-shell {
  --login-primary: #0f9f8f;
  --login-primary-dark: #0b756f;
  --login-ink: #17212b;
  --login-muted: #6b7785;
  --login-line: #dfe7ed;
  min-height: 100vh;
  max-height: 100vh;
  overflow-y: auto;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(390px, 0.82fr);
  color: var(--login-ink);
  background:
          linear-gradient(135deg, rgba(15, 159, 143, 0.14), transparent 34%),
          linear-gradient(215deg, rgba(238, 180, 82, 0.17), transparent 31%),
          #f6f8f7;
  font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
}

.login-visual {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 36px 46px;
  overflow: hidden;
  background:
          linear-gradient(150deg, rgba(17, 31, 38, 0.96), rgba(17, 31, 38, 0.9)),
          radial-gradient(circle at 18% 20%, rgba(15, 159, 143, 0.35), transparent 28%);
  color: #f7fbfa;
}

.login-visual::before {
  content: "";
  position: absolute;
  inset: 9% auto auto -120px;
  width: 390px;
  height: 390px;
  border: 1px solid rgba(157, 229, 220, 0.24);
  transform: rotate(-14deg);
}

.login-visual::after {
  content: "";
  position: absolute;
  inset: auto -80px -120px 20%;
  height: 280px;
  background:
          repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px 42px),
          repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px 42px);
  transform: rotate(-8deg);
  opacity: 0.58;
}

.visual-content {
  position: relative;
  z-index: 1;
  width: min(100%, 720px);
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #eeb452;
  color: #17212b;
  font-size: 22px;
  font-weight: 800;
}

.brand-name {
  font-size: 17px;
  font-weight: 800;
}

.brand-desc {
  margin-top: 2px;
  color: rgba(247, 251, 250, 0.62);
  font-size: 12px;
}

.visual-card {
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.07);
}

.eyebrow {
  margin: 0 0 12px;
  color: #9de5dc;
  font-size: 13px;
  font-weight: 800;
}

.visual-card h1 {
  margin: 0;
  max-width: 720px;
  font-size: 36px;
  line-height: 1.18;
  font-weight: 850;
}

.summary {
  max-width: 570px;
  margin: 18px 0 0;
  color: rgba(247, 251, 250, 0.72);
  font-size: 15px;
  line-height: 1.8;
}

.signal-board {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.signal-card {
  min-width: 0;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.07);
}

.signal-card.active {
  background: rgba(15, 159, 143, 0.2);
  border-color: rgba(157, 229, 220, 0.34);
}

.signal-card span,
.signal-card em {
  display: block;
  color: rgba(247, 251, 250, 0.56);
  font-size: 12px;
  font-style: normal;
}

.signal-card strong {
  display: block;
  margin: 8px 0 5px;
  font-size: 15px;
}

.login-panel {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 28px;
  background: rgba(255, 255, 255, 0.58);
  backdrop-filter: blur(18px);
}

.login-card {
  width: min(100%, 455px);
  padding: 32px 34px 30px;
  border: 1px solid rgba(223, 231, 237, 0.9);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 24px 70px rgba(23, 33, 43, 0.1);
}

.panel-header {
  margin-bottom: 24px;
}

.panel-tag {
  --el-tag-border-color: rgba(15, 159, 143, 0.3);
  --el-tag-text-color: var(--login-primary-dark);
  --el-tag-bg-color: rgba(15, 159, 143, 0.08);
  margin-bottom: 14px;
}

.panel-header h2 {
  margin: 0;
  font-size: 30px;
  line-height: 1.2;
  font-weight: 850;
}

.panel-header p {
  margin: 10px 0 0;
  color: var(--login-muted);
  font-size: 14px;
  line-height: 1.65;
}

.login-form {
  width: 100%;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.login-form :deep(.el-form-item__label) {
  height: 24px;
  margin-bottom: 4px;
  color: var(--login-ink);
  font-weight: 700;
  line-height: 24px;
}

.login-form :deep(.el-input__wrapper) {
  min-height: 44px;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 0 0 1px var(--login-line) inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--login-primary) inset, 0 0 0 4px rgba(15, 159, 143, 0.12);
}

.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.captcha-btn,
.login-btn {
  height: 44px;
  margin: 0;
  border: 0;
  border-radius: 8px;
  font-weight: 800;
}

.captcha-btn {
  background: #17212b;
}

.captcha-btn:not(.is-disabled):hover {
  background: #24313d;
}

.login-btn {
  background: var(--login-primary);
}

.login-btn:not(.is-disabled):hover {
  background: #12ad9d;
}

.captcha-btn.is-disabled,
.login-btn.is-disabled {
  background: #b9c6c4;
}

.login-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 18px 0 16px;
  color: var(--login-muted);
  font-size: 13px;
  font-weight: 700;
}

.login-divider::before,
.login-divider::after {
  content: "";
  height: 1px;
  flex: 1;
  background: var(--login-line);
}

.password-login {
  padding: 16px;
  border: 1px solid rgba(223, 231, 237, 0.92);
  border-radius: 8px;
  background: rgba(238, 246, 244, 0.58);
}

.password-login :deep(.el-form-item) {
  margin-bottom: 12px;
}

.password-login-btn {
  width: 100%;
  height: 44px;
  margin: 0;
  border: 0;
  border-radius: 8px;
  background: #eeb452;
  color: #17212b;
  font-weight: 800;
}

.password-login-btn:not(.is-disabled):hover {
  background: #f3bf67;
  color: #17212b;
}

.register-btn {
  display: block;
  margin: 16px auto 0;
  color: var(--login-primary-dark);
  font-weight: 700;
}

@media (max-width: 980px) {
  .login-shell {
    max-height: none;
    grid-template-columns: 1fr;
  }

  .login-visual {
    min-height: auto;
    padding: 26px 24px 34px;
  }

  .login-panel {
    min-height: auto;
    padding: 24px;
  }

  .login-card {
    padding: 28px 24px;
  }

  .visual-card {
    padding: 24px;
  }

  .visual-card h1,
  .panel-header h2 {
    font-size: 28px;
  }

  .signal-board {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .login-panel,
  .login-visual {
    padding-left: 16px;
    padding-right: 16px;
  }

  .action-grid {
    grid-template-columns: 1fr;
  }

  .password-login {
    padding: 14px;
  }
}
</style>
