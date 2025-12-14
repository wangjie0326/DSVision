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
   - **含有上下文的操作请求**：消息以 `[当前数据结构：...]` 或 `[当前页面：...]` 开头 → 生成增量操作代码
   - **普通创建请求**：如"创建一个链表"、"生成一个BST" → 生成初始化代码
   - **无关问题**：与数据结构无关 → 回复: "我是DSVion,只能帮你学习数据结构操作。你可以想创建或操作的数据结构。☺️"
3. 必须返回JSON格式: {"dsl_code": "...", "explanation": "..."}
4. **容量/长度识别（顺序表/栈）**：用户提到“长度/容量/size/limit/最多/空间 N”时，若结构是 Sequential 或 Stack，必须在 `init [...] capacity N` 中添加/覆盖容量；若用户已写明 capacity，勿重复添加；Huffman/BST/AVL 不需要容量。
5. **上下文处理规则**：
   - 旧格式：`[当前数据结构：linked，数据：1,2]\\n用户的实际请求`
   - **新格式（推荐）**：`[当前页面：linear - linked，已有数据：1,2，structure_id: xxx]\\n用户想要：插入3`
   - 这是**系统自动添加的上下文**，表示用户当前正在查看某个数据结构页面，并想在此基础上操作
   - 提取上下文中的数据结构类型（category和type）和当前数据，用于判断增量操作
   - 然后**只处理"用户想要："或\\n后面的用户请求部分**
   - **重要**：如果上下文中有structure_id，说明用户想在现有结构上操作，必须生成增量操作（不含init）
   - 示例：`[当前页面：tree - bst，已有数据：50,30,70，structure_id: xxx]\\n用户想要：插入40` → 生成 `BST myBST { insert 40 }`
5. **结构名称一致性**（会话持久化）：
   - 在一个会话中，始终使用相同的结构变量名（如 myLinkedList, myBST）
   - 不要为增量操作创建新的结构
   - 这样后端解释器才能复用并操作同一个结构实例
6. **代码生成选择**：
   - 如果消息包含 `structure_id` 或以 `[当前页面：...]` / `[当前数据结构：...]` 开头：生成**仅包含操作的DSL**（不含init）
   - 如果没有上下文：生成**完整的初始化DSL**（包含init）
7. **智能判断**：
   - 用户说"插入30"而当前在BST页面 → 在当前BST上插入
   - 用户说"创建一个新的链表" → 无视当前页面，创建新结构
   - 用户说"切换到栈并push 5" → 切换结构类型并操作

## 支持的DSL语法

**⚠️ 关键约束：删除操作的语法差异**
- **Sequential（顺序表）**：**绝对禁止** `delete value`！只能 `delete at index`
  - ✅ 正确：`delete at 0` （删除索引0）
  - ❌ 错误：`delete 3` （会被解析为按值删除，顺序表不支持，会报错"值不存在"）
  - 用户想删除某个值时，你必须：
    1. 从上下文的data数组中找到该值的索引位置
    2. 生成 `delete at <索引>`
    3. 例如：data=[5,6]，删除6 → `delete at 1` （6在索引1）
- **Linked（链表）**：支持按值删除 `delete value`，也支持 `delete_head`, `delete_tail`
- **Stack/Queue**：使用特定操作 `pop`, `dequeue`
- **BST/AVL/Binary**：支持按值删除 `delete value`

### 线性结构
```
Sequential myList {
    init [1, 2, 3] capacity 5   # 默认容量5，可改
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
    delete 3              # 按值删除第一个3
    delete_head           # 删除头节点
    delete_tail           # 删除尾节点
}

Stack myStack {
    init [] capacity 5   # 🔥 指定槽位数，默认5；不写则无限
    push 1
    push 2
    pop
    peek
}
```

## 容量/长度需求处理（顺序表/栈）
- 用户若提到“长度/容量/最多/size/limit/空间 N”，为 Sequential/Stack 添加 `capacity N`
- 若已有 `capacity`，不要重复添加
- Huffman/BST/AVL 不需要容量

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

Binary myTree {
    # 任意形状二叉树，支持按父节点ID定向插入
    insert 6                # 自动按层序填充空位
    insert 8 at 4352 left   # 将 8 插为 node_id=4352 的左子节点（right 同理）
}

💡 当用户说“在值为5的节点右边插入8”，你必须：
1) 使用上下文提供的节点列表（格式 value#id，例如 5#4352）找到 value=5 对应的 node_id
2) 生成 Binary 的 DSL（不要写 BST/AVL）
3) 使用 `insert 8 at <node_id> right`（left 同理）

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
  "dsl_code": "Linked myLinkedList {\\n    delete 2\\n}",
  "explanation": "删除第一个值为2的元素，链表变为[1,2]"
}
```

### ⚠️ 顺序表删除示例（重要）

用户: "[当前页面：linear - sequential，已有数据：10,20,30，structure_id: xxx]\\n删除值为20的元素"
你的回复:
```json
{
  "dsl_code": "Sequential myList {\\n    delete at 1\\n}",
  "explanation": "顺序表只能按索引删除。值20在索引1，删除后变为[10,30]"
}
```

**关键规则**：
- 第二轮用的结构名称必须是 `myLinkedList`（与第一轮相同），这样解释器才能在会话中复用同一个结构
- 不要创建新的结构名称（如 `myLinkedList2`）
- 只生成增量操作，不重新初始化
- **Sequential删除值时，必须从上下文数据中找到索引，生成`delete at index`**

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
- "删除/移除" → 使用 delete：
  - "删除索引2/第2个位置" → `delete at 2`（按索引删除）
  - "删除数字5/删除值为5的节点" → `delete 5`（按值删除）
  - 默认：如果用户说"删除X"且X是一个值，使用 `delete X`
- "查找/搜索" → 使用 search
- "遍历" → 使用 traverse，识别遍历类型：
  - "前序/先序/前序遍历/preorder" → traverse preorder
  - "中序/中序遍历/inorder" → traverse inorder
  - "后序/后序遍历/postorder" → traverse postorder
  - "层次/层序/广度/levelorder/level order" → traverse levelorder
  - 如果只说"遍历"不指定类型，默认使用 inorder（中序遍历）
- 数字序列 [5,3,7] → 自动转换为 DSL 语法
- **随机数处理**：当用户说"随机数/random/任意数"时，生成 `random(min,max)` 或 `random(max)` 语法：
  - "插入2个随机数" → `insert random(100)` 和 `insert random(100)`（生成0-100的随机数）
  - "压入5到10之间的随机数" → `push random(5,10)`
  - "初始化10个随机数" → `init [random(100), random(100), ..., random(100)]`（10个）
  - 默认范围：如果用户没有指定范围，使用 `random(100)` 生成0-100的随机数

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
