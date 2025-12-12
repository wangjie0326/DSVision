<template>
  <Transition name="modal">
    <div v-if="isOpen" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="closeModal">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div class="modal-header">
          <h2>DSL Quick Guide</h2>
          <p class="subtitle">声明结构 · 执行操作 · 生成动画</p>
        </div>

        <div class="guide-content">
          <section class="guide-section">
          <h3>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 20h16V4H4z"></path>
              <path d="M9 4v16"></path>
            </svg>
            Structure Declaration
          </h3>
          <div class="chips">
            <span class="chip">Sequential name { ... }</span>
            <span class="chip">Linked name { ... }</span>
            <span class="chip">Stack name { ... }</span>
            <span class="chip">BST name { ... }</span>
            <span class="chip">AVL name { ... }</span>
            <span class="chip">Huffman name { ... }</span>
          </div>
            <p class="hint">支持数字与字符串；<code>// comment</code> 单行注释；顺序表/栈可用 <code>capacity</code> 指定初始容量。</p>
          </section>

          <section class="guide-section grid">
            <div class="card">
              <div class="card-title">线性结构</div>
              <ul>
                <li><code>init [1, 2, 3]</code></li>
                <li><code>insert 10 at 2</code></li>
                <li><code>delete at 3</code></li>
                <li><code>search 10</code></li>
                <li><code>init [1,2,3] capacity 10</code> <span class="hint-inline">(指定容量)</span></li>
              </ul>
            </div>
            <div class="card">
              <div class="card-title">Stack</div>
              <ul>
                <li><code>push 1</code></li>
                <li><code>pop</code></li>
                <li><code>peek</code></li>
                <li><code>init [1,2] capacity 5</code></li>
              </ul>
            </div>
            <div class="card">
            <div class="card-title">BST / AVL</div>
            <ul>
                <li><code>insert 50</code> / <code>delete 30</code> / <code>search 40</code></li>
                <li><code>traverse</code> <span class="nowrap">inorder | preorder</span></li>
                <li><span class="nowrap">postorder | levelorder</span></li>
                <li><code>min</code>, <code>max</code> (BST)</li>
              </ul>
            </div>
            <div class="card">
              <div class="card-title">Huffman</div>
              <ul>
                <li><code>build_text "ABRACADABRA"</code></li>
                <li><code>build_numbers [1,2,3]</code></li>
                <li><code>encode "ABRA"</code> / <code>decode "0101"</code></li>
                <li><code>show_codes</code></li>
              </ul>
            </div>
          </section>

          <section class="guide-section">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="7 13 10 16 17 9"></polyline>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              Example
            </h3>
<pre>
Sequential myList {
  init [1, 2, 3, 4]
  insert 10 at 2
  delete at 4
}

BST myBST {
  insert 50
  insert 30
  insert 70
  traverse inorder
}

Huffman myZip {
  build_text "HELLO WORLD"
  show_codes
  encode "HELLO"
}</pre>
          </section>

          <section class="guide-section">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14"></path>
                <path d="M5 12h14"></path>
              </svg>
              How It Runs
            </h3>
            <ul class="flow">
              <li>DSL text → Lexer → Parser → AST</li>
              <li>Interpreter maps structure names to instances，执行操作并记录 <code>OperationStep</code></li>
              <li>后端返回结构状态 + 步骤，前端播放动画</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const closeModal = () => {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 2rem;
}

.modal-content {
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.15);
  width: 95%;
  max-width: 1100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  color: #0f172a;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.06);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
  color: #cbd5e1;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #111827;
  transform: scale(1.05);
}

.modal-header {
  padding: 1.5rem 2rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.modal-header h2 {
  margin: 0 0 6px;
  font-size: 1.8rem;
  font-weight: 700;
  letter-spacing: 0.4px;
  color: #0f172a;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.guide-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 2rem 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.guide-section {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 1rem 1.1rem 1rem;
}

.guide-section h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}

.guide-section p {
  margin: 0 0 0.5rem;
  color: #4b5563;
}

.hint-inline {
  color: #6b7280;
  font-size: 0.85rem;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.12);
  color: #065f46;
  font-size: 0.85rem;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.hint {
  color: #4b5563;
  font-size: 0.9rem;
  margin-top: 0.4rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.75rem;
}

.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 0.9rem;
}

.card-title {
  font-weight: 700;
  margin-bottom: 0.4rem;
  color: #111827;
}

ul {
  margin: 0.2rem 0 0.2rem 1rem;
  color: #4b5563;
  padding-left: 0.5rem;
}

li {
  margin-bottom: 0.25rem;
}

code {
  background: rgba(15, 23, 42, 0.05);
  border-radius: 6px;
  padding: 2px 6px;
  color: #0f172a;
}

pre {
  background: #ffffff;
  color: #0f172a;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.9rem;
  white-space: pre-wrap;
  margin: 0.4rem 0 0;
}

.flow {
  list-style: disc;
  margin-left: 1rem;
  color: #4b5563;
}

.nowrap {
  white-space: nowrap;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95);
}

@media (max-width: 768px) {
  .modal-overlay {
    padding: 1rem;
  }

  .modal-content {
    width: 100%;
    height: 90vh;
  }

  .guide-content {
    padding: 1rem 1.25rem 1.25rem;
  }
}
</style>
