from .base import TreeStructureBase,TreeNode
from ..operation.operation import OperationType,OperationStep
from typing import Optional,Any, Dict,List,Tuple

class HuffmanNode(TreeNode):
    """哈夫曼树节点"""
    def __init__(self,value:Any,weight:int):
        super().__init__(value)
        self.weight = weight#权重
        self.is_leaf = True #是否为叶子节点

    def __lt__(self,other):
        """用于堆排序的比较方法"""
        return self.weight < other.weight

    def __repr__(self):
        return f"Huffman({self.value}, freq={self.weight})"

class MinHeap:
    """最小堆实现"""
    def __init__(self):
        self.heap : List[HuffmanNode] = []
        self.size = 0
    def parent(self, i:int) -> int:
        """获取父节点索引"""
        return (i-1)//2

    def left_child(self, i: int) -> int:
        """获取左子节点索引"""
        return 2 * i + 1

    def right_child(self, i: int) -> int:
        """获取右子节点索引"""
        return 2 * i + 2

    def swap(self, i: int, j: int) -> None:
        """交换两个节点"""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def insert(self, node: HuffmanNode) -> None:
        """插入节点到堆中"""
        self.heap.append(node)
        self.size += 1
        self._heapify_up(self.size - 1)

    def _heapify_up(self, i: int) -> None:
        """向上调整堆（上浮）"""
        while i > 0:
            parent_idx = self.parent(i)
            if self.heap[i].weight < self.heap[parent_idx].weight:
                self.swap(i, parent_idx)
                i = parent_idx
            else:
                break

    def extract_min(self) -> Optional[HuffmanNode]:
        """取出并删除最小元素"""
        if self.size == 0:
            return None

        if self.size == 1:
            self.size -= 1
            return self.heap.pop()

        # 保存最小元素
        min_node = self.heap[0]

        # 用最后一个元素替换根节点
        self.heap[0] = self.heap.pop()
        self.size -= 1

        # 向下调整堆
        self._heapify_down(0)

        return min_node

    def _heapify_down(self, i: int) -> None:
        """向下调整堆（下沉）"""
        while True:
            smallest = i
            left = self.left_child(i)
            right = self.right_child(i)

            # 找到当前节点、左子节点、右子节点中最小的
            if left < self.size and self.heap[left].weight < self.heap[smallest].weight:
                smallest = left

            if right < self.size and self.heap[right].weight < self.heap[smallest].weight:
                smallest = right

            # 如果当前节点不是最小的，交换并继续下沉
            if smallest != i:
                self.swap(i, smallest)
                i = smallest
            else:
                break

    def is_empty(self) -> bool:
        """判断堆是否为空"""
        return self.size == 0

    def get_all_sorted(self) -> List[HuffmanNode]:
        """获取堆中所有元素的排序列表（用于显示）"""
        return sorted(self.heap, key=lambda x: x.weight)

