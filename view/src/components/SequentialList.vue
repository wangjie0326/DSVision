<template>
  <div class="sequential-canvas" ref="canvasContainer">
    <svg :width="svgWidth" :height="svgHeight">
      <!-- 绘制网格背景 -->
      <defs>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" stroke-width="0.5"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />

      <!-- 绘制容量指示器 -->
      <g v-for="i in capacity" :key="`slot-${i}`">
        <circle
          :cx="getNodeX(i - 1)"
          :cy="nodeY"
          :r="nodeRadius"
          fill="#f9fafb"
          stroke="#e5e7eb"
          stroke-width="2"
          opacity="0.5"
        />
        <text
          :x="getNodeX(i - 1)"
          :y="nodeY + nodeRadius + 25"
          text-anchor="middle"
          font-size="12"
          fill="#9ca3af"
        >
          {{ i - 1 }}
        </text>
      </g>

      <!-- 绘制实际数据节点 -->
      <g v-for="(item, index) in data" :key="`node-${index}`">
        <!-- 节点圆圈 -->
        <circle
          :cx="getNodeX(index)"
          :cy="nodeY"
          :r="nodeRadius"
          :fill="isHighlighted(index) ? '#3b82f6' : '#ffffff'"
          :stroke="isHighlighted(index) ? '#2563eb' : '#111827'"
          stroke-width="2"
          class="node-circle"
          :class="{ 'highlighted': isHighlighted(index) }"
        />

        <!-- 节点值 -->
        <text
          :x="getNodeX(index)"
          :y="nodeY"
          text-anchor="middle"
          dominant-baseline="central"
          font-size="16"
          font-weight="600"
          :fill="isHighlighted(index) ? '#ffffff' : '#111827'"
          class="node-text"
        >
          {{ item }}
        </text>

        <!-- 连接线（箭头） -->
        <g v-if="index < data.length - 1">
          <defs>
            <marker
              :id="`arrowhead-${index}`"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#6b7280" />
            </marker>
          </defs>
          <line
            :x1="getNodeX(index) + nodeRadius + 5"
            :y1="nodeY"
            :x2="getNodeX(index + 1) - nodeRadius - 5"
            :y2="nodeY"
            stroke="#6b7280"
            stroke-width="2"
            :marker-end="`url(#arrowhead-${index})`"
          />
        </g>
      </g>

      <!-- 空状态提示 -->
      <g v-if="data.length === 0">
        <text
          :x="svgWidth / 2"
          :y="svgHeight / 2"
          text-anchor="middle"
          font-size="18"
          fill="#9ca3af"
        >
          Empty Sequential List - Insert elements to begin
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  highlighted: {
    type: Array,
    default: () => []
  },
  capacity: {
    type: Number,
    default: 100
  }
})

const canvasContainer = ref(null)
const nodeRadius = 30
const nodeSpacing = 100
const nodeY = 150
const padding = 60

const svgWidth = computed(() => {
  const minWidth = 800
  const calculatedWidth = Math.max(props.capacity, props.data.length) * nodeSpacing + padding * 2
  return Math.max(minWidth, calculatedWidth)
})

const svgHeight = computed(() => 300)

const getNodeX = (index) => {
  return padding + nodeSpacing / 2 + index * nodeSpacing
}

const isHighlighted = (index) => {
  return props.highlighted.includes(index)
}
</script>

<style scoped>
.sequential-canvas {
  width: 100%;
  height: 100%;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

svg {
  display: block;
}

.node-circle {
  transition: all 0.3s ease;
  cursor: pointer;
}

.node-circle:hover {
  filter: brightness(0.95);
}

.node-circle.highlighted {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.node-text {
  pointer-events: none;
  user-select: none;
}
</style>
