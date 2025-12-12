<template>
  <div
    v-if="node && position"
    class="tree-node"
    :class="{
      'highlighted': isHighlighted || isSelected,
      'huffman-node': isHuffman,
      'dashed-node': isDashed,
      'preview-node': isPreview,
      'selected': isSelected && !isHighlighted
    }"
    :style="{
      position: 'absolute',
      left: `${position.x}px`,
      top: `${position.y}px`,
      transform: 'translate(-50%, -50%)'
    }"
    @click.stop="selectNode"
  >
    <div class="node-content">
      <!-- 普通节点显示值 -->
      <span v-if="!isHuffman" class="node-value">{{ node.value }}</span>

      <!-- Huffman节点显示值和权重 -->
      <template v-else>
        <span class="node-value huffman-value">{{ node.value }}</span>
        <span class="node-weight">{{ node.weight }}</span>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  position: {
    type: Object,
    required: true
  },
  highlighted: {
    type: Array,
    default: () => []
  },
  isHuffman: {
    type: Boolean,
    default: false
  },
  dashedNodes: {
    type: Array,
    default: () => []
  },
  selectedNodeId: {
    type: Number,
    default: null
  },
  isPreview: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['select-node'])

const isHighlighted = computed(() => {
  const id = props.node?.node_id
  return !!(id && props.highlighted.includes(id))
})

const isSelected = computed(() => {
  const id = props.node?.node_id
  return !!(id && props.selectedNodeId === id)
})

const isDashed = computed(() => {
  const id = props.node?.node_id
  const result = !!(id && props.dashedNodes.includes(id))

  // 🔥 调试输出
  if (result) {
    console.log(`🟢 节点 ${props.node?.value} (ID: ${id}) isDashed=true`)
    console.log('   -> dashedNodes:', props.dashedNodes)
  }

  return result
})

const selectNode = () => {
  if (!props.node?.node_id) return
  emit('select-node', props.node.node_id)
}

</script>

<style>
.tree-node {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #10b981;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.125rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  box-sizing: border-box;  /* 🔥 确保边框包含在尺寸内，保持正圆形 */
  /* 平滑过渡：位置、背景色、边框等所有属性 */
  transition: left 0.8s cubic-bezier(0.4, 0.0, 0.2, 1),
              top 0.8s cubic-bezier(0.4, 0.0, 0.2, 1),
              background-color 0.3s ease,
              border 0.3s ease,
              transform 0.3s ease,
              opacity 0.3s ease;
  z-index: 2;
}

.tree-node.tree-node.dashed-node {
  width: 60px !important;  /* 🔥 强制正方形 */
  height: 60px !important;
  background-color: rgba(144, 238, 144, 0.7) !important;  /* 🔥 浅绿色 */
  border: none !important;  /* 🔥 移除虚线边框 */
  border-radius: 50% !important;  /* 🔥 确保圆形 */
  color: white !important;  /* 🔥 白色文字 */
  opacity: 1 !important;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: dashedPulse 1.2s ease-in-out infinite !important;
  box-shadow: 0 0 0 4px rgba(144, 238, 144, 0.8), 0 0 15px rgba(144, 238, 144, 0.9) !important;
  z-index: 100 !important;
  box-sizing: border-box !important;
}


.tree-node.dashed-node .node-content {
  color: #0c0c0c;  /* 🔥 白色文字 */
}

.tree-node.dashed-node .node-value {
  color: white;  /* 🔥 白色文字 */
  font-weight: 700;
}

.tree-node.highlighted {
  background-color: #ef4444 !important;
  transform: translate(-50%, -50%) scale(1.2) !important;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.3), 0 8px 12px -2px rgba(0, 0, 0, 0.2) !important;
  animation: pulse 1s ease-in-out infinite !important;
  z-index: 200 !important;  /* 🔥 确保高亮节点在虚线节点之上 */
  border: none !important;  /* 🔥 移除虚线边框（如果同时是虚线节点） */
}

.tree-node.selected {
  background-color: #ef4444 !important;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.18), 0 8px 12px -2px rgba(0, 0, 0, 0.15) !important;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1.2);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.25);
  }
}

/* 🔥 虚线节点的脉冲动画 - 极其明显 */
@keyframes dashedPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    border-color: #00DD00;
    background-color: rgba(144, 238, 144, 0.4);
    box-shadow: 0 0 0 8px rgba(144, 238, 144, 0.6), 0 0 20px rgba(144, 238, 144, 0.8);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.25);
    border-color: #00FF00;
    background-color: rgba(144, 238, 144, 0.7);
    box-shadow: 0 0 0 12px rgba(144, 238, 144, 0.8), 0 0 30px rgba(144, 238, 144, 1);
  }
}

@keyframes dashFade {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.8);
  }
  100% {
    opacity: 0.7;
    transform: translate(-50%, -50%) scale(1);
  }
}

/* 🔥 预览节点样式 - 浅绿色半透明 */
.tree-node.preview-node {
  background-color: rgba(144, 238, 144, 0.6);  /* 浅绿色 lightgreen */
  border: 2px dashed #90EE90;
  color: #2d5016;
  box-shadow: 0 0 20px rgba(144, 238, 144, 0.8);
  animation: previewPulse 1s ease-in-out infinite;
}

.tree-node.preview-node .node-content {
  color: #2d5016;
}

.tree-node.preview-node .node-value {
  color: #2d5016;
  font-weight: 700;
}

@keyframes previewPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 0.8;
  }
}

.tree-node.huffman-node {
  width: 80px;
  height: 80px;
  border-radius: 12px;
}

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.node-value {
  font-size: 1.125rem;
  font-weight: 700;
}

.huffman-value {
  font-size: 0.875rem;
  max-width: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-weight {
  font-size: 0.75rem;
  opacity: 0.8;
  font-weight: 500;
}

@media (max-width: 768px) {
  .tree-node {
    width: 50px;
    height: 50px;
    font-size: 1rem;
  }

  .tree-node.huffman-node {
    width: 70px;
    height: 70px;
  }
}
</style>
