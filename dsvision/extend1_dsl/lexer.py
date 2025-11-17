import re
from enum import Enum
from typing import List,Optional, Tuple

class TokenType(Enum):
    """Token type"""
    #关键字
    SEQUENTIAL = "SEQUENTIAL"
    LINKED = "LINKED"
    STACK = "STACK"
    QUEUE = "QUEUE"
    BINARY = "BINARY"
    BST = "BST"
    AVL = "AVL"
    HUFFMAN = "HUFFMAN"

    #操作关键字
    INIT = "INIT"
    INSERT = "INSERT"
    DELETE = "DELETE"
    SEARCH = "SEARCH"
    CLEAR = "CLEAR"
    SAVE = "SAVE"
    LOAD = "LOAD"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"

    #栈/队列操作
    PUSH = "PUSH"
    POP = "POP"
    PEEK = "PEEK"
    ENQUEUE = "ENQUEUE"
    DEQUEUE = "DEQUEUE"
    FRONT = "FRONT"
    REAR = "REAR"

    #树操作
    BUILD = "BUILD"
    TRAVERSE = "TRAVERSE"
    HEIGHT = "HEIGHT"
    MIN = "MIN"
    MAX = "MAX"
    REVERSE = "REVERSE"

    #HUFFMAN
    BUILD_TEXT = "BUILD_TEXT"
    BUILD_FREQ = "BUILD_FREQ"
    BUILD_NUMBERS = "BUILD_NUMBERS"  # 🔥 新增：纯数字模式
    ENCODE = "ENCODE"
    DECODE = "DECODE"
    SHOW_CODES = "SHOW_CODES"

    #链表操作
    INSERT_HEAD = "INSERT_HEAD"
    INSERT_TAIL = "INSERT_TAIL"
    DELETE_HEAD = "DELETE_HEAD"
    DELETE_TAIL = "DELETE_TAIL"

    #高级特性
    FOR = "FOR"
    IN = "IN"
    IF = "IF"
    TRY = "TRY"
    CATCH = "CATCH"
    RANGE = "RANGE"
    SPEED = "SPEED"
    PAUSE = "PAUSE"

    #遍历方式
    PREORDER = "PREORDER"
    INORDER = "INORDER"
    POSTORDER = "POSTORDER"
    LEVELORDER = "LEVELORDER"

    #位置关键字
    AT = "AT"
    GET = "GET"
    SIZE = "SIZE"

    #符号
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA = "COMMA"
    COLON = "COLON"
    DOT = "DOT"

    #字面量
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    # 特殊
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COMMENT = "COMMENT"

