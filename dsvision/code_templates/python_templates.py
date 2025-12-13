"""
Python 代码模板库
为每种数据结构操作提供对应的Python实现代码，用于教学演示
"""

# ==================== 顺序表代码模板 ====================
SEQUENTIAL_INSERT = """def insert(self, index, value):
    # 检查容量，满了则扩容
    if self.size >= self.capacity:
        self.expand()

    # 检查索引有效性
    if index < 0 or index > self.size:
        return

    # 从后往前移动元素
    for i in range(self.size, index, -1):
        self.data[i] = self.data[i - 1]

    # 插入新元素
    self.data[index] = value
    self.size += 1"""

SEQUENTIAL_DELETE = """def delete(self, index):
    # 检查索引有效性
    if index < 0 or index >= self.size:
        return

    # 从前往后移动元素
    for i in range(index, self.size - 1):
        self.data[i] = self.data[i + 1]

    # 减少大小
    self.size -= 1"""

SEQUENTIAL_SEARCH = """def search(self, value):
    # 顺序查找
    for i in range(self.size):
        if self.data[i] == value:
            return i  # 找到，返回索引

    return -1  # 未找到"""

SEQUENTIAL_EXPAND = """def expand(self):
    # 计算新容量（1.5倍）
    new_capacity = int(self.capacity * 1.5)

    # 创建新列表
    new_data = [None] * new_capacity

    # 复制旧数据到新列表
    for i in range(self.size):
        new_data[i] = self.data[i]

    # 更新数据和容量
    self.data = new_data
    self.capacity = new_capacity"""

# ==================== 栈代码模板 ====================
STACK_PUSH = """def push(self, value):
    # 检查栈是否已满
    if self.top >= self.capacity - 1:
        return  # 栈满

    # 添加元素到栈顶
    self.top += 1
    self.data[self.top] = value"""

STACK_POP = """def pop(self):
    # 检查栈是否为空
    if self.top < 0:
        return None  # 栈空

    # 获取栈顶元素
    value = self.data[self.top]

    # 栈顶指针下移
    self.top -= 1

    return value"""

STACK_PEEK = """def peek(self):
    # 检查栈是否为空
    if self.top < 0:
        return None

    # 返回栈顶元素（不删除）
    return self.data[self.top]"""

# ==================== 链表代码模板 ====================
LINKED_INSERT = """def insert(self, index, value):
    # 检查索引有效性
    if index < 0 or index > self.size:
        return

    # 创建新节点
    new_node = Node(value)

    # 插入到头部
    if index == 0:
        new_node.next = self.head
        self.head = new_node
    else:
        # 遍历找到插入位置的前一个节点
        current = self.head
        for i in range(index - 1):
            current = current.next

        # 插入节点
        new_node.next = current.next
        current.next = new_node

    self.size += 1"""

LINKED_DELETE = """def delete(self, index):
    # 检查索引有效性
    if index < 0 or index >= self.size:
        return

    # 删除头节点
    if index == 0:
        self.head = self.head.next
    else:
        # 遍历找到删除位置的前一个节点
        current = self.head
        for i in range(index - 1):
            current = current.next

        # 删除节点
        current.next = current.next.next

    self.size -= 1"""

LINKED_SEARCH = """def search(self, value):
    # 从头节点开始遍历
    current = self.head
    index = 0

    while current:
        if current.value == value:
            return index  # 找到，返回索引
        current = current.next
        index += 1

    return -1  # 未找到"""

# ==================== 二叉搜索树代码模板 ====================
BST_INSERT = """def insert(self, value):
    # 创建新节点
    new_node = Node(value)

    # 如果树为空
    if self.root is None:
        self.root = new_node
        return

    # 从根节点开始遍历
    current = self.root
    while current:
        if value < current.value:
            # 左子树
            if current.left is None:
                current.left = new_node
                break
            current = current.left
        else:
            # 右子树
            if current.right is None:
                current.right = new_node
                break
            current = current.right"""

BST_DELETE = """def delete(self, value):
    self.root = self._delete_node(self.root, value)

def _delete_node(self, node, value):
    if node is None:
        return None

    if value < node.value:
        node.left = self._delete_node(node.left, value)
    elif value > node.value:
        node.right = self._delete_node(node.right, value)
    else:
        # 找到要删除的节点
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left

        # 两个子节点情况
        min_larger_node = node.right
        while min_larger_node.left:
            min_larger_node = min_larger_node.left

        node.value = min_larger_node.value
        node.right = self._delete_node(node.right, min_larger_node.value)

    return node"""

