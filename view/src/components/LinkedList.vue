<template>
  <div class="linked-list-canvas" @wheel="handleWheel" @mousedown="handleMouseDown" @mousemove="handleMouseMove" @mouseup="handleMouseUp" @mouseleave="handleMouseUp">
    <svg
      ref="svgRef"
      :width="canvasWidth"
      :height="canvasHeight"
      class="canvas-svg"
      :viewBox="`${panX} ${panY} ${1600 / scale} ${600 / scale}`"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- 定义箭头标记和阴影效果 -->
      <defs>
        <!-- 节点阴影效果 -->
        <filter id="shadow">
          <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.2" />
        </filter>

        <!-- 节点间链接箭头（黑色，小箭头） -->
        <marker
          id="arrowhead-node"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="5"
          orient="auto"
        >
          <polygon points="0 0, 10 5, 0 10" fill="#333" />
        </marker>
        <!-- 指针箭头（红色-head，小） -->
        <marker
          id="arrowhead-red"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="5"
          orient="auto"
        >
          <polygon points="0 0, 10 5, 0 10" fill="#e74c3c" />
        </marker>
        <!-- 指针箭头（蓝色-prev，小） -->
        <marker
          id="arrowhead-blue"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="5"
          orient="auto"
        >
          <polygon points="0 0, 10 5, 0 10" fill="#3498db" />
        </marker>
        <!-- 指针箭头（绿色-current，小） -->
        <marker
          id="arrowhead-green"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="5"
          orient="auto"
        >
          <polygon points="0 0, 10 5, 0 10" fill="#27ae60" />
        </marker>
        <!-- 向上指的绿色箭头（current用，正三角） -->
        <marker
          id="arrowhead-green-up"
          markerWidth="10"
          markerHeight="10"
          refX="5"
          refY="9.6"
          orient="180"
        >
          <polygon points="0 0, 5 10, 10 0" fill="#27ae60" />
        </marker>
        <!-- 向下指的蓝色箭头（prev用，倒三角） -->
        <marker
          id="arrowhead-blue-down"
          markerWidth="10"
          markerHeight="10"
          refX="5"
          refY="1.1"
          orient="180"
        >
          <polygon points="0 10, 5 0, 10 10" fill="#3498db" />
        </marker>
      </defs>

      <!-- 绘制指针变量（head, prev等） -->
      <g class="pointers-layer">
        <!-- HEAD 指针 -->
        <g v-if="nodes.length > 0">
          <text x="30" y="335" class="pointer-label">HEAD</text>
          <circle cx="65" cy="325" r="5" fill="#e74c3c" stroke="#333" stroke-width="1" />
          <line
            x1="65"
            y1="325"
            :x2="nodes[0].x"
            :y2="nodeY + nodeHeight / 2"
            stroke="#e74c3c"
            stroke-width="3"
            stroke-dasharray="5,5"
            marker-end="url(#arrowhead-red)"
          />
        </g>

        <!-- PREV 指针（从上方向下，竖直向下，箭头接触节点上方边缘） -->
        <g v-if="pointerStates && pointerStates.prev >= 0 && pointerStates.prev < nodes.length">
          <text
            :x="nodes[pointerStates.prev].x + nodeCellWidth / 2"
            y="210"
            class="pointer-label"
            text-anchor="middle"
          >
            PREV
          </text>
          <!-- 圆点在上方 -->
          <circle
            :cx="nodes[pointerStates.prev].x + nodeCellWidth / 2"
            :cy="230"
            r="5"
            fill="#3498db"
            stroke="#333"
            stroke-width="1"
          />
          <!-- 竖直向下的线，箭头接触节点上边缘 -->
          <line
            :x1="nodes[pointerStates.prev].x + nodeCellWidth / 2"
            :y1="240"
            :x2="nodes[pointerStates.prev].x + nodeCellWidth / 2"
            :y2="nodeY"
            stroke="#3498db"
            stroke-width="3"
            stroke-dasharray="5,5"
            marker-end="url(#arrowhead-blue-down)"
          />
        </g>

        <!-- CURRENT 指针（在节点下方，竖直向上，箭头接触节点下方边缘） -->
        <g v-if="pointerStates && pointerStates.current >= 0 && pointerStates.current < nodes.length">
          <!-- 圆点 -->
          <circle
            :cx="nodes[pointerStates.current].x + nodeCellWidth / 2"
            :cy="nodeY + nodeHeight + 100"
            r="5"
            fill="#27ae60"
            stroke="#333"
            stroke-width="1"
          />
          <!-- 竖直向上的线，箭头接触节点下边缘 -->
          <line
            :x1="nodes[pointerStates.current].x + nodeCellWidth / 2"
            :y1="nodeY + nodeHeight + 95"
            :x2="nodes[pointerStates.current].x + nodeCellWidth / 2"
            :y2="nodeY + nodeHeight"
            stroke="#27ae60"
            stroke-width="3"
            stroke-dasharray="5,5"
            marker-end="url(#arrowhead-green-up)"
          />
          <!-- 标签 -->
          <text
            :x="nodes[pointerStates.current].x + nodeCellWidth / 2"
            :y="nodeY + nodeHeight + 125"
            class="pointer-label"
            text-anchor="middle"
          >
            CURR
          </text>
        </g>
      </g>

      <!-- 绘制链表节点 -->
      <g v-for="(node, index) in nodes" :key="index" class="node-group">
        <!-- 节点边界矩形（带阴影） -->
        <rect
          :x="node.x"
          :y="nodeY"
          :width="nodeCellWidth"
          :height="nodeHeight"
          :fill="getNodeFill(index)"
          stroke="#333"
          stroke-width="2"
          rx="3"
          class="node-boundary"
          filter="url(#shadow)"
        />

        <!-- 数据值区域 -->
        <rect
          :x="node.x"
          :y="nodeY"
          :width="dataCellWidth"
          :height="nodeHeight"
          fill="none"
          stroke="#333"
          stroke-width="1"
        />

        <!-- 指针域区域 -->
        <rect
          :x="node.x + dataCellWidth"
          :y="nodeY"
          :width="pointerCellWidth"
          :height="nodeHeight"
          fill="none"
          stroke="#333"
          stroke-width="1"
        />

        <!-- 数据值文本 -->
        <text
          :x="node.x + dataCellWidth / 2"
          :y="nodeY + nodeHeight / 2"
          class="node-text"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          {{ node.value }}
        </text>

        <!-- 指针域文本（显示 NULL 或链接符号） -->
        <text
          v-if="index < nodes.length - 1"
          :x="node.x + dataCellWidth + pointerCellWidth / 2"
          :y="nodeY + nodeHeight / 2"
          class="pointer-content"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          ◦
        </text>
        <text
          v-else
          :x="node.x + dataCellWidth + pointerCellWidth / 2"
          :y="nodeY + nodeHeight / 2"
          class="null-pointer"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          ∅
        </text>

        <!-- 索引标签 -->
        <text
          :x="node.x + nodeCellWidth / 2"
          :y="nodeY - 25"
          class="index-text"
          text-anchor="middle"
        >
          [{{ index }}]
        </text>

        <!-- 从节点右侧中心指向下一个节点的连接线 -->
        <g v-if="index < nodes.length - 1">
          <line
            :x1="node.x + dataCellWidth + pointerCellWidth / 2"
            :y1="nodeY + nodeHeight / 2"
            :x2="nodes[index + 1].x"
            :y2="nodeY + nodeHeight / 2"
            stroke="#333"
            stroke-width="3"
            marker-end="url(#arrowhead-node)"
          />
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  highlightIndices: {
    type: Array,
    default: () => []
  },
  pointerStates: {
    type: Object,
    default: () => ({ head: -1, prev: -1, current: -1 })
  }
})

