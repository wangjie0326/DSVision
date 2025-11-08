<template>
  <div class="category-container" :class="{ 'fade-out': fadeOut }">
    <!-- 顶部导入按钮 -->
    <div class="import-button">
      <button @click="handleImport" class="btn-import">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <span>Import History Files</span>
      </button>
    </div>

    <!-- 中央选择区域 -->
    <div class="categories-wrapper">
      <div class="categories">
        <div class="choose-text">Hi! You can choose structure first.</div>
        <div class="choose-text">Or you can also use DSL or LLM to explore!</div>
        <div class="category-buttons">
          <button
            v-for="(category, index) in categories"
            :key="category.id"
            @mouseenter="hoveredIndex = index"
            @mouseleave="hoveredIndex = null"
            @click="selectCategory(category.id)"
            class="category-button"
            :class="{ 'hovered': hoveredIndex === index }"
          >
            <div class="category-pill">
              {{ category.label }}
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- DSL/LLM 模式选择 + 输入框 -->
    <div class="input-section">
      <!-- 模式选择按钮 -->
      <div class="mode-selector">
        <button
          @click="currentMode = 'dsl'"
          class="mode-button"
          :class="{ active: currentMode === 'dsl' }"
        >
          <span>DSL Coding</span>
        </button>
        <button
          @click="currentMode = 'llm'"
          class="mode-button"
          :class="{ active: currentMode === 'llm' }"
        >
          <span>LLM</span>
        </button>
      </div>



    <!-- 输入框 -->
      <div class="chat-input-bar">
        <textarea
          v-if="currentMode === 'dsl'"
          v-model="dslInput"
          @keydown.ctrl.enter="handleExecute"
          placeholder="Enter DSL code here... (Ctrl+Enter to execute)
Example:
Sequential myList {
    init [1, 2, 3, 4, 5]
    insert 10 at 2
}"
          class="dsl-input"
          rows="4"
        />
        <input
          v-else
          v-model="llmInput"
          @keyup.enter="handleExecute"
          type="text"
          placeholder="Send a natural language instruction here..."
          class="chat-input"
        />
        <button @click="handleExecute" class="send-button" :disabled="!canExecute">
          <svg xmlns="http://www.w3.org/2000/svg" class="send-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12l14-7-4 7 4 7-14-7z" />
          </svg>
        </button>
      </div>

      <!-- 🔥 DSL 模式下显示示例按钮 -->
      <div v-if="currentMode === 'dsl'" class="examples-row">
        <span class="examples-label">Quick Examples:</span>
        <button
          v-for="example in exampleButtons"
          :key="example.type"
          @click="loadExample(example.type)"
          class="example-btn"
        >
          {{ example.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref,computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'

const router = useRouter()
const hoveredIndex = ref(null)
const fadeOut = ref(false)
const userInput = ref('')

const currentMode = ref('dsl')  // 'dsl' 或 'llm'
const dslInput = ref('')
const llmInput = ref('')

const categories = [
  { id: 'linear', label: 'Linear Structure' },
  { id: 'tree', label: 'Tree Structure' }
]

const exampleButtons = [
  { type: 'sequential', label: 'Sequential' },
  { type: 'linked', label: 'Linked' },
  { type: 'stack', label: 'Stack' },
  { type: 'bst', label: 'BST' },
  { type: 'huffman', label: 'Huffman' }
]

const canExecute = computed(() => {
  if (currentMode.value === 'dsl') {
    return dslInput.value.trim().length > 0
  }
  return llmInput.value.trim().length > 0
})

const selectCategory = (categoryId) => {
  fadeOut.value = true
  setTimeout(() => {
    router.push(`/${categoryId}`)
  }, 800)
}

const handleImport = async () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'

  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    try {
      const text = await file.text()
      const data = JSON.parse(text)
      //调用后段api
      const response = await api.importStructure(data)

      if (response.success) {
        alert('导入成功！')
        const category = data.category || 'linear'
        const structureType = data.structure_type

        //带上 structure_id，这样可以直接加载已有数据
        if (category === 'linear') {
          //映射结构类型名称
          const typeMap = {
            'SequentialList': 'sequential',
            'LinearLinkedList': 'linked',
            'SequentialStack': 'stack'
          }
          const route = typeMap[structureType] || 'sequential'
          router.push({
            path: `/linear/${route}`,
            query: { importId: response.structure_id }
          })
        } else if(category === 'tree') {
          const typeMap = {
            'BinaryTree': 'binary',
            'BinarySearchTree': 'bst',
            'AVLTree': 'avl',
            'HuffmanTree': 'huffman'
          }
          const route = typeMap[structureType] || 'binary'

          router.push({
            path: `/tree/${route}`,
            query: { importId: response.structure_id }
          })
        }
      }
    } catch (error) {
      console.error('导入失败:', error)
      alert('导入失败: ' + (error.response?.data?.error || error.message))
    }
  }

  input.click()
}

