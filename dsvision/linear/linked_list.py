from ..operation.operation import OperationStep,OperationType
from .base import LinearStructureBase
from typing import List, Tuple,Any,Optional

class LinearNode:
    def __init__(self,value:Any):
        self.value = value
        self.next: Optional['LinearNode'] = None
        self.node_id = id(self)

class LinearLinkedList(LinearStructureBase):
    def __init__(self):
        super().__init__()
        self._head: Optional[LinearNode] = None
        self._size = 0

        step = OperationStep(
            OperationType.INIT,
            description="初始化单链表"
        )
        self.add_operation_step(step)

    def initlist(self, values: List[Any]) -> bool:
        """从列表批量初始化链表"""
        # 清空现有链表
        self._head = None
        self._size = 0

        if not values:
            return True

        #创建头节点
        self._head = LinearNode(values[0])
        self._size = 1
        current = self._head

        #依次创建后续节点
        for value in values[1:]:
            new_node = LinearNode(value)
            current.next = new_node
            current = new_node
            self._size += 1

        step = OperationStep(
            OperationType.INIT,
            description=f'批量初始化{len(values)}个元素: {values}',
            highlight_indices=list(range(len(values)))
        )
        self.add_operation_step(step)
        return True

    def insert(self,index: int, value:Any) -> bool:
        if index < 0 or index > self._size:
            step = OperationStep(
                OperationType.INIT,
                index,
                value,
                f'Inserting failed, because index is out of range (index:{index}) '
            )
            self.add_operation_step(step)
            return False

        new_node = LinearNode(value)

        if index==0:
            step = OperationStep(
                OperationType.INSERT,
                index,
                value,
                f'Inserting {value} at the beginning of the linked list'
            )
            self.add_operation_step(step)
            new_node.next = self._head
            self._head = new_node

        else:
            step = OperationStep(
                OperationType.INSERT,
                index,
                value,
                f'Finding position {index} to insert {value} until position {index-1}'
            )
            self.add_operation_step(step)
            # 找到插入位置的前一个节点
            prev = self._head
            for i in range(index - 1):
                prev = prev.next

            step = OperationStep(
                OperationType.INSERT,
                index, value,
                f"找到位置 {index - 1}，在其后插入元素 {value}"
            )
            self.add_operation_step(step)

            new_node.next = prev.next
            prev.next = new_node

        self._size += 1

        step = OperationStep(
            OperationType.INSERT,
            index, value,
            f"成功插入元素 {value} 到位置 {index}",
            highlight_indices=[index]
        )
        self.add_operation_step(step)
        return True

    def delete(self, index: int) -> Any:
        """删除指定位置元素"""
        if index < 0 or index >= self._size:
            step = OperationStep(
                OperationType.DELETE,
                index,
                description=f'Delete failed, index out of range (index:{index})'
            )
            self.add_operation_step(step)
            return None

        if index == 0:
            deleted_value = self._head.value
            self._head = self._head.next
        else:
            prev = self._head
            for i in range(index - 1):
                prev = prev.next
            deleted_value = prev.next.value
            prev.next = prev.next.next

        self._size -= 1
        step = OperationStep(
            OperationType.DELETE,
            index,
            deleted_value,
            f'Successfully deleted element {deleted_value} at position {index}'
        )
        self.add_operation_step(step)
        return deleted_value

    def search(self, value: Any) -> int:
        """搜索元素位置"""
        current = self._head
        index = 0
        while current:
            if current.value == value:
                return index
            current = current.next
            index += 1
        return -1

    def get(self, index: int) -> Any:
        """获取指定位置元素"""
        if index < 0 or index >= self._size:
            return None
        current = self._head
        for i in range(index):
            current = current.next
        return current.value

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def to_list(self) -> List[Any]:
        """转换为列表"""
        result = []
        current = self._head
        while current:
            result.append(current.value)
            current = current.next
        return result

