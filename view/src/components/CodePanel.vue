<template>
  <div class="code-panel" :class="{ 'collapsed': isCollapsed }">
    <!-- 标题栏 -->
    <div class="panel-header" @click="toggleCollapse">
      <div class="header-left">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="16 18 22 12 16 6"></polyline>
          <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
        <span class="panel-title">C++ Implementation</span>
      </div>
      <button class="collapse-button">
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
        <p class="hint">Perform an operation to see the C++ implementation</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

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
  }
})

const isCollapsed = ref(false)
const codeContainer = ref(null)

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
</script>

<style scoped>
.code-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 480px;
  height: 100vh;
  background: #1e1e1e;
  color: #d4d4d4;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease;
  z-index: 100;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.code-panel.collapsed {
  transform: translateX(440px);
}

/* 标题栏 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  cursor: pointer;
  user-select: none;
}

.panel-header:hover {
  background: #2a2a2b;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #cccccc;
}

.panel-title {
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.5px;
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
}

/* 代码容器 */
.code-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.code-block {
  margin: 0;
  padding: 0;
  font-size: 0.875rem;
  line-height: 1.6;
}

.code-line {
  padding: 0.25rem 1.25rem 0.25rem 3.5rem;
  position: relative;
  transition: all 0.2s ease;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 行号 */
.code-line::before {
  content: attr(data-line-number);
  position: absolute;
  left: 1rem;
  width: 2rem;
  text-align: right;
  color: #858585;
  font-size: 0.75rem;
  user-select: none;
}

/* 高亮行 */
.code-line.highlighted {
  background: rgba(255, 255, 0, 0.1);
  border-left: 3px solid #ffd700;
}

/* 当前执行行 - 红色强调 */
.code-line.current-line {
  background: rgba(255, 68, 68, 0.15);
  border-left: 3px solid #ef4444;
  font-weight: 600;
  animation: pulse 1.5s ease-in-out infinite;
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
  }

  .code-panel.collapsed {
    transform: translateX(360px);
  }
}

@media (max-width: 768px) {
  .code-panel {
    width: 100%;
  }

  .code-panel.collapsed {
    transform: translateX(calc(100% - 40px));
  }
}
</style>
