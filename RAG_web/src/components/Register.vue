<template>
  <main class="register-shell">
    <section class="register-panel">
      <div class="register-card">
        <div class="brand-row">
          <div class="brand-mark">R</div>
          <div>
            <div class="brand-name">RAG Chat</div>
            <div class="brand-desc">知识库问答助手</div>
          </div>
        </div>

        <div class="panel-header">
          <el-tag class="panel-tag" effect="plain" round>Create Account</el-tag>
          <h1>创建你的 RAG Chat 账号</h1>
          <p>填写邮箱、昵称和密码，获取验证码后即可完成注册。</p>
        </div>

        <el-form class="register-form" label-position="top" @submit.prevent>
          <el-form-item label="邮箱账号">
            <el-input
                    v-model="email"
                    size="large"
                    placeholder="请输入邮箱账号"
                    clearable
            />
          </el-form-item>

          <el-form-item label="登录密码">
            <el-input
                    v-model="password"
                    size="large"
                    type="password"
                    placeholder="请输入登录密码"
                    show-password
            />
          </el-form-item>

          <el-form-item label="昵称">
            <el-input
                    v-model="nickname"
                    size="large"
                    placeholder="请输入昵称"
                    clearable
            />
          </el-form-item>

          <el-form-item label="验证码">
            <el-input
                    v-model="captcha"
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
                    @click="sendRegisterCaptcha"
            >
              发送验证码
            </el-button>
            <el-button
                    class="register-btn"
                    type="primary"
                    size="large"
                    :disabled="!isSend"
                    @click="register"
            >
              注册
            </el-button>
          </div>

          <router-link class="login-link" to="/">
            已有账号？返回登录
          </router-link>
        </el-form>
      </div>
    </section>

    <section class="register-visual">
      <div class="visual-content">
        <div class="visual-card">
          <p class="eyebrow">New Workspace</p>
          <h2>从一个账号开始，拥有你的专属新闻问答助手。</h2>
          <p class="summary">
            注册后可以使用邮箱验证码登录，保存历史会话，并在同一上下文中持续追问。
          </p>
        </div>

        <div class="feature-stack">
          <div class="feature-item active">
            <span>01</span>
            <strong>安全验证</strong>
            <em>邮箱验证码确认身份</em>
          </div>
          <div class="feature-item">
            <span>02</span>
            <strong>个人会话</strong>
            <em>记录每一次问答</em>
          </div>
          <div class="feature-item">
            <span>03</span>
            <strong>连续追问</strong>
            <em>保留上下文线索</em>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import {ref, getCurrentInstance, onMounted} from "vue";
import {useRouter} from "vue-router";
import {ElMessage} from "element-plus";

let proxy = getCurrentInstance().proxy;
let router = new useRouter();
let isSend = ref(false);
let email = ref("");
let password = ref("");
let nickname = ref("");
let captcha = ref("");

// 发送注册验证码
function sendRegisterCaptcha() {
  isSend.value = !isSend.value;
  proxy.$axios({
    url: "users/registerSendCaptcha",
    method: 'get',
    params: {
      email: email.value,
    }
  }).then(res => {
    if (res.data.code === 200) {
      ElMessage.success("验证码已发送，请查收！");
    } else {
      ElMessage.error(res.data.msg);
    }
  })
}

// 注册
function register() {
  isSend.value = !isSend.value;
  proxy.$axios({
    url: "users/register",
    method: 'post',
    data: JSON.stringify({
      email: email.value,
      password: password.value,
      nickname: nickname.value,
      captcha: captcha.value,
    }),
  }).then(res => {
    if (res.data.code === 200) {
      sessionStorage.setItem("nickname", res.data.data.nickname);
      sessionStorage.setItem("usersId", res.data.data.usersId);
      ElMessage.success("注册成功！");
      sessionStorage.setItem('token', res.data.data.token);
      setTimeout(() => {
        router.push("/chat");
      }, 1000);
    } else {
      ElMessage.error(res.data.msg);
    }
  })
}
</script>

<style scoped>
.register-shell {
  --register-primary: #0f9f8f;
  --register-primary-dark: #0b756f;
  --register-ink: #17212b;
  --register-muted: #6b7785;
  --register-line: #dfe7ed;
  min-height: 100vh;
  max-height: 100vh;
  overflow-y: auto;
  display: grid;
  grid-template-columns: minmax(390px, 0.82fr) minmax(0, 1fr);
  color: var(--register-ink);
  background:
          linear-gradient(135deg, rgba(15, 159, 143, 0.14), transparent 34%),
          linear-gradient(215deg, rgba(238, 180, 82, 0.17), transparent 31%),
          #f6f8f7;
  font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
}

