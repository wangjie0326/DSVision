<template>
  <div class="category-container" :class="{ 'fade-out': fadeOut }">
    <!-- Top Navigation Bar -->
    <TopNavBar
      @open-dsl-manual="showDSLManual = true"
      @open-llm-guide="showLLMGuide = true"
      @import-file="handleImport"
    />

    <!-- DSL Guide Modal -->
    <DSLGuideModal
      :is-open="showDSLManual"
      @close="showDSLManual = false"
    />

    <!-- LLM Guide Modal -->
    <LLMGuideModal
      :is-open="showLLMGuide"
      @close="showLLMGuide = false"
    />

    <!-- 中央选择区域 -->
    <div class="categories-wrapper">
      <div class="categories" :class="{ 'hero-exit': heroExit }">
        <div class="choose-text">{{ displayedText1 }}<span class="cursor" v-if="showCursor1">|</span></div>
        <div class="choose-text">{{ displayedText2 }}<span class="cursor" v-if="showCursor2">|</span></div>
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

      <!-- LLM 推理舞台 -->
      <div v-if="llmShowcase" class="llm-visualizer">
        <div class="llm-label">
          <span class="glow-dot"></span>
          LLM ChatGPT 4o
        </div>
        <div class="llm-panels">
          <div class="panel glass">
            <div class="panel-title">Reasoning</div>
            <div class="typing-line" :class="{ active: llmStage === 'reasoning' || llmStage === 'dsl' }">
              <pre>{{ llmReasoning }}</pre>
              <span class="caret" v-if="llmStage === 'reasoning'"></span>
            </div>
          </div>
          <div class="panel code">
            <div class="panel-title">DSL</div>
            <div class="typing-block" :class="{ active: llmStage === 'dsl' || llmStage === 'complete' }">
              <pre>{{ llmDSL }}</pre>
              <span class="caret" v-if="llmStage === 'dsl'"></span>
            </div>
          </div>
        </div>
        <div class="stage-footer" v-if="llmStage === 'complete'">
          <span class="pill success">Ready · 跳转中</span>
        </div>
        <div class="cloud-wrapper" v-if="llmStage === 'reject'">
          <div class="cloud-bubble">
            {{ cloudMessage }}
          </div>
        </div>
      </div>
    </div>

    <!-- DSL/LLM 模式选择 + 输入框 -->
    <div class="input-section">
      <div class="input-header">
        <!-- 模式选择按钮 -->
        <div class="mode-selector">
          <button
            @click="currentMode = 'dsl'"
            class="mode-button"
            :class="{ active: currentMode === 'dsl' }"
          >
            <span>{{ t('dslCoding') }}</span>
          </button>
          <button
            @click="currentMode = 'llm'"
            class="mode-button"
            :class="{ active: currentMode === 'llm' }"
          >
            <span>{{ t('llm') }}</span>
          </button>
        </div>

        <!-- 🔥 DSL 模式下显示示例按钮 -->
        <div v-if="currentMode === 'dsl'" class="examples-row header-examples">
          <span class="examples-label">{{ t('quickExamples') }}</span>
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

      <!-- 输入框 -->
      <div class="chat-input-bar">
        <textarea
          v-if="currentMode === 'dsl'"
          v-model="dslInput"
          @keydown.ctrl.enter="handleExecute"
          :placeholder="t('dslPlaceholder')"
          class="dsl-input"
          rows="1"
        />
        <template v-else>
          <input
            v-model="llmInput"
            @keyup.enter="handleExecute"
            type="text"
            :placeholder="t('llmPlaceholder')"
            class="chat-input"
          />
          <button
            type="button"
            @click="handleVoiceInput"
            class="send-button voice-button"
            :class="{ listening: isListening }"
            :aria-pressed="isListening"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="send-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 1a3 3 0 00-3 3v7a3 3 0 006 0V4a3 3 0 00-3-3z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10v1a7 7 0 0014 0v-1M12 21v-3" />
            </svg>
          </button>
        </template>
        <button @click="handleExecute" class="send-button" :disabled="!canExecute || (currentMode === 'llm' && isAnimating)">
          <svg xmlns="http://www.w3.org/2000/svg" class="send-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12l14-7-4 7 4 7-14-7z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api.js'
