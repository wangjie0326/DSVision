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
}

def get_java_template(structure_type, operation):
    """获取Java代码模板"""
    template_key = f"{structure_type}_{operation}"

    if template_key in JAVA_CODE_TEMPLATES:
        code = JAVA_CODE_TEMPLATES[template_key]
        total_lines = len(code.split('\n'))
        return code, total_lines

    return None, 0
