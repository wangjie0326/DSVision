import { ref, computed } from 'vue'

// Simple language store using composition API
export const currentLanguage = ref(localStorage.getItem('language') || 'en')

// Language translations
export const translations = {
  en: {
    // Navigation
    dslManual: 'DSL Manual',
    llmGuide: 'LLM Guide',
    aboutAuthor: 'About Author',
    importFile: 'Import File',

    // Settings
    settings: 'Settings',
    darkMode: 'Dark Mode',
    language: 'Language',
    english: 'English',
    chinese: '中文',
    about: 'About DSVision',
    version: 'Version 1.0.0',
    on: 'On',
    off: 'Off',

    // Welcome
    welcomeTitle: 'Welcome to DSVision!',
    chooseStructure: 'Hi! You can choose structure first.',
    useDSLorLLM: 'Or you can also use DSL or LLM to explore!',

    // Categories
    linearStructure: 'Linear Structure',
    treeStructure: 'Tree Structure',

    // DSL/LLM
    dslCoding: 'DSL Coding',
    llm: 'LLM',
    quickExamples: 'Quick Examples:',
    sequential: 'Sequential',
    linked: 'Linked',
    stack: 'Stack',
    bst: 'BST',
    huffman: 'Huffman',

    // Placeholders
    dslPlaceholder: 'Enter DSL code here... (Ctrl+Enter to execute)\nExample:\nSequential myList {\n    init [1, 2, 3] capacity 10\n    insert 10 at 2\n}',
    llmPlaceholder: 'Send a natural language instruction here...',

    // Data Structures
    binaryTree: 'Binary Tree',
    binarySearchTree: 'Binary Search Tree',
    avlTree: 'AVL Tree',
    huffmanTree: 'Huffman Tree',
    sequentialList: 'Sequential List',
    linkedList: 'Linked List',
    sequentialStack: 'Sequential Stack',

    // Operations
    insert: 'Insert',
    delete: 'Delete',
    search: 'Search',
    traverse: 'Traverse',
    clear: 'Clear',
    export: 'Export',

    // Messages
    importSuccess: 'Import successful!',
    importFailed: 'Import failed',
    executionSuccess: 'Execution successful',
    executionFailed: 'Execution failed',
    error: 'Error',
    success: 'Success',
  },
  zh: {
    // Navigation
    dslManual: 'DSL 手册',
    llmGuide: 'LLM 指南',
    aboutAuthor: '关于作者',
    importFile: '导入文件',

    // Settings
    settings: '设置',
    darkMode: '深色模式',
    language: '语言',
    english: 'English',
    chinese: '中文',
    about: '关于 DSVision',
    version: '版本 1.0.0',
    on: '开启',
    off: '关闭',

    // Welcome
    welcomeTitle: '欢迎使用 DSVision！',
    chooseStructure: '你好！你可以先选择数据结构。',
    useDSLorLLM: '或者你也可以使用 DSL 或 LLM 来探索！',

    // Categories
    linearStructure: '线性结构',
    treeStructure: '树形结构',

    // DSL/LLM
    dslCoding: 'DSL 编程',
    llm: 'LLM',
    quickExamples: '快速示例：',
    sequential: '顺序表',
    linked: '链表',
    stack: '栈',
    bst: '二叉搜索树',
    huffman: '哈夫曼树',

    // Placeholders
    dslPlaceholder: '在这里输入 DSL 代码... (Ctrl+Enter 执行)\n示例：\nSequential myList {\n    init [1, 2, 3] capacity 10\n    insert 10 at 2\n}',
    llmPlaceholder: '在这里发送自然语言指令...',

    // Data Structures
    binaryTree: '二叉树',
    binarySearchTree: '二叉搜索树',
    avlTree: 'AVL树',
    huffmanTree: '哈夫曼树',
    sequentialList: '顺序表',
    linkedList: '链表',
    sequentialStack: '顺序栈',

    // Operations
    insert: '插入',
    delete: '删除',
    search: '搜索',
    traverse: '遍历',
    clear: '清空',
    export: '导出',

    // Messages
    importSuccess: '导入成功！',
    importFailed: '导入失败',
    executionSuccess: '执行成功',
    executionFailed: '执行失败',
    error: '错误',
    success: '成功',
  }
}

// Get translation for current language
export const t = (key) => {
  return translations[currentLanguage.value]?.[key] || key
}

// Set language
export const setLanguage = (lang) => {
  currentLanguage.value = lang
  localStorage.setItem('language', lang)
}

// Export reactive computed for use in components
export const useLanguage = () => {
  return {
    currentLanguage: computed(() => currentLanguage.value),
    t,
    setLanguage
  }
}