import TopNavBar from '../components/TopNavBar.vue'
import LLMGuideModal from '../components/LLMGuideModal.vue'
import DSLGuideModal from '../components/DSLGuideModal.vue'
import { useLanguage } from '../stores/language.js'

const { t } = useLanguage()

const router = useRouter()
const hoveredIndex = ref(null)
const fadeOut = ref(false)
const userInput = ref('')
const heroExit = ref(false)

const currentMode = ref('dsl')  // 'dsl' 或 'llm'
const dslInput = ref('')
const llmInput = ref('')
const llmShowcase = ref(false)
const llmStage = ref('idle') // idle | reasoning | dsl | complete | reject
const llmReasoning = ref('')
const llmDSL = ref('')
const cloudMessage = ref('')
const isAnimating = ref(false)
const isListening = ref(false)
let recognitionInstance = null
let pendingTranscript = ''

// Modal states
const showDSLManual = ref(false)
const showLLMGuide = ref(false)

// 🔥 打字机动画相关
const fullText1 = t('chooseStructure')
const fullText2 = t('useDSLorLLM')
const displayedText1 = ref('')
const displayedText2 = ref('')
const showCursor1 = ref(true)
const showCursor2 = ref(false)

const categories = computed(() => [
  { id: 'linear', label: t('linearStructure') },
  { id: 'tree', label: t('treeStructure') }
])

const exampleButtons = computed(() => [
  { type: 'sequential', label: t('sequential') },
  { type: 'linked', label: t('linked') },
  { type: 'stack', label: t('stack') },
  { type: 'bst', label: t('bst') },
  { type: 'huffman', label: t('huffman') }
])

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

const handleVoiceInput = () => {
  if (currentMode.value !== 'llm') return

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    console.warn('Speech recognition not supported in this browser.')
    return
  }

  // Toggle off if already listening
  if (isListening.value && recognitionInstance) {
    recognitionInstance.stop()
    return
  }

  pendingTranscript = ''
  recognitionInstance = new SpeechRecognition()
  recognitionInstance.lang = 'zh-CN'
  recognitionInstance.interimResults = false
  recognitionInstance.maxAlternatives = 1
  recognitionInstance.continuous = false

  isListening.value = true

  recognitionInstance.onresult = (event) => {
    const lastResult = event.results[event.results.length - 1]
    const transcript = lastResult?.[0]?.transcript || ''
    pendingTranscript = transcript
    if (lastResult?.isFinal && transcript.trim()) {
      llmInput.value = transcript
    }
  }

  recognitionInstance.onerror = () => {
    isListening.value = false
    recognitionInstance = null
    pendingTranscript = ''
  }

  recognitionInstance.onend = () => {
    isListening.value = false
    if (pendingTranscript.trim()) {
      llmInput.value = pendingTranscript
    }
    recognitionInstance = null
    pendingTranscript = ''
  }

  recognitionInstance.start()
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

