<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <transition :name="transitionName" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const transitionName = ref('fade')

watch(() => router.currentRoute.value, (to, from) => {
  if (to.meta.transitionName) {
    transitionName.value = to.meta.transitionName
  } else {
    transitionName.value = 'fade'
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  overflow: hidden;
  transition: background-color 0.3s ease, color 0.3s ease;
}

#app {
  width: 100vw;
  height: 100vh;
  background-color: white;
  transition: background-color 0.3s ease;
}

/* Dark mode styles */
.dark body {
  background-color: #111827;
  color: #f9fafb;
}

.dark #app {
  background-color: #111827;
}

.dark .top-nav-bar {
  background: rgba(31, 41, 55, 0.95) !important;
  border-bottom-color: rgba(255, 255, 255, 0.1) !important;
}

.dark .my-logo {
  color: #60a5fa !important;
}

.dark .menu-btn {
  color: #d1d5db !important;
}

.dark .menu-btn:hover {
  color: #60a5fa !important;
  background: rgba(96, 165, 250, 0.1) !important;
}

.dark .category-container {
  background-color: #111827 !important;
}

.dark .choose-text {
  color: #f9fafb !important;
}

.dark .cursor {
  background-color: #f9fafb !important;
}

.dark .category-pill {
  background-color: #1f2937 !important;
  color: #f9fafb !important;
}

.dark .input-section {
  background: #1f2937 !important;
  border-top-color: rgba(255, 255, 255, 0.1) !important;
}

.dark .mode-button {
  background: #374151 !important;
  border-color: #4b5563 !important;
  color: #d1d5db !important;
}

.dark .mode-button.active {
  background: #60a5fa !important;
  color: white !important;
}

.dark .chat-input,
.dark .dsl-input {
  background-color: #374151 !important;
  border-color: #4b5563 !important;
  color: #f9fafb !important;
}

.dark .chat-input::placeholder,
.dark .dsl-input::placeholder {
  color: #9ca3af !important;
}

.dark .send-button {
  background: #60a5fa !important;
}

.dark .send-button:hover:not(:disabled) {
  background: #3b82f6 !important;
}

.dark .example-btn {
  background: #374151 !important;
  border-color: #4b5563 !important;
  color: #d1d5db !important;
}

.dark .example-btn:hover {
  background: #4b5563 !important;
  border-color: #6b7280 !important;
}

/* Dark mode for modals */
.dark .modal-overlay {
  background: rgba(0, 0, 0, 0.7) !important;
}

.dark .modal-content {
  background: #1f2937 !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.dark .modal-header {
  border-bottom-color: rgba(255, 255, 255, 0.1) !important;
}

.dark .modal-header h2,
.dark .modal-header h3 {
  color: #f9fafb !important;
}

.dark .subtitle {
  color: #9ca3af !important;
}

.dark .close-btn {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #d1d5db !important;
}

.dark .close-btn:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #f9fafb !important;
}

.dark .guide-content {
  color: #d1d5db !important;
}

.dark .guide-section h3 {
  color: #f9fafb !important;
}

.dark .guide-section p {
  color: #d1d5db !important;
}

.dark .example-card {
  background: #374151 !important;
  border-color: #4b5563 !important;
}

.dark .example-card h4 {
  color: #f9fafb !important;
}

.dark .example-card li {
  color: #d1d5db !important;
}

.dark .tips-list li {
  color: #d1d5db !important;
}

.dark .note-section {
  background: rgba(59, 130, 246, 0.1) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
}

.dark .note-section h3,
.dark .note-section p {
  color: #93c5fd !important;
}

.dark .workflow-diagram {
  background: #374151 !important;
}

.dark .step-text {
  color: #d1d5db !important;
}

.dark .operation-category h5 {
  color: #f9fafb !important;
}

.dark .comparison-card.good {
  background: rgba(34, 197, 94, 0.1) !important;
  border-color: rgba(34, 197, 94, 0.3) !important;
}

.dark .comparison-card.bad {
  background: rgba(239, 68, 68, 0.1) !important;
  border-color: rgba(239, 68, 68, 0.3) !important;
}

.dark .comparison-card p {
  color: #f9fafb !important;
}

.dark .comparison-card small {
  color: #9ca3af !important;
}

.dark .faq-item {
  background: #374151 !important;
  border-left-color: #60a5fa !important;
}

.dark .faq-item h5 {
  color: #f9fafb !important;
}

.dark .faq-item p {
  color: #d1d5db !important;
}

.dark .comparison-section {
  background: #374151 !important;
}

.dark .vs-card {
  background: #1f2937 !important;
  border-color: #4b5563 !important;
}

.dark .vs-card h5 {
  color: #f9fafb !important;
  border-bottom-color: #60a5fa !important;
}

.dark .vs-card li {
  color: #d1d5db !important;
}

.dark .pdf-placeholder {
  color: #6b7280 !important;
}

.dark .pdf-placeholder .hint {
  color: #4b5563 !important;
}

/* Dark mode scrollbar */
.dark ::-webkit-scrollbar-track {
  background: #1f2937 !important;
}

.dark ::-webkit-scrollbar-thumb {
  background: #4b5563 !important;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #6b7280 !important;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.5s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}

.tree-node.dashed-node {
  all: unset;
  background-color: rgba(144, 238, 144, 0.5) !important;
  border: 4px dashed #00DD00 !important;
  color: #003300 !important;
  animation: dashedPulse 1.2s ease-in-out infinite !important;
  z-index: 100 !important;
}
</style>