BST_SEARCH = """def search(self, value):
    current = self.root

    while current:
        if current.value == value:
            return True  # 找到
        elif value < current.value:
            current = current.left
        else:
            current = current.right

    return False  # 未找到"""

# ==================== AVL树代码模板 ====================
AVL_INSERT = """def insert(self, value):
    self.root = self._insert_node(self.root, value)

def _insert_node(self, node, value):
    # 递归插入
    if node is None:
        return Node(value)

    if value < node.value:
        node.left = self._insert_node(node.left, value)
    elif value > node.value:
        node.right = self._insert_node(node.right, value)
    else:
        return node

    # 更新高度
    node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

    # 计算平衡因子
    balance = self._get_balance(node)

    # 执行旋转
    if balance > 1 and value < node.left.value:
        return self._rotate_right(node)
    if balance < -1 and value > node.right.value:
        return self._rotate_left(node)
    if balance > 1 and value > node.left.value:
        node.left = self._rotate_left(node.left)
        return self._rotate_right(node)
    if balance < -1 and value < node.right.value:
        node.right = self._rotate_right(node.right)
        return self._rotate_left(node)

    return node"""

AVL_DELETE = """def delete(self, value):
    self.root = self._delete_node(self.root, value)

def _delete_node(self, node, value):
    if node is None:
        return None

    if value < node.value:
        node.left = self._delete_node(node.left, value)
    elif value > node.value:
        node.right = self._delete_node(node.right, value)
    else:
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left

        min_larger_node = node.right
        while min_larger_node.left:
            min_larger_node = min_larger_node.left

        node.value = min_larger_node.value
        node.right = self._delete_node(node.right, min_larger_node.value)

    # 更新高度和平衡
    if node:
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        if balance > 1:
            return self._rotate_right(node)
        if balance < -1:
            return self._rotate_left(node)

    return node"""

# ==================== 树遍历代码模板 ====================
TREE_TRAVERSAL_INORDER = """def inorder(self, node):
    if node is None:
        return

    # 递归左子树
    self.inorder(node.left)

    # 访问当前节点
    self.visit(node)

    # 递归右子树
    self.inorder(node.right)"""

TREE_TRAVERSAL_PREORDER = """def preorder(self, node):
    if node is None:
        return

    # 访问当前节点
    self.visit(node)

    # 递归左子树
    self.preorder(node.left)

    # 递归右子树
    self.preorder(node.right)"""

TREE_TRAVERSAL_POSTORDER = """def postorder(self, node):
    if node is None:
        return

    # 递归左子树
    self.postorder(node.left)

    # 递归右子树
    self.postorder(node.right)

    # 访问当前节点
    self.visit(node)"""

# 🔄 非递归遍历
TREE_TRAVERSAL_PREORDER_ITERATIVE = """def preorder_iterative(self, root):
    if root is None:
        return
    stack = [root]
    while stack:
        node = stack.pop()
        self.visit(node)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
"""

TREE_TRAVERSAL_INORDER_ITERATIVE = """def inorder_iterative(self, root):
    stack = []
    curr = root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        self.visit(curr)
        curr = curr.right
"""

TREE_TRAVERSAL_POSTORDER_ITERATIVE = """def postorder_iterative(self, root):
    if root is None:
        return
    s1, s2 = [root], []
    while s1:
        node = s1.pop()
        s2.append(node)
        if node.left:
            s1.append(node.left)
        if node.right:
            s1.append(node.right)
    while s2:
        self.visit(s2.pop())
"""

TREE_TRAVERSAL_LEVELORDER = """def levelorder(self, root):
    if root is None:
        return

    queue = [root]

    while queue:
        node = queue.pop(0)

        # 访问当前节点
        self.visit(node)

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)"""

# ==================== Huffman 树代码模板 ====================
HUFFMAN_BUILD = """def build_huffman_tree(self, frequencies):
    # 创建最小堆
    import heapq
    heap = []

    # 为每个字符创建叶子节点并加入堆
    for char, freq in frequencies.items():
        node = HuffmanNode(char, freq)
        heapq.heappush(heap, (freq, node))

    # 合并节点直到只剩一个根节点
    while len(heap) > 1:
        # 取出频率最小的两个节点
        freq1, left = heapq.heappop(heap)
        freq2, right = heapq.heappop(heap)

        # 创建新的内部节点
        merged_freq = freq1 + freq2
        merged = HuffmanNode(None, merged_freq)
        merged.left = left
        merged.right = right

        # 将新节点插入堆
        heapq.heappush(heap, (merged_freq, merged))

    # 最后一个节点就是根节点
    self.root = heap[0][1] if heap else None"""

