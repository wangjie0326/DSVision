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
        #批量插入
        for i,value in enumerate(values):
            self._data[i] = value
            self._size += 1

        step = OperationStep(
            OperationType.INIT,
            description=f'批量初始化{len(values)}个元素: {values}',
            highlight_indices=list(range(len(values)))
        )
        self.add_operation_step(step)
        return True

    def insert(self,index:int,value:Any) -> bool:
        """在指定位置插入元素"""
        #顺序表已满
        if self._size >= self._capacity:
            step = OperationStep(
                OperationType.INSERT,
                index,
                value,
                f'Inserting failed, because capacity is full (capacity:{self._capacity}) '
            )
            self.add_operation_step(step)
            return False
        #插入的索引超过容量
        if index < 0 or index > self._size:
            step = OperationStep(
                OperationType.INSERT,
                index,
                value,
                f'Inserting failed, because index is out of range (index:{index}) '
            )
            self.add_operation_step(step)
            return False

        #正常，记录移动元素步骤
        if index < self._size:
            step = OperationStep(
                OperationType.INSERT,
                index,
                value,
                f"Inserting {value} into position'{index}', and now moving elements behind that.",
                highlight_indices = list(range(index,self._size))
            )
            self.add_operation_step(step)
        #向后移动元素
        for i in range(self._size,index,-1):
            self._data[i] = self._data[i-1] #从后往前依次后退
        #插入新元素
        self._data[index] = value
        self._size += 1

        step = OperationStep(
            OperationType.INSERT,
            index,
            value,
            f'Inserted {value} into position{index} successfully.',
            highlight_indices = [index]
        )
        self.add_operation_step(step)
        return True

    def delete(self,index:int) -> Any:
        """删除指定位置元素"""
        if index < 0 or index >= self._size:
            step = OperationStep(
                OperationType.DELETE,
                index,
                description=f'Delete failed, because index is out of range (index:{self._capacity}) '
            )
            self.add_operation_step(step)
            return None

        deleted_value = self._data[index]
        step = OperationStep(
            OperationType.DELETE,
            index,
            deleted_value,
            f'Deleting {deleted_value} from position{index}.',
            highlight_indices = [index]
        )
        self.add_operation_step(step)
        #向前移动元素
        for i in range(index,self._size - 1):
            self._data[i] = self._data[i+1]
        self._size -= 1
        self._data[self._size] = None
        step = OperationStep(
            OperationType.DELETE,
            index,
            deleted_value,
            f'Deleted {deleted_value} from position{index} successfully,and now moving elements behind that.',
            highlight_indices = list(range(index,self._size))
        )
        self.add_operation_step(step)
        return deleted_value

    def search(self,value:Any) -> int:
        """搜索元素的位置"""
        step = OperationStep(
            OperationType.SEARCH,
            value,
            description=f'starting to search {value}.'
        )
        self.add_operation_step(step)

        for i in range(self._size):
            step = OperationStep(
                OperationType.SEARCH,
                i,value,
                f'Comparing the element {self._data[i]} of position{i} and destination{value}',
                highlight_indices = [i]
            )
            self.add_operation_step(step)

            if self._data[i] == value:
                step = OperationStep(
                    OperationType.SEARCH,
                    i,value,
                    f'Found the destination element {self._data[i]} of position{i}',
                )
                self.add_operation_step(step)
                return i

        step = OperationStep(
            OperationType.SEARCH,
            value = value,
            description=f'The destination element {value} is not found.',
        )
        self.add_operation_step(step)
        return -1

    def get(self,index:int) -> Any:
        """给位置返回元素"""
        ###这一步没有错误提示,比较简陋,主要作为功能
        if index >=0 and index < self._size:
            return self._data[index]
        return None

    def size(self) -> int:
        return self._size

    def is_empty(self) ->bool:
        return self._size == 0

    def to_list(self) -> List[Any]:
        return [self._data[i] for i in range(self._size)]

    def get_capacity(self) -> int:
        return self._capacity






