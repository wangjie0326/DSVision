from dotenv import load_dotenv
load_dotenv()

import os
import sys
# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('/controller', ''))
from dsvision.extend2_llm.llm_service import LLMService

# 初始化LLM服务 (选择提供商)
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_BASE_URL = os.getenv('LLM_BASE_URL')  # 支持自定义URL

try:
    llm_service = LLMService(
        provider=LLM_PROVIDER,
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL
    )
    print(f"LLM服务已启用 - 提供商: {LLM_PROVIDER}")
except Exception as e:
    llm_service = None
    print(f"LLM服务未启用: {e}")


def _convert_tree_value(value):
    """统一转换树节点值的类型"""
    if value is None:
        return None

    # 尝试转换为数字
    try:
        # 先尝试整数
        if isinstance(value, str) and '.' not in value:
            return int(value)
        else:
            return float(value)
    except (ValueError, TypeError):
        # 如果转换失败，返回原字符串
        return str(value)


from flask import Flask,jsonify,request
from flask_cors import CORS
import uuid
from datetime import datetime
import sys
import os
#添加项目根目录到Python路径
#当前文件: DSVision/flask_interface/app.py
#dsvision目录: DSVision/dsvision/
#需要添加: DSVision/ 到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))  # flask_interface/
root_dir = os.path.dirname(current_dir)  # DSVision/
sys.path.insert(0, root_dir)

from dsvision.tree.avl_tree import AVLTree
import json

from dsvision.linear.sequential_list import SequentialList
from dsvision.linear.linked_list import LinearLinkedList
from dsvision.operation.operation import OperationType
from dsvision.linear.stack import SequentialStack
from dsvision.tree.binary_tree import BinaryTree
from dsvision.tree.binary_search_tree import BinarySearchTree
from dsvision.tree.huffman import HuffmanTree


app = Flask(__name__)


CORS(app)


#存储数据结构实例
structures = {}

@app.route('/', methods=['GET'])
def index():
    """根路径 - 显示 API 信息"""
    return jsonify({
        'message': 'DSVision API Server',
        'version': '1.0',
        'endpoints': {
            'health': '/api/health',
            'create': 'POST /api/structure/create',
            'state': 'GET /api/structure/<id>/state',
            'insert': 'POST /api/structure/<id>/insert',
            'delete': 'POST /api/structure/<id>/delete',
            'search': 'POST /api/structure/<id>/search',
            'clear': 'POST /api/structure/<id>/clear',
            'init_batch': 'POST /api/structure/<id>/init_batch',
        }
    })


@app.route('/health',methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'message': 'Flask服务器运行正常',
        'active_structures':len(structures)
    })

