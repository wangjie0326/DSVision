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

      <!-- Huffman树特殊输入 -->
      <template v-if="structureType === 'huffman' && currentOperation === 'build'">
        <div class="operation-group">
          <label class="label">Input Text:</label>
          <input
            v-model="huffmanText"
            type="text"
            placeholder="Enter text for Huffman encoding"
            class="text-input text-input-wide"
            @keyup.enter="executeOperation"
          />
        </div>
      </template>

      <!-- 普通值输入 -->
      <div v-else-if="needsValue" class="operation-group">
        <label class="label">Value:</label>
        <input
          v-model="inputValue"
          type="text"
          placeholder="Enter value"
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
        <div v-if="!treeData || !treeData.root" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <circle cx="12" cy="5" r="3"/>
            <circle cx="6" cy="15" r="3"/>
            <circle cx="18" cy="15" r="3"/>
            <path d="M10 7l-2 6M14 7l2 6"/>
          </svg>
          <p>Start building the tree...</p>
        </div>

        <div v-else class="tree-canvas">
          <TreeNode
            :node="treeData.root"
            :highlighted="highlightedNodes"
            :isHuffman="structureType === 'huffman'"
          />
        </div>
      </div>
    </div>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-info">
        <span class="status-label">Nodes:</span>
        <span class="status-value">{{ treeData?.size || 0 }}</span>
      </div>
      <div class="status-info">
        <span class="status-label">Height:</span>
        <span class="status-value">{{ treeData?.height || 0 }}</span>
      </div>
      <div v-if="structureType === 'bst' && treeData?.min !== undefined" class="status-info">
        <span class="status-label">Min:</span>
        <span class="status-value">{{ treeData.min }}</span>
      </div>
      <div v-if="structureType === 'bst' && treeData?.max !== undefined" class="status-info">
        <span class="status-label">Max:</span>
        <span class="status-value">{{ treeData.max }}</span>
      </div>
      <div v-if="lastOperation" class="status-message">
        {{ lastOperation }}
      </div>
    </div>

    <!-- Huffman编码表（仅Huffman树显示） -->
    <div v-if="structureType === 'huffman' && huffmanCodes" class="huffman-panel">
      <div class="huffman-header">
        <span class="huffman-title">Huffman Codes</span>
      </div>
      <div class="huffman-codes">
        <div v-for="(code, char) in huffmanCodes" :key="char" class="code-item">
          <span class="code-char">{{ char }}:</span>
          <span class="code-value">{{ code }}</span>
        </div>
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
import TreeNode from '../views/TreeNode.vue'

const router = useRouter()
const route = useRoute()

// 数据状态
const structureType = ref(route.params.type || 'binary')
const structureId = ref(null)
const treeData = ref(null)
const currentOperation = ref('insert')
const inputValue = ref('')
const huffmanText = ref('')
const isAnimating = ref(false)
const highlightedNodes = ref([])
const operationHistory = ref([])
const lastOperation = ref('')
const historyCollapsed = ref(true)
const huffmanCodes = ref(null)

// 计算属性
const structureTitle = computed(() => {
  const titles = {
    'binary': 'Binary Tree Visualization',
    'bst': 'Binary Search Tree Visualization',
    'huffman': 'Huffman Tree Visualization'
  }
  return titles[structureType.value] || 'Tree Structure Visualization'
})

const availableOperations = computed(() => {
  const ops = {
    'binary': [
      { value: 'insert', label: 'Insert' },
      { value: 'delete', label: 'Delete' },
      { value: 'search', label: 'Search' }
    ],
    'bst': [
      { value: 'insert', label: 'Insert' },
      { value: 'delete', label: 'Delete' },
      { value: 'search', label: 'Search' }
    ],
    'avl': [  // 添加这个
      { value: 'insert', label: 'Insert' },
      { value: 'delete', label: 'Delete' },
      { value: 'search', label: 'Search' }
    ],
    'huffman': [
      { value: 'build', label: 'Build from Text' },
      { value: 'search', label: 'Search Node' }
    ]
  }
  return ops[structureType.value] || []
})

const needsValue = computed(() => {
  if (structureType.value === 'huffman') {
    return currentOperation.value === 'search'
  }
  return ['insert', 'delete', 'search'].includes(currentOperation.value)
})

const canExecute = computed(() => {
  if (structureType.value === 'huffman' && currentOperation.value === 'build') {
    return huffmanText.value.trim().length > 0
  }
  if (needsValue.value && !inputValue.value) return false
  return true
})

// 方法
const createStructure = async () => {
  try {
    const response = await api.createTreeStructure(structureType.value)
    structureId.value = response.structure_id
    console.log('Tree structure created:', response)
  } catch (error) {
    console.error('Failed to create tree structure:', error)
    alert('Failed to create tree structure')
  }
}

const executeOperation = async () => {
  if (!structureId.value || !canExecute.value) return

  isAnimating.value = true

  try {
    let response

    switch (currentOperation.value) {
      case 'insert':
        response = await api.insertTreeNode(structureId.value, inputValue.value)
        break
      case 'delete':
        response = await api.deleteTreeNode(structureId.value, inputValue.value)
        break
      case 'search':
        response = await api.searchTreeNode(structureId.value, inputValue.value)
        break
      case 'build':
        if (structureType.value === 'huffman') {
          response = await api.buildHuffmanTree(structureId.value, huffmanText.value)
        }
        break
    }

    if (response) {
      treeData.value = response.tree_data
      operationHistory.value = response.operation_history || []

      // 更新Huffman编码表
      if (structureType.value === 'huffman' && response.tree_data?.huffman_codes) {
        huffmanCodes.value = response.tree_data.huffman_codes
      }

      if (operationHistory.value.length > 0) {
        const lastOp = operationHistory.value[operationHistory.value.length - 1]
        lastOperation.value = lastOp.description
      }

      // 动画效果
      await new Promise(resolve => setTimeout(resolve, 500))
      highlightedNodes.value = []
    }

    inputValue.value = ''
    huffmanText.value = ''

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
    await api.clearTreeStructure(structureId.value)
    treeData.value = null
    operationHistory.value = []
    huffmanCodes.value = null
    lastOperation.value = 'Structure cleared'
    highlightedNodes.value = []
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
  router.push('/tree')
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
  flex-wrap: wrap;
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

.text-input-wide {
  width: 300px;
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
  align-items: flex-start;
  justify-content: center;
  padding-top: 2rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #9ca3af;
  margin-top: 4rem;
}

.empty-state svg {
  opacity: 0.3;
}

.empty-state p {
  font-size: 1.125rem;
}

.tree-canvas {
  width: 100%;
  display: flex;
  justify-content: center;
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

/* Huffman编码表 */
.huffman-panel {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  width: 300px;
  max-height: 60vh;
  background-color: white;
  border-left: 1px solid #e5e7eb;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: -4px 0 6px -1px rgba(0, 0, 0, 0.1);
}

.huffman-header {
  padding: 0.75rem 1rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.huffman-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

.huffman-codes {
  max-height: calc(60vh - 40px);
  overflow-y: auto;
  padding: 0.5rem;
}

.code-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  font-size: 0.875rem;
  border-bottom: 1px solid #f3f4f6;
  font-family: monospace;
}

.code-char {
  color: #374151;
  font-weight: 600;
}

.code-value {
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
    flex-direction: column;
    align-items: stretch;
  }

  .history-panel,
  .huffman-panel {
    width: 100%;
  }
}
</style>
