from .base import TreeStructureBase,TreeNode
from ..operation.operation import OperationStep, OperationType
from typing import Optional,Any,List

class BinarySearchTree(TreeStructureBase):
    """二叉搜索树实现"""
    def __init__(self):
        super().__init__()
        step = OperationStep(
            OperationType.INIT,
            description = "初始化二叉搜索树"
        )
        self.add_operation_step(step)

    def insert(self, value:Any) -> bool:
        """插入节点"""
        # # 统一转换为整数类型(如果可能)
        # try:
        #     value = int(value)
        # except (ValueError, TypeError):
        #     step = OperationStep(
        #         OperationType.INSERT,
        #         value=value,
        #         description=f"插入失败：值'{value}'无法转换为数字"
        #     )
        #     self.add_operation_step(step)
        #     return False  # 添加这个返回，拒绝非数字

        step = OperationStep(
            OperationType.INSERT,
            value = value,
            description = f"准备插入节点{value}"
        )
        self.add_operation_step(step)

        if self._root is None:
            self._root = TreeNode(value)
            self._size += 1
            step = OperationStep(
                OperationType.INSERT,
                value=value,
                description=f"插入节点 {value} 作为根节点"
            )
            self.add_operation_step(step)
            return True

        self._root = self._insert_recursive(self._root, value)
        return True

    # binary_search_tree.py
    def _insert_recursive(self, node: Optional[TreeNode], value: Any, path: str = "root") -> Optional[TreeNode]:
        """递归插入 - 详细过程版"""

        if node is None:
            # 找到插入位置
            self._size += 1
            step = OperationStep(
                OperationType.CREATE_NODE,
                description=f'在 {path} 创建新节点 {value}',
                value=value,
                animation_type="fade",
                duration=0.5
            )
            self.add_operation_step(step)
            return TreeNode(value)

        # === 比较当前节点 ===
        step = OperationStep(
            OperationType.COMPARE,
            description=f'在 {path} 比较: {value} vs {node.value}',
            value=value,
            node_id=node.node_id,
            compare_indices=[],
            animation_type="highlight",
            duration=0.4
        )
        self.add_operation_step(step)

        if value < node.value:
            # === 向左遍历 ===
            step = OperationStep(
                OperationType.TRAVERSE_LEFT,
                description=f'{value} < {node.value}, 向左子树移动',
                value=value,
                node_id=node.node_id,
                animation_type="move",
                duration=0.5
            )
            self.add_operation_step(step)

            node.left = self._insert_recursive(node.left, value, f"{path} → left")

        elif value > node.value:
            # === 向右遍历 ===
            step = OperationStep(
                OperationType.TRAVERSE_RIGHT,
                description=f'{value} > {node.value}, 向右子树移动',
                value=value,
                node_id=node.node_id,
                animation_type="move",
                duration=0.5
            )
            self.add_operation_step(step)

            node.right = self._insert_recursive(node.right, value, f"{path} → right")

        else:
            # === 值已存在 ===
            step = OperationStep(
                OperationType.COMPARE,
                description=f'节点 {value} 已存在,不插入',
                value=value,
                node_id=node.node_id,
                animation_type="highlight",
                duration=0.5
            )
            self.add_operation_step(step)

        return node

    def search(self, value:Any) -> Optional[TreeNode]:
        """搜索节点"""
        step = OperationStep(
            OperationType.SEARCH,
            value = value,
            description=f"开始搜索节点{value}"
        )
        self.add_operation_step(step)
        return self._search_recursive(self._root, value)

    def _search_recursive(self, node:Optional[TreeNode], value:Any) -> Optional[TreeNode]:
        """递归搜索辅助函数"""
        if node is None:
            step = OperationStep(
                OperationType.SEARCH,
                value=value,
                description=f"未找到节点 {value}"
            )
            self.add_operation_step(step)
            return None

        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f"检查节点 {node.value}"
        )
        self.add_operation_step(step)

        if value == node.value:
            step = OperationStep(
                OperationType.SEARCH,
                value=value,
                description=f"找到目标节点{value}"
            )
            self.add_operation_step(step)
            return node
        elif value < node.value:
            step = OperationStep(
                OperationType.SEARCH,
                value=value,
                description=f"{value} < {node.value}，向左子树搜索"
            )
            self.add_operation_step(step)
            return self._search_recursive(node.left, value)
        else:
            step = OperationStep(
                OperationType.SEARCH,
                value=value,
                description=f"{value} > {node.value}，向右子树搜索"
            )
            self.add_operation_step(step)
            return self._search_recursive(node.right, value)

    def delete(self,value:Any) -> bool:
        """删除节点"""
        step = OperationStep(
            operation=OperationType.DELETE,
            value=value,
            description=f"开始删除节点{value}"
        )
        self.add_operation_step(step)

        if self._root is None:
            step = OperationStep(
                operation=OperationType.DELETE,
                value=value,
                description="删除失败：树为空"
            )
            self.add_operation_step(step)
            return False
        original_size = self._size
        self._root = self._delete_recursive(self._root, value)

        if self._size < original_size:
            step = OperationStep(
                operation=OperationType.DELETE,
                value=value,
                description=f"成功删除节点 {value}"
            )
            self.add_operation_step(step)
            return True
        else:
            step = OperationStep(
                OperationType.DELETE,
                value=value,
                description=f"删除失败：未找到节点 {value}"
            )
            self.add_operation_step(step)
            return False

    def _delete_recursive(self, node: Optional[TreeNode], value: Any) -> Optional[TreeNode]:
        """递归删除辅助函数"""
        if node is None:
            return None

        if value < node.value:
            step = OperationStep(
                OperationType.DELETE,
                value=value,
                description=f"{value} < {node.value}，向左子树搜索"
            )
            self.add_operation_step(step)
            node.left = self._delete_recursive(node.left, value)
        elif value > node.value:
            step = OperationStep(
                OperationType.DELETE,
                value=value,
                description=f"{value} > {node.value}，向右子树搜索"
            )
            self.add_operation_step(step)
            node.right = self._delete_recursive(node.right, value)
        else:
            step = OperationStep(
                OperationType.DELETE,
                value=value,
                description=f"找到目标节点{value}"
            )
            self.add_operation_step(step)

            #情况1 叶子节点只有一个子节点
            if node.left is None:
                step = OperationStep(
                    OperationType.DELETE,
                    value=value,
                    description=f"节点 {value} 没有左子树，用右子树替代"
                )
                self.add_operation_step(step)
                self._size -= 1
                return node.right
            elif node.right is None:
                step = OperationStep(
                    OperationType.DELETE,
                    value=value,
                    description=f"节点 {value} 没有右子树，用左子树替代"
                )
                self.add_operation_step(step)
                self._size -= 1
                return node.left

            #情况2 有两个子节点
            step = OperationStep(
                OperationType.DELETE,
                value=value,
                description=f"节点 {value} 有两个子节点，查找右子树最小值"
            )
            self.add_operation_step(step)

            #找到右子树的最小节点
            min_node = self._find_min(node.right)
            step = OperationStep(
                OperationType.DELETE,
                value=value,
                description=f"用右子树最小值 {min_node.value} 替换 {value}"
            )
            self.add_operation_step(step)

            #用右子树最小值替换当前节点
            node.value = min_node.value
            #删除右子树的最小节点
            node.right = self._delete_recursive(node.right, min_node.value)

        return node

    def _find_min(self, node:TreeNode) -> TreeNode:
        """找到子树中的最小节点"""
        while node.left is not None:
            node = node.left
        return node

    def _find_max(self, node:TreeNode) -> TreeNode:
        """找到子树中的最大节点"""
        while node.right is not None:
            node = node.right
        return node

    def get_min(self) -> Optional[Any]:
        """获取树中最小值"""
        if self._root is None:
            return None
        return self._find_min(self._root).value

    def get_max(self) -> Optional[Any]:
        """获取树中最大值"""
        if self._root is None:
            return None
        return self._find_max(self._root).value

    def get_tree_data(self) -> dict:
        """获取树的结构数据，用于前端可视化"""
        return {
            'root': self._node_to_dict(self._root),
            'size': self._size,
            'height': self.get_height(),
            'min': self.get_min(),
            'max': self.get_max(),
            'traversals': {
                'inorder': self.inorder_traversal(),
                'preorder': self.preorder_traversal(),
                'postorder': self.postorder_traversal(),
                'levelorder': self.level_order_traversal()
            }
        }

    def build_from_list(self, values: List[Any]) -> bool:
        """从列表构建BST"""
        if not values:
            return False

        step = OperationStep(
            OperationType.INIT,
            description=f"从列表构建二叉搜索树: {values}"
        )
        self.add_operation_step(step)

        for value in values:
            self.insert(value)

        step = OperationStep(
            OperationType.INIT,
            description=f"成功构建二叉搜索树，共 {self._size} 个节点"
        )
        self.add_operation_step(step)
        return True


