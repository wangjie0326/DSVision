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
        <!-- 🔥 新增: 显示来源标识 -->
        <span v-if="fromDSL" class="source-badge dsl">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
          DSL
        </span>
        <span v-else-if="fromImport" class="source-badge import">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Imported
        </span>
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
      <!-- 🔥 1. 操作类型选择器 -->
      <div class="operation-group">
        <label class="label">Operation:</label>
        <select v-model="currentOperation" class="select-input">
          <option v-for="op in availableOperations" :key="op.value" :value="op.value">
            {{ op.label }}
          </option>
        </select>
      </div>

      <!-- 🔥 2. 容量输入（仅顺序表显示） -->
      <div v-if="structureType === 'sequential' && !structureId" class="operation-group">
        <label class="label">Capacity:</label>
        <input
          v-model.number="capacity"
          type="number"
          placeholder="100"
          class="text-input"
          min="1"
          max="100"
        />
      </div>

      <!-- 🔥 3. 动画速度选择器 -->
      <div class="operation-group">
        <label class="label">Speed:</label>
        <select v-model="animationSpeed" class="select-input">
          <option :value="0.5">0.5x</option>
          <option :value="1">1x</option>
          <option :value="2">2x</option>
          <option :value="4">4x</option>
        </select>
      </div>

      <!-- 4. Value 输入框 -->
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

      <!-- 5. Index 输入框 -->
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

      <!-- 6. 执行按钮 -->
      <button
        @click="executeOperation"
        :disabled="isAnimating || !canExecute"
        class="btn-execute"
      >
        <span v-if="!isAnimating">Execute</span>
        <span v-else class="loading-spinner">⟳</span>
      </button>

      <!-- 7. 清空按钮 -->
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

    <!-- 可视化区域 -->
    <div class="visualization-area" :style="{ paddingBottom: '180px' }">
      <div class="canvas-wrapper">
        <!-- 🔥 空状态提示（非顺序表才显示） -->
        <div v-if="elements.length === 0 && structureType !== 'sequential'" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <path d="M9 9h6M9 15h6"/>
          </svg>
          <p>Start adding elements...</p>
        </div>

        <!-- 🔥 顺序表始终显示网格，即使为空 -->
        <div v-if="structureType === 'sequential' || elements.length > 0" class="elements-container" :class="containerClass">
          <!-- 🔥 链表的可视化 - 使用SVG组件 -->
          <template v-if="structureType === 'linked'">
            <LinkedList
              :data="elements"
              :highlightIndices="highlightedIndices"
              :pointerStates="pointerStates"
            />
          </template>

          <!-- 🔥 顺序表的可视化 - 10x10网格，显示所有容量槽位 -->
          <template v-if="structureType === 'sequential'">
            <div
              v-for="index in capacity"
              :key="`elem-${index - 1}`"
              class="element-wrapper"
            >
              <div
                class="element-node"
                :class="[getNodeClass(index - 1), { 'empty-slot': !elements[index - 1] && elements[index - 1] !== 0 }]"
              >
                <span v-if="elements[index - 1] !== null && elements[index - 1] !== undefined" class="element-value">
                  {{ elements[index - 1] }}
                </span>
              </div>
              <div class="element-index">[{{ index - 1 }}]</div>
            </div>
          </template>

          <!-- 栈的可视化 - 保持原样 -->
          <template v-if="structureType === 'stack'">
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
              <div v-if="index === elements.length - 1" class="stack-top-indicator">
                TOP
              </div>
            </div>
          </template>
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
    <!-- 🔥 新增: DSL 输入栏 -->
    <DSLInputBar />
  </div>
</template>

