from ..operation.operation import OperationStep, OperationType
from .base import LinearStructureBase
from typing import List, Any, Optional


class LinearNode:
    def __init__(self, value: Any):
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
            description="初始化单链表",
            pointers={"head": -1},
            code_template='linked_insert_head',
            code_line=1,
            code_highlight=[1]
        )
        self.add_operation_step(step)

    def initlist(self, values: List[Any]) -> bool:
        """批量初始化 - 详细展示每个节点创建和连接"""
        self._head = None
        self._size = 0

        if not values:
            step = OperationStep(
                OperationType.INIT,
                description="初始化完成：链表为空",
                pointers={"head": -1}
            )
            self.add_operation_step(step)
            return True

        step = OperationStep(
            OperationType.INIT,
            description=f"开始批量初始化 {len(values)} 个元素: {values}",
            animation_type="instant",
            duration=0.5
        )
        self.add_operation_step(step)

        # === 创建头节点 ===
        step = OperationStep(
            OperationType.CREATE_NODE,
            value=values[0],
            description=f"Step 1: 创建头节点，值为 {values[0]}",
            animation_type="fade",
            duration=0.6,
            data_snapshot=[]
        )
        self.add_operation_step(step)

        self._head = LinearNode(values[0])
        self._size = 1

        step = OperationStep(
            OperationType.POINTER_MOVE,
            description="Step 2: head 指针指向新创建的节点",
            pointers={"head": 0},
            highlight_indices=[0],
            animation_type="highlight",
            duration=0.5,
            data_snapshot=[values[0]]
        )
        self.add_operation_step(step)

        # === 依次创建后续节点 ===
        current = self._head

        for i, value in enumerate(values[1:], 1):
            # 显示 current 指针位置
            step = OperationStep(
                OperationType.POINTER_MOVE,
                description=f"Step {2 * i + 1}: current 指针指向位置 {i - 1}（值为 {current.value}）",
                pointers={"head": 0, "current": i - 1},
                highlight_indices=[i - 1],
                animation_type="highlight",
                duration=0.4,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            # 创建新节点
            step = OperationStep(
                OperationType.CREATE_NODE,
                value=value,
                description=f"Step {2 * i + 2}: 创建新节点，值为 {value}",
                pointers={"head": 0, "current": i - 1},
                animation_type="fade",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            new_node = LinearNode(value)

            # 连接节点
            step = OperationStep(
                OperationType.LINK_NODE,
                description=f"Step {2 * i + 3}: 将 current.next 指向新节点",
                pointers={"head": 0, "current": i - 1},
                highlight_indices=[i - 1, i],
                animation_type="move",
                duration=0.5,
                visual_hints={"show_arrow": True, "from": i - 1, "to": i},
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            current.next = new_node
            current = new_node
            self._size += 1

        step = OperationStep(
            OperationType.INIT,
            description=f"✓ 批量初始化完成，共创建 {self._size} 个节点",
            pointers={"head": 0},
            highlight_indices=list(range(self._size)),
            animation_type="highlight",
            duration=1.0,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
        return True

    def insert(self, index: int, value: Any) -> bool:
        """插入元素 - 完整详细过程"""
        # 🔥 清空操作历史，避免累积之前的操作
        self._operation_history = []

        if index < 0 or index > self._size:
            step = OperationStep(
                OperationType.INSERT,
                description=f"插入失败：索引越界 (index: {index}, 有效范围: 0-{self._size})",
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)
            return False

        step = OperationStep(
            OperationType.INSERT,
            description=f"准备在位置 {index} 插入元素 {value}",
            value=value,
            index=index,
            highlight_indices=[index] if index < self._size else [],
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # 头部插入
        if index == 0:
            return self._insert_at_head(value)

        # 中间/尾部插入
        return self._insert_at_middle(index, value)

    def _insert_at_head(self, value: Any) -> bool:
        """头部插入 - 详细展示"""
        step = OperationStep(
            OperationType.CREATE_NODE,
            value=value,
            description=f"Step 1/3: 创建新节点，值为 {value}",
            animation_type="fade",
            duration=0.6,
            data_snapshot=self.to_list(),
            code_template='linked_insert_head',
            code_line=2,
            code_highlight=[2, 3]
        )
        self.add_operation_step(step)

        new_node = LinearNode(value)

        if self._head is not None:
            step = OperationStep(
                OperationType.LINK_NODE,
                description=f"Step 2/3: 新节点.next → 原 head（值为 {self._head.value}）",
                pointers={"head": 0, "new_node": -1},
                highlight_indices=[0],
                animation_type="move",
                duration=0.6,
                visual_hints={"show_arrow": True, "from": -1, "to": 0},
                data_snapshot=self.to_list(),
                code_template='linked_insert_head',
                code_line=6,
                code_highlight=[6]
            )
            self.add_operation_step(step)

        new_node.next = self._head

        step = OperationStep(
            OperationType.POINTER_MOVE,
            description=f"Step 3/3: head 指针更新，指向新节点",
            pointers={"head": 0},
            highlight_indices=[0],
            animation_type="move",
            duration=0.6,
            data_snapshot=self.to_list(),
            code_template='linked_insert_head',
            code_line=9,
            code_highlight=[9, 10]
        )
        self.add_operation_step(step)

        self._head = new_node
        self._size += 1

        step = OperationStep(
            OperationType.INSERT,
            index=0,
            value=value,
            description=f"头部插入完成！新节点成为第一个节点",
            pointers={"head": 0},
            highlight_indices=[0],
            animation_type="highlight",
            duration=1.0,
            data_snapshot=self.to_list(),
            code_template='linked_insert_head',
            code_line=10,
            code_highlight=[10]
        )
        self.add_operation_step(step)
        return True

    def _insert_at_middle(self, index: int, value: Any) -> bool:
        """中间/尾部插入 - 完整指针移动过程"""

        # === 阶段1：定位到插入位置 ===
        step = OperationStep(
            OperationType.POINTER_MOVE,
            description=f"阶段 1/3：开始定位到位置 {index - 1}",
            pointers={"head": 0, "prev": 0},
            highlight_indices=[0],
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        prev = self._head
        for i in range(index - 1):
            step = OperationStep(
                OperationType.COMPARE,
                description=f"当前 prev 在位置 {i}（值={prev.value}），目标位置 {index - 1}",
                pointers={"head": 0, "prev": i},
                highlight_indices=[i],
                animation_type="highlight",
                duration=0.4,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            step = OperationStep(
                OperationType.POINTER_MOVE,
                description=f"prev = prev.next，移动到位置 {i + 1}",
                pointers={"head": 0, "prev": i + 1},
                highlight_indices=[i, i + 1],
                animation_type="move",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            prev = prev.next

        step = OperationStep(
            OperationType.COMPARE,
            description=f"到达目标：prev 在位置 {index - 1}（值={prev.value}）",
            pointers={"head": 0, "prev": index - 1},
            highlight_indices=[index - 1],
            animation_type="highlight",
            duration=0.7,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # === 阶段2：创建新节点 ===
        step = OperationStep(
            OperationType.CREATE_NODE,
            value=value,
            description=f"阶段 2/3：创建新节点，值为 {value}",
            pointers={"head": 0, "prev": index - 1},
            animation_type="fade",
            duration=0.6,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        new_node = LinearNode(value)

        # === 阶段3：调整指针连接 ===
        if prev.next is not None:
            step = OperationStep(
                OperationType.LINK_NODE,
                description=f"阶段 3/3 - Step 1: 新节点.next → 位置 {index}（值={prev.next.value}）",
                pointers={"head": 0, "prev": index - 1, "new_node": index},
                highlight_indices=[index - 1, index],
                animation_type="move",
                duration=0.6,
                visual_hints={"show_arrow": True, "from": index, "to": index + 1},
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)
        else:
            step = OperationStep(
                OperationType.LINK_NODE,
                description=f"阶段 3/3 - Step 1: 新节点.next → NULL（尾部插入）",
                pointers={"head": 0, "prev": index - 1, "new_node": index},
                animation_type="move",
                duration=0.6,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

        new_node.next = prev.next

        step = OperationStep(
            OperationType.UNLINK_NODE,
            description=f"Step 2: 断开 prev.next 的原连接",
            pointers={"head": 0, "prev": index - 1, "new_node": index},
            highlight_indices=[index - 1],
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        step = OperationStep(
            OperationType.LINK_NODE,
            description=f"Step 3: prev.next → 新节点",
            pointers={"head": 0, "prev": index - 1, "new_node": index},
            highlight_indices=[index - 1, index],
            animation_type="move",
            duration=0.6,
            visual_hints={"show_arrow": True, "from": index - 1, "to": index},
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        prev.next = new_node
        self._size += 1

        step = OperationStep(
            OperationType.INSERT,
            index=index,
            value=value,
            description=f"插入完成！元素 {value} 已插入到位置 {index}",
            pointers={"head": 0},
            highlight_indices=[index],
            animation_type="highlight",
            duration=1.2,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
        return True

    def delete(self, index: int) -> Any:
        """删除元素 - 完整详细过程"""
        # 🔥 清空操作历史，避免累积之前的操作
        self._operation_history = []

        if index < 0 or index >= self._size:
            step = OperationStep(
                OperationType.DELETE,
                index=index,
                description=f"删除失败：索引越界 (index: {index}, 有效范围: 0-{self._size - 1})",
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)
            return None

        deleted_value = self.get(index)

        step = OperationStep(
            OperationType.DELETE,
            index=index,
            description=f"准备删除位置 {index} 的节点（值={deleted_value}）",
            highlight_indices=[index],
            animation_type="highlight",
            duration=0.6,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        if index == 0:
            return self._delete_head()

        return self._delete_middle(index)

    def _delete_head(self) -> Any:
        """删除头节点 - 详细步骤"""
        deleted_value = self._head.value

        step = OperationStep(
            OperationType.DELETE,
            value=deleted_value,
            description=f"定位到头节点（值={deleted_value}）",
            pointers={"head": 0},
            highlight_indices=[0],
            animation_type="highlight",
            duration=0.6,
            data_snapshot=self.to_list(),
            code_template='linked_delete',
            code_line=3,
            code_highlight=[2, 3, 4, 5]
        )
        self.add_operation_step(step)

        if self._head.next is not None:
            step = OperationStep(
                OperationType.POINTER_MOVE,
                description=f"Step 1/2: head → 下一个节点（值={self._head.next.value}）",
                pointers={"head": 1},
                highlight_indices=[0, 1],
                animation_type="move",
                duration=0.6,
                data_snapshot=self.to_list(),
                code_template='linked_delete',
                code_line=4,
                code_highlight=[4]
            )
            self.add_operation_step(step)
        else:
            step = OperationStep(
                OperationType.POINTER_MOVE,
                description="Step 1/2: head → NULL（链表将变为空）",
                pointers={"head": -1},
                animation_type="move",
                duration=0.6,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

        self._head = self._head.next

        step = OperationStep(
            OperationType.DELETE,
            value=deleted_value,
            description=f"Step 2/2: 删除原头节点（值={deleted_value}）",
            animation_type="fade",
            duration=0.6,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        self._size -= 1

        step = OperationStep(
            OperationType.DELETE,
            value=deleted_value,
            description=f"删除完成！已移除元素 {deleted_value}",
            pointers={"head": 0} if self._head else {"head": -1},
            animation_type="highlight",
            duration=1.0,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
        return deleted_value

    def _delete_middle(self, index: int) -> Any:
        """删除中间/尾部节点 - 完整指针调整"""

        # === 阶段1：定位到目标节点的前驱 ===
        step = OperationStep(
            OperationType.POINTER_MOVE,
            description=f"阶段 1/2：定位到位置 {index - 1}",
            pointers={"head": 0, "prev": 0},
            highlight_indices=[0],
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        prev = self._head
        for i in range(index - 1):
            step = OperationStep(
                OperationType.COMPARE,
                description=f"当前 prev 在位置 {i}，目标位置 {index - 1}",
                pointers={"head": 0, "prev": i},
                highlight_indices=[i],
                animation_type="highlight",
                duration=0.4,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            step = OperationStep(
                OperationType.POINTER_MOVE,
                description=f"prev = prev.next，移动到位置 {i + 1}",
                pointers={"head": 0, "prev": i + 1},
                highlight_indices=[i, i + 1],
                animation_type="move",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            prev = prev.next

        deleted_value = prev.next.value

        step = OperationStep(
            OperationType.COMPARE,
            description=f"到达：prev 在位置 {index - 1}，要删除的节点值={deleted_value}",
            pointers={"head": 0, "prev": index - 1},
            highlight_indices=[index - 1, index],
            animation_type="highlight",
            duration=0.7,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # === 阶段2：调整指针，跳过目标节点 ===
        if prev.next.next is not None:
            step = OperationStep(
                OperationType.UNLINK_NODE,
                description=f"阶段 2/2 - Step 1: 准备断开与节点 {deleted_value} 的连接",
                pointers={"head": 0, "prev": index - 1},
                highlight_indices=[index - 1, index],
                animation_type="highlight",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            step = OperationStep(
                OperationType.LINK_NODE,
                description=f"Step 2: prev.next → 位置 {index + 1}（值={prev.next.next.value}）",
                pointers={"head": 0, "prev": index - 1},
                highlight_indices=[index - 1, index, index + 1],
                animation_type="move",
                duration=0.6,
                visual_hints={"show_arrow": True, "from": index - 1, "to": index + 1},
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)
        else:
            step = OperationStep(
                OperationType.LINK_NODE,
                description=f"Step 2: prev.next → NULL（删除尾节点）",
                pointers={"head": 0, "prev": index - 1},
                highlight_indices=[index - 1, index],
                animation_type="move",
                duration=0.6,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

        prev.next = prev.next.next

        step = OperationStep(
            OperationType.DELETE,
            value=deleted_value,
            description=f"Step 3: 删除节点（值={deleted_value}）",
            animation_type="fade",
            duration=0.6,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        self._size -= 1

        step = OperationStep(
            OperationType.DELETE,
            value=deleted_value,
            description=f"删除完成！已移除元素 {deleted_value}",
            pointers={"head": 0},
            animation_type="highlight",
            duration=1.2,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
        return deleted_value

    def search(self, value: Any) -> int:
        """搜索元素 - 完整遍历比较过程"""
        # 🔥 清空操作历史，避免累积之前的操作
        self._operation_history = []

        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f"开始搜索元素 {value}",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        if self._head is None:
            step = OperationStep(
                OperationType.SEARCH,
                value=value,
                description="链表为空，搜索失败",
                pointers={"head": -1}
            )
            self.add_operation_step(step)
            return -1

        step = OperationStep(
            OperationType.POINTER_MOVE,
            description="初始化：current 指针从 head 开始",
            pointers={"head": 0, "current": 0},
            highlight_indices=[0],
            animation_type="move",
            duration=0.5,
            data_snapshot=self.to_list(),
            code_template='linked_search',
            code_line=2,
            code_highlight=[2, 3]
        )
        self.add_operation_step(step)

        current = self._head
        index = 0

        while current is not None:
            step = OperationStep(
                OperationType.COMPARE,
                value=value,
                code_template='linked_search',
                code_line=7,
                code_highlight=[6, 7, 8],
                description=f"位置 {index}: 比较 {current.value} == {value} ?",
                pointers={"head": 0, "current": index},
                highlight_indices=[index],
                compare_indices=[index],
                animation_type="highlight",
                duration=0.6,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            if current.value == value:
                step = OperationStep(
                    OperationType.SEARCH,
                    index=index,
                    value=value,
                    description=f"找到了！元素 {value} 在位置 {index}",
                    pointers={"head": 0, "current": index},
                    highlight_indices=[index],
                    animation_type="highlight",
                    duration=1.5,
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)
                return index

            step = OperationStep(
                OperationType.COMPARE,
                description=f"{current.value} ≠ {value}，继续向后查找",
                pointers={"head": 0, "current": index},
                animation_type="instant",
                duration=0.3,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            if current.next is not None:
                step = OperationStep(
                    OperationType.POINTER_MOVE,
                    description=f"current = current.next，移动到位置 {index + 1}",
                    pointers={"head": 0, "current": index + 1},
                    highlight_indices=[index, index + 1],
                    animation_type="move",
                    duration=0.5,
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)

            current = current.next
            index += 1

        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f"遍历结束，未找到元素 {value}",
            pointers={"head": 0},
            animation_type="instant",
            duration=0.8,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
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

