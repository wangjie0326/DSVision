"""
DSL解释器 (Interpreter)
负责执行AST节点,调用后端API
"""

import json
import random
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

    def __init__(self, structure_manager, global_structures=None):
        """
        structure_manager: 后端数据结构管理器,提供创建/操作数据结构的接口
        global_structures: 全局structures字典的引用 {structure_id: structure_instance}
        """
        self.structure_manager = structure_manager
        self.context = ExecutionContext()
        self.execution_log: List[str] = []
        self.operation_history: List[Dict] = []
        self.global_structures = global_structures or {}  # 保存全局structures引用
        self.structure_id_map = {}  # 映射: structure_name -> structure_id

    def log(self, message: str):
        """记录日志"""
        self.execution_log.append(message)
        print(f"[Interpreter] {message}")

    def error(self, message: str):
        """报错"""
        raise RuntimeError(f"[Interpreter Error] {message}")

    def _create_new_structure(self, name: str, backend_type: str):
        """创建新结构实例的辅助方法"""
        self.log(f"\n创建新数据结构: {backend_type} {name}")
        structure = self.structure_manager.create_structure(backend_type)
        self.context.structures[name] = {
            'type': backend_type,
            'instance': structure,
            'data': []
        }

    def _get_structure_type(self, structure) -> str:
        """推断结构类型的辅助方法"""
        class_name = structure.__class__.__name__
        type_map = {
            'SequentialList': 'sequential',
            'LinearLinkedList': 'linked',
            'SequentialStack': 'stack',
            'LinkedStack': 'stack',
            'SequentialQueue': 'queue',
            'LinkedQueue': 'queue',
            'BinaryTree': 'binary',
            'BinarySearchTree': 'bst',
            'AVLTree': 'avl',
            'HuffmanTree': 'huffman'
        }
        return type_map.get(class_name, 'unknown')

    def register_structure_mapping(self, name: str, structure_id: str):
        """注册结构名称到ID的映射"""
        self.structure_id_map[name] = structure_id
        self.log(f"注册结构映射: {name} -> {structure_id[:8]}...")

    def evaluate_value(self, value: Any) -> Any:
        """评估值，将RandomCall节点替换为实际随机数"""
        if isinstance(value, RandomCall):
            random_num = random.randint(value.min_value, value.max_value)
            self.log(f"    random({value.min_value}, {value.max_value}) -> {random_num}")
            return random_num
        elif isinstance(value, list):
            return [self.evaluate_value(v) for v in value]
        else:
            return value

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

        # 🔥 优先级1: 检查当前会话内存
        if decl.name in self.context.structures:
            existing_struct = self.context.structures[decl.name]
            if existing_struct['type'] != backend_type:
                # 如果结构来自当前页面（带有 structure_id），优先使用现有结构，避免误重建
                if 'structure_id' in existing_struct:
                    self.log(f"⚠️ 类型不匹配，优先复用当前页面结构: {decl.name} {existing_struct['type']} (忽略声明的 {backend_type})")
                    backend_type = existing_struct['type']
                else:
                    self.log(f"⚠️ 类型不匹配，重建结构: {decl.name} {existing_struct['type']} -> {backend_type}")
                    self._create_new_structure(decl.name, backend_type)
            else:
                self.log(f"\n✓ 复用现有数据结构: {decl.structure_type} {decl.name} (会话内存)")

        # 🔥 优先级2: 检查全局structures（跨会话复用）
        elif decl.name in self.structure_id_map:
            structure_id = self.structure_id_map[decl.name]
            if structure_id in self.global_structures:
                structure = self.global_structures[structure_id]
                structure_backend_type = self._get_structure_type(structure)
                if structure_backend_type != backend_type:
                    self.log(f"⚠️ 全局类型不匹配，重建结构: {decl.name} {structure_backend_type} -> {backend_type}")
                    del self.structure_id_map[decl.name]
                    self._create_new_structure(decl.name, backend_type)
                else:
                    self.log(f"\n✓ 复用全局数据结构: {decl.structure_type} {decl.name} (ID: {structure_id[:8]}...)")
                    self.context.structures[decl.name] = {
                        'type': backend_type,
                        'instance': structure,
                        'data': [],
                        'structure_id': structure_id  # 保存ID
                    }
            else:
                # ID映射存在但结构不存在，清除映射并创建新的
                del self.structure_id_map[decl.name]
                self._create_new_structure(decl.name, backend_type)
        else:
            # 🔥 优先级3: 创建新结构实例
            self._create_new_structure(decl.name, backend_type)

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

        # 🔥 关键修复: 在执行每个操作前清空操作历史，避免累积之前的动画步骤
        structure.clear_operation_history()

        # 记录操作
        op_record = {
            'structure': structure_name,
            'operation': operation.__class__.__name__,
            'details': {}
        }

        # 根据操作类型执行
        if isinstance(operation, InitOperation):
            # 评估随机数
            values = self.evaluate_value(operation.values)
            capacity_info = f" capacity {operation.capacity}" if operation.capacity else ""
            self.log(f"  init {values}{capacity_info}")

            # 如果指定了 capacity 且结构支持设置容量，先更新容量
            if operation.capacity and hasattr(structure, '_capacity'):
                old_capacity = structure._capacity
                structure._capacity = operation.capacity
                structure._data = [None] * operation.capacity
                structure._size = 0
                self.log(f"    设置容量: {old_capacity} -> {operation.capacity}")

            if hasattr(structure, 'initlist'):
                structure.initlist(values)
            else:
                for value in values:
                    # 线性结构按索引插入，树形结构直接按值插入
                    if struct_type in ['bst', 'binary', 'avl', 'huffman']:
                        structure.insert(value)
                    else:
                        structure.insert(structure.size(), value)
            op_record['details'] = {'values': values, 'capacity': operation.capacity}

        elif isinstance(operation, InsertOperation):
            # 评估随机数
            value = self.evaluate_value(operation.value)
            # 线性结构缺省 index 使用 size()；树结构保留 None
            index = operation.index
            direction = getattr(operation, 'direction', None)
            parent_id = getattr(operation, 'parent_id', None)
            self.log(f"  insert {value}" + (f" at {index}" if index is not None else "") + (f" {direction}" if direction else ""))

            # 针对不同结构类型区分处理
            if struct_type in ['stack']:
                structure.push(value)
            elif struct_type in ['binary']:
                # 支持按父节点左/右插入
                structure.insert(value, parent_id=parent_id, direction=direction)
            elif struct_type in ['bst', 'avl', 'huffman']:
                # 这些树形结构的 insert 不需要 index
                structure.insert(value)
            else:
                if index is None:
                    index = structure.size()
                structure.insert(index, value)

            op_record['details'] = {'value': value, 'index': index, 'direction': direction}

        elif isinstance(operation, DeleteOperation):
            tree_types = {'bst', 'binary', 'avl', 'huffman'}

            # 树结构：只按值删除，直接调用 delete(value)
            if struct_type in tree_types:
                # 优先使用 value；如果 DSL 写成 delete at X，也把 X 当值处理
                raw_value = operation.value if operation.value is not None else operation.index
                value = self.evaluate_value(raw_value)
                self.log(f"  delete value {value}")
                structure.delete(value)
                op_record['details'] = {'value': value}

            else:
                if operation.index is not None:
                    # 按索引删除
                    self.log(f"  delete at {operation.index}")
                    structure.delete(operation.index)
                    op_record['details'] = {'index': operation.index}
                elif operation.value is not None:
                    # 按值删除
                    value = self.evaluate_value(operation.value)
                    self.log(f"  delete value {value}")
                    # 先搜索找到索引
                    index = structure.search(value)
                    if index == -1:
                        self.log(f"    警告: 值 {value} 不存在")
                    else:
                        structure.delete(index)
                        self.log(f"    在索引 {index} 处删除")
                    op_record['details'] = {'value': value, 'index': index if index != -1 else None}
                else:
                    self.error("DeleteOperation requires either index or value")

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
            value = self.evaluate_value(operation.value)
            self.log(f"  push {value}")
            structure.push(value)
            op_record['details'] = {'value': value}

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

        elif isinstance(operation, EnqueueOperation):
            value = self.evaluate_value(operation.value)
            self.log(f"  enqueue {value}")
            if hasattr(structure, 'enqueue'):
                structure.enqueue(value)
            elif hasattr(structure, 'insert'):
                structure.insert(structure.size(), value)
            else:
                self.error(f"Structure does not support enqueue/insert")
            op_record['details'] = {'value': value}

        elif isinstance(operation, DequeueOperation):
            self.log(f"  dequeue")
            if hasattr(structure, 'dequeue'):
                result = structure.dequeue()
            elif hasattr(structure, 'delete'):
                result = structure.delete(0)
            else:
                self.error(f"Structure does not support dequeue/delete")
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, FrontOperation):
            self.log(f"  front")
            if hasattr(structure, 'front'):
                result = structure.front()
            elif hasattr(structure, 'get'):
                result = structure.get(0)
            else:
                self.error(f"Structure does not support front/get")
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, RearOperation):
            self.log(f"  rear")
            if hasattr(structure, 'rear'):
                result = structure.rear()
            elif hasattr(structure, 'get'):
                result = structure.get(structure.size() - 1)
            else:
                self.error(f"Structure does not support rear/get")
            self.log(f"    结果: {result}")
            op_record['details'] = {'result': result}

        elif isinstance(operation, BuildOperation):
            values = self.evaluate_value(operation.values)
            self.log(f"  build {values}")
            if hasattr(structure, 'build_from_list'):
                structure.build_from_list(values)
            op_record['details'] = {'values': values}

        elif isinstance(operation, TraverseOperation):
            self.log(f"  traverse {operation.method}")
            # 🎬 使用新的带动画的遍历方法
            if hasattr(structure, 'traverse_with_animation'):
                result = structure.traverse_with_animation(operation.method.lower())
                self.log(f"    结果: {result}")
                op_record['details'] = {'method': operation.method, 'result': result}
            else:
                # 兼容旧的遍历方法
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

        elif isinstance(operation, BuildNumbersOperation):
            numbers = self.evaluate_value(operation.numbers)
            self.log(f"  build_numbers {numbers}")
            if hasattr(structure, 'build_from_numbers'):
                structure.build_from_numbers(numbers)
            op_record['details'] = {'numbers': numbers}

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
            value = self.evaluate_value(operation.value)
            self.log(f"  insert_head {value}")
            structure.insert(0, value)
            op_record['details'] = {'value': value}

        elif isinstance(operation, InsertTailOperation):
            value = self.evaluate_value(operation.value)
            self.log(f"  insert_tail {value}")
            structure.insert(structure.size(), value)
            op_record['details'] = {'value': value}

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
        from dsvision.linear.queue import SequentialQueue
        from dsvision.tree.binary_tree import BinaryTree
        from dsvision.tree.binary_search_tree import BinarySearchTree
        from dsvision.tree.avl_tree import AVLTree
        from dsvision.tree.huffman import HuffmanTree

        type_map = {
            'sequential': SequentialList,
            'linked': LinearLinkedList,
            'stack': SequentialStack,
            'queue': SequentialQueue,
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
