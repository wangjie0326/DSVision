#!/usr/bin/env python
"""生成AVL测试数据,用于前端调试"""

import json
from dsvision.tree.avl_tree import AVLTree

def generate_test_data():
    """生成AVL树插入数据用于前端测试"""
    avl = AVLTree()

    # 构建会触发旋转的场景
    avl.insert(50)
    avl.insert(30)

    # 清空历史,只看插入10的步骤
    avl.clear_operation_history()
    avl.insert(10)  # 这会触发LL旋转

    history = avl.get_operation_history()

    print("=" * 70)
    print("AVL插入节点10的完整动画步骤 (会触发LL旋转)")
    print("=" * 70)
    print()

    for i, step in enumerate(history, 1):
        print(f"步骤 {i}: {step.description}")
        print(f"  - duration: {getattr(step, 'duration', 0.5)}秒")
        print(f"  - animation_type: {getattr(step, 'animation_type', 'none')}")
        print(f"  - highlight_indices: {getattr(step, 'highlight_indices', [])}")

        if '✏️' in step.description:
            print(f"  🔥 这是虚线节点步骤!")
            print(f"  🔥 前端应该显示浅绿色虚线节点,持续{getattr(step, 'duration', 0.5)}秒")

            # 检查tree_snapshot是否存在
            if hasattr(step, 'tree_snapshot') and step.tree_snapshot:
                print(f"  ✓ 有tree_snapshot,节点已插入到树中")
                # 打印树的简化结构
                def print_tree(node, prefix="", is_tail=True):
                    if node:
                        print(f"  {prefix}{'└── ' if is_tail else '├── '}{node.get('value', '?')}")
                        children = []
                        if node.get('left'):
                            children.append((node['left'], False))
                        if node.get('right'):
                            children.append((node['right'], True))
                        for child, is_last in children:
                            print_tree(child, prefix + ("    " if is_tail else "│   "), is_last)

                print("  树结构:")
                print_tree(step.tree_snapshot)

        print()

    print("=" * 70)
    print("前端调试提示:")
    print("1. 打开浏览器开发者工具 Console")
    print("2. 插入节点时查看console.log输出")
    print("3. 检查 'dashedNodes' 是否被正确设置")
    print("4. 检查虚线节点的CSS class 'dashed-node' 是否被应用")
    print("=" * 70)

if __name__ == "__main__":
    generate_test_data()
