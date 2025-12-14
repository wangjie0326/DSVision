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

      <!-- 输入框 + LLM 模型显示 -->
      <div class="input-wrapper">
        <div class="input-section">
          <textarea
            v-if="currentMode === 'dsl'"
            v-model="dslInput"
            @keydown.ctrl.enter="handleExecute"
            placeholder="Enter DSL code... (Ctrl+Enter to execute)"
            class="dsl-textarea"
            rows="3"
          />
          <div v-else class="llm-input-container">
            <input
              v-model="llmInput"
              @keyup.enter="handleExecute"
              type="text"
              placeholder="Natural language instruction..."
              class="llm-input"
            />
            <span class="llm-model-badge">{{ currentLLMModel }}</span>
          </div>
        </div>
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

      <!-- LLM 推理可视化 -->
      <div
        v-if="currentMode === 'llm' && llmShowcase"
        class="llm-visualizer"
        :class="{
          'float-in': !llmFadingOut,
          'fade-out': llmFadingOut
        }"
      >
        <div class="llm-label">
          <span class="glow-dot"></span>
          LLM Chat
        </div>
        <div class="llm-panels">
          <div class="panel glass">
            <div class="panel-title">Reasoning</div>
            <div class="typing-line" :class="{ active: llmStage === 'reasoning' || llmStage === 'dsl' }">
              <pre>{{ llmReasoning }}</pre>
              <span class="caret" v-if="llmStage === 'reasoning'"></span>
            </div>
          </div>
          <div class="panel code">
            <div class="panel-title">DSL</div>
            <div class="typing-block" :class="{ active: llmStage === 'dsl' || llmStage === 'complete' }">
              <pre>{{ llmDSL }}</pre>
              <span class="caret" v-if="llmStage === 'dsl'"></span>
            </div>
          </div>
        </div>
        <div class="stage-footer" v-if="llmStage === 'complete'">
          <span class="pill success">Ready</span>
        </div>
        <div class="cloud-wrapper" v-if="llmStage === 'reject'">
          <div class="cloud-bubble">
            {{ cloudMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'

const router = useRouter()

// 🔥 接收当前页面的结构状态
const props = defineProps({
  currentStructureType: {
    type: String,
    default: null
  },
  currentStructureName: {
    type: String,
    default: null
  },
  currentStructureId: {
    type: String,
    default: null
  },
  currentElements: {
    type: Array,
    default: () => []
  },
  currentTreeData: {
    type: Object,
    default: null
  },
  category: {
    type: String,
    default: null  // 'linear' 或 'tree'
  }
})

// 状态
const isCollapsed = ref(false)
const currentMode = ref('dsl')
const dslInput = ref('')
const llmInput = ref('')
const statusMessage = ref('')
const statusType = ref('info')  // 'info' | 'success' | 'error'
const currentLLMModel = ref('gpt-3.5-turbo')  // LLM 模型显示

// LLM 会话状态
const llmSessionId = ref(null)  // LLM 会话 ID
const llmShowcase = ref(false)
const llmFadingOut = ref(false)
const llmStage = ref('idle') // idle | reasoning | dsl | complete | reject
const llmReasoning = ref('')
const llmDSL = ref('')
const cloudMessage = ref('')

const exampleButtons = [
  { type: 'sequential', label: 'Sequential' },
  { type: 'queue', label: 'Queue' },
  { type: 'bst', label: 'BST' },
  { type: 'stack', label: 'Stack' },
]

// 初始化：加载 LLM 配置
onMounted(async () => {
  try {
    const config = await api.getLLMConfig()
    if (config.provider && config.base_url) {
      currentLLMModel.value = `${config.provider} - ${config.base_url.split('//')[1]?.split('.')[0] || 'custom'}`
    } else if (config.provider) {
      currentLLMModel.value = config.provider
    }
  } catch (e) {
    console.error('Failed to load LLM config:', e)
    currentLLMModel.value = 'LLM'
  }
})

const canExecute = computed(() => {
  if (currentMode.value === 'dsl') {
    return dslInput.value.trim().length > 0
  }
  return llmInput.value.trim().length > 0
})

watch(currentMode, (mode) => {
  if (mode === 'llm') {
    llmShowcase.value = false
    llmStage.value = 'idle'
    llmReasoning.value = ''
    llmDSL.value = ''
    cloudMessage.value = ''
    llmFadingOut.value = false
  }
})

// 🔥 从树结构中提取节点值/ID（中序遍历）
const extractTreeValues = (node) => {
  if (!node) return []
  const values = []
  const inorder = (n) => {
    if (!n) return
    if (n.left) inorder(n.left)
    values.push(n.value)
    if (n.right) inorder(n.right)
  }
  inorder(node)
  return values
}

const extractTreeNodes = (node) => {
  if (!node) return []
  const nodes = []
  const traverse = (n) => {
    if (!n) return
    nodes.push({ id: n.node_id, value: n.value })
    traverse(n.left)
    traverse(n.right)
  }
  traverse(node)
  return nodes
}

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

    // 🔥 修复: 使用正确的 API 调用
    const response = await api.executeDSL(dslInput.value)

    console.log('✅ DSL 执行成功:', response)

    if (!response.success) {
      statusMessage.value = `错误: ${response.error}`
      statusType.value = 'error'
      setTimeout(() => { statusMessage.value = '' }, 5000)
      return
    }

    statusMessage.value = '✓ 执行成功! 正在跳转...'
    statusType.value = 'success'

    // 🔥 修复: 正确处理返回数据
    if (response.structures && response.structures.length > 0) {
      const firstStruct = response.structures[0]
      const category = firstStruct.category  // 'linear' 或 'tree'
      const type = firstStruct.type
      const structureId = firstStruct.structure_id
      const structName = firstStruct.name
      // 复用当前名称（若同一结构），避免频繁改名导致混乱
      const resolvedName = (props.currentStructureId && props.currentStructureId === structureId && props.currentStructureName)
        ? props.currentStructureName
        : (structName || props.currentStructureName)

      console.log('📊 跳转信息:', { category, type, structureId })

      // 🔥 关键：检查是否已经在目标页面
      const targetPath = category === 'linear' ? `/linear/${type}` : `/tree/${type}`
      const currentPath = router.currentRoute.value.path
      const currentImportId = router.currentRoute.value.query.importId

      setTimeout(() => {
        if (currentPath === targetPath && currentImportId === structureId) {
          // 已经在目标页面且是同一个结构，强制刷新
          console.log('🔄 当前页面已是目标页面，强制刷新...')
          window.location.href = `${targetPath}?importId=${structureId}&fromDSL=true&structName=${encodeURIComponent(resolvedName || '')}&_refresh=${Date.now()}`
        } else {
          // 跳转到新页面
          if (category === 'linear') {
            router.push({
              path: `/linear/${type}`,
              query: { importId: structureId, fromDSL: 'true', structName: resolvedName }
            })
          } else {
            router.push({
              path: `/tree/${type}`,
              query: { importId: structureId, fromDSL: 'true', structName: resolvedName }
            })
          }
        }
      }, 800)
    } else {
      statusMessage.value = '⚠️ 执行成功但没有返回数据结构'
      statusType.value = 'error'
      setTimeout(() => { statusMessage.value = '' }, 3000)
    }
  } catch (error) {
    console.error('❌ DSL 执行失败:', error)
    statusMessage.value = '执行失败: ' + (error.response?.data?.error || error.message)
    statusType.value = 'error'
    setTimeout(() => { statusMessage.value = '' }, 5000)
  }
}

