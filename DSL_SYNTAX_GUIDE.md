# DSVision DSL 用户手册

一份更完整、可演示的 DSL 指南，帮助你用最少的语法记忆完成数据结构操作，并与 LLM 翻译模式形成互补。

## 为什么用这门 DSL？
- 更直观：操作关键字就是动作本身（insert、delete、search…）
- 更快演示：一段 DSL = 多行 Python，动画自动生成
- 更好扩展：新增操作只需在 Lexer / Parser / Interpreter 三处声明
- LLM 友好：自然语言可以一键翻译成 DSL（见 LLM Guide）

## 5 秒快速上手
```
Sequential myList {
    init [1, 2, 3] capacity 5   # 可选容量；栈/顺序表会显示槽位
    insert 10 at 1
    delete at 0
    search 3
}
```
执行结果：顺序表容量 5，经历插入/删除/查询的动画播放。

## 核心语法
```
<结构类型> <变量名> {
    <操作1>
    <操作2>
    ...
}
```
- 一段 DSL 只描述一个结构；多结构请写多段。
- 操作从上到下依次执行，前一步的状态会被后续操作复用。
- 数组字面量用方括号 `[]`，字符串用双引号 `"text"`。

## 支持的结构与操作

**线性结构**
- `Sequential`：`init [list] (capacity n)`、`batch_init 1,2,3`、`insert v [at i]`、`delete at i`、`search v`
- `Linked`：`init [list]`、`insert_head v`、`insert_tail v`、`insert v at i`、`delete at i`、`search v`
- `Stack`：`init [list] (capacity n)`、`push v`、`pop`、`peek`
  - 栈容量可省略，默认 5，满时自动扩容（动画可见）
- `Queue`：`init [list] (capacity n)`、`enqueue v`、`dequeue`、`front`、`rear`、`search v`
  - 指针模型：FRONT/REAR 指针移动，不整体搬移；满时触发扩容动画

**树结构**
- `BST` / `AVL`：`insert n`、`delete n`、`search n`、`traverse inorder|preorder|postorder|levelorder`、`min`、`max`
- `Huffman`：
  - 文本：`build_text "HELLO"`、`show_codes`、`encode "..."`、`decode "..."`  
  - 数字：`build_numbers [2, 4, 6, 8]`

## 常用模板

**顺序表（带容量）**
```
Sequential scores {
    init [60, 80, 90] capacity 6
    insert 75 at 1
    delete at 0
}
```

**链表（头尾插入混合）**
```
Linked chain {
    init [1, 2, 3]
    insert_head 0
    insert_tail 4
    search 2
}
```

**栈（展示扩容）**
```
Stack box {
    init [1, 2, 3, 4] capacity 4
    push 5      # 触发扩容动画
    pop
    peek
}
```

**BST / AVL**
```
BST tree {
    insert 50
    insert 30
    insert 70
    delete 30
    search 70
    min
    max
}
```

**Huffman（数字模式）**
```
Huffman freqTree {
    build_numbers [2, 4, 6, 8]
    show_codes
}
```

**队列（指针移动，不整体前移）**
```
Queue myQueue {
    init [1, 2, 3] capacity 5
    enqueue 4
    front
    dequeue
    rear
}
```

## 好的 vs 不好的写法
- ✓ 清晰：`BST myBST { insert 50; insert 30; search 30 }`
- ✗ 含糊：`make a tree with some numbers`（缺少类型/数据）
- ✓ 指定位置：`insert 10 at 2`
- ✗ 缺参数：`insert 10 at`

## 错误与提示
- 语法错误：拼写/缺参数会在 Parser 阶段报出行列号  
  例：`insrt 10` → `Unknown keyword 'insrt'. Did you mean 'insert'?`
- 类型错误：在不支持的结构上调用操作会被拒绝  
  例：`Sequential { insert_head 1 }`
- 参数错误：数字/字符串缺失或格式不符时会提示

## 与 LLM 协同
- 不想记语法时，用自然语言让 LLM 生成 DSL，确认后执行。
- 多步场景可先用 LLM 生成初稿，再手改 DSL 精确控制。
- 复杂动画（如栈扩容、AVL 旋转）用 DSL 能保证顺序和细节。

## 速查表（口头解释时）
```
DSL = 特定领域语言（数据结构）
流程：Lexer → Parser → Interpreter → OperationStep → 动画
关键类：Token / AST / OperationStep
优势：简洁｜直观｜可视化友好｜LLM 友好
```
