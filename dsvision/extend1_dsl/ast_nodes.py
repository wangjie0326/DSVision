"""
抽象语法树（ast)节点定义
"""

from typing import List, Optional,Any
from dataclasses import dataclass

@dataclass
class ASTNode:
    """AST节点基类"""
    line: int
    column:int

@dataclass
class Program(ASTNode):
    """程序根节点"""
    structures: List['StructureDeclaration']

@dataclass
class StructureDeclaration(ASTNode):
    """数据结构声明"""
    structure_type: str  # Sequential, Linked, Stack, etc.
    name: str
    operations: List['Operation']

@dataclass
class Operation(ASTNode):
    """操作基类"""
    pass

@dataclass
class InitOperation(Operation):
    """初始化操作 init [1, 2, 3]"""
    values: List[Any]

@dataclass
class InsertOperation(Operation):
    """插入操作 insert 10 at 2"""
    value: Any
    index: Optional[int] = None

@dataclass
class DeleteOperation(Operation):
    """删除操作 delete at 2"""
    index: int

@dataclass
class SearchOperation(Operation):
    """搜索操作 search 10"""
    value: Any

@dataclass
class ClearOperation(Operation):
    """清空操作 clear"""
    pass

@dataclass
class SaveOperation(Operation):
    """保存操作 save "file.json" """
    filename: str

@dataclass
class LoadOperation(Operation):
    """加载操作 load "file.json" """
    filename: str

@dataclass
class ExportOperation(Operation):
    """导出操作 export "file.dsl" """
    filename: str

@dataclass
class ImportOperation(Operation):
    """导入操作 import "file.dsl" """
    filename: str

@dataclass
class PushOperation(Operation):
    """入栈操作 push 10"""
    value: Any

@dataclass
class PopOperation(Operation):
    """出栈操作 pop"""
    pass

@dataclass
class PeekOperation(Operation):
    """查看栈顶 peek"""
    pass

@dataclass
class EnqueueOperation(Operation):
    """入队操作 enqueue 10"""
    value: Any

@dataclass
class DequeueOperation(Operation):
    """出队操作 dequeue"""
    pass

@dataclass
class FrontOperation(Operation):
    """查看队首 front"""
    pass

@dataclass
class RearOperation(Operation):
    """查看队尾 rear"""
    pass


@dataclass
class BuildOperation(Operation):
    """构建操作 build [1, 2, 3, null, 4]"""
    values: List[Any]


@dataclass
class TraverseOperation(Operation):
    """遍历操作 traverse inorder"""
    method: str  # preorder, inorder, postorder, levelorder


@dataclass
class HeightOperation(Operation):
    """获取高度 height"""
    pass


@dataclass
class MinOperation(Operation):
    """获取最小值 min"""
    pass


@dataclass
class MaxOperation(Operation):
    """获取最大值 max"""
    pass


@dataclass
class ReverseOperation(Operation):
    """反转操作 reverse"""
    pass


@dataclass
class BuildTextOperation(Operation):
    """Huffman从文本构建 build_text "text" """
    text: str


@dataclass
class BuildFreqOperation(Operation):
    """Huffman从频率构建 build_freq {A: 5, B: 2}"""
    frequencies: dict


@dataclass
class EncodeOperation(Operation):
    """Huffman编码 encode "text" """
    text: str


@dataclass
class DecodeOperation(Operation):
    """Huffman解码 decode "01010" """
    encoded: str


@dataclass
class ShowCodesOperation(Operation):
    """显示编码表 show_codes"""
    pass


@dataclass
class InsertHeadOperation(Operation):
    """链表头插 insert_head 10"""
    value: Any


@dataclass
class InsertTailOperation(Operation):
    """链表尾插 insert_tail 10"""
    value: Any


@dataclass
class DeleteHeadOperation(Operation):
    """删除头节点 delete_head"""
    pass


@dataclass
class DeleteTailOperation(Operation):
    """删除尾节点 delete_tail"""
    pass


@dataclass
class GetOperation(Operation):
    """获取元素 get 2"""
    index: int


@dataclass
class SizeOperation(Operation):
    """获取大小 size"""
    pass


@dataclass
class SpeedOperation(Operation):
    """设置速度 speed 2x"""
    speed: str


@dataclass
class PauseOperation(Operation):
    """暂停 pause 2s"""
    duration: Optional[str] = None


@dataclass
class ForLoop(Operation):
    """for循环 for i in range(1, 10) { ... }"""
    variable: str
    iterable: Any
    body: List[Operation]


@dataclass
class IfStatement(Operation):
    """if语句 if size > 5 { ... }"""
    condition: str
    body: List[Operation]


@dataclass
class TryCatch(Operation):
    """try-catch语句"""
    try_body: List[Operation]
    catch_type: str
    catch_body: List[Operation]


@dataclass
class RangeExpression(ASTNode):
    """range表达式 range(1, 10)"""
    start: int
    end: int
    step: int = 1


@dataclass
class ArrayLiteral(ASTNode):
    """数组字面量 [1, 2, 3]"""
    elements: List[Any]


@dataclass
class DictLiteral(ASTNode):
    """字典字面量 {A: 5, B: 2}"""
    pairs: dict


def ast_to_dict(node: ASTNode) -> dict:
    """将AST节点转换为字典(用于JSON序列化)"""
    if node is None:
        return None

    result = {
        'type': node.__class__.__name__,
        'line': node.line,
        'column': node.column
    }

    for key, value in node.__dict__.items():
        if key in ['line', 'column']:
            continue

        if isinstance(value, list):
            result[key] = [ast_to_dict(item) if isinstance(item, ASTNode) else item
                           for item in value]
        elif isinstance(value, ASTNode):
            result[key] = ast_to_dict(value)
        else:
            result[key] = value

    return result