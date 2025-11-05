<template>
  <div class="tree-canvas" ref="canvasEl" @resize="onResize">
    <!-- SVG overlay for lines -->
    <!-- SVG overlay for lines -->
    <svg class="connection-svg" ref="svgEl" :width="canvasSize.width" :height="canvasSize.height">
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="10"
          refY="3.5"
          orient="auto"
        >
          <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
        </marker>
      </defs>

      <g v-for="edge in edges" :key="edge.id">
        <line
          :x1="edge.start.x"
          :y1="edge.start.y"
          :x2="edge.end.x"
          :y2="edge.end.y"
          stroke="#6b7280"
          stroke-width="2"
          stroke-linecap="round"
          marker-end="url(#arrowhead)"
        />
      </g>
    </svg>


    <!-- 你的树节点插槽/渲染区域 -->
    <div class="nodes-layer">
      <!-- 将 TreeNode 放在这里并监听 register/unregister -->
      <!-- 假设你使用递归 TreeNode 的渲染方式：根节点 -->
      <TreeNode
        :node="root"
        :highlighted="highlighted"
        :isHuffman="isHuffman"
        :currentAnimation="currentAnimation"
        :useExternalEdges="true"
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
  root: { type: Object, required: true },
  highlighted: { type: Array, default: () => [] },
  isHuffman: { type: Boolean, default: false },
  currentAnimation: { type: String, default: '' }
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
// 计算所有边（父->子）
function computeEdges() {
  const list = [];
  const radius = 30; // 节点半径（可与 nodeWidth/2 保持一致）

  const traverse = (node) => {
    if (!node || !nodes.has(node.node_id)) return;
    const parentRec = nodes.get(node.node_id)?.rect;
    if (!parentRec) return;

    const parentCenter = { x: parentRec.centerX, y: parentRec.centerY };

    const makeEdge = (childNode) => {
      if (!childNode || !nodes.has(childNode.node_id)) return;
      const childRec = nodes.get(childNode.node_id)?.rect;
      if (!childRec) return;

      const childCenter = { x: childRec.centerX, y: childRec.centerY };

      // 向量方向
      const dx = childCenter.x - parentCenter.x;
      const dy = childCenter.y - parentCenter.y;
      const angle = Math.atan2(dy, dx);

      // 起点在父节点圆边缘，终点在子节点圆边缘
      const startX = parentCenter.x + radius * Math.cos(angle);
      const startY = parentCenter.y + radius * Math.sin(angle);
      const endX = childCenter.x - radius * Math.cos(angle);
      const endY = childCenter.y - radius * Math.sin(angle);

      list.push({
        id: `${node.node_id}-${childNode.node_id}`,
        start: { x: startX, y: startY },
        end: { x: endX, y: endY },
      });
    };

    // 左右子树
    if (node.left) makeEdge(node.left);
    if (node.right) makeEdge(node.right);

    if (node.left) traverse(node.left);
    if (node.right) traverse(node.right);
  };

  traverse(props.root);
  edges.value = list;
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

// 监听 root 变化，动画步骤的每一步都会触发快照更新
watch(() => props.root, () => {
  nextTick(() => scheduleRecompute())
}, { deep: true })
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
