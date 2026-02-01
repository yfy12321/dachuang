import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 全局错误处理：捕获未处理的Promise rejection
window.addEventListener('unhandledrejection', (event) => {
  // 忽略浏览器扩展相关的错误
  if (event.reason && (
    typeof event.reason === 'string' && event.reason.includes('Receiving end does not exist')
  )) {
    event.preventDefault()
    return
  }
  console.error('未处理的Promise rejection:', event.reason)
  // 阻止默认的错误提示
  event.preventDefault()
})

// 全局错误处理：捕获未捕获的错误
window.addEventListener('error', (event) => {
  // 忽略浏览器扩展相关的错误
  if (event.message && (
    event.message.includes('Receiving end does not exist') ||
    event.message.includes('Could not establish connection') ||
    event.message.includes('Extension context invalidated')
  )) {
    event.preventDefault()
    return
  }
  console.error('全局错误:', event.error)
})

// 处理 chrome.runtime 错误
if (typeof chrome !== 'undefined' && chrome.runtime) {
  chrome.runtime.onMessage.addListener(() => {
    // 允许其他扩展的消息监听
  })
}

const app = createApp(App)

// 全局注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用ElementPlus插件
app.use(ElementPlus)

app.mount('#app')