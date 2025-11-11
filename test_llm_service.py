#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM服务测试脚本
用于测试不同LLM提供商的连接和功能
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from dotenv import load_dotenv
load_dotenv()

from dsvision.extend2_llm.llm_service import LLMService


def print_section(title):
    """打印分隔线"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def test_llm_service():
    """测试LLM服务"""
    # 读取环境变量
    provider = os.getenv('LLM_PROVIDER', 'openai')
    api_key = os.getenv('LLM_API_KEY')
    base_url = os.getenv('LLM_BASE_URL')

    print_section("LLM 配置信息")
    print(f"提供商: {provider}")
    print(f"API Key: {api_key[:15]}..." if api_key and len(api_key) > 15 else f"API Key: {api_key}")
    print(f"Base URL: {base_url or '默认官方API'}")

    if not api_key:
        print("\n❌ 错误: 未设置 LLM_API_KEY")
        print("请在项目根目录创建 .env 文件并配置:")
        print("  LLM_PROVIDER=openai")
        print("  LLM_API_KEY=sk-xxx")
        print("  LLM_BASE_URL=https://api.example.com (可选)")
        return

    # 初始化服务
    try:
        print_section("初始化 LLM 服务")
        llm = LLMService(provider=provider, api_key=api_key, base_url=base_url)
        print("✓ LLM服务初始化成功\n")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return

    # 测试用例
    test_cases = [
        {
            'name': '测试1: 创建二叉搜索树',
            'input': '创建一个包含5,3,7,2,4的二叉搜索树'
        },
        {
            'name': '测试2: 创建顺序表',
            'input': '构建一个顺序表,初始元素是1到10'
        },
        {
            'name': '测试3: 创建栈',
            'input': '帮我创建一个栈,压入1,2,3,然后弹出一个元素'
        },
        {
            'name': '测试4: 无关问题(应拒绝)',
            'input': '你是谁?'
        },
        {
            'name': '测试5: 天气问题(应拒绝)',
            'input': '今天天气怎么样'
        },
    ]

    # 执行测试
    for i, test in enumerate(test_cases, 1):
        print_section(f"{test['name']}")
        print(f"📝 用户输入: {test['input']}\n")

        try:
            result = llm.natural_language_to_dsl(test['input'])

            if result['success']:
                print("✅ 生成成功")
                print(f"\nDSL代码:")
                print("-" * 60)
                print(result['dsl_code'] if result['dsl_code'] else "(空代码)")
                print("-" * 60)
                print(f"\n说明: {result['explanation']}")
                print(f"提供商: {result.get('provider', 'unknown')}")
            else:
                print(f"❌ 生成失败: {result.get('error', '未知错误')}")

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()

        # 等待用户按键继续(可选)
        if i < len(test_cases):
            input("\n按Enter继续下一个测试...")


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                 DSVision LLM 服务测试工具                ║
╚══════════════════════════════════════════════════════════╝
    """)

    try:
        test_llm_service()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()

    print_section("测试完成")
    print("感谢使用 DSVision LLM 服务!\n")


if __name__ == "__main__":
    main()
