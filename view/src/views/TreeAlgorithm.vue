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

      <!-- 动画速度控制 -->
      <div class="operation-group">
        <label class="label">Speed:</label>
        <select v-model="animationSpeed" class="select-input">
          <option :value="0.5">0.5x (慢)</option>
          <option :value="1">1x (正常)</option>
          <option :value="2">2x (快)</option>
          <option :value="4">4x (很快)</option>
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
    <div class="visualization-area" ref="visualAreaRef">
      <div class="canvas-wrapper">
        <div v-if="!treeData || !treeData.root || treeData.size === 0" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <circle cx="12" cy="5" r="3"/>
            <circle cx="6" cy="15" r="3"/>
            <circle cx="18" cy="15" r="3"/>
            <path d="M10 7l-2 6M14 7l2 6"/>
          </svg>
          <p>Start building the tree...</p>
        </div>

        <div v-else class="tree-canvas">
          <!-- SVG层：绘制连接线 -->
          <svg
            :width="canvasSize.width"
            :height="canvasSize.height"
            class="connection-svg"
          >
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="10"
                refX="9"
                refY="3"
                orient="auto"
                markerUnits="strokeWidth"
              >
                <path d="M0,0 L0,6 L9,3 z" fill="#6b7280" />
              </marker>
            </defs>
            <g class="edges-layer">
              <line
                v-for="edge in edges"
                :key="edge.id"
                :x1="edge.start.x"
                :y1="edge.start.y"
                :x2="edge.end.x"
                :y2="edge.end.y"
                stroke="#6b7280"
                stroke-width="2"
                stroke-linecap="round"
                marker-end="url(#arrowhead)"
                class="edge-line"
              />
            </g>
          </svg>

          <!-- 节点层：绝对定位 -->
          <div
            class="nodes-layer"
            :style="{
              width: `${canvasSize.width}px`,
              height: `${canvasSize.height}px`
            }"
          >
            <TreeNodeComponent
              v-for="(position, nodeId) in nodePositions"
              :key="nodeId"
              :node="findNodeById(treeData.root, parseInt(nodeId))"
              :position="position"
              :highlighted="highlightedNodes"
              :isHuffman="structureType === 'huffman'"
            />
          </div>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api.js'
import TreeNodeComponent from './TreeNodeSimple.vue'
import { TreeLayoutEngine } from '../utils/treeLayout.js'
import DSLInputBar from './DSLInputBar.vue'  // 🔥 添加导入

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
const animationSpeed = ref(1)
const visualAreaRef = ref(null)

// 🔥 布局相关状态
const nodePositions = ref({})  // { nodeId: { x, y } }
const edges = ref([])          // [{ id, path, start, end }]
const canvasSize = ref({ width: 1200, height: 800 })
const layoutEngine = new TreeLayoutEngine(60, 60, 120, 80)

