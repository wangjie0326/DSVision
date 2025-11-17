"""
测试Huffman树数字模式构建
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsvision.tree.huffman import HuffmanTree

def test_number_mode():
    """测试数字模式"""
    print("=" * 60)
    print("测试Huffman树 - 数字模式")
    print("=" * 60)

    huffman = HuffmanTree()
    numbers = [2, 4, 6, 8]

    print(f"\n输入数字列表: {numbers}")
    success = huffman.build_from_numbers(numbers)

    print(f"\n构建成功: {success}")
    print(f"树大小: {huffman.size()}")

    # 打印操作历史
    print(f"\n操作历史 ({len(huffman.get_operation_history())} 步):")
    for i, step in enumerate(huffman.get_operation_history(), 1):
        print(f"\n步骤 {i}:")
        print(f"  描述: {step.description}")
        if hasattr(step, 'visual_hints') and step.visual_hints:
            print(f"  visual_hints: {step.visual_hints}")

    # 打印树结构
    print("\n树结构:")
    tree_data = huffman.get_tree_data()
    print(f"  根节点: {tree_data.get('root')}")
    print(f"  大小: {tree_data.get('size')}")

def test_text_mode():
    """测试文本模式"""
    print("\n" + "=" * 60)
    print("测试Huffman树 - 文本模式")
    print("=" * 60)

    huffman = HuffmanTree()
    text = "HELLO"

    print(f"\n输入文本: {text}")
    success = huffman.build_from_string(text)

    print(f"\n构建成功: {success}")
    print(f"树大小: {huffman.size()}")

    # 打印操作历史
    print(f"\n操作历史 ({len(huffman.get_operation_history())} 步):")
    for i, step in enumerate(huffman.get_operation_history(), 1):
        print(f"\n步骤 {i}:")
        print(f"  描述: {step.description}")
        if hasattr(step, 'visual_hints') and step.visual_hints:
            print(f"  visual_hints: {step.visual_hints}")

if __name__ == "__main__":
    test_number_mode()
    test_text_mode()
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)