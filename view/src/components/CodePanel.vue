<template>
  <div
    class="code-panel"
    :class="{ 'collapsed': isCollapsed }"
    :style="panelStyle"
    ref="panelRef"
  >
    <!-- 标题栏 (可拖动) -->
    <div
      class="panel-header"
      @mousedown="startDrag"
    >
      <div class="header-left">
        <button class="collapse-button" @click="toggleCollapse">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'rotated': isCollapsed }">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="cursor: move;">
          <polyline points="16 18 22 12 16 6"></polyline>
          <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
        <span class="panel-title" style="cursor: move;">{{ getPanelTitle }}</span>
      </div>

      <!-- 语言选择器 -->
      <div class="language-selector">
        <button
          v-for="lang in supportedLanguages"
          :key="lang.value"
          @click="handleLanguageChange(lang.value)"
          class="lang-button"
          :class="{ 'active': selectedLanguage === lang.value }"
          :title="lang.label"
        >
          {{ lang.abbr }}
        </button>
      </div>
    </div>

    <!-- 调整大小手柄 -->
    <div class="resize-handle resize-left" @mousedown.stop="(e) => startResize('left', e)"></div>
    <div class="resize-handle resize-right" @mousedown.stop="(e) => startResize('right', e)"></div>
    <div class="resize-handle resize-top" @mousedown.stop="(e) => startResize('top', e)"></div>
    <div class="resize-handle resize-bottom" @mousedown.stop="(e) => startResize('bottom', e)"></div>
    <div class="resize-handle resize-corner-tl" @mousedown.stop="(e) => startResize('top-left', e)"></div>
    <div class="resize-handle resize-corner-tr" @mousedown.stop="(e) => startResize('top-right', e)"></div>
    <div class="resize-handle resize-corner-bl" @mousedown.stop="(e) => startResize('bottom-left', e)"></div>
    <div class="resize-handle resize-corner-br" @mousedown.stop="(e) => startResize('bottom-right', e)"></div>

    <!-- 代码内容区域 -->
    <div v-if="!isCollapsed" class="panel-content">
      <!-- 当前操作函数名 -->
      <div v-if="currentOperation" class="operation-badge">
        {{ currentOperation }}
      </div>

      <!-- 代码显示区 -->
      <div class="code-container" ref="codeContainer">
        <div class="code-block">
          <div
            v-for="(line, index) in codeLines"
            :key="index"
            class="code-line"
            :class="{
              'highlighted': highlightedLines.includes(index + 1),
              'current-line': currentLine === index + 1
            }"
            :data-line-number="index + 1"
            v-html="line.html"
          ></div>
        </div>
      </div>

      <!-- 空状态提示 -->
      <div v-if="codeLines.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <polyline points="16 18 22 12 16 6"></polyline>
          <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
        <p>No code to display</p>
        <p class="hint">Perform an operation to see the {{ selectedLanguage.toUpperCase() }} implementation</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import api from '../services/api.js'
// 使用 highlight.js 进行语法高亮
import hljs from 'highlight.js/lib/core'
import cpp from 'highlight.js/lib/languages/cpp'
import python from 'highlight.js/lib/languages/python'
import java from 'highlight.js/lib/languages/java'
import 'highlight.js/styles/atom-one-dark.css'

// 注册语言
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('python', python)
hljs.registerLanguage('java', java)

