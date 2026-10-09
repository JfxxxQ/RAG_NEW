<template>
    <div class="chat-shell">
        <aside class="chat-sidebar">
            <div class="brand-panel">
                <div class="brand-mark">CO</div>
                <div>
                    <div class="brand-name">COCO Chat</div>
                    <div class="brand-desc">新闻回溯问答助手</div>
                </div>
            </div>

            <el-button class="new-chat-btn" type="primary" @click="createNewChat">
                <el-icon><Plus /></el-icon>
                新建对话
            </el-button>

            <div class="sidebar-section-title">历史记录</div>
            <el-scrollbar class="history-scroll">
                <div v-if="historyList.length === 0" class="history-empty">
                    暂无历史会话
                </div>
                <div
                        v-for="item in historyList"
                        :key="item.historyId"
                        class="history-card"
                        :class="{ active: item.historyId === globalHistoryId }"
                        @click="selectHistory(item.historyId)"
                >
                    <span class="history-icon">
                        <el-icon><ChatDotRound /></el-icon>
                    </span>
                    <span class="history-content">
                        <span class="history-question">{{ item.question || '未命名对话' }}</span>
                        <span class="history-time">{{ item.createTime || '刚刚' }}</span>
                    </span>
                    <button
                            class="history-delete"
                            type="button"
                            title="删除历史记录"
                            @click.stop="deleteHistory(item.historyId)"
                    >
                        <el-icon><Delete /></el-icon>
                    </button>
                </div>
            </el-scrollbar>

            <el-dropdown trigger="click" @command="handleUserCommand">
                <div class="user-panel">
                    <el-avatar :size="40" class="user-avatar">{{ nickname }}</el-avatar>
                    <div class="user-copy">
                        <div class="user-name">{{ nickname }}</div>
                        <div class="user-status">在线使用中</div>
                    </div>
                    <span class="user-chevron">⌄</span>
                </div>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                        <el-dropdown-item command="settings">设置</el-dropdown-item>
                        <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </aside>

        <main class="chat-main">
            <header class="chat-header">
                <div>
                    <div class="chat-title">{{ currentTitle }}</div>
                    <div class="chat-subtitle">基于本地知识库进行连续问答</div>
                </div>
                <el-tag class="status-tag" effect="plain" round>RAG Assistant</el-tag>
            </header>

            <section class="message-stage" ref="messageBox">
                <div v-if="messages.length === 0" class="empty-state">
                    <div class="empty-kicker">开始一次检索增强对话</div>
                    <h1>你好，{{ nickname }}</h1>
                    <p>输入问题后，助手会结合知识库内容生成回答，并保留上下文用于继续追问。</p>
                </div>

                <article
                        v-for="(item, index) in messages"
                        :key="index"
                        class="message-row"
                        :class="item.role"
                >
                    <el-avatar :size="36" class="message-avatar" :class="item.role">
                        {{ item.role === 'assistant' ? 'AI' : nickname }}
                    </el-avatar>
                    <div class="message-stack">
                        <div class="message-meta">
                            {{ item.role === 'assistant' ? 'RAG 助手' : nickname }}
                        </div>
                        <div class="message-bubble" :class="item.role">
                            <span v-if="item.role === 'user'">{{ item.content }}</span>
                            <div v-else class="markdown-body" v-html="$renderMarkdown(item.content)"></div>
                        </div>
                    </div>
                </article>
            </section>

            <footer class="composer">
                <el-input
                        v-model="question"
                        class="chat-input"
                        type="textarea"
                        resize="none"
                        :autosize="{ minRows: 1, maxRows: 5 }"
                        placeholder="向 coco 提问，Enter 发送，Shift + Enter 换行"
                        @keydown.enter.exact.prevent="handleEnter"
                />
                <el-button
                        class="send-btn"
                        type="primary"
                        :disabled="isButtonDisabled"
                        v-loading="isLoading"
                        @click="chat"
                >
                    <el-icon v-if="!isLoading"><Promotion /></el-icon>
                    <span>发送</span>
                </el-button>
            </footer>
        </main>
    </div>
</template>