// 🔥 执行 LLM - 自然语言转DSL并执行
const executeLLM = async () => {
  if (isAnimating.value) return
  try {
    isAnimating.value = true
    heroExit.value = true
    llmShowcase.value = true
    llmStage.value = 'reasoning'
    llmReasoning.value = '模型推理中...'
    llmDSL.value = ''
    cloudMessage.value = ''

    console.log('执行 LLM 推理:', llmInput.value)

    const response = await api.llmChat(llmInput.value)

    console.log('✅ LLM 推理成功:', response)
    console.log('🔍 LLM 执行结果:', response.execution)

    if (!response.success) {
      cloudMessage.value = response.error || '无法生成 DSL 代码'
      llmStage.value = 'reject'
      return
    }

    const llmResponse = response.llm_response
    const dslCode = llmResponse.dsl_code || ''
    const explanation = llmResponse.explanation || ''

    // 无关问题或拒绝场景：展示云朵对话
    if (!dslCode.trim()) {
      cloudMessage.value = explanation || '我是DSVion,只能帮你学习数据结构操作。你可以想创建或操作的数据结构。☺'
      llmStage.value = 'reject'
      return
    }

    llmReasoning.value = ''
    await typeWriter(explanation, llmReasoning, 18)
    llmStage.value = 'dsl'
    await typeWriter(dslCode, llmDSL, 12)
    llmStage.value = 'complete'

    // 优先使用后端执行结果跳转
    if (response.execution?.success && response.execution?.structures?.length > 0) {
      const firstStruct = response.execution.structures[0]
      navigateToStruct(firstStruct.category, firstStruct.type, firstStruct.structure_id)
    } else {
      // 兜底：解析 DSL 首个结构类型推断跳转
      const parsed = deriveRouteFromDSL(dslCode)
      if (parsed) {
        navigateToStruct(parsed.category, parsed.type)
      }
    }

    llmInput.value = ''
  } catch (error) {
    console.error('❌ LLM 推理失败:', error)
    cloudMessage.value = error.response?.data?.error || error.message || '推理失败'
    llmStage.value = 'reject'
  } finally {
    isAnimating.value = false
  }
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

// 🔥 打字机动画函数
const typeWriter = async (text, displayRef, speed = 130) => {
  for (let i = 0; i <= text.length; i++) {
    displayRef.value = text.substring(0, i)
    await new Promise(resolve => setTimeout(resolve, speed))
  }
}

const deriveRouteFromDSL = (code) => {
  if (!code) return null
  const match = code.match(/\b(Sequential|Linked|Stack|Queue|Binary|BST|AVL|Huffman)\b/i)
  if (!match) return null
  const mapping = {
    sequential: { category: 'linear', type: 'sequential' },
    linked: { category: 'linear', type: 'linked' },
    stack: { category: 'linear', type: 'stack' },
    queue: { category: 'linear', type: 'queue' },
    binary: { category: 'tree', type: 'binary' },
    bst: { category: 'tree', type: 'bst' },
    avl: { category: 'tree', type: 'avl' },
    huffman: { category: 'tree', type: 'huffman' }
  }
  return mapping[match[1].toLowerCase()] || null
}

const navigateToStruct = (category, type, structureId = null) => {
  if (!category || !type) return
  console.log('📊 跳转信息:', { category, type, structureId })
  setTimeout(() => {
    const routeBase = category === 'linear' ? '/linear' : '/tree'
    const query = structureId ? { importId: structureId, fromDSL: 'true' } : {}
    router.push({
      path: `${routeBase}/${type}`,
      query
    })
  }, 900)
}

// 组件挂载时启动打字机动画
onMounted(async () => {
  // 延迟 500ms 后开始第一行
  await new Promise(resolve => setTimeout(resolve, 500))
  showCursor1.value = true
  await typeWriter(fullText1, displayedText1, 40)// 打字速度（
  showCursor1.value = false

  // 第一行打完后，延迟 300ms 再开始第二行
  await new Promise(resolve => setTimeout(resolve, 100))
  showCursor2.value = true
  await typeWriter(fullText2, displayedText2, 40)// 打字速度（
  showCursor2.value = false
})
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

/* 中心内容 */
.categories-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 64px; /* Account for fixed nav bar */
  position: relative;
}

.categories {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  transition: transform 0.9s cubic-bezier(0.19, 1, 0.22, 1), opacity 0.8s ease;
}

.choose-text {
  font-size: 2.0rem;
  font-weight: 500;
  font-family: Georgia,'Times New Roman',Times, serif;
  color: black;
  margin-bottom: 1rem;
  min-height: 3rem; /* 保持高度稳定 */
}

.hero-exit {
  transform: translateY(-120px);
  opacity: 0;
  filter: blur(2px);
}

/* 🔥 打字机光标动画 */
.cursor {
  display: inline-block;
  width: 2px;
  height: 1.8rem;
  background-color: black;
  margin-left: 2px;
  animation: blink 1s infinite;
  vertical-align: middle;
}

