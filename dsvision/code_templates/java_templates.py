"""
Java 代码模板库
为每种数据结构操作提供对应的Java实现代码，用于教学演示
"""

# ==================== 顺序表代码模板 ====================
SEQUENTIAL_INSERT = """public void insert(int index, int value) {
    // 检查容量，满了则扩容
    if (size >= capacity) {
        expand();
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

SEQUENTIAL_DELETE = """public void delete(int index) {
    // 检查索引有效性
    if (index < 0 || index >= size) {
        return;
    }

    // 从前往后移动元素
    for (int i = index; i < size - 1; i++) {
        data[i] = data[i + 1];
    }

    // 减少大小
    size--;
}"""

SEQUENTIAL_SEARCH = """public int search(int value) {
    // 顺序查找
    for (int i = 0; i < size; i++) {
        if (data[i] == value) {
            return i;  // 找到，返回索引
        }
    }

    return -1;  // 未找到
}"""

SEQUENTIAL_EXPAND = """private void expand() {
    // 计算新容量（1.5倍）
    int newCapacity = (int)(capacity * 1.5);

    // 创建新数组
    int[] newData = new int[newCapacity];

    // 复制旧数据到新数组
    System.arraycopy(data, 0, newData, 0, size);

    // 更新数据和容量
    data = newData;
    capacity = newCapacity;
}"""

# ==================== 栈代码模板 ====================
STACK_PUSH = """public void push(int value) {
    // 检查栈是否已满
    if (top >= capacity - 1) {
        return;  // 栈满
    }

    // 添加元素到栈顶
    top++;
    data[top] = value;
}"""

STACK_POP = """public Integer pop() {
    // 检查栈是否为空
    if (top < 0) {
        return null;  // 栈空
    }

    // 获取栈顶元素
    int value = data[top];

    // 栈顶指针下移
    top--;

    return value;
}"""

STACK_PEEK = """public Integer peek() {
    // 检查栈是否为空
    if (top < 0) {
        return null;
    }

    // 返回栈顶元素（不删除）
    return data[top];
}"""

# ==================== 链表代码模板 ====================
LINKED_INSERT = """public void insert(int index, int value) {
    // 检查索引有效性
    if (index < 0 || index > size) {
        return;
    }

    // 创建新节点
    Node newNode = new Node(value);

    // 插入到头部
    if (index == 0) {
        newNode.next = head;
        head = newNode;
    } else {
        // 遍历找到插入位置的前一个节点
        Node current = head;
        for (int i = 0; i < index - 1; i++) {
            current = current.next;
        }

        // 插入节点
        newNode.next = current.next;
        current.next = newNode;
    }

    size++;
}"""

LINKED_DELETE = """public void delete(int index) {
    // 检查索引有效性
    if (index < 0 || index >= size) {
        return;
    }

    // 删除头节点
    if (index == 0) {
        head = head.next;
    } else {
        // 遍历找到删除位置的前一个节点
        Node current = head;
        for (int i = 0; i < index - 1; i++) {
            current = current.next;
        }

        // 删除节点
        current.next = current.next.next;
    }

    size--;
}"""

LINKED_SEARCH = """public int search(int value) {
    // 从头节点开始遍历
    Node current = head;
    int index = 0;

    while (current != null) {
        if (current.value == value) {
            return index;  // 找到，返回索引
        }
        current = current.next;
        index++;
    }

    return -1;  // 未找到
}"""

# ==================== 二叉搜索树代码模板 ====================
BST_INSERT = """public void insert(int value) {
    root = insertNode(root, value);
}

private Node insertNode(Node node, int value) {
    // 如果节点为空，创建新节点
    if (node == null) {
        return new Node(value);
    }

    // 递归插入
    if (value < node.value) {
        node.left = insertNode(node.left, value);
    } else if (value > node.value) {
        node.right = insertNode(node.right, value);
    }

    return node;
}"""

BST_DELETE = """public void delete(int value) {
    root = deleteNode(root, value);
}

