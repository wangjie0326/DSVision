# 顺序表扩容功能说明

## 功能概述

DSVision 现在支持顺序表的**自动扩容**功能，当顺序表容量已满时，系统会自动进行 1.5 倍扩容，并提供完整的动画演示。

## 核心特性

### 1. 自动扩容机制
- **触发条件**：当 `size >= capacity` 时，插入新元素会触发扩容
- **扩容倍数**：1.5 倍扩容（`new_capacity = int(old_capacity * 1.5)`）
- **无缝切换**：扩容完成后自动切换到新数组，不影响数据完整性

### 2. 完整的动画演示
扩容过程分为以下步骤，每个步骤都有对应的动画效果：

1. **容量已满提示** (0.5s)
   - 高亮显示当前状态
   - 提示信息：`容量已满 (当前: 2/2)，触发扩容`

2. **扩容计划** (0.5s)
   - 显示扩容方案：`准备扩容: 2 -> 3 (1.5倍)`

3. **创建新数组** (0.8s)
   - 在原数组下方淡入显示新数组
   - 带有 "新数组 (容量: 3)" 标签
   - 绿色虚线边框，浅绿色背景

4. **逐个复制元素** (每个元素 0.5s)
   - 从旧数组逐个移动元素到新数组
   - 每个元素复制后短暂高亮

5. **标记旧数组删除** (1.0s)
   - 旧数组所有元素全红闪烁
   - 提示：`标记旧数组准备删除`

6. **完成扩容** (0.8s)
   - 旧数组淡出消失
   - 新数组成为主数组
   - 容量值更新

### 3. DSL 语法支持

#### 基本语法
```dsl
Sequential myList {
    init [values...] capacity N
}
```

#### 示例 1: 指定初始容量
```dsl
Sequential smallList {
    init [1, 2, 3] capacity 5
    insert 4
    insert 5
    insert 6  // 触发扩容：5 -> 7
}
```

#### 示例 2: 演示多次扩容
```dsl
Sequential tinyList {
    init [10, 20] capacity 2
    insert 30  // 第1次扩容：2 -> 3
    insert 40  // 第2次扩容：3 -> 4
    insert 50  // 第3次扩容：4 -> 6
}
```

## 使用方法

### 方法 1: 通过 DSL 输入栏

1. 在首页点击 "DSL Input" 按钮
2. 输入 DSL 代码，例如：
   ```dsl
   Sequential test {
       init [1, 2] capacity 2
       insert 3
       insert 4
   }
   ```
3. 点击 "Execute" 观看扩容动画

### 方法 2: 手动操作

1. 进入 "Sequential List Visualization"
2. 设置 **Capacity** 为较小的值（如 2 或 3）
3. 使用 "Batch Init" 初始化数据
4. 继续插入元素，当容量满时会自动触发扩容

### 方法 3: 使用 LLM 自然语言

如果已配置 LLM API，可以使用自然语言：
```
创建一个容量为3的顺序表，初始值为 10, 20, 30，
然后依次插入 40, 50, 60，观察扩容过程
```

## 技术实现

### 后端实现

#### 1. 操作类型（`operation.py`）
```python
class OperationType(Enum):
    EXPAND = "expand"  # 扩容操作
```

#### 2. 扩容方法（`sequential_list.py`）
```python
def _expand(self) -> bool:
    """扩容操作 - 1.5倍扩容，带完整动画步骤"""
    old_capacity = self._capacity
    new_capacity = int(old_capacity * 1.5)

    # 记录动画步骤
    # 1. 提示容量已满
    # 2. 显示扩容计划
    # 3. 创建新数组 (visual_hints: new_array, new_capacity)
    # 4. 逐个复制元素 (visual_hints: copy_index, new_array)
    # 5. 标记旧数组删除 (visual_hints: old_array_delete)
    # 6. 完成扩容

    return True
```

#### 3. DSL 语法支持

**Lexer** (`lexer.py`)：
```python
CAPACITY = "CAPACITY"
KEYWORDS = {
    'capacity': TokenType.CAPACITY,
    # ...
}
```

**Parser** (`parser.py`)：
```python
if token.type == TokenType.INIT:
    self.advance()
    values = self.parse_array()
    capacity = None
    if self.current_token and self.current_token.type == TokenType.CAPACITY:
        self.advance()
        capacity = self.expect(TokenType.NUMBER).value
    return InitOperation(values=values, capacity=capacity)
```

