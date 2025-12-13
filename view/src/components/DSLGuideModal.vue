<template>
  <Transition name="modal">
    <div v-if="isOpen" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <!-- Close Button -->
        <button class="close-btn" @click="closeModal">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div class="modal-header">
          <h2>DSL Guide</h2>
          <p class="subtitle">Write concise DSL code, run it instantly, and drive the visualizer.</p>
        </div>

        <div class="guide-content">
          <section class="guide-section">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              What is DSL Mode?
            </h3>
            <p>DSL Mode is a compact domain language for data structures. Each block declares one structure and a sequence of operations — the backend records steps, and the frontend animates them.</p>
            <div class="workflow-diagram">
              <div class="workflow-step">
                <span class="step-number">1</span>
                <span class="step-text">Write DSL</span>
              </div>
              <div class="workflow-arrow">→</div>
              <div class="workflow-step">
                <span class="step-number">2</span>
                <span class="step-text">Lexer & Parser</span>
              </div>
              <div class="workflow-arrow">→</div>
              <div class="workflow-step">
                <span class="step-number">3</span>
                <span class="step-text">Interpreter</span>
              </div>
              <div class="workflow-arrow">→</div>
              <div class="workflow-step">
                <span class="step-number">4</span>
                <span class="step-text">Animation</span>
              </div>
            </div>
          </section>

          <section class="guide-section">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 11 12 14 22 4"></polyline>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              Quick Start (copy & run)
            </h3>
<pre class="code-block">Sequential myList {
  init [1, 2, 3] capacity 5
  insert 10 at 1
  delete at 0
  search 3
}

Stack box {
  init [1, 2, 3, 4] capacity 4
  push 5   // triggers expansion animation
  pop
}</pre>
            <p class="subtitle">One block = one structure. Operations run top to bottom and produce step-by-step animations.</p>
          </section>

          <section class="guide-section">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="9" y1="3" x2="9" y2="21"></line>
              </svg>
              Supported Operations
            </h3>
            <div class="operations-table">
              <div class="operation-category">
                <h5>Sequential</h5>
                <div class="operation-tags">
                  <span class="op-tag">init [list]</span>
                  <span class="op-tag">batch_init</span>
                  <span class="op-tag">insert [at]</span>
                  <span class="op-tag">delete at</span>
                  <span class="op-tag">search</span>
                  <span class="op-tag">capacity n</span>
                </div>
              </div>
              <div class="operation-category">
                <h5>Linked</h5>
                <div class="operation-tags">
                  <span class="op-tag">init [list]</span>
                  <span class="op-tag">insert_head</span>
                  <span class="op-tag">insert_tail</span>
                  <span class="op-tag">insert at</span>
                  <span class="op-tag">delete at</span>
                  <span class="op-tag">search</span>
                </div>
              </div>
              <div class="operation-category">
                <h5>Stack</h5>
                <div class="operation-tags">
                  <span class="op-tag">init [list]</span>
                  <span class="op-tag">capacity n</span>
                  <span class="op-tag">push</span>
                  <span class="op-tag">pop</span>
                  <span class="op-tag">peek</span>
                </div>
              </div>
              <div class="operation-category">
                <h5>Queue</h5>
                <div class="operation-tags">
                  <span class="op-tag">init [list]</span>
                  <span class="op-tag">capacity n</span>
                  <span class="op-tag">enqueue</span>
                  <span class="op-tag">dequeue</span>
                  <span class="op-tag">front</span>
                  <span class="op-tag">rear</span>
                  <span class="op-tag">search</span>
                </div>
              </div>
              <div class="operation-category">
                <h5>BST / AVL</h5>
                <div class="operation-tags">
                  <span class="op-tag">insert</span>
                  <span class="op-tag">delete</span>
                  <span class="op-tag">search</span>
                  <span class="op-tag">traverse *</span>
                  <span class="op-tag">min</span>
                  <span class="op-tag">max</span>
                </div>
              </div>
              <div class="operation-category">
                <h5>Huffman</h5>
                <div class="operation-tags">
                  <span class="op-tag">build_text</span>
                  <span class="op-tag">build_numbers</span>
                  <span class="op-tag">show_codes</span>
                  <span class="op-tag">encode</span>
                  <span class="op-tag">decode</span>
                </div>
              </div>
            </div>
            <p class="subtitle">Traversal options: inorder | preorder | postorder | levelorder.</p>
          </section>

          <section class="guide-section">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 11l3 3L22 4"></path>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              Ready-to-run snippets
            </h3>
            <div class="examples-grid">
              <div class="example-card">
                <h4>Linked list</h4>
<pre class="code-block">Linked chain {
  init [1, 2, 3]
  insert_head 0
  insert_tail 4
  search 2
}</pre>
              </div>
              <div class="example-card">
                <h4>BST</h4>
<pre class="code-block">BST tree {
  insert 50
  insert 30
  insert 70
  traverse inorder
  min
}</pre>
              </div>
              <div class="example-card">
                <h4>Huffman</h4>
<pre class="code-block">Huffman zip {
  build_numbers [2, 4, 6, 8]
  show_codes
}</pre>
              </div>
              <div class="example-card">
                <h4>Queue</h4>