@app.route('/structure/create',methods=['POST', 'OPTIONS'])
def structure_create():
    """
    创建新的数据结构
    请求体“{
        "type":"sequential" | "linked" |"stack"|队列，树
        “capacity":100(可选，仅顺序表需要
    """
    try:
        data = request.json
        structure_type = data.get('type')
        capacity = data.get('capacity',100)

        structure_id = str(uuid.uuid4())#生成唯一id

        if structure_type == 'sequential':
            structures[structure_id] = SequentialList(capacity = capacity)
        elif structure_type == 'linked':
            structures[structure_id] = LinearLinkedList()
        elif structure_type == 'stack':
            structures[structure_id] = SequentialStack(capacity=capacity)
        elif structure_type == 'binary':
            structures[structure_id] = BinaryTree()
        elif structure_type == 'bst':
            structures[structure_id] = BinarySearchTree()
        elif structure_type == 'avl':  # 添加AVL树支持
            structures[structure_id] = AVLTree()
        elif structure_type == 'huffman':
            structures[structure_id] = HuffmanTree()
        ###此处可以扩展更多
        else:
            return jsonify({'error': f'未知的数据结构类型: {structure_type}'}), 400

        return jsonify({
            'success': True,
            'structure_id': structure_id,
            'type': structure_type,
            'message':f"成功创建{structure_type}结构"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/structure/<structure_id>/state',methods=['GET'])
def get_state(structure_id):
    """
    获取数据结构当前状态
    返回{
    "data：[]#当前数据
    “size”：3，
    ‘operation_history":[...]#操作历史
    """
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error':'结构不存在，请先创建'}),404
        #调用类方法
        return jsonify({
            'data':structure.to_list(),
            'size':structure.size(),
            'is_empty':structure.is_empty(),
            'operation_history':[step.to_dict() for step in structure.get_operation_history()],
            'capacity':getattr(structure,'_capacity',None) #没懂getattr
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/structure/<structure_id>/init_batch', methods=['POST'])
def init_batch(structure_id):
    """
    批量初始化数据结构
    请求体: {
        "values": [1, 2, 3, 4, 5]  # 或 "1,2,3,4,5" 或 "1 2 3 4 5"
    }
    """
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error': '结构不存在，请先创建'}), 404

        data = request.json
        values_input = data.get('values')

        # 处理不同格式的输入
        if isinstance(values_input, str):
            # 支持逗号或空格分隔
            values_input = values_input.replace(',', ' ')
            values = [v.strip() for v in values_input.split() if v.strip()]
        elif isinstance(values_input, list):
            values = values_input
        else:
            return jsonify({'error': '无效的输入格式'}), 400

        # 调用批量初始化方法
        success = structure.initlist(values)

        return jsonify({
            'success': success,
            'data': structure.to_list(),
            'size': structure.size(),
            'operation_history': [step.to_dict() for step in structure.get_operation_history()]
        })

    except Exception as e:
        print(f"批量初始化错误: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/structure/<structure_id>/insert',methods=['POST', 'OPTIONS'])
def insert_element(structure_id):
    """
    插入元素，调用insert方法
    请求体:{
        "insert":0,#位置
        "value":"test"，#值
    }
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error':'结构不存在，请先创建'}),404

        data = request.json
        print(f"收到插入请求: {data}")  # 调试输出

        index = data.get('index')
        value = data.get('value')

        #确保参数正确
        if index is None:
            index = structure.size()  #默认插入到末尾
        else:
            index = int(index)
        print(f"插入参数 - index: {index}, value: {value}")  #调试输出

        # 清空历史，准备记录新的操作步骤
        structure.clear_operation_history()

        # 执行插入
        success = structure.insert(index, value)

        #返回更新后的状态
        return jsonify({
            'success': success,
            'data': structure.to_list(),
            'size': structure.size(),
            'operation_history':[step.to_dict() for step in structure.get_operation_history()]
        })

    except Exception as e:
        print(f"插入元素错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/structure/<structure_id>/delete',methods=['POST'])
def delete_element(structure_id):
    """
    删除元素-调用delete方法
    请求体:{
        "delete":0,#要删除的位置
    }
    """
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error':'结构不存在，请先创建'}),404

        data = request.json
        index = data.get('index')

        # 清空历史
        structure.clear_operation_history()
        #调用delete方法
        deleted_value = structure.delete(index)

        return jsonify({
            'success': deleted_value is not None,
            'deleted_value': deleted_value,
            'data': structure.to_list(),
            'size': structure.size(),
            'operation_history':[step.to_dict() for step in structure.get_operation_history()]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/structure/<structure_id>/search',methods=['POST'])
def search_element(structure_id):
    """
        搜索元素-调用delete方法
        请求体:{
            "value":“test”,#要搜索的值
        }
        """
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error':'结构不存在，请先创建'}),404

        data = request.json
        value = data.get('value')

        #调用search方法
        result_index = structure.search(value)

        return jsonify({
            'found':result_index != -1,
            'index':result_index,
            'data': structure.to_list(),
            'size': structure.size(),
            'operation_history':[step.to_dict() for step in structure.get_operation_history()]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/structure/<structure_id>/clear',methods=['POST'])
def clear_structure(structure_id):
    """清空数据结构"""
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error':'结构不存在，请先创建'}),404

        #清空数据和历史
        structure.clear_operation_history()

        #重新初始化
        if isinstance(structure,SequentialList):
            structure._data = [None]*structure._capacity
            structure._size = 0
        elif isinstance(structure,LinearLinkedList):
            structure._head = None
            structure._size = 0
        return jsonify({
            'success': True,
            'data': structure.to_list(),
            'size': structure.size(),
            'operation_history':[]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/structure/<structure_id>',methods=['DELETE'])
def delete_structure(structure_id):
    """删除数据结构"""
    try:
        if structure_id in structures:
            del structures[structure_id]
            return jsonify({
                'success': True,
                'message':'结构已删除'
            })
        else:
            return jsonify({'error': '结构不存在'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 树结构路由 ====================
@app.route('/tree/create', methods=['POST', 'OPTIONS'])
def tree_create():
    """创建树结构"""
    try:
        data = request.json
        structure_type = data.get('type')
        structure_id = str(uuid.uuid4())

        if structure_type == 'binary':
            structures[structure_id] = BinaryTree()
        elif structure_type == 'bst':
            structures[structure_id] = BinarySearchTree()
        elif structure_type == 'avl':  # 添加AVL树支持
            structures[structure_id] = AVLTree()
        elif structure_type == 'huffman':
            structures[structure_id] = HuffmanTree()
        else:
            return jsonify({'error': f'未知的树类型: {structure_type}'}), 400

        return jsonify({
            'success': True,
            'structure_id': structure_id,
            'type': structure_type,
            'message': f"成功创建{structure_type}树结构"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tree/<structure_id>/state', methods=['GET'])
def get_tree_state(structure_id):
    """获取树状态"""
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error': '结构不存在'}), 404

        return jsonify({
            'tree_data': structure.get_tree_data(),
            'size': structure.size(),
            'is_empty': structure.is_empty(),
            'operation_history': [step.to_dict() for step in structure.get_operation_history()]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tree/<structure_id>/insert', methods=['POST'])
def insert_tree_node(structure_id):
    """插入树节点"""
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error': '结构不存在'}), 404

        data = request.json
        value = data.get('value')

        # 🔥 关键: 清空历史记录
        structure.clear_operation_history()

        value = _convert_tree_value(value)

        success = structure.insert(value)

        # 🔥 打印调试信息
        tree_data = structure.get_tree_data()
        operation_history = structure.get_operation_history()
        print(f"插入节点 {value}, 成功: {success}")
        print(f"树大小: {tree_data.get('size', 0)}")
        print(f"操作步骤数: {len(operation_history)}")

        return jsonify({
            'success': success,
            'tree_data': structure.get_tree_data(),
            'operation_history': [step.to_dict() for step in structure.get_operation_history()]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tree/<structure_id>/delete', methods=['POST'])
def delete_tree_node(structure_id):
    """删除树节点"""
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error': '结构不存在'}), 404

        data = request.json
        value = data.get('value')

        value = _convert_tree_value(value)

        success = structure.delete(value)

        return jsonify({
            'success': success,
            'tree_data': structure.get_tree_data(),
            'operation_history': [step.to_dict() for step in structure.get_operation_history()]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tree/<structure_id>/search', methods=['POST'])
def search_tree_node(structure_id):
    """搜索树节点"""
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error': '结构不存在'}), 404

        data = request.json
        value = data.get('value')

        value = _convert_tree_value(value)

        node = structure.search(value)

        return jsonify({
            'found': node is not None,
            'tree_data': structure.get_tree_data(),
            'operation_history': [step.to_dict() for step in structure.get_operation_history()]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tree/<structure_id>/clear', methods=['POST'])
def clear_tree(structure_id):
    """清空树"""
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error': '结构不存在'}), 404

        structure.clear()

        return jsonify({
            'success': True,
            'tree_data': structure.get_tree_data(),
            'operation_history': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tree/<structure_id>', methods=['DELETE'])
def delete_tree(structure_id):
    """删除树结构"""
    try:
        if structure_id in structures:
            del structures[structure_id]
            return jsonify({
                'success': True,
                'message': '树结构已删除'
            })
        else:
            return jsonify({'error': '结构不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Huffman树专用路由
@app.route('/tree/<structure_id>/huffman/build', methods=['POST'])
def build_huffman_tree(structure_id):
    """从文本构建Huffman树"""
    try:
        structure = structures.get(structure_id)
        if not structure or not isinstance(structure, HuffmanTree):
            return jsonify({'error': '不是Huffman树结构'}), 404

        data = request.json
        text = data.get('text')

        print(f"收到构建请求, 文本: {text}")  # 调试日志

        success = structure.build_from_string(text)

        tree_data = structure.get_tree_data()
        print(f"树数据: {tree_data}")  # 调试日志
        print(f"root: {tree_data.get('root')}")  # 调试日志

        return jsonify({
            'success': success,
            'tree_data': tree_data,
            'operation_history': [step.to_dict() for step in structure.get_operation_history()]
        })
    except Exception as e:
        print(f"错误: {e}")  # 调试日志
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# 添加导出功能
@app.route('/structure/<structure_id>/export', methods=['GET'])
def export_structure(structure_id):
    """导出数据结构到JSON"""
    try:
        structure = structures.get(structure_id)
        if not structure:
            return jsonify({'error': '结构不存在'}), 404

        # 判断是线性结构还是树结构
        if hasattr(structure, 'to_list'):
            # 线性结构
            export_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'structure_type': type(structure).__name__,
                'category': 'linear',
                'data': structure.to_list(),
                'size': structure.size(),
                'capacity': getattr(structure, '_capacity', None)
            }
        else:
            #树结构
            tree_data = structure.get_tree_data()
            export_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'structure_type': type(structure).__name__,
                'category': 'tree',
                'tree_data': tree_data,
                'huffman_codes': tree_data.get('huffman_codes') if hasattr(structure, '_huffman_codes') else None,
            }

        print(f"导出数据结构: {export_data['structure_type']}, size={export_data.get('size', 'N/A')}")
        return jsonify(export_data)

    except Exception as e:
        print(f"导出失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# 添加导入功能
@app.route('/structure/import', methods=['POST'])
def import_structure():
    """从JSON导入数据结构"""
    try:
        data = request.json

        if not data or 'structure_type' not in data:
            return jsonify({'error': '无效的导入数据'}), 400

        structure_type_name = data['structure_type']
        category = data.get('category', 'linear')
        structure_id = str(uuid.uuid4()) #生成新id

        # 根据类型创建结构
        type_mapping = {
            'SequentialList': ('sequential', SequentialList),
            'LinearLinkedList': ('linked', LinearLinkedList),
            'SequentialStack': ('stack', SequentialStack),
            'BinaryTree': ('binary', BinaryTree),
            'BinarySearchTree': ('bst', BinarySearchTree),
            'AVLTree': ('avl', AVLTree),
            'HuffmanTree': ('huffman', HuffmanTree)
        }

        if structure_type_name not in type_mapping:
            return jsonify({'error': f'不支持的结构类型: {structure_type_name}'}), 400

        structure_type, structure_class = type_mapping[structure_type_name]

        # 创建结构实例
        if structure_type in ['sequential', 'stack']:
            capacity = data.get('capacity', 100)
            structure = structure_class(capacity=capacity)
        else:
            structure = structure_class()

        # 恢复数据
        if category == 'linear':
            # 线性结构：批量插入数据
            linear_data = data.get('data', [])
            if structure_type == 'stack':
                # 栈：依次 push
                for value in linear_data:
                    structure.push(value)
                    print(f"  ✓ Push: {value}")
            else:
                # 顺序表/链表：使用 initlist 批量初始化
                if hasattr(structure, 'initlist') and linear_data:
                    structure.clear_operation_history()  # 清空初始化时的历史
                    structure.initlist(linear_data)
                    print(f"  ✓ 批量初始化: {linear_data}")
                else:
                    # 如果没有 initlist，逐个插入
                    for i, value in enumerate(linear_data):
                        structure.insert(i, value)
                        print(f"  ✓ Insert[{i}]: {value}")
            print(f"线性结构恢复完成，当前大小: {structure.size()}")

        else:
            tree_data = data.get('tree_data', {})
            # 树结构：根据类型恢复
            if structure_type == 'huffman':
                # Huffman树需要特殊处理
                if 'huffman_text' in data:
                    text = data['huffman_text']
                    structure.build_from_string(text)
                    print(f"  ✓ 从文本重建: {text}")
                elif tree_data.get('huffman_codes'):
                    # 从编码表重建（需要反推权重）
                    # 简化：从层序遍历重建
                    levelorder = tree_data.get('traversals', {}).get('levelorder', [])
                    if levelorder:
                        # Huffman树无法直接从遍历序列重建，需要保存权重信息
                        print("Huffman树需要保存原始文本或权重信息")
                else:
                    print("Huffman树缺少重建信息")
            else:
                # 普通树：从层序遍历重建
                levelorder = tree_data.get('traversals', {}).get('levelorder', [])
                print(f"📊 恢复树数据 (层序): {levelorder}")

                # 清空初始化历史
                structure.clear_operation_history()

                # 逐个插入节点
                for value in levelorder:
                    # 转换类型（重要！）
                    converted_value = _convert_tree_value(value)
                    structure.insert(converted_value)
                    print(f"  ✓ Insert: {converted_value}")

                print(f"树结构恢复完成，节点数: {structure.size()}")

        #保存到全局字典
        structures[structure_id] = structure

        # 验证恢复结果
        if category == 'linear':
            restored_data = structure.to_list()
            print(f"🔍 验证恢复数据: {restored_data}")
        else:
            restored_tree = structure.get_tree_data()
            print(f"🔍 验证恢复树: size={restored_tree.get('size')}")


        return jsonify({
            'success': True,
            'structure_id': structure_id,
            'type': structure_type,
            'message': f'成功导入{structure_type_name}',
            #用于前端验证
            'restored_size': structure.size()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

from dsvision.extend1_dsl.lexer import Lexer
from dsvision.extend1_dsl.parser import Parser
from dsvision.extend1_dsl.interpreter import Interpreter, SimpleStructureManager
# 全局解释器管理器
interpreters = {}
@app.route('/dsl/execute', methods=['POST'])
def execute_dsl():
    """
    执行dsl代码
    请求体: {
        "code": "Sequential myList { init [1,2,3] insert 10 at 2 }",
        "session_id": "optional-session-id"  # 可选,用于保持会话
    }
    """
    try:
        ##获取请求数据
        data = request.json
        dsl_code = data.get('code', '')
        session_id = data.get('session_id', str(uuid.uuid4()))

        if not dsl_code.strip():
            return jsonify({'error': 'DSL 代码不能为空'}), 400

        print(f"\n{'=' * 60}")
        print(f"收到 DSL 执行请求 (Session: {session_id})")
        print(f"代码:\n{dsl_code}")
        print(f"{'=' * 60}\n")

        #词法分析
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()
        print(f"✓ 词法分析完成, Token 数: {len(tokens)}")

        #语法分析
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"✓ 语法分析完成, 结构数: {len(ast.structures)}")

        #创建或获取解释器
        if session_id not in interpreters:
            manager = SimpleStructureManager()
            interpreters[session_id] = Interpreter(manager)

        interpreter = interpreters[session_id]

        # 执行dsl
        result = interpreter.execute(ast)  # 修复: 使用正确的方法名
        print(f"✓ DSL 执行完成")

        #提取结构信息
        response_data = {
            'success': True,
            'session_id': session_id,
            'execution_log':result['execution_log'],
            'structures': []
        }

        #遍历每个创建的结构
        for struct_name, struct_result in result['results'].items():
            struct_type = struct_result['type']

            # 从解释器上下文中获取实际的结构实例
            if struct_name in interpreter.context.structures:
                struct_info = interpreter.context.structures[struct_name]
                structure = struct_info['instance']

                # 注册到全局 structures 字典,生成 ID
                structure_id = str(uuid.uuid4())
                structures[structure_id] = structure

                # 准备返回数据
                struct_data = {
                    'name': struct_name,
                    'type': struct_type,
                    'structure_id': structure_id,
                    'operations_count': struct_result['operations_count']
                }

                # 根据结构类型返回数据
                if struct_type in ['sequential', 'linked', 'stack', 'queue']:
                    # 线性结构
                    struct_data['data'] = structure.to_list()
                    struct_data['size'] = structure.size()
                    struct_data['category'] = 'linear'
                elif struct_type in ['binary', 'bst', 'avl', 'huffman']:
                    # 树结构
                    struct_data['tree_data'] = structure.get_tree_data()
                    struct_data['size'] = structure.size()
                    struct_data['category'] = 'tree'

                    # Huffman 特殊处理
                    if struct_type == 'huffman' and hasattr(structure, 'get_huffman_codes'):
                        struct_data['huffman_codes'] = structure.get_huffman_codes()

                response_data['structures'].append(struct_data)

        print(f"\n✓ 成功执行,返回 {len(response_data['structures'])} 个结构\n")
        return jsonify(response_data)

    except SyntaxError as e:
        print(f"✗ 语法错误: {e}")
        return jsonify({
            'success': False,
            'error': f'语法错误: {str(e)}',
            'error_type': 'SyntaxError'
        }), 400

    except Exception as e:
        print(f"✗ 执行错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/dsl/validate', methods=['POST'])
def validate_dsl():
    """
    验证 DSL 代码语法
    请求体: { "code": "..." }
    """
    try:
        data = request.json
        dsl_code = data.get('code', '')

        # 词法分析
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()

        # 语法分析
        parser = Parser(tokens)
        ast = parser.parse()

        return jsonify({
            'valid': True,
            'token_count': len(tokens),
            'structure_count': len(ast.structures),
            'message': '代码语法正确'
        })

    except SyntaxError as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'error_type': 'SyntaxError'
        }), 400

    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 400


@app.route('/dsl/session/<session_id>', methods=['DELETE'])
def delete_dsl_session(session_id):
    """删除 DSL 会话"""
    try:
        if session_id in interpreters:
            # 清理解释器中的结构
            interpreter = interpreters[session_id]
            for struct_name in list(interpreter.context.structures.keys()):
                struct_info = interpreter.context.structures[struct_name]
                # 从全局 structures 中移除
                for sid, s in list(structures.items()):
                    if s is struct_info['instance']:
                        del structures[sid]

            del interpreters[session_id]
            return jsonify({
                'success': True,
                'message': f'会话 {session_id} 已删除'
            })
        else:
            return jsonify({'error': '会话不存在'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dsl/examples', methods=['GET'])
def get_dsl_examples():
    """获取 DSL 示例代码"""
    examples = {
        'sequential': """Sequential myList {
    init [1, 2, 3, 4, 5]
    insert 10 at 2
    search 10
    delete at 3
}""",
        'linked': """Linked myLinkedList {
    init [1, 2, 3]
    insert_head 0
    insert_tail 4
    search 2
}""",
        'stack': """Stack myStack {
    push 1
    push 2
    push 3
    peek
    pop
}""",
        'bst': """BST myBST {
    insert 50
    insert 30
    insert 70
    insert 20
    insert 40
    traverse inorder
    min
    max
}""",
        'avl': """AVL myAVL {
    insert 10
    insert 20
    insert 30
    insert 40
    insert 50
    traverse levelorder
}""",
        'huffman': """Huffman myHuffman {
    build_text "ABRACADABRA"
    show_codes
    encode "ABRA"
}""",
        'complex': """// 复杂示例：多个结构
Sequential list1 {
    init [1, 2, 3, 4, 5]
    insert 10 at 2
}

BST tree1 {
    insert 50
    insert 30
    insert 70
    traverse inorder
}

Stack stack1 {
    push 1
    push 2
    push 3
}"""
    }

    return jsonify({
        'examples': examples,
        'categories': {
            'linear': ['sequential', 'linked', 'stack'],
            'tree': ['bst', 'avl', 'huffman'],
            'complex': ['complex']
        }
    })


# ==================== LLM 路由 ====================

@app.route('/api/llm/chat', methods=['POST'])
def llm_chat():
    """
    LLM对话接口 - 自然语言转DSL

    请求体: {
        "message": "创建一个包含5,3,7的二叉搜索树",
        "session_id": "optional-session-id"
    }
    """
    try:
        if not llm_service:
            return jsonify({
                'success': False,
                'error': 'LLM服务未配置',
                'message': '请设置环境变量 LLM_PROVIDER 和 LLM_API_KEY'
            }), 503

        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))

        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400

        print(f"\n{'=' * 60}")
        print(f"[LLM Chat] Session: {session_id}")
        print(f"用户: {user_message}")
        print(f"{'=' * 60}\n")

        # 调用LLM生成DSL
        result = llm_service.natural_language_to_dsl(user_message)

        if not result['success']:
            return jsonify({
                'success': False,
                'error': result.get('error', '未知错误'),
                'provider': result.get('provider')
            }), 500

        dsl_code = result['dsl_code']
        explanation = result['explanation']

        # 如果生成了DSL代码,自动执行
        execution_result = None
        if dsl_code and dsl_code.strip():
            print(f"✓ 自动执行生成的DSL代码\n")

            try:
                # 复用DSL执行逻辑
                from dsvision.extend1_dsl.lexer import Lexer
                from dsvision.extend1_dsl.parser import Parser
                from dsvision.extend1_dsl.interpreter import Interpreter, SimpleStructureManager

                # 词法+语法分析
                lexer = Lexer(dsl_code)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()

                # 创建解释器
                if session_id not in interpreters:
                    manager = SimpleStructureManager()
                    interpreters[session_id] = Interpreter(manager)

                interpreter = interpreters[session_id]
                exec_result = interpreter.execute(ast)

                # 提取结构信息
                structures_data = []
                for struct_name, struct_result in exec_result['results'].items():
                    if struct_name in interpreter.context.structures:
                        struct_info = interpreter.context.structures[struct_name]
                        structure = struct_info['instance']

                        # 注册到全局字典
                        structure_id = str(uuid.uuid4())
                        structures[structure_id] = structure

                        struct_data = {
                            'name': struct_name,
                            'type': struct_result['type'],
                            'structure_id': structure_id,
                            'operations_count': struct_result['operations_count'],
                            # 🔥 添加操作历史以支持动画播放
                            'operation_history': [step.to_dict() for step in structure.get_operation_history()]
                        }

                        # 根据类型添加数据
                        if struct_result['type'] in ['sequential', 'linked', 'stack', 'queue']:
                            struct_data['data'] = structure.to_list()
                            struct_data['size'] = structure.size()
                            struct_data['category'] = 'linear'
                        else:
                            struct_data['tree_data'] = structure.get_tree_data()
                            struct_data['size'] = structure.size()
                            struct_data['category'] = 'tree'

                        structures_data.append(struct_data)

                execution_result = {
                    'success': True,
                    'structures': structures_data,
                    'execution_log': exec_result['execution_log']
                }

                print(f"✓ DSL执行成功,创建了 {len(structures_data)} 个结构\n")

            except Exception as exec_error:
                print(f"✗ DSL执行失败: {exec_error}\n")
                execution_result = {
                    'success': False,
                    'error': str(exec_error)
                }

        return jsonify({
            'success': True,
            'session_id': session_id,
            'llm_response': {
                'dsl_code': dsl_code,
                'explanation': explanation,
                'provider': result.get('provider')
            },
            'execution': execution_result
        })

    except Exception as e:
        print(f"✗ LLM Chat错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500


@app.route('/api/llm/status', methods=['GET'])
def llm_status():
    """检查LLM服务状态"""
    if llm_service:
        return jsonify({
            'enabled': True,
            'provider': LLM_PROVIDER,
            'message': 'LLM服务运行中'
        })
    else:
        return jsonify({
            'enabled': False,
            'message': 'LLM服务未配置'
        }), 503


@app.route('/api/llm/config', methods=['GET', 'POST'])
def llm_config():
    """
    获取或更新LLM配置
    GET: 返回当前配置
    POST: { "provider": "openai", "api_key": "sk-...", "base_url": "https://..." (可选) }
    """
    global llm_service, LLM_PROVIDER, LLM_API_KEY, LLM_BASE_URL

    if request.method == 'GET':
        return jsonify({
            'provider': LLM_PROVIDER,
            'api_key_set': bool(LLM_API_KEY),
            'base_url': LLM_BASE_URL or '(使用默认)',
            'available_providers': ['openai']
        })

    elif request.method == 'POST':
        try:
            data = request.json
            provider = data.get('provider', LLM_PROVIDER)
            api_key = data.get('api_key', LLM_API_KEY)
            base_url = data.get('base_url', LLM_BASE_URL)

            if not api_key:
                return jsonify({'error': 'API密钥不能为空'}), 400

            # 更新全局配置
            LLM_PROVIDER = provider
            LLM_API_KEY = api_key
            LLM_BASE_URL = base_url

            # 重新初始化服务
            llm_service = LLMService(provider=provider, api_key=api_key, base_url=base_url)

            return jsonify({
                'success': True,
                'provider': provider,
                'base_url': base_url or '(使用默认)',
                'message': 'LLM配置已更新'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
if __name__ == '__main__':
    app.run()
    print("-"*50)
    print("启动Flask服务器")
    print("-"*50)
    print("后端地址：http://localhost:5000")#疑问
    print("前端地址：http://localhost:8080")
    print("健康检查: http://localhost:5000/api/health")
    print("-" * 50)
    print("可用的API端口如下：")
    print("  POST   /api/structure/create           - 创建数据结构")
    print("  GET    /api/structure/<id>/state       - 获取状态")
    print("  POST   /api/structure/<id>/insert      - 插入元素")
    print("  POST   /api/structure/<id>/delete      - 删除元素")
    print("  POST   /api/structure/<id>/search      - 搜索元素")
    print("  POST   /api/structure/<id>/clear       - 清空结构")
    print("  DELETE /api/structure/<id>             - 删除结构")
    print("-" * 50)