HUFFMAN_ENCODE = """def encode(self, text):
    # 检查编码表是否已生成
    if not self.huffman_codes:
        self.generate_codes(self.root, "")

    encoded = ""

    # 遍历文本，用编码替换每个字符
    for char in text:
        if char in self.huffman_codes:
            encoded += self.huffman_codes[char]

    return encoded"""

HUFFMAN_DECODE = """def decode(self, encoded):
    if self.root is None:
        return ""

    decoded = ""
    current = self.root

    # 遍历编码串
    for bit in encoded:
        # 根据位向左或向右移动
        if bit == '0':
            current = current.left
        else:
            current = current.right

        # 到达叶子节点，记录字符并返回根节点
        if current.is_leaf():
            decoded += current.value
            current = self.root

    return decoded"""

HUFFMAN_GENERATE_CODES = """def generate_codes(self, node, code):
    if node is None:
        return

    # 如果是叶子节点，记录编码
    if node.is_leaf():
        self.huffman_codes[node.value] = code if code else "0"
        return

    # 递归处理左右子树（左=0，右=1）
    self.generate_codes(node.left, code + "0")
    self.generate_codes(node.right, code + "1")"""

# ==================== Queue ====================
QUEUE_ENQUEUE = """def enqueue(self, value):
    # 满则扩容
    if self.is_full():
        self._expand()

    self._rear += 1
    self._data[self._rear] = value
    if self._size == 0:
        self._front = 0
    self._size += 1"""

QUEUE_DEQUEUE = """def dequeue(self):
    if self.is_empty():
        return None

    value = self._data[self._front]
    self._data[self._front] = None
    self._front += 1
    self._size -= 1
    if self._size == 0:
        self._front = 0
        self._rear = -1
    return value"""

QUEUE_FRONT = """def front(self):
    if self.is_empty():
        return None
    return self._data[self._front]"""

QUEUE_REAR = """def rear(self):
    if self.is_empty():
        return None
    return self._data[self._rear]"""

# ==================== 代码模板字典 ====================
PYTHON_CODE_TEMPLATES = {
    'sequential_insert': SEQUENTIAL_INSERT,
    'sequential_delete': SEQUENTIAL_DELETE,
    'sequential_search': SEQUENTIAL_SEARCH,
    'sequential_expand': SEQUENTIAL_EXPAND,
    'stack_push': STACK_PUSH,
    'stack_pop': STACK_POP,
    'stack_peek': STACK_PEEK,
    'queue_enqueue': QUEUE_ENQUEUE,
    'queue_dequeue': QUEUE_DEQUEUE,
    'queue_front': QUEUE_FRONT,
    'queue_rear': QUEUE_REAR,
    'linked_insert': LINKED_INSERT,
    'linked_delete': LINKED_DELETE,
    'linked_search': LINKED_SEARCH,
    'bst_insert': BST_INSERT,
    'bst_delete': BST_DELETE,
    'bst_search': BST_SEARCH,
    'avl_insert': AVL_INSERT,
    'avl_delete': AVL_DELETE,

    # 树遍历
    'tree_traversal_inorder': TREE_TRAVERSAL_INORDER,
    'tree_traversal_preorder': TREE_TRAVERSAL_PREORDER,
    'tree_traversal_postorder': TREE_TRAVERSAL_POSTORDER,
    'tree_traversal_levelorder': TREE_TRAVERSAL_LEVELORDER,
    'tree_traversal_preorder_iterative': TREE_TRAVERSAL_PREORDER_ITERATIVE,
    'tree_traversal_inorder_iterative': TREE_TRAVERSAL_INORDER_ITERATIVE,
    'tree_traversal_postorder_iterative': TREE_TRAVERSAL_POSTORDER_ITERATIVE,

    # Huffman树
    'huffman_build': HUFFMAN_BUILD,
    'huffman_encode': HUFFMAN_ENCODE,
    'huffman_decode': HUFFMAN_DECODE,
    'huffman_generate_codes': HUFFMAN_GENERATE_CODES,
}

def get_python_template(structure_type, operation):
    """获取Python代码模板"""
    template_key = f"{structure_type}_{operation}"

    if template_key in PYTHON_CODE_TEMPLATES:
        code = PYTHON_CODE_TEMPLATES[template_key]
        total_lines = len(code.split('\n'))
        return code, total_lines

    return None, 0
