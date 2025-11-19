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

      <!-- 🎬 遍历类型选择 -->
      <div v-if="currentOperation === 'traverse'" class="operation-group">
        <label class="label">Traversal Type:</label>
        <select v-model="traversalType" class="select-input">
          <option value="preorder">前序遍历 (Preorder)</option>
          <option value="inorder">中序遍历 (Inorder)</option>
          <option value="postorder">后序遍历 (Postorder)</option>
          <option value="levelorder">层次遍历 (Level Order)</option>
        </select>
      </div>

      <!-- Huffman树特殊输入 -->
      <template v-if="structureType === 'huffman' && currentOperation === 'build'">
        <!-- 模式选择 -->
        <div class="operation-group">
          <label class="label">Mode:</label>
          <select v-model="huffmanMode" class="select">
            <option value="text">Text Mode</option>
            <option value="number">Number Mode</option>
          </select>
        </div>

        <!-- 文本模式输入 -->
        <div v-if="huffmanMode === 'text'" class="operation-group">
          <label class="label">Input Text:</label>
          <input
            v-model="huffmanText"
            type="text"
            placeholder="Enter text for Huffman encoding (e.g., HELLO)"
            class="text-input text-input-wide"
            @keyup.enter="executeOperation"
          />
        </div>

        <!-- 数字模式输入 -->
        <div v-else class="operation-group">
          <label class="label">Input Numbers:</label>
          <input
            v-model="huffmanNumbers"
            type="text"
            placeholder="Enter numbers separated by comma (e.g., 2,4,6,8)"
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

    <!-- 状态栏 - 放在操作面板下方 -->
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
      <div v-if="dashedNodes.length > 0" class="status-info status-dashed-debug">
        <span class="status-label">虚线节点:</span>
        <span class="status-value">{{ dashedNodes.join(', ') }}</span>
      </div>
      <div v-if="lastOperation" class="status-message">
        {{ lastOperation }}
      </div>
    </div>

    <!-- 可视化区域 -->
    <div class="visualization-area" :style="{ paddingBottom: '180px' }" ref="visualAreaRef">
      <!-- 🔥 Huffman频率列表面板 -->
      <div v-if="structureType === 'huffman' && huffmanFrequencyList.length > 0" class="frequency-panel">
        <div class="frequency-list">
          <div
            v-for="(freq, index) in huffmanFrequencyList"
            :key="`freq-${index}`"
            class="frequency-item"
            :class="{ 'selected': huffmanSelectedWeights.includes(freq) }"
          >
            {{ freq }}
          </div>
        </div>
      </div>

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
                :stroke="isEdgeDashed(edge) ? '#10b981' : '#6b7280'"
                stroke-width="2"
                stroke-linecap="round"
                :stroke-dasharray="isEdgeDashed(edge) ? '5,5' : 'none'"
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
            <!-- 正常节点 -->
            <TreeNodeComponent
              v-for="(position, nodeId) in nodePositions"
              :key="`node-${nodeId}`"
              :node="findNodeById(treeData.root, parseInt(nodeId))"
              :position="position"
              :highlighted="highlightedNodes"
              :dashedNodes="dashedNodes"
              :isHuffman="structureType === 'huffman'"
            />

            <!-- 🔥 预览节点 -->
            <TreeNodeComponent
              v-if="previewNode"
              :key="'preview'"
              :node="{ value: previewNode.value, node_id: -1 }"
              :position="previewNode.position"
              :highlighted="[]"
              :dashedNodes="[]"
              :isPreview="true"
              :isHuffman="structureType === 'huffman'"
            />
          </div>
        </div>
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
    <DSLInputBar />

    <!-- 🔥 代码面板 -->
    <CodePanel
      :code="currentCode"
      :currentLine="currentCodeLine"
      :highlightedLines="currentCodeHighlight"
      :operationName="currentOperationName"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api.js'
import TreeNodeComponent from './TreeNodeSimple.vue'
import { TreeLayoutEngine } from '../utils/treeLayout.js'
import DSLInputBar from './DSLInputBar.vue'  // 🔥 添加导入
import CodePanel from '../components/CodePanel.vue'  // 🔥 代码面板组件

