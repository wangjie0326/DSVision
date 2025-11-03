<template>
  <div class="tree-canvas" ref="canvasEl" @resize="onResize">
    <!-- SVG overlay for lines -->
    <svg class="connection-svg" ref="svgEl" :width="canvasSize.width" :height="canvasSize.height">
      <g v-for="edge in edges" :key="edge.id">
        <path
          :d="edge.path"
          stroke="#6b7280"
          stroke-width="2"
          fill="none"
          stroke-linecap="round"
        />
        <!-- 可选箭头 -->
        <!-- <circle :cx="edge.end.x" :cy="edge.end.y" r="3" fill="#6b7280" /> -->
      </g>
    </svg>

    <!-- 你的树节点插槽/渲染区域 -->
    <div class="nodes-layer">
      <!-- 将 TreeNode 放在这里并监听 register/unregister -->
      <!-- 假设你使用递归 TreeNode 的渲染方式：根节点 -->
      <TreeNode
        :node="root"
        @register-node="handleRegister"
        @unregister-node="handleUnregister"
        @insert-left="$emit('insert-left', $event)"
        @insert-right="$emit('insert-right', $event)"
        @delete-node="$emit('delete-node', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import TreeNode from './TreeNode.vue' // 你的节点文件路径

const props = defineProps({
  root: { type: Object, required: true }
})
const emit = defineEmits(['insert-left','insert-right','delete-node'])

const canvasEl = ref(null)
const svgEl = ref(null)

// 注册表：nodeId -> { el, rect }
const nodes = reactive(new Map())

// svg / canvas size
const canvasSize = reactive({ width: 2000, height: 2000 }) // 初始值，onMounted 会调整

// edges 列表由 nodes 动态计算
const edges = ref([])

// 接收 TreeNode 的 register 事件
const handleRegister = ({ id, el }) => {
  nodes.set(id, { el, rect: null })
  updateNodeRect(id)
  scheduleRecompute()
}
const handleUnregister = ({ id }) => {
  nodes.delete(id)
  scheduleRecompute()
}

// 更新一个 node 的 DOMRect
function updateNodeRect(id) {
  const rec = nodes.get(id)
  if (!rec || !rec.el) return
  const rect = rec.el.getBoundingClientRect()
  // 将 rect 转换到 canvas 内相对坐标（svg 在 canvas 的左上角）
  const canvasRect = canvasEl.value.getBoundingClientRect()
  rec.rect = {
    x: rect.left - canvasRect.left,
    y: rect.top - canvasRect.top,
    width: rect.width,
    height: rect.height,
    centerX: rect.left - canvasRect.left + rect.width / 2,
    centerY: rect.top - canvasRect.top + rect.height / 2
  }
}

// 当布局发生变化或者窗口 resize，我们更新所有 rect
function updateAllRects() {
  if (!canvasEl.value) return
  const canvasRect = canvasEl.value.getBoundingClientRect()
  // 可选：更新 canvasSize 以匹配容器
  canvasSize.width = Math.max(canvasRect.width, 1200)
  canvasSize.height = Math.max(canvasRect.height, 1200)

  for (const [id, rec] of nodes) {
    if (!rec.el) continue
    const domRect = rec.el.getBoundingClientRect()
    rec.rect = {
      x: domRect.left - canvasRect.left,
      y: domRect.top - canvasRect.top,
      width: domRect.width,
      height: domRect.height,
      centerX: domRect.left - canvasRect.left + domRect.width / 2,
      centerY: domRect.top - canvasRect.top + domRect.height / 2
    }
  }
}

// 计算所有边（父->子）
function computeEdges() {
  const list = []
  // 遍历树（递归）
  const traverse = (node) => {
    if (!node || !nodes.has(node.node_id)) return
    const parent = nodes.get(node.node_id)
    if (!parent || !parent.rect) return

    const parentRect = parent.rect

    // 父节点圆半径（假设圆形；如果方形或其它，按最大半径）
    const radius = Math.max(parentRect.width, parentRect.height) / 2

    // 我们要求：从父节点 4点钟 (-30deg) 与 8点钟 (-150deg) 发出
    // 右子节点使用 -30° 起点，左子节点使用 -150° 起点
    const angleRight = (-30 * Math.PI) / 180
    const angleLeft  = (-150 * Math.PI) / 180

    const makeEdge = (childNode, angle, side) => {
      if (!childNode) return
      const childRec = nodes.get(childNode.node_id)
      if (!childRec || !childRec.rect) return

      const startX = parentRect.centerX + radius * Math.cos(angle)
      const startY = parentRect.centerY + radius * Math.sin(angle)

      // end is child top-center (12点钟)
      const endX = childRec.rect.centerX
      const endY = childRec.rect.y // top edge

      // 计算贝塞尔控制点，向下/向外拉伸以形成自然弯曲
      const dx = endX - startX
      const dy = endY - startY

      // 基础控制点距离 = 0.5 * abs(dx) + 40 （经验值）
      const cpDist = Math.max(Math.abs(dx) * 0.4, 40)

      // 控制点1 在起点的垂直方向延伸（朝向子节点）
      // 控制点2 在终点的垂直方向上方一些，使曲线向上接触子节点顶部
      let cp1x = startX + (side === 'right' ? cpDist : -cpDist) * 0.4
      let cp1y = startY + cpDist * 0.6

      let cp2x = endX
      let cp2y = endY - cpDist * 0.6

      // 调整：如果 start 已经在 end 左侧/右侧，控制点调整为更水平/更垂直
      if (Math.abs(dx) < 30) {
        cp1x = startX
        cp2x = endX
      }

      const path = `M ${startX} ${startY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${endX} ${endY}`

      list.push({
        id: `${node.node_id}-${childNode.node_id}`,
        path,
        start: { x: startX, y: startY },
        end: { x: endX, y: endY }
      })
    }

    if (node.left) makeEdge(node.left, angleLeft, 'left')
    if (node.right) makeEdge(node.right, angleRight, 'right')

    if (node.left) traverse(node.left)
    if (node.right) traverse(node.right)
  }

  traverse(props.root)
  edges.value = list
}

// 防抖更新
let updateTimer = null
function scheduleRecompute() {
  if (updateTimer) clearTimeout(updateTimer)
  updateTimer = setTimeout(() => {
    updateAllRects()
    computeEdges()
    updateTimer = null
  }, 60) // 60ms 防抖
}

// 监听窗口 resize
function onResize() {
  scheduleRecompute()
}

// 初始化
onMounted(() => {
  // 小延迟，等节点都 mount 完
  setTimeout(() => {
    updateAllRects()
    computeEdges()
  }, 120)
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.tree-canvas {
  position: relative;
  width: 100%;
  min-height: 600px; /* 根据需要调整 */
  overflow: visible;
}

/* SVG 覆盖在最顶层，pointer-events: none 让节点可被交互 */
.connection-svg {
  position: absolute;
  left: 0;
  top: 0;
  pointer-events: none;
  z-index: 1;
}

/* nodes 层放在 svg 之上 */
.nodes-layer {
  position: relative;
  z-index: 2;
}
</style>