<script setup>
import { ref, computed, onMounted,watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api.js'
import DSLInputBar from './DSLInputBar.vue'  // 🔥 添加导入
import LinkedList from '../components/LinkedList.vue'  // 🔥 链表SVG组件

const router = useRouter()
const route = useRoute()

// 数据状态
const structureType = ref(route.params.type || 'sequential')
const structureId = ref(null)
const elements = ref([])
const capacity = ref(100)

// 🔥 新增: 来源标识
const fromDSL = ref(route.query.fromDSL === 'true')
const fromImport = ref(route.query.fromImport === 'true')

// 🔥 操作相关 - 保持原有的操作类型
const currentOperation = ref('insert')
const inputValue = ref('')
const inputIndex = ref('')

// 🔥 动画相关 - 新增
const isAnimating = ref(false)
const isPlaying = ref(false)
const animationSpeed = ref(1)  // 动画速度倍数
const currentStepIndex = ref(0)

// 🔥 可视化状态 - 修改
const highlightedIndices = ref([])
const pointerStates = ref({
  head: -1,
  prev: -1,
  current: -1,
  new_node: -1
})

// 历史记录
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

const playOperationSteps = async (steps) => {
  isPlaying.value = true
  console.log('开始播放动画，共', steps.length, '步')

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]
    currentStepIndex.value = i

    console.log(`Step ${i + 1}:`, step.description)

    // 1. 更新描述
    lastOperation.value = step.description || ''

    // 2. 更新高亮索引
    highlightedIndices.value = step.highlight_indices || []

    // 3. 更新多指针状态
    if (step.pointers) {
      // 先重置所有指针
      pointerStates.value = { head: -1, prev: -1, current: -1, new_node: -1 }
      // 然后更新指定的指针
      Object.keys(step.pointers).forEach(key => {
        pointerStates.value[key] = step.pointers[key]
      })
      console.log('指针状态:', step.pointers)
    }

    // 4. 更新数据快照
    if (step.data_snapshot && step.data_snapshot.length > 0) {
      elements.value = [...step.data_snapshot]
      console.log('数据快照:', step.data_snapshot)
    }

    // 5. 延迟（根据速度调整）
    const baseDelay = step.duration || 0.5
    const delay = (baseDelay / animationSpeed.value) * 1000
    await new Promise(resolve => setTimeout(resolve, delay))
  }

  console.log('动画播放完毕')

  // 播放完毕，清除高亮和指针
  highlightedIndices.value = []
  pointerStates.value = { head: -1, prev: -1, current: -1, new_node: -1 }
  isPlaying.value = false
}

const executeOperation = async () => {
  // 🔥 如果结构还未创建（顺序表延迟创建），先创建
  if (!structureId.value) {
    console.log('首次操作，创建数据结构...')
    await createNewStructure()
  }

  if (!structureId.value || !canExecute.value) return

  isAnimating.value = true
  console.log('执行操作:', currentOperation.value)

  try {
    let response
    const index = inputIndex.value === '' ? elements.value.length : parseInt(inputIndex.value)

    switch (currentOperation.value) {
      case 'batch_init':
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
      console.log('收到响应:', response)
      const steps = response.operation_history || []

      // 🔥 关键修改：播放动画
      if (steps.length > 0) {
        await playOperationSteps(steps)
      }

      // 动画播放完后更新最终状态
      elements.value = response.data
      operationHistory.value = steps

      if (steps.length > 0) {
        lastOperation.value = steps[steps.length - 1].description
      }
    }

    inputValue.value = ''
    inputIndex.value = ''

  } catch (error) {
    console.error('操作失败:', error)
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
    pointerStates.value = { head: -1, prev: -1, current: -1, new_node: -1 }
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
  await createOrLoadStructure()
})

