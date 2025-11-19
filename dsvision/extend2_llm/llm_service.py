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
1. **关键：** 这是一个数据结构操作助手，你必须根据用户输入生成DSL代码
2. 识别问题类型：
   - **含有上下文的操作请求**：消息以 `[当前数据结构：...]` 开头 → 生成增量操作代码
   - **普通创建请求**：如"创建一个链表"、"生成一个BST" → 生成初始化代码
   - **无关问题**：与数据结构无关 → 回复: "我是DSVion,只能帮你学习数据结构操作。你可以想创建或操作的数据结构。☺️"
3. 必须返回JSON格式: {"dsl_code": "...", "explanation": "..."}
4. **上下文处理规则**：
   - 格式：`[当前数据结构：linked，数据：1,2]\\n用户的实际请求`
   - 这是**系统自动添加的上下文**，用来帮助你生成增量操作
   - 提取上下文中的数据结构类型和当前数据，用于判断增量操作
   - 然后**只处理\\n后面的用户请求部分**
   - 示例：消息"[当前数据结构：linked，数据：1,2]\\n插入一个2"表示在[1,2]基础上插入2
5. **结构名称一致性**（会话持久化）：
   - 在一个会话中，始终使用相同的结构变量名（如 myLinkedList, myBST）
   - 不要为增量操作创建新的结构
   - 这样后端解释器才能复用并操作同一个结构实例
6. **代码生成选择**：
   - 如果消息以 `[当前数据结构：...]` 开头：生成**仅包含操作的DSL**（不含init）
   - 如果没有上下文：生成**完整的初始化DSL**（包含init）

## 支持的DSL语法