**AST Node** (`ast_nodes.py`)：
```python
@dataclass
class InitOperation(Operation):
    values: List[Any]
    capacity: Optional[int] = None
```

### 前端实现

#### 响应式状态（`LinearAlgorithm.vue`）
```javascript
const isExpanding = ref(false)       // 是否正在扩容
const newArray = ref([])             // 新数组数据
const newCapacity = ref(0)           // 新容量
const oldArrayMarkedForDelete = ref(false)  // 旧数组删除标记
```

#### 动画处理逻辑
```javascript
if (step.operation === 'expand') {
  if (step.visual_hints) {
    // 显示新数组
    if (step.visual_hints.new_array) {
      isExpanding.value = true
      newArray.value = [...step.visual_hints.new_array]
      newCapacity.value = step.visual_hints.new_capacity
    }

    // 标记旧数组删除
    if (step.visual_hints.old_array_delete) {
      oldArrayMarkedForDelete.value = true
    }
  }

  // 扩容完成，切换
  if (step.description.includes('扩容完成')) {
    isExpanding.value = false
    capacity.value = newCapacity.value
  }
}
```

#### CSS 动画样式
```css
/* 新数组容器 - 绿色虚线边框 */
.new-array-container {
  background-color: #f0fdf4;
  border: 2px dashed #10b981;
  animation: fadeIn 0.5s ease;
}

/* 标记删除的节点 - 全红闪烁 */
.delete-marked {
  background-color: #ef4444 !important;
  animation: deleteFlash 1s ease-in-out infinite;
}

/* 旧数组淡出 */
.old-array-delete {
  animation: fadeOut 1s ease-out forwards;
}
```

## 测试验证

运行测试脚本：
```bash
python test_expansion.py
```

测试结果：
- ✅ 基本扩容功能：通过
- ✅ 扩容动画步骤：通过（10个步骤，包含新数组、复制、删除标记）
- ✅ 多次扩容：通过（连续插入10个元素，触发5次扩容）

## 视觉效果预览

### 扩容前
```
旧数组 (容量: 2)
┌────┬────┐
│ 10 │ 20 │
└────┴────┘
```

### 扩容中
```
旧数组 (容量: 2) 【全红闪烁】
┌────┬────┐
│ 10 │ 20 │ ← 准备删除
└────┴────┘

新数组 (容量: 3) 【绿色虚线边框】
┌────┬────┬────┐
│ 10 │ 20 │    │ ← 逐个复制
└────┴────┴────┘
```

### 扩容后
```
┌────┬────┬────┐
│ 10 │ 20 │ 30 │
└────┴────┴────┘
容量: 3
```

## 常见问题

### Q: 为什么是 1.5 倍扩容而不是 2 倍？
**A**: 1.5 倍扩容在空间利用率和性能之间取得了良好的平衡。2 倍扩容会导致空间浪费，而 1.5 倍能更有效地利用内存。

### Q: 扩容会影响原有数据吗？
**A**: 不会。扩容过程会完整复制所有元素到新数组，保证数据完整性。

### Q: 可以自定义扩容倍数吗？
**A**: 当前实现固定为 1.5 倍。如需修改，请在 `sequential_list.py` 的 `_expand()` 方法中修改：
```python
new_capacity = int(old_capacity * 1.5)  # 修改这里
```

### Q: 动画太快/太慢怎么办？
**A**: 在前端界面调整 "Speed" 选项：
- 0.5x：慢速，适合观察细节
- 1x：正常速度
- 2x：快速
- 4x：超快速

## 后续优化建议

1. **缩容功能**：当 `size < capacity / 2` 时自动缩容
2. **预扩容**：批量插入时预判容量需求，减少扩容次数
3. **自定义扩容因子**：允许用户指定扩容倍数
4. **内存统计**：显示扩容前后的内存使用情况

## 更新日志

### v1.0 - 2025年1月
- ✅ 实现基本扩容功能（1.5倍）
- ✅ 添加完整的动画演示（10个步骤）
- ✅ DSL 语法支持 capacity 参数
- ✅ 前端双数组渲染
- ✅ 旧数组全红强调动画
- ✅ 新数组淡入淡出效果

---

**开发团队**：王杰
**最后更新**：2025-01-18