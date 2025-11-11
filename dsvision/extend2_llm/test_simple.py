"""
简单的 Claude API 测试
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv('LLM_PROVIDER', 'claude')
API_KEY = os.getenv('LLM_API_KEY')

print(f"Provider: {PROVIDER}")
print(f"API Key: {API_KEY[:20]}...")
print("=" * 60)

try:
    if PROVIDER == 'claude':
        from anthropic import Anthropic
        client = Anthropic(api_key=API_KEY, timeout=120.0)

        print("📝 发送简单请求...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            timeout=120.0,
            messages=[
                {"role": "user", "content": "简单回复：hello"}
            ]
        )

        print(f"✅ 成功!")
        print(f"回复: {response.content[0].text}")

    elif PROVIDER == 'groq':
        from groq import Groq
        client = Groq(api_key=API_KEY)

        print("📝 发送简单请求...")
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "简单回复：hello"}
            ]
        )

        print(f"✅ 成功!")
        print(f"回复: {response.choices[0].message.content}")

    else:
        print(f"不支持的 provider: {PROVIDER}")

except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()
