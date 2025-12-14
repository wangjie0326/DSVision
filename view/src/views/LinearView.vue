<template>
  <div class="linear-container" :class="{ 'fade-out': fadeOut }">
    <!-- 返回按钮 -->
    <div class="back-button">
      <button @click="goBack" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        <span>Back</span>
      </button>
    </div>

    <!-- 中央结构类型选择区域 -->
    <div class="structures-wrapper">
      <div class="hero-text">
        <span class="typewriter">{{ displayedText }}<span class="cursor" v-if="showCursor">|</span></span>
      </div>
      <div class="structures">
        <button
          v-for="(structure, index) in structures"
          :key="structure.id"
          @mouseenter="hoveredIndex = index"
          @mouseleave="hoveredIndex = null"
          @click="selectStructure(structure.id)"
          class="structure-button"
          :class="{ 'hovered': hoveredIndex === index }"
        >
          <div class="structure-pill">
            {{ structure.label }}
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const hoveredIndex = ref(null)
const fadeOut = ref(false)
const displayedText = ref('')
const showCursor = ref(true)
const fullText = 'Select one of the following linear structures:'

const structures = [
  { id: 'sequential', label: 'Sequential List' },
  { id: 'linked', label: 'Linked List' },
  { id: 'stack', label: 'Stack' },
  { id: 'queue', label: 'Queue' }
]

const selectStructure = (structureId) => {
  fadeOut.value = true
  setTimeout(() => {
    // 跳转到具体的可视化页面，携带结构类型参数
    router.push(`/linear/${structureId}`)
  }, 800)
}

const goBack = () => {
  fadeOut.value = true
  setTimeout(() => {
    router.push('/category')
  }, 800)
}

// 打字机效果
let typeIndex = 0
const typeNext = () => {
  if (typeIndex <= fullText.length) {
    displayedText.value = fullText.slice(0, typeIndex)
    typeIndex++
    setTimeout(typeNext, 40)
  } else {
    showCursor.value = false
  }
}
typeNext()
</script>

<style scoped>
.linear-container {
  position: fixed;
  inset: 0;
  background-color: white;
  display: flex;
  flex-direction: column;
  transition: opacity 0.8s ease;
  opacity: 1;
}

.linear-container.fade-out {
  opacity: 0;
}

.back-button {
  position: absolute;
  top: 2rem;
  left: 2rem;
  z-index: 10;
}

.btn-back {
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

.btn-back:hover {
  color: black;
}

.structures-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero-text {
  font-family: 'Georgia', serif;
  font-size: 1.7rem;
  margin-bottom: 2.4rem;
  color: #111827;
}

.typewriter {
  white-space: nowrap;
}

.cursor {
  animation: blink 1s step-start infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.structures {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3rem;
}

.structure-button {
  background: transparent;
  border: none;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform: scale(1);
}

.structure-button.hovered {
  transform: scale(1.2);
}

.structure-pill {
  background-color: black;
  color: white;
  padding: 2rem 3rem;
  border-radius: 9999px;
  font-size: 1.25rem;
  font-weight: 500;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
  white-space: nowrap;
}

.structure-button:hover .structure-pill {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .structures {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .structure-pill {
    padding: 1.5rem 2.5rem;
    font-size: 1rem;
  }
}
</style>
