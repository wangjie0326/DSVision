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
        # 🔥 清空操作历史，避免累积之前的操作
        self._operation_history = []

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

        # 标记开始插入,用于在递归中只显示一次虚线节点
        self._just_inserted = False
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
        """右旋转 - 带中间步骤的详细动画"""
        # 第1步：标记需要旋转的节点（红色高亮）
        step = OperationStep(
            OperationType.ROTATE_RIGHT,
            description=f"🔄 开始右旋转：节点{z.value}向右旋转",
            tree_snapshot={
                'root': self._node_to_dict(self._root),
                'size': self._size,
                'height': self.get_height()
            },
            highlight_indices=[z.node_id, z.left.node_id],  # 高亮要旋转的两个节点
            animation_type="rotate",
            duration=1.0,
            code_template='avl_rotate_right',
            code_line=2,
            code_highlight=[2, 3, 4]
        )
        self.add_operation_step(step)

        y = z.left
        T3 = y.right

        # 第2步：显示T3子树将被移动
        if T3:
            step = OperationStep(
                OperationType.UPDATE,
                description=f"移动T3子树：从节点{y.value}右侧移到节点{z.value}左侧",
                tree_snapshot={
                    'root': self._node_to_dict(self._root),
                    'size': self._size,
                    'height': self.get_height()
                },
                highlight_indices=[T3.node_id],
                animation_type="move",
                duration=0.8
            )
            self.add_operation_step(step)

        # 执行旋转
        y.right = z
        z.left = T3

        # 更新高度
        self._update_height(z)
        self._update_height(y)

        # 第3步：显示旋转完成后的结果（带过渡动画）
        step = OperationStep(
            OperationType.UPDATE,
            description=f"✅ 右旋转完成，{y.value}成为新的根节点",
            tree_snapshot={
                'root': self._node_to_dict(y),  # 🔥 使用新的根节点y
                'size': self._size,
                'height': self.get_height()
            },
            highlight_indices=[y.node_id],
            animation_type="settle",
            duration=0.6,
            code_template='avl_rotate_right',
            code_line=12,
            code_highlight=[6, 7, 10, 11, 12]
        )
        self.add_operation_step(step)

        return y

    def _rotate_left(self, z: TreeNode) -> TreeNode:
        """左旋转 - 带中间步骤的详细动画"""
        # 第1步：标记需要旋转的节点（红色高亮）
        step = OperationStep(
            OperationType.ROTATE_LEFT,
            description=f"🔄 开始左旋转：节点{z.value}向左旋转",
            tree_snapshot={
                'root': self._node_to_dict(self._root),
                'size': self._size,
                'height': self.get_height()
            },
            highlight_indices=[z.node_id, z.right.node_id],  # 高亮要旋转的两个节点
            animation_type="rotate",
            duration=1.0,
            code_template='avl_rotate_left',
            code_line=2,
            code_highlight=[2, 3, 4]
        )
        self.add_operation_step(step)

        y = z.right
        T2 = y.left

        # 第2步：显示T2子树将被移动
        if T2:
            step = OperationStep(
                OperationType.UPDATE,
                description=f"移动T2子树：从节点{y.value}左侧移到节点{z.value}右侧",
                tree_snapshot={
                    'root': self._node_to_dict(self._root),
                    'size': self._size,
                    'height': self.get_height()
                },
                highlight_indices=[T2.node_id],
                animation_type="move",
                duration=0.8
            )
            self.add_operation_step(step)

        # 执行旋转
        y.left = z
        z.right = T2

        # 更新高度
        self._update_height(z)
        self._update_height(y)

        # 第3步：显示旋转完成后的结果（带过渡动画）
        step = OperationStep(
            OperationType.UPDATE,
            description=f"✅ 左旋转完成，{y.value}成为新的根节点",
            tree_snapshot={
                'root': self._node_to_dict(y),  # 🔥 使用新的根节点y
                'size': self._size,
                'height': self.get_height()
            },
            highlight_indices=[y.node_id],
            animation_type="settle",
            duration=0.6
        )
        self.add_operation_step(step)

        return y

    def _insert_recursive(self, node: Optional[TreeNode], value: Any) -> TreeNode:
        """递归插入并保持平衡"""
        # 1. 执行标准BST插入
        if node is None:
            self._size += 1
            new_node = TreeNode(value)
            self._just_inserted = True  # 标记刚插入了新节点
            return new_node

        if value < node.value:
            node.left = self._insert_recursive(node.left, value)
        elif value > node.value:
            node.right = self._insert_recursive(node.right, value)
        else:
            # 值已存在
            return node

        # 2. 更新当前节点高度
        self._update_height(node)

        # 🔥 只在刚插入新节点后的第一次回溯时显示虚线节点
        if hasattr(self, '_just_inserted') and self._just_inserted:
            self._just_inserted = False  # 只显示一次
            inserted_node = self._find_node_by_value(self._root, value)
            if inserted_node:
                # 步骤1: 显示浅绿色脉冲（BST位置）
                step = OperationStep(
                    OperationType.UPDATE,
                    description=f"✏️ 节点{value}已按BST规则插入",
                    tree_snapshot={
                        'root': self._node_to_dict(self._root),
                        'size': self._size,
                        'height': self.get_height()
                    },
                    highlight_indices=[inserted_node.node_id],
                    animation_type="pulse",  # 明确表示脉冲动画
                    duration=0.8
                )
                self.add_operation_step(step)

        # 3. 获取平衡因子
        balance = self._get_balance(node)

        # 🔥 获取新插入的节点引用（用于后续确认步骤）
        inserted_node = self._find_node_by_value(self._root, value) if hasattr(self, '_just_inserted') or True else None

        # 4. 检查是否需要旋转
        # Left Left Case
        if balance > 1 and value < node.left.value:
            # 步骤2: 检测不平衡并提示需要旋转
            step = OperationStep(
                OperationType.UPDATE,
                description=f"⚠️ 检测到LL失衡：节点{node.value}平衡因子={balance}，左子树过高，需要右旋",
                tree_snapshot={
                    'root': self._node_to_dict(self._root),
                    'size': self._size,
                    'height': self.get_height()
                },
                highlight_indices=[node.node_id],  # 高亮失衡节点
                animation_type="warning",
                duration=0.8
            )
            self.add_operation_step(step)

            # 执行旋转
            new_root = self._rotate_right(node)

            # 步骤3: 旋转完成后，确认新插入的节点为深绿色
            if inserted_node:
                step = OperationStep(
                    OperationType.UPDATE,
                    description=f"✅ 旋转完成，节点{value}已确认插入",
                    tree_snapshot={
                        'root': self._node_to_dict(new_root),
                        'size': self._size,
                        'height': self.get_height()
                    },
                    highlight_indices=[inserted_node.node_id],
                    animation_type="confirm",  # 停止脉冲，变深绿色
                    duration=0.5
                )
                self.add_operation_step(step)

            return new_root

        # Right Right Case
        elif balance < -1 and value > node.right.value:
            # 步骤2: 检测不平衡并提示需要旋转
            step = OperationStep(
                OperationType.UPDATE,
                description=f"⚠️ 检测到RR失衡：节点{node.value}平衡因子={balance}，右子树过高，需要左旋",
                tree_snapshot={
                    'root': self._node_to_dict(self._root),
                    'size': self._size,
                    'height': self.get_height()
                },
                highlight_indices=[node.node_id],  # 高亮失衡节点
                animation_type="warning",
                duration=0.8
            )
            self.add_operation_step(step)

            # 执行旋转
            new_root = self._rotate_left(node)

            # 步骤3: 旋转完成后，确认新插入的节点为深绿色
            if inserted_node:
                step = OperationStep(
                    OperationType.UPDATE,
                    description=f"✅ 旋转完成，节点{value}已确认插入",
                    tree_snapshot={
                        'root': self._node_to_dict(new_root),
                        'size': self._size,
                        'height': self.get_height()
                    },
                    highlight_indices=[inserted_node.node_id],
                    animation_type="confirm",  # 停止脉冲，变深绿色
                    duration=0.5
                )
                self.add_operation_step(step)

            return new_root

        # Left Right Case
        elif balance > 1 and value > node.left.value:
            # 步骤2: 检测不平衡并提示需要旋转
            step = OperationStep(
                OperationType.UPDATE,
                description=f"⚠️ 检测到LR失衡：节点{node.value}平衡因子={balance}，需要先左旋后右旋",
                tree_snapshot={
                    'root': self._node_to_dict(self._root),
                    'size': self._size,
                    'height': self.get_height()
                },
                highlight_indices=[node.node_id],  # 高亮失衡节点
                animation_type="warning",
                duration=0.8
            )
            self.add_operation_step(step)

            # 执行双旋转
            node.left = self._rotate_left(node.left)
            new_root = self._rotate_right(node)

            # 步骤3: 旋转完成后，确认新插入的节点为深绿色
            if inserted_node:
                step = OperationStep(
                    OperationType.UPDATE,
                    description=f"✅ 旋转完成，节点{value}已确认插入",
                    tree_snapshot={
                        'root': self._node_to_dict(new_root),
                        'size': self._size,
                        'height': self.get_height()
                    },
                    highlight_indices=[inserted_node.node_id],
                    animation_type="confirm",  # 停止脉冲，变深绿色
                    duration=0.5
                )
                self.add_operation_step(step)

            return new_root

        # Right Left Case
        elif balance < -1 and value < node.right.value:
            # 步骤2: 检测不平衡并提示需要旋转
            step = OperationStep(
                OperationType.UPDATE,
                description=f"⚠️ 检测到RL失衡：节点{node.value}平衡因子={balance}，需要先右旋后左旋",
                tree_snapshot={
                    'root': self._node_to_dict(self._root),
                    'size': self._size,
                    'height': self.get_height()
                },
                highlight_indices=[node.node_id],  # 高亮失衡节点
                animation_type="warning",
                duration=0.8
            )
            self.add_operation_step(step)

            # 执行双旋转
            node.right = self._rotate_right(node.right)
            new_root = self._rotate_left(node)

            # 步骤3: 旋转完成后，确认新插入的节点为深绿色
            if inserted_node:
                step = OperationStep(
                    OperationType.UPDATE,
                    description=f"✅ 旋转完成，节点{value}已确认插入",
                    tree_snapshot={
                        'root': self._node_to_dict(new_root),
                        'size': self._size,
                        'height': self.get_height()
                    },
                    highlight_indices=[inserted_node.node_id],
                    animation_type="confirm",  # 停止脉冲，变深绿色
                    duration=0.5
                )
                self.add_operation_step(step)

            return new_root

        # 平衡的情况：直接确认节点为深绿色
        else:
            # 步骤2: 停止脉冲，确认节点（深绿色） - 树已平衡
            if inserted_node:
                step = OperationStep(
                    OperationType.UPDATE,
                    description=f"✅ 节点{value}已确认插入，节点{node.value}平衡因子为{balance}，树保持平衡",
                    tree_snapshot={
                        'root': self._node_to_dict(self._root),
                        'size': self._size,
                        'height': self.get_height()
                    },
                    highlight_indices=[inserted_node.node_id],
                    animation_type="confirm",  # 停止脉冲，变深绿色
                    duration=0.6
                )
                self.add_operation_step(step)

        return node

    def _find_node_by_value(self, node: Optional[TreeNode], value: Any) -> Optional[TreeNode]:
        """根据值查找节点"""
        if node is None:
            return None
        if node.value == value:
            return node

        left_result = self._find_node_by_value(node.left, value)
        if left_result:
            return left_result

        return self._find_node_by_value(node.right, value)

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