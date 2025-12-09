"""
C++ 代码模板库
为每种数据结构操作提供对应的C++实现代码，用于教学演示
"""

# ==================== 顺序表代码模板 ====================
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

SEQUENTIAL_DELETE = """void deleteAt(int index) {
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

SEQUENTIAL_SEARCH = """int search(int value) {
    // 顺序查找
    for (int i = 0; i < size; i++) {
        if (data[i] == value) {
            return i;  // 找到，返回索引
        }
    }

    return -1;  // 未找到
}"""

SEQUENTIAL_EXPAND = """void expand() {
    // 计算新容量（1.5倍）
    int newCapacity = capacity * 1.5;

    // 创建新数组
    int* newData = new int[newCapacity];

    // 复制旧数据到新数组
    for (int i = 0; i < size; i++) {
        newData[i] = data[i];
    }

    // 释放旧数组
    delete[] data;

    // 更新指针和容量
    data = newData;
    capacity = newCapacity;
}"""

# ==================== 栈代码模板 ====================
STACK_PUSH = """void push(int value) {
    // 检查栈是否已满
    if (top >= capacity - 1) {
        return;  // 栈满
    }

    // top指针上移
    top++;

    // 入栈
    data[top] = value;
}"""

STACK_POP = """int pop() {
    // 检查栈是否为空
    if (top < 0) {
        return -1;  // 栈空
    }

    // 获取栈顶元素
    int value = data[top];

    // top指针下移
    top--;

    return value;
}"""

STACK_PEEK = """int peek() {
    // 检查栈是否为空
    if (top < 0) {
        return -1;  // 栈空
    }

    // 返回栈顶元素
    return data[top];
}"""

# ==================== 链表代码模板 ====================
LINKED_INSERT_HEAD = """void insertHead(int value) {
    // 创建新节点
    Node* newNode = new Node(value);

    // 新节点指向原头节点
    newNode->next = head;

    // 更新头指针
    head = newNode;
    size++;
}"""

LINKED_INSERT_TAIL = """void insertTail(int value) {
    // 创建新节点
    Node* newNode = new Node(value);

    // 如果链表为空
    if (head == nullptr) {
        head = newNode;
        return;
    }

    // 找到尾节点
    Node* current = head;
    while (current->next != nullptr) {
        current = current->next;
    }

    // 尾节点指向新节点
    current->next = newNode;
    size++;
}"""

LINKED_DELETE = """void deleteAt(int index) {
    // 删除头节点
    if (index == 0) {
        Node* temp = head;
        head = head->next;
        delete temp;
        size--;
        return;
    }

    // 找到要删除节点的前一个节点
    Node* prev = head;
    for (int i = 0; i < index - 1; i++) {
        prev = prev->next;
    }

    // 删除节点
    Node* temp = prev->next;
    prev->next = temp->next;
    delete temp;
    size--;
}"""

LINKED_SEARCH = """int search(int value) {
    Node* current = head;
    int index = 0;

    // 遍历链表查找
    while (current != nullptr) {
        if (current->value == value) {
            return index;  // 找到
        }
        current = current->next;
        index++;
    }

    return -1;  // 未找到
}"""

# ==================== 二叉树代码模板 ====================
BINARY_INSERT = """void insert(int value) {
    // 创建新节点
    Node* newNode = new Node(value);

    // 如果树为空，新节点作为根节点
    if (root == nullptr) {
        root = newNode;
        return;
    }

    // 层序遍历找到第一个空位置
    queue<Node*> q;
    q.push(root);

    while (!q.empty()) {
        Node* current = q.front();
        q.pop();

        // 检查左子节点
        if (current->left == nullptr) {
            current->left = newNode;
            return;
        } else {
            q.push(current->left);
        }

        // 检查右子节点
        if (current->right == nullptr) {
            current->right = newNode;
            return;
        } else {
            q.push(current->right);
        }
    }
}"""

BINARY_DELETE = """void deleteNode(int value) {
    if (root == nullptr) return;

    // 查找目标节点和最后一个节点
    Node* target = nullptr;
    Node* lastNode = nullptr;
    Node* parentOfLast = nullptr;
    queue<pair<Node*, Node*>> q;
    q.push({root, nullptr});

    while (!q.empty()) {
        auto [node, parent] = q.front();
        q.pop();

        if (node->value == value) {
            target = node;
        }

        lastNode = node;
        parentOfLast = parent;

        if (node->left) q.push({node->left, node});
        if (node->right) q.push({node->right, node});
    }

    if (target == nullptr) return;

    // 用最后节点的值替换目标节点
    if (target != lastNode) {
        target->value = lastNode->value;
    }

    // 删除最后一个节点
    if (parentOfLast == nullptr) {
        root = nullptr;
    } else if (parentOfLast->left == lastNode) {
        parentOfLast->left = nullptr;
    } else {
        parentOfLast->right = nullptr;
    }
    delete lastNode;
}"""

BINARY_SEARCH = """bool search(int value) {
    if (root == nullptr) return false;

    // 层序遍历搜索
    queue<Node*> q;
    q.push(root);

    while (!q.empty()) {
        Node* current = q.front();
        q.pop();

        // 检查当前节点
        if (current->value == value) {
            return true;
        }

        if (current->left) q.push(current->left);
        if (current->right) q.push(current->right);
    }

    return false;
}"""

# ==================== BST 代码模板 ====================
BST_INSERT = """void insert(int value) {
    // 空树，创建根节点
    if (root == nullptr) {
        root = new Node(value);
        return;
    }

    // 查找插入位置
    Node* current = root;
    Node* parent = nullptr;

    while (current != nullptr) {
        parent = current;
        if (value < current->value) {
            current = current->left;
        } else {
            current = current->right;
        }
    }

    // 插入新节点
    if (value < parent->value) {
        parent->left = new Node(value);
    } else {
        parent->right = new Node(value);
    }
}"""

BST_SEARCH = """bool search(int value) {
    Node* current = root;

    // 二分查找
    while (current != nullptr) {
        if (value == current->value) {
            return true;  // 找到
        } else if (value < current->value) {
            current = current->left;
        } else {
            current = current->right;
        }
    }

    return false;  // 未找到
}"""

BST_DELETE = """void deleteNode(int value) {
    root = deleteHelper(root, value);
}

