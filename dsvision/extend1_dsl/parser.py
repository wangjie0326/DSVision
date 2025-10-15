"""
DSL语法示例:
STRUCTURE bst {
    INSERT 5, 3, 7, 2, 4, 6, 8
    DELETE 3
    SEARCH 7
}

STRUCTURE sequential CAPACITY 10 {
    INIT 1, 2, 3, 4, 5
    INSERT AT 2 VALUE 99
    DELETE AT 1
}

STRUCTURE huffman {
    BUILD_TEXT "ABRACADABRA"
    ENCODE "ABRA"
}
"""

import re
from typing import List, Dict, Any, Optional
from enum import Enum


class DSLTokenType(Enum):
    """DSL词法单元类型"""
    STRUCTURE = "STRUCTURE"
    INSERT = "INSERT"
    DELETE = "DELETE"
    SEARCH = "SEARCH"
    INIT = "INIT"
    BUILD_TEXT = "BUILD_TEXT"
    ENCODE = "ENCODE"
    AT = "AT"
    VALUE = "VALUE"
    CAPACITY = "CAPACITY"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    EOF = "EOF"


class Token:
    """词法单元"""

    def __init__(self, type_: DSLTokenType, value: Any, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}:{self.column})"


class DSLLexer:
    """DSL词法分析器"""

    KEYWORDS = {
        'STRUCTURE', 'INSERT', 'DELETE', 'SEARCH', 'INIT',
        'BUILD_TEXT', 'ENCODE', 'AT', 'VALUE', 'CAPACITY'
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if text else None

    def error(self, msg: str):
        raise SyntaxError(f"词法错误 [{self.line}:{self.column}]: {msg}")

    def advance(self):
        """前进一个字符"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """跳过注释 (// 或 #)"""
        if self.current_char in ['/', '#']:
            if self.current_char == '/' and self.peek() == '/':
                while self.current_char and self.current_char != '\n':
                    self.advance()
            elif self.current_char == '#':
                while self.current_char and self.current_char != '\n':
                    self.advance()

    def peek(self) -> Optional[str]:
        """查看下一个字符"""
        peek_pos = self.pos + 1
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    def read_number(self) -> Token:
        """读取数字"""
        start_line, start_col = self.line, self.column
        num_str = ''

        # 处理负号
        if self.current_char == '-':
            num_str += '-'
            self.advance()

        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()

        try:
            value = int(num_str) if '.' not in num_str else float(num_str)
            return Token(DSLTokenType.NUMBER, value, start_line, start_col)
        except ValueError:
            self.error(f"无效的数字: {num_str}")

    def read_string(self) -> Token:
        """读取字符串"""
        start_line, start_col = self.line, self.column
        quote = self.current_char
        self.advance()  # 跳过开始引号

        string_val = ''
        while self.current_char and self.current_char != quote:
            if self.current_char == '\\':
                self.advance()
                if self.current_char in ['n', 't', 'r', '"', "'"]:
                    escape_chars = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', "'": "'"}
                    string_val += escape_chars.get(self.current_char, self.current_char)
                    self.advance()
            else:
                string_val += self.current_char
                self.advance()

        if self.current_char != quote:
            self.error("未闭合的字符串")

        self.advance()  # 跳过结束引号
        return Token(DSLTokenType.STRING, string_val, start_line, start_col)

    def read_identifier(self) -> Token:
        """读取标识符或关键字"""
        start_line, start_col = self.line, self.column
        identifier = ''

        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            identifier += self.current_char
            self.advance()

        # 检查是否为关键字
        if identifier.upper() in self.KEYWORDS:
            return Token(DSLTokenType[identifier.upper()], identifier.upper(), start_line, start_col)

        return Token(DSLTokenType.IDENTIFIER, identifier, start_line, start_col)

    def get_next_token(self) -> Token:
        """获取下一个词法单元"""
        while self.current_char:
            # 跳过空白
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # 跳过注释
            if self.current_char in ['/', '#']:
                self.skip_comment()
                continue

            # 数字
            if self.current_char.isdigit() or (self.current_char == '-' and self.peek() and self.peek().isdigit()):
                return self.read_number()

            # 字符串
            if self.current_char in ['"', "'"]:
                return self.read_string()

            # 标识符或关键字
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()

            # 单字符token
            single_char_tokens = {
                '{': DSLTokenType.LBRACE,
                '}': DSLTokenType.RBRACE,
                ',': DSLTokenType.COMMA
            }

            if self.current_char in single_char_tokens:
                token = Token(single_char_tokens[self.current_char],
                              self.current_char, self.line, self.column)
                self.advance()
                return token

            self.error(f"未知字符: {self.current_char}")

        return Token(DSLTokenType.EOF, None, self.line, self.column)


class DSLCommand:
    """DSL命令"""

    def __init__(self, command_type: str, params: Dict[str, Any]):
        self.command_type = command_type
        self.params = params

    def __repr__(self):
        return f"DSLCommand({self.command_type}, {self.params})"


class DSLStructure:
    """DSL结构定义"""

    def __init__(self, structure_type: str, capacity: Optional[int] = None):
        self.structure_type = structure_type
        self.capacity = capacity
        self.commands: List[DSLCommand] = []

    def add_command(self, command: DSLCommand):
        self.commands.append(command)

    def __repr__(self):
        return f"DSLStructure({self.structure_type}, commands={len(self.commands)})"


class DSLParser:
    """DSL语法分析器"""

    def __init__(self, text: str):
        self.lexer = DSLLexer(text)
        self.current_token = self.lexer.get_next_token()

    def error(self, msg: str):
        raise SyntaxError(f"语法错误 [{self.current_token.line}:{self.current_token.column}]: {msg}")

    def eat(self, token_type: DSLTokenType):
        """消费一个token"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"期望 {token_type}, 但得到 {self.current_token.type}")

    def parse(self) -> DSLStructure:
        """解析DSL程序"""
        return self.parse_structure()

    def parse_structure(self) -> DSLStructure:
        """解析结构定义"""
        self.eat(DSLTokenType.STRUCTURE)

        # 结构类型
        if self.current_token.type != DSLTokenType.IDENTIFIER:
            self.error("期望结构类型标识符")
        structure_type = self.current_token.value
        self.eat(DSLTokenType.IDENTIFIER)

        # 可选的容量参数
        capacity = None
        if self.current_token.type == DSLTokenType.CAPACITY:
            self.eat(DSLTokenType.CAPACITY)
            if self.current_token.type != DSLTokenType.NUMBER:
                self.error("容量必须是数字")
            capacity = self.current_token.value
            self.eat(DSLTokenType.NUMBER)

        structure = DSLStructure(structure_type, capacity)

        # 解析命令块
        self.eat(DSLTokenType.LBRACE)

        while self.current_token.type != DSLTokenType.RBRACE:
            command = self.parse_command()
            if command:
                structure.add_command(command)

        self.eat(DSLTokenType.RBRACE)

        return structure

    def parse_command(self) -> Optional[DSLCommand]:
        """解析命令"""
        if self.current_token.type == DSLTokenType.INSERT:
            return self.parse_insert()
        elif self.current_token.type == DSLTokenType.DELETE:
            return self.parse_delete()
        elif self.current_token.type == DSLTokenType.SEARCH:
            return self.parse_search()
        elif self.current_token.type == DSLTokenType.INIT:
            return self.parse_init()
        elif self.current_token.type == DSLTokenType.BUILD_TEXT:
            return self.parse_build_text()
        elif self.current_token.type == DSLTokenType.ENCODE:
            return self.parse_encode()
        else:
            self.error(f"未知命令: {self.current_token.type}")

    def parse_insert(self) -> DSLCommand:
        """解析INSERT命令"""
        self.eat(DSLTokenType.INSERT)

        params = {}

        # 检查是否有AT关键字(用于顺序表/链表)
        if self.current_token.type == DSLTokenType.AT:
            self.eat(DSLTokenType.AT)
            if self.current_token.type != DSLTokenType.NUMBER:
                self.error("AT后面必须是数字")
            params['index'] = self.current_token.value
            self.eat(DSLTokenType.NUMBER)

            self.eat(DSLTokenType.VALUE)
            params['value'] = self.parse_value()
        else:
            # 树结构或批量插入
            params['values'] = self.parse_value_list()

        return DSLCommand('insert', params)

    def parse_delete(self) -> DSLCommand:
        """解析DELETE命令"""
        self.eat(DSLTokenType.DELETE)

        params = {}

        if self.current_token.type == DSLTokenType.AT:
            self.eat(DSLTokenType.AT)
            if self.current_token.type != DSLTokenType.NUMBER:
                self.error("AT后面必须是数字")
            params['index'] = self.current_token.value
            self.eat(DSLTokenType.NUMBER)
        else:
            params['value'] = self.parse_value()

        return DSLCommand('delete', params)

    def parse_search(self) -> DSLCommand:
        """解析SEARCH命令"""
        self.eat(DSLTokenType.SEARCH)
        value = self.parse_value()
        return DSLCommand('search', {'value': value})

    def parse_init(self) -> DSLCommand:
        """解析INIT命令"""
        self.eat(DSLTokenType.INIT)
        values = self.parse_value_list()
        return DSLCommand('init', {'values': values})

    def parse_build_text(self) -> DSLCommand:
        """解析BUILD_TEXT命令(Huffman树)"""
        self.eat(DSLTokenType.BUILD_TEXT)
        if self.current_token.type != DSLTokenType.STRING:
            self.error("BUILD_TEXT需要字符串参数")
        text = self.current_token.value
        self.eat(DSLTokenType.STRING)
        return DSLCommand('build_text', {'text': text})

    def parse_encode(self) -> DSLCommand:
        """解析ENCODE命令"""
        self.eat(DSLTokenType.ENCODE)
        if self.current_token.type != DSLTokenType.STRING:
            self.error("ENCODE需要字符串参数")
        text = self.current_token.value
        self.eat(DSLTokenType.STRING)
        return DSLCommand('encode', {'text': text})

    def parse_value(self) -> Any:
        """解析单个值"""
        if self.current_token.type == DSLTokenType.NUMBER:
            value = self.current_token.value
            self.eat(DSLTokenType.NUMBER)
            return value
        elif self.current_token.type == DSLTokenType.STRING:
            value = self.current_token.value
            self.eat(DSLTokenType.STRING)
            return value
        elif self.current_token.type == DSLTokenType.IDENTIFIER:
            value = self.current_token.value
            self.eat(DSLTokenType.IDENTIFIER)
            return value
        else:
            self.error(f"期望值,但得到 {self.current_token.type}")

    def parse_value_list(self) -> List[Any]:
        """解析值列表"""
        values = [self.parse_value()]

        while self.current_token.type == DSLTokenType.COMMA:
            self.eat(DSLTokenType.COMMA)
            values.append(self.parse_value())

        return values


# 使用示例
if __name__ == "__main__":
    # 测试DSL解析
    dsl_code = """
    STRUCTURE bst {
        INSERT 5, 3, 7, 2, 4, 6, 8
        DELETE 3
        SEARCH 7
    }
    """

    parser = DSLParser(dsl_code)
    structure = parser.parse()
    print(f"解析结果: {structure}")
    for cmd in structure.commands:
        print(f"  命令: {cmd}")