// 执行 DSL 或 LLM
const handleExecute = async () => {
  if (!canExecute.value) return

  if (currentMode.value === 'dsl') {
    await executeDSL()
  } else {
    await executeLLM()
  }
}
// 执行 DSL 代码
const executeDSL = async () => {
  try {
    console.log('执行 DSL 代码:', dslInput.value)

    const response = await fetch('/api/dsl/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: dslInput.value })
    })

    const result = await response.json()

    if (!response.ok) {
      alert(`DSL 错误: ${result.error}`)
      return
    }

    console.log('✓ DSL 执行成功:', result)

    // 跳转到对应的可视化页面
    if (result.structures && result.structures.length > 0) {
      const firstStruct = result.structures[0]
      const category = firstStruct.category  // 'linear' 或 'tree'
      const type = firstStruct.type
      const structureId = firstStruct.structure_id

      // 跳转并携带 structure_id
      if (category === 'linear') {
        router.push({
          path: `/linear/${type}`,
          query: { importId: structureId, fromDSL: 'true' }
        })
      } else {
        router.push({
          path: `/tree/${type}`,
          query: { importId: structureId, fromDSL: 'true' }
        })
      }
    }
  } catch (error) {
    console.error('DSL 执行失败:', error)
    alert('执行失败: ' + error.message)
  }
}

// 🔥 执行 LLM (暂时提示未实现)
const executeLLM = async () => {
  alert('LLM 功能正在开发中...\n\n您输入的指令: ' + llmInput.value)
  llmInput.value = ''
}

// 加载示例代码 //?
const loadExample = async (exampleType) => {
  try {
    const response = await fetch('/api/dsl/examples')
    const data = await response.json()

    if (data.examples && data.examples[exampleType]) {
      dslInput.value = data.examples[exampleType]
    }
  } catch (error) {
    console.error('加载示例失败:', error)
  }
}
const handleSend = () => {
  if (!userInput.value.trim()) return
  console.log('用户输入:', userInput.value)
  userInput.value = ''
}
</script>

<style scoped>
.category-container {
  position: fixed;
  inset: 0;
  background-color: white;
  display: flex;
  flex-direction: column;
  transition: opacity 0.8s ease;
  opacity: 1;
}

.category-container.fade-out {
  opacity: 0;
}

.import-button {
  position: absolute;
  top: 2rem;
  right: 2rem;
  z-index: 10;
}

.btn-import {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #6b7280;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-import:hover {
  color: black;
}

/* 中心内容 */
.categories-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.categories {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.choose-text {
  font-size: 2.0rem;
  font-weight: 500;
  font-family: Georgia,'Times New Roman',Times, serif;
  color: black;
  margin-bottom: 1rem;
}

.category-buttons {
  display: flex;
  gap: 4rem;
}

.category-button {
  background: transparent;
  border: none;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform: scale(1);
}

.category-button.hovered {
  transform: scale(1.3);
}

.category-pill {
  background-color: black;
  color: white;
  padding: 2rem 4rem;
  border-radius: 9999px;
  font-size: 1.5rem;
  font-weight: 500;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.category-button:hover .category-pill {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}

/* 底部输入区域 */
.input-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  padding: 0rem 0 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

/* 模式选择器 */
.mode-selector {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
  position: absolute;
  top: -2.46rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.mode-button {
  padding: 0.4rem 1.5rem;
  border-radius: 9999px;
  border: 2px solid #b3b3b3;
  background: white;
  color: #555555;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-button.active {
  background: #8a8a8a;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.mode-button:hover:not(.active) {
  background: #f3f4f6;
}


/* ChatGPT风格底部输入栏 */
.chat-input-bar {
  width: 100%;
  position: relative;
  bottom: 0;
  left: 0;
  right: 0;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: flex-end;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
}

.chat-input,
.dsl-input{
  flex: 1;
  width: 100%;
  padding: 1rem 1rem;
  border-radius: 1.5rem;
  border: 1px solid #d1d5db;
  outline: none;
  font-size: 1rem;
  background-color: white;
  font-family: 'Consolas', 'Monaco', monospace;
  resize: vertical;
  transition: all 0.1s;
}
.chat-input {
  min-height: 48px;
}

.dsl-input {
  min-height: 100px;
  line-height: 1.6;
}
.chat-input:focus,
.dsl-input:focus{
  border-color: black;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
}

.send-button {
  background: black;
  color: white;
  border: none;
  border-radius: 50%;
  width: 3.25rem;
  height: 3.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #374151;
  transform: scale(1.05);
}

.send-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  opacity: 0.5;
}

.send-icon {
  width: 1.25rem;
  height: 1.25rem;
}
/* 🔥 示例按钮行 */
.examples-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 0.25rem;
}

.examples-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.example-btn {
  padding: 0.4rem 1rem;
  border-radius: 1rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.example-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

@media (max-width: 768px) {
  .category-buttons {
    flex-direction: column;
    gap: 2rem;
  }

  .category-pill {
    padding: 1.5rem 3rem;
    font-size: 1.25rem;
  }
  .mode-selector {
    flex-direction: row;
    top: -2rem;
  }

  .examples-row {
    flex-direction: column;
    align-items: stretch;
  }
  .chat-input-bar {
    width: 95%;
    padding: 0.75rem;
  }

}
</style>
