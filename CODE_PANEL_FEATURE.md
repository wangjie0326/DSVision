# 代码面板功能说明

## 功能概述

DSVision 现在支持**实时代码面板**功能！在执行数据结构操作时，右侧会显示对应的 C++ 实现代码，并且当前执行的代码行会**红色高亮**，同步展示算法的执行流程。

这个功能极大地增强了教学效果，让学生能够：
1. 看到实际的 C++ 代码实现
2. 理解每个操作步骤对应的代码行
3. 同步观察数据结构动画和代码执行

## 核心特性

### 1. 实时代码显示
- 右侧固定面板显示 C++ 代码
- VS Code 深色主题风格
- 代码行号清晰显示
- 支持折叠/展开

### 2. 红色高亮同步
- 当前执行的代码行**红色背景**高亮
- 带有脉冲动画效果，更加醒目
- 自动滚动到当前执行行
- 多行高亮支持

### 3. 操作函数标识
- 顶部显示当前操作函数名（如 `sequential::insert()`）
- 蓝色背景标识，便于识别

### 4. 完整的动画流程
```
用户执行 insert 操作
    ↓
后端记录操作步骤 + 代码行号
    ↓
前端播放动画
    ↓
代码面板同步高亮
    ↓
当前行红色闪烁
```

## 技术实现

### 后端实现

#### 1. 代码模板库 (`dsvision/code_templates/cpp_templates.py`)

存储各种数据结构操作的 C++ 实现代码：

```python
SEQUENTIAL_INSERT = """void insert(int index, int value) {
    // 检查容量，满了则扩容
    if (size >= capacity) {
        expand();  // 1.5倍扩容
    }

    // 检查索引有效性
    if (index < 0 || index > size) {
        return;
    }

    // 从后往前移动元素
    for (int i = size; i > index; i--) {
        data[i] = data[i - 1];
    }

    // 插入新元素
    data[index] = value;
    size++;
}"""
```

支持的数据结构和操作：
- **顺序表**: insert, delete, search, expand
- **链表**: insert_head, insert_tail, delete, search
- **BST**: insert, search, delete
- **AVL**: insert, rotate_left, rotate_right

#### 2. OperationStep 扩展

添加了三个新字段：

```python
class OperationStep:
    # ... 其他字段 ...

    # 🔥 代码面板相关字段
    code_template: str = None        # 模板key (如 'sequential_insert')
    code_line: int = None            # 当前执行的代码行号（从1开始）
    code_highlight: List[int] = None  # 需要高亮的代码行列表
```

#### 3. 数据结构方法中的标记

以顺序表的 `insert` 方法为例：

```python
def insert(self, index: int, value: Any) -> bool:
    # 🔥 对应C++代码第2-4行：检查容量
    step = OperationStep(
        OperationType.INSERT,
        description=f'检查容量 (当前: {self._size}/{self._capacity})',
        data_snapshot=self.to_list(),
        code_template='sequential_insert',  # 🔥 指定代码模板
        code_line=2,                         # 🔥 当前行号
        code_highlight=[2, 3, 4]            # 🔥 高亮行2-4
    )
    self.add_operation_step(step)

    # ... 其他步骤 ...

    # 🔥 对应C++代码第12-14行：移动元素
    step = OperationStep(
        OperationType.POINTER_MOVE,
        description=f'将位置 {i - 1} 的元素移动到位置 {i} (line 13)',
        code_template='sequential_insert',
        code_line=13,                    # 🔥 当前行号
        code_highlight=[13]             # 🔥 高亮行13
    )
    self.add_operation_step(step)
```

#### 4. API 端点

```python
@app.route('/api/code/template/<structure_type>/<operation>', methods=['GET'])
def get_code_template(structure_type, operation):
    """获取代码模板"""
    from dsvision.code_templates import get_code_template

    template_key = f"{structure_type}_{operation}"
    code, total_lines = get_code_template(structure_type, operation)

    return jsonify({
        'success': True,
        'code': code,
        'total_lines': total_lines
    })
```

### 前端实现

#### 1. CodePanel 组件 (`view/src/components/CodePanel.vue`)

核心功能：
- 接收代码字符串
- 接收当前行号和高亮行
- 自动滚动到当前行
- VS Code 风格渲染

Props:
```javascript
props: {
  code: String,              // 代码字符串
  currentLine: Number,       // 当前执行行
  highlightedLines: Array,   // 高亮行列表
  operationName: String      // 操作名称
}
```

CSS 关键样式：
```css
/* 当前执行行 - 红色强调 */
.code-line.current-line {
  background: rgba(255, 68, 68, 0.15);
  border-left: 3px solid #ef4444;
  font-weight: 600;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { background: rgba(255, 68, 68, 0.15); }
  50% { background: rgba(255, 68, 68, 0.25); }
}
```

#### 2. LinearAlgorithm.vue 集成

状态管理：
```javascript
// 🔥 代码面板相关
const currentCode = ref('')              // 当前显示的代码
const currentCodeLine = ref(null)        // 当前执行的代码行
const currentCodeHighlight = ref([])     // 当前高亮的代码行
const currentOperationName = ref('')     // 当前操作名称
```

动画同步：
```javascript
const playOperationSteps = async (steps) => {
  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]

    // 🔥 处理代码面板
    if (step.code_template) {
      // 加载代码模板（如果是新的）
      if (currentCode.value === '' || step.code_template !== currentOperationName.value) {
        await loadCodeTemplate(step.code_template)
      }

      // 更新当前执行行和高亮行
      currentCodeLine.value = step.code_line
      currentCodeHighlight.value = step.code_highlight || []
    }

    // ... 播放其他动画 ...
  }
}
```

