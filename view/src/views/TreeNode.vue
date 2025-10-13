<template>
  <div class="tree-node-container">
    <div class="node-wrapper">
      <!-- 当前节点 -->
      <div
        class="tree-node"
        :class="{
          'highlighted': isHighlighted,
          'leaf-node': !node.left && !node.right,
          'huffman-node': isHuffman
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

      <!-- 子节点容器 -->
      <div v-if="node.left || node.right" class="children-container">
        <!-- 左子树 -->
        <div class="child-wrapper left-child">
          <div v-if="node.left" class="connection-line left-line"></div>
          <TreeNode
            v-if="node.left"
            :node="node.left"
            :highlighted="highlighted"
            :isHuffman="isHuffman"
          />
          <div v-else class="null-node">NULL</div>
        </div>

        <!-- 右子树 -->
        <div class="child-wrapper right-child">
          <div v-if="node.right" class="connection-line right-line"></div>
          <TreeNode
            v-if="node.right"
            :node="node.right"
            :highlighted="highlighted"
            :isHuffman="isHuffman"
          />
          <div v-else class="null-node">NULL</div>
        </div>
      </div>
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
  highlighted: {
    type: Array,
    default: () => []
  },
  isHuffman: {
    type: Boolean,
    default: false
  }
})

const isHighlighted = computed(() => {
  return props.highlighted.includes(props.node.node_id)
})
</script>

<style scoped>
.tree-node-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.node-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
}

/* 节点样式 */
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
  position: relative;
  z-index: 2;
}

.tree-node.highlighted {
  background-color: #ef4444;
  transform: scale(1.2);
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.3), 0 8px 12px -2px rgba(0, 0, 0, 0.2);
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1.2);
  }
  50% {
    transform: scale(1.25);
  }
}

.tree-node.leaf-node {
  background-color: #3b82f6;
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

/* 子节点容器 */
.children-container {
  display: flex;
  gap: 4rem;
  position: relative;
}

.child-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

/* 连接线 */
.connection-line {
  position: absolute;
  top: -3rem;
  width: 2px;
  height: 3rem;
  background-color: #9ca3af;
  z-index: 1;
}

.connection-line::before {
  content: '';
  position: absolute;
  top: 0;
  width: 2rem;
  height: 2px;
  background-color: #9ca3af;
}

.left-line::before {
  left: 0;
  transform-origin: left;
  transform: rotate(-45deg);
}

.right-line::before {
  right: 0;
  transform-origin: right;
  transform: rotate(45deg);
}

/* NULL节点 */
.null-node {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #e5e7eb;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 0.5;
}

/* 响应式调整 */
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

  .children-container {
    gap: 2rem;
  }

  .connection-line::before {
    width: 1.5rem;
  }
}
</style>
