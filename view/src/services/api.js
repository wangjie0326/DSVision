import axios from 'axios'; //用于调用Flask接口

//const API_BASE_URL = 'http://localhost:5000/api';
const API_BASE_URL = '/api';


//创建axios实例
const apiClient = axios.create({
  baseURL:API_BASE_URL,
  timeout: 10000,
  headers:{
    'Content-Type':'application/json'
  },
  withCredentials:false
});

apiClient.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.data);
    return response.data;
  },
  (error) => {
    console.error('API错误:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);


export default{
  //健康检查
  checkHealth(){
    return apiClient.get('/health');
  },

  //创建数据结构
  createStructure(type,capacity = 100) {
    return apiClient.post('/structure/create', {
      type,
      capacity
    });
  },

  //获取数据结构状态
  getState(structureId){
    return apiClient.get(`/structure/${structureId}/state`);
  },


  //批量初始化元素
  initBatch(structureId, values) {
    return apiClient.post(`/structure/${structureId}/init_batch`, {
      values
    });
  },

  //插入元素
  insertElement(structureId,index,value){
    return apiClient.post(`/structure/${structureId}/insert`,{index,
      value
    });
  },

  //删除元素
  deleteElement(structureId,index) {
    return apiClient.post(`/structure/${structureId}/delete`, {
      index
    });
  },

  //搜索元素
  searchElement(structureId,value) {
    return apiClient.post(`/structure/${structureId}/search`, {
      value
    });
  },

  //清空结构
  clearStructure(structureId) {
    return apiClient.post(`/structure/${structureId}/clear`);
  },

  //删除结构
  deleteStructure(structureId) {
    return apiClient.delete(`/structure/${structureId}`);
  },


// ==================== 树结构接口 ====================

  //创建树结构
  createTreeStructure(type){
    return apiClient.post('/tree/create',{
      type
    });
  },
  // 获取树数据结构状态
  getTreeState(structureId) {
    return apiClient.get(`/tree/${structureId}/state`);
  },

  // 插入树节点
  insertTreeNode(structureId, value) {
    return apiClient.post(`/tree/${structureId}/insert`, {
      value
    });
  },

  // 删除树节点
  deleteTreeNode(structureId, value) {
    return apiClient.post(`/tree/${structureId}/delete`, {
      value
    });
  },

  // 搜索树节点
  searchTreeNode(structureId, value) {
    return apiClient.post(`/tree/${structureId}/search`, {
      value
    });
  },

  // 清空树结构
  clearTreeStructure(structureId) {
    return apiClient.post(`/tree/${structureId}/clear`);
  },

  // 删除树结构
  deleteTreeStructure(structureId) {
    return apiClient.delete(`/tree/${structureId}`);
  },

  // 🎬 树遍历
  traverseTree(structureId, traversalType) {
    return apiClient.post(`/tree/${structureId}/traverse`, {
      traversal_type: traversalType
    });
  },

  // ==================== Huffman树专用接口 ====================

  // 从文本或数字列表构建Huffman树
  buildHuffmanTree(structureId, textOrNumbers) {
    // 判断是文本还是数字数组
    const payload = Array.isArray(textOrNumbers)
      ? { numbers: textOrNumbers }  // 数字模式
      : { text: textOrNumbers };     // 文本模式

    return apiClient.post(`/tree/${structureId}/huffman/build`, payload);
  },

  // 从权重字典构建Huffman树
  buildHuffmanFromWeights(structureId, weights) {
    return apiClient.post(`/tree/${structureId}/huffman/build-weights`, {
      weights
    });
  },

  // Huffman编码
  encodeHuffman(structureId, text) {
    return apiClient.post(`/tree/${structureId}/huffman/encode`, {
      text
    });
  },

  // Huffman解码
  decodeHuffman(structureId, encoded) {
    return apiClient.post(`/tree/${structureId}/huffman/decode`, {
      encoded
    });
  },

  // 获取Huffman编码表
  getHuffmanCodes(structureId) {
    return apiClient.get(`/tree/${structureId}/huffman/codes`);
  },

  // ==================== BST专用接口 ====================

  // 从列表构建BST
  buildBSTFromList(structureId, values) {
    return apiClient.post(`/tree/${structureId}/bst/build`, {
      values
    });
  },

  // 获取BST的最小值
  getBSTMin(structureId) {
    return apiClient.get(`/tree/${structureId}/bst/min`);
  },

  // 获取BST的最大值
  getBSTMax(structureId) {
    return apiClient.get(`/tree/${structureId}/bst/max`);
  },

  // ==================== 二叉树专用接口 ====================

  // 从列表构建二叉树（层序）
  buildBinaryTreeFromList(structureId, values) {
    return apiClient.post(`/tree/${structureId}/binary/build`, {
      values
    });
  },

  // ==================== 遍历接口 ====================

  // 获取树的所有遍历结果
  getTreeTraversals(structureId) {
    return apiClient.get(`/tree/${structureId}/traversals`);
  },

  // 前序遍历
  preorderTraversal(structureId) {
    return apiClient.get(`/tree/${structureId}/traversal/preorder`);
  },

  // 中序遍历
  inorderTraversal(structureId) {
    return apiClient.get(`/tree/${structureId}/traversal/inorder`);
  },

  // 后序遍历
  postorderTraversal(structureId) {
    return apiClient.get(`/tree/${structureId}/traversal/postorder`);
  },

  // 层序遍历
  levelorderTraversal(structureId) {
    return apiClient.get(`/tree/${structureId}/traversal/levelorder`);
  },

  // 导出数据结构
  exportStructure(structureId) {
    return apiClient.get(`/structure/${structureId}/export`);
  },

  // 导入数据结构
  importStructure(structureData) {
    return apiClient.post('/structure/import', structureData);
  },
  // ==================== DSL 相关接口 ====================

  // 执行 DSL 代码
  executeDSL(code, sessionId = null) {
    return apiClient.post('/dsl/execute', {
      code,
      session_id: sessionId
    });
  },

  // 验证 DSL 语法
  validateDSL(code) {
    return apiClient.post('/dsl/validate', {
      code
    });
  },

  // 获取 DSL 示例
  getDSLExamples() {
    return apiClient.get('/dsl/examples');
  },

  // 删除 DSL 会话
  deleteDSLSession(sessionId) {
    return apiClient.delete(`/dsl/session/${sessionId}`);
  },


  // ==================== LLM 相关接口 ====================

  /**
   * LLM对话 - 自然语言转DSL并执行
   * @param {string} message - 用户输入的自然语言
   * @param {string} sessionId - 会话ID(可选)
   * @returns {Promise} 包含DSL代码和执行结果
   */
  llmChat(message, sessionId = null) {
    return apiClient.post('/llm/chat', {
      message,
      session_id: sessionId
    });
  },

  /**
   * 检查LLM服务状态
   * @returns {Promise} LLM服务配置信息
   */
  llmStatus() {
    return apiClient.get('/llm/status');
  },

  /**
   * 获取LLM配置
   * @returns {Promise} 当前LLM配置
   */
  getLLMConfig() {
    return apiClient.get('/llm/config');
  },

  /**
   * 更新LLM配置
   * @param {string} provider - LLM提供商 ('openai' | 'claude' | 'tongyi')
   * @param {string} apiKey - API密钥
   * @returns {Promise} 更新结果
   */
  updateLLMConfig(provider, apiKey) {
    return apiClient.post('/llm/config', {
      provider,
      api_key: apiKey
    });
  }
};