Node* deleteHelper(Node* node, int value) {
    if (node == nullptr) return nullptr;

    // 查找要删除的节点
    if (value < node->value) {
        node->left = deleteHelper(node->left, value);
    } else if (value > node->value) {
        node->right = deleteHelper(node->right, value);
    } else {
        // 找到了要删除的节点

        // 情况1: 叶子节点
        if (node->left == nullptr && node->right == nullptr) {
            delete node;
            return nullptr;
        }

        // 情况2: 只有一个子节点
        if (node->left == nullptr) {
            Node* temp = node->right;
            delete node;
            return temp;
        }
        if (node->right == nullptr) {
            Node* temp = node->left;
            delete node;
            return temp;
        }

        // 情况3: 有两个子节点
        // 找到右子树的最小节点
        Node* minNode = findMin(node->right);
        node->value = minNode->value;
        node->right = deleteHelper(node->right, minNode->value);
    }

    return node;
}"""

# ==================== AVL 树代码模板 ====================
AVL_INSERT = """void insert(int value) {
    root = insertHelper(root, value);
}

Node* insertHelper(Node* node, int value) {
    // 标准BST插入
    if (node == nullptr) {
        return new Node(value);
    }

    if (value < node->value) {
        node->left = insertHelper(node->left, value);
    } else {
        node->right = insertHelper(node->right, value);
    }

    // 更新节点高度
    updateHeight(node);

    // 检查平衡因子
    int balance = getBalance(node);

    // LL情况：右旋
    if (balance > 1 && value < node->left->value) {
        return rotateRight(node);
    }

    // RR情况：左旋
    if (balance < -1 && value > node->right->value) {
        return rotateLeft(node);
    }

    // LR情况：先左旋后右旋
    if (balance > 1 && value > node->left->value) {
        node->left = rotateLeft(node->left);
        return rotateRight(node);
    }

    // RL情况：先右旋后左旋
    if (balance < -1 && value < node->right->value) {
        node->right = rotateRight(node->right);
        return rotateLeft(node);
    }

    return node;
}"""

AVL_ROTATE_LEFT = """Node* rotateLeft(Node* y) {
    // 保存节点
    Node* x = y->right;
    Node* T2 = x->left;

    // 执行旋转
    x->left = y;
    y->right = T2;

    // 更新高度
    updateHeight(y);
    updateHeight(x);

    return x;  // 新根节点
}"""

AVL_ROTATE_RIGHT = """Node* rotateRight(Node* x) {
    // 保存节点
    Node* y = x->left;
    Node* T2 = y->right;

    // 执行旋转
    y->right = x;
    x->left = T2;

    // 更新高度
    updateHeight(x);
    updateHeight(y);

    return y;  // 新根节点
}"""

# ==================== 树遍历代码模板 ====================
TREE_TRAVERSAL_INORDER = """void inorder(Node* node) {
    if (node == nullptr) return;

    // 递归左子树
    inorder(node->left);

    // 访问当前节点
    visit(node);

    // 递归右子树
    inorder(node->right);
}"""

TREE_TRAVERSAL_PREORDER = """void preorder(Node* node) {
    if (node == nullptr) return;

    // 访问当前节点
    visit(node);

    // 递归左子树
    preorder(node->left);

    // 递归右子树
    preorder(node->right);
}"""

TREE_TRAVERSAL_POSTORDER = """void postorder(Node* node) {
    if (node == nullptr) return;

    // 递归左子树
    postorder(node->left);

    // 递归右子树
    postorder(node->right);

    // 访问当前节点
    visit(node);
}"""

# 🔄 非递归遍历
TREE_TRAVERSAL_PREORDER_ITERATIVE = """void preorder_iterative(Node* root) {
    if (root == nullptr) return;

    std::stack<Node*> st;
    st.push(root);

    while (!st.empty()) {
        Node* node = st.top(); st.pop();
        visit(node);

        if (node->right) st.push(node->right);
        if (node->left)  st.push(node->left);
    }
}"""

TREE_TRAVERSAL_INORDER_ITERATIVE = """void inorder_iterative(Node* root) {
    std::stack<Node*> st;
    Node* curr = root;

    while (curr != nullptr || !st.empty()) {
        while (curr != nullptr) {
            st.push(curr);
            curr = curr->left;
        }
        curr = st.top(); st.pop();
        visit(curr);
        curr = curr->right;
    }
}"""

TREE_TRAVERSAL_POSTORDER_ITERATIVE = """void postorder_iterative(Node* root) {
    if (root == nullptr) return;

    std::stack<Node*> s1, s2;
    s1.push(root);

    while (!s1.empty()) {
        Node* node = s1.top(); s1.pop();
        s2.push(node);
        if (node->left)  s1.push(node->left);
        if (node->right) s1.push(node->right);
    }

    while (!s2.empty()) {
        visit(s2.top());
        s2.pop();
    }
}"""

TREE_TRAVERSAL_LEVELORDER = """void levelorder(Node* root) {
    if (root == nullptr) return;

    queue<Node*> q;
    q.push(root);

    while (!q.empty()) {
        Node* node = q.front();
        q.pop();

        // 访问当前节点
        visit(node);

        if (node->left) q.push(node->left);
        if (node->right) q.push(node->right);
    }
}"""

# ==================== Huffman 树代码模板 ====================
HUFFMAN_BUILD = """void buildHuffmanTree(map<char, int> frequencies) {
    // 创建最小堆
    priority_queue<Node*, vector<Node*>, Compare> minHeap;

    // 为每个字符创建叶子节点并加入堆
    for (auto& pair : frequencies) {
        Node* node = new Node(pair.first, pair.second);
        minHeap.push(node);
    }

    // 合并节点直到只剩一个根节点
    while (minHeap.size() > 1) {
        // 取出频率最小的两个节点
        Node* left = minHeap.top();
        minHeap.pop();
        Node* right = minHeap.top();
        minHeap.pop();

        // 创建新的内部节点
        int mergedWeight = left->weight + right->weight;
        Node* merged = new Node('\\0', mergedWeight);
        merged->left = left;
        merged->right = right;

        // 将新节点插入堆
        minHeap.push(merged);
    }

    // 最后一个节点就是根节点
    root = minHeap.top();
}"""

HUFFMAN_ENCODE = """string encode(string text) {
    // 检查编码表是否已生成
    if (huffmanCodes.empty()) {
        generateCodes(root, "");
    }

    string encoded = "";

    // 遍历文本，用编码替换每个字符
    for (char c : text) {
        if (huffmanCodes.find(c) != huffmanCodes.end()) {
            encoded += huffmanCodes[c];
        }
    }

    return encoded;
}"""

HUFFMAN_DECODE = """string decode(string encoded) {
    if (root == nullptr) {
        return "";
    }

    string decoded = "";
    Node* current = root;

    // 遍历编码串
    for (char bit : encoded) {
        // 根据位向左或向右移动
        if (bit == '0') {
            current = current->left;
        } else {
            current = current->right;
        }

        // 到达叶子节点，记录字符并返回根节点
        if (current->isLeaf()) {
            decoded += current->value;
            current = root;
        }
    }

    return decoded;
}"""

HUFFMAN_GENERATE_CODES = """void generateCodes(Node* node, string code) {
    if (node == nullptr) return;

    // 如果是叶子节点，记录编码
    if (node->isLeaf()) {
        huffmanCodes[node->value] = code.empty() ? "0" : code;
        return;
    }

    // 递归处理左右子树（左=0，右=1）
    generateCodes(node->left, code + "0");
    generateCodes(node->right, code + "1");
}"""

# ==================== 代码模板映射 ====================
CODE_TEMPLATES = {
    # 顺序表
    'sequential_insert': SEQUENTIAL_INSERT,
    'sequential_delete': SEQUENTIAL_DELETE,
    'sequential_search': SEQUENTIAL_SEARCH,
    'sequential_expand': SEQUENTIAL_EXPAND,

    # 栈
    'stack_push': STACK_PUSH,
    'stack_pop': STACK_POP,
    'stack_peek': STACK_PEEK,

    # 链表
    'linked_insert_head': LINKED_INSERT_HEAD,
    'linked_insert_tail': LINKED_INSERT_TAIL,
    'linked_delete': LINKED_DELETE,
    'linked_search': LINKED_SEARCH,

    # 二叉树
    'binary_insert': BINARY_INSERT,
    'binary_delete': BINARY_DELETE,
    'binary_search': BINARY_SEARCH,

    # BST
    'bst_insert': BST_INSERT,
    'bst_search': BST_SEARCH,
    'bst_delete': BST_DELETE,

    # AVL
    'avl_insert': AVL_INSERT,
    'avl_rotate_left': AVL_ROTATE_LEFT,
    'avl_rotate_right': AVL_ROTATE_RIGHT,

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


def get_code_template(structure_type: str, operation: str) -> tuple:
    """
    获取指定数据结构和操作的代码模板

    Args:
        structure_type: 数据结构类型 (sequential, linked, bst, avl等)
        operation: 操作类型 (insert, delete, search等)

    Returns:
        (code, total_lines): 代码字符串和总行数
    """
    key = f"{structure_type}_{operation}"
    code = CODE_TEMPLATES.get(key, "// 暂无对应代码模板")
    lines = code.split('\n')
    return code, len(lines)


def get_code_lines(code: str) -> list:
    """将代码分割成行数组"""
    return code.split('\n')
