from .base import TreeStructureBase, TreeNode
from ..operation.operation import OperationStep, OperationType
from typing import Optional, Any, List

class BinaryTree(TreeStructureBase):
    """"二叉树（链式存储）实现"""
    def __init__(self):
        super().__init__()
        step = OperationStep(
            OperationType.INIT,
            description = "初始化二叉树"
        )
        self.add_operation_step(step)

    def insert(self, value:Any) -> bool:
        """按层序方法插入节点"""
        step = OperationStep(
            OperationType.INSERT,
            value = value,
            description = f"准备插入节点{value}"
        )
        self.add_operation_step(step)

        new_node = TreeNode(value)

        if self._root is None:
            self._root = new_node
            self._size += 1
            print(f"插入 {value} 作为根节点")
            step = OperationStep(
                OperationType.INSERT,
                value = value,
                description = f'插入节点{value}作为根节点'
            )
            self.add_operation_step(step)
            return True

        #宽度周游找到第一个空位置
        queue = [self._root]
        while queue:
            node = queue.pop(0)

            print(f"检查节点: {node.value}, left={node.left}, right={node.right}")

            if node.left is None:
                node.left = new_node
                print(f"插入 {value} 到 {node.value}.left")
                self._size += 1
                step = OperationStep(
                    OperationType.INSERT,
                    value = value,
                    description = f'将节点{value}插入为节点{node.value}的左子节点'
                )
                self.add_operation_step(step)
                return True
            else:
                queue.append(node.left)

            if node.right is None:
                node.right = new_node
                print(f"插入 {value} 到 {node.value}.right")
                self._size += 1
                step = OperationStep(
                    OperationType.INSERT,
                    value = value,
                    description = f'将节点{value}插入为节点{node.value}的右子节点'
                )
                self.add_operation_step(step)
                return True
            else:
                queue.append(node.right)

        return False

    def delete(self, value:Any) -> bool:
        """删除指定值的节点"""
        if self._root is None:
            step = OperationStep(
                OperationType.DELETE,
                value = value,
                description = "删除失败：树为空"
            )
            self.add_operation_step(step)
            return False
        step = OperationStep(
            OperationType.DELETE,
            value = value,
            description = f"开始查找并删除节点{value}"
        )
        self.add_operation_step(step)

        #找到要删除的节点和最后一个节点
        target_node = None
        last_node = None
        parent_of_last = None
        queue = [(self._root,None)]

        while queue:
            node, parent = queue.pop(0)

            if node.value == value:
                target_node = node

            last_node = node
            parent_of_last = parent

            if node.left:
                queue.append((node.left, node))
            if node.right:
                queue.append((node.right, node))

        if target_node is None:
            step = OperationStep(
                OperationType.DELETE,
                value = value,
                description = f"删除失败：未找到节点{value}"
            )
            self.add_operation_step(step)
            return False

        #用最后一个节点的值替换目标节点
        if target_node != last_node:
            step = OperationStep(
                OperationType.DELETE,
                value = value,
                description = f'用节点{last_node.value}替换节点{value}'
            )
            self.add_operation_step(step)
            target_node.value = last_node.value

        #删除最后一个节点
        if parent_of_last is None:
            self._root = None
        elif parent_of_last.left == last_node:
            parent_of_last.left = None
        elif parent_of_last.right == last_node:
            parent_of_last.right = None

        self._size -= 1
        step = OperationStep(
            OperationType.DELETE,
            value = value,
            description = f"成功删除节点{value}"
        )
        self.add_operation_step(step)
        return True

    def search(self, value: Any) -> Optional[TreeNode]:
        """搜索指定值的节点"""
        step = OperationStep(
            OperationType.SEARCH,
            value = value,
            description = f"开始搜索节点{value}"
        )
        self.add_operation_step(step)

        if self._root is None:
            step = OperationStep(
                OperationType.SEARCH,
                value = value,
                description = "搜索失败：树为空"
            )
            self.add_operation_step(step)
            return None

        #宽度周游搜索
        queue = [self._root]
        while queue:
            node = queue.pop(0)

            step = OperationStep(
                OperationType.SEARCH,
                value = value,
                description = f"检查节点 {node.value}"
            )
            self.add_operation_step(step)

            if node.value == value:
                step = OperationStep(
                    OperationType.SEARCH,
                    value = value,
                    description = f"找到目标节点{value}"
                )
                self.add_operation_step(step)
                return node

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        step = OperationStep(
            OperationType.SEARCH,
            value = value,
            description = f"未找到节点{value}"
        )
        self.add_operation_step(step)
        return None

    def get_tree_data(self) -> dict:
        """获取树的结构数据，用于前端可视化"""
        print(f"调试: 进入 get_tree_data() root={getattr(self._root, 'value', None)}")
        return {
            'root': self._node_to_dict(self._root),
            'size': self._size,  # 添加这行
            'height': self.get_height(),  # 添加这行
            'traversals': {  # 添加遍历信息
                'levelorder': self.level_order_traversal()
            }
        }

    def build_from_list(self, values: List[Any]) -> bool:
        """从列表构建二叉树（层序方式）"""
        if not values:
            return False

        step = OperationStep(
            OperationType.INIT,
            description=f"从列表构建二叉树: {values}"
        )
        self.add_operation_step(step)

        self._root = TreeNode(values[0])
        self._size = 1
        queue = [self._root]
        i = 1

        while queue and i < len(values):
            node = queue.pop(0)

            # 左子节点
            if i < len(values) and values[i] is not None:
                node.left = TreeNode(values[i])
                queue.append(node.left)
                self._size += 1
            i += 1

            # 右子节点
            if i < len(values) and values[i] is not None:
                node.right = TreeNode(values[i])
                queue.append(node.right)
                self._size += 1
            i += 1

        step = OperationStep(
            OperationType.INIT,
            description=f"成功构建二叉树，共 {self._size} 个节点"
        )
        self.add_operation_step(step)
        return True




