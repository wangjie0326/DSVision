<template>
  <div class="complexity-indicator">
    <div class="complexity-header">
      <span class="complexity-title">Complexity</span>
    </div>
    <div v-if="currentComplexity" class="complexity-content">
      <div class="complexity-item">
        <span class="complexity-label">Time</span>
        <span class="complexity-value">{{ currentComplexity.time }}</span>
      </div>
      <div class="complexity-item">
        <span class="complexity-label">Space</span>
        <span class="complexity-value">{{ currentComplexity.space }}</span>
      </div>
      <div class="complexity-item total">
        <span class="complexity-label">Total</span>
        <span class="complexity-value">{{ currentComplexity.total }}</span>
      </div>
    </div>
    <div v-else class="complexity-empty">
      Select operation
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  structureType: {
    type: String,
    required: true
  },
  operation: {
    type: String,
    required: true
  }
})

// 所有数据结构的所有操作的复杂度映射
const complexityMap = {
  // 顺序表
  sequential: {
    insert: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    delete: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    search: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    get: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    clear: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    init: { time: 'O(n)', space: 'O(n)', total: 'O(n)' }
  },

  // 链表
  linked: {
    insert: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    insert_head: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    insert_tail: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    delete: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    delete_head: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    delete_tail: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    search: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    get: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    clear: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    init: { time: 'O(n)', space: 'O(n)', total: 'O(n)' }
  },

  // 栈
  stack: {
    push: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    pop: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    peek: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    clear: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    init: { time: 'O(n)', space: 'O(n)', total: 'O(n)' }
  },

  // 队列
  queue: {
    enqueue: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    dequeue: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    front: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    rear: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    clear: { time: 'O(1)', space: 'O(1)', total: 'O(1)' },
    init: { time: 'O(n)', space: 'O(n)', total: 'O(n)' }
  },

  // 二叉树
  binary: {
    insert: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    delete: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    search: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    traverse: { time: 'O(n)', space: 'O(n)', total: 'O(n)' },
    clear: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    build: { time: 'O(n)', space: 'O(n)', total: 'O(n)' }
  },

  // 二叉搜索树
  bst: {
    insert: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    delete: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    search: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    traverse: { time: 'O(n)', space: 'O(n)', total: 'O(n)' },
    min: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    max: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    clear: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    build: { time: 'O(n²)', space: 'O(n)', total: 'O(n²)' }
  },

  // AVL树
  avl: {
    insert: { time: 'O(log n)', space: 'O(1)', total: 'O(log n)' },
    delete: { time: 'O(log n)', space: 'O(1)', total: 'O(log n)' },
    search: { time: 'O(log n)', space: 'O(1)', total: 'O(log n)' },
    traverse: { time: 'O(n)', space: 'O(n)', total: 'O(n)' },
    min: { time: 'O(log n)', space: 'O(1)', total: 'O(log n)' },
    max: { time: 'O(log n)', space: 'O(1)', total: 'O(log n)' },
    clear: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    build: { time: 'O(n log n)', space: 'O(n)', total: 'O(n log n)' }
  },

  // Huffman树
  huffman: {
    build: { time: 'O(n log n)', space: 'O(n)', total: 'O(n log n)' },
    search: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    build_text: { time: 'O(n log n)', space: 'O(n)', total: 'O(n log n)' },
    build_numbers: { time: 'O(n log n)', space: 'O(n)', total: 'O(n log n)' },
    encode: { time: 'O(n)', space: 'O(n)', total: 'O(n)' },
    decode: { time: 'O(n)', space: 'O(n)', total: 'O(n)' },
    show_codes: { time: 'O(n)', space: 'O(1)', total: 'O(n)' },
    clear: { time: 'O(n)', space: 'O(1)', total: 'O(n)' }
  }
}

const currentComplexity = computed(() => {
  if (!props.structureType || !props.operation) {
    return null
  }

  const structureComplexity = complexityMap[props.structureType]
  if (!structureComplexity) {
    return null
  }

  return structureComplexity[props.operation] || null
})
</script>

<style scoped>
.complexity-indicator {
  position: fixed;
  bottom:190px;
  left: 20px;
  background: rgb(248, 236, 171);
  border: 2px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  padding: 10px 14px;
  min-width: 160px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  z-index: 999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  backdrop-filter: blur(8px);
}

.complexity-header {
  margin-bottom: 10px;
  padding-bottom: 7px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.complexity-title {
  font-size: 14px;
  font-weight: 790;
  color: #333d4c;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

.complexity-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.complexity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  gap: 12px;
}

.complexity-item.total {
  margin-top: 3px;
  padding-top: 6px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  font-weight: 600;
}

.complexity-label {
  color: #111d2e;
  font-weight: 700;
  min-width: 38px;
}

.complexity-value {
  color: #b30505;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-weight: 900;
  font-size: 14px;
  letter-spacing: 0.6px;
}

.complexity-empty {
  color: #9ca3af;
  font-size: 10px;
  text-align: center;
  opacity: 0.8;
  padding: 2px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .complexity-indicator {
    left: 10px;
    bottom: 180px;
    min-width: 150px;
    padding: 8px 12px;
  }

  .complexity-title {
    font-size: 10px;
  }

  .complexity-item {
    font-size: 11px;
  }

  .complexity-value {
    font-size: 11px;
  }
}
</style>