<script setup>
import {ref, getCurrentInstance, onMounted, watch, computed, nextTick, onUnmounted} from "vue";
import {ElMessage} from "element-plus";
import {useRouter} from "vue-router";
import {ChatDotRound, Delete, Plus, Promotion} from "@element-plus/icons-vue";
import { fetchEventSource } from '@microsoft/fetch-event-source';


// 代理对象
let proxy = getCurrentInstance().proxy;
// 用户输入问题
let question = ref("");
// 路由对象
let router = useRouter();
// 按钮是否禁用
let isButtonDisabled = ref(true);
// loading状态
let isLoading = ref(false);
// 当前登录用户信息
let nickname = ref("");
// 历史记录模拟数据
let historyList = ref([]);
// 消息区 DOM，用于自动滚动到底部
let messageBox = ref(null);
// 全局对话保存的history_id【默认值为0】
let globalHistoryId = ref(0);
// 存储聊天记录的数组
let messages = ref([]);
// 中断当前sse连接
let ctrl = null;

// 当前对话标题
const currentTitle = computed(() => {
    const cur = historyList.value.find(h => h.historyId === globalHistoryId.value);
    return cur ? cur.question : '新的对话';
});


// 监听用户输入，如果用户输入长度大于0则按钮不禁用
watch(question, (newQuestion) => {
  // 如果用户输入长度大于0则按钮不禁用
  isButtonDisabled.value = !(newQuestion.length > 0 && newQuestion.trim());
});

// 监听消息变化，自动滚动到底部（流式输出时保持跟随）
watch(messages, () => {
    nextTick(() => {
        if (messageBox.value) {
            messageBox.value.scrollTop = messageBox.value.scrollHeight;
        }
    });
}, {deep: true});

// 聊天
function chat() {
  let myQuestion = question.value.trim(); // 把用户输入的内容赋值给新的变量接受，以便清空提问框
  question.value = ""; // 清空提问框
  // 把用户输入的问题添加到聊天记录数组中
  messages.value.push({role: "user", content: myQuestion});
  // 把coco的回复添加到聊天记录数组中
  messages.value.push({role: 'assistant', content: 'coco正在思考...'});
  let token = sessionStorage.getItem('token');
  if (!token) {
    ElMessage.error("请先登录");
    router.push('/login');
    return;
  }

  if (ctrl) {
    ctrl.abort();
    ctrl = null;
  }
  ctrl = new AbortController();
  let params = new URLSearchParams({
    question: myQuestion,
    historyId: globalHistoryId.value,
  });
  // 拼接结果的变量
  let s = "";
  isLoading.value = true;
  // 创建sse请求 --- 对象 ---参数就是服务器请求地址 + 客户端给服务器的参数 --- get 请求
  fetchEventSource("http://localhost:8000/chat/chat?" + params, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    signal: ctrl.signal,
    // sse请求监听服务器返回的结果
    onmessage(event) {
      let content = JSON.parse(event.data); // 取出来的数据本来是json，使用json.parse转js对象
      if (content.content === "[DONE]") { // 如果内容是[DONE]则表示数据取完了
        console.log("SSE 连接关闭")
        isLoading.value = false; // 隐藏loading
        // 保存对话结果
        saveChatResult(myQuestion, s);
        return;
      }
      if (content.error) { // 错误内容
        if (content.error.includes("inappropriate content") || content.error.includes("DataInspectionFailed")) {
          s += `\n\n抱歉，当前对话内容有敏感词汇，请尝试换个问法或开启新对话。`;
        } else {
          s += `\n\n${content.error}`;
        }
        // 实时更新最后一条消息的显示内容（实现打字机效果）
        messages.value[messages.value.length - 1].content = s;
        return;
      }
      if (content.content) { // 正常内容
        s += content.content;
        // 修改messages中最后一个元素中content属性的值
        messages.value[messages.value.length - 1].content = s;
      }
    },
    // sse请求监听服务器返回的错误
    onerror(err) {
      console.log("SSE 请求错误：", err);
      isLoading.value = false; // 隐藏loading
      throw { name: "FatalError", message: "停止重连" };
    },
    // sse请求监听服务器返回的连接成功
    onopen(response) {
      // 401：token 失效，直接拒绝，不要重连
      if (response.status === 401) {
        isLoading.value = false;
        ctrl.abort();
        throw { name: "AuthError", message: "登录已过期，请重新登录" };
      }

      if (response.ok && response.headers.get('content-type')?.includes('text/event-stream')) {
        console.log("SSE 连接成功");
        return;
      }
      isLoading.value = false;
      throw { name: "FatalError", message: `SSE 连接失败：${response.status}` };
    },
    onclose() {
      console.log("SSE 连接关闭");
      isLoading.value = false;
    },
  }).catch(err => {
    console.log("SSE 请求错误：", err);
    isLoading.value = false;
  });
}