class HuffmanTree(TreeStructureBase):
    """哈夫曼树实现"""
    def __init__(self):
        super().__init__()
        self._huffman_codes: Dict[Any,str] = {} #存储哈夫曼编码
        self._root: Optional[HuffmanNode] = None

        step = OperationStep(
            OperationType.INIT,
            description="初始化哈夫曼树"
        )
        self.add_operation_step(step)

    def build_from_weights(self,weights:Dict[Any, int]) -> bool:
        """
        从频率字典构建哈夫曼树
        frequencies: {字符: 频率} 例如 {'A': 5, 'B': 9, 'C': 12}
        """
        if not weights:
            step = OperationStep(
                OperationType.INIT,
                description="构建失败：权重字典为空"
            )
            self.add_operation_step(step)
            return False
        step = OperationStep(
            OperationType.INIT,
            description=f"开始构建哈夫曼树，输入权重: {weights}"
        )
        self.add_operation_step(step)

        #创建初始节点列表
        heap = MinHeap()

        #给每个字符创建叶子节点并插入堆
        for value,wei in weights.items():
            node = HuffmanNode(value,wei)
            heap.insert(node)
            self._size += 1

            step = OperationStep(
                OperationType.INSERT,
                value=value,
                description=f"创建叶子节点: 字符='{value}', 权重={wei}"
            )
            self.add_operation_step(step)

        sorted_nodes = heap.get_all_sorted()
        step = OperationStep(
            OperationType.INIT,
            description=f"初始节点队列（按权重排序）: {[f'{n.value}({n.weight})' for n in sorted_nodes]}"
        )
        self.add_operation_step(step)

        #构建哈夫曼树的主循环
        merge_count = 0
        while heap.size > 1:
            merge_count += 1
            #取出频率最小的两个节点
            left = heap.extract_min()
            right = heap.extract_min()

            step = OperationStep(
                OperationType.INSERT,
                description=f"【第{merge_count}次合并】从堆中取出权重最小的两个节点: "
                            f"左节点='{left.value}'(频率{left.weight}), "
                            f"右节点='{right.value}'(频率{right.weight})"
            )
            self.add_operation_step(step)

            #创建新的内部节点
            merged_wei = left.weight + right.weight
            #内部节点值使用组合标记
            merged_value = f"[{left.value}+{right.value}]"
            merged_node = HuffmanNode(merged_value, merged_wei)
            merged_node.is_leaf = False
            merged_node.left = left
            merged_node.right = right

            self._size += 1
            step = OperationStep(
                OperationType.INSERT,
                value = merged_value,
                description=f"创建新的内部节点: "
                            f"值='{merged_value}', "
                            f"权重={left.weight}+{right.weight}={merged_wei}"
            )
            self.add_operation_step(step)

            step = OperationStep(
                OperationType.INSERT,
                description=f"将新节点插入堆，重新调整堆结构"
            )
            self.add_operation_step(step)

            #显示当前堆的状态
            remaining = heap.get_all_sorted()
            step = OperationStep(
                OperationType.INSERT,
                description=f"当前堆中节点（按权重排序）: {[f'{n.value}({n.weight})' for n in remaining]}"
            )
            self.add_operation_step(step)

        #最后一个节点就是根节点
        if heap.size == 1:
            self._root = heap.extract_min()

        if self._root:
            step = OperationStep(
                OperationType.INIT,
                description=f"哈夫曼树构建完成！"
                            f"根节点权重={self._root.weight}, "
                            f"共{self._size}个节点，"
                            f"进行了{merge_count}次合并操作"
            )
            self.add_operation_step(step)

            # 生成哈夫曼编码
            self._generate_codes()

            return True
        return False

    def build_from_string(self,text:str) -> bool:
        """
        从字符串构建哈夫曼树（自动统计频率）
        text: 输入字符串，例如 "ABRACADABRA"
        """
        if not text:
            step = OperationStep(
                OperationType.INIT,
                description="构建失败：输入文本为空"
            )
            self.add_operation_step(step)
            return False
        step = OperationStep(
            OperationType.INIT,
            description=f"分析输入文本: '{text}' (长度={len(text)})"
        )
        self.add_operation_step(step)

        # 统计字符频率
        frequencies = {}
        for char in text:
            frequencies[char] = frequencies.get(char, 0) + 1

        # 按字符排序显示
        sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
        step = OperationStep(
            OperationType.INIT,
            description=f"字符频率统计完成: {dict(sorted_freq)}"
        )
        self.add_operation_step(step)

        # 使用频率字典构建树
        return self.build_from_weights(frequencies)

    def _generate_codes(self) -> None:
        """生成哈夫曼编码"""
        self._huffman_codes = {}

        step = OperationStep(
            OperationType.INIT,
            description="开始生成哈夫曼编码(规则:左分支=0, 右分支=1)"
        )
        self.add_operation_step(step)

        if self._root is None:
            return

        self._generate_codes_helper(self._root, "")

        # 计算平均编码长度
        if self._huffman_codes and self._root:
            total_freq = self._root.weight
            avg_length = sum(len(code) * self._get_node_weight(char)
                             for char, code in self._huffman_codes.items()) / total_freq

            step = OperationStep(
                OperationType.INIT,
                description=f"哈夫曼编码生成完成,编码表: {self._huffman_codes}, "
                            f"平均编码长度: {avg_length:.2f}位"
            )
            self.add_operation_step(step)

    def _generate_codes_helper(self, node: Optional[HuffmanNode], code: str) -> None:
        """递归辅助方法"""
        if node is None:
            return

        # 如果是叶子节点,记录编码
        if node.is_leaf:
            final_code = code if code else "0"
            self._huffman_codes[node.value] = final_code
            step = OperationStep(
                OperationType.SEARCH,
                value=node.value,
                description=f"字符 '{node.value}' (频率={node.weight}) 的编码为: {final_code}"
            )
            self.add_operation_step(step)
            return

        # 递归处理左右子树
        if node.left:
            self._generate_codes_helper(node.left, code + "0")
        if node.right:
            self._generate_codes_helper(node.right, code + "1")

    def _get_node_weight(self, value: Any) -> int:
        """获取指定值的节点权重"""
        node = self._search_recursive(self._root, value)
        return node.weight if node else 0

    def encode(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        使用哈夫曼编码压缩文本
        返回: (编码后的二进制字符串, 统计信息)
        """
        if not self._huffman_codes:
            raise ValueError("哈夫曼树未构建或编码未生成")
        step = OperationStep(
            OperationType.SEARCH,
            description=f"开始编码文本: '{text}'"
        )
        self.add_operation_step(step)

        encoded = ""
        for char in text:
            if char in self._huffman_codes:
                encoded += self._huffman_codes[char]

        original_bits = len(text) * 8  # ASCII编码（8位/字符）
        compressed_bits = len(encoded)
        compression_ratio = (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0

        stats = {
            'original_length': len(text),
            'original_bits': original_bits,
            'compressed_bits': compressed_bits,
            'compression_ratio': f"{compression_ratio:.2f}%",
            'savings_bits': original_bits - compressed_bits
        }

        step = OperationStep(
            OperationType.SEARCH,
            description=f"编码完成，结果: {encoded[:50]}{'...' if len(encoded) > 50 else ''}\n"
                        f"原始大小: {original_bits}位，经压缩后: {compressed_bits}位, "
                        f"节省: {stats['savings_bits']}位, "
                        f"压缩率: {compression_ratio:.2f}%"
        )
        self.add_operation_step(step)

        return encoded, stats

    def decode(self, encoded: str) -> str:
        """
        解码哈夫曼编码
        encoded: 二进制字符串
        """
        if not self._root:
            raise ValueError("哈夫曼树未构建")

        step = OperationStep(
            OperationType.SEARCH,
            description=f"开始解码二进制串: {encoded[:50]}{'...' if len(encoded) > 50 else ''} (长度={len(encoded)}位)"
        )
        self.add_operation_step(step)

        decoded = ""
        current = self._root
        path = ""

        for i, bit in enumerate(encoded):
            path += bit

            # 根据位向左或向右移动
            if bit == '0':
                current = current.left
            else:
                current = current.right

            # 到达叶子节点，记录字符并返回根节点
            if current and current.is_leaf:
                decoded += str(current.value)

                step = OperationStep(
                    OperationType.SEARCH,
                    value=current.value,
                    description=f"路径 '{path}' → 解码为字符 '{current.value}'"
                )
                self.add_operation_step(step)

                current = self._root
                path = ""

        step = OperationStep(
            OperationType.SEARCH,
            description=f"✓ 解码完成，结果: '{decoded}'"
        )
        self.add_operation_step(step)

        return decoded

    def get_huffman_codes(self) -> Dict[Any, str]:
        """获取哈夫曼编码表"""
        return self._huffman_codes.copy()

    def get_tree_data(self) -> dict:
        """获取树的结构数据，用于前端可视化"""
        return {
            'root': self._node_to_dict_huffman(self._root),
            'size': self._size,
            'height': self.get_height(),
            'huffman_codes': self._huffman_codes,
            'traversals': {
                'inorder': self.inorder_traversal(),
                'preorder': self.preorder_traversal(),
                'postorder': self.postorder_traversal(),
                'levelorder': self.level_order_traversal()
            }
        }

    def _node_to_dict_huffman(self, node: Optional[HuffmanNode]) -> Optional[dict]:
        """将哈夫曼节点转换为字典格式（包含权重信息）"""
        if node is None:
            return None
        return {
            'value': node.value,
            'weight': node.weight,
            'is_leaf': node.is_leaf,
            'node_id': node.node_id,
            'left': self._node_to_dict_huffman(node.left),
            'right': self._node_to_dict_huffman(node.right)
        }

    #实现抽象方法（不常用这些操作）
    def insert(self, value: Any) -> bool:
        """哈夫曼树不支持单个插入，使用build_from_weights"""
        step = OperationStep(
            OperationType.INSERT,
            description="提示：哈夫曼树不支持单个节点插入"
        )
        self.add_operation_step(step)
        return False

    def delete(self, value: Any) -> bool:
        """哈夫曼树不支持删除操作"""
        step = OperationStep(
            OperationType.DELETE,
            description="提示：哈夫曼树不支持删除操作"
        )
        self.add_operation_step(step)
        return False

    def search(self, value: Any) -> Optional[TreeNode]:
        """搜索指定值的节点"""
        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f"开始在哈夫曼树中搜索节点 '{value}'"
        )
        self.add_operation_step(step)

        result = self._search_recursive(self._root, value)

        if result is None:
            step = OperationStep(
                OperationType.SEARCH,
                value=value,
                description=f"未找到节点 '{value}'"
            )
            self.add_operation_step(step)

        return result

    def _search_recursive(self, node: Optional[HuffmanNode], value: Any) -> Optional[HuffmanNode]:
        """递归搜索节点"""
        if node is None:
            return None

        if node.value == value:
            step = OperationStep(
                OperationType.SEARCH,
                value=value,
                description=f"找到节点 '{value}' (权重={node.weight}, "
                            f"{'叶子节点' if node.is_leaf else '内部节点'})"
            )
            self.add_operation_step(step)
            return node

        # 搜索左右子树
        left_result = self._search_recursive(node.left, value)
        if left_result:
            return left_result

        return self._search_recursive(node.right, value)

