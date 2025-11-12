<template>
  <div
    v-if="node && position"
    class="tree-node"
    :class="{
      'highlighted': isHighlighted,
      'huffman-node': isHuffman,
      'dashed-node': isDashed
    }"
    :style="{
      position: 'absolute',
      left: `${position.x}px`,
      top: `${position.y}px`,
      transform: 'translate(-50%, -50%)'
    }"
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
  }
})

const isHighlighted = computed(() => {
  return props.highlighted.includes(props.node?.node_id)
})

const isDashed = computed(() => {
  return props.dashedNodes.includes(props.node?.node_id)
})
</script>

<style scoped>
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
  transition: all 0.3s ease;
  z-index: 2;
}

.tree-node.dashed-node {
  background-color: transparent;
  border: 2px dashed #10b981;
  color: #10b981;
  opacity: 0.7;
  animation: dashFade 1s ease-in-out;
}

.tree-node.dashed-node .node-content {
  color: #10b981;
}

.tree-node.dashed-node .node-value {
  color: #10b981;
}

.tree-node.highlighted {
  background-color: #ef4444;
  transform: translate(-50%, -50%) scale(1.2);
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.3), 0 8px 12px -2px rgba(0, 0, 0, 0.2);
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1.2);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.25);
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