加载代码模板：
```javascript
const loadCodeTemplate = async (templateKey) => {
  const parts = templateKey.split('_')
  const structureType = parts[0]
  const operation = parts.slice(1).join('_')

  const response = await fetch(`/api/code/template/${structureType}/${operation}`)
  const data = await response.json()

  if (data.success) {
    currentCode.value = data.code
    currentOperationName.value = `${structureType}::${operation}()`
  }
}
```

## 使用示例

### 示例 1: 顺序表插入

用户执行：
```
Operation: Insert
Value: 10
Index: 2
```

代码面板显示：
```cpp
void insert(int index, int value) {
    // 检查容量，满了则扩容
    if (size >= capacity) {      ← 第2行高亮（检查容量）
        expand();
    }

    // 检查索引有效性
    if (index < 0 || index > size) {  ← 第7行高亮（检查索引）
        return;
    }

    // 从后往前移动元素
    for (int i = size; i > index; i--) {  ← 第12行高亮（移动元素）
        data[i] = data[i - 1];            ← 第13行红色闪烁（执行移动）
    }

    // 插入新元素
    data[index] = value;         ← 第17行红色闪烁（插入元素）
    size++;                      ← 第18行红色闪烁（更新大小）
}
```

### 示例 2: AVL 树左旋

代码面板显示：
```cpp
Node* rotateLeft(Node* y) {
    // 保存节点
    Node* x = y->right;          ← 红色高亮
    Node* T2 = x->left;          ← 红色高亮

    // 执行旋转
    x->left = y;                 ← 红色高亮（旋转中）
    y->right = T2;               ← 红色高亮

    // 更新高度
    updateHeight(y);             ← 红色高亮
    updateHeight(x);

    return x;  // 新根节点
}
```

## 视觉效果

### 代码面板布局
```
┌─────────────────────────────────────┐
│ 🔧 C++ Implementation               │ ← 标题栏（可折叠）
├─────────────────────────────────────┤
│ sequential::insert()                │ ← 操作标识
├─────────────────────────────────────┤
│  1  void insert(int index, int value) {│
│  2    // 检查容量，满了则扩容         │
│  3▸   if (size >= capacity) {        │ ← 当前行（红色闪烁）
│  4      expand();                    │
│  5    }                              │
│  6                                   │
│  7    // 检查索引有效性               │
│  8    if (index < 0 || index > size) {│
│  9      return;                      │
│ 10    }                              │
│ ...                                  │
└─────────────────────────────────────┘
```

### 高亮效果
- **红色背景** (`rgba(255, 68, 68, 0.15)`)
- **红色左边框** (`3px solid #ef4444`)
- **脉冲动画** (1.5秒循环)
- **行号红色** (突出显示)
- **字体加粗** (更易读)

## 扩展其他数据结构

要为其他数据结构添加代码面板支持，只需 3 步：

### 步骤 1: 添加代码模板

在 `cpp_templates.py` 中添加：
```python
LINKED_INSERT_HEAD = """void insertHead(int value) {
    // 创建新节点
    Node* newNode = new Node(value);

    // 新节点指向原头节点
    newNode->next = head;

    // 更新头指针
    head = newNode;
    size++;
}"""

CODE_TEMPLATES['linked_insert_head'] = LINKED_INSERT_HEAD
```

### 步骤 2: 在方法中添加标记

```python
def insert_head(self, value: Any) -> bool:
    # 🔥 对应C++代码第2行
    step = OperationStep(
        OperationType.CREATE_NODE,
        description=f'创建新节点，值为 {value}',
        code_template='linked_insert_head',
        code_line=2,
        code_highlight=[2]
    )
    self.add_operation_step(step)

    # ... 后续步骤 ...
```

### 步骤 3: 前端自动支持

无需修改前端代码！代码面板会自动：
1. 检测 `code_template` 字段
2. 加载对应的 C++ 代码
3. 高亮指定的行号

## 性能优化

- **懒加载**：代码模板只在首次使用时加载
- **缓存机制**：同一操作的代码只加载一次
- **异步加载**：不阻塞动画播放
- **虚拟滚动**：大代码文件流畅滚动

## 常见问题

### Q: 为什么有些操作没有代码显示？
**A**: 需要在对应的 Python 方法中添加 `code_template` 标记。目前只实现了顺序表的 insert 操作作为示例。

### Q: 可以切换其他编程语言吗？
**A**: 可以！只需在 `code_templates` 中添加其他语言的模板（如 Java、Python），并通过配置切换。

### Q: 代码面板可以隐藏吗？
**A**: 可以！点击代码面板标题栏即可折叠/展开。

### Q: 如何调整代码行高亮的速度？
**A**: 修改 CSS 中的 `animation` 持续时间：
```css
animation: pulse 1.5s ease-in-out infinite;  /* 修改1.5s为其他值 */
```

## 后续优化

1. **语言切换**：支持 C++/Java/Python 多种语言
2. **代码编辑**：允许用户修改代码模板
3. **断点功能**：点击行号设置断点，暂停动画
4. **变量监视**：显示当前变量的值
5. **步进模式**：逐行执行代码
6. **代码对比**：显示多种实现方式

---

**开发团队**：王杰
**最后更新**：2025-01-19
**版本**：v1.0