const router = useRouter()
const route = useRoute()

// 数据状态
const structureType = ref(route.params.type || 'binary')
const structureId = ref(null)
const treeData = ref(null)
const currentOperation = ref('insert')
const inputValue = ref('')
const huffmanText = ref('')
const huffmanMode = ref('text')  // 🔥 Huffman树模式: 'text' 或 'number'
const huffmanNumbers = ref('')   // 🔥 Huffman树数字模式输入
const traversalType = ref('inorder')  // 🎬 遍历类型
const isAnimating = ref(false)
const highlightedNodes = ref([])
const dashedNodes = ref([])  // 虚线节点（新插入还未平衡的）
const previewNode = ref(null)  // 🔥 预览节点: { value, position: {x, y}, parentId }
const operationHistory = ref([])
const lastOperation = ref('')
const historyCollapsed = ref(true)
const huffmanCodes = ref(null)
const huffmanFrequencyList = ref([])      // 🔥 Huffman树频率列表
const huffmanSelectedWeights = ref([])    // 🔥 Huffman树选中的权重（红色高亮）
const animationSpeed = ref(1)
const visualAreaRef = ref(null)

// 🔥 代码面板相关
const currentCode = ref('')  // 当前显示的代码
const currentCodeLine = ref(null)  // 当前执行的代码行
const currentCodeHighlight = ref([])  // 当前高亮的代码行
const currentOperationName = ref('')  // 当前操作名称

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
      { value: 'search', label: 'Search' },
      { value: 'traverse', label: 'Traverse' }
    ],
    'bst': [
      { value: 'insert', label: 'Insert' },
      { value: 'delete', label: 'Delete' },
      { value: 'search', label: 'Search' },
      { value: 'traverse', label: 'Traverse' }
    ],
    'avl': [
      { value: 'insert', label: 'Insert' },
      { value: 'delete', label: 'Delete' },
      { value: 'search', label: 'Search' },
      { value: 'traverse', label: 'Traverse' }
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
    // 🔥 根据模式检查不同的输入
    if (huffmanMode.value === 'text') {
      return huffmanText.value.trim().length > 0
    } else {
      return huffmanNumbers.value.trim().length > 0
    }
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

  // 🔥 保存临时节点的位置和连接线（如果有的话）
  const tempNodePositions = {}
  const tempEdges = []

  if (treeData.value?._tempNodes) {
    for (const nodeId of Object.keys(treeData.value._tempNodes)) {
      if (nodePositions.value[nodeId]) {
        tempNodePositions[nodeId] = nodePositions.value[nodeId]
      }
    }
  }

  // 保存临时连接线
  for (const edge of edges.value) {
    if (edge._isTemp) {
      tempEdges.push(edge)
    }
  }

  // 使用布局引擎计算
  const layout = layoutEngine.getLayout(treeData.value.root)

  nodePositions.value = layout.positions
  edges.value = layout.edges
  canvasSize.value = {
    width: layout.width,
    height: layout.height
  }

  // 🔥 恢复临时节点的位置和连接线
  if (Object.keys(tempNodePositions).length > 0) {
    nodePositions.value = {
      ...nodePositions.value,
      ...tempNodePositions
    }
    console.log('✓ 已恢复临时节点位置:', Object.keys(tempNodePositions))
  }

  if (tempEdges.length > 0) {
    edges.value = [...edges.value, ...tempEdges]
    console.log('✓ 已恢复临时连接线:', tempEdges.length, '条')
  }

  console.log('✓ 布局计算完成:', {
    节点数: Object.keys(layout.positions).length,
    连接线数: layout.edges.length,
    画布大小: layout.width + 'x' + layout.height
  })
}

// 🔥 辅助方法：根据ID查找节点（支持临时节点）
const findNodeById = (node, targetId) => {
  // 🔥 优先查找临时节点
  if (treeData.value?._tempNodes?.[String(targetId)]) {
    return treeData.value._tempNodes[String(targetId)]
  }

  // 在树中递归查找
  if (!node) return null
  if (node.node_id === targetId) return node

  const leftResult = findNodeById(node.left, targetId)
  if (leftResult) return leftResult

  return findNodeById(node.right, targetId)
}

