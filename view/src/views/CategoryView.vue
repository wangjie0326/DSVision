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

    <!-- ChatGPT风格底部输入栏 -->
    <div class="chat-input-bar">
      <input
        v-model="userInput"
        @keyup.enter="handleSend"
        type="text"
        placeholder="Send an instruction here..."
        class="chat-input"
      />
      <button @click="handleSend" class="send-button">
        <svg xmlns="http://www.w3.org/2000/svg" class="send-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M5 12l14-7-4 7 4 7-14-7z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'

const router = useRouter()
const hoveredIndex = ref(null)
const fadeOut = ref(false)
const userInput = ref('')

const categories = [
  { id: 'linear', label: 'Linear Structure' },
  { id: 'tree', label: 'Tree Structure' }
]

const selectCategory = (categoryId) => {
  fadeOut.value = true
  setTimeout(() => {
    router.push(`/${categoryId}`)
  }, 800)
}

const handleImport = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'

  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    try {
      const text = await file.text()
      const data = JSON.parse(text)
      const response = await api.importStructure(data)

      if (response.success) {
        alert('导入成功！')
        const category = data.category || 'linear'
        if (category === 'linear') {
          router.push(`/linear/${response.type}`)
        } else {
          router.push(`/tree/${response.type}`)
        }
      }
    } catch (error) {
      console.error('导入失败:', error)
      alert('导入失败: ' + (error.response?.data?.error || error.message))
    }
  }

  input.click()
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

/* ChatGPT风格底部输入栏 */
.chat-input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  gap: 0.5rem;
}

.chat-input {
  flex: 1;
  padding: 1rem 1rem;
  border-radius: 1.5rem;
  border: 1px solid #d1d5db;
  outline: none;
  font-size: 1rem;
  background-color: white;
}

.chat-input:focus {
  border-color: black;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

.send-button {
  background: black;
  color: white;
  border: none;
  border-radius: 50%;
  width: 3.5rem;
  height: 3.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.send-button:hover {
  background: black;
}

.send-icon {
  width: 1.25rem;
  height: 1.25rem;
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
}
</style>
