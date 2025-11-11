#!/usr/bin/env python
"""
Test script to verify DSL interpreter session persistence
"""

import sys
sys.path.insert(0, '/Users/jiewang/WJ_Undergrad/Academy/大三上期学业/数据结构课设/DSVision')

from dsvision.extend1_dsl.lexer import Lexer
from dsvision.extend1_dsl.parser import Parser
from dsvision.extend1_dsl.interpreter import Interpreter, SimpleStructureManager

def test_session_persistence():
    """Test that the same interpreter can handle incremental operations"""

    print("\n" + "="*60)
    print("Testing DSL Session Persistence")
    print("="*60)

    # Create one interpreter instance (same session)
    manager = SimpleStructureManager()
    interpreter = Interpreter(manager)

    # First operation: Create and initialize
    print("\n[Test 1] First operation: Create and init linked list with [1, 2]")
    dsl_code_1 = """Linked myLinkedList {
    init [1, 2]
}"""

    lexer1 = Lexer(dsl_code_1)
    tokens1 = lexer1.tokenize()
    parser1 = Parser(tokens1)
    ast1 = parser1.parse()
    result1 = interpreter.execute(ast1)

    print(f"✓ Result: {result1['success']}")
    print(f"  Structures: {list(result1['results'].keys())}")
    # Get all values from linked list
    ll1 = interpreter.context.structures['myLinkedList']['instance']
    data1 = []
    for i in range(ll1.size()):
        data1.append(ll1.get(i))
    print(f"  Data: {data1}")

    # Second operation: Add element (should reuse the same structure)
    print("\n[Test 2] Second operation: Insert 3 to tail (should reuse same structure)")
    dsl_code_2 = """Linked myLinkedList {
    insert_tail 3
}"""

    lexer2 = Lexer(dsl_code_2)
    tokens2 = lexer2.tokenize()
    parser2 = Parser(tokens2)
    ast2 = parser2.parse()
    result2 = interpreter.execute(ast2)

    print(f"✓ Result: {result2['success']}")
    print(f"  Structures: {list(result2['results'].keys())}")
    # Get all values from linked list
    ll2 = interpreter.context.structures['myLinkedList']['instance']
    data2 = []
    for i in range(ll2.size()):
        data2.append(ll2.get(i))
    print(f"  Data: {data2}")

    # Verify
    ll_final = interpreter.context.structures['myLinkedList']['instance']
    final_data = []
    for i in range(ll_final.size()):
        final_data.append(ll_final.get(i))
    expected_data = [1, 2, 3]

    print("\n" + "="*60)
    if final_data == expected_data:
        print("✅ TEST PASSED: Session persistence works correctly!")
        print(f"   Final data: {final_data} == {expected_data}")
    else:
        print("❌ TEST FAILED: Session persistence not working!")
        print(f"   Expected: {expected_data}")
        print(f"   Got: {final_data}")
    print("="*60)

if __name__ == '__main__':
    test_session_persistence()