// 执行 LLM
const typeWriter = async (text, targetRef, speed = 12) => {
  targetRef.value = ''
  for (let i = 0; i < text.length; i++) {
    targetRef.value += text[i]
    await new Promise(resolve => setTimeout(resolve, speed))
  }
}

const executeLLM = async () => {
  try {
    statusMessage.value = '正在推理中...'
    statusType.value = 'info'
    llmFadingOut.value = false
    llmShowcase.value = true
    llmStage.value = 'reasoning'
    llmReasoning.value = '模型推理中...'
    llmDSL.value = ''
    cloudMessage.value = ''

    // 🔥 构建上下文对象 - 使用当前页面的状态
    let context = null
    if (props.currentStructureType && props.currentStructureId) {
      // 如果当前页面有结构，构建上下文对象
      let currentData = []

      if (props.category === 'linear' && props.currentElements) {
        // 线性结构：使用elements数组（已经是简单数组，直接filter掉null/undefined）
        currentData = props.currentElements.filter(el => el !== null && el !== undefined)
      } else if (props.category === 'tree' && props.currentTreeData) {
        // 树结构：提取树节点值（中序遍历）
        currentData = extractTreeValues(props.currentTreeData.root || props.currentTreeData)
      }

      const treeNodes = (props.category === 'tree' && props.currentTreeData)
        ? extractTreeNodes(props.currentTreeData.root || props.currentTreeData)
        : []

      context = {
        current_page: {
          category: props.category,  // 'linear' 或 'tree'
          type: props.currentStructureType,  // 'sequential', 'bst', etc.
          name: props.currentStructureName || '',
          structure_id: props.currentStructureId,
          data: currentData,
          nodes: treeNodes
        }
      }

      console.log('🔥 LLM上下文:', context)
    }

    const response = await api.llmChat(llmInput.value, llmSessionId.value, context)

    console.log('✅ LLM 推理成功:', response)

    if (!response.success) {
      statusMessage.value = `错误: ${response.error}`
      statusType.value = 'error'
      cloudMessage.value = response.error || '无法生成 DSL 代码'
      llmStage.value = 'reject'
      setTimeout(() => { statusMessage.value = '' }, 5000)
      return
    }

    // 显示推理结果
    const llmResponse = response.llm_response
    const dslCode = llmResponse.dsl_code
    const explanation = llmResponse.explanation

    // 如果 DSL 代码为空，显示 LLM 的解释（通常是拒绝信息）
    if (!dslCode || dslCode.trim() === '') {
      cloudMessage.value = explanation || '无法生成 DSL 代码'
      llmStage.value = 'reject'
      statusMessage.value = explanation || '无法生成 DSL 代码'
      statusType.value = 'info'
      setTimeout(() => { statusMessage.value = '' }, 5000)
      return
    }

    llmReasoning.value = ''
    await typeWriter(explanation || '', llmReasoning, 18)
    llmStage.value = 'dsl'
    await typeWriter(dslCode, llmDSL, 12)
    llmStage.value = 'complete'

    statusMessage.value = `✓ 推理成功! DSL: ${dslCode.substring(0, 50)}...`
    statusType.value = 'success'

    // 如果有执行结果，跳转到对应视图
    if (response.execution?.success && response.execution?.structures?.length > 0) {
      const firstStruct = response.execution.structures[0]
      const category = firstStruct.category  // 'linear' 或 'tree'
      const type = firstStruct.type
      const structureId = firstStruct.structure_id

      // 保存 LLM session ID 用于会话记忆
      if (response.session_id) {
        llmSessionId.value = response.session_id
      }

      console.log('📊 跳转信息:', { category, type, structureId })

      // 🔥 关键：检查是否已经在目标页面
      const targetPath = category === 'linear' ? `/linear/${type}` : `/tree/${type}`
      const currentPath = router.currentRoute.value.path
      const currentImportId = router.currentRoute.value.query.importId

      setTimeout(() => {
        if (currentPath === targetPath && currentImportId === structureId) {
          // 已经在目标页面且是同一个结构，强制刷新
          console.log('🔄 当前页面已是目标页面，强制刷新...')
          llmFadingOut.value = true
          window.location.href = `${targetPath}?importId=${structureId}&fromDSL=true&_refresh=${Date.now()}`
        } else {
          // 跳转到新页面
          llmFadingOut.value = true
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
        }
        setTimeout(() => {
          llmShowcase.value = false
        }, 500)
      }, 800)
    } else if (response.execution?.error) {
      statusMessage.value = `推理成功但执行失败: ${response.execution.error}`
      statusType.value = 'error'
      setTimeout(() => { statusMessage.value = '' }, 5000)
    } else {
      // 只有推理结果，没有执行，将 DSL 代码放到编辑框
      dslInput.value = dslCode
      currentMode.value = 'dsl'
      statusMessage.value = '✓ 已生成 DSL 代码，可点击执行'
      setTimeout(() => { statusMessage.value = '' }, 3000)
    }
  } catch (error) {
    console.error('❌ LLM 推理失败:', error)
    statusMessage.value = '推理失败: ' + (error.response?.data?.error || error.message)
    statusType.value = 'error'
    cloudMessage.value = error.response?.data?.error || error.message || '推理失败'
    llmStage.value = 'reject'
    setTimeout(() => { statusMessage.value = '' }, 5000)
  }
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

.input-section {
  flex: 1;
  position: relative;
}

.dsl-textarea,
.llm-input {
  flex: 1;
  width: 100%;
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
  padding-right: 120px;
}

.llm-input-container {
  position: relative;
  width: 100%;
}

.llm-model-badge {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  white-space: nowrap;
  pointer-events: none;
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

/* LLM visualizer (同步首页动画风格) */
.llm-visualizer {
  margin-top: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: #0f172a;
  box-shadow: 0 12px 35px rgba(15, 23, 42, 0.12);
  transform-origin: bottom;
}

.llm-visualizer.float-in {
  animation: floatUp 0.45s ease;
}

.llm-visualizer.fade-out {
  opacity: 0;
  transform: translateY(-8px);
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.llm-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 0.95rem;
  margin-bottom: 0.75rem;
}

.glow-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #22d3ee;
  box-shadow: 0 0 12px #22d3ee, 0 0 24px #22d3ee;
}

.llm-panels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.75rem;
}

.panel {
  border-radius: 12px;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
}

.panel.glass {
  background: #ffffff;
}

.panel.code {
  background: #f1f5f9;
}

.panel-title {
  font-weight: 700;
  margin-bottom: 0.4rem;
  font-size: 0.9rem;
}

.typing-line,
.typing-block {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.6rem;
  min-height: 60px;
  position: relative;
}

.typing-line.active,
.typing-block.active {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.25);
}

.typing-line pre,
.typing-block pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: "SFMono-Regular", Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 0.85rem;
}

.caret {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: 6px;
  height: 16px;
  background: #0ea5e9;
  animation: blink 1s step-start infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.stage-footer {
  margin-top: 0.5rem;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  border: 1px solid #0ea5e9;
  color: #0b7bc1;
  background: rgba(14, 165, 233, 0.1);
}

.pill.success {
  background: rgba(14, 165, 233, 0.15);
}

.cloud-wrapper {
  margin-top: 0.75rem;
  display: flex;
  justify-content: center;
}

.cloud-bubble {
  background: #fef3c7;
  color: #92400e;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid #fcd34d;
  max-width: 100%;
  font-size: 0.9rem;
}

@keyframes floatUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
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