private Node deleteNode(Node node, int value) {
    if (node == null) {
        return null;
    }

    if (value < node.value) {
        node.left = deleteNode(node.left, value);
    } else if (value > node.value) {
        node.right = deleteNode(node.right, value);
    } else {
        // 找到要删除的节点
        if (node.left == null) {
            return node.right;
        }
        if (node.right == null) {
            return node.left;
        }

        // 两个子节点情况
        Node minLargerNode = node.right;
        while (minLargerNode.left != null) {
            minLargerNode = minLargerNode.left;
        }

        node.value = minLargerNode.value;
        node.right = deleteNode(node.right, minLargerNode.value);
    }

    return node;
}"""

BST_SEARCH = """public boolean search(int value) {
    return searchNode(root, value);
}

private boolean searchNode(Node node, int value) {
    if (node == null) {
        return false;
    }

    if (value == node.value) {
        return true;
    } else if (value < node.value) {
        return searchNode(node.left, value);
    } else {
        return searchNode(node.right, value);
    }
}"""

# ==================== AVL树代码模板 ====================
AVL_INSERT = """public void insert(int value) {
    root = insertNode(root, value);
}

private Node insertNode(Node node, int value) {
    if (node == null) {
        return new Node(value);
    }

    if (value < node.value) {
        node.left = insertNode(node.left, value);
    } else if (value > node.value) {
        node.right = insertNode(node.right, value);
    } else {
        return node;
    }

    // 更新高度
    node.height = 1 + Math.max(getHeight(node.left), getHeight(node.right));

    // 计算平衡因子
    int balance = getBalance(node);

    // 执行旋转
    if (balance > 1 && value < node.left.value) {
        return rotateRight(node);
    }
    if (balance < -1 && value > node.right.value) {
        return rotateLeft(node);
    }
    if (balance > 1 && value > node.left.value) {
        node.left = rotateLeft(node.left);
        return rotateRight(node);
    }
    if (balance < -1 && value < node.right.value) {
        node.right = rotateRight(node.right);
        return rotateLeft(node);
    }

    return node;
}"""

AVL_DELETE = """public void delete(int value) {
    root = deleteNode(root, value);
}

