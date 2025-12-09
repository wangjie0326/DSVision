<template>
  <Transition name="settings-dropdown">
    <div v-if="isOpen" class="settings-panel">
      <div class="panel-header">
        <h3>{{ t('settings') }}</h3>
      </div>

      <div class="panel-content">
        <!-- Dark Mode Toggle -->
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-icon">
              <svg v-if="!darkMode" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
            </div>
            <div class="setting-label">
              <span class="label-text">{{ t('darkMode') }}</span>
              <span class="label-desc">{{ darkMode ? t('on') : t('off') }}</span>
            </div>
          </div>
          <button @click="toggleDarkMode" class="toggle-switch" :class="{ active: darkMode }">
            <span class="toggle-slider"></span>
          </button>
        </div>

        <div class="divider"></div>

        <!-- Language Selection -->
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
            </div>
            <div class="setting-label">
              <span class="label-text">{{ t('language') }}</span>
              <span class="label-desc">{{ language === 'en' ? t('english') : t('chinese') }}</span>
            </div>
          </div>
        </div>

        <div class="language-options">
          <button
            @click="setLanguage('en')"
            class="language-btn"
            :class="{ active: language === 'en' }"
          >
            <span class="flag">🇺🇸</span>
            <span>{{ t('english') }}</span>
            <svg v-if="language === 'en'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="check-icon">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </button>
          <button
            @click="setLanguage('zh')"
            class="language-btn"
            :class="{ active: language === 'zh' }"
          >
            <span class="flag">🇨🇳</span>
            <span>{{ t('chinese') }}</span>
            <svg v-if="language === 'zh'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="check-icon">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </button>
        </div>

        <div class="divider"></div>

        <!-- About Section -->
        <div class="setting-item clickable" @click="handleAbout">
          <div class="setting-info">
            <div class="setting-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
            </div>
            <div class="setting-label">
              <span class="label-text">{{ t('about') }}</span>
              <span class="label-desc">{{ t('version') }}</span>
            </div>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="arrow-icon">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { setLanguage as setGlobalLanguage, currentLanguage, useLanguage } from '../stores/language.js'

const { t } = useLanguage()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'update:darkMode', 'update:language'])

// Settings state
const darkMode = ref(localStorage.getItem('darkMode') === 'true' || false)
const language = ref(currentLanguage.value)

// Toggle dark mode
const toggleDarkMode = () => {
  darkMode.value = !darkMode.value
  localStorage.setItem('darkMode', darkMode.value)
  emit('update:darkMode', darkMode.value)

  // Apply dark mode to document
  if (darkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// Set language
const setLanguage = (lang) => {
  language.value = lang
  setGlobalLanguage(lang)
  emit('update:language', lang)

  // Force page refresh to update all translations
  window.location.reload()
}

// About handler
const handleAbout = () => {
  alert('DSVision v1.0.0\n\nA data structure visualization system\nBuilt with Vue 3 + Flask')
}

// Initialize dark mode on component mount
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    // Refresh settings from localStorage when panel opens
    darkMode.value = localStorage.getItem('darkMode') === 'true'
    language.value = currentLanguage.value
  }
}, { immediate: true })
</script>

<style scoped>
.settings-panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 320px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 1rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 100;
}

.panel-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.panel-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.panel-content {
  padding: 0.75rem;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0.5rem;
  border-radius: 0.5rem;
  transition: background 0.2s;
}

.setting-item.clickable {
  cursor: pointer;
}

.setting-item.clickable:hover {
  background: rgba(0, 0, 0, 0.05);
}

.setting-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.setting-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(32, 167, 255, 0.1);
  border-radius: 0.5rem;
  color: #20A7FF;
}

.setting-label {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.label-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}

.label-desc {
  font-size: 0.75rem;
  color: #6b7280;
}

.toggle-switch {
  width: 48px;
  height: 28px;
  background: #d1d5db;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  position: relative;
  transition: background 0.3s;
  flex-shrink: 0;
}

.toggle-switch.active {
  background: #20A7FF;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 24px;
  height: 24px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch.active .toggle-slider {
  transform: translateX(20px);
}

.divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.08);
  margin: 0.5rem 0;
}

.language-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0 0.5rem;
  margin-top: 0.5rem;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.03);
  border: 2px solid transparent;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
}

.language-btn:hover {
  background: rgba(0, 0, 0, 0.06);
}

.language-btn.active {
  background: rgba(32, 167, 255, 0.1);
  border-color: #20A7FF;
  color: #20A7FF;
}

.flag {
  font-size: 1.5rem;
  line-height: 1;
}

.check-icon {
  margin-left: auto;
  color: #20A7FF;
}

.arrow-icon {
  color: #9ca3af;
  flex-shrink: 0;
}

/* Dropdown Animation */
.settings-dropdown-enter-active,
.settings-dropdown-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.settings-dropdown-enter-from,
.settings-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* Dark mode styles (will be applied when dark class is added to html) */
:global(.dark) .settings-panel {
  background: rgba(31, 41, 55, 0.95);
  border-color: rgba(255, 255, 255, 0.1);
}

:global(.dark) .panel-header {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

:global(.dark) .panel-header h3 {
  color: #f9fafb;
}

:global(.dark) .setting-item.clickable:hover {
  background: rgba(255, 255, 255, 0.05);
}

:global(.dark) .label-text {
  color: #f9fafb;
}

:global(.dark) .label-desc {
  color: #9ca3af;
}

:global(.dark) .divider {
  background: rgba(255, 255, 255, 0.1);
}

:global(.dark) .language-btn {
  background: rgba(255, 255, 255, 0.05);
  color: #d1d5db;
}

:global(.dark) .language-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

:global(.dark) .language-btn.active {
  background: rgba(32, 167, 255, 0.2);
  color: #60a5fa;
}

@media (max-width: 768px) {
  .settings-panel {
    width: 280px;
  }
}
</style>
