from .binary_search_tree import BinarySearchTree
from .base import TreeNode
from ..operation.operation import OperationStep, OperationType
from typing import Optional, Any


class AVLTree(BinarySearchTree):
    """AVL树实现（自平衡二叉搜索树）"""

    def __init__(self):
        super().__init__()
        step = OperationStep(
            OperationType.INIT,
            description="初始化AVL树"
        )
        self.add_operation_step(step)

    def insert(self, value: Any) -> bool:
        """插入节点"""
        # 类型检查
        try:
            value = int(value)
        except (ValueError, TypeError):
            step = OperationStep(
                OperationType.INSERT,
                value=value,
                description=f"插入失败：值'{value}'无法转换为数字"
            )
            self.add_operation_step(step)
            return False

        step = OperationStep(
            OperationType.INSERT,
            value=value,
            description=f"准备插入节点{value}到AVL树"
        )
        self.add_operation_step(step)

        if self._root is None:
            self._root = TreeNode(value)
            self._size += 1
            return True

        # 调用AVL的递归插入，不是BST的
        self._root = self._insert_recursive(self._root, value)
        return True

    def _get_height(self, node: Optional[TreeNode]) -> int:
        """获取节点高度"""
        if node is None:
            return 0
        return node.height

    def _update_height(self, node: TreeNode) -> None:
        """更新节点高度"""
        if node:
            node.height = 1 + max(self._get_height(node.left),
                                  self._get_height(node.right))

    def _get_balance(self, node: Optional[TreeNode]) -> int:
        """获取平衡因子"""
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, z: TreeNode) -> TreeNode:
        """右旋转"""
        step = OperationStep(
            OperationType.UPDATE,
            value=z.value,
            description=f"对节点{z.value}进行右旋转"
        )
        self.add_operation_step(step)

        y = z.left
        T3 = y.right

        # 执行旋转
        y.right = z
        z.left = T3

        # 更新高度
        self._update_height(z)
        self._update_height(y)

        step = OperationStep(
            OperationType.UPDATE,
            value=y.value,
            description=f"右旋转完成，新根节点为{y.value}"
        )
        self.add_operation_step(step)

        return y

    def _rotate_left(self, z: TreeNode) -> TreeNode:
        """左旋转"""
        step = OperationStep(
            OperationType.UPDATE,
            value=z.value,
            description=f"对节点{z.value}进行左旋转"
        )
        self.add_operation_step(step)

        y = z.right
        T2 = y.left

        # 执行旋转
        y.left = z
        z.right = T2

        # 更新高度
        self._update_height(z)
        self._update_height(y)

        step = OperationStep(
            OperationType.UPDATE,
            value=y.value,
            description=f"左旋转完成，新根节点为{y.value}"
        )
        self.add_operation_step(step)

        return y

    def _insert_recursive(self, node: Optional[TreeNode], value: Any) -> TreeNode:
        """递归插入并保持平衡"""
        # 1. 执行标准BST插入
        if node is None:
            self._size += 1
            step = OperationStep(
                OperationType.INSERT,
                value=value,
                description=f"找到插入位置，插入节点{value}"
            )
            self.add_operation_step(step)
            return TreeNode(value)

        if value < node.value:
            node.left = self._insert_recursive(node.left, value)
        elif value > node.value:
            node.right = self._insert_recursive(node.right, value)
        else:
            # 值已存在
            return node

        # 2. 更新当前节点高度
        self._update_height(node)

        # 3. 获取平衡因子
        balance = self._get_balance(node)

        step = OperationStep(
            OperationType.UPDATE,
            value=node.value,
            description=f"节点{node.value}的平衡因子为{balance}"
        )
        self.add_operation_step(step)

        # 4. 如果不平衡，进行旋转
        # Left Left Case
        if balance > 1 and value < node.left.value:
            step = OperationStep(
                OperationType.UPDATE,
                description=f"检测到LL失衡，在节点{node.value}处"
            )
            self.add_operation_step(step)
            return self._rotate_right(node)

        # Right Right Case
        if balance < -1 and value > node.right.value:
            step = OperationStep(
                OperationType.UPDATE,
                description=f"检测到RR失衡，在节点{node.value}处"
            )
            self.add_operation_step(step)
            return self._rotate_left(node)

        # Left Right Case
        if balance > 1 and value > node.left.value:
            step = OperationStep(
                OperationType.UPDATE,
                description=f"检测到LR失衡，在节点{node.value}处"
            )
            self.add_operation_step(step)
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right Left Case
        if balance < -1 and value < node.right.value:
            step = OperationStep(
                OperationType.UPDATE,
                description=f"检测到RL失衡，在节点{node.value}处"
            )
            self.add_operation_step(step)
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _delete_recursive(self, node: Optional[TreeNode], value: Any) -> Optional[TreeNode]:
        """递归删除并保持平衡"""
        # 1. 执行标准BST删除
        if node is None:
            return None

        if value < node.value:
            node.left = self._delete_recursive(node.left, value)
        elif value > node.value:
            node.right = self._delete_recursive(node.right, value)
        else:
            # 找到要删除的节点
            if node.left is None:
                self._size -= 1
                return node.right
            elif node.right is None:
                self._size -= 1
                return node.left

            # 有两个子节点
            min_node = self._find_min(node.right)
            node.value = min_node.value
            node.right = self._delete_recursive(node.right, min_node.value)

        if node is None:
            return node

        # 2. 更新高度
        self._update_height(node)

        # 3. 获取平衡因子
        balance = self._get_balance(node)

        # 4. 如果不平衡，进行旋转
        # Left Left Case
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)

        # Left Right Case
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right Right Case
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)

        # Right Left Case
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def get_tree_data(self) -> dict:
        """获取AVL树数据"""
        data = super().get_tree_data()
        data['is_avl'] = True
        return data