private Node deleteNode(Node node, int value) {
    if (node == null) {
        return null;
    }

    if (value < node.value) {
        node.left = deleteNode(node.left, value);
    } else if (value > node.value) {
        node.right = deleteNode(node.right, value);
    } else {
        if (node.left == null) {
            return node.right;
        }
        if (node.right == null) {
            return node.left;
        }

        Node minLargerNode = node.right;
        while (minLargerNode.left != null) {
            minLargerNode = minLargerNode.left;
        }

        node.value = minLargerNode.value;
        node.right = deleteNode(node.right, minLargerNode.value);
    }

    // 更新高度和平衡
    if (node != null) {
        node.height = 1 + Math.max(getHeight(node.left), getHeight(node.right));
        int balance = getBalance(node);

        if (balance > 1) {
            return rotateRight(node);
        }
        if (balance < -1) {
            return rotateLeft(node);
        }
    }

    return node;
}"""

# ==================== 树遍历代码模板 ====================
TREE_TRAVERSAL_INORDER = """void inorder(Node node) {
    if (node == null) return;

    // 递归左子树
    inorder(node.left);

    // 访问当前节点
    visit(node);

    // 递归右子树
    inorder(node.right);
}"""

TREE_TRAVERSAL_PREORDER = """void preorder(Node node) {
    if (node == null) return;

    // 访问当前节点
    visit(node);

    // 递归左子树
    preorder(node.left);

    // 递归右子树
    preorder(node.right);
}"""

TREE_TRAVERSAL_POSTORDER = """void postorder(Node node) {
    if (node == null) return;

    // 递归左子树
    postorder(node.left);

    // 递归右子树
    postorder(node.right);

    // 访问当前节点
    visit(node);
}"""

# 🔄 非递归遍历
TREE_TRAVERSAL_PREORDER_ITERATIVE = """void preorderIterative(Node root) {
    if (root == null) return;

    Deque<Node> stack = new ArrayDeque<>();
    stack.push(root);

    while (!stack.isEmpty()) {
        Node node = stack.pop();
        visit(node);
        if (node.right != null) stack.push(node.right);
        if (node.left != null) stack.push(node.left);
    }
}"""

TREE_TRAVERSAL_INORDER_ITERATIVE = """void inorderIterative(Node root) {
    Deque<Node> stack = new ArrayDeque<>();
    Node curr = root;

    while (curr != null || !stack.isEmpty()) {
        while (curr != null) {
            stack.push(curr);
            curr = curr.left;
        }
        curr = stack.pop();
        visit(curr);
        curr = curr.right;
    }
}"""

TREE_TRAVERSAL_POSTORDER_ITERATIVE = """void postorderIterative(Node root) {
    if (root == null) return;

    Deque<Node> s1 = new ArrayDeque<>();
    Deque<Node> s2 = new ArrayDeque<>();
    s1.push(root);

    while (!s1.isEmpty()) {
        Node node = s1.pop();
        s2.push(node);
        if (node.left != null) s1.push(node.left);
        if (node.right != null) s1.push(node.right);
    }

    while (!s2.isEmpty()) {
        visit(s2.pop());
    }
}"""

TREE_TRAVERSAL_LEVELORDER = """void levelorder(Node root) {
    if (root == null) return;

    Queue<Node> queue = new LinkedList<>();
    queue.add(root);

    while (!queue.isEmpty()) {
        Node node = queue.poll();

        // 访问当前节点
        visit(node);

        if (node.left != null) queue.add(node.left);
        if (node.right != null) queue.add(node.right);
    }
}"""

# ==================== Huffman 树代码模板 ====================
HUFFMAN_BUILD = """void buildHuffmanTree(Map<Character, Integer> frequencies) {
    // 创建最小堆
    PriorityQueue<Node> minHeap = new PriorityQueue<>(
        (a, b) -> a.weight - b.weight
    );

    // 为每个字符创建叶子节点并加入堆
    for (Map.Entry<Character, Integer> entry : frequencies.entrySet()) {
        Node node = new Node(entry.getKey(), entry.getValue());
        minHeap.add(node);
    }

    // 合并节点直到只剩一个根节点
    while (minHeap.size() > 1) {
        // 取出频率最小的两个节点
        Node left = minHeap.poll();
        Node right = minHeap.poll();

        // 创建新的内部节点
        int mergedWeight = left.weight + right.weight;
        Node merged = new Node('\\0', mergedWeight);
        merged.left = left;
        merged.right = right;

        // 将新节点插入堆
        minHeap.add(merged);
    }

    // 最后一个节点就是根节点
    root = minHeap.poll();
}"""

HUFFMAN_ENCODE = """String encode(String text) {
    // 检查编码表是否已生成
    if (huffmanCodes.isEmpty()) {
        generateCodes(root, "");
    }

    StringBuilder encoded = new StringBuilder();

    // 遍历文本，用编码替换每个字符
    for (char c : text.toCharArray()) {
        if (huffmanCodes.containsKey(c)) {
            encoded.append(huffmanCodes.get(c));
        }
    }

    return encoded.toString();
}"""

HUFFMAN_DECODE = """String decode(String encoded) {
    if (root == null) {
        return "";
    }

    StringBuilder decoded = new StringBuilder();
    Node current = root;

    // 遍历编码串
    for (char bit : encoded.toCharArray()) {
        // 根据位向左或向右移动
        if (bit == '0') {
            current = current.left;
        } else {
            current = current.right;
        }

        // 到达叶子节点，记录字符并返回根节点
        if (current.isLeaf()) {
            decoded.append(current.value);
            current = root;
        }
    }

    return decoded.toString();
}"""

HUFFMAN_GENERATE_CODES = """void generateCodes(Node node, String code) {
    if (node == null) return;

    // 如果是叶子节点，记录编码
    if (node.isLeaf()) {
        huffmanCodes.put(node.value, code.isEmpty() ? "0" : code);
        return;
    }

    // 递归处理左右子树（左=0，右=1）
    generateCodes(node.left, code + "0");
    generateCodes(node.right, code + "1");
}"""

# ==================== 代码模板字典 ====================
JAVA_CODE_TEMPLATES = {
    'sequential_insert': SEQUENTIAL_INSERT,
    'sequential_delete': SEQUENTIAL_DELETE,
    'sequential_search': SEQUENTIAL_SEARCH,
    'sequential_expand': SEQUENTIAL_EXPAND,
    'stack_push': STACK_PUSH,
    'stack_pop': STACK_POP,
    'stack_peek': STACK_PEEK,
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

def get_java_template(structure_type, operation):
    """获取Java代码模板"""
    template_key = f"{structure_type}_{operation}"

    if template_key in JAVA_CODE_TEMPLATES:
        code = JAVA_CODE_TEMPLATES[template_key]
        total_lines = len(code.split('\n'))
        return code, total_lines

    return None, 0