const createOrLoadStructure = async()=>{
  const importId = route.query.importId
  if(importId){
    //如果有importid说明是导入进来的
    console.log('检测到了id，加载已有数据结构',importId)
    structureId.value = importId

    try{
      //从后端获取数据结构
      const response = await api.getState(importId)
      console.log('加载的数据:', response)


      // 🔥 关键：验证数据是否存在
      if (!response.data || response.data.length === 0) {
        console.warn('后端返回的数据为空')
        lastOperation.value = '导入的数据结构为空'
      } else {
        console.log(`✓ 成功加载 ${response.data.length} 个元素:`, response.data)

        // 恢复状态
        capacity.value = response.capacity || 100
        operationHistory.value = response.operation_history || []

        // 🔥 如果来自DSL且有操作历史，播放动画
        if (fromDSL.value && operationHistory.value.length > 0) {
          console.log(`🎬 播放DSL动画，共 ${operationHistory.value.length} 步`)
          lastOperation.value = '▶ 正在播放操作动画...'
          await playOperationSteps(operationHistory.value)
          elements.value = response.data
          lastOperation.value = `✓ DSL 执行完成 (${elements.value.length} 个元素)`
        } else {
          // 没有操作历史，直接显示结果
          elements.value = response.data
          if (fromDSL.value) {
            lastOperation.value = `✓ 已加载 DSL 执行结果 (${elements.value.length} 个元素)`
          } else {
            lastOperation.value = `✓ 已加载保存的数据 (${elements.value.length} 个元素)`
          }

          // 高亮动画
          highlightedIndices.value = elements.value.map((_, idx) => idx)
          setTimeout(() => {
            highlightedIndices.value = []
          }, 1500)
        }
      }

    }catch (error) {
      console.error('加载数据结构失败:', error)
      alert('加载失败，将创建新的数据结构'+ (error.response?.data?.error || error.message))
      // 如果加载失败，创建新的
      await createNewStructure()
    }
  }else {
    // 🔥 修改：对于顺序表，不立即创建，让用户先选择容量
    // 其他类型的结构则立即创建
    if (structureType.value !== 'sequential') {
      await createNewStructure()
    } else {
      console.log('等待用户设置顺序表容量...')
      lastOperation.value = '请设置容量后开始操作'
    }
  }
}
//新增创建数据结构的独立函数
const createNewStructure = async () => {
  try {
    const response = await api.createStructure(structureType.value, capacity.value)
    structureId.value = response.structure_id
    console.log('新建数据结构:', response)

    // 🔥 立即获取初始状态，显示所有容量槽位
    if (structureType.value === 'sequential') {
      const state = await api.getState(structureId.value)
      elements.value = state.data || []
      capacity.value = state.capacity || capacity.value
      console.log(`✓ 顺序表已创建，容量: ${capacity.value}，显示 ${elements.value.length} 个槽位`)
    }
  } catch (error) {
    console.error('创建数据结构失败:', error)
    alert('创建数据结构失败')
  }
}

//监听路由变化（可选，用于热重载场景）
watch(() => route.query.importId, async (newId) => {
  if (newId && newId !== structureId.value) {
    await createOrLoadStructure()
  }
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

/* 🔥 顺序表10x10网格布局 */
.sequential-container {
  flex-wrap: wrap;
  max-width: calc(10 * (80px + 1rem)); /* 10列，每列80px宽度 + 1rem间距 */
  justify-content: flex-start;
  align-items: flex-start;
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

/* 🔥 空节点样式 - 只显示索引，无值 */
.element-node.empty-slot {
  background-color: #10b981;
  opacity: 0.4;
  border: 2px dashed #6b7280;
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

/* 指针标签容器 */
.pointer-labels {
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  justify-content: center;
  z-index: 10;
}

/* 指针标签样式 */
.pointer-label {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  color: white;
  white-space: nowrap;
  animation: pointerPulse 0.5s ease-in-out;
}

.pointer-label.head {
  background-color: #3b82f6; /* 蓝色 */
}

.pointer-label.prev {
  background-color: #8b5cf6; /* 紫色 */
}

.pointer-label.current {
  background-color: #10b981; /* 绿色 */
}

.pointer-label.new {
  background-color: #f59e0b; /* 橙色 */
}

.source-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-left: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.source-badge.dsl {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.source-badge.import {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
}
@keyframes pointerPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
}

/* 调整链表节点容器,为指针标签留出空间 */
.linked-node-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding-top: 40px; /* 为指针标签留出空间 */
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
