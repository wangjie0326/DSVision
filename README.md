# DSVision - 数据结构可视化系统

DSVision 是由 Jie Wang 开发的一个交互式的数据结构可视化教学系统，提供直观的动画演示和步骤追踪功能，帮助数据结构与算法新入门的学生和开发者更好地理解各种数据结构的内部工作原理。

## ✨ 主要特性

- **丰富的数据结构支持**
  - 线性结构：顺序表、链表、栈
  - 树形结构：二叉树、二叉搜索树（BST）、平衡二叉树（AVL）、哈夫曼树

- **实时可视化动画**
  - 逐步演示每个操作的执行过程
  - 高亮显示关键节点和指针变化
  - 自定义动画速度控制

- **自定义 DSL 语言**
  - 声明式语法，简洁易懂
  - 支持批量操作定义
  - 完整的词法/语法分析器

- **AI 自然语言处理**
  - 使用 LLM 将自然语言转换为 DSL 代码
  - 降低使用门槛，提升交互体验

## 🎯 界面预览

![First Page](UI-First Page.png)

## 🛠️ 技术栈

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue 状态管理
- **Axios** - HTTP 客户端

### 后端
- **Flask** - Python Web 框架
- **OpenAI API** - 自然语言处理
- **Python 3.9+** - 核心数据结构实现

## 📁 项目结构

```
DSVision/
├── controller/          # Flask 后端服务
│   └── app.py          # REST API 服务器
├── dsvision/           # 核心数据结构库
│   ├── linear/         # 线性结构实现
│   ├── tree/           # 树结构实现
│   ├── operation/      # 操作步骤记录
│   ├── extend1_dsl/    # 自定义 DSL 解释器
│   └── extend2_llm/    # LLM 自然语言服务
├── view/               # Vue 3 前端应用
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   ├── components/ # 可复用组件
│   │   └── services/   # API 服务
│   └── package.json
└── README.md
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.9 或更高版本
- **Node.js**: 20.19.0 或 22.12.0+
- **npm**: 最新版本

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd DSVision
```

### 2. 配置后端

#### 创建虚拟环境（推荐）

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

#### 安装依赖

```bash
pip install flask flask-cors openai python-dotenv
```

#### 配置环境变量（可选 - LLM 功能）

如果需要使用 AI 自然语言转 DSL 功能，请创建 `.env` 文件：

```bash
# 在项目根目录创建 .env 文件
echo "LLM_PROVIDER=openai" >> .env
echo "LLM_API_KEY=your-api-key-here" >> .env
# 可选：自定义 API 端点
# echo "LLM_BASE_URL=https://your-custom-endpoint.com" >> .env
```

#### 启动后端服务器

```bash
# 从项目根目录运行
python -m controller.app

# 或者
python controller/app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 3. 配置前端

```bash
cd view
npm install 20
```

#### 启动开发服务器

```bash
npm run dev
```

前端应用将在 `http://localhost:5173` 启动。

### 4. 访问应用

打开浏览器访问 `http://localhost:5173`，开始使用 DSVision！

## 📖 使用示例

### DSL 语法示例

#### 创建顺序表并进行操作

```dsl
Sequential myList {
    init [10, 20, 30, 40]
    insert 25 at 2
    delete at 1
    search 30
}
```

#### 构建 AVL 树

```dsl
AVL myAVL {
    insert [50, 30, 70, 20, 40, 60, 80]
    delete 20
    search 60
}
```

#### 哈夫曼编码

```dsl
Huffman myHuffman {
    build_from_text "hello world"
    encode "hello"
    decode "10101"
}
```

### 自然语言示例

你也可以直接使用自然语言（需要配置 LLM API）：

```
创建一个顺序表，初始值为 1, 2, 3, 4, 5，然后在索引 2 的位置插入 10
```

系统会自动转换为对应的 DSL 代码并执行。

## 🎮 功能说明

### 线性结构可视化
- **顺序表**：支持随机访问、插入、删除操作
- **链表**：动态演示指针移动和节点链接
- **栈**：LIFO 操作的直观展示

### 树结构可视化
- **二叉搜索树**：展示查找、插入、删除过程
- **AVL 树**：自动平衡的旋转操作动画
- **哈夫曼树**：编码树构建和编解码过程

### 操作控制
- 播放/暂停动画
- 步进模式（逐步执行）
- 调节动画速度
- 查看操作历史

## 🔧 开发命令

### 后端

```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 运行 Flask 服务器
python -m controller.app
```

### 前端

```bash
cd view

# 开发服务器（热重载）
npm run dev

# 生产构建
npm run build

# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 DSL 完整语法

详细的 DSL 语法参考，请查看：
- [DSL 快速参考](DSL_QUICK_REFERENCE.md)
- [DSL 语法指南](DSL_SYNTAX_GUIDE.md)
- [DSL 演示指南](DSL_PRESENTATION_GUIDE.md)

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 👨‍💻 作者

王颉 - 数据结构与算法课程设计项目 - 指导教师：苏航老师

## 🙏 致谢

感谢这门课的指导老师苏航老师，在每次的检查过程中提了非常宝贵和细致的建议。

感谢所有为数据结构教学可视化做出贡献的开发者和教育工作者。

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