const svgRef = ref(null)
const canvasWidth = ref(1600)
const canvasHeight = ref(600)

// 缩放和拖动状态
const scale = ref(1)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragStartPanX = ref(0)
const dragStartPanY = ref(0)

// 节点样式配置（教科书风格）
const dataCellWidth = 80      // 数据域宽度
const pointerCellWidth = 50   // 指针域宽度
const nodeCellWidth = dataCellWidth + pointerCellWidth  // 整个节点宽度
const nodeHeight = 60         // 节点高度
const horizontalGap = 80      // 节点间距
const startX = 200            // 起始X位置
const nodeY = 300             // 节点Y位置（固定）

// 计算节点位置
const nodes = computed(() => {
  return props.data.map((value, index) => ({
    value,
    x: startX + index * (nodeCellWidth + horizontalGap)
  }))
})

// 检查节点是否被高亮
const isHighlighted = (index) => {
  return props.highlightIndices.includes(index)
}

// 获取节点填充色（淡红色高亮）
const getNodeFill = (index) => {
  if (isHighlighted(index)) {
    return '#ffcccc'  // 淡红色
  }
  return 'white'
}

// 鼠标滚轮缩放
const handleWheel = (event) => {
  event.preventDefault()
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  const newScale = Math.max(0.5, Math.min(3, scale.value + delta))
  scale.value = newScale
}