.register-panel {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 28px;
  background: rgba(255, 255, 255, 0.58);
  backdrop-filter: blur(18px);
}

.register-card {
  width: min(100%, 455px);
  padding: 30px 34px 28px;
  border: 1px solid rgba(223, 231, 237, 0.9);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 24px 70px rgba(23, 33, 43, 0.1);
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
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
  color: var(--register-muted);
  font-size: 12px;
}

.panel-header {
  margin-bottom: 22px;
}

.panel-tag {
  --el-tag-border-color: rgba(15, 159, 143, 0.3);
  --el-tag-text-color: var(--register-primary-dark);
  --el-tag-bg-color: rgba(15, 159, 143, 0.08);
  margin-bottom: 14px;
}

.panel-header h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
  font-weight: 850;
}

.panel-header p {
  margin: 10px 0 0;
  color: var(--register-muted);
  font-size: 14px;
  line-height: 1.65;
}

.register-form {
  width: 100%;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.register-form :deep(.el-form-item__label) {
  height: 24px;
  margin-bottom: 4px;
  color: var(--register-ink);
  font-weight: 700;
  line-height: 24px;
}

.register-form :deep(.el-input__wrapper) {
  min-height: 44px;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 0 0 1px var(--register-line) inset;
}

.register-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--register-primary) inset, 0 0 0 4px rgba(15, 159, 143, 0.12);
}

.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.captcha-btn,
.register-btn {
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

.register-btn {
  background: var(--register-primary);
}

.register-btn:not(.is-disabled):hover {
  background: #12ad9d;
}

.captcha-btn.is-disabled,
.register-btn.is-disabled {
  background: #b9c6c4;
}

.login-link {
  display: block;
  width: fit-content;
  margin: 16px auto 0;
  color: var(--register-primary-dark);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
}

.login-link:hover {
  color: var(--register-primary);
}

.register-visual {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 36px 46px;
  overflow: hidden;
  background:
          linear-gradient(150deg, rgba(17, 31, 38, 0.96), rgba(17, 31, 38, 0.9)),
          radial-gradient(circle at 78% 16%, rgba(15, 159, 143, 0.38), transparent 30%);
  color: #f7fbfa;
}

.register-visual::before {
  content: "";
  position: absolute;
  inset: 8% -140px auto auto;
  width: 390px;
  height: 390px;
  border: 1px solid rgba(157, 229, 220, 0.24);
  transform: rotate(18deg);
}

.register-visual::after {
  content: "";
  position: absolute;
  inset: auto 8% -120px -90px;
  height: 280px;
  background:
          repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px 42px),
          repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px 42px);
  transform: rotate(7deg);
  opacity: 0.58;
}

.visual-content {
  position: relative;
  z-index: 1;
  width: min(100%, 700px);
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

.visual-card h2 {
  margin: 0;
  font-size: 36px;
  line-height: 1.18;
  font-weight: 850;
}

.summary {
  margin: 18px 0 0;
  color: rgba(247, 251, 250, 0.72);
  font-size: 15px;
  line-height: 1.8;
}

.feature-stack {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.feature-item {
  min-width: 0;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.07);
}

.feature-item.active {
  background: rgba(15, 159, 143, 0.2);
  border-color: rgba(157, 229, 220, 0.34);
}

.feature-item span,
.feature-item em {
  display: block;
  color: rgba(247, 251, 250, 0.56);
  font-size: 12px;
  font-style: normal;
}

.feature-item strong {
  display: block;
  margin: 8px 0 5px;
  font-size: 15px;
}

@media (max-width: 980px) {
  .register-shell {
    max-height: none;
    grid-template-columns: 1fr;
  }

  .register-panel {
    min-height: auto;
    padding: 24px;
  }

  .register-card {
    padding: 26px 24px;
  }

  .register-visual {
    min-height: auto;
    padding: 26px 24px 34px;
  }

  .visual-card {
    padding: 24px;
  }

  .visual-card h2,
  .panel-header h1 {
    font-size: 28px;
  }

  .feature-stack {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .register-panel,
  .register-visual {
    padding-left: 16px;
    padding-right: 16px;
  }

  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>
