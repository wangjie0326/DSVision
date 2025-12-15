#!/usr/bin/env python3
"""
顺序表扩容功能测试脚本
测试扩容逻辑和动画步骤记录
"""

from dsvision.linear.sequential_list import SequentialList
from dsvision.operation.operation import OperationType


def test_expansion_basic():
    """测试基本扩容功能"""
    print("=" * 60)
    print("测试 1: 基本扩容功能")
    print("=" * 60)

    # 创建容量为 3 的顺序表
    seq = SequentialList(capacity=3)

    # 插入 3 个元素（填满）
    print("\n插入前 3 个元素...")
    seq.insert(0, 10)
    seq.insert(1, 20)
    seq.insert(2, 30)

    print(f"当前容量: {seq.get_capacity()}")
    print(f"当前大小: {seq.get_used_size()}")
    print(f"数据: {seq.to_list()[:seq.get_used_size()]}")

    # 插入第 4 个元素（触发扩容）
    print("\n插入第 4 个元素（应该触发扩容）...")
    result = seq.insert(3, 40)

    print(f"插入结果: {result}")
    print(f"扩容后容量: {seq.get_capacity()} (应为 4 或 5)")
    print(f"当前大小: {seq.get_used_size()}")
    print(f"数据: {seq.to_list()[:seq.get_used_size()]}")

    # 检查操作历史
    history = seq.get_operation_history()
    expand_ops = [op for op in history if op.operation == OperationType.EXPAND]
    print(f"\n✓ 扩容操作记录数: {len(expand_ops)}")

    return len(expand_ops) > 0


def test_expansion_animation_steps():
    """测试扩容动画步骤"""
    print("\n" + "=" * 60)
    print("测试 2: 扩容动画步骤")
    print("=" * 60)

    # 创建容量为 2 的顺序表
    seq = SequentialList(capacity=2)

    # 填满
    seq.insert(0, 100)
    seq.insert(1, 200)

    # 清空历史，只关注扩容操作
    seq._operation_history = []

    # 触发扩容
    print("\n触发扩容...")
    seq.insert(2, 300)

    # 分析操作历史
    history = seq.get_operation_history()
    print(f"\n总操作步骤数: {len(history)}")

    expand_steps = [op for op in history if op.operation == OperationType.EXPAND]
    print(f"扩容相关步骤数: {len(expand_steps)}")

    print("\n扩容动画步骤详情:")
    for i, step in enumerate(expand_steps, 1):
        print(f"\n步骤 {i}:")
        print(f"  描述: {step.description}")
        print(f"  动画类型: {step.animation_type}")
        print(f"  持续时间: {step.duration}s")
        if step.visual_hints:
            print(f"  视觉提示: {list(step.visual_hints.keys())}")

    # 验证关键步骤
    has_new_array = any('new_array' in (op.visual_hints or {}) for op in expand_steps)
    has_delete_mark = any((op.visual_hints or {}).get('old_array_delete') for op in expand_steps)
    has_completion = any('扩容完成' in op.description for op in expand_steps)

    print(f"\n✓ 包含新数组创建: {has_new_array}")
    print(f"✓ 包含旧数组删除标记: {has_delete_mark}")
    print(f"✓ 包含扩容完成提示: {has_completion}")

    return has_new_array and has_delete_mark and has_completion


def test_multiple_expansions():
    """测试多次扩容"""
    print("\n" + "=" * 60)
    print("测试 3: 多次扩容")
    print("=" * 60)

    # 创建容量为 2 的顺序表
    seq = SequentialList(capacity=2)

    print("\n连续插入 10 个元素...")
    for i in range(10):
        old_cap = seq.get_capacity()
        seq.insert(i, i * 10)
        new_cap = seq.get_capacity()

        if new_cap > old_cap:
            print(f"第 {i+1} 次插入时扩容: {old_cap} -> {new_cap}")

    print(f"\n最终容量: {seq.get_capacity()}")
    print(f"最终大小: {seq.get_used_size()}")
    print(f"数据: {seq.to_list()[:seq.get_used_size()]}")

    # 统计扩容次数
    history = seq.get_operation_history()
    expand_ops = [op for op in history if op.operation == OperationType.EXPAND and '容量已满' in op.description]
    print(f"\n✓ 总扩容次数: {len(expand_ops)}")

    return len(expand_ops) >= 3


def test_dsl_with_capacity():
    """测试 DSL 的 capacity 参数"""
    print("\n" + "=" * 60)
    print("测试 4: DSL capacity 参数")
    print("=" * 60)

    from dsvision.extend1_dsl.lexer import Lexer
    from dsvision.extend1_dsl.parser import Parser
    from dsvision.extend1_dsl.interpreter import Interpreter

    # 测试 DSL 代码
    dsl_code = """
    Sequential myList {
        init [1, 2, 3] capacity 5
        insert 4
        insert 5
        insert 6
    }
    """

    print("DSL 代码:")
    print(dsl_code)

    try:
        # 解析和执行
        lexer = Lexer(dsl_code)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        interpreter = Interpreter()
        result = interpreter.interpret(ast)

        # 检查结果
        if result.get('myList'):
            structure = result['myList']['structure']
            print(f"\n✓ 初始容量: {structure.get_capacity()}")
            print(f"✓ 当前大小: {structure.get_used_size()}")
            print(f"✓ 数据: {structure.to_list()[:structure.get_used_size()]}")

            # 检查是否触发了扩容
            history = structure.get_operation_history()
            expand_ops = [op for op in history if op.operation == OperationType.EXPAND]
            print(f"✓ 扩容次数: {len(expand_ops)}")

            return structure.get_capacity() > 5

    except Exception as e:
        print(f"✗ DSL 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n" + "🔥" * 30)
    print("顺序表扩容功能测试")
    print("🔥" * 30)

    results = []

    # 运行测试
    results.append(("基本扩容功能", test_expansion_basic()))
    results.append(("扩容动画步骤", test_expansion_animation_steps()))
    results.append(("多次扩容", test_multiple_expansions()))
    results.append(("DSL capacity 参数", test_dsl_with_capacity()))

    # 输出结果
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n通过率: {passed}/{total} ({passed*100//total}%)")

    if passed == total:
        print("\n🎉 所有测试通过！扩容功能已成功实现！")
    else:
        print("\n⚠️  部分测试失败，请检查实现。")