// 保存对话结果 --- 需要参数 userId、question、answer、parentId
function saveChatResult(question, answer) {
    let params = {
        usersId: sessionStorage.getItem('usersId'),
        question: question,
        answer: answer,
        parentId: globalHistoryId.value
    }
    proxy.$axios({
        url: 'history/saveChatResult',
        method: 'post',
        data: JSON.stringify(params)
    }).then(res => { // 返回的数据就是新增的对话记录的id
        if (globalHistoryId.value === 0){
            // 新对话 --- 继续对话不需要做任何处理
            globalHistoryId.value = res.data.data;
            // 重新加载历史记录菜单
            queryHistoryMenu();
        }
    });
}

// 点击某条历史记录
function selectHistory(historyId) {
    globalHistoryId.value = historyId; // 点击历史记录，更新全局对话ID
    proxy.$axios({
        url: 'history/queryHistoryList/' + historyId,
        method: 'get'
    }).then(res => {
        messages.value = res.data.data;
    });
}

// onUnmounted 清理
onUnmounted(() => {
  if (ctrl) {
    ctrl.abort();
    ctrl = null;
  }
});

// 新建对话
function createNewChat() {
    globalHistoryId.value = 0; // 重置新对话的parentId为0
    messages.value = []; // 清空messages数组中的内容
}

// 删除历史记录
function deleteHistory(historyId) {
    if (!historyId) {
        ElMessage.warning('请选择要删除的历史记录');
        return;
    }
    let token = sessionStorage.getItem('token');
    proxy.$axios({
        url: 'history/deleteHistory/' + historyId,
        method: 'delete',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    }).then(() => {
        if (String(globalHistoryId.value) === String(historyId)) {
            globalHistoryId.value = 0;
            messages.value = [];
        }
        queryHistoryMenu();
        ElMessage.success('删除成功');
    }).catch(() => {
        ElMessage.error('删除失败，请稍后重试');
    });
}

// 键盘 Enter 发送（Shift+Enter 换行）
function handleEnter() {
    if (!isButtonDisabled.value) {
        chat();
    }
}

// 用户菜单命令处理
function handleUserCommand(command) {
    switch (command) {
        case 'profile':
            ElMessage.info('个人中心功能开发中');
            break;
        case 'settings':
            ElMessage.info('设置功能开发中');
            break;
        case 'logout':
            logout();
            break;
        default:
            break;
    }
    // TODO: 后续对接后端，根据 command 跳转对应页面
}

// 退出登录
function logout() {
    sessionStorage.removeItem('nickname');
    ElMessage.success('已退出登录');
    router.push('/');
    // TODO: 后续对接后端，清理登录态（token）后再跳转登录页
}

// 加载历史对话菜单
function queryHistoryMenu() {
    proxy.$axios({
        url: 'history/queryHistoryMenu/' + sessionStorage.getItem('usersId'),
        method: 'get'
    }).then(res => {
        historyList.value = res.data.data;
    });
}

// 加载页面后执行
onMounted(() => {
    nickname.value = sessionStorage.getItem('nickname') || 'undefined';
    queryHistoryMenu();
});
</script>

<style scoped>
.chat-shell {
    --chat-primary: #0f9f8f;
    --chat-primary-dark: #0b756f;
    --chat-ink: #17212b;
    --chat-muted: #6b7785;
    --chat-line: #dfe7ed;
    --chat-soft: #eef6f4;
    --chat-panel: rgba(255, 255, 255, 0.88);
    display: flex;
    width: 100%;
    height: 100vh;
    overflow: hidden;
    color: var(--chat-ink);
    background:
            linear-gradient(135deg, rgba(15, 159, 143, 0.14), transparent 32%),
            linear-gradient(215deg, rgba(238, 180, 82, 0.16), transparent 30%),
            #f6f8f7;
    font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
}

