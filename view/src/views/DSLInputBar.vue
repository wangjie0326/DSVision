<template>
  <div class="dsl-input-bar" :class="{ collapsed: isCollapsed }">
    <!-- 🔥 折叠/展开按钮 -->
    <button @click="isCollapsed = !isCollapsed" class="collapse-button">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        :class="{ rotated: isCollapsed }"
      >
        <polyline points="18 15 12 9 6 15"/>
      </svg>
    </button>

    <!-- 内容区域 -->
    <div v-if="!isCollapsed" class="input-content">
      <!-- 模式选择 + 示例按钮 -->
      <div class="top-controls">
        <div class="mode-selector">
          <button
            @click="currentMode = 'dsl'"
            class="mode-button"
            :class="{ active: currentMode === 'dsl' }"
          >
            DSL Coding
          </button>
          <button
            @click="currentMode = 'llm'"
            class="mode-button"
            :class="{ active: currentMode === 'llm' }"
          >
            LLM
          </button>
        </div>

        <!-- DSL 示例按钮 -->
        <div v-if="currentMode === 'dsl'" class="examples-row">
          <button
            v-for="example in exampleButtons"
            :key="example.type"
            @click="loadExample(example.type)"
            class="example-btn"
          >
            {{ example.label }}
          </button>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-wrapper">
        <textarea
          v-if="currentMode === 'dsl'"
          v-model="dslInput"
          @keydown.ctrl.enter="handleExecute"
          placeholder="Enter DSL code... (Ctrl+Enter to execute)"
          class="dsl-textarea"
          rows="3"
        />
        <input
          v-else
          v-model="llmInput"
          @keyup.enter="handleExecute"
          type="text"
          placeholder="Natural language instruction..."
          class="llm-input"
        />
        <button
          @click="handleExecute"
          class="execute-button"
          :disabled="!canExecute"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12l14-7-4 7 4 7-14-7z" />
          </svg>
        </button>
      </div>

      <!-- 执行状态提示 -->
      <div v-if="statusMessage" class="status-message" :class="statusType">
        {{ statusMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 状态
const isCollapsed = ref(false)
const currentMode = ref('dsl')
const dslInput = ref('')
const llmInput = ref('')
const statusMessage = ref('')
const statusType = ref('info')  // 'info' | 'success' | 'error'

const exampleButtons = [
  { type: 'sequential', label: 'Sequential' },
  { type: 'bst', label: 'BST' },
  { type: 'stack', label: 'Stack' }
]

const canExecute = computed(() => {
  if (currentMode.value === 'dsl') {
    return dslInput.value.trim().length > 0
  }
  return llmInput.value.trim().length > 0
})

// 执行代码
const handleExecute = async () => {
  if (!canExecute.value) return

  if (currentMode.value === 'dsl') {
    await executeDSL()
  } else {
    await executeLLM()
  }
}

// 执行 DSL
const executeDSL = async () => {
  try {
    statusMessage.value = '正在执行 DSL 代码...'
    statusType.value = 'info'

    const response = await fetch('/api/dsl/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: dslInput.value })
    })

    const result = await response.json()

    if (!response.ok) {
      statusMessage.value = `错误: ${result.error}`
      statusType.value = 'error'
      setTimeout(() => { statusMessage.value = '' }, 5000)
      return
    }

    statusMessage.value = '✓ 执行成功! 正在跳转...'
    statusType.value = 'success'

    // 跳转到可视化页面
    if (result.structures && result.structures.length > 0) {
      const firstStruct = result.structures[0]
      const category = firstStruct.category
      const type = firstStruct.type
      const structureId = firstStruct.structure_id

      setTimeout(() => {
        if (category === 'linear') {
          router.push({
            path: `/linear/${type}`,
            query: { importId: structureId, fromDSL: 'true' }
          })
        } else {
          router.push({
            path: `/tree/${type}`,
            query: { importId: structureId, fromDSL: 'true' }
          })
        }
      }, 800)
    }
  } catch (error) {
    console.error('DSL 执行失败:', error)
    statusMessage.value = '执行失败: ' + error.message
    statusType.value = 'error'
    setTimeout(() => { statusMessage.value = '' }, 5000)
  }
}

// 执行 LLM
const executeLLM = async () => {
  statusMessage.value = 'LLM 功能开发中...'
  statusType.value = 'info'
  setTimeout(() => { statusMessage.value = '' }, 3000)
}

// 加载示例
const loadExample = async (exampleType) => {
  try {
    const response = await fetch('/api/dsl/examples')
    const data = await response.json()

    if (data.examples && data.examples[exampleType]) {
      dslInput.value = data.examples[exampleType]
      statusMessage.value = `已加载 ${exampleType} 示例`
      statusType.value = 'success'
      setTimeout(() => { statusMessage.value = '' }, 2000)
    }
  } catch (error) {
    console.error('加载示例失败:', error)
  }
}
</script>

<style scoped>
.dsl-input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 2px solid #e5e7eb;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  z-index: 100;
}

.dsl-input-bar.collapsed {
  transform: translateY(calc(100% - 40px));
}

.collapse-button {
  position: absolute;
  top: -40px;
  right: 2rem;
  width: 40px;
  height: 40px;
  background: white;
  border: 2px solid #e5e7eb;
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.collapse-button:hover {
  background: #f3f4f6;
}

.collapse-button svg {
  transition: transform 0.3s ease;
}

.collapse-button svg.rotated {
  transform: rotate(180deg);
}

.input-content {
  padding: 1rem 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.mode-selector {
  display: flex;
  gap: 0.75rem;
}

.mode-button {
  padding: 0.4rem 1.25rem;
  border-radius: 9999px;
  border: 1.5px solid black;
  background: white;
  color: black;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-button.active {
  background: black;
  color: white;
}

.mode-button:hover:not(.active) {
  background: #f3f4f6;
}

.examples-row {
  display: flex;
  gap: 0.5rem;
}

.example-btn {
  padding: 0.35rem 0.85rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.example-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.dsl-textarea,
.llm-input {
  flex: 1;
  padding: 0.75rem;
  border-radius: 0.75rem;
  border: 1px solid #d1d5db;
  outline: none;
  font-size: 0.875rem;
  font-family: 'Consolas', 'Monaco', monospace;
  resize: vertical;
}

.dsl-textarea {
  min-height: 80px;
}

.llm-input {
  height: 44px;
}

.dsl-textarea:focus,
.llm-input:focus {
  border-color: black;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.execute-button {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: black;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.execute-button:hover:not(:disabled) {
  background: #374151;
  transform: scale(1.05);
}

.execute-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  opacity: 0.5;
}

.status-message {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  text-align: center;
}

.status-message.info {
  background: #dbeafe;
  color: #1e40af;
}

.status-message.success {
  background: #d1fae5;
  color: #065f46;
}

.status-message.error {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 768px) {
  .top-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .examples-row {
    justify-content: center;
  }
}
</style>
