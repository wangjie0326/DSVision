<template>
  <div class="tree-node-container":data-node-id="node.node_id">
    <div class="node-wrapper">
      <!-- 当前节点 -->
      <div
        class="tree-node"
        ref="nodeEl"
        :class="{
          'highlighted': isHighlighted,
          'comparing': isComparing,
          'creating': isCreating,
          'leaf-node': !node.left && !node.right,
          'huffman-node': isHuffman
        }"
        @contextmenu.prevent="handleRightClick"
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
        <!-- 新增: 右键菜单 -->
        <div v-if="showContextMenu" class="context-menu" :style="menuPosition">
          <div class="menu-item" @click="insertLeft">插入左节点</div>
          <div class="menu-item" @click="insertRight">插入右节点</div>
          <div class="menu-item danger" @click="deleteNode">删除节点</div>
        </div>
      </div>



      <!-- 子节点容器 -->
      <div v-if="node.left || node.right" class="children-container">
        <!-- 🔥 新增: 方向箭头动画 -->
        <div v-if="showLeftArrow" class="direction-arrow left-arrow">↙️</div>
        <div v-if="showRightArrow" class="direction-arrow right-arrow">↘️</div>
        <!-- 左子树 -->
        <div class="child-wrapper left-child">
          <div v-if="node.left" class="connection-line left-line"></div>
          <TreeNode
            v-if="node.left"
            :node="node.left"
            :highlighted="highlighted"
            :isHuffman="isHuffman"
            :currentAnimation="currentAnimation"
            @insert-left="$emit('insert-left', $event)"
            @insert-right="$emit('insert-right', $event)"
            @delete-node="$emit('delete-node', $event)"
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
            :currentAnimation="currentAnimation"
            @insert-left="$emit('insert-left', $event)"
            @insert-right="$emit('insert-right', $event)"
            @delete-node="$emit('delete-node', $event)"
          />
          <div v-else class="null-node">NULL</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

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
  },
  currentAnimation: {  // 🔥 新增
    type: String,
    default: ''
  }
})

const emit = defineEmits(['insert-left', 'insert-right', 'delete-node'])

const nodeEl = ref(null)

// 注册到上层：发送一个带 node_id 和元素引用的事件
const registerNode = () => {
  // 使用 nextTick 确保 DOM 已定位
  nextTick(() => {
    if (nodeEl.value) {
      emit('register-node', { id: props.node.node_id, el: nodeEl.value })
    }
  })
}
const unregisterNode = () => {
  emit('unregister-node', { id: props.node.node_id })
}

onMounted(() => {
  registerNode()
})

onBeforeUnmount(() => {
  unregisterNode()
})

// 右键菜单状态
const showContextMenu = ref(false)
const menuPosition = ref({ top: '0px', left: '0px' })

const isHighlighted = computed(() => {
  return props.highlighted.includes(props.node.node_id)
})

const isComparing = computed(() => {
  return props.currentAnimation === 'comparing' && isHighlighted.value
})

const isCreating = computed(() => {
  return props.currentAnimation === 'creating' && isHighlighted.value
})

const showLeftArrow = computed(() => {
  return props.currentAnimation === 'arrow_left' && isHighlighted.value
})

const showRightArrow = computed(() => {
  return props.currentAnimation === 'arrow_right' && isHighlighted.value
})

// 🔥 右键菜单处理
const handleRightClick = (event) => {
  showContextMenu.value = true
  menuPosition.value = {
    top: `${event.offsetY}px`,
    left: `${event.offsetX}px`
  }

  // 3秒后自动关闭
  setTimeout(() => {
    showContextMenu.value = false
  }, 3000)
}

const insertLeft = () => {
  emit('insert-left', props.node.node_id)
  showContextMenu.value = false
}

const insertRight = () => {
  emit('insert-right', props.node.node_id)
  showContextMenu.value = false
}

const deleteNode = () => {
  emit('delete-node', props.node.node_id)
  showContextMenu.value = false
}
</script>

<style scoped>
/* 🔥 新增动画效果 */
.tree-node.comparing {
  animation: compareAnimation 0.6s ease-in-out;
}

@keyframes compareAnimation {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.tree-node.creating {
  animation: createAnimation 0.8s ease-out;
}

@keyframes createAnimation {
  0% {
    opacity: 0;
    transform: scale(0) rotate(180deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}

/* 🔥 方向箭头 */
.direction-arrow {
  position: absolute;
  font-size: 2rem;
  z-index: 10;
  animation: arrowBounce 0.5s ease-in-out infinite;
}

.left-arrow {
  left: -40px;
  top: 50%;
}

.right-arrow {
  right: -40px;
  top: 50%;
}

@keyframes arrowBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 🔥 右键菜单 */
.context-menu {
  position: absolute;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 100;
  min-width: 120px;
}

.menu-item {
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  color: #2c3e50;
  font-size: 0.875rem;
}

.menu-item:hover {
  background-color: #f3f4f6;
}

.menu-item.danger {
  color: #ef4444;
}

.menu-item.danger:hover {
  background-color: #fee2e2;
}


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

/* 连接线 - 从父节点边缘到子节点边缘 */
.connection-line {
  position: absolute;
  top: -3rem;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 3rem;
  background-color: #6b7280;
  z-index: 1;
  transition: all 0.3s ease;
}

.connection-line:hover {
  background-color: #3b82f6;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
}

/* 左连接线 - 从父节点左下边缘到左子节点上边缘 */
.left-line {
  position: absolute;
  top: -3.1rem;
  left: 120%;
  transform: translateX(-50%) rotate(30deg);
  transform-origin: top left;
  width: 2px;
  height: 3.3rem;
  background-color: #6b7280;
  z-index: 1;
  transition: all 0.3s ease;

}

.left-line:hover {
  background-color: #3b82f6;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
}

/* 左连接线的三角形箭头 - 指向左子节点 */
.left-line::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 8px solid #6b7280;
  transition: all 0.3s ease;
}

.left-line:hover::after {
  border-top-color: #3b82f6;
}

/* 右连接线 - 从父节点右下边缘到右子节点上边缘 */
.right-line {
  position: absolute;
  top: -3.3rem;
  left: 33%;
  transform: translateX(-50%) rotate(-30deg);
  transform-origin: top right;
  width: 2px;
  height: 3.3rem;
  background-color: #6b7280;
  z-index: 1;
  transition: all 0.3s ease;
}

.right-line:hover {
  background-color: #3b82f6;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
}

/* 右连接线的三角形箭头 - 指向右子节点 */
.right-line::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 8px solid #6b7280;
  transition: all 0.3s ease;
}

.right-line:hover::after {
  border-top-color: #3b82f6;
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

  .left-line::after,
  .right-line::after {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #6b7280;
  }
}
</style>