class Token:
    """Token type"""
    def __init__(self, type: TokenType, value: any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"

class Lexer:
    """词法分析器"""
    #关键词映射
    KEYWORDS = {
        'sequential': TokenType.SEQUENTIAL,
        'linked': TokenType.LINKED,
        'stack': TokenType.STACK,
        'queue': TokenType.QUEUE,
        'binary': TokenType.BINARY,
        'bst': TokenType.BST,
        'avl': TokenType.AVL,
        'huffman': TokenType.HUFFMAN,

        'init': TokenType.INIT,
        'insert': TokenType.INSERT,
        'delete': TokenType.DELETE,
        'search': TokenType.SEARCH,
        'clear': TokenType.CLEAR,
        'export': TokenType.EXPORT,
        'import': TokenType.IMPORT,
        'save': TokenType.SAVE,
        'load': TokenType.LOAD,

        'push':TokenType.PUSH,
        'pop': TokenType.POP,
        'peek': TokenType.PEEK,
        'enqueue': TokenType.ENQUEUE,
        'dequeue': TokenType.DEQUEUE,
        'front': TokenType.FRONT,
        'rear': TokenType.REAR,

        'build': TokenType.BUILD,
        'traverse': TokenType.TRAVERSE,
        'height': TokenType.HEIGHT,
        'min': TokenType.MIN,
        'max': TokenType.MAX,
        'reverse': TokenType.REVERSE,

        'build_text': TokenType.BUILD_TEXT,
        'build_freq': TokenType.BUILD_FREQ,
        'build_numbers': TokenType.BUILD_NUMBERS,  # 🔥 新增
        'encode': TokenType.ENCODE,
        'decode': TokenType.DECODE,
        'show_codes': TokenType.SHOW_CODES,

        'insert_head': TokenType.INSERT_HEAD,
        'insert_tail': TokenType.INSERT_TAIL,
        'delete_head': TokenType.DELETE_HEAD,
        'delete_tail': TokenType.DELETE_TAIL,

        'for': TokenType.FOR,
        'in': TokenType.IN,
        'if': TokenType.IF,
        'try': TokenType.TRY,
        'catch': TokenType.CATCH,
        'range': TokenType.RANGE,
        'speed': TokenType.SPEED,
        'pause': TokenType.PAUSE,

        'preorder': TokenType.PREORDER,
        'inorder': TokenType.INORDER,
        'postorder': TokenType.POSTORDER,
        'levelorder': TokenType.LEVELORDER,

        'at': TokenType.AT,
        'get': TokenType.GET,
        'size': TokenType.SIZE,
    }

    def __init__(self,code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self,message: str):
        """报错"""
        raise SyntaxError(f"[Lexer Error] Line {self.line}:{self.column} - {message}")

    def advance(self):
        """读取并移动到下一个字符"""
        if self.pos >= len(self.code):
            return None
        char = self.code[self.pos]
        self.pos += 1

        if char == '\n':
            self.line += 1
            self.column += 1
        else:
            self.column += 1

        return char

    def peek(self, offset: int = 0) -> Optional[str]:
        """查看字符但不移动位置"""
        pos = self.pos + offset
        if pos < len(self.code):
            return self.code[pos]
        return None

    def skip_whitespace(self):
        """跳过空格（不包括换行）"""
        while self.peek() and self.peek() in ' \t\r':
            self.advance()

    def skip_comment(self):
        """跳过注释"""
        #单行注释
        if self.peek() == '/' and self.peek(1) == '/':
            while self.peek(2) and self.peek() == '/':
                self.advance()
            return True

        #多行注释
        if self.peek() == '/' and self.peek(1) == '/':
            self.advance() # /
            self.advance() # *

            while True:
                if self.peek() is None:
                    self.error("未闭合的多行注释")
                if self.peek() == '*' and self.peek(1) == '/':
                    self.advance()  # *
                    self.advance()  # /
                    break
                self.advance()
            return True
        return False

    def read_number(self) -> Token:
        """读取数字"""
        start_line = self.line
        start_column = self.column
        num_str = ''

        # 负号
        if self.peek() == '-':
            num_str += self.advance()

        # 整数部分
        while self.peek() and self.peek().isdigit():
            num_str += self.advance()

        # 小数部分
        if self.peek() == '.':
            num_str += self.advance()
            while self.peek() and self.peek().isdigit():
                num_str += self.advance()
            return Token(TokenType.NUMBER, float(num_str), start_line, start_column)

        return Token(TokenType.NUMBER, int(num_str), start_line, start_column)

    def read_string(self) -> Token:
        """读取字符串"""
        start_line = self.line
        start_column = self.column
        quote = self.advance()  # " 或 '
        string = ''

        while True:
            char = self.peek()
            if char is None:
                self.error(f"未闭合的字符串")
            if char == quote:
                self.advance()
                break
            if char == '\\':
                self.advance()
                next_char = self.advance()
                if next_char == 'n':
                    string += '\n'
                elif next_char == 't':
                    string += '\t'
                elif next_char == '\\':
                    string += '\\'
                elif next_char == quote:
                    string += quote
                else:
                    string += next_char
            else:
                string += self.advance()

        return Token(TokenType.STRING, string, start_line, start_column)

    def read_identifier(self) -> Token:
        """读取标识符或关键字"""
        start_line = self.line
        start_column = self.column
        identifier = ''

        while self.peek and (self.peek().isalnum() or self.peek() == '_'):
            identifier += self.advance()

        # 检查是否是关键字
        token_type = self.KEYWORDS.get(identifier.lower(), TokenType.IDENTIFIER)

        return Token(token_type, identifier, start_line, start_column)

    def tokenize(self) -> List[Token]:
        """词法分析，返回token列表"""

        while self.pos < len(self.code):
            self.skip_whitespace()

            #跳过注释
            if self.skip_comment():
                continue

            char = self.peek()

            if char is None:
                break

            #换行
            if char == '\n':
                line = self.line
                col = self.column
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\n', line, col))
                continue

            # 数字
            if char.isdigit() or (char == '-' and self.peek(1) and self.peek(1).isdigit()):
                self.tokens.append(self.read_number())
                continue

            # 字符串
            if char in '"\'':
                self.tokens.append(self.read_string())
                continue

            # 标识符或关键字
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue

            # 符号
            line = self.line
            col = self.column

            if char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', line, col))
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', line, col))
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', line, col))
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', line, col))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', line, col))
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', line, col))
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', line, col))
            else:
                self.error(f"未知字符: '{char}'")

        # 添加EOF标记
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))

        return self.tokens


if __name__ == "__main__":
    test_code = """
    Sequential myList {
        init [1, 2, 3, 4, 5]
        insert 10 at 2
        search 10
        save "mylist.json"
    }
    """

    lexer = Lexer(test_code)
    tokens = lexer.tokenize()

    print("=== Token流 ===")
    for token in tokens:
        if token.type != TokenType.NEWLINE:
            print(token)




