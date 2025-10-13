from abc import ABC,abstractmethod
from typing import List, Optional, Any, Tuple
from ..operation.operation import OperationStep

class LinearStructureBase(ABC):
    def __init__(self):
        self._operation_history: List[OperationStep] = []
        self._current_step = -1

    @abstractmethod
    def initlist(self,values:List[Any]) -> bool:
        pass

    @abstractmethod
    def insert(self,index:int,value:Any) -> bool:
        pass
    @abstractmethod
    def delete(self,index:int) -> Any:
        pass
    @abstractmethod
    def search(self,value:Any)->int:
        pass
    @abstractmethod
    def get(self,index:int,value:Any) -> Any:
        #给位置，返回元素
        pass
    @abstractmethod
    def size(self) ->int:
        pass
    @abstractmethod
    def is_empty(self)->bool:
        pass
    ###后面还差 转列表、添加操作步骤、获取操作历史、清空操作历史、保存当前状态

    def add_operation_step(self,step:OperationStep) -> None:
        """添加操作步骤"""
        self._operation_history.append(step)
        self._current_step += 1

    def remove_operation_step(self,step:OperationStep) -> None:
        self._operation_history.remove(step)
        self._current_step -= 1

    def get_operation_history(self) -> List[OperationStep]:
        return self._operation_history.copy()

    def clear_operation_history(self) -> None:
        self._operation_history.clear()
        self._current_step = -1

    def save_state(self)->dict:
        """保存当前状态"""
        return {
            'size': self.size(),
            'is_empty': self.is_empty(),
            'operation_history': [step.to_dict() for step in self._operation_history]
        }

    def to_list(self) -> List[Any]:
        """转换为列表（子类可选实现）"""
        raise NotImplementedError("子类需要实现 to_list 方法")