const props = defineProps({
  code: {
    type: String,
    default: ''
  },
  currentLine: {
    type: Number,
    default: null
  },
  highlightedLines: {
    type: Array,
    default: () => []
  },
  operationName: {
    type: String,
    default: ''
  },
  structureType: {
    type: String,
    default: ''
  },
  operation: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['language-change', 'code-loaded'])

const isCollapsed = ref(false)
const codeContainer = ref(null)
const panelRef = ref(null)
const selectedLanguage = ref('cpp')
const loadedCode = ref({})  // 缓存已加载的代码 {language: code}

// 拖动和缩放状态
const panelPosition = ref({ x: null, y: 156 })
const panelSize = ref({ width: 480, height: null })
const isDragging = ref(false)
const isResizing = ref(false)
const resizeDirection = ref('')
const dragStart = ref({ x: 0, y: 0 })
const initialPosition = ref({ x: 0, y: 0 })
const initialSize = ref({ width: 0, height: 0 })

// 支持的编程语言
const supportedLanguages = [
  { value: 'cpp', label: 'C++', abbr: 'C++' },
  { value: 'python', label: 'Python', abbr: 'Py' },
  { value: 'java', label: 'Java', abbr: 'Java' }
]

// 获取面板标题
const getPanelTitle = computed(() => {
  const lang = supportedLanguages.find(l => l.value === selectedLanguage.value)
  return lang ? `${lang.label} Implementation` : 'Code Implementation'
})

// 获取带语法高亮的代码行
const codeLines = computed(() => {
  if (!props.code) return []

  try {
    // 使用 highlight.js 进行语法高亮
    const result = hljs.highlight(props.code, { language: selectedLanguage.value })
    const highlightedCode = result.value

    // 分割成行
    const lines = highlightedCode.split('\n')

    return lines.map(line => ({
      raw: line.replace(/<[^>]*>/g, ''), // 纯文本版本
      html: line // 带 HTML 标签的高亮版本
    }))
  } catch (error) {
    console.error('语法高亮失败:', error)
    // 如果高亮失败，返回原始代码
    return props.code.split('\n').map(line => ({
      raw: line,
      html: line
    }))
  }
})

// 当前操作显示名称
const currentOperation = computed(() => {
  if (!props.operationName) return ''
  return props.operationName
})

// 切换折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// 处理语言切换
const handleLanguageChange = async (language) => {
  if (selectedLanguage.value === language) return

  selectedLanguage.value = language

  // 如果有 structureType 和 operation，主动获取代码
  if (props.structureType && props.operation) {
    await fetchCodeForLanguage(language)
  }

  // 通知父组件语言已切换
  emit('language-change', language)
}

// 获取指定语言的代码
const fetchCodeForLanguage = async (language) => {
  // 检查缓存
  const cacheKey = `${props.structureType}_${props.operation}_${language}`
  if (loadedCode.value[cacheKey]) {
    emit('code-loaded', loadedCode.value[cacheKey])
    return
  }

  try {
    const response = await api.getCodeTemplate(props.structureType, props.operation, language)
    if (response.success) {
      loadedCode.value[cacheKey] = response.code
      emit('code-loaded', response.code)
    }
  } catch (error) {
    console.error(`获取${language}代码模板失败:`, error)
  }
}

// 面板样式计算
const panelStyle = computed(() => {
  const style = {}

  if (panelPosition.value.x !== null) {
    style.left = `${panelPosition.value.x}px`
    style.right = 'auto'
  }

  if (panelPosition.value.y !== null) {
    style.top = `${panelPosition.value.y}px`
  }

  if (panelSize.value.width !== null) {
    style.width = `${panelSize.value.width}px`
  }

  if (panelSize.value.height !== null) {
    style.height = `${panelSize.value.height}px`
  }

  return style
})

// 开始拖动
const startDrag = (e) => {
  if (e.target.closest('.lang-button') || e.target.closest('.collapse-button')) {
    return // 不在语言按钮和折叠按钮上触发拖动
  }

  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY }

  const rect = panelRef.value.getBoundingClientRect()
  initialPosition.value = { x: rect.left, y: rect.top }

  // 如果还没有设置位置，初始化位置
  if (panelPosition.value.x === null) {
    panelPosition.value.x = rect.left
  }
  if (panelPosition.value.y === null) {
    panelPosition.value.y = rect.top
  }
  if (panelSize.value.height === null) {
    panelSize.value.height = rect.height
  }

  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  e.preventDefault()
}

// 拖动过程
const onDrag = (e) => {
  if (!isDragging.value) return

  const deltaX = e.clientX - dragStart.value.x
  const deltaY = e.clientY - dragStart.value.y

  let newX = initialPosition.value.x + deltaX
  let newY = initialPosition.value.y + deltaY

  // 限制在视口内
  const minX = 0
  const minY = 0
  const maxX = window.innerWidth - panelSize.value.width
  const maxY = window.innerHeight - 50 // 至少保留 50px 可见

  newX = Math.max(minX, Math.min(newX, maxX))
  newY = Math.max(minY, Math.min(newY, maxY))

  panelPosition.value.x = newX
  panelPosition.value.y = newY
}

// 停止拖动
const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  savePosition()
}

// 开始缩放
const startResize = (direction, e) => {
  isResizing.value = true
  resizeDirection.value = direction
  dragStart.value = { x: e.clientX, y: e.clientY }

  const rect = panelRef.value.getBoundingClientRect()
  initialPosition.value = { x: rect.left, y: rect.top }
  initialSize.value = { width: rect.width, height: rect.height }

  // 初始化位置和大小
  if (panelPosition.value.x === null) {
    panelPosition.value.x = rect.left
  }
  if (panelPosition.value.y === null) {
    panelPosition.value.y = rect.top
  }
  if (panelSize.value.height === null) {
    panelSize.value.height = rect.height
  }

  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  e.preventDefault()
}

