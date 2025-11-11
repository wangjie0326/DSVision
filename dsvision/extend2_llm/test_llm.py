"""
LLM 测试脚本 - 支持多个提供商
测试前请在 .env 中配置:
  LLM_PROVIDER=openai  # 或 claude
  LLM_API_KEY=你的key
  LLM_BASE_URL=https://... (可选,仅 openai 兼容 API 需要)
"""
import os
from dotenv import load_dotenv
from llm_service import LLMService

# 加载环境变量
load_dotenv()

# 获取配置
PROVIDER = os.getenv('LLM_PROVIDER', 'openai')
API_KEY = os.getenv('LLM_API_KEY')
BASE_URL = os.getenv('LLM_BASE_URL')

print(f"🚀 LLM 测试脚本")
print("=" * 60)
print(f"Provider: {PROVIDER}")
print(f"API Key: {'已设置' if API_KEY else '❌ 未设置'}")
print(f"Base URL: {BASE_URL or '(使用默认)'}")
print("=" * 60)

# 初始化服务
try:
    if PROVIDER == 'claude':
        # Claude API 不需要 base_url
        llm = LLMService(provider=PROVIDER, api_key=API_KEY)
    else:
        # OpenAI 兼容 API
        llm = LLMService(provider=PROVIDER, api_key=API_KEY, base_url=BASE_URL)

    print("✅ LLM服务初始化成功\n")
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    print("\n💡 请检查:")
    print(f"  1. .env 文件是否存在且包含 LLM_API_KEY")
    print(f"  2. LLM_PROVIDER 是否正确 (openai/claude)")
    print(f"  3. API Key 是否有效")
    exit(1)

# 测试用例
test_cases = [
    {
        'input': '创建一个包含5,3,7,2,4的二叉搜索树',
        'should_generate_dsl': True
    },
    {
        'input': '帮我构建一个顺序表,元素是1到10',
        'should_generate_dsl': True
    },
    {
        'input': '你好,你是谁?',
        'should_generate_dsl': False  # 应该拒绝
    },
    {
        'input': '今天天气怎么样',
        'should_generate_dsl': False  # 应该拒绝
    }
]

# 运行测试
for i, test in enumerate(test_cases, 1):
    print(f"\n{'=' * 60}")
    print(f"测试 {i}/{len(test_cases)}")
    print(f"{'=' * 60}")
    print(f"📝 输入: {test['input']}")
    print(f"期望生成DSL: {'是' if test['should_generate_dsl'] else '否'}")

    try:
        result = llm.natural_language_to_dsl(test['input'])

        if result['success']:
            print(f"\n✅ 调用成功")
            print(f"📋 说明: {result['explanation']}")

            if result['dsl_code']:
                print(f"\n💻 生成的DSL代码:")
                print("-" * 60)
                print(result['dsl_code'])
                print("-" * 60)

                if not test['should_generate_dsl']:
                    print("⚠️  警告: 不应该生成DSL代码,但生成了!")
            else:
                print("\n📝 未生成DSL代码(可能是拒绝了无关问题)")

                if test['should_generate_dsl']:
                    print("⚠️  警告: 应该生成DSL代码,但没有生成!")
        else:
            print(f"\n❌ 调用失败")
            print(f"错误: {result.get('error', '未知错误')}")

    except Exception as e:
        print(f"\n❌ 异常: {e}")
        import traceback

        traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 测试完成!")
print("=" * 60)

