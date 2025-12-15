#!/usr/bin/env python
"""测试AVL树的虚线节点步骤"""

import sys
import json
sys.path.insert(0, '/')

from dsvision.tree.avl_tree import AVLTree

def test_avl_animation():
    print("\n" + "="*60)
    print("测试AVL树旋转动画步骤")
    print("="*60)

    # 创建AVL树
    avl = AVLTree()

    # 插入节点触发旋转
    print("\n插入 10...")
    avl.insert(10)

    print("\n插入 20...")
    avl.insert(20)

    print("\n插入 30 (会触发RR旋转)...")
    avl.insert(30)

    # 获取操作历史
    history = avl.get_operation_history()

    print(f"\n操作历史共 {len(history)} 步:")
    print("-" * 60)

    for i, step in enumerate(history, 1):
        step_dict = step.to_dict()
        print(f"\n步骤 {i}: {step.description}")

        # 检查是否是虚线节点步骤
        if '✏️' in step.description:
            print(f"  🔵 这是虚线节点步骤!")
            print(f"  - highlight_indices: {step.highlight_indices}")
            print(f"  - 有tree_snapshot: {step.tree_snapshot is not None}")

            if step.tree_snapshot:
                # 检查tree_snapshot中是否有节点30
                def find_value_in_tree(node_dict, value):
                    if not node_dict:
                        return False
                    if node_dict.get('value') == value:
                        return True
                    return (find_value_in_tree(node_dict.get('left'), value) or
                           find_value_in_tree(node_dict.get('right'), value))

                has_30 = find_value_in_tree(step.tree_snapshot.get('root'), 30)
                print(f"  - tree_snapshot包含节点30: {has_30}")

        # 检查是否是失衡检测步骤
        if '⚠️' in step.description:
            print(f"  ⚠️ 这是失衡检测步骤!")
            print(f"  - highlight_indices: {step.highlight_indices}")

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == '__main__':
    test_avl_animation()