// 缩放过程
const onResize = (e) => {
  if (!isResizing.value) return

  const deltaX = e.clientX - dragStart.value.x
  const deltaY = e.clientY - dragStart.value.y

  const minWidth = 300
  const minHeight = 200

  let newWidth = initialSize.value.width
  let newHeight = initialSize.value.height
  let newX = initialPosition.value.x
  let newY = initialPosition.value.y

  // 根据方向调整大小
  if (resizeDirection.value.includes('right')) {
    newWidth = Math.max(minWidth, initialSize.value.width + deltaX)
  }
  if (resizeDirection.value.includes('left')) {
    const widthChange = -deltaX
    newWidth = Math.max(minWidth, initialSize.value.width + widthChange)
    if (newWidth > minWidth) {
      newX = initialPosition.value.x + deltaX
    }
  }
  if (resizeDirection.value.includes('bottom')) {
    newHeight = Math.max(minHeight, initialSize.value.height + deltaY)
  }
  if (resizeDirection.value.includes('top')) {
    const heightChange = -deltaY
    newHeight = Math.max(minHeight, initialSize.value.height + heightChange)
    if (newHeight > minHeight) {
      newY = initialPosition.value.y + deltaY
    }
  }

  panelSize.value.width = newWidth
  panelSize.value.height = newHeight
  panelPosition.value.x = newX
  panelPosition.value.y = newY
}

// 停止缩放
const stopResize = () => {
  isResizing.value = false
  resizeDirection.value = ''
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  savePosition()
}

// 保存位置到 localStorage
const savePosition = () => {
  const state = {
    x: panelPosition.value.x,
    y: panelPosition.value.y,
    width: panelSize.value.width,
    height: panelSize.value.height
  }
  localStorage.setItem('codePanelState', JSON.stringify(state))
}

// 从 localStorage 加载位置
const loadPosition = () => {
  try {
    const saved = localStorage.getItem('codePanelState')
    if (saved) {
      const state = JSON.parse(saved)
      panelPosition.value.x = state.x
      panelPosition.value.y = state.y
      panelSize.value.width = state.width
      panelSize.value.height = state.height
    }
  } catch (error) {
    console.error('加载面板位置失败:', error)
  }
}

// 组件挂载时加载位置
onMounted(() => {
  loadPosition()
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
})

