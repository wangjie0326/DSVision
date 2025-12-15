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

      <!-- 🔥 2. 容量输入（顺序表/栈/队列，未创建时可设；栈首个操作前可修改） -->
      <div v-if="(structureType === 'sequential' || structureType === 'stack' || structureType === 'queue') && !structureId && !stackStarted" class="operation-group">
        <label class="label">Capacity:</label>
        <input
          v-model.number="capacity"
          type="number"
          :placeholder="(structureType === 'stack' || structureType === 'queue') ? 'optional (5 default)' : '5'"
          class="text-input"
          min="1"
          max="1000"
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
          :placeholder="valuePlaceholder"
          :disabled="disableValueInput"
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
          :disabled="disableIndexInput"
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
        <span class="status-label">Name:</span>
        <span class="status-value">{{ structureName }}</span>
      </div>
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
      <div v-if="elements.length === 0 && structureType !== 'sequential' && !capacity" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M9 9h6M9 15h6"/>
        </svg>
        <p>Start adding elements...</p>
        </div>

        <!-- 🔥 顺序表始终显示网格，即使为空 -->
        <div v-if="structureType === 'sequential' || structureType === 'queue' || structureType === 'stack' || elements.length > 0" class="elements-container" :class="containerClass">
          <!-- 🔥 链表的可视化 - 使用SVG组件 -->
          <template v-if="structureType === 'linked'">
            <LinkedList
              :data="elements"
              :highlightIndices="highlightedIndices"
              :pointerStates="pointerStates"
            />
          </template>

          <!-- 🔥 顺序表的可视化 - 10x10网格，显示所有容量槽位 -->
          <template v-if="structureType === 'sequential' || structureType === 'queue'">
            <!-- 旧数组（原始数组） -->
            <div class="array-container" :class="{ 'old-array-delete': oldArrayMarkedForDelete }">
              <div v-if="capacity" class="array-label">
                {{ structureType === 'queue' ? 'Queue' : 'Sequential' }} (capacity: {{ capacity ?? '∞' }})
              </div>
              <div
                v-for="index in capacity"
                :key="`old-elem-${index - 1}`"
                class="element-wrapper"
              >
                <div
                  class="element-node"
                  :class="[
                    getNodeClass(index - 1),
                    {
                      'empty-slot': !elements[index - 1] && elements[index - 1] !== 0,
                      'delete-marked': oldArrayMarkedForDelete
                    }
                  ]"
                >
                  <span v-if="elements[index - 1] !== null && elements[index - 1] !== undefined" class="element-value">
                    {{ elements[index - 1] }}
                  </span>
                  <div v-if="isQueueFront(index - 1)" class="queue-indicator front">FRONT</div>
                  <div v-if="isQueueRear(index - 1)" class="queue-indicator rear">REAR</div>
                </div>
                <div class="element-index">[{{ index - 1 }}]</div>
              </div>
            </div>

            <!-- 🔥 新数组（扩容时显示） -->
              <div v-if="isExpanding" class="array-container new-array-container">
              <div class="array-label">New {{ structureType === 'queue' ? 'Queue' : 'Array' }} (capacity: {{ newCapacity }})</div>
              <div
                v-for="index in newCapacity"
                :key="`new-elem-${index - 1}`"
                class="element-wrapper"
              >
                <div
                  class="element-node new-array-node"
                  :class="[
                    {
                      'empty-slot': !newArray[index - 1] && newArray[index - 1] !== 0,
                      'highlighted': highlightedIndices.includes(index - 1)
                    }
                  ]"
                >
                  <span v-if="newArray[index - 1] !== null && newArray[index - 1] !== undefined" class="element-value">
                    {{ newArray[index - 1] }}
                  </span>
                </div>
                <div class="element-index">[{{ index - 1 }}]</div>
              </div>
            </div>
          </template>

          <!-- 栈的可视化 -->
          <template v-if="structureType === 'stack'">
            <div class="stack-area">
              <!-- 旧栈 -->
              <div class="stack-container-outer" :class="{ 'old-array-delete': oldArrayMarkedForDelete }">
                <div v-if="capacity" class="array-label">Stack (capacity: {{ capacity ?? '∞' }})</div>
                <div class="stack-border">
                  <div
                    v-for="(slot, index) in stackSlots"
                    :key="`elem-${index}`"
                    class="element-wrapper stack-wrapper"
                  >
                    <div
                      class="element-node"
                      :class="[
                        getNodeClass(index),
                        {
                          'empty-slot': slot.value === null || slot.value === undefined,
                          'delete-marked': oldArrayMarkedForDelete
                        }
                      ]"
                    >
                      <span class="element-value" v-if="slot.value !== null && slot.value !== undefined">{{ slot.value }}</span>
                    </div>
                    <div class="element-index">[{{ index }}]</div>
                    <div v-if="slot.isTop" class="stack-top-indicator">
                      TOP
                    </div>
                  </div>
                </div>
              </div>

              <!-- 🔥 栈扩容时显示新栈（右侧虚线边框） -->
              <div v-if="isExpanding" class="stack-container-outer ghost">
                <div class="array-label">New Stack (capacity: {{ newCapacity }})</div>
                <div class="stack-border ghost-border">
                  <div
                    v-for="idx in newCapacity"
                    :key="`stack-new-${idx - 1}`"
                    class="element-wrapper stack-wrapper ghost"
                  >
                    <div
                      class="element-node new-array-node"
                      :class="{
                        'empty-slot': !newArray[idx - 1] && newArray[idx - 1] !== 0,
                        'highlighted': highlightedIndices.includes(idx - 1)
                      }"
                    >
                      <span class="element-value" v-if="newArray[idx - 1] !== null && newArray[idx - 1] !== undefined">
                        {{ newArray[idx - 1] }}
                      </span>
                    </div>
                    <div class="element-index">[{{ idx - 1 }}]</div>
                  </div>
                </div>
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
    <!-- 🔥 新增: DSL 输入栏 - 传递当前页面状态 -->
    <DSLInputBar
      :currentStructureType="structureType"
      :currentStructureName="structureName"
      :currentStructureId="structureId"
      :currentElements="elements"
      category="linear"
    />

    <!-- 🔥 代码面板 -->
    <CodePanel
      :code="currentCode"
      :currentLine="currentCodeLine"
      :highlightedLines="currentCodeHighlight"
      :operationName="currentOperationName"
      :structureType="structureType"
      :operation="currentOperation"
      @code-loaded="handleCodeLoaded"
      @language-change="handleLanguageChange"
    />

    <!-- 🔥 算法复杂度指示器 -->
    <ComplexityIndicator
      :structureType="structureType"
      :operation="currentOperation"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api.js'
