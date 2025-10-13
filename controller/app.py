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
#添加项目根目录到Python路径，不知道为什么要这样？？？
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
            'operation_history':[step.to_dict() for step in structure.get_operation_history],
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

        #调用你的insert方法
        success = structure.insert(index,value)

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

        try:
            value = int(value)  # 尝试转为整数
        except (ValueError, TypeError):
            pass  # 保持原类型

        value = _convert_tree_value(value)

        success = structure.insert(value)

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

        success = structure.build_from_string(text)

        return jsonify({
            'success': success,
            'tree_data': structure.get_tree_data(),
            'operation_history': [step.to_dict() for step in structure.get_operation_history()]
        })
    except Exception as e:
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
                'capacity': getattr(structure, '_capacity', None),
                'operation_history': [step.to_dict() for step in structure.get_operation_history()]
            }
        else:
            # 树结构
            export_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'structure_type': type(structure).__name__,
                'category': 'tree',
                'tree_data': structure.get_tree_data(),
                'operation_history': [step.to_dict() for step in structure.get_operation_history()]
            }

        return jsonify(export_data)

    except Exception as e:
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
        structure_id = str(uuid.uuid4())

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
            for value in linear_data:
                if structure_type == 'stack':
                    structure.push(value)
                else:
                    structure.insert(structure.size(), value)
        else:
            # 树结构：根据类型恢复
            if structure_type == 'huffman':
                # Huffman树需要特殊处理
                if 'huffman_text' in data:
                    structure.build_from_string(data['huffman_text'])
                elif 'huffman_weights' in data:
                    structure.build_from_weights(data['huffman_weights'])
            else:
                # 普通树：通过遍历序列重建
                tree_data = data.get('tree_data', {})
                traversal = tree_data.get('traversals', {}).get('levelorder', [])
                for value in traversal:
                    structure.insert(value)

        structures[structure_id] = structure

        return jsonify({
            'success': True,
            'structure_id': structure_id,
            'type': structure_type,
            'message': f'成功导入{structure_type_name}'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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