// 当高亮行变化时,滚动到对应位置
watch(() => props.currentLine, async (newLine) => {
  if (newLine && codeContainer.value) {
    await nextTick()
    const lineElement = codeContainer.value.querySelector(`[data-line-number="${newLine}"]`)
    if (lineElement) {
      lineElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
})

// 监听 structureType 和 operation 的变化，自动获取当前语言的代码
watch([() => props.structureType, () => props.operation], async ([newType, newOp]) => {
  if (newType && newOp) {
    await fetchCodeForLanguage(selectedLanguage.value)
  }
}, { immediate: false })
</script>

<style scoped>
.code-panel {
  position: fixed;
  top: 156px;
  right: 0;
  width: 480px;
  height: calc(100vh - 326px);
  background: #1e1e1e;
  color: #d4d4d4;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease;
  z-index: 100;
  font-family: 'JetBrains Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
  border-top: 1px solid #3e3e42;
}

.code-panel.collapsed {
  transform: translateX(calc(100% - 50px));
}

/* 标题栏 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  user-select: none;
  gap: 0.5rem;
}

.panel-header:hover {
  background: #2a2a2b;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #cccccc;
  flex: 1;
  min-width: 0;
}

.panel-title {
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* 语言选择器 */
.language-selector {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.lang-button {
  padding: 0.35rem 0.65rem;
  background: #1e1e1e;
  color: #858585;
  border: 1px solid #3e3e42;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-family: 'JetBrains Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
}

.lang-button:hover {
  color: #cccccc;
  border-color: #4e4e4e;
  background: #2a2a2b;
}

.lang-button.active {
  background: #094771;
  color: #4fc3f7;
  border-color: #0369a1;
  box-shadow: 0 0 8px rgba(15, 114, 207, 0.3);
}

.collapse-button {
  background: transparent;
  border: none;
  color: #cccccc;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  transition: color 0.2s;
  flex-shrink: 0;
}

.collapse-button:hover {
  color: #ffffff;
}

.collapse-button svg {
  transition: transform 0.3s ease;
}

.collapse-button svg.rotated {
  transform: rotate(180deg);
}

/* 内容区域 */
.panel-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* 操作徽章 */
.operation-badge {
  padding: 0.5rem 1.25rem;
  background: #094771;
  color: #4fc3f7;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #1e4d69;
  flex-shrink: 0;
}

/* 代码容器 */
.code-container {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.code-block {
  margin: 0;
  padding: 0;
  font-family: 'JetBrains Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  font-weight: 400;
  letter-spacing: 0.01em;
}

.code-line {
  padding: 0.25rem 1.25rem 0.25rem 3.5rem;
  position: relative;
  transition: all 0.2s ease;
  white-space: pre-wrap;
  word-break: break-word;
  min-height: 1.5em;
  line-height: 1.5;
}

/* 行号 */
.code-line::before {
  content: attr(data-line-number);
  position: absolute;
  left: 0.75rem;
  top: 0.25rem;
  width: 2.5rem;
  text-align: right;
  color: #858585;
  font-size: 11px;
  user-select: none;
  line-height: 1.5;
}

/* 高亮行 */
.code-line.highlighted {
  background: rgba(255, 255, 0, 0.1);
  border-left: 3px solid #ffd700;
  padding-left: calc(3.5rem - 3px);
}

/* 当前执行行 - 红色强调 */
.code-line.current-line {
  background: rgba(255, 68, 68, 0.15);
  border-left: 3px solid #ef4444;
  font-weight: 600;
  animation: pulse 1.5s ease-in-out infinite;
  padding-left: calc(3.5rem - 3px);
}

.code-line.current-line::before {
  color: #ef4444;
  font-weight: 700;
}

@keyframes pulse {
  0%, 100% {
    background: rgba(255, 68, 68, 0.15);
  }
  50% {
    background: rgba(255, 68, 68, 0.25);
  }
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  color: #858585;
  text-align: center;
}

.empty-state svg {
  opacity: 0.3;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

.empty-state .hint {
  font-size: 0.75rem;
  opacity: 0.7;
}

/* 滚动条样式 */
.panel-content::-webkit-scrollbar,
.code-container::-webkit-scrollbar {
  width: 10px;
}

.panel-content::-webkit-scrollbar-track,
.code-container::-webkit-scrollbar-track {
  background: #1e1e1e;
}

.panel-content::-webkit-scrollbar-thumb,
.code-container::-webkit-scrollbar-thumb {
  background: #424242;
  border-radius: 5px;
}

.panel-content::-webkit-scrollbar-thumb:hover,
.code-container::-webkit-scrollbar-thumb:hover {
  background: #4e4e4e;
}

/* 调整大小手柄 */
.resize-handle {
  position: absolute;
  z-index: 10;
}

.resize-left,
.resize-right {
  width: 6px;
  top: 0;
  bottom: 0;
  cursor: ew-resize;
}

.resize-left {
  left: 0;
}

.resize-right {
  right: 0;
}

.resize-top,
.resize-bottom {
  height: 6px;
  left: 0;
  right: 0;
  cursor: ns-resize;
}

.resize-top {
  top: 0;
}

.resize-bottom {
  bottom: 0;
}

.resize-corner-tl,
.resize-corner-tr,
.resize-corner-bl,
.resize-corner-br {
  width: 12px;
  height: 12px;
}

.resize-corner-tl {
  top: 0;
  left: 0;
  cursor: nwse-resize;
}

.resize-corner-tr {
  top: 0;
  right: 0;
  cursor: nesw-resize;
}

.resize-corner-bl {
  bottom: 0;
  left: 0;
  cursor: nesw-resize;
}

.resize-corner-br {
  bottom: 0;
  right: 0;
  cursor: nwse-resize;
}

/* 鼠标悬停时显示手柄提示 */
.resize-handle:hover {
  background: rgba(79, 195, 247, 0.2);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .code-panel {
    width: 400px;
    top: 160px;
    height: calc(100vh - 360px);
  }

  .code-panel.collapsed {
    transform: translateX(calc(100% - 50px));
  }
}

@media (max-width: 768px) {
  .code-panel {
    width: 100%;
    top: 160px;
    height: calc(100vh - 360px);
  }

  .code-panel.collapsed {
    transform: translateX(calc(100% - 50px));
  }
}
</style>