import DSLInputBar from './DSLInputBar.vue'  // 🔥 添加导入
import LinkedList from '../components/LinkedList.vue'  // 🔥 链表SVG组件
import CodePanel from '../components/CodePanel.vue'  // 🔥 代码面板组件
import ComplexityIndicator from '../components/ComplexityIndicator.vue'  // 🔥 复杂度指示器
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const router = useRouter()
const route = useRoute()

// 数据状态
const structureType = ref(route.params.type || 'sequential')
const structureId = ref(null)
const structureName = ref(route.query.structName || generateDefaultName(route.params.type || 'sequential'))
const elements = ref([])
const capacity = ref(null)
const stackStarted = ref(false)

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

// 🔥 扩容动画相关
const isExpanding = ref(false)  // 是否正在扩容
const newArray = ref([])  // 扩容时的新数组
const newCapacity = ref(0)  // 新数组的容量
const oldArrayMarkedForDelete = ref(false)  // 旧数组是否标记为删除
const queueFrontIndex = ref(-1)
const queueRearIndex = ref(-1)

// 🔥 代码面板相关
const currentCode = ref('')  // 当前显示的代码
const currentCodeLine = ref(null)  // 当前执行的代码行
const currentCodeHighlight = ref([])  // 当前高亮的代码行
const currentOperationName = ref('')  // 当前操作名称
const currentLanguage = ref('cpp')  // 当前选择的编程语言
const lastCodeStep = ref(null)  // 记录最近一步的代码行信息，便于语言切换时复用
// 多语言高亮映射（简化版，避免错误跳转）
const codeHighlightMap = {
  python: {
    sequential_insert: { line: 1, highlight: [1, 6, 12] },
    sequential_delete: { line: 1, highlight: [1, 6, 12] },
    sequential_search: { line: 1, highlight: [1, 5, 10] },
    linked_insert: { line: 12, highlight: [12, 16, 20] },
    linked_insert_head: { line: 10, highlight: [10, 11, 12] },
    linked_insert_tail: { line: 12, highlight: [12, 16, 20] },
    linked_delete: { line: 1, highlight: [1, 6, 14] },
    linked_search: { line: 1, highlight: [1, 6, 12] },
    stack_push: { line: 1, highlight: [1, 4, 9] },
    stack_pop: { line: 1, highlight: [1, 5, 10] },
    stack_peek: { line: 1, highlight: [1, 5, 8] },
    queue_enqueue: { line: 6, highlight: [6, 7] },
    queue_dequeue: { line: 3, highlight: [3, 4, 5] },
    queue_front: { line: 1, highlight: [1, 4, 8] },
    queue_rear: { line: 1, highlight: [1, 4, 8] },
  },
  java: {
    sequential_insert: { line: 1, highlight: [1, 8, 16] },
    sequential_delete: { line: 1, highlight: [1, 8, 16] },
    sequential_search: { line: 1, highlight: [1, 6, 12] },
    linked_insert: { line: 15, highlight: [15, 18, 22] },
    linked_insert_head: { line: 11, highlight: [11, 12, 13] },
    linked_insert_tail: { line: 15, highlight: [15, 18, 22] },
    linked_delete: { line: 1, highlight: [1, 10, 18] },
    linked_search: { line: 1, highlight: [1, 8, 16] },
    stack_push: { line: 1, highlight: [1, 6, 10] },
    stack_pop: { line: 1, highlight: [1, 6, 10] },
    stack_peek: { line: 1, highlight: [1, 6, 10] },
    queue_enqueue: { line: 6, highlight: [6, 7] },
    queue_dequeue: { line: 3, highlight: [3, 4, 5] },
    queue_front: { line: 1, highlight: [1, 6, 10] },
    queue_rear: { line: 1, highlight: [1, 6, 10] },
  }
}