// 鼠标拖动
const handleMouseDown = (event) => {
  isDragging.value = true
  dragStartX.value = event.clientX
  dragStartY.value = event.clientY
  dragStartPanX.value = panX.value
  dragStartPanY.value = panY.value
}

const handleMouseMove = (event) => {
  if (!isDragging.value) return
  const deltaX = event.clientX - dragStartX.value
  const deltaY = event.clientY - dragStartY.value
  panX.value = dragStartPanX.value - deltaX / scale.value
  panY.value = dragStartPanY.value - deltaY / scale.value
}

const handleMouseUp = () => {
  isDragging.value = false
}

// 监听数据变化，调整画布宽度
watch(() => props.data.length, (newLength) => {
  if (newLength > 0) {
    const requiredWidth = startX + newLength * (nodeCellWidth + horizontalGap) + 100
    canvasWidth.value = Math.max(1600, requiredWidth)
  }
}, { immediate: true })
</script>

<style scoped>
.linked-list-canvas {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: transparent;
  cursor: grab;
  user-select: none;
}

.linked-list-canvas:active {
  cursor: grabbing;
}

.canvas-svg {
  display: block;
  width: 100%;
  height: 100%;
}

/* 节点相关样式 */
.node-boundary {
  transition: fill 0.3s ease, stroke 0.3s ease;
}

.node-boundary:hover {
  filter: drop-shadow(0 0 8px rgba(0, 0, 0, 0.15));
}

.node-text {
  font-size: 20px;
  font-weight: 700;
  fill: #2c3e50;
  pointer-events: none;
  font-family: 'Monaco', 'Courier New', monospace;
}

/* 指针域相关 */
.pointer-content {
  font-size: 16px;
  font-weight: bold;
  fill: #3498db;
  pointer-events: none;
}

.null-pointer {
  font-size: 18px;
  font-weight: bold;
  fill: #95a5a6;
  pointer-events: none;
}

/* 索引标签 */
.index-text {
  font-size: 14px;
  font-weight: 600;
  fill: #7f8c8d;
  pointer-events: none;
  font-family: 'Monaco', 'Courier New', monospace;
}

/* 指针变量（head, prev, curr） */
.pointer-label {
  font-size: 14px;
  font-weight: 700;
  fill: #2c3e50;
  pointer-events: none;
  font-family: 'Monaco', 'Courier New', monospace;
}

.pointers-layer {
  animation: fadeIn 0.5s ease-in;
}

.node-group {
  animation: slideIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 高亮动画（淡红色） */
@keyframes pulse {
  0%, 100% {
    fill: white;
    filter: drop-shadow(0 0 0px rgba(255, 100, 100, 0.3));
  }
  50% {
    fill: #ffcccc;
    filter: drop-shadow(0 0 8px rgba(255, 100, 100, 0.6));
  }
}

.node-boundary.highlight {
  animation: pulse 0.6s ease-in-out;
}
</style>
