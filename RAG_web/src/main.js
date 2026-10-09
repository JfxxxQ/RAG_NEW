import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import axios from 'axios'
import router from './router'
// 注册element-plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'


const app = createApp(App)
app.use(ElementPlus)
app.use(router)

// axios 配置
axios.defaults.baseURL = 'http://localhost:8000/'
axios.defaults.headers.post['Content-Type'] = 'application/json'
axios.defaults.headers.put['Content-Type'] = 'application/json'
app.config.globalProperties.$axios = axios

// Markdown 配置
import { marked } from 'marked'
import DOMPurify from 'dompurify'

//  Markdown 配置
marked.setOptions({
  breaks: true,    // 支持换行
  gfm: true,       // GitHub 风格
  smartLists: true,
  smartypants: false
})

// Markdown 正则处理
function normalizeMarkdown(text) {
  return text
    .replace(/(#{1,6} )/g, '\n$1')
    .replace(/- /g, '\n- ')
}

// 全局 markdown 渲染方法
function renderMarkdown(text) {
  if (!text) return ''
  const rawHtml = marked.parse(normalizeMarkdown(text))
  return DOMPurify.sanitize(rawHtml)
}
app.config.globalProperties.$renderMarkdown = renderMarkdown

app.mount('#app')

/*
导航守卫
参数：
1、to: 去访问哪一个请求地址
2、from: 来自哪一个请求地址
3、next: 是否允许访问

 */
router.beforeEach((to, from, next) => {
    // 请求路径中的meta的isLogin参数为false，直接放行
    if (to.meta.isLogin) { // 请求地址需要拦截
      const token = sessionStorage.getItem("token");
      if (token && token !== "null" && token !== "undefined") {
        // 放行
        next();
      } else {
        // 拦截，让它回到登录界面
        next("/");
      }
    } else { // 直接访问，请求地址无需拦截
      next();
    }
})