.chat-sidebar {
    width: 300px;
    flex: 0 0 300px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 20px 16px;
    background: rgba(17, 31, 38, 0.94);
    color: #f7fbfa;
    box-shadow: 16px 0 40px rgba(23, 33, 43, 0.12);
}

.brand-panel,
.user-panel {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-mark {
    width: 44px;
    height: 44px;
    display: grid;
    place-items: center;
    border-radius: 8px;
    background: #eeb452;
    color: #17212b;
    font-size: 22px;
    font-weight: 800;
}

.brand-name {
    font-size: 18px;
    font-weight: 800;
}

.brand-desc,
.user-status {
    margin-top: 3px;
    color: rgba(247, 251, 250, 0.62);
    font-size: 12px;
}

.new-chat-btn {
    width: 100%;
    height: 42px;
    border: 0;
    border-radius: 8px;
    background: var(--chat-primary);
    font-weight: 700;
}

.new-chat-btn:hover {
    background: #12ad9d;
}

.sidebar-section-title {
    margin-top: 4px;
    color: rgba(247, 251, 250, 0.58);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0;
}

.history-scroll {
    min-height: 0;
    flex: 1;
}

.history-empty {
    padding: 22px 12px;
    color: rgba(247, 251, 250, 0.48);
    font-size: 13px;
}

.history-card {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    padding: 11px 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.06);
    color: inherit;
    cursor: pointer;
    text-align: left;
    transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}

.history-card:hover,
.history-card.active {
    background: rgba(15, 159, 143, 0.18);
    border-color: rgba(15, 159, 143, 0.55);
    transform: translateY(-1px);
}

.history-icon {
    width: 30px;
    height: 30px;
    flex: 0 0 30px;
    display: grid;
    place-items: center;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.08);
    color: #9de5dc;
}

.history-content {
    min-width: 0;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.history-delete {
    width: 28px;
    height: 28px;
    flex: 0 0 28px;
    display: grid;
    place-items: center;
    border: 0;
    border-radius: 8px;
    background: transparent;
    color: rgba(247, 251, 250, 0.48);
    cursor: pointer;
    opacity: 0;
    transition: background 0.18s ease, color 0.18s ease, opacity 0.18s ease;
}

.history-card:hover .history-delete,
.history-card.active .history-delete {
    opacity: 1;
}

.history-delete:hover {
    background: rgba(245, 108, 108, 0.18);
    color: #f56c6c;
}

.history-question,
.history-time {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.history-question {
    font-size: 14px;
    font-weight: 650;
}

.history-time {
    color: rgba(247, 251, 250, 0.5);
    font-size: 12px;
}

.user-panel {
    padding: 12px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.07);
    cursor: pointer;
    outline: none;
}

.user-avatar {
    flex: 0 0 auto;
    background: #eeb452;
    color: #17212b;
    font-weight: 800;
}

.user-copy {
    min-width: 0;
    flex: 1;
}

.user-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 14px;
    font-weight: 700;
}

.user-chevron {
    color: rgba(247, 251, 250, 0.58);
    font-size: 18px;
}

.chat-main {
    min-width: 0;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.chat-header {
    height: 76px;
    flex: 0 0 76px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 34px;
    border-bottom: 1px solid rgba(223, 231, 237, 0.9);
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(18px);
}

.chat-title {
    max-width: 56vw;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 18px;
    font-weight: 800;
}

.chat-subtitle {
    margin-top: 5px;
    color: var(--chat-muted);
    font-size: 13px;
}

.status-tag {
    --el-tag-border-color: rgba(15, 159, 143, 0.3);
    --el-tag-text-color: var(--chat-primary-dark);
    --el-tag-bg-color: rgba(15, 159, 143, 0.08);
}

.message-stage {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 30px 34px;
    display: flex;
    flex-direction: column;
    gap: 22px;
}

.empty-state {
    margin: auto;
    max-width: 620px;
    padding: 44px;
    border: 1px solid rgba(223, 231, 237, 0.85);
    border-radius: 8px;
    background: var(--chat-panel);
    box-shadow: 0 24px 70px rgba(23, 33, 43, 0.08);
}

.empty-kicker {
    color: var(--chat-primary-dark);
    font-size: 13px;
    font-weight: 800;
}

.empty-state h1 {
    margin: 12px 0 10px;
    font-size: 34px;
    line-height: 1.15;
}

.empty-state p {
    margin: 0;
    color: var(--chat-muted);
    font-size: 15px;
    line-height: 1.8;
}

.message-row {
    width: min(820px, 86%);
    display: flex;
    gap: 12px;
    animation: message-in 0.22s ease both;
}

.message-row.user {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.message-avatar {
    flex: 0 0 auto;
    background: #ffffff;
    color: var(--chat-primary-dark);
    border: 1px solid var(--chat-line);
    font-weight: 800;
}

.message-avatar.assistant {
    background: #17212b;
    color: #ffffff;
    border-color: #17212b;
}

.message-stack {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.message-row.user .message-stack {
    align-items: flex-end;
}

.message-meta {
    padding: 0 2px;
    color: var(--chat-muted);
    font-size: 12px;
}

.message-bubble {
    max-width: 100%;
    padding: 13px 16px;
    border-radius: 8px;
    line-height: 1.75;
    font-size: 14px;
    word-break: break-word;
    box-shadow: 0 10px 26px rgba(23, 33, 43, 0.06);
}

.message-bubble.assistant {
    border: 1px solid var(--chat-line);
    background: rgba(255, 255, 255, 0.92);
}

.message-bubble.user {
    background: var(--chat-primary);
    color: #ffffff;
}

.markdown-body :deep(p) {
    margin: 0 0 8px;
}

.markdown-body :deep(p:last-child) {
    margin-bottom: 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
    margin: 12px 0 8px;
    color: var(--chat-ink);
    line-height: 1.35;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
    margin: 6px 0 10px;
    padding-left: 22px;
}

.markdown-body :deep(pre) {
    margin: 10px 0;
    padding: 13px;
    overflow-x: auto;
    border-radius: 8px;
    background: #111f26;
    color: #edf7f5;
}

.markdown-body :deep(code) {
    padding: 2px 6px;
    border-radius: 5px;
    background: var(--chat-soft);
    color: var(--chat-primary-dark);
    font-family: Consolas, "Courier New", monospace;
    font-size: 13px;
}

.markdown-body :deep(pre code) {
    padding: 0;
    background: transparent;
    color: inherit;
}

.markdown-body :deep(blockquote) {
    margin: 10px 0;
    padding: 4px 12px;
    border-left: 3px solid var(--chat-primary);
    background: var(--chat-soft);
    color: var(--chat-muted);
}

.composer {
    flex: 0 0 auto;
    display: flex;
    align-items: flex-end;
    gap: 12px;
    padding: 18px 34px 24px;
    border-top: 1px solid rgba(223, 231, 237, 0.9);
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(18px);
}

.chat-input :deep(.el-textarea__inner) {
    min-height: 48px !important;
    padding: 13px 15px;
    border-radius: 8px;
    background: #ffffff;
    box-shadow: 0 0 0 1px var(--chat-line) inset;
    color: var(--chat-ink);
    font-size: 14px;
    line-height: 1.55;
}

.chat-input :deep(.el-textarea__inner:focus) {
    box-shadow: 0 0 0 1px var(--chat-primary) inset, 0 0 0 4px rgba(15, 159, 143, 0.12);
}

.send-btn {
    height: 48px;
    min-width: 92px;
    border: 0;
    border-radius: 8px;
    background: var(--chat-primary);
    font-weight: 800;
}

.send-btn:not(.is-disabled):hover {
    background: #12ad9d;
}

.send-btn.is-disabled {
    background: #b9c6c4;
}

.send-btn .el-icon {
    margin-right: 5px;
    font-size: 17px;
}

@keyframes message-in {
    from {
        opacity: 0;
        transform: translateY(6px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 820px) {
    .chat-shell {
        flex-direction: column;
    }

    .chat-sidebar {
        width: 100%;
        flex: 0 0 auto;
        max-height: 240px;
    }

    .chat-header,
    .composer {
        padding-left: 18px;
        padding-right: 18px;
    }

    .message-stage {
        padding: 22px 18px;
    }

    .message-row {
        width: 100%;
    }

    .status-tag {
        display: none;
    }
}
</style>
