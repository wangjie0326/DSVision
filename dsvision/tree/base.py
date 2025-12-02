from abc import ABC,abstractmethod
from typing import List, Optional, Any
from ..operation.operation import OperationStep, OperationType

class TreeNode:
    """树节点基类"""
    def __init__(self,value:Any):
        self.value = value
        self.left:Optional['TreeNode'] = None
        self.right:Optional['TreeNode'] = None
        self.node_id = id(self)
        self.height = 1 #用于AVL树


class TreeStructureBase(ABC):
    """树结构抽象基类"""
    def __init__(self):
        self._root: Optional[TreeNode] = None
        self._operation_history: List[OperationStep] = []
        self._current_step = -1
        self._size = 0

    @abstractmethod
    def insert(self,value:Any) -> bool:
        """插入节点"""
        pass

    @abstractmethod
    def delete(self,value:Any) -> bool:
        """删除节点"""
        pass

    @abstractmethod
    def search(self,value:Any)-> Optional[TreeNode]:
        """搜索节点"""
        pass

    @abstractmethod
    def get_tree_data(self) -> dict:
        """获取树的结构数据，用于前端可视化"""
        pass

    def size(self)->int:
        """返回树的节点数"""
        return self._size

    def is_empty(self)->bool:
        """判断树是否为空"""
        return self._root is None

    def add_operation_step(self,step:OperationStep) -> None:
        """添加操作步骤"""
        #防止内存溢出
        if len(self._operation_history) > 100:
            self._operation_history = self._operation_history[-50:]  # 只保留最近50条
        self._operation_history.append(step)
        self._current_step += 1

    def get_operation_history(self)->List[OperationStep]:
        """获取操作历史"""
        return self._operation_history.copy()

    def clear_operation_history(self) -> None:
        """清空操作历史"""
        self._operation_history.clear()
        self._current_step = -1

    def _node_to_dict(self, node: Optional[TreeNode])-> Optional[dict]:
        """将节点转换为字典格式"""
        if node is None:
            return None
        result = {
            'value': node.value,
            'node_id': node.node_id,
            'left': self._node_to_dict(node.left),
            'right': self._node_to_dict(node.right),
            'height': getattr(node, 'height', None)
        }
        print(f"调试: 节点 {node.value} 转换为字典: {result}")
        return result

    def inorder_traversal(self) -> List[Any]:
        """中序周游"""
        result = []
        self._inorder_helper(self._root,result)
        return result

    def _inorder_helper(self,node:Optional[TreeNode], result:List[Any])-> None:
        """中序周游辅助函数"""
        if node:
            self._inorder_helper(node.left, result)
            result.append(node.value)
            self._inorder_helper(node.right, result)

    def preorder_traversal(self) -> List[Any]:
        """前序周游"""
        result = []
        self._preorder_helper(self._root,result)
        return result

    def _preorder_helper(self,node:Optional[TreeNode],result:List[Any])-> None:
        """前序周游辅助函数"""
        if node:
            result.append(node.value)
            self._preorder_helper(node.left, result)
            self._preorder_helper(node.right, result)

    def postorder_traversal(self) -> List[Any]:
        """后序周游"""
        result = []
        self._postorder_helper(self._root,result)
        return result

    def _postorder_helper(self,node:Optional[TreeNode],result:List[Any])-> None:
        """后序周游辅助函数"""
        if node:
            self._postorder_helper(node.left, result)
            self._postorder_helper(node.right, result)
            result.append(node.value)

    def level_order_traversal(self) -> List[Any]:
        """宽度优先周游"""
        if not self._root:
            return []
        result = []
        queue = [self._root]

        while queue:
            node = queue.pop(0)
            result.append(node.value)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        return result

    # 🎬 可视化遍历方法（记录OperationStep）
    def traverse_with_animation(self, traversal_type: str) -> List[Any]:
        """
        执行遍历并记录每个节点的访问步骤（用于动画）
        traversal_type: 'preorder' | 'inorder' | 'postorder' | 'levelorder'
        """
        self.clear_operation_history()  # 清空之前的操作历史

        type_names = {
            'preorder': '前序遍历',
            'inorder': '中序遍历',
            'postorder': '后序遍历',
            'levelorder': '层次遍历'
        }

        step = OperationStep(
            OperationType.SEARCH,
            description=f"开始{type_names.get(traversal_type, '遍历')}"
        )
        self.add_operation_step(step)

        result = []

        if traversal_type == 'preorder':
            self._preorder_with_steps(self._root, result)
        elif traversal_type == 'inorder':
            self._inorder_with_steps(self._root, result)
        elif traversal_type == 'postorder':
            self._postorder_with_steps(self._root, result)
        elif traversal_type == 'levelorder':
            self._levelorder_with_steps(result)
        else:
            raise ValueError(f"未知的遍历类型: {traversal_type}")

        step = OperationStep(
            OperationType.SEARCH,
            description=f"{type_names.get(traversal_type)}完成，访问顺序: {result}"
        )
        self.add_operation_step(step)

        return result

    def _preorder_with_steps(self, node: Optional[TreeNode], result: List[Any]) -> None:
        """前序遍历并记录步骤"""
        if node:
            # 访问当前节点
            result.append(node.value)
            step = OperationStep(
                OperationType.SEARCH,
                value=node.value,
                description=f"访问节点: {node.value}",
                highlight_indices=[node.node_id],
                animation_type="highlight",
                duration=1.0,
                code_template='tree_traversal_preorder',
                code_line=5,
                code_highlight=[5]
            )
            self.add_operation_step(step)

            # 递归左子树
            self._preorder_with_steps(node.left, result)
            # 递归右子树
            self._preorder_with_steps(node.right, result)

    def _inorder_with_steps(self, node: Optional[TreeNode], result: List[Any]) -> None:
        """中序遍历并记录步骤"""
        if node:
            # 递归左子树
            self._inorder_with_steps(node.left, result)

            # 访问当前节点
            result.append(node.value)
            step = OperationStep(
                OperationType.SEARCH,
                value=node.value,
                description=f"访问节点: {node.value}",
                highlight_indices=[node.node_id],
                animation_type="highlight",
                duration=1.0,
                code_template='tree_traversal_inorder',
                code_line=8,
                code_highlight=[8]
            )
            self.add_operation_step(step)

            # 递归右子树
            self._inorder_with_steps(node.right, result)

    def _postorder_with_steps(self, node: Optional[TreeNode], result: List[Any]) -> None:
        """后序遍历并记录步骤"""
        if node:
            # 递归左子树
            self._postorder_with_steps(node.left, result)
            # 递归右子树
            self._postorder_with_steps(node.right, result)

            # 访问当前节点
            result.append(node.value)
            step = OperationStep(
                OperationType.SEARCH,
                value=node.value,
                description=f"访问节点: {node.value}",
                highlight_indices=[node.node_id],
                animation_type="highlight",
                duration=1.0,
                code_template='tree_traversal_postorder',
                code_line=11,
                code_highlight=[11]
            )
            self.add_operation_step(step)

    def _levelorder_with_steps(self, result: List[Any]) -> None:
        """层次遍历并记录步骤"""
        if not self._root:
            return

        queue = [self._root]

        while queue:
            node = queue.pop(0)
            result.append(node.value)

            # 访问当前节点
            step = OperationStep(
                OperationType.SEARCH,
                value=node.value,
                description=f"访问节点: {node.value}",
                highlight_indices=[node.node_id],
                animation_type="highlight",
                duration=1.0,
                code_template='tree_traversal_levelorder',
                code_line=12,
                code_highlight=[12]
            )
            self.add_operation_step(step)

            # 将子节点加入队列
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    def get_height(self) -> int:
        """获取树的高度，内部递归"""
        def _height(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            return 1 + max(_height(node.left), _height(node.right))
        return _height(self._root)

    def clear(self)-> None:
        """清空树"""
        self._root = None
        self._size = 0
        self.clear_operation_history()