### 线性结构
```
Sequential myList {
    init [1, 2, 3]          # 默认容量100
    insert 10 at 2
    delete at 1
    search 3
}

Sequential mySmallList {
    init [1, 2, 3] capacity 5   # 🔥 指定初始容量为5
    insert 4                     # 当容量满时会自动1.5倍扩容
    insert 5
    insert 6                     # 触发扩容：5 -> 7
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

Huffman myHuffmanNumbers {
    build_numbers [2, 4, 6, 8]
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

### 多轮对话示例（会话内存）

第一轮:
用户: "创建一个链表，初始化是1和2"
你的回复:
```json
{
  "dsl_code": "Linked myLinkedList {\\n    init [1, 2]\\n}",
  "explanation": "已创建链表，初始化了2个节点"
}
```

第二轮 - **重要**：用户提供了上下文 `[当前数据结构：linked，数据：1,2]`
用户: "[当前数据结构：linked，数据：1,2]\\n在基础上插入一个2"
你的回复:
```json
{
  "dsl_code": "Linked myLinkedList {\\n    insert_tail 2\\n}",
  "explanation": "在现有链表[1,2]的基础上，在尾部插入2，现在链表为[1,2,2]"
}
```

第三轮 - 再次提供上下文
用户: "[当前数据结构：linked，数据：1,2,2]\\n现在删除第一个2"
你的回复:
```json
{
  "dsl_code": "Linked myLinkedList {\\n    delete_by_value 2\\n}",
  "explanation": "删除第一个值为2的元素，链表变为[1,2]"
}
```

**关键规则**：
- 第二轮用的结构名称必须是 `myLinkedList`（与第一轮相同），这样解释器才能在会话中复用同一个结构
- 不要创建新的结构名称（如 `myLinkedList2`）
- 只生成增量操作，不重新初始化

用户: "你是谁?"
你的回复:
```json
{
  "dsl_code": "",
  "explanation": "我是DSVion,只能帮你学习数据结构操作。你可以想创建或操作的数据结构。☺️"
}
```

用户: "今天天气怎么样"
你的回复:
```json
{
  "dsl_code": "",
  "explanation": "我是DSVion,只能帮你学习数据结构操作。你可以想创建或操作的数据结构。☺️"
}
```

### 树遍历示例

用户: "创建一个包含50,30,70,20,40的BST并进行中序遍历"
你的回复:
```json
{
  "dsl_code": "BST myBST {\\n    insert 50\\n    insert 30\\n    insert 70\\n    insert 20\\n    insert 40\\n    traverse inorder\\n}",
  "explanation": "已创建二叉搜索树，插入5个节点，并进行中序遍历（结果应为：20, 30, 40, 50, 70）"
}
```

用户: "前序遍历这棵树"
你的回复:
```json
{
  "dsl_code": "BST myBST {\\n    traverse preorder\\n}",
  "explanation": "对当前二叉搜索树进行前序遍历（根→左→右）"
}
```

用户: "层次遍历"
你的回复:
```json
{
  "dsl_code": "BST myBST {\\n    traverse levelorder\\n}",
  "explanation": "对当前二叉搜索树进行层次遍历（从上到下，从左到右）"
}
```

用户: "后序遍历一下"
你的回复:
```json
{
  "dsl_code": "BST myBST {\\n    traverse postorder\\n}",
  "explanation": "对当前二叉搜索树进行后序遍历（左→右→根）"
}
```

## 智能识别规则
- "创建/构建/生成" → 使用 init 或 insert
- "删除/移除" → 使用 delete
- "查找/搜索" → 使用 search
- "遍历" → 使用 traverse，识别遍历类型：
  - "前序/先序/前序遍历/preorder" → traverse preorder
  - "中序/中序遍历/inorder" → traverse inorder
  - "后序/后序遍历/postorder" → traverse postorder
  - "层次/层序/广度/levelorder/level order" → traverse levelorder
  - 如果只说"遍历"不指定类型，默认使用 inorder（中序遍历）
- 数字序列 [5,3,7] → 自动转换为 DSL 语法

### Huffman树特殊规则
- **文本模式**：用户提到"文本"、"字符串"、"单词"等关键词 → 使用 `build_text "文本内容"`
  - 示例："用HELLO构建Huffman树" → `build_text "HELLO"`
- **数字模式**：用户提到"数字"、"频率"、"权重"，或直接给出数字列表 → 使用 `build_numbers [数字列表]`
  - 示例："用2,4,6,8构建Huffman树" → `build_numbers [2, 4, 6, 8]`
  - 示例："创建频率为2、4、6、8的Huffman树" → `build_numbers [2, 4, 6, 8]`
- **默认规则**：如果用户没有明确指定模式，根据输入内容判断：
  - 包含字母/汉字 → 文本模式
  - 只包含数字 → 数字模式
"""


# ==================== Groq 实现 ====================
class GroqProvider:
    def __init__(self, api_key: str):
        from groq import Groq

        self.client = Groq(api_key=api_key)
        print("✓ Groq 客户端初始化成功")

    def generate(self, user_message: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Groq 免费模型
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=500
            )

            result = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'dsl_code': result.get('dsl_code', ''),
                'explanation': result.get('explanation', ''),
                'provider': 'groq'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'groq'
            }


# ==================== Claude 实现 ====================
class ClaudeProvider:
    def __init__(self, api_key: str):
        from anthropic import Anthropic

        # 增加超时时间到 120 秒
        self.client = Anthropic(api_key=api_key, timeout=120.0)
        print("✓ Claude 客户端初始化成功")
        print(f"✓ 超时设置: 120.0 秒")

    def generate(self, user_message: str) -> Dict:
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.3,
                timeout=120.0,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            result = json.loads(response.content[0].text)
            return {
                'success': True,
                'dsl_code': result.get('dsl_code', ''),
                'explanation': result.get('explanation', ''),
                'provider': 'claude'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'claude'
            }


# ==================== OpenAI 实现 ====================
class OpenAIProvider:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        from openai import OpenAI

        # 使用传入的 base_url，否则使用默认 OpenAI API
        if base_url:
            # OpenRouter 需要较长的超时时间
            timeout = 120.0  # 增加超时时间到 120 秒
            self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
            print(f"✓ 使用自定义 Base URL: {base_url}")
            print(f"✓ 超时设置: {timeout} 秒")
        else:
            self.client = OpenAI(api_key=api_key)
            print("✓ 使用默认 OpenAI API")

        print("✓ OpenAI 客户端初始化成功")

    def generate(self, user_message: str) -> Dict:
        try:
            # 使用兼容的模型名称（OpenRouter 和官方 OpenAI 都支持）
            model = "openai/gpt-4o-mini"  # OpenRouter格式: provider/model

            # OpenRouter配置
            extra_headers = {}
            extra_body = {}

            # 如果使用OpenRouter，不使用response_format（某些模型不支持）
            # 改为在system prompt中要求JSON格式
            print(f"🔄 正在调用 OpenAI API (模型: {model})...")
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=500,
                timeout=120.0,  # 显式设置超时
                extra_headers=extra_headers,
                extra_body=extra_body
            )

            # 获取响应内容
            content = response.choices[0].message.content
            print(f"✓ API响应成功")
            print(f"原始响应内容: {content}")

            # 🔥 处理markdown代码块格式（```json ... ```）
            import re
            json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1).strip()
                print(f"✓ 提取到JSON内容: {content}")

            # 尝试解析JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as json_err:
                print(f"❌ JSON解析失败: {json_err}")
                print(f"原始内容: {repr(content)}")
                return {
                    'success': False,
                    'error': f'LLM返回的内容不是有效的JSON格式: {content[:200]}...',
                    'provider': 'openai'
                }

            return {
                'success': True,
                'dsl_code': result.get('dsl_code', ''),
                'explanation': result.get('explanation', ''),
                'provider': 'openai'
            }

        except Exception as e:
            print(f"❌ API调用失败: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
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
            self.provider = ClaudeProvider(api_key)
        elif provider == 'groq':
            self.provider = GroqProvider(api_key)
        else:
            raise ValueError(f"不支持的提供商: {provider}。支持的提供商: openai, claude, groq")

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