@keyframes blink {
  0%, 49% {
    opacity: 1;
  }
  50%, 100% {
    opacity: 0;
  }
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
  background: transparent;
  border-top: 1px solid #e5e7eb;
  padding: 0 0 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  overflow: visible;
}

.input-header {
  position: absolute;
  bottom: calc(100% + 0.4rem);
  left: 1rem;
  right: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* 模式选择器 */
.mode-selector {
  display: flex;
  justify-content: flex-start;
  gap: 0.75rem;
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
  align-items: center;
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
  resize: none;
  transition: all 0.1s;
  box-sizing: border-box;
}
.chat-input {
  height: 48px;
}

.dsl-input {
  height: 48px;
  line-height: 1.4;
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

.voice-button.listening {
  background: #1f2937;
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
  justify-content: flex-end;
  flex-wrap: wrap;
}

.header-examples {
  margin-left: auto;
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

.llm-visualizer {
  position: absolute;
  inset: 12% 8% auto 8%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: linear-gradient(145deg, rgba(255,255,255,0.92), rgba(233,240,255,0.96));
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 24px;
  padding: 1.5rem;
  box-shadow: 0 20px 50px rgba(0,0,0,0.08);
  z-index: 2;
}

.llm-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #0f172a;
  text-transform: uppercase;
  font-size: 0.9rem;
}

.glow-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #a5b4fc, #4338ca);
  box-shadow: 0 0 12px rgba(67, 56, 202, 0.7);
}

.llm-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.panel {
  position: relative;
  border-radius: 18px;
  padding: 1rem 1.2rem 1.4rem;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.05);
  min-height: 180px;
}

.panel-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #1f2937;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.75rem;
}

.panel.glass {
  background: linear-gradient(160deg, rgba(255,255,255,0.95), rgba(236,242,255,0.85));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}

.panel.code {
  background: #0b1021;
  color: #e2e8f0;
  border: 1px solid #1f2937;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.typing-line pre,
.typing-block pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'JetBrains Mono', 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
  font-size: 0.95rem;
  line-height: 1.6;
}

.typing-line {
  color: #111827;
}

.typing-block {
  background: rgba(255,255,255,0.02);
  border: 1px dashed rgba(255,255,255,0.08);
  padding: 0.75rem;
  border-radius: 12px;
  min-height: 140px;
}

.typing-line.active,
.typing-block.active {
  animation: breathe 1.6s ease-in-out infinite;
}

.caret {
  display: inline-block;
  width: 10px;
  height: 18px;
  background: currentColor;
  margin-left: 4px;
  animation: blink 1s infinite;
  vertical-align: bottom;
}

.stage-footer {
  display: flex;
  justify-content: flex-end;
}

.pill {
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.pill.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.cloud-wrapper {
  position: absolute;
  right: 6%;
  bottom: -12px;
  display: flex;
  justify-content: flex-end;
  pointer-events: none;
}

.cloud-bubble {
  background: white;
  border-radius: 30px;
  padding: 0.9rem 1.2rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.12);
  border: 1px solid rgba(0,0,0,0.04);
  font-weight: 600;
  color: #0f172a;
  animation: floatUp 2.2s ease-out forwards;
}

@keyframes breathe {
  0% { box-shadow: 0 0 0 0 rgba(67,56,202,0.08); }
  50% { box-shadow: 0 0 0 8px rgba(67,56,202,0.0); }
  100% { box-shadow: 0 0 0 0 rgba(67,56,202,0.0); }
}

@keyframes floatUp {
  0% { transform: translateY(0) scale(0.96); opacity: 0; }
  20% { opacity: 1; }
  100% { transform: translateY(-70px) scale(1); opacity: 1; }
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
  .llm-visualizer {
    position: relative;
    inset: unset;
    width: 92%;
    margin-top: 1rem;
  }
  .llm-panels {
    grid-template-columns: 1fr;
  }
}
</style>
