from enum import Enum
from typing import Any,List,Optional,Tuple,Dict


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

            # 多指针跟踪系统（核心改进）
            pointers: Dict[str, int] = None,  # {"head": 0, "prev": 1, "current": 2}
            pointer_position: int = -1,  # 保留兼容性

            # 比较和节点相关
            compare_indices: List[int] = None,
            node_id: int = -1,

            # 动画控制
            animation_type: str = "instant",  # instant/move/fade/highlight
            duration: float = 0.5,

            # 状态快照
            data_snapshot: List[Any] = None,

            # 新增：链表专用可视化数据
            visual_hints: Dict[str, Any] = None  # {"show_arrow": True, "from": 1, "to": 2}
    ):
        self.operation = operation
        self.description = description
        self.index = index
        self.value = value
        self.highlight_indices = highlight_indices or []

        # 多指针系统
        self.pointers = pointers or {}
        self.pointer_position = pointer_position


        # 动画字段
        self.compare_indices = compare_indices or []
        self.node_id = node_id
        self.animation_type = animation_type
        self.duration = duration

        # 状态数据
        self.data_snapshot = data_snapshot or []
        self.visual_hints = visual_hints or {}
        self.timestamp = None

    def to_dict(self) -> dict:
        """转字典"""
        return {
            'operation': self.operation.value,
            'description': self.description,
            'index': self.index,
            'value': self.value,
            'highlight_indices': self.highlight_indices,

            # 多指针数据
            'pointers': self.pointers,
            'pointer_position': self.pointer_position,

            # 动画字段
            'compare_indices': self.compare_indices,
            'node_id': self.node_id,
            'animation_type': self.animation_type,
            'duration': self.duration,

            # 状态快照
            'data_snapshot': self.data_snapshot,
            'visual_hints': self.visual_hints
        }