const resolveCodeHighlight = (templateKey, langKey, stepInfo = null) => {
  const alt = codeHighlightMap[langKey]?.[templateKey]
  const line = stepInfo?.codeLine ?? alt?.line ?? null
  const highlight = (stepInfo?.codeHighlight && stepInfo.codeHighlight.length > 0)
    ? stepInfo.codeHighlight
    : (alt?.highlight ?? [])
  return { line, highlight }
}

const applyHighlightForLanguage = (templateKey, langKey) => {
  const stepInfo = lastCodeStep.value && lastCodeStep.value.template === templateKey
    ? lastCodeStep.value
    : null
  const { line, highlight } = resolveCodeHighlight(templateKey, langKey, stepInfo)
  currentCodeLine.value = line
  currentCodeHighlight.value = highlight
}

// 历史记录
const operationHistory = ref([])
const lastOperation = ref('')
const historyCollapsed = ref(true)

// 计算属性
const structureTitle = computed(() => {
  const titles = {
    'sequential': 'Sequential List Visualization',
    'linked': 'Linked List Visualization',
    'stack': 'Stack Visualization',
    'queue': 'Queue Visualization'
  }
  return titles[structureType.value] || 'Data Structure Visualization'
})

function generateDefaultName(type) {
  const baseMap = {
    sequential: 'myList',
    linked: 'myLinkedList',
    stack: 'myStack',
    queue: 'myQueue'
  }
  const base = baseMap[type] || 'myStructure'
  return `${base}${Math.floor(Date.now() % 10000)}`
}

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
    ],
    'queue': [
      { value: 'batch_init', label: 'Batch Init' },
      { value: 'enqueue', label: 'Enqueue' },
      { value: 'dequeue', label: 'Dequeue' },
      { value: 'front', label: 'Front' },
      { value: 'rear', label: 'Rear' },
      { value: 'search', label: 'Search' }
    ]
  }
  return ops[structureType.value] || []
})

