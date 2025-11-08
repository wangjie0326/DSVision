"""
DSL解释器 (Interpreter)
负责执行AST节点,调用后端API
"""

import json
from typing import Dict, Any, List, Optional
from .ast_nodes import *

class ExecutionContext:
    """执行上下文"""
    def __init__(self):
        self.structures: Dict[str, Any] = {}  # 存储已创建的结构 {name: structure_instance}
        self.variables: Dict[str, Any] = {}   # 存储变量
        self.animation_speed: float = 1.0
        self.step_mode: bool = False

class Interpreter:
    """解释器"""

    def __init__(self, structure_manager):
        """
        structure_manager: 后端数据结构管理器,提供创建/操作数据结构的接口
        """
        self.structure_manager = structure_manager
        self.context = ExecutionContext()
        self.execution_log: List[str] = []
        self.operation_history: List[Dict] = []

    def log(self, message: str):
        """记录日志"""
        self.execution_log.append(message)
        print(f"[Interpreter] {message}")

    def error(self, message: str):
        """报错"""
        raise RuntimeError(f"[Interpreter Error] {message}")

    def execute(self,program: Program) -> Dict[str, Any]:
        """执行整个程序"""
        self.log("=== 开始执行DSL程序 ===")

        results = {}

        for structure_decl in program.structures:
            result = self.execute_structure_declaration(structure_decl)
            results[structure_decl.name] = result

        self.log("=== DSL程序执行完成 ===")

        return{
            'success': True,
            'results': results,
            'execution_log': self.execution_log,
            'operation_history': self.operation_history
        }

    def execute_structure_declaration(self, decl: StructureDeclaration) -> Dict[str, Any]:
        """执行数据结构声明"""
        self.log(f"\n创建数据结构: {decl.structure_type} {decl.name}")

        #映射dsl类型到后端类型
        type_mapping = {
            'Sequential': 'sequential',
            'Linked': 'linked',
            'Stack': 'stack',
            'Queue': 'queue',
            'Binary': 'binary',
            'BST': 'bst',
            'AVL': 'avl',
            'Huffman': 'huffman'
        }

        backend_type = type_mapping.get(decl.structure_type)
        if not backend_type:
            self.error(f"Unknown structure type: {decl.structure_type}")

        # 创建结构实例
        structure = self.structure_manager.create_structure(backend_type)
        self.context.structures[decl.name] = {
            'type': backend_type,
            'instance': structure,
            'data': []
        }

        # 执行操作
        for operation in decl.operations:
            self.execute_operation(decl.name, operation)

        # 返回结果
        return {
            'type': backend_type,
            'data': self.get_structure_data(decl.name),
            'operations_count': len(decl.operations)
        }

    def execute_operation(self, structure_name: str, operation: Operation):
        """执行操作"""
        if structure_name not in self.context.structures:
            self.error(f"Structure {structure_name} not found")

        struct_info = self.context.structures[structure_name]
        structure = struct_info['instance']
        struct_type = struct_info['type']

        # 记录操作
        op_record = {
            'structure': structure_name,
            'operation': operation.__class__.__name__,
            'details': {}
        }

        # 根据操作类型执行
        if isinstance(operation, InitOperation):
            self.log(f"  init {operation.values}")
            if hasattr(structure, 'initlist'):
                structure.initlist(operation.values)
            else:
                for value in operation.values:
                    structure.insert(structure.size(), value)
            op_record['details'] = {'values': operation.values}

        elif isinstance(operation, InsertOperation):
            index = operation.index if operation.index is not None else structure.size()
            self.log(f"  insert {operation.value} at {index}")

            # 针对不同结构类型区分处理
            if struct_type in ['stack']:
                structure.push(operation.value)
            elif struct_type in ['bst', 'binary', 'avl', 'huffman']:
                # 这些树形结构的 insert 不需要 index
                structure.insert(operation.value)
            else:
                structure.insert(index, operation.value)

            op_record['details'] = {'value': operation.value, 'index': index}

        elif isinstance(operation, DeleteOperation):
            self.log(f"  delete at {operation.index}")
            structure.delete(operation.index)
            op_record['details'] = {'index': operation.index}

        elif isinstance(operation, SearchOperation):
            self.log(f"  search {operation.value}")
            result = structure.search(operation.value)
            self.log(f"    结果: {result}")
            op_record['details'] = {'value': operation.value, 'result': result}

        elif isinstance(operation, ClearOperation):
            self.log(f"  clear")
            structure.clear()

        elif isinstance(operation, SaveOperation):
            self.log(f"  save {operation.filename}")
            self.save_structure(structure_name, operation.filename)
            op_record['details'] = {'filename': operation.filename}

        elif isinstance(operation, LoadOperation):
            self.log(f"  load {operation.filename}")
            self.load_structure(structure_name, operation.filename)
            op_record['details'] = {'filename': operation.filename}

        elif isinstance(operation, ExportOperation):
            self.log(f"  export {operation.filename}")
            self.export_dsl(structure_name, operation.filename)
            op_record['details'] = {'filename': operation.filename}

        elif isinstance(operation, PushOperation):
            self.log(f"  push {operation.value}")
            structure.push(operation.value)
            op_record['details'] = {'value': operation.value}

        elif isinstance(operation, PopOperation):
            self.log(f"  pop")
            result = structure.pop()
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, PeekOperation):
            self.log(f"  peek")
            result = structure.peek()
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, BuildOperation):
            self.log(f"  build {operation.values}")
            if hasattr(structure, 'build_from_list'):
                structure.build_from_list(operation.values)
            op_record['details'] = {'values': operation.values}

        elif isinstance(operation, TraverseOperation):
            self.log(f"  traverse {operation.method}")
            method_map = {
                'preorder': 'preorder_traversal',
                'inorder': 'inorder_traversal',
                'postorder': 'postorder_traversal',
                'levelorder': 'level_order_traversal'
            }
            method_name = method_map.get(operation.method.lower())
            if method_name and hasattr(structure, method_name):
                result = getattr(structure, method_name)()
                self.log(f"    结果: {result}")
                op_record['details'] = {'method': operation.method, 'result': result}

        elif isinstance(operation, HeightOperation):
            self.log(f"  height")
            result = structure.get_height()
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, MinOperation):
            self.log(f"  min")
            result = structure.get_min() if hasattr(structure, 'get_min') else None
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, MaxOperation):
            self.log(f"  max")
            result = structure.get_max() if hasattr(structure, 'get_max') else None
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, ReverseOperation):
            self.log(f"  reverse")
            if hasattr(structure, 'reverse'):
                structure.reverse()

        elif isinstance(operation, BuildTextOperation):
            self.log(f"  build_text \"{operation.text}\"")
            if hasattr(structure, 'build_from_string'):
                structure.build_from_string(operation.text)
            op_record['details'] = {'text': operation.text}

        elif isinstance(operation, EncodeOperation):
            self.log(f"  encode \"{operation.text}\"")
            if hasattr(structure, 'encode'):
                result, stats = structure.encode(operation.text)
                self.log(f"    结果: {result}")
                self.log(f"    统计: {stats}")
                op_record['details'] = {'text': operation.text, 'result': result, 'stats': stats}

        elif isinstance(operation, DecodeOperation):
            self.log(f"  decode \"{operation.encoded}\"")
            if hasattr(structure, 'decode'):
                result = structure.decode(operation.encoded)
                self.log(f"    结果: {result}")
                op_record['details'] = {'encoded': operation.encoded, 'result': result}

        elif isinstance(operation, ShowCodesOperation):
            self.log(f"  show_codes")
            if hasattr(structure, 'get_huffman_codes'):
                codes = structure.get_huffman_codes()
                self.log(f"    编码表: {codes}")
                op_record['details'] = {'codes': codes}

        elif isinstance(operation, InsertHeadOperation):
            self.log(f"  insert_head {operation.value}")
            structure.insert(0, operation.value)
            op_record['details'] = {'value': operation.value}

        elif isinstance(operation, InsertTailOperation):
            self.log(f"  insert_tail {operation.value}")
            structure.insert(structure.size(), operation.value)
            op_record['details'] = {'value': operation.value}

        elif isinstance(operation, DeleteHeadOperation):
            self.log(f"  delete_head")
            structure.delete(0)

        elif isinstance(operation, DeleteTailOperation):
            self.log(f"  delete_tail")
            structure.delete(structure.size() - 1)

        elif isinstance(operation, GetOperation):
            self.log(f"  get {operation.index}")
            result = structure.get(operation.index)
            self.log(f"    结果: {result}")
            op_record['details'] = {'index': operation.index, 'result': result}

        elif isinstance(operation, SizeOperation):
            self.log(f"  size")
            result = structure.size()
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, SpeedOperation):
            self.log(f"  speed {operation.speed}")
            # 解析速度 (如 "2x" -> 2.0)
            speed_str = operation.speed.lower().replace('x', '')
            try:
                self.context.animation_speed = float(speed_str)
            except ValueError:
                self.log(f"    警告: 无效的速度值 {operation.speed}")
            op_record['details'] = {'speed': operation.speed}

        elif isinstance(operation, PauseOperation):
            self.log(f"  pause {operation.duration or ''}")
            op_record['details'] = {'duration': operation.duration}

        else:
            self.log(f"  未实现的操作: {operation.__class__.__name__}")

        self.operation_history.append(op_record)

    def get_structure_data(self, structure_name: str) -> Any:
        """获取结构数据"""
        if structure_name not in self.context.structures:
            return None

        struct_info = self.context.structures[structure_name]
        structure = struct_info['instance']
        struct_type = struct_info['type']

        # 线性结构
        if struct_type in ['sequential', 'linked', 'stack', 'queue']:
            return structure.to_list()

        # 树结构
        elif struct_type in ['binary', 'bst', 'avl', 'huffman']:
            return structure.get_tree_data()

        return None

    def save_structure(self, structure_name: str, filename: str):
        """保存结构到文件"""
        data = {
            'structure_name': structure_name,
            'structure_type': self.context.structures[structure_name]['type'],
            'data': self.get_structure_data(structure_name),
            'timestamp': str(datetime.now())
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.log(f"    已保存到 {filename}")

    def load_structure(self, structure_name: str, filename: str):
        """从文件加载结构"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # TODO: 实现加载逻辑
        self.log(f"    已从 {filename} 加载")

    def export_dsl(self, structure_name: str, filename: str):
        """导出为DSL脚本"""
        struct_info = self.context.structures[structure_name]
        struct_type = struct_info['type']
        data = self.get_structure_data(structure_name)

        # 生成DSL代码
        dsl_code = f"""// Auto-generated DSL script
            // Structure: {structure_name}
            // Type: {struct_type}
            // Generated: {datetime.now()}
            {struct_type.capitalize()} {structure_name} {{
    init {data if isinstance(data, list) else '[]'}
}}
"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dsl_code)

        self.log(f"    已导出到 {filename}")


# 简化的结构管理器(用于测试)
class SimpleStructureManager:
    """简单的结构管理器"""

    def create_structure(self, struct_type: str):
        """创建数据结构实例"""
        # 这里返回一个模拟对象
        # 实际使用时应该返回 dsvision.linear 或 dsvision.tree 中的实例
        from dsvision.linear.sequential_list import SequentialList
        from dsvision.linear.linked_list import LinearLinkedList
        from dsvision.linear.stack import SequentialStack
        from dsvision.tree.binary_tree import BinaryTree
        from dsvision.tree.binary_search_tree import BinarySearchTree
        from dsvision.tree.avl_tree import AVLTree
        from dsvision.tree.huffman import HuffmanTree

        type_map = {
            'sequential': SequentialList,
            'linked': LinearLinkedList,
            'stack': SequentialStack,
            'binary': BinaryTree,
            'bst': BinarySearchTree,
            'avl': AVLTree,
            'huffman': HuffmanTree
        }

        cls = type_map.get(struct_type)
        if cls:
            return cls()

        raise ValueError(f"Unknown structure type: {struct_type}")


# 测试代码
if __name__ == "__main__":
    from dsvision.extend1_dsl.lexer import Lexer
    from dsvision.extend1_dsl.parser import Parser
    from datetime import datetime

    test_code = """
    Sequential myList {
        init [1, 2, 3, 4, 5]
        insert 10 at 2
        search 10
        delete at 3
        size
    }

    BST myBST {
        insert 50
        insert 30
        insert 70
        insert 20
        insert 40
        traverse inorder
        min
        max
    }
    """

    # 词法分析
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()

    # 语法分析
    parser = Parser(tokens)
    ast = parser.parse()

    # 解释执行
    manager = SimpleStructureManager()
    interpreter = Interpreter(manager)
    result = interpreter.execute(ast)

    print("\n=== 执行结果 ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
