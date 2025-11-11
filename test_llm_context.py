#!/usr/bin/env python
"""
Test LLM context handling - verify the system prompt correctly processes context messages
"""

import sys
import os
sys.path.insert(0, '/Users/jiewang/WJ_Undergrad/Academy/大三上期学业/数据结构课设/DSVision')

from dsvision.extend2_llm.llm_service import LLMService

def test_llm_context():
    """Test LLM handling of context messages"""

    print("\n" + "="*60)
    print("Testing LLM Context Handling")
    print("="*60)

    # Initialize LLM service
    llm = LLMService(provider='openai')

    # Test 1: Initial creation
    print("\n[Test 1] Create linked list with [1, 2]")
    result1 = llm.natural_language_to_dsl("创建一个链表，初始化是1和2")
    print(f"✓ Success: {result1['success']}")
    print(f"  DSL Code:\n{result1['dsl_code']}")
    print(f"  Explanation: {result1['explanation']}")

    # Test 2: Incremental operation with context
    print("\n[Test 2] Insert 2 with context [当前数据结构：linked，数据：1,2]")
    context_message = "[当前数据结构：linked，数据：1,2]\n在基础上插入一个2"
    result2 = llm.natural_language_to_dsl(context_message)
    print(f"✓ Success: {result2['success']}")
    print(f"  DSL Code:\n{result2['dsl_code']}")
    print(f"  Explanation: {result2['explanation']}")

    # Verify results
    print("\n" + "="*60)
    print("Test Results:")
    if result1['success'] and 'myLinkedList' in result1['dsl_code'] and 'init' in result1['dsl_code']:
        print("✅ Test 1 PASSED: Initial creation generates init code")
    else:
        print("❌ Test 1 FAILED: Unexpected format for initial creation")

    if result2['success'] and result2['dsl_code'].strip():
        if 'init' not in result2['dsl_code'].lower():
            print("✅ Test 2 PASSED: Context message generates incremental code (no init)")
        else:
            print("⚠️  Test 2 PARTIAL: Code generated but contains init (should only have operations)")
    else:
        print("❌ Test 2 FAILED: Context message rejected or no code generated")
        print(f"   Explanation: {result2.get('explanation', 'N/A')}")
    print("="*60)

if __name__ == '__main__':
    test_llm_context()