watch(availableOperations, (ops) => {
  if (ops && ops.length > 0) {
    currentOperation.value = ops[0].value
  }
}, { immediate: true })

const needsValue = computed(() => {
  return ['batch_init','insert', 'push', 'enqueue', 'search', 'delete'].includes(currentOperation.value)
})

const batchInput = ref('')
const showBatchDialog = ref(false)

const needsIndex = computed(() => {
  return ['insert', 'delete'].includes(currentOperation.value) &&
         structureType.value !== 'stack' &&
         structureType.value !== 'queue'
})

const isDeleteOperation = computed(() => currentOperation.value === 'delete')

const disableIndexInput = computed(() => isDeleteOperation.value && inputValue.value !== '')
const disableValueInput = computed(() => isDeleteOperation.value && inputIndex.value !== '')

const indexPlaceholder = computed(() => {
  if (currentOperation.value === 'insert') return 'Optional (default: append to end)'
  if (currentOperation.value === 'delete') return 'Index (leave empty to delete by value)'
  return 'Required'
})

const valuePlaceholder = computed(() => {
  if (currentOperation.value === 'batch_init') return 'e.g., 1,2,3,4 or 1 2 3 4'
  if (currentOperation.value === 'delete') return 'Value (leave empty to delete by index)'
  return 'Enter value'
})

const canExecute = computed(() => {
  if (isDeleteOperation.value) {
    return inputIndex.value !== '' || inputValue.value !== ''
  }

  if (needsValue.value && !inputValue.value) return false
  if (needsIndex.value && currentOperation.value !== 'insert' && inputIndex.value === '') return false
  return true
})

const containerClass = computed(() => {
  if (structureType.value === 'stack') return 'stack-container'
  if (structureType.value === 'linked') return 'linked-container'
  if (structureType.value === 'queue') return 'sequential-container'
  return 'sequential-container'
})

// 栈显示槽位（支持固定容量展示空位）
const stackSlots = computed(() => {
  if (structureType.value !== 'stack') return []
  const cap = capacity.value
  const elems = elements.value || []

  if (cap && cap > 0) {
    return Array.from({ length: cap }, (_, i) => ({
      value: elems[i],
      isTop: elems.length > 0 && i === elems.length - 1
    }))
  }

  // 无容量限制：仅显示已有元素
  return elems.map((v, i) => ({
    value: v,
    isTop: elems.length > 0 && i === elems.length - 1
  }))
})

// 方法
const getNodeClass = (index) => {
  return {
    'highlighted': highlightedIndices.value.includes(index),
    'animating': isAnimating.value
  }
}

const isQueueFront = (index) => {
  return structureType.value === 'queue' && queueFrontIndex.value >= 0 && index === queueFrontIndex.value
}

const isQueueRear = (index) => {
  return structureType.value === 'queue' && queueRearIndex.value >= 0 && index === queueRearIndex.value
}

const createStructure = async () => {
  try {
    let cap = capacity.value
    if (structureType.value === 'stack') {
      cap = cap && cap > 0 ? cap : 5  // 栈默认 5
    } else if (structureType.value === 'sequential' || structureType.value === 'queue') {
      cap = cap && cap > 0 ? cap : 5   // 顺序表默认 5
    }

    const response = await api.createStructure(structureType.value, cap)
    structureId.value = response.structure_id
    if (response.capacity !== undefined) {
      capacity.value = response.capacity
    }
    if (structureType.value === 'queue') {
      queueFrontIndex.value = response.front_index ?? -1
      queueRearIndex.value = response.rear_index ?? -1
    }
    if (structureType.value === 'stack') {
      stackStarted.value = true
    }
    console.log('Structure created:', response)
  } catch (error) {
    console.error('Failed to create structure:', error)
    alert('Failed to create data structure')
  }
}

const playOperationSteps = async (steps) => {
  isPlaying.value = true
  console.log('开始播放动画，共', steps.length, '步')
  const complexityOps = ['insert','delete','search','push','pop','peek','enqueue','dequeue','front','rear']

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]
    currentStepIndex.value = i

    console.log(`Step ${i + 1}:`, step.description, step)

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

    // 🔥 4. 处理代码面板
    if (step.code_template) {
      console.log('🔥 检测到代码模板:', step.code_template)

      // 如果是新的代码模板，加载代码
      if (currentCode.value === '' || step.code_template !== currentOperationName.value) {
        await loadCodeTemplate(step.code_template)
      }

      // 更新当前执行行和高亮行（多语言映射）
      const langKey = currentLanguage.value
      const templateKey = step.code_template
      const stepInfo = {
        template: templateKey,
        codeLine: step.code_line,
        codeHighlight: step.code_highlight
      }
      const { line, highlight } = resolveCodeHighlight(templateKey, langKey, stepInfo)
      currentCodeLine.value = line
      currentCodeHighlight.value = highlight
      lastCodeStep.value = stepInfo

      console.log('🔥 代码行高亮:', step.code_line, step.code_highlight)
    }

    // 🔥 5. 处理扩容动画
    if (step.operation === 'expand') {
      console.log('🔥 检测到扩容操作，visual_hints:', step.visual_hints)

      if (step.visual_hints) {
        // 开始扩容，显示新数组
        if (step.visual_hints.new_array && step.visual_hints.new_capacity) {
          isExpanding.value = true
          newArray.value = [...step.visual_hints.new_array]
          newCapacity.value = step.visual_hints.new_capacity
          console.log('🔥 显示新数组，容量:', newCapacity.value)
        }

        // 更新新数组的复制进度
        if (step.visual_hints.copy_index !== undefined && step.visual_hints.new_array) {
          newArray.value = [...step.visual_hints.new_array]
          console.log('🔥 更新新数组复制进度:', step.visual_hints.copy_index)
        }

        // 标记旧数组准备删除（全红强调）
        if (step.visual_hints.old_array_delete) {
          oldArrayMarkedForDelete.value = true
          console.log('🔥 标记旧数组准备删除')
        }
      }

      // 扩容完成，切换到新数组
      if (step.description && step.description.includes('扩容完成')) {
        console.log('🔥 扩容完成，切换到新数组')
        // 延迟后清除扩容状态
        await new Promise(resolve => setTimeout(resolve, 500))
        isExpanding.value = false
        oldArrayMarkedForDelete.value = false
        capacity.value = newCapacity.value  // 更新容量
        newArray.value = []
        newCapacity.value = 0
      }
    }

    // 5. 更新数据快照
    if (step.data_snapshot && step.data_snapshot.length > 0) {
      elements.value = [...step.data_snapshot]
      console.log('数据快照:', step.data_snapshot)
    }

    // 队列指针可视化
    if (step.visual_hints) {
      if (step.visual_hints.front !== undefined) {
        queueFrontIndex.value = step.visual_hints.front
      }
      if (step.visual_hints.rear !== undefined) {
        queueRearIndex.value = step.visual_hints.rear
      }
    }

    // 更新复杂度展示的操作类型（仅已知操作）
    let opForComplexity = step.operation
    if (structureType.value === 'queue') {
      if (step.operation === 'insert') opForComplexity = 'enqueue'
      if (step.operation === 'delete') opForComplexity = 'dequeue'
    }
    if (complexityOps.includes(opForComplexity)) {
      currentOperation.value = opForComplexity
    }

    // 6. 延迟（根据速度调整）——提高默认停留时间，保证代码高亮可见
    let baseDelay = step.duration || 0.9
    if (step.code_highlight && step.code_highlight.length > 0) {
      baseDelay += 0.3
    }
    const delay = (baseDelay / animationSpeed.value) * 1000
    await new Promise(resolve => setTimeout(resolve, delay))
  }

  console.log('动画播放完毕')

  // 播放完毕，清除高亮和指针
  highlightedIndices.value = []
  pointerStates.value = { head: -1, prev: -1, current: -1, new_node: -1 }
  isExpanding.value = false
  oldArrayMarkedForDelete.value = false
  newArray.value = []
  newCapacity.value = 0
  isPlaying.value = false
}

