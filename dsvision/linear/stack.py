from .base import LinearStructureBase
from ..operation.operation import OperationStep, OperationType
from typing import List, Any, Optional


class SequentialStack(LinearStructureBase):
    """顺序栈实现 (LIFO - Last In First Out)"""

    def __init__(self, capacity: int = 100):
        super().__init__()
        self._capacity = capacity
        self._data = [None] * capacity
        self._top = -1  # 栈顶指针，-1表示空栈

        # 记录初始化步骤
        step = OperationStep(
            OperationType.INIT,
            description=f"初始化顺序栈，容量为{capacity}"
        )
        self.add_operation_step(step)

    def initlist(self, values: List[Any]) -> bool:
        """从列表批量初始化栈（列表首元素为栈底）"""
        if len(values) > self._capacity:
            step = OperationStep(
                OperationType.INIT,
                description=f'初始化失败：元素数量({len(values)})超过容量({self._capacity})'
            )
            self.add_operation_step(step)
            return False

        #清空现有数据
        self._data = [None] * self._capacity
        self._top = -1

        #批量入栈
        for value in values:
            self._top += 1
            self._data[self._top] = value

        step = OperationStep(
            OperationType.INIT,
            description=f'批量初始化栈，{len(values)}个元素: {values}',
            highlight_indices=list(range(len(values)))
        )
        self.add_operation_step(step)
        return True

    def push(self, value: Any) -> bool:
        """入栈操作"""
        # 检查栈是否已满
        if self.is_full():
            step = OperationStep(
                OperationType.INSERT,
                self._top,
                value,
                f'入栈失败：栈已满 (容量: {self._capacity})',
            )
            self.add_operation_step(step)
            return False

        # 记录入栈操作
        step = OperationStep(
            OperationType.INSERT,
            self._top + 1,
            value,
            f'准备将元素 {value} 入栈，栈顶指针从 {self._top} 移动到 {self._top + 1}',
            highlight_indices=[self._top + 1] if self._top >= 0 else [0]
        )
        self.add_operation_step(step)

        # 栈顶指针上移，插入新元素
        self._top += 1
        self._data[self._top] = value

        # 记录入栈成功
        step = OperationStep(
            OperationType.INSERT,
            self._top,
            value,
            f'成功将元素 {value} 入栈到位置 {self._top}，当前栈大小: {self._top + 1}',
            highlight_indices=[self._top]
        )
        self.add_operation_step(step)
        return True

    def pop(self) -> Any:
        """出栈操作"""
        # 检查栈是否为空
        if self.is_empty():
            step = OperationStep(
                OperationType.DELETE,
                self._top,
                description='出栈失败：栈为空',
            )
            self.add_operation_step(step)
            return None

        # 获取栈顶元素
        popped_value = self._data[self._top]

        # 记录出栈操作
        step = OperationStep(
            OperationType.DELETE,
            self._top,
            popped_value,
            f'准备将栈顶元素 {popped_value} (位置 {self._top}) 出栈',
            highlight_indices=[self._top]
        )
        self.add_operation_step(step)

        # 删除栈顶元素，栈顶指针下移
        self._data[self._top] = None
        self._top -= 1

        # 记录出栈成功
        step = OperationStep(
            OperationType.DELETE,
            self._top + 1,
            popped_value,
            f'成功将元素 {popped_value} 出栈，栈顶指针移动到 {self._top}，当前栈大小: {self._top + 1}',
            highlight_indices=[self._top] if self._top >= 0 else []
        )
        self.add_operation_step(step)
        return popped_value

    def peek(self) -> Any:
        """查看栈顶元素（不出栈）"""
        if self.is_empty():
            step = OperationStep(
                OperationType.SEARCH,
                self._top,
                description='查看失败：栈为空',
            )
            self.add_operation_step(step)
            return None

        top_value = self._data[self._top]
        step = OperationStep(
            OperationType.SEARCH,
            self._top,
            top_value,
            f'查看栈顶元素: {top_value} (位置 {self._top})',
            highlight_indices=[self._top]
        )
        self.add_operation_step(step)
        return top_value

    def insert(self, index: int, value: Any) -> bool:
        """栈不支持随机位置插入，使用push代替"""
        return self.push(value)

    def delete(self, index: int) -> Any:
        """栈不支持随机位置删除，使用pop代替"""
        return self.pop()

    def search(self, value: Any) -> int:
        """搜索元素在栈中的位置（从栈底开始计数）"""
        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f'开始搜索元素 {value}',
        )
        self.add_operation_step(step)

        for i in range(self._top + 1):
            step = OperationStep(
                OperationType.SEARCH,
                i,
                value,
                f'比较位置 {i} 的元素 {self._data[i]} 与目标元素 {value}',
                highlight_indices=[i]
            )
            self.add_operation_step(step)

            if self._data[i] == value:
                step = OperationStep(
                    OperationType.SEARCH,
                    i,
                    value,
                    f'找到目标元素 {value}，位置为 {i}',
                    highlight_indices=[i]
                )
                self.add_operation_step(step)
                return i

        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f'未找到目标元素 {value}',
        )
        self.add_operation_step(step)
        return -1

    def get(self, index: int) -> Any:
        """获取指定位置的元素"""
        if 0 <= index <= self._top:
            return self._data[index]
        return None

    def size(self) -> int:
        """返回栈的当前大小"""
        return self._top + 1

    def is_empty(self) -> bool:
        """判断栈是否为空"""
        return self._top == -1

    def is_full(self) -> bool:
        """判断栈是否已满"""
        return self._top == self._capacity - 1

    def to_list(self) -> List[Any]:
        """将栈转换为列表（从栈底到栈顶）"""
        return [self._data[i] for i in range(self._top + 1)]

    def get_capacity(self) -> int:
        """获取栈的容量"""
        return self._capacity

    def get_top_index(self) -> int:
        """获取栈顶指针位置"""
        return self._top

    def clear(self) -> None:
        """清空栈"""
        step = OperationStep(
            OperationType.CLEAR,
            description='清空栈',
        )
        self.add_operation_step(step)

        self._data = [None] * self._capacity
        self._top = -1

        step = OperationStep(
            OperationType.CLEAR,
            description='栈已清空',
        )
        self.add_operation_step(step)