// 计算属性
const structureTitle = computed(() => {
  const titles = {
    'binary': 'Binary Tree Visualization',
    'bst': 'Binary Search Tree Visualization',
    'avl': 'AVL Tree Visualization',
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
    'avl': [
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

// 🔥 核心方法：计算树的布局
const calculateTreeLayout = () => {
  if (!treeData.value?.root) {
    nodePositions.value = {}
    edges.value = []
    return
  }

  console.log('🔄 重新计算树布局...')

  // 使用布局引擎计算
  const layout = layoutEngine.getLayout(treeData.value.root)

  nodePositions.value = layout.positions
  edges.value = layout.edges
  canvasSize.value = {
    width: layout.width,
    height: layout.height
  }

  console.log('✓ 布局计算完成:', {
    节点数: Object.keys(layout.positions).length,
    连接线数: layout.edges.length,
    画布大小: layout.width + 'x' + layout.height
  })
}

// 🔥 辅助方法：根据ID查找节点
const findNodeById = (node, targetId) => {
  if (!node) return null
  if (node.node_id === targetId) return node

  const leftResult = findNodeById(node.left, targetId)
  if (leftResult) return leftResult

  return findNodeById(node.right, targetId)
}

// 🔥 动画播放器（每步重新计算布局）
const playTreeAnimationSteps = async (steps) => {
  isAnimating.value = true
  console.log('🎬 开始播放动画，共', steps.length, '步')

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]
    console.log(`Step ${i + 1}/${steps.length}:`, step.description)

    // 1. 更新描述
    lastOperation.value = step.description || ''

    // 2. 🔥 如果有树快照，更新树数据并重新计算布局
    if (step.tree_snapshot) {
      treeData.value = step.tree_snapshot
      await nextTick()  // 等待DOM更新
      calculateTreeLayout()  // 重新计算布局
    }

    // 3. 更新高亮节点
    if (step.node_id && step.node_id !== -1) {
      highlightedNodes.value = [step.node_id]
    } else if (step.highlight_indices) {
      highlightedNodes.value = step.highlight_indices
    } else {
      highlightedNodes.value = []
    }

    // 4. 延迟
    const baseDelay = step.duration || 0.5
    const delay = (baseDelay / animationSpeed.value) * 1000
    await new Promise(resolve => setTimeout(resolve, delay))
  }

  console.log('✓ 动画播放完毕')
  highlightedNodes.value = []
  isAnimating.value = false
}

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
  console.log('=== 开始执行操作 ===')

  try {
    let response

    switch (currentOperation.value) {
      case 'build':
        if (structureType.value === 'huffman') {
          console.log('🔥 构建Huffman树, 文本:', huffmanText.value)
          response = await api.buildHuffmanTree(structureId.value, huffmanText.value)
        }
        break
      case 'insert': {
        const val = isNaN(Number(inputValue.value)) ? inputValue.value : Number(inputValue.value)
        response = await api.insertTreeNode(structureId.value, val)
        break
      }
      case 'delete': {
        const val = isNaN(Number(inputValue.value)) ? inputValue.value : Number(inputValue.value)
        response = await api.deleteTreeNode(structureId.value, val)
        break
      }
      case 'search': {
        const val = isNaN(Number(inputValue.value)) ? inputValue.value : Number(inputValue.value)
        response = await api.searchTreeNode(structureId.value, val)
        break
      }
      default:
        console.warn('未处理的操作:', currentOperation.value)
        break
    }

    if (response) {
      console.log('收到响应:', response)

      const steps = response.operation_history || []
      console.log('操作步骤数:', steps.length)

      // 🔥 关键: 先播放动画,再更新最终数据
      if (steps.length > 0) {
        await playTreeAnimationSteps(steps)
      }

      // 动画播放完后更新最终状态
      treeData.value = response.tree_data
      await nextTick()
      calculateTreeLayout()  // 🔥 最终布局计算

      operationHistory.value = steps

      if (structureType.value === 'huffman' && response.tree_data?.huffman_codes) {
        huffmanCodes.value = response.tree_data.huffman_codes
      }

      if (steps.length > 0) {
        lastOperation.value = steps[steps.length - 1].description
      }
    }

    inputValue.value = ''
    huffmanText.value = ''

  } catch (error) {
    console.error('❌ 操作失败:', error)
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
    nodePositions.value = {}
    edges.value = []
  } catch (error) {
    console.error('Failed to clear structure:', error)
  }
}

const saveStructure = async () => {
  if (!structureId.value) return

  try {
    const data = await api.exportStructure(structureId.value)
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

// 监听树数据变化，自动重新计算布局
watch(() => treeData.value, async (newData) => {
  if (newData?.root) {
    await nextTick()
    calculateTreeLayout()
  }
}, { deep: true })

// 生命周期
onMounted(async () => {
  await createOrLoadTreeStructure()
})

// 创建或加载树结构
const createOrLoadTreeStructure = async () => {
  const importId = route.query.importId

  if (importId) {
    // 如果有 importId，加载已有数据
    console.log('检测到导入ID，加载树结构:', importId)
    structureId.value = importId

    try {
      // 从后端获取树状态
      const response = await api.getTreeState(importId)
      console.log('加载的树数据:', response)

      // 🔥 验证树数据
      if (!response.tree_data || !response.tree_data.root) {
        console.warn('⚠️ 后端返回的树数据为空')
        lastOperation.value = '导入的树结构为空'
      } else {
        console.log(`✅ 成功加载树结构: ${response.tree_data.size} 个节点`)

        // 🔥 恢复状态
        treeData.value = response.tree_data
        operationHistory.value = response.operation_history || []

        // 🔥 Huffman树的编码表
        if (structureType.value === 'huffman' && response.tree_data?.huffman_codes) {
          huffmanCodes.value = response.tree_data.huffman_codes
          console.log('✅ 恢复Huffman编码表:', huffmanCodes.value)
        }

        // 🔥 显示加载提示
        lastOperation.value = `✅ 已加载保存的树 (${response.tree_data.size} 个节点)`

        // 🔥 重新计算布局
        await nextTick()
        calculateTreeLayout()

        // 🔥 可选：高亮所有节点
        if (response.tree_data.traversals?.levelorder) {
          const allNodeIds = []
          const collectIds = (node) => {
            if (!node) return
            allNodeIds.push(node.node_id)
            collectIds(node.left)
            collectIds(node.right)
          }
          collectIds(response.tree_data.root)

          highlightedNodes.value = allNodeIds
          setTimeout(() => {
            highlightedNodes.value = []
          }, 1500)
        }
      }

    } catch (error) {
      console.error('加载树结构失败:', error)
      alert('加载失败，将创建新的树结构'+ (error.response?.data?.error || error.message))
      await createNewTreeStructure()
    }
  } else {
    // 创建新树结构
    await createNewTreeStructure()
  }
}

// 新增：创建新树结构
const createNewTreeStructure = async () => {
  try {
    const response = await api.createTreeStructure(structureType.value)
    structureId.value = response.structure_id
    console.log('新建树结构:', response)
  } catch (error) {
    console.error('创建树结构失败:', error)
    alert('创建树结构失败')
  }
}
// 监听路由变化
watch(() => route.query.importId, async (newId) => {
  if (newId && newId !== structureId.value) {
    await createOrLoadTreeStructure()
  }
})

</script>

<style scoped>
/* ... 保持原有样式不变 ... */
.visualization-container {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  background-color: #f9fafb;
}

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

/* 🔥 关键样式：树画布 */
.tree-canvas {
  position: relative;
  width: 100%;
  min-height: 600px;
}

.connection-svg {
  position: absolute;
  left: 0;
  top: 0;
  pointer-events: none;
  z-index: 1;
}

.nodes-layer {
  position: relative;
  z-index: 2;
}

.edge-line {
  transition: stroke 0.3s ease;
}

.edge-line:hover {
  stroke: #3b82f6;
  stroke-width: 3;
}

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
