<template>
  <div class="visualization-container">
    <!-- 顶部控制栏 -->
    <div class="control-bar">
      <div class="control-left">
        <button @click="goBack" class="btn-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>
        <h2 class="structure-title">{{ structureTitle }}</h2>
      </div>

      <div class="control-right">
        <button @click="saveStructure" class="btn-secondary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          Save
        </button>
      </div>
    </div>

    <!-- 操作面板 -->
    <div class="operation-panel">
      <div class="operation-group">
        <label class="label">Operation:</label>
        <select v-model="currentOperation" class="select-input">
          <option v-for="op in availableOperations" :key="op.value" :value="op.value">
            {{ op.label }}
          </option>
        </select>
      </div>

      <!-- value 输入框 -->
      <div v-if="needsValue" class="operation-group">
        <label class="label">Value:</label>
        <input
          v-model="inputValue"
          type="text"
          :placeholder="currentOperation === 'batch_init' ? 'e.g., 1,2,3,4 or 1 2 3 4' : 'Enter value'"
          class="text-input"
          @keyup.enter="executeOperation"
        />
      </div>

      <div v-if="needsIndex" class="operation-group">
        <label class="label">Index:</label>
        <input
          v-model="inputIndex"
          type="number"
          :placeholder="indexPlaceholder"
          class="text-input"
          @keyup.enter="executeOperation"
        />
      </div>

      <button
        @click="executeOperation"
        :disabled="isAnimating || !canExecute"
        class="btn-execute"
      >
        <span v-if="!isAnimating">Execute</span>
        <span v-else class="loading-spinner">⟳</span>
      </button>

      <button
        @click="clearStructure"
        :disabled="isAnimating"
        class="btn-clear"
      >
        Clear
      </button>
    </div>

    <!-- 可视化区域 -->
    <div class="visualization-area">
      <div class="canvas-wrapper">
        <div v-if="elements.length === 0" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <path d="M9 9h6M9 15h6"/>
          </svg>
          <p>Start adding elements...</p>
        </div>

        <div v-else class="elements-container" :class="containerClass">
          <!-- 顺序表/栈的可视化 -->
          <template v-if="structureType === 'sequential' || structureType === 'stack'">
            <div
              v-for="(element, index) in elements"
              :key="`elem-${index}`"
              class="element-wrapper"
            >
              <div
                class="element-node"
                :class="getNodeClass(index)"
              >
                <span class="element-value">{{ element }}</span>
              </div>
              <div class="element-index">[{{ index }}]</div>
              <div v-if="structureType === 'stack' && index === elements.length - 1" class="stack-top-indicator">
                TOP
              </div>
            </div>
          </template>

          <!-- 链表的可视化 -->
          <template v-if="structureType === 'linked'">
            <div
              v-for="(element, index) in elements"
              :key="`node-${index}`"
              class="linked-node-wrapper"
            >
              <div v-if="currentPointerPosition === index"class="pointer-indicator">
                <div class = "pointer-arrow">
                  👆
                </div>
                <div class="pointer-label">
                  current
                </div>
              </div>
              <div
                class="linked-node"
                :class="getNodeClass(index)"
              >
                <div class="node-value">{{ element }}</div>
                <div class="node-pointer">→</div>
              </div>
              <div class="node-index">[{{ index }}]</div>

              <!-- 箭头连接线 -->
              <div v-if="index < elements.length - 1" class="node-arrow">
                <svg width="40" height="20" viewBox="0 0 40 20">
                  <line x1="0" y1="10" x2="35" y2="10" stroke="#9ca3af" stroke-width="2"/>
                  <polygon points="35,5 40,10 35,15" fill="#9ca3af"/>
                </svg>
              </div>
            </div>
            <!-- NULL 结束标记 -->
            <div class="null-node">NULL</div>
          </template>
        </div>
      </div>
    </div>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-info">
        <span class="status-label">Elements:</span>
        <span class="status-value">{{ elements.length }}</span>
      </div>
      <div class="status-info">
        <span class="status-label">Capacity:</span>
        <span class="status-value">{{ capacity || 'Unlimited' }}</span>
      </div>
      <div v-if="lastOperation" class="status-message">
        {{ lastOperation }}
      </div>
    </div>

    <!-- 操作历史面板 -->
    <div class="history-panel" :class="{ 'collapsed': historyCollapsed }">
      <div class="history-header" @click="historyCollapsed = !historyCollapsed">
        <span class="history-title">Operation History</span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          :class="{ 'rotated': historyCollapsed }"
        >
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </div>
      <div v-if="!historyCollapsed" class="history-list">
        <div
          v-for="(op, index) in operationHistory"
          :key="index"
          class="history-item"
        >
          <span class="history-index">{{ index + 1 }}.</span>
          <span class="history-description">{{ op.description }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api.js'

const router = useRouter()
const route = useRoute()

// 数据状态
const structureType = ref(route.params.type || 'sequential')
const structureId = ref(null)
const elements = ref([])
const capacity = ref(100)
const currentOperation = ref('insert')
const inputValue = ref('')
const inputIndex = ref('')
const isAnimating = ref(false)
const highlightedIndices = ref([])
const currentPointerPosition = ref(-1)
const operationHistory = ref([])
const lastOperation = ref('')
const historyCollapsed = ref(true)

// 计算属性
const structureTitle = computed(() => {
  const titles = {
    'sequential': 'Sequential List Visualization',
    'linked': 'Linked List Visualization',
    'stack': 'Stack Visualization'
  }
  return titles[structureType.value] || 'Data Structure Visualization'
})

const availableOperations = computed(() => {
  const ops = {
    'sequential': [
      { value: 'batch_init', label: 'Batch Init' },
      { value: 'insert', label: 'Insert' },
      { value: 'delete', label: 'Delete' },
      { value: 'search', label: 'Search' }
    ],
    'linked': [
      { value: 'batch_init', label: 'Batch Init' },
      { value: 'insert', label: 'Insert' },
      { value: 'delete', label: 'Delete' },
      { value: 'search', label: 'Search' }
    ],
    'stack': [
      { value: 'batch_init', label: 'Batch Init' },
      { value: 'push', label: 'Push' },
      { value: 'pop', label: 'Pop' },
      { value: 'peek', label: 'Peek' }
    ]
  }
  return ops[structureType.value] || []
})

const needsValue = computed(() => {
  return ['batch_init','insert', 'push', 'search'].includes(currentOperation.value)
})

const batchInput = ref('')
const showBatchDialog = ref(false)

const needsIndex = computed(() => {
  return ['insert', 'delete'].includes(currentOperation.value) &&
         structureType.value !== 'stack'
})

const indexPlaceholder = computed(() => {
  return currentOperation.value === 'insert' ? 'Optional' : 'Required'
})

const canExecute = computed(() => {
  if (needsValue.value && !inputValue.value) return false
  if (needsIndex.value && currentOperation.value === 'delete' && inputIndex.value === '') return false
  return true
})

const containerClass = computed(() => {
  if (structureType.value === 'stack') return 'stack-container'
  if (structureType.value === 'linked') return 'linked-container'
  return 'sequential-container'
})

// 方法
const getNodeClass = (index) => {
  return {
    'highlighted': highlightedIndices.value.includes(index),
    'animating': isAnimating.value
  }
}

const createStructure = async () => {
  try {
    const response = await api.createStructure(structureType.value, capacity.value)
    structureId.value = response.structure_id
    console.log('Structure created:', response)
  } catch (error) {
    console.error('Failed to create structure:', error)
    alert('Failed to create data structure')
  }
}

const executeOperation = async () => {
  if (!structureId.value || !canExecute.value) return

  isAnimating.value = true

  try {
    let response
    const index = inputIndex.value === '' ? elements.value.length : parseInt(inputIndex.value)

    switch (currentOperation.value) {
      case 'batch_init':
        // 处理批量初始化
        const values = inputValue.value.split(/[,\s]+/).filter(v => v.trim())
        response = await api.initBatch(structureId.value, values)
        break
      case 'insert':
      case 'push':
        response = await api.insertElement(structureId.value, index, inputValue.value)
        break
      case 'delete':
      case 'pop':
        response = await api.deleteElement(structureId.value, index)
        break
      case 'search':
      case 'peek':
        response = await api.searchElement(structureId.value, inputValue.value)
        break
    }

    if (response) {
      elements.value = response.data
      operationHistory.value = response.operation_history || []

      if (operationHistory.value.length > 0) {
        const lastOp = operationHistory.value[operationHistory.value.length - 1]
        lastOperation.value = lastOp.description
        highlightedIndices.value = lastOp.highlight_indices || []
      }

      if (operationHistory.value.length > 0) {
        const lastOp = operationHistory.value[operationHistory.value.length - 1]
        lastOperation.value = lastOp.description
        highlightedIndices.value = lastOp.highlight_indices || []

        // 🆕 添加这部分
        if (lastOp.pointer_position >= 0) {
          // 显示指针位置（你可以用一个新的 ref 存储）
          currentPointerPosition.value = lastOp.pointer_position // 🆕 添加这行
          console.log('指针位置:', lastOp.pointer_position)
        }
        // 动画效果
        await new Promise(resolve => setTimeout(resolve, 500))
        highlightedIndices.value = []
        currentPointerPosition.value = -1 // 🆕 动画结束后重置指针
      }
      // 动画效果
      await new Promise(resolve => setTimeout(resolve, 500))
      highlightedIndices.value = []
    }

    inputValue.value = ''
    inputIndex.value = ''

  } catch (error) {
    console.error('Operation failed:', error)
    alert('Operation failed: ' + (error.response?.data?.error || error.message))
  } finally {
    isAnimating.value = false
  }
}

const clearStructure = async () => {
  if (!structureId.value) return

  try {
    await api.clearStructure(structureId.value)
    elements.value = []
    operationHistory.value = []
    lastOperation.value = 'Structure cleared'
    highlightedIndices.value = []
  } catch (error) {
    console.error('Failed to clear structure:', error)
  }
}

const saveStructure = async () => {
  if (!structureId.value) return

  try {
    // 调用导出API
    const data = await api.exportStructure(structureId.value)

    // 创建下载
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${structureType.value}_${new Date().getTime()}.json`
    a.click()
    URL.revokeObjectURL(url)

    alert('保存成功！')
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败: ' + (error.response?.data?.error || error.message))
  }
}


const goBack = () => {
  router.push('/linear')
}

// 生命周期
onMounted(async () => {
  await createStructure()
})
</script>

<style scoped>
.visualization-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  background-color: #f9fafb;
}

/* 控制栏 */
.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
}

.control-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-icon {
  padding: 0.5rem;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s;
}

.btn-icon:hover {
  color: black;
}

.structure-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: black;
}

.control-right {
  display: flex;
  gap: 0.5rem;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

/* 操作面板 */
.operation-panel {
  display: flex;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  align-items: center;
}

.operation-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.select-input,
.text-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
}

.select-input:focus,
.text-input:focus {
  border-color: black;
}

.text-input {
  width: 120px;
}

.btn-execute {
  padding: 0.5rem 1.5rem;
  background-color: black;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-left: 0.5rem;
}

.btn-execute:hover:not(:disabled) {
  background-color: #374151;
}

.btn-execute:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-clear {
  padding: 0.5rem 1rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-clear:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-clear:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* 可视化区域 */
.visualization-area {
  flex: 1;
  padding: 2rem;
  overflow: auto;
}

.canvas-wrapper {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #9ca3af;
}

.empty-state svg {
  opacity: 0.3;
}

.empty-state p {
  font-size: 1.125rem;
}

/* 元素容器 */
.elements-container {
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 2rem;
}

.sequential-container {
  flex-wrap: wrap;
}

.stack-container {
  flex-direction: column-reverse;
  align-items: center;
}

.linked-container {
  flex-wrap: nowrap;
  overflow-x: auto;
}

/* 元素节点 */
.element-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.element-node {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #10b981;
  color: white;
  font-size: 1.25rem;
  font-weight: bold;
  border-radius: 0.11rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.element-node.highlighted {
  background-color: #ef4444;
  transform: scale(1.15);
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.3);
}

.element-value {
  user-select: none;
}

.element-index {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stack-top-indicator {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: #ef4444;
  background-color: #fee2e2;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

/* 链表节点 */
.linked-node-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.pointer-indicator {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: pointerBounce 0.6s ease-in-out infinite;
  z-index: 10;
}

.pointer-arrow {
  font-size: 2rem;
  animation: bounce 1s ease-in-out infinite;
}

.pointer-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #ef4444;
  background-color: #fee2e2;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  margin-top: 0.25rem;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.linked-node {
  display: flex;
  align-items: center;
  background-color: #10b981;
  color: white;
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.linked-node.highlighted {
  background-color: #ef4444;
  transform: scale(1.15);
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.3);
}

.node-value {
  padding: 1.5rem;
  font-size: 1.25rem;
  font-weight: bold;
  border-right: 2px solid rgba(255, 255, 255, 0.3);
}

.node-pointer {
  padding: 0 1rem;
  font-size: 1.5rem;
}

.node-index {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.node-arrow {
  position: absolute;
  right: -40px;
  top: 35%;
}

.null-node {
  padding: 1rem 1.5rem;
  background-color: #6b7280;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 0.5rem;
  opacity: 0.5;
}

/* 状态栏 */
.status-bar {
  display: flex;
  gap: 2rem;
  padding: 0.75rem 2rem;
  background-color: white;
  border-top: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

.status-info {
  display: flex;
  gap: 0.5rem;
}

.status-label {
  color: #6b7280;
  font-weight: 500;
}

.status-value {
  color: black;
  font-weight: 600;
}

.status-message {
  flex: 1;
  color: #10b981;
  font-weight: 500;
}

/* 操作历史面板 */
.history-panel {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 400px;
  max-height: 50vh;
  background-color: white;
  border-left: 1px solid #e5e7eb;
  border-top: 1px solid #e5e7eb;
  box-shadow: -4px 0 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.history-panel.collapsed {
  transform: translateY(calc(100% - 40px));
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  cursor: pointer;
  user-select: none;
}

.history-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

.history-header svg {
  transition: transform 0.3s ease;
}

.history-header svg.rotated {
  transform: rotate(180deg);
}

.history-list {
  max-height: calc(50vh - 40px);
  overflow-y: auto;
  padding: 0.5rem;
}

.history-item {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  font-size: 0.875rem;
  border-bottom: 1px solid #f3f4f6;
}

.history-index {
  color: #9ca3af;
  font-weight: 600;
  min-width: 2rem;
}

.history-description {
  color: #374151;
  flex: 1;
}

@media (max-width: 768px) {
  .operation-panel {
    flex-wrap: wrap;
  }

  .history-panel {
    width: 100%;
  }
}
</style>