// 🔥 辅助方法：判断边是否应该为虚线
const isEdgeDashed = (edge) => {
  // 边的ID格式是 "fromId-toId"
  const toNodeId = parseInt(edge.id.split('-')[1])
  return dashedNodes.value.includes(toNodeId)
}

// 🔥 动画播放器（每步重新计算布局）
const playTreeAnimationSteps = async (steps) => {
  isAnimating.value = true
  console.log('🎬 开始播放动画，共', steps.length, '步')

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]
    const nextStep = i < steps.length - 1 ? steps[i + 1] : null
    console.log(`Step ${i + 1}/${steps.length}:`, step.description)

    // 1. 更新描述
    lastOperation.value = step.description || ''

    // 1.5 🔥 更新Huffman频率列表和选中的权重（从visual_hints中提取）
    if (structureType.value === 'huffman' && step.visual_hints) {
      if (step.visual_hints.frequency_list) {
        huffmanFrequencyList.value = [...step.visual_hints.frequency_list]
        console.log('🔥 更新频率列表:', huffmanFrequencyList.value)
      }
      if (step.visual_hints.selected_weights) {
        huffmanSelectedWeights.value = [...step.visual_hints.selected_weights]
        console.log('🔥 选中权重（红色）:', huffmanSelectedWeights.value)
      } else {
        huffmanSelectedWeights.value = []
      }
    }

    // 2. 🔥 如果有树快照，更新树数据并重新计算布局
    if (step.tree_snapshot) {
      treeData.value = step.tree_snapshot

      // 🔥 调试：打印树快照的结构
      console.log('   -> 树快照root:', step.tree_snapshot.root)
      if (step.tree_snapshot.root) {
        const collectNodeIds = (node) => {
          if (!node) return []
          return [
            node.node_id,
            ...collectNodeIds(node.left),
            ...collectNodeIds(node.right)
          ]
        }
        const allNodeIds = collectNodeIds(step.tree_snapshot.root)
        console.log('   -> 树快照中的所有节点ID:', allNodeIds)
      }

      await nextTick()  // 等待DOM更新
      calculateTreeLayout()  // 重新计算布局
    }

    // 3. 更新虚线节点和高亮节点
    // 🔥 根据 animation_type 决定如何显示节点
    const animationType = step.animation_type || ''

    if (animationType === 'pulse') {
      // 浅绿色脉冲动画（虚线节点）
      console.log('🔵 检测到脉冲动画步骤:', step.description)
      console.log('   -> highlight_indices:', step.highlight_indices)

      // 🔥 关键修复1：创建新数组引用，强制 Vue 触发响应式更新
      dashedNodes.value = [...(step.highlight_indices || [])]
      highlightedNodes.value = []
      console.log('   -> dashedNodes设置为:', dashedNodes.value)
      console.log('   -> 🔥 虚线节点将显示', step.duration || 0.5, '秒')
      // 🔥 关键修复2：等待多个渲染周期确保样式生效
      await nextTick()
      await nextTick()  // 双重 nextTick 确保子组件完全重新渲染
      console.log('   -> ✅ DOM已更新,虚线节点应该可见')

      // 🔥 关键修复3：检查并补充虚线节点的临时位置
      const nodeIdsInPositions = Object.keys(nodePositions.value)
      const dashedNodeId = step.highlight_indices[0]
      const isDashedNodeInPositions = nodeIdsInPositions.includes(String(dashedNodeId))

      console.log('   -> nodePositions的keys:', nodeIdsInPositions)
      console.log('   -> 虚线节点ID:', dashedNodeId)
      console.log('   -> 虚线节点在nodePositions中?', isDashedNodeInPositions)

      if (!isDashedNodeInPositions) {
        console.warn('⚠️ 虚线节点不在nodePositions中, 自动补充临时节点和位置')

        // 🔥 从 tree_snapshot 中找到虚线节点和它的父节点
        let parentNode = null
        let dashedNode = null
        let isLeftChild = false

        // 辅助函数：在树中查找节点
        const findNodeInTree = (node, targetId) => {
          if (!node) return null
          if (node.node_id === targetId) return node
          const leftResult = findNodeInTree(node.left, targetId)
          if (leftResult) return leftResult
          return findNodeInTree(node.right, targetId)
        }

        // 辅助函数：查找父节点
        const findParent = (node, targetId) => {
          if (!node) return null
          if (node.left?.node_id === targetId) return { parent: node, isLeft: true }
          if (node.right?.node_id === targetId) return { parent: node, isLeft: false }
          const leftResult = findParent(node.left, targetId)
          if (leftResult) return leftResult
          return findParent(node.right, targetId)
        }

        if (step.tree_snapshot?.root) {
          // 🔥 打印树结构帮助调试
          const printTree = (node, prefix = '') => {
            if (!node) return prefix + 'null'
            let result = `${prefix}node_id=${node.node_id}, value=${node.value}\n`
            if (node.left) result += printTree(node.left, prefix + '  L:')
            if (node.right) result += printTree(node.right, prefix + '  R:')
            return result
          }
          console.log('   -> 🔍 树结构:\n' + printTree(step.tree_snapshot.root))
          console.log('   -> 🔍 寻找虚线节点ID:', dashedNodeId)

          dashedNode = findNodeInTree(step.tree_snapshot.root, dashedNodeId)
          const parentInfo = findParent(step.tree_snapshot.root, dashedNodeId)
          if (parentInfo) {
            parentNode = parentInfo.parent
            isLeftChild = parentInfo.isLeft
          }
        } else {
          console.error('   -> ❌ step.tree_snapshot 或 root 不存在')
        }

        console.log('   -> 找到虚线节点:', dashedNode)
        console.log('   -> 找到父节点:', parentNode)
        console.log('   -> 是左子节点?', isLeftChild)

        if (!dashedNode || !parentNode) {
          console.error('❌ 无法找到虚线节点或父节点')
          return
        }

        // 🔥 从 nodePositions 中获取父节点的实际位置
        const parentPos = nodePositions.value[String(parentNode.node_id)]
        if (!parentPos) {
          console.error('❌ 父节点位置不存在')
          return
        }

        // 🔥 使用布局引擎的逻辑计算子节点位置
        const LEVEL_HEIGHT = 120  // 与 treeLayout.js 保持一致
        const MIN_SPACING = 100   // 与 treeLayout.js 保持一致

        // 计算水平位置：根据是左子还是右子
        let tempX
        if (isLeftChild) {
          // 左子节点：在父节点左侧
          tempX = parentPos.x - MIN_SPACING / 2
        } else {
          // 右子节点：在父节点右侧
          tempX = parentPos.x + MIN_SPACING / 2
        }

        const tempPos = {
          x: tempX,
          y: parentPos.y + LEVEL_HEIGHT  // 垂直距离固定
        }

        // 🔥 创建临时节点对象
        if (!treeData.value._tempNodes) {
          treeData.value._tempNodes = {}
        }
        treeData.value._tempNodes[String(dashedNodeId)] = {
          value: dashedNode.value,
          node_id: dashedNodeId,
          left: null,
          right: null,
          height: dashedNode.height || 1,
          _isTemp: true
        }

        // 🔥 添加临时位置到 nodePositions
        nodePositions.value = {
          ...nodePositions.value,
          [String(dashedNodeId)]: tempPos
        }

        // 🔥 添加连接线（从父节点到虚线节点）
        const RADIUS = 30  // 节点半径
        const dx = tempPos.x - parentPos.x
        const dy = tempPos.y - parentPos.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        const ux = dx / distance
        const uy = dy / distance

        const startX = parentPos.x + RADIUS * ux
        const startY = parentPos.y + RADIUS * uy
        const endX = tempPos.x - RADIUS * ux
        const endY = tempPos.y - RADIUS * uy

        const tempEdge = {
          id: `${parentNode.node_id}-${dashedNodeId}`,
          path: `M ${startX} ${startY} L ${endX} ${endY}`,
          start: { x: startX, y: startY },
          end: { x: endX, y: endY },
          _isTemp: true  // 标记为临时连接线
        }

        edges.value = [...edges.value, tempEdge]

        console.log('✅ 已为虚线节点补充临时位置、节点对象和连接线')
        console.log('   -> 父节点位置:', parentPos)
        console.log('   -> 虚线节点位置:', tempPos)
        console.log('   -> 虚线节点值:', dashedNode.value)
        console.log('   -> 连接线:', tempEdge)
      } else {
        console.log('✅ 虚线节点位置:', nodePositions.value[String(dashedNodeId)])
      }

      // 🔥 显示虚线节点（浅绿色脉冲），等待下一个步骤（confirm）来停止脉冲
      const baseDelay = step.duration || 0.8
      const delay = (baseDelay / animationSpeed.value) * 1000
      console.log('   -> 🟢 虚线节点脉冲中，持续', delay, 'ms')
      console.log('   -> 🟢 当前 dashedNodes:', dashedNodes.value)
      await new Promise(resolve => setTimeout(resolve, delay))
    } else if (animationType === 'confirm') {
      // 确认节点：停止脉冲，变为深绿色
      console.log('🟢 检测到确认动画步骤:', step.description)
      console.log('   -> highlight_indices:', step.highlight_indices)

      // 清空虚线节点和高亮节点，让节点变为正常深绿色
      dashedNodes.value = []
      highlightedNodes.value = []
      console.log('   -> 节点已确认为深绿色，停止脉冲')

      // 等待DOM更新
      await nextTick()

      // 延迟
      const baseDelay = step.duration || 0.5
      const delay = (baseDelay / animationSpeed.value) * 1000
      console.log('   -> 确认动画延迟:', delay, 'ms')
      await new Promise(resolve => setTimeout(resolve, delay))
    } else {
      // 其他步骤显示红色高亮
      if (step.node_id && step.node_id !== -1) {
        highlightedNodes.value = [step.node_id]
      } else if (step.highlight_indices) {
        highlightedNodes.value = step.highlight_indices
      } else {
        highlightedNodes.value = []
      }

      // 🔥 关键修复：在warning/rotate/settle动画期间，保持浅绿色脉冲状态
      // 不清除 dashedNodes，让新插入的节点继续保持浅绿色脉冲
      console.log('   -> 保持 dashedNodes 状态:', dashedNodes.value)

      // 🔥 等待 DOM 更新，确保高亮生效
      await nextTick()

      // 4. 延迟
      const baseDelay = step.duration || 0.5
      let delay = (baseDelay / animationSpeed.value) * 1000

      // 🔥 特殊处理旋转动画和失衡检测：确保最小延迟，让用户看清红色高亮和旋转过程
      if (step.description && step.description.includes('旋转')) {
        const minRotationDelay = 1500  // 🔥 旋转动画最少1.5秒，让用户看清
        delay = Math.max(delay, minRotationDelay)
        console.log('   -> 🔄 旋转步骤，延长延迟到:', delay, 'ms，高亮节点:', highlightedNodes.value)
      } else if (step.description && step.description.includes('失衡')) {
        const minImbalanceDelay = 1200  // 🔥 失衡检测最少1.2秒，让用户看清
        delay = Math.max(delay, minImbalanceDelay)
        console.log('   -> ⚠️ 失衡检测步骤，延长延迟到:', delay, 'ms，高亮节点:', highlightedNodes.value)
      }

      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }

  console.log('✓ 动画播放完毕')
  highlightedNodes.value = []
  dashedNodes.value = []

  // 🔥 清空Huffman频率列表
  if (structureType.value === 'huffman') {
    huffmanFrequencyList.value = []
    huffmanSelectedWeights.value = []
  }

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
          // 🔥 根据模式构建Huffman树
          if (huffmanMode.value === 'text') {
            console.log('🔥 构建Huffman树 (文本模式), 文本:', huffmanText.value)
            response = await api.buildHuffmanTree(structureId.value, huffmanText.value)
          } else {
            // 数字模式：解析逗号分隔的数字
            const numbers = huffmanNumbers.value.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n))
            console.log('🔥 构建Huffman树 (数字模式), 数字列表:', numbers)
            response = await api.buildHuffmanTree(structureId.value, numbers)
          }
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
      case 'traverse': {
        console.log('🎬 执行遍历操作，类型:', traversalType.value)
        response = await api.traverseTree(structureId.value, traversalType.value)
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
    huffmanNumbers.value = ''

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
        const hasOperationHistory = response.operation_history && response.operation_history.length > 0
        const isFromDSL = route.query.fromDSL === 'true'

        // 如果是从DSL跳转过来的，并且有操作历史，播放动画
        if (isFromDSL && hasOperationHistory) {
          console.log('🎬 检测到从DSL跳转，将播放构建动画')

          // 先清空树数据，准备播放动画
          treeData.value = { root: null, size: 0, height: 0 }
          await nextTick()

          // 播放动画
          await playTreeAnimationSteps(response.operation_history)

          // 动画结束后，更新最终数据
          treeData.value = response.tree_data
          operationHistory.value = response.operation_history

          // 清除URL中的fromDSL参数
          router.replace({
            path: route.path,
            query: { importId: route.query.importId }
          })
        } else {
          // 正常加载（不播放动画）
          treeData.value = response.tree_data
          operationHistory.value = response.operation_history || []
        }

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

        // 🔥 可选：高亮所有节点（只在非DSL跳转时）
        if (!isFromDSL && response.tree_data.traversals?.levelorder) {
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

      // 🔥 清除无效的 importId 参数
      router.replace({
        path: route.path,
        query: {}
      })

      // 静默创建新结构（不弹出alert，更友好）
      console.log('⚠️ 旧结构已失效，正在创建新结构...')
      lastOperation.value = '⚠️ 之前的树结构已失效，已自动创建新结构'
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

<style>
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
  /* 平滑过渡连接线的位置和颜色 */
  transition: x1 0.8s cubic-bezier(0.4, 0.0, 0.2, 1),
              y1 0.8s cubic-bezier(0.4, 0.0, 0.2, 1),
              x2 0.8s cubic-bezier(0.4, 0.0, 0.2, 1),
              y2 0.8s cubic-bezier(0.4, 0.0, 0.2, 1),
              stroke 0.3s ease,
              stroke-dasharray 0.3s ease;
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

.status-dashed-debug {
  background-color: #f0fdf4;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  border-left: 3px solid #10b981;
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
  top: 160px;  /* 🔥 对齐状态栏：control-bar(约60px) + operation-panel(约115px) = 175px */
  right: 0;
  width: 400px;
  max-height: 50vh;
  background-color: white;
  border-left: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: -4px 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  z-index: 10;
}

.history-panel.collapsed {
  transform: translateY(calc(-100% + 40px));
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
  transform: rotate(180deg);  /* 🔥 默认向上 */
}

.history-header svg.rotated {
  transform: rotate(0deg);  /* 🔥 collapsed时向下 */
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

/* 🔥 Huffman频率列表面板样式 */
.frequency-panel {
  width: 100%;
  padding: 1rem 2rem;
  background-color: #1f2937;
  border-bottom: 2px solid #374151;
  display: flex;
  justify-content: center;
  align-items: center;
}

.frequency-list {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
}

.frequency-item {
  font-family: 'Calibri', 'Arial', sans-serif;
  font-size: 1.5rem;
  font-weight: 400;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background-color: #374151;
  transition: all 0.3s ease;
  min-width: 3rem;
  text-align: center;
}

.frequency-item.selected {
  color: #ef4444;
  background-color: #7f1d1d;
  font-weight: 600;
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
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

  .frequency-list {
    gap: 1rem;
  }

  .frequency-item {
    font-size: 1.25rem;
    padding: 0.375rem 0.75rem;
  }
}
</style>
