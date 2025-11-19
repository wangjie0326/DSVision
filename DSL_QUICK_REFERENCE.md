# DSL 快速参考卡

## 🎯 核心定义

**DSL是什么**：
> 一种为数据结构操作设计的特殊语言，用户不需要写Python代码，而是用更直观的方式描述数据结构操作。

**为什么要做**：
> 更简洁、更易用、更易扩展、更容易与AI结合。

---

## 📋 三大核心模块

```
┌─────────┐     ┌─────────┐     ┌──────────────┐
│  Lexer  │ --> │ Parser  │ --> │ Interpreter  │
│  分词    │     │ 验证语法 │     │  执行操作     │
└─────────┘     └─────────┘     └──────────────┘
   输入：             输入：           输入：
  "insert 50"    [INSERT, 50]      AST树
                                    输出：
   输出：             输出：        操作历史
  [INSERT, 50]      AST树        (用于动画)
```

---

## 🔤 支持的关键字

| 数据结构 | 操作类型 | 示例 |
|---------|---------|------|
| **Sequential** | init, insert, delete, search | `Sequential list { init [1,2,3] }` |
| **Linked** | init, insert, delete, search, insert_head, insert_tail | `Linked list { insert_head 0 }` |
| **Stack** | init, push, pop, peek | `Stack st { push 1 }` |
| **BST** | insert, delete, search, traverse, min, max | `BST tree { insert 50 }` |
| **AVL** | insert, delete, search, traverse | `AVL tree { insert 50 }` |
| **Huffman** | build_text, build_numbers, show_codes, encode, decode | `Huffman ht { build_text "HELLO" }` |

---

## 💡 快速示例

### 例1：最简单的（30秒钟演示）
```
BST myBST {
    insert 50
    insert 30
    insert 70
}
```
**说的话**："创建一个二叉搜索树，依次插入50、30、70"

### 例2：链表操作
```
Linked myList {
    init [1, 2, 3]
    insert_head 0
    insert_tail 4
}
```

### 例3：Huffman（创新点）
```
Huffman myHuffman {
    build_numbers [2, 4, 6, 8]
}
```
**说的话**："支持直接从数字构建，而不仅是文本"

---

## 🏗️ 执行流程

```
用户输入DSL代码
    ↓
【Lexer】分解成Token
    ↓
【Parser】验证语法，生成AST
    ↓
【Interpreter】执行AST，记录每一步
    ↓
返回：操作历史 + 结果
    ↓
前端播放动画
```

---

## 📦 三个关键类（带功能）

### 1️⃣ Token（记号）
```python
Token(type=INSERT, value="50", line=1, column=5)
```
- 作用：表示DSL代码中的一个最小单位
- 包含：类型、值、位置信息

### 2️⃣ OperationStep（操作步骤）
```python
OperationStep(
    operation=INSERT,
    description="插入50",
    highlight_indices=[1, 2],     # 哪些节点要高亮
    animation_type="pulse",        # 什么动画
    duration=0.5,                  # 多长时间
    data_snapshot=[50, 30, 70]     # 当前状态
)
```
- 作用：记录一步操作的所有信息
- 用于：前端播放动画

### 3️⃣ AST（抽象语法树）
```python
StructureDeclaration(
    type="BST",
    name="myBST",
    operations=[
        InsertOperation(50),
        InsertOperation(30)
    ]
)
```
- 作用：将扁平的Token组织成树形结构
- 用于：便于Interpreter遍历和执行

---

## ⚡ 核心优势速记

| 特点 | 说法 |
|------|------|
| 简洁 | "代码量少，一行DSL顶几行Python" |
| 直观 | "操作名就是关键词，一看就懂" |
| 可扩展 | "添加新操作不需要修改核心系统" |
| 可视化友好 | "OperationStep天然支持动画逐步播放" |
| LLM友好 | "自然语言可以转换为DSL代码" |

---

## ❓ 被问"Lexer做什么"

**快速重讲**：
> "Lexer就是分词器。它把一行代码 `insert 50` 分成两部分：一个是关键字INSERT，一个是数字50。这样后面的Parser就能一个一个地检查。"

---

## ❓ 被问"为什么需要Parser？直接执行不行吗？"

**快速回答**：
> "不行。Token只是一个一个的词，Parser的作用是检查这些词的组合是否符合语法规则。比如 `insert` 后面必须有一个数字，如果没有就是语法错误。Parser发现错误就能立即告诉用户。"

---

## ❓ 被问"OperationStep有什么用？"

**快速回答**：
> "OperationStep记录每个操作的细节信息，包括高亮哪些节点、什么时候改变颜色等。前端就是根据这些信息逐个播放动画，所以用户能看到一步一步的操作过程。"

---

## ❓ 被问"怎么区分不同数据结构的同名操作？"

**快速回答**：
> "通过多态。每个数据结构都实现了自己的insert方法。Interpreter在执行时，根据结构的类型来调用对应的方法。比如LinkedList的insert和BST的insert实现完全不同。"

---

## 🎬 演示时的台词

### 开场
> "我现在演示DSL的执行过程。这是一个Huffman树的例子，用数字2、4、6、8构建。我们在输入框里输入这个DSL代码..."

### 播放
> "现在点击Execute按钮...你可以看到上方显示的频率列表：2、4、6、8。系统会把最小的两个（2和4）用红色高亮...然后合并成一个新节点6...接下来选中6和6...以此类推..."

### 总结
> "这整个过程是这样的：我们的代码通过Lexer分词，再通过Parser验证语法，最后由Interpreter执行，并且记录每一步操作。前端就根据这些操作信息来播放动画。"

---

## 💾 答辩前检查清单

- [ ] 理解Lexer、Parser、Interpreter的作用
- [ ] 能用一句话解释DSL是什么
- [ ] 知道为什么要设计DSL（至少3个理由）
- [ ] 能说出5种支持的数据结构
- [ ] 理解Token和AST的区别
- [ ] 能手指着代码解释执行流程
- [ ] 准备好一个简单的DSL演示例子
- [ ] 知道项目的创新点（Huffman双模式 + LLM）

---

## 🚀 最后：一句话总结

> **"我们的DSL让用户用最直观的方式操作数据结构，通过Lexer、Parser、Interpreter三个阶段处理，最后记录OperationStep供前端播放动画，达到了教学和易用性的完美结合。"**

---

## 📱 速记

```
DSL = 特定领域语言
Lexer = 分词（字符串→Token列表）
Parser = 检验（Token→AST）
Interp = 执行（AST→操作历史）

3个关键类：
Token → 最小单位
OperationStep → 动画信息
AST → 树形结构

记住核心优势：
✓简洁 ✓直观 ✓可扩展 ✓可视化友好
```

