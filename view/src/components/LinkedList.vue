<template>
  <div class="linked-list-canvas">
    <svg
      ref="svgRef"
      :width="canvasWidth"
      :height="canvasHeight"
      class="canvas-svg"
    >
      <!-- 绘制链表节点和箭头 -->
      <g v-for="(node, index) in nodes" :key="index">
        <!-- 节点矩形 -->
        <rect
          :x="node.x"
          :y="node.y"
          :width="nodeWidth"
          :height="nodeHeight"
          :class="['node-rect', { 'highlight': isHighlighted(index) }]"
          :fill="getNodeFill(index)"
          stroke="#333"
          stroke-width="2"
          rx="4"
        />

        <!-- 数据区域 -->
        <text
          :x="node.x + nodeWidth * 0.35"
          :y="node.y + nodeHeight / 2"
          class="node-text"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          {{ node.value }}
        </text>

        <!-- 分隔线 -->
        <line
          :x1="node.x + nodeWidth * 0.7"
          :y1="node.y"
          :x2="node.x + nodeWidth * 0.7"
          :y2="node.y + nodeHeight"
          stroke="#333"
          stroke-width="1"
        />

        <!-- 指针区域箭头 -->
        <text
          v-if="index < nodes.length - 1"
          :x="node.x + nodeWidth * 0.85"
          :y="node.y + nodeHeight / 2"
          class="pointer-text"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          →
        </text>

        <!-- NULL 指针 -->
        <text
          v-else
          :x="node.x + nodeWidth * 0.85"
          :y="node.y + nodeHeight / 2"
          class="null-text"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          ∅
        </text>

        <!-- 索引标签 -->
        <text
          :x="node.x + nodeWidth / 2"
          :y="node.y - 10"
          class="index-text"
          text-anchor="middle"
        >
          [{{ index }}]
        </text>

        <!-- 连接箭头 -->
        <g v-if="index < nodes.length - 1">
          <line
            :x1="node.x + nodeWidth"
            :y1="node.y + nodeHeight / 2"
            :x2="nodes[index + 1].x"
            :y2="nodes[index + 1].y + nodeHeight / 2"
            stroke="#666"
            stroke-width="2"
            marker-end="url(#arrowhead)"
          />
        </g>
      </g>

      <!-- HEAD 指针 -->
      <g v-if="nodes.length > 0">
        <text
          :x="nodes[0].x - 80"
          :y="nodes[0].y + nodeHeight / 2 - 20"
          class="head-text"
          text-anchor="middle"
        >
          HEAD
        </text>
        <line
          :x1="nodes[0].x - 80"
          :y1="nodes[0].y + nodeHeight / 2"
          :x2="nodes[0].x - 10"
          :y2="nodes[0].y + nodeHeight / 2"
          stroke="#e74c3c"
          stroke-width="2"
          marker-end="url(#arrowhead-red)"
        />
      </g>

      <!-- 箭头定义 -->
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon points="0 0, 10 3, 0 6" fill="#666" />
        </marker>
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
  highlightIndices: {
    type: Array,
    default: () => []
  }
})

const svgRef = ref(null)
const canvasWidth = ref(1200)
const canvasHeight = ref(400)

// 节点样式配置
const nodeWidth = 100
const nodeHeight = 60
const horizontalGap = 60
const startX = 150
const startY = 170

// 计算节点位置
const nodes = computed(() => {
  return props.data.map((value, index) => ({
    value,
    x: startX + index * (nodeWidth + horizontalGap),
    y: startY
  }))
})

// 检查节点是否被高亮
const isHighlighted = (index) => {
  return props.highlightIndices.includes(index)
}

// 获取节点填充色
const getNodeFill = (index) => {
  if (isHighlighted(index)) {
    return '#ffeaa7'
  }
  return 'white'
}

// 监听数据变化，调整画布宽度
watch(() => props.data.length, (newLength) => {
  if (newLength > 0) {
    const requiredWidth = startX + newLength * (nodeWidth + horizontalGap) + 100
    canvasWidth.value = Math.max(1200, requiredWidth)
  }
}, { immediate: true })
</script>

<style scoped>
.linked-list-canvas {
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: #f8f9fa;
}

.canvas-svg {
  display: block;
  min-width: 100%;
  min-height: 100%;
}

.node-rect {
  transition: all 0.3s ease;
}

.node-rect.highlight {
  animation: pulse 0.5s ease-in-out;
}

.node-text {
  font-size: 18px;
  font-weight: 600;
  fill: #2c3e50;
  pointer-events: none;
}

.pointer-text {
  font-size: 24px;
  font-weight: bold;
  fill: #3498db;
  pointer-events: none;
}

.null-text {
  font-size: 20px;
  font-weight: bold;
  fill: #95a5a6;
  pointer-events: none;
}

.index-text {
  font-size: 14px;
  fill: #7f8c8d;
  pointer-events: none;
}

.head-text {
  font-size: 16px;
  font-weight: bold;
  fill: #e74c3c;
  pointer-events: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}
</style>
