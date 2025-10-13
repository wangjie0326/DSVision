<template>
  <div class="stack-canvas">
    <svg
      ref="svgRef"
      :width="canvasWidth"
      :height="canvasHeight"
      class="canvas-svg"
    >
      <!-- 栈的外框 -->
      <g v-if="capacity > 0">
        <!-- 底座 -->
        <rect
          :x="baseX - 10"
          :y="baseY + 10"
          :width="stackWidth + 20"
          :height="20"
          fill="#34495e"
          rx="4"
        />

        <!-- 左边框 -->
        <line
          :x1="baseX"
          :y1="baseY - (capacity - 1) * cellHeight"
          :x2="baseX"
          :y2="baseY + 10"
          stroke="#2c3e50"
          stroke-width="3"
        />

        <!-- 右边框 -->
        <line
          :x1="baseX + stackWidth"
          :y1="baseY - (capacity - 1) * cellHeight"
          :x2="baseX + stackWidth"
          :y2="baseY + 10"
          stroke="#2c3e50"
          stroke-width="3"
        />
      </g>

      <!-- 栈的单元格 -->
      <g v-for="(cell, index) in cells" :key="index">
        <!-- 单元格矩形 -->
        <rect
          :x="cell.x"
          :y="cell.y"
          :width="stackWidth"
          :height="cellHeight"
          :class="['cell-rect', {
            'highlight': isHighlighted(cell.logicalIndex),
            'empty': cell.isEmpty,
            'top-cell': cell.logicalIndex === topIndex
          }]"
          :fill="getCellFill(cell)"
          stroke="#2c3e50"
          stroke-width="2"
        />

        <!-- 单元格内容 -->
        <text
          v-if="!cell.isEmpty"
          :x="cell.x + stackWidth / 2"
          :y="cell.y + cellHeight / 2"
          class="cell-text"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          {{ cell.value }}
        </text>

        <!-- 空单元格显示虚线 -->
        <text
          v-else
          :x="cell.x + stackWidth / 2"
          :y="cell.y + cellHeight / 2"
          class="empty-text"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          -
        </text>

        <!-- 索引标签 -->
        <text
          :x="cell.x - 40"
          :y="cell.y + cellHeight / 2"
          class="index-text"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          [{{ cell.logicalIndex }}]
        </text>
      </g>

      <!-- TOP 指针 -->
      <g v-if="topIndex >= 0 && cells.length > 0">
        <text
          :x="baseX + stackWidth + 60"
          :y="cells[topIndex].y + cellHeight / 2 - 20"
          class="top-label"
          text-anchor="middle"
        >
          TOP
        </text>
        <line
          :x1="baseX + stackWidth + 60"
          :y1="cells[topIndex].y + cellHeight / 2"
          :x2="baseX + stackWidth + 10"
          :y2="cells[topIndex].y + cellHeight / 2"
          stroke="#e74c3c"
          stroke-width="3"
          marker-end="url(#arrowhead-red)"
        />
      </g>

      <!-- 空栈提示 -->
      <g v-if="topIndex < 0">
        <text
          :x="baseX + stackWidth + 60"
          :y="baseY"
          class="empty-stack-text"
          text-anchor="middle"
        >
          栈空
        </text>
      </g>

      <!-- 容量标签 -->
      <text
        :x="baseX + stackWidth / 2"
        :y="baseY + 50"
        class="capacity-text"
        text-anchor="middle"
      >
        容量: {{ capacity }}
      </text>

      <!-- 当前大小标签 -->
      <text
        :x="baseX + stackWidth / 2"
        :y="baseY + 75"
        class="size-text"
        text-anchor="middle"
      >
        大小: {{ currentSize }}
      </text>

      <!-- 箭头定义 -->
      <defs>
        <marker
          id="arrowhead-red"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon points="0 0, 10 3, 0 6" fill="#e74c3c" />
        </marker>
      </defs>
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
  capacity: {
    type: Number,
    default: 10
  },
  topIndex: {
    type: Number,
    default: -1
  },
  highlightIndices: {
    type: Array,
    default: () => []
  }
})

const svgRef = ref(null)
const canvasWidth = ref(600)
const canvasHeight = ref(800)

// 栈的样式配置
const stackWidth = 120
const cellHeight = 50
const baseX = 200
const baseY = computed(() => 650)

// 当前栈的大小
const currentSize = computed(() => props.data.length)

// 计算所有单元格（包括空的）
const cells = computed(() => {
  const result = []

  // 从栈底到栈顶显示（逻辑上索引0在底部）
  for (let i = 0; i < props.capacity; i++) {
    const logicalIndex = i
    const visualIndex = props.capacity - 1 - i // 视觉上反转，栈顶在上

    result.push({
      logicalIndex,
      visualIndex,
      x: baseX,
      y: baseY.value - (visualIndex + 1) * cellHeight,
      value: i < props.data.length ? props.data[i] : null,
      isEmpty: i >= props.data.length
    })
  }

  return result
})

// 检查单元格是否被高亮
const isHighlighted = (index) => {
  return props.highlightIndices.includes(index)
}

// 获取单元格填充色
const getCellFill = (cell) => {
  if (isHighlighted(cell.logicalIndex)) {
    return '#ffeaa7' // 高亮黄色
  }
  if (cell.logicalIndex === props.topIndex) {
    return '#74b9ff' // 栈顶蓝色
  }
  if (cell.isEmpty) {
    return '#ecf0f1' // 空单元格灰色
  }
  return 'white' // 普通单元格白色
}

// 根据容量调整画布高度
watch(() => props.capacity, (newCapacity) => {
  const requiredHeight = 200 + newCapacity * cellHeight
  canvasHeight.value = Math.max(800, requiredHeight)
}, { immediate: true })
</script>

<style scoped>
.stack-canvas {
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.canvas-svg {
  display: block;
}

.cell-rect {
  transition: all 0.3s ease;
}

.cell-rect.highlight {
  animation: pulse 0.5s ease-in-out;
  filter: drop-shadow(0 0 8px rgba(255, 234, 167, 0.8));
}

.cell-rect.top-cell {
  stroke: #e74c3c;
  stroke-width: 3;
}

.cell-text {
  font-size: 20px;
  font-weight: 600;
  fill: #2c3e50;
  pointer-events: none;
}

.empty-text {
  font-size: 18px;
  fill: #bdc3c7;
  pointer-events: none;
}

.index-text {
  font-size: 14px;
  fill: #7f8c8d;
  font-weight: 500;
  pointer-events: none;
}

.top-label {
  font-size: 18px;
  font-weight: bold;
  fill: #e74c3c;
  pointer-events: none;
}

.empty-stack-text {
  font-size: 16px;
  fill: #95a5a6;
  font-style: italic;
  pointer-events: none;
}

.capacity-text {
  font-size: 14px;
  fill: #34495e;
  font-weight: 500;
  pointer-events: none;
}

.size-text {
  font-size: 14px;
  fill: #27ae60;
  font-weight: 600;
  pointer-events: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.02);
  }
}
</style>
