"""
LLM服务 - 将自然语言转换为DSL代码
支持多种LLM提供商
"""

import os
from typing import Dict, Optional
import json
from dotenv import load_dotenv
load_dotenv()

# ==================== 配置部分 ====================
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')
LLM_BASE_URL = os.getenv('LLM_BASE_URL', None)  # 可选,用于第三方API或代理
API_KEY = os.getenv('LLM_API_KEY')

if not API_KEY:
    raise ValueError("未设置 LLM_API_KEY,请在 .env 文件中配置")

print(f"✓ LLM配置加载成功")
print(f"  - 提供商: {LLM_PROVIDER}")
print(f"  - Base URL: {LLM_BASE_URL or '默认'}")
print(f"  - API Key: {API_KEY[:15]}..." if len(API_KEY) > 15 else f"  - API Key: {API_KEY}")

# ==================== 系统提示词 ====================
SYSTEM_PROMPT = """你是DSVison,你的数据结构可视化系统的DSL代码生成助手。

## 你的唯一任务
将用户的自然语言描述转换为DSL代码,用于操作数据结构。

## 严格规则
1. 只回答与数据结构操作相关的问题
2. 对于无关问题,统一回复: "我是DSVion,只能帮你学习数据结构操作。你可以想创建或操作的数据结构。☺️"
3. 必须返回JSON格式: {"dsl_code": "...", "explanation": "..."}

## 支持的DSL语法

### 线性结构
```
Sequential myList {
    init [1, 2, 3]
    insert 10 at 2
    delete at 1
    search 3
}

Linked myLinkedList {
    init [1, 2, 3]
    insert_head 0
    insert_tail 4
}

Stack myStack {
    push 1
    push 2
    pop
    peek
}
```

### 树结构
```
BST myBST {
    insert 50
    insert 30
    insert 70
    traverse inorder
    min
    max
}

AVL myAVL {
    insert 10
    insert 20
    insert 30
}

Huffman myHuffman {
    build_text "HELLO"
    show_codes
    encode "HI"
}
```

## 示例对话

用户: "创建一个包含5,3,7,2,4的二叉搜索树"
你的回复:
```json
{
  "dsl_code": "BST myBST {\\n    insert 5\\n    insert 3\\n    insert 7\\n    insert 2\\n    insert 4\\n}",
  "explanation": "已创建二叉搜索树,依次插入5个节点"
}
```

用户: "你是谁?"
你的回复:
```json
{
  "dsl_code": "",
  "explanation": "我是数据结构助手,只能帮你生成数据结构操作代码。请描述你想创建或操作的数据结构。"
}
```

用户: "今天天气怎么样"
你的回复:
```json
{
  "dsl_code": "",
  "explanation": "我是数据结构助手,只能帮你生成数据结构操作代码。请描述你想创建或操作的数据结构。"
}
```

## 智能识别规则
- "创建/构建/生成" → 使用 init 或 insert
- "删除/移除" → 使用 delete
- "查找/搜索" → 使用 search
- "遍历" → 使用 traverse
- 数字序列 [5,3,7] → 自动转换为 DSL 语法
"""


# ==================== OpenAI 实现 ====================
class OpenAIProvider:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        from openai import OpenAI

        # 根据是否提供 base_url 决定使用官方API还是第三方API
        if base_url:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            print(f"✓ OpenAI 客户端初始化成功 (自定义URL: {base_url})")
        else:
            # 标准 OpenAI API
            self.client = OpenAI(api_key=api_key)
            print("✓ OpenAI 客户端初始化成功 (官方API)")

    def generate(self, user_message: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )

            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'dsl_code': result.get('dsl_code', ''),
                'explanation': result.get('explanation', ''),
                'provider': 'openai'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'openai'
            }


# ==================== LLM服务类 ====================
class LLMService:
    def __init__(self, provider: str = 'openai', api_key: str = None, base_url: str = None):
        self.provider_name = provider
        api_key = api_key or API_KEY
        base_url = base_url or LLM_BASE_URL

        if provider == 'openai':
            self.provider = OpenAIProvider(api_key, base_url)
        elif provider == 'claude':
            # TODO: 实现 Claude Provider
            raise ValueError("Claude 提供商暂未实现,敬请期待")
        else:
            raise ValueError(f"不支持的提供商: {provider}，可选: openai, claude")

    def natural_language_to_dsl(self, user_input: str) -> Dict:
        """
        将自然语言转换为DSL代码

        Args:
            user_input: 用户的自然语言描述

        Returns:
            {
                'success': bool,
                'dsl_code': str,
                'explanation': str,
                'provider': str
            }
        """
        print(f"\n{'=' * 60}")
        print(f"[LLM服务] 处理用户输入")
        print(f"提供商: {self.provider_name}")
        print(f"用户: {user_input}")
        print(f"{'=' * 60}\n")

        result = self.provider.generate(user_input)

        if result['success']:
            print(f"✓ DSL生成成功")
            print(f"代码:\n{result['dsl_code']}")
            print(f"说明: {result['explanation']}\n")
        else:
            print(f"✗ 生成失败: {result['error']}\n")

        return result


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试示例
    test_cases = [
        "创建一个包含5,3,7,2,4的二叉搜索树",
        "构建一个顺序表,初始元素是1到10",
        "帮我创建一个栈,压入1,2,3",
        "你是谁?",
        "今天天气怎么样",
    ]

    llm = LLMService(provider='openai')

    for test_input in test_cases:
        result = llm.natural_language_to_dsl(test_input)
        print("-" * 60)