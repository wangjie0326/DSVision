from typing import Any, List
from .base import LinearStructureBase
from ..operation.operation import OperationStep, OperationType


class SequentialQueue(LinearStructureBase):
    """顺序队列（基于数组，支持可选容量与扩容动画）"""

    def __init__(self, capacity: int = 100):
        super().__init__()
        self._capacity = capacity if capacity else None  # None 表示无限容量
        self._data = [] if self._capacity is None else [None] * self._capacity
        self._size = 0
        self._front = 0
        self._rear = -1

        step = OperationStep(
            OperationType.INIT,
            description=f"初始化顺序队列，容量为{self._capacity if self._capacity is not None else '∞'}",
            highlight_indices=[],
            code_template='queue_enqueue',
            code_line=1,
            code_highlight=[1]
        )
        self.add_operation_step(step)

    # 基础能力
    def initlist(self, values: List[Any]) -> bool:
        if self._capacity is not None and len(values) > self._capacity:
            step = OperationStep(
                OperationType.INIT,
                description=f'初始化失败：元素数量({len(values)})超过容量({self._capacity})',
                code_template='queue_enqueue',
                code_line=3,
                code_highlight=[2, 3, 4]
            )
            self.add_operation_step(step)
            return False

        self._data = [] if self._capacity is None else [None] * self._capacity
        self._size = 0
        self._front = 0
        self._rear = -1

        for i, value in enumerate(values):
            if self._capacity is None:
                self._data.append(value)
            else:
                self._data[i] = value
            self._size += 1
            self._rear = i

        step = OperationStep(
            OperationType.INIT,
            description=f'批量初始化队列，{len(values)}个元素: {values}',
            highlight_indices=list(range(len(values))),
            code_template='queue_enqueue',
            code_line=10,
            code_highlight=[7, 8, 9, 10]
        )
        self.add_operation_step(step)
        return True

    # 队列操作
    def enqueue(self, value: Any) -> bool:
        if self.is_full():
            if not self._expand():
                step = OperationStep(
                    OperationType.INSERT,
                    index=self._size,
                    value=value,
                    description=f'入队失败：队列已满 (容量: {self._capacity})',
                    code_template='queue_enqueue',
                    code_line=3,
                    code_highlight=[2, 3, 4]
                )
                self.add_operation_step(step)
                return False

        target_index = self._rear + 1
        step = OperationStep(
            OperationType.INSERT,
            index=target_index,
            value=value,
            description=f'准备将元素 {value} 入队到位置 {target_index}',
            highlight_indices=[target_index],
            code_template='queue_enqueue',
            code_line=7,
            code_highlight=[7, 8],
            visual_hints={'front': self._front, 'rear': self._rear}
        )
        self.add_operation_step(step)

        move_step = OperationStep(
            OperationType.POINTER_MOVE,
            index=target_index,
            description=f'REAR 移动到位置 {target_index}',
            highlight_indices=[target_index],
            pointer_position=target_index,
            animation_type="move",
            duration=0.35,
            data_snapshot=self.to_list(),
            visual_hints={'front': self._front, 'rear': target_index}
        )
        self.add_operation_step(move_step)

        # 写入数据
        if self._capacity is None:
            if target_index < len(self._data):
                self._data[target_index] = value
            else:
                self._data.append(value)
        else:
            self._data[target_index] = value
        self._rear = target_index
        self._size += 1
        if self._size == 1:
            self._front = 0

        step = OperationStep(
            OperationType.INSERT,
            index=target_index,
            value=value,
            description=f'成功入队元素 {value} 到位置 {target_index}，当前大小: {self._size}',
            highlight_indices=[0, self._size - 1] if self._size > 1 else [0],
            code_template='queue_enqueue',
            code_line=10,
            code_highlight=[10],
            visual_hints={'front': self._front, 'rear': self._rear}
        )
        self.add_operation_step(step)
        return True

    def dequeue(self) -> Any:
        if self.is_empty():
            step = OperationStep(
                OperationType.DELETE,
                index=0,
                description='出队失败：队列为空',
                code_template='queue_dequeue',
                code_line=3,
                code_highlight=[2, 3, 4]
            )
            self.add_operation_step(step)
            return None

        old_front = self._front
        front_value = self._data[old_front] if old_front < len(self._data) else None

        step = OperationStep(
            OperationType.DELETE,
            index=old_front,
            value=front_value,
            description=f'准备出队队首元素 {front_value}',
            highlight_indices=[old_front],
            code_template='queue_dequeue',
            code_line=7,
            code_highlight=[7],
            visual_hints={'front': old_front, 'rear': self._rear}
        )
        self.add_operation_step(step)

        # 清空当前队首并仅移动指针（非循环队列）
        if self._capacity is None and old_front < len(self._data):
            self._data[old_front] = None
        elif self._capacity is not None and old_front < len(self._data):
            self._data[old_front] = None

        move_step = OperationStep(
            OperationType.POINTER_MOVE,
            index=old_front,
            description=f'FRONT 从 {old_front} 移动到 {old_front + 1 if self._size > 0 else 0}',
            highlight_indices=[old_front],
            pointer_position=old_front,
            animation_type="move",
            duration=0.35,
            data_snapshot=self.to_list(),
            visual_hints={'front': old_front + 1 if self._size > 0 else 0, 'rear': self._rear}
        )
        self.add_operation_step(move_step)

        self._front += 1
        self._size -= 1
        if self._size == 0:
            # 重置指针
            self._front = 0
            self._rear = -1

        step = OperationStep(
            OperationType.DELETE,
            index=old_front,
            value=front_value,
            description=f'成功出队 {front_value}，当前大小: {self._size}',
            highlight_indices=[self._front] if self._size > 0 else [],
            code_template='queue_dequeue',
            code_line=10,
            code_highlight=[10],
            visual_hints={'front': self._front, 'rear': self._rear}
        )
        self.add_operation_step(step)
        return front_value

    def front(self) -> Any:
        if self.is_empty():
            step = OperationStep(
                OperationType.SEARCH,
                description='查看失败：队列为空',
                code_template='queue_front',
                code_line=3,
                code_highlight=[2, 3, 4]
            )
            self.add_operation_step(step)
            return None

        idx = self._front
        value = self._data[idx]
        step = OperationStep(
            OperationType.SEARCH,
            index=idx,
            value=value,
            description=f'队首元素: {value}',
            highlight_indices=[idx],
            code_template='queue_front',
            code_line=7,
            code_highlight=[7],
            visual_hints={'front': self._front, 'rear': self._rear}
        )
        self.add_operation_step(step)
        return value

    def rear(self) -> Any:
        if self.is_empty():
            step = OperationStep(
                OperationType.SEARCH,
                description='查看失败：队列为空',
                code_template='queue_rear',
                code_line=3,
                code_highlight=[2, 3, 4]
            )
            self.add_operation_step(step)
            return None

        idx = self._rear
        value = self._data[idx] if idx >= 0 else None
        step = OperationStep(
            OperationType.SEARCH,
            index=idx,
            value=value,
            description=f'队尾元素: {value}',
            highlight_indices=[idx],
            code_template='queue_rear',
            code_line=7,
            code_highlight=[7],
            visual_hints={'front': self._front, 'rear': self._rear}
        )
        self.add_operation_step(step)
        return value

    # 兼容基类接口
    def insert(self, index: int, value: Any) -> bool:
        return self.enqueue(value)

    def delete(self, index: int) -> Any:
        return self.dequeue()

    def search(self, value: Any) -> int:
        for i in range(self._size):
            idx = self._front + i
            if idx < len(self._data) and self._data[idx] == value:
                step = OperationStep(
                    OperationType.SEARCH,
                    index=idx,
                    value=value,
                    description=f'找到元素 {value} 于位置 {idx}',
                    highlight_indices=[idx],
                    visual_hints={'front': self._front, 'rear': self._rear}
                )
                self.add_operation_step(step)
                return idx

        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f'未找到元素 {value}',
            visual_hints={'front': self._front, 'rear': self._rear}
        )
        self.add_operation_step(step)
        return -1

    def get(self, index: int, value: Any = None) -> Any:
        if 0 <= index < self._size:
            return self._data[index]
        return None

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def is_full(self) -> bool:
        if self._capacity is None:
            return False
        return (self._rear + 1) >= self._capacity

    def to_list(self) -> List[Any]:
        return list(self._data)

    def get_capacity(self) -> int:
        return self._capacity

    def get_front_index(self) -> int:
        return self._front if self._size > 0 else -1

    def get_rear_index(self) -> int:
        return self._rear

    def clear(self) -> None:
        step = OperationStep(
            OperationType.CLEAR,
            description='清空队列'
        )
        self.add_operation_step(step)

        self._data = [] if self._capacity is None else [None] * self._capacity
        self._size = 0
        self._front = 0
        self._rear = -1

        step = OperationStep(
            OperationType.CLEAR,
            description='队列已清空'
        )
        self.add_operation_step(step)

    # 扩容
    def _expand(self) -> bool:
        if self._capacity is None:
            return False

        old_capacity = self._capacity
        new_capacity = max(int(old_capacity * 1.5), old_capacity + 1)

        # 1) 提示扩容
        step = OperationStep(
            OperationType.EXPAND,
            description=f'容量已满 (当前: {self._size}/{old_capacity})，触发扩容',
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # 2) 创建新槽位
        new_data = [None] * new_capacity
        step = OperationStep(
            OperationType.EXPAND,
            description=f'准备扩容: {old_capacity} -> {new_capacity}',
            animation_type="fade",
            duration=0.8,
            data_snapshot=self.to_list(),
            visual_hints={'new_array': new_data[:], 'new_capacity': new_capacity}
        )
        self.add_operation_step(step)

        # 3) 复制元素（保持逻辑顺序，从 front 开始紧凑拷贝）
        for i in range(self._size):
            new_data[i] = self._data[self._front + i]

        step = OperationStep(
            OperationType.EXPAND,
            description=f'完成复制 {self._size} 个元素',
            animation_type="highlight",
            duration=0.4,
            data_snapshot=self.to_list(),
            visual_hints={'new_array': new_data[:], 'new_capacity': new_capacity}
        )
        self.add_operation_step(step)

        # 4) 切换新数组
        self._data = new_data
        self._capacity = new_capacity
        self._front = 0
        self._rear = self._size - 1

        step = OperationStep(
            OperationType.EXPAND,
            description=f'✓ 扩容完成！新容量: {new_capacity}',
            animation_type="fade",
            duration=0.6,
            data_snapshot=self.to_list(),
            visual_hints={'front': self._front, 'rear': self._rear}
        )
        self.add_operation_step(step)
        return True
