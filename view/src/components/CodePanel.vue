<template>
  <div class="code-panel" :class="{ 'collapsed': isCollapsed }">
    <!-- 标题栏 -->
    <div class="panel-header">
      <div class="header-left" @click="toggleCollapse" style="cursor: pointer;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="16 18 22 12 16 6"></polyline>
          <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
        <span class="panel-title">{{ getPanelTitle }}</span>
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

      <button class="collapse-button" @click="toggleCollapse">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'rotated': isCollapsed }">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
    </div>

    <!-- 代码内容区域 -->
    <div v-if="!isCollapsed" class="panel-content">
      <!-- 当前操作函数名 -->
      <div v-if="currentOperation" class="operation-badge">
        {{ currentOperation }}
      </div>

      <!-- 代码显示区 -->
      <div class="code-container" ref="codeContainer">
        <pre class="code-block"><code><div
            v-for="(line, index) in codeLines"
            :key="index"
            class="code-line"
            :class="{
              'highlighted': highlightedLines.includes(index + 1),
              'current-line': currentLine === index + 1
            }"
            :data-line-number="index + 1"
          >{{ line }}</div></code></pre>
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
import { ref, computed, watch, nextTick } from 'vue'
import api from '../services/api.js'

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
const selectedLanguage = ref('cpp')
const loadedCode = ref({})  // 缓存已加载的代码 {language: code}

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

// 将代码分割成行
const codeLines = computed(() => {
  if (!props.code) return []
  return props.code.split('\n')
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

// 当高亮行变化时，滚动到对应位置
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
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  border-top: 1px solid #3e3e42;
}

.code-panel.collapsed {
  transform: translateX(440px);
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
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
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
  font-size: 0.875rem;
  line-height: 1.6;
}

.code-line {
  padding: 0.35rem 1.25rem 0.35rem 3.5rem;
  position: relative;
  transition: all 0.2s ease;
  white-space: pre-wrap;
  word-break: break-word;
  min-height: 1.6em;
}

/* 行号 */
.code-line::before {
  content: attr(data-line-number);
  position: absolute;
  left: 0.75rem;
  top: 0.35rem;
  width: 2.5rem;
  text-align: right;
  color: #858585;
  font-size: 0.75rem;
  user-select: none;
  line-height: 1.6;
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .code-panel {
    width: 400px;
    top: 160px;
    height: calc(100vh - 360px);
  }

  .code-panel.collapsed {
    transform: translateX(360px);
  }
}

@media (max-width: 768px) {
  .code-panel {
    width: 100%;
    top: 160px;
    height: calc(100vh - 360px);
  }

  .code-panel.collapsed {
    transform: translateX(calc(100% - 40px));
  }
}
</style>