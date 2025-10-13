from enum import Enum
from typing import Any,List,Optional,Tuple


class OperationType(Enum):
    """操作类型"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    CLEAR = "clear"
    INIT = "init"
    #后面再加

class OperationStep:
    """记录操作步骤"""
    def __init__(self,operation:OperationType = OperationType,index:int = -1,
                value:Any = None, description:str = "",highlight_indices:List[int] = None):
        self.operation = operation
        self.index = index
        self.value = value
        self.description = description
        self.highlight_indices = highlight_indices or []
        self.timestamp = None

    def to_dict(self) -> dict:
        """转字典，序列化"""
        return {
            'operation': self.operation.value,
            'index': self.index,
            'value': self.value,
            'description': self.description,
            'highlight_indices': self.highlight_indices
        }


