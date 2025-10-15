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
    POINTER_MOVE = "pointer_move"  # 指针移动
    COMPARE = "compare"  # 比较操作
    CREATE_NODE = "create_node"  # 创建节点
    LINK_NODE = "link_node"  # 连接节点
    UNLINK_NODE = "unlink_node"  # 断开节点
    # 树结构专用
    TRAVERSE_LEFT = "traverse_left"  # 向左遍历
    TRAVERSE_RIGHT = "traverse_right"  # 向右遍历
    ROTATE_LEFT = "rotate_left"  # 左旋
    ROTATE_RIGHT = "rotate_right"  # 右旋


class OperationStep:
    """记录操作步骤 - 增强版"""

    def __init__(
            self,
            operation: OperationType,
            description: str = "",
            # 通用字段
            index: int = -1,
            value: Any = None,
            highlight_indices: List[int] = None,

            # 新增:动画相关字段
            pointer_position: int = -1,  # 当前指针位置
            compare_indices: List[int] = None,  # 比较的节点索引
            node_id: int = -1,  # 节点ID(用于树)
            animation_type: str = "instant",  # instant/move/fade/highlight
            duration: float = 0.5,  # 动画持续时间(秒)

            # 新增:状态快照
            data_snapshot: List[Any] = None  # 当前数据状态快照
    ):
        self.operation = operation
        self.description = description
        self.index = index
        self.value = value
        self.highlight_indices = highlight_indices or []

        # 动画字段
        self.pointer_position = pointer_position
        self.compare_indices = compare_indices or []
        self.node_id = node_id
        self.animation_type = animation_type
        self.duration = duration

        # 状态快照
        self.data_snapshot = data_snapshot or []
        self.timestamp = None

    def to_dict(self) -> dict:
        """转字典"""
        return {
            'operation': self.operation.value,
            'description': self.description,
            'index': self.index,
            'value': self.value,
            'highlight_indices': self.highlight_indices,

            # 动画字段
            'pointer_position': self.pointer_position,
            'compare_indices': self.compare_indices,
            'node_id': self.node_id,
            'animation_type': self.animation_type,
            'duration': self.duration,

            # 状态快照
            'data_snapshot': self.data_snapshot
        }
