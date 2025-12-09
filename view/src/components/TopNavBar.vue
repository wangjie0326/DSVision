<template>
  <div class="top-nav-bar">
    <!-- Logo -->
    <div class="logo-section">
      <span class="my-logo">DSVision</span>
    </div>

    <!-- Menu Items -->
    <div class="menu-items">
      <button @click="$emit('open-dsl-manual')" class="menu-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>
        <span>{{ t('dslManual') }}</span>
      </button>

      <button @click="$emit('open-llm-guide')" class="menu-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
        <span>{{ t('llmGuide') }}</span>
      </button>

      <a href="https://wangjie0326.github.io" target="_blank" class="menu-btn menu-link">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
        <span>{{ t('aboutAuthor') }}</span>
      </a>

      <!-- 交流 / 反馈 -->
      <div class="feedback-wrapper" ref="feedbackRef">
        <button class="menu-btn" :class="{ active: showFeedback }" @click="toggleFeedback">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span>Feedback</span>
        </button>
        <div v-if="showFeedback" class="feedback-card">
          <div class="feedback-header">
            <div>
              <div class="feedback-title">Tell us your golden ideas</div>
              <div class="feedback-sub">Problems / Suggestions / Ideas</div>
            </div>
            <a
              class="pill"
              href="https://github.com/wangjie0326/DSVision"
              target="_blank"
              rel="noreferrer"
            >Open Source</a>
          </div>
          <textarea
            v-model="feedbackText"
            placeholder="描述你的问题或建议（会通过邮件发送给 wangjie@emails.bjut.edu.cn）"
            rows="4"
          ></textarea>
          <div class="feedback-actions">
            <span class="badge">配置示例: npm install && npm run dev</span>
            <div class="action-buttons">
              <button class="ghost-btn" @click="feedbackText = ''">清空</button>
              <a
                class="send-btn"
                :href="mailtoLink"
                @click="closeFeedback"
              >发送邮件</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Section - Import File & Settings -->
    <div class="right-section">
      <button @click="$emit('import-file')" class="menu-btn import-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <span>{{ t('importFile') }}</span>
      </button>

      <div class="settings-wrapper" ref="settingsRef">
        <button @click="toggleSettings" class="menu-btn settings-btn" :class="{ active: showSettings }">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M12 1v6m0 6v6m5.196-15.804l-4.243 4.243m-2.121 2.121l-4.243 4.243m15.804.536l-4.243-4.243m-2.121-2.121l-4.243-4.243"></path>
          </svg>
        </button>
        <SettingsPanel
          :is-open="showSettings"
          @update:darkMode="handleDarkModeChange"
          @update:language="handleLanguageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import SettingsPanel from './SettingsPanel.vue'
import { useLanguage } from '../stores/language.js'

defineEmits(['open-dsl-manual', 'open-llm-guide', 'import-file'])

const { t } = useLanguage()
const showSettings = ref(false)
const settingsRef = ref(null)
const showFeedback = ref(false)
const feedbackRef = ref(null)
const feedbackText = ref('')

const mailtoLink = computed(() => {
  const subject = encodeURIComponent('DSVision 反馈')
  const body = encodeURIComponent(feedbackText.value || 'Hi, 我有以下反馈：')
  return `mailto:wangjie@emails.bjut.edu.cn?subject=${subject}&body=${body}`
})

const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

const toggleFeedback = () => {
  showFeedback.value = !showFeedback.value
}

const closeFeedback = () => {
  showFeedback.value = false
}

const handleDarkModeChange = (isDark) => {
  console.log('Dark mode changed:', isDark)
}

const handleLanguageChange = (lang) => {
  console.log('Language changed:', lang)
  // You can emit this to parent for global language handling
}

// Close settings when clicking outside
const handleClickOutside = (event) => {
  if (settingsRef.value && !settingsRef.value.contains(event.target)) {
    showSettings.value = false
  }
  if (feedbackRef.value && !feedbackRef.value.contains(event.target)) {
    showFeedback.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)

  // Initialize dark mode on mount
  const isDark = localStorage.getItem('darkMode') === 'true'
  if (isDark) {
    document.documentElement.classList.add('dark')
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.top-nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.logo-section {
  flex-shrink: 0;
}

.my-logo {
  font-family: 'Lato', 'Avenir', 'Helvetica Neue', sans-serif;
  font-weight: 1000;
  font-size: 32px;
  color: #20A7FF;
  letter-spacing: 1px;
  cursor: default;
  user-select: none;
}

.menu-items {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  justify-content: center;
  margin: 0 2rem;
}

.menu-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: #6b7280;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
}

.menu-btn:hover {
  color: #20A7FF;
  background: rgba(32, 167, 255, 0.1);
}

.menu-link {
  text-decoration: none;
}

.feedback-wrapper {
  position: relative;
}

.feedback-card {
  position: absolute;
  top: 110%;
  left: 0;
  width: 360px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.12);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 20;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.feedback-title {
  font-weight: 700;
  color: #0f172a;
}

.feedback-sub {
  font-size: 0.875rem;
  color: #6b7280;
}

.feedback-card textarea {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.75rem;
  resize: vertical;
  font-size: 0.95rem;
  font-family: 'Inter', 'SF Pro', sans-serif;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
}

.feedback-card textarea:focus {
  border-color: #20A7FF;
  box-shadow: 0 0 0 3px rgba(32, 167, 255, 0.15);
}

.feedback-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  background: #f3f4f6;
  color: #111827;
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.ghost-btn {
  border: 1px solid #e5e7eb;
  background: white;
  color: #374151;
  padding: 0.45rem 0.9rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.ghost-btn:hover {
  border-color: #cbd5e1;
}

.send-btn {
  background: linear-gradient(120deg, #20A7FF, #4f46e5);
  color: white;
  text-decoration: none;
  padding: 0.45rem 0.95rem;
  border-radius: 0.75rem;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.send-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.25);
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background: #eef2ff;
  color: #4338ca;
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration: none;
}

.right-section {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.import-btn {
  color: #6b7280;
}

.import-btn:hover {
  color: #374151;
  background: #f3f4f6;
}

.settings-wrapper {
  position: relative;
}

.settings-btn {
  color: #6b7280;
  padding: 0.5rem;
}

.settings-btn:hover,
.settings-btn.active {
  color: #20A7FF;
  background: rgba(32, 167, 255, 0.1);
}

.settings-btn svg {
  transition: transform 0.3s;
}

.settings-btn.active svg {
  transform: rotate(45deg);
}

/* Responsive */
@media (max-width: 768px) {
  .top-nav-bar {
    padding: 0 1rem;
  }

  .my-logo {
    font-size: 24px;
  }

  .menu-items {
    gap: 0.5rem;
    margin: 0 1rem;
  }

  .menu-btn span {
    display: none;
  }

  .menu-btn {
    padding: 0.5rem;
  }
}
</style>
