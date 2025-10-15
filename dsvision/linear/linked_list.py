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

    # linked_list.py
    def insert(self, index: int, value: Any) -> bool:
        """插入元素 - 详细过程版"""
        if index < 0 or index > self._size:
            step = OperationStep(
                OperationType.INSERT,
                description=f'插入失败:索引越界 (index:{index})',
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)
            return False

        # === 步骤1: 显示插入目标 ===
        step = OperationStep(
            OperationType.INSERT,
            description=f'准备在位置 {index} 插入元素 {value}',
            value=value,
            index=index,
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        new_node = LinearNode(value)

        if index == 0:
            # === 头部插入 ===
            step = OperationStep(
                OperationType.CREATE_NODE,
                description=f'创建新节点: {value}',
                value=value,
                animation_type="fade",
                duration=0.3,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            step = OperationStep(
                OperationType.LINK_NODE,
                description=f'新节点指向原头节点',
                pointer_position=0,
                animation_type="move",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            new_node.next = self._head
            self._head = new_node
        else:
            # === 中间/尾部插入 ===
            # 步骤1: 指针从头开始
            step = OperationStep(
                OperationType.POINTER_MOVE,
                description='指针从头节点开始移动',
                pointer_position=0,
                animation_type="move",
                duration=0.3,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            # 步骤2: 遍历到目标位置前一个节点
            prev = self._head
            for i in range(index - 1):
                step = OperationStep(
                    OperationType.POINTER_MOVE,
                    description=f'指针移动到位置 {i + 1}',
                    pointer_position=i + 1,
                    highlight_indices=[i + 1],
                    animation_type="move",
                    duration=0.3,
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)
                prev = prev.next

            # 步骤3: 找到插入位置
            step = OperationStep(
                OperationType.COMPARE,
                description=f'找到位置 {index - 1},准备在其后插入',
                pointer_position=index - 1,
                highlight_indices=[index - 1],
                animation_type="highlight",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            # 步骤4: 创建新节点
            step = OperationStep(
                OperationType.CREATE_NODE,
                description=f'创建新节点: {value}',
                value=value,
                animation_type="fade",
                duration=0.3,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            # 步骤5: 连接新节点
            step = OperationStep(
                OperationType.LINK_NODE,
                description=f'新节点指向位置 {index} 的原节点',
                pointer_position=index - 1,
                animation_type="move",
                duration=0.4,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            new_node.next = prev.next

            step = OperationStep(
                OperationType.LINK_NODE,
                description=f'位置 {index - 1} 的节点指向新节点',
                pointer_position=index - 1,
                animation_type="move",
                duration=0.4,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            prev.next = new_node

        self._size += 1

        # === 最终步骤: 插入完成 ===
        step = OperationStep(
            OperationType.INSERT,
            description=f'✓ 成功插入元素 {value} 到位置 {index}',
            index=index,
            value=value,
            highlight_indices=[index],
            animation_type="highlight",
            duration=0.8,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
        return True

    def delete(self, index: int) -> Any:
        """删除元素 - 详细过程版"""

        # === 步骤1: 检查索引 ===
        if index < 0 or index >= self._size:
            step = OperationStep(
                OperationType.DELETE,
                index=index,
                description=f'删除失败：索引越界 (索引: {index}, 有效范围: 0-{self._size - 1})',
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)
            return None

        # === 步骤2: 标记要删除的节点 ===
        deleted_value = self.get(index)

        step = OperationStep(
            OperationType.DELETE,
            index=index,
            value=deleted_value,
            description=f'准备删除位置 {index} 的节点 {deleted_value}',
            highlight_indices=[index],
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        if index == 0:
            # === 删除头节点 ===
            step = OperationStep(
                OperationType.POINTER_MOVE,
                index=0,
                description=f'头指针指向下一个节点 {self._head.next.value if self._head.next else "NULL"}',
                pointer_position=1 if self._head.next else -1,
                animation_type="move",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            self._head = self._head.next
        else:
            # === 删除中间/尾部节点 ===

            # 步骤1: 指针从头开始
            step = OperationStep(
                OperationType.POINTER_MOVE,
                description='指针从头节点开始移动',
                pointer_position=0,
                highlight_indices=[0],
                animation_type="highlight",
                duration=0.3,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            # 步骤2: 遍历到目标位置前一个节点
            prev = self._head
            for i in range(index - 1):
                step = OperationStep(
                    OperationType.POINTER_MOVE,
                    description=f'指针移动: 位置 {i} → 位置 {i + 1}',
                    pointer_position=i + 1,
                    highlight_indices=[i, i + 1],
                    animation_type="move",
                    duration=0.4,
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)
                prev = prev.next

            # 步骤3: 找到待删除节点的前驱
            step = OperationStep(
                OperationType.COMPARE,
                description=f'到达位置 {index - 1}，其后继节点 {prev.next.value} 将被删除',
                pointer_position=index - 1,
                highlight_indices=[index - 1, index],
                animation_type="highlight",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            # 步骤4: 修改指针跳过待删除节点
            next_next_value = prev.next.next.value if prev.next.next else "NULL"
            step = OperationStep(
                OperationType.UNLINK_NODE,
                description=f'节点 {prev.value} 的 next 指向 {next_next_value}，跳过待删除节点',
                pointer_position=index - 1,
                animation_type="move",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            prev.next = prev.next.next

        self._size -= 1

        # === 最终步骤: 删除完成 ===
        step = OperationStep(
            OperationType.DELETE,
            index=index,
            value=deleted_value,
            description=f'✓ 成功删除节点 {deleted_value}，当前大小: {self._size}',
            animation_type="fade",
            duration=0.8,
            data_snapshot=self.to_list()
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