const executeOperation = async () => {
  // 🔥 如果结构还未创建（顺序表延迟创建），先创建
  if (!structureId.value) {
    console.log('首次操作，创建数据结构...')
    await createNewStructure()
    if (structureType.value === 'stack') {
      stackStarted.value = true
    }
  }

  if (!structureId.value || !canExecute.value) return

  isAnimating.value = true
  console.log('执行操作:', currentOperation.value)

  try {
    let response
    // 当用户不输入index时，发送null让后端处理默认值
    const index = inputIndex.value === '' ? null : parseInt(inputIndex.value)
    const value = inputValue.value === '' ? null : inputValue.value

    switch (currentOperation.value) {
      case 'batch_init':
        // 直接将用户输入传给后端，由后端保留空位为 null
        response = await api.initBatch(structureId.value, inputValue.value)
        break
      case 'insert':
      case 'push':
      case 'enqueue':
        response = await api.insertElement(structureId.value, index, inputValue.value)
        break
      case 'delete':
      case 'pop':
      case 'dequeue':
        response = await api.deleteElement(structureId.value, index, value)
        break
      case 'search':
      case 'peek':
        response = await api.searchElement(structureId.value, inputValue.value)
        break
      case 'front':
        response = await api.getQueueFront(structureId.value)
        break
      case 'rear':
        response = await api.getQueueRear(structureId.value)
        break
    }

    if (response) {
      console.log('收到响应:', response)
      const steps = response.operation_history || []
      if (response.name) {
        structureName.value = response.name
      }

      // 🔥 关键修改：播放动画
      if (steps.length > 0) {
        await playOperationSteps(steps)
      }

      // 动画播放完后更新最终状态
      elements.value = response.data
      operationHistory.value = steps
      if (structureType.value === 'queue') {
        queueFrontIndex.value = response.front_index ?? -1
        queueRearIndex.value = response.rear_index ?? -1
      }

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
    queueFrontIndex.value = -1
    queueRearIndex.value = -1
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

// 🔥 加载代码模板
const loadCodeTemplate = async (templateKey, language = null) => {
  try {
    // If no language specified, use current selected language
    const lang = language || currentLanguage.value

    // 解析模板key (格式: "structure_operation")
    const parts = templateKey.split('_')
    if (parts.length < 2) {
      console.warn('无效的模板key:', templateKey)
      return
    }

    const structureType = parts[0]
    const operation = parts.slice(1).join('_')

    console.log(`🔥 加载代码模板: ${structureType}/${operation} [语言: ${lang}]`)

    // 使用axios发送请求，会通过vite代理
    const response = await fetch(`${API_BASE_URL}/api/code/template/${structureType}/${operation}?language=${lang}`)

    if (!response.ok) {
      console.error('API请求失败:', response.status, response.statusText)
      return
    }

    const data = await response.json()

    if (data.success) {
      currentCode.value = data.code
      currentOperationName.value = `${structureType}::${operation}()`
      console.log(`✓ 代码模板加载成功 [${lang}]，代码长度:`, data.code.length)
    } else {
      console.error('❌ 代码模板加载失败:', data.error)
      if (data.available_templates) {
        console.log('可用模板:', data.available_templates)
      }
    }
  } catch (error) {
    console.error('❌ 加载代码模板异常:', error)
  }
}


// 生命周期
onMounted(async () => {
  await createOrLoadStructure()
})

// 监听路由查询参数变化（用于DSL/导入后的同页刷新）
watch(
  () => [route.query.importId, route.query._refresh],
  async (newVals, oldVals) => {
    const [newId, newRefresh] = newVals || []
    const [oldId, oldRefresh] = oldVals || []
    if ((newId && newId !== oldId) || (newRefresh && newRefresh !== oldRefresh)) {
      fromDSL.value = route.query.fromDSL === 'true'
      fromImport.value = route.query.fromImport === 'true'
      if (route.query.structName) {
        structureName.value = route.query.structName
      }
      await createOrLoadStructure()
    }
  }
)

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
        if (response.name) {
          structureName.value = response.name
        } else if (route.query.structName) {
          structureName.value = route.query.structName
        }
        console.log(`✓ 成功加载 ${response.data.length} 个元素:`, response.data)

        // 恢复状态
        if (response.capacity !== undefined) {
          capacity.value = response.capacity
        } else if (!capacity.value && (structureType.value === 'sequential' || structureType.value === 'queue')) {
          capacity.value = 5
        }
        if (structureType.value === 'queue') {
          queueFrontIndex.value = response.front_index ?? -1
          queueRearIndex.value = response.rear_index ?? -1
        }
        if (structureType.value === 'stack') {
          stackStarted.value = true
        }
        operationHistory.value = response.operation_history || []

        // 🔥 如果来自DSL且有操作历史，播放动画
        if (fromDSL.value && operationHistory.value.length > 0) {
          console.log(`🎬 播放DSL动画，共 ${operationHistory.value.length} 步`)
          lastOperation.value = '▶ 正在播放操作动画...'
          // 预先展示第一帧，避免页面短暂空白（LLM 自动执行时更明显）
          const firstSnapshot = operationHistory.value.find(step => step.data_snapshot && step.data_snapshot.length > 0)?.data_snapshot
          if (firstSnapshot && firstSnapshot.length > 0) {
            elements.value = [...firstSnapshot]
          } else if (response.data && response.data.length > 0) {
            // 没有快照时至少保持最终状态，避免闪烁
            elements.value = [...response.data]
          }
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
    // 🔥 修改：顺序表/栈/队列不立即创建，等待用户设置容量；其他类型立即创建
    if (structureType.value !== 'sequential' && structureType.value !== 'stack' && structureType.value !== 'queue') {
      await createNewStructure()
    } else {
      console.log('等待用户设置容量后开始操作...')
      lastOperation.value = '请设置容量后开始操作'
    }
  }
}
//新增创建数据结构的独立函数
const createNewStructure = async () => {
  try {
    let cap = capacity.value
    if (structureType.value === 'stack') {
      cap = cap && cap > 0 ? cap : 5  // 栈默认 5（视作初始槽位）
    } else if (structureType.value === 'sequential' || structureType.value === 'queue') {
      cap = cap && cap > 0 ? cap : 5   // 顺序表默认 5
    }

    const response = await api.createStructure(structureType.value, cap)
    structureId.value = response.structure_id
    if (response.name) {
      structureName.value = response.name
    } else if (!structureName.value) {
      structureName.value = generateDefaultName(structureType.value)
    }
    console.log('新建数据结构:', response)

    // 🔥 立即获取初始状态，显示容量槽位
    if (structureType.value === 'sequential' || structureType.value === 'stack' || structureType.value === 'queue') {
      const state = await api.getState(structureId.value)
      elements.value = state.data || []
      if (state.capacity !== undefined) {
        capacity.value = state.capacity
      }
      if (structureType.value === 'queue') {
        queueFrontIndex.value = state.front_index ?? -1
        queueRearIndex.value = state.rear_index ?? -1
      }
      console.log(`✓ 结构已创建，容量: ${capacity.value ?? '∞'}，元素: ${elements.value.length}`)
    }
    if (structureType.value === 'stack') {
      stackStarted.value = true
    }
  } catch (error) {
    console.error('创建数据结构失败:', error)
    alert('创建数据结构失败')
  }
}

// 🔥 处理代码加载完成
const handleCodeLoaded = (code) => {
  currentCode.value = code
  console.log('✓ 代码已加载:', code.substring(0, 100))
}

// 🔥 处理语言切换
const handleLanguageChange = async (language) => {
  console.log('🔥 语言切换:', currentLanguage.value, '->', language)
  currentLanguage.value = language

  // If currently displaying code, reload in new language
  if (currentOperationName.value) {
    // Extract template key from currentOperationName
    // Format: "sequential::insert()" -> "sequential_insert"
    const parts = currentOperationName.value.split('::')
    if (parts.length === 2) {
      const structureType = parts[0]
      const operation = parts[1].replace('()', '')
      const templateKey = `${structureType}_${operation}`
      await loadCodeTemplate(templateKey, language)
      applyHighlightForLanguage(templateKey, language)
    }
  }
}

//监听路由变化（可选，用于热重载场景）
watch(() => route.query.importId, async (newId) => {
  if (newId && newId !== structureId.value) {
    await createOrLoadStructure()
  }
})

watch(structureType, (newType) => {
  if (newType === 'stack') {
    stackStarted.value = false
  }
  if (newType === 'queue') {
    queueFrontIndex.value = -1
    queueRearIndex.value = -1
  }
  const ops = availableOperations.value
  if (ops.length > 0) {
    currentOperation.value = ops[0].value
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
  flex-direction: column;
  align-items: flex-start;
  position: relative;
  padding-left: 60px;
}

.stack-area {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
  flex-wrap: wrap;
}

.stack-container-outer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stack-border {
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  position: relative;
  background: white;
  min-width: 120px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column-reverse; /* 栈底在下方，栈顶在上方 */
  align-items: center;
  gap: 0.5rem;
}

.stack-border.ghost-border {
  border: 2px dashed #9ca3af;
  background: #f9fafb;
}

.stack-container-outer.old-array-delete .stack-border {
  border-color: #fca5a5;
}

.stack-container-outer.ghost .element-node {
  opacity: 0.8;
}

.stack-wrapper {
  align-items: flex-start;
  flex-direction: column;
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
  position: relative;
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
  left: -50px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  font-weight: 700;
  color: #ef4444;
  background-color: #fee2e2;
  padding: 0.25rem 0.6rem;
  border-radius: 0.75rem;
}

.queue-indicator {
  position: absolute;
  top: 6px;
  right: 6px;
  padding: 0.15rem 0.4rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.queue-indicator.front {
  background: #e0f2fe;
  color: #0369a1;
}

.queue-indicator.rear {
  background: #f3e8ff;
  color: #7c3aed;
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

/* 🔥 扩容动画相关样式 */
.array-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  max-width: calc(10 * (80px + 1rem));
  position: relative;
  padding: 2rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.5s ease;
}

.array-label {
  position: absolute;
  top: 0.5rem;
  left: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  background-color: #f3f4f6;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
}

.new-array-container {
  margin-top: 3rem;
  background-color: #f0fdf4;
  border: 2px dashed #10b981;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.new-array-node {
  background-color: #10b981;
  opacity: 0.7;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
  to {
    opacity: 0.7;
    transform: scale(1);
  }
}

.delete-marked {
  background-color: #ef4444 !important;
  animation: deleteFlash 1s ease-in-out infinite;
}

.old-array-delete {
  animation: fadeOut 1s ease-out forwards;
}

@keyframes deleteFlash {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(0.95);
  }
}

@keyframes fadeOut {
  0% {
    opacity: 1;
  }
  70% {
    opacity: 0.5;
  }
  100% {
    opacity: 0;
    transform: scale(0.9);
  }
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