<pre class="code-block">Queue myQueue {
  init [1, 2, 3] capacity 5
  enqueue 4
  front
  dequeue
  rear
}</pre>
              </div>
            </div>
          </section>

          <section class="guide-section">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              Tips (avoid parser errors)
            </h3>
            <ul class="tips-list">
              <li>One structure per block; give it a name: <code>Sequential scores { ... }</code></li>
              <li>Positions need <code>at</code>: <code>insert 10 at 2</code>; missing index will be rejected.</li>
              <li>Capacity applies to Sequential/Stack: <code>capacity 5</code>; stacks default to 5 and expand before inserting.</li>
              <li>LLM handoff: draft with LLM if you forget syntax, then fine-tune here for exact animation order.</li>
            </ul>
          </section>

          <section class="guide-section note-section">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              Execution flow
            </h3>
            <p>Lexer → Parser → AST → Interpreter → OperationStep → Animation. Errors (typos, missing args) are caught early with line/column info.</p>
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
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(0, 0, 0, 0.05);
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
  color: #6b7280;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #374151;
  transform: scale(1.05);
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
}

.guide-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.guide-section {
  margin-bottom: 2rem;
}

.guide-section:last-child {
  margin-bottom: 0;
}

.guide-section h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.guide-section h3 svg {
  color: #20A7FF;
}

.guide-section p {
  margin: 0;
  line-height: 1.6;
  color: #4b5563;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.example-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.example-card h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.example-card ul {
  margin: 0;
  padding-left: 1.25rem;
  list-style: disc;
}

.example-card li {
  margin-bottom: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.example-card li:last-child {
  margin-bottom: 0;
}

.tips-list {
  margin: 0;
  padding-left: 1.5rem;
  list-style: disc;
}

.tips-list li {
  margin-bottom: 0.75rem;
  color: #4b5563;
  line-height: 1.6;
}

.tips-list li:last-child {
  margin-bottom: 0;
}

.note-section {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 0.5rem;
  padding: 1rem;
}

.note-section h3 {
  color: #1e40af;
}

.note-section h3 svg {
  color: #3b82f6;
}

.note-section p {
  color: #1e40af;
  font-size: 0.875rem;
}

/* Workflow Diagram */
.workflow-diagram {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 140px;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #20A7FF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.step-text {
  font-size: 0.875rem;
  color: #4b5563;
  text-align: center;
  font-weight: 500;
}

.workflow-arrow {
  font-size: 1.5rem;
  color: #9ca3af;
  font-weight: bold;
}

/* Operations Table */
.operations-table {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.operation-category h5 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.operation-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.op-tag {
  padding: 0.25rem 0.75rem;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  font-family: 'Consolas', 'Monaco', monospace;
}

.code-block {
  background: #f8fafc;
  color: #0f172a;
  padding: 0.95rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  font-family: 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace;
  white-space: pre-wrap;
  margin: 0;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* Comparison Grid */
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.comparison-card {
  padding: 1rem;
  border-radius: 0.5rem;
  border: 2px solid;
  position: relative;
}

.comparison-card.good {
  background: #f0fdf4;
  border-color: #86efac;
}

.comparison-card.bad {
  background: #fef2f2;
  border-color: #fca5a5;
}

.comparison-badge {
  position: absolute;
  top: -10px;
  right: 10px;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.comparison-card.good .comparison-badge {
  background: #22c55e;
  color: white;
}

.comparison-card.bad .comparison-badge {
  background: #ef4444;
  color: white;
}

.comparison-card p {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #1f2937;
  font-style: italic;
}

.comparison-card small {
  display: block;
  color: #6b7280;
  font-size: 0.75rem;
  line-height: 1.4;
}

/* FAQ List */
.faq-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.faq-item {
  background: #f9fafb;
  border-left: 3px solid #20A7FF;
  padding: 1rem;
  border-radius: 0.25rem;
}

.faq-item h5 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #111827;
}

.faq-item p {
  margin: 0;
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.5;
}

/* VS Grid */
.comparison-section {
  background: #f9fafb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.vs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.vs-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.vs-card h5 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #20A7FF;
}

.vs-card ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.vs-card li {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.5;
  padding-left: 0.25rem;
}

.vs-card li:last-child {
  margin-bottom: 0;
}

/* Modal Transition */
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

/* Scrollbar Styling */
.guide-content::-webkit-scrollbar {
  width: 8px;
}

.guide-content::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 4px;
}

.guide-content::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.guide-content::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 1rem;
  }

  .modal-content {
    width: 95%;
    max-height: 90vh;
  }

  .modal-header {
    padding: 1rem 1.5rem;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .guide-content {
    padding: 1.5rem;
  }

  .examples-grid {
    grid-template-columns: 1fr;
  }

  .workflow-diagram {
    flex-direction: column;
    gap: 0.75rem;
  }

  .workflow-arrow {
    transform: rotate(90deg);
  }

  .workflow-step {
    min-width: auto;
    width: 100%;
  }

  .comparison-grid {
    grid-template-columns: 1fr;
  }

  .vs-grid {
    grid-template-columns: 1fr;
  }

  .operation-tags {
    gap: 0.375rem;
  }

  .op-tag {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
  }
}
</style>
