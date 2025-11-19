from dsvision.linear.base import LinearStructureBase
from ..operation.operation import OperationStep, OperationType
from typing import List,Any

class SequentialList(LinearStructureBase):
    """顺序表实现"""
    def __init__(self,capacity:int = 100):
        super().__init__()
        self._capacity = capacity
        self._data = [None] * capacity #创建一个长度为 capacity 的列表，每个位置先用 None 占位
        self._size = 0

        #记录初始化步骤
        step = OperationStep(
            OperationType.INIT,
            description = f"初始化顺序表，容量为{capacity}"
        )
        self.add_operation_step(step)

    def initlist(self,values:List[Any]) -> bool:
        """从列表批量初始化顺序表"""
        if len(values) > self._capacity:
            step = OperationStep(
                OperationType.INIT,
                description = f'初始化失败：元素数量({len(values)})超过容量({self._capacity})'
            )
            self.add_operation_step(step)
            return False
        #清空现有数据
        self._data = [None] * self._capacity
        self._size = 0
        step = OperationStep(
            OperationType.INIT,
            description=f'开始批量初始化 {len(values)} 个元素',
            data_snapshot=[]
        )
        self.add_operation_step(step)
        # 逐个插入
        for i, value in enumerate(values):
            if self._size >= self._capacity:
                step = OperationStep(
                    OperationType.INSERT,
                    description=f'容量已满，停止插入',
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)
                return False

            # 显示当前正在插入的元素
            step = OperationStep(
                OperationType.INSERT,
                index=i,
                value=value,
                description=f'正在插入第 {i + 1} 个元素: {value}',
                highlight_indices=[i],
                animation_type="fade",
                duration=0.3,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            self._data[i] = value
            self._size += 1

            # 显示插入后的状态
            step = OperationStep(
                OperationType.INSERT,
                index=i,
                value=value,
                description=f'成功插入元素 {value} 到位置 {i}',
                highlight_indices=[i],
                animation_type="highlight",
                duration=0.2,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

        step = OperationStep(
            OperationType.INIT,
            description=f'批量初始化完成，共 {self._size} 个元素',
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
        return True

    def insert(self,index:int,value:Any) -> bool:
        """在指定位置插入元素"""
        # === 步骤1: 检查容量，如果满了就扩容 ===
        # 🔥 对应C++代码第2-4行
        step = OperationStep(
            OperationType.INSERT,
            description=f'检查容量 (当前: {self._size}/{self._capacity})',
            data_snapshot=self.to_list(),
            code_template='sequential_insert',
            code_line=2,
            code_highlight=[2, 3, 4]
        )
        self.add_operation_step(step)

        if self._size >= self._capacity:
            # 触发扩容
            step = OperationStep(
                OperationType.INSERT,
                description=f'容量已满，触发扩容 (line 3)',
                data_snapshot=self.to_list(),
                code_template='sequential_insert',
                code_line=3,
                code_highlight=[3]
            )
            self.add_operation_step(step)

            if not self._expand():
                step = OperationStep(
                    OperationType.INSERT,
                    index=index,
                    value=value,
                    description=f'扩容失败，无法插入',
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)
                return False

        # === 步骤2: 检查索引 ===
        # 🔥 对应C++代码第7-9行
        step = OperationStep(
            OperationType.INSERT,
            index=index,
            description=f'检查索引有效性 (索引: {index}, 范围: 0-{self._size})',
            data_snapshot=self.to_list(),
            code_template='sequential_insert',
            code_line=7,
            code_highlight=[7, 8, 9]
        )
        self.add_operation_step(step)

        if index < 0 or index > self._size:
            step = OperationStep(
                OperationType.INSERT,
                index=index,
                value=value,
                description=f'插入失败：索引越界 (line 8)',
                data_snapshot=self.to_list(),
                code_template='sequential_insert',
                code_line=8,
                code_highlight=[8]
            )
            self.add_operation_step(step)
            return False

        # === 步骤3: 显示插入目标 ===
        step = OperationStep(
            OperationType.INSERT,
            index=index,
            value=value,
            description=f'准备在位置 {index} 插入元素 {value}',
            highlight_indices=[index],
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # === 步骤4: 如果不是末尾插入，需要移动元素 ===
        # 🔥 对应C++代码第12-14行
        if index < self._size:
            step = OperationStep(
                OperationType.INSERT,
                index=index,
                value=value,
                description=f'需要将位置 {index} 到 {self._size - 1} 的元素向后移动 (line 12)',
                highlight_indices=list(range(index, self._size)),
                animation_type="highlight",
                duration=0.5,
                data_snapshot=self.to_list(),
                code_template='sequential_insert',
                code_line=12,
                code_highlight=[12, 13, 14]
            )
            self.add_operation_step(step)

            # 从后往前逐个移动
            for i in range(self._size, index, -1):
                step = OperationStep(
                    OperationType.POINTER_MOVE,
                    index=i - 1,
                    description=f'将位置 {i - 1} 的元素移动到位置 {i} (line 13)',
                    pointer_position=i - 1,
                    highlight_indices=[i - 1, i],
                    animation_type="move",
                    duration=0.4,
                    data_snapshot=self.to_list(),
                    code_template='sequential_insert',
                    code_line=13,
                    code_highlight=[13]
                )
                self.add_operation_step(step)

                self._data[i] = self._data[i - 1]

        # === 步骤5: 插入新元素 ===
        # 🔥 对应C++代码第17行
        step = OperationStep(
            OperationType.CREATE_NODE,
            index=index,
            value=value,
            description=f'在位置 {index} 插入新元素 {value} (line 17)',
            highlight_indices=[index],
            animation_type="fade",
            duration=0.5,
            data_snapshot=self.to_list(),
            code_template='sequential_insert',
            code_line=17,
            code_highlight=[17]
        )
        self.add_operation_step(step)

        self._data[index] = value
        self._size += 1

        # === 步骤6: 更新大小 ===
        # 🔥 对应C++代码第18行
        step = OperationStep(
            OperationType.INSERT,
            index=index,
            value=value,
            description=f'✓ 插入完成！size++ (当前大小: {self._size}) (line 18)',
            highlight_indices=[index],
            animation_type="highlight",
            duration=0.8,
            data_snapshot=self.to_list(),
            code_template='sequential_insert',
            code_line=18,
            code_highlight=[18]
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

        deleted_value = self._data[index]

        # === 步骤2: 标记要删除的元素 ===
        step = OperationStep(
            OperationType.DELETE,
            index=index,
            value=deleted_value,
            description=f'准备删除位置 {index} 的元素 {deleted_value}',
            highlight_indices=[index],
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # === 步骤3: 如果不是最后一个元素，需要前移 ===
        if index < self._size - 1:
            step = OperationStep(
                OperationType.DELETE,
                index=index,
                value=deleted_value,
                description=f'需要将位置 {index + 1} 到 {self._size - 1} 的元素向前移动',
                highlight_indices=list(range(index + 1, self._size)),
                animation_type="highlight",
                duration=0.5,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            # 从前往后逐个移动
            for i in range(index, self._size - 1):
                step = OperationStep(
                    OperationType.POINTER_MOVE,
                    index=i,
                    description=f'将位置 {i + 1} 的元素 {self._data[i + 1]} 移动到位置 {i}',
                    pointer_position=i + 1,
                    highlight_indices=[i, i + 1],
                    animation_type="move",
                    duration=0.4,
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)

                self._data[i] = self._data[i + 1]

        # === 步骤4: 清空最后一个位置 ===
        self._size -= 1
        self._data[self._size] = None

        # === 步骤5: 删除完成 ===
        step = OperationStep(
            OperationType.DELETE,
            index=index,
            value=deleted_value,
            description=f'✓ 成功删除元素 {deleted_value}，当前大小: {self._size}',
            animation_type="fade",
            duration=0.8,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
        return deleted_value

    def search(self, value: Any) -> int:
        """搜索元素 - 详细过程版"""

        # === 步骤1: 开始搜索 ===
        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f'开始在顺序表中搜索元素 {value}',
            animation_type="instant",
            duration=0.3,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # === 步骤2: 逐个比较 ===
        for i in range(self._size):
            # 显示当前检查的位置
            step = OperationStep(
                OperationType.COMPARE,
                index=i,
                value=value,
                description=f'检查位置 {i}: {self._data[i]} == {value} ?',
                pointer_position=i,
                highlight_indices=[i],
                compare_indices=[i],
                animation_type="highlight",
                duration=0.4,
                data_snapshot=self.to_list()
            )
            self.add_operation_step(step)

            # 比较结果
            if self._data[i] == value:
                # 找到了
                step = OperationStep(
                    OperationType.SEARCH,
                    index=i,
                    value=value,
                    description=f'✓ 找到目标元素 {value}，位置为 {i}',
                    highlight_indices=[i],
                    animation_type="highlight",
                    duration=1.0,
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)
                return i
            else:
                # 不匹配，继续
                step = OperationStep(
                    OperationType.COMPARE,
                    index=i,
                    value=value,
                    description=f'✗ {self._data[i]} ≠ {value}，继续搜索',
                    pointer_position=i,
                    animation_type="instant",
                    duration=0.2,
                    data_snapshot=self.to_list()
                )
                self.add_operation_step(step)

        # === 步骤3: 未找到 ===
        step = OperationStep(
            OperationType.SEARCH,
            value=value,
            description=f'✗ 未找到元素 {value}',
            animation_type="instant",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)
        return -1

    def get(self, index: int) -> Any:
        """获取指定位置元素"""
        if 0 <= index < self._size:
            return self._data[index]
        return None

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def to_list(self) -> List[Any]:
        """返回完整容量的数据数组（包括None的空位）"""
        return self._data.copy()

    def get_capacity(self) -> int:
        """获取顺序表容量"""
        return self._capacity

    def get_used_size(self) -> int:
        """获取已使用的大小"""
        return self._size

    def _expand(self) -> bool:
        """扩容操作 - 1.5倍扩容，带完整动画步骤"""
        old_capacity = self._capacity
        new_capacity = int(old_capacity * 1.5)

        # === 步骤1: 开始扩容提示 ===
        step = OperationStep(
            OperationType.EXPAND,
            description=f'容量已满 (当前: {self._size}/{old_capacity})，触发扩容',
            animation_type="highlight",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # === 步骤2: 显示扩容计划 ===
        step = OperationStep(
            OperationType.EXPAND,
            description=f'准备扩容: {old_capacity} -> {new_capacity} (1.5倍)',
            animation_type="instant",
            duration=0.5,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        # === 步骤3: 创建新数组（在下方显示） ===
        new_data = [None] * new_capacity
        step = OperationStep(
            OperationType.EXPAND,
            description=f'创建新数组，容量: {new_capacity}',
            animation_type="fade",
            duration=0.8,
            data_snapshot=self.to_list(),
            visual_hints={'new_array': new_data, 'new_capacity': new_capacity}
        )
        self.add_operation_step(step)

        # === 步骤4: 逐个复制元素到新数组 ===
        step = OperationStep(
            OperationType.EXPAND,
            description=f'开始复制 {self._size} 个元素到新数组',
            animation_type="instant",
            duration=0.3,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        for i in range(self._size):
            # 显示复制过程
            step = OperationStep(
                OperationType.EXPAND,
                index=i,
                value=self._data[i],
                description=f'复制元素 [{i}]: {self._data[i]} 到新数组',
                highlight_indices=[i],
                animation_type="move",
                duration=0.3,
                data_snapshot=self.to_list(),
                visual_hints={'copy_index': i, 'new_array': new_data[:]}
            )
            self.add_operation_step(step)

            # 执行复制
            new_data[i] = self._data[i]

            # 显示复制后状态
            step = OperationStep(
                OperationType.EXPAND,
                index=i,
                value=self._data[i],
                description=f'✓ 已复制元素 [{i}]',
                highlight_indices=[i],
                animation_type="highlight",
                duration=0.2,
                data_snapshot=self.to_list(),
                visual_hints={'copy_index': i, 'new_array': new_data[:]}
            )
            self.add_operation_step(step)

        # === 步骤5: 标记旧数组（全红强调） ===
        step = OperationStep(
            OperationType.EXPAND,
            description=f'标记旧数组准备删除',
            highlight_indices=list(range(self._size)),
            animation_type="highlight",
            duration=1.0,
            data_snapshot=self.to_list(),
            visual_hints={'old_array_delete': True, 'new_array': new_data[:]}
        )
        self.add_operation_step(step)

        # === 步骤6: 删除旧数组，切换到新数组 ===
        self._data = new_data
        self._capacity = new_capacity

        step = OperationStep(
            OperationType.EXPAND,
            description=f'✓ 扩容完成！新容量: {new_capacity}',
            animation_type="fade",
            duration=0.8,
            data_snapshot=self.to_list()
        )
        self.add_operation_step(step)

        return True





