
"""
DSL语法分析器 (Parser)
负责将Token流解析为抽象语法树(AST)
"""

from typing import List, Dict, Any, Optional
from .lexer import Token, TokenType, Lexer
from .ast_nodes import *


class Parser:
    """语法分析器"""
    def __init__(self,tokens:List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    def error(self, message: str):
        """报错"""
        if self.current_token:
            raise SyntaxError(
                f"[Parser Error] Line {self.current_token.line}:{self.current_token.column} - {message}"
            )
        raise SyntaxError(f"[Parser Error] {message}")

    def peek(self, offset: int = 0) -> Optional[Token]:
        """查看token但不移动"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def advance(self) -> Token:
        """移动到下一个token"""
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
        return token

    def expect(self, token_type: TokenType) -> Token:
        """期望特定类型的token"""
        if self.current_token is None:
            self.error(f"Expected {token_type.name}, got EOF")
        if self.current_token.type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
        return self.advance()

    def skip_newlines(self):
        """跳过换行符"""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def parse(self) -> Program:
        """解析整个程序"""
        structures = []

        self.skip_newlines()

        while self.current_token and self.current_token.type != TokenType.EOF:
            structures.append(self.parse_structure_declaration())
            self.skip_newlines()

        return Program(structures=structures, line=1, column=1)

    def parse_structure_declaration(self) -> StructureDeclaration:
        """解析数据结构声明"""
        self.skip_newlines()

        # 获取结构类型
        structure_types = [
            TokenType.SEQUENTIAL, TokenType.LINKED, TokenType.STACK, TokenType.QUEUE,
            TokenType.BINARY, TokenType.BST, TokenType.AVL, TokenType.HUFFMAN
        ]

        if self.current_token.type not in structure_types:
            self.error(f"Expected structure type, got {self.current_token.type.name}")

        structure_token = self.advance()
        structure_type = structure_token.value
        line = structure_token.line
        column = structure_token.column

        # 获取结构名称(可选)
        name = "default"
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            name = self.advance().value

        # 期望 {
        self.expect(TokenType.LBRACE)
        self.skip_newlines()

        # 解析操作列表
        operations = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            operations.append(self.parse_operation(structure_type))
            self.skip_newlines()

        # 期望 }
        self.expect(TokenType.RBRACE)

        return StructureDeclaration(
            structure_type=structure_type,
            name=name,
            operations=operations,
            line=line,
            column=column
        )

    def parse_operation(self, structure_type: str) -> Operation:
        """解析操作"""
        self.skip_newlines()

        if not self.current_token:
            self.error("Unexpected end of input")

        token = self.current_token
        line = token.line
        column = token.column

        # init [1, 2, 3] 或 init [1, 2, 3] capacity 10
        if token.type == TokenType.INIT:
            self.advance()
            values = self.parse_array()
            capacity = None
            # 检查是否有 capacity 关键字
            if self.current_token and self.current_token.type == TokenType.CAPACITY:
                self.advance()  # 跳过 capacity
                capacity = self.expect(TokenType.NUMBER).value
            return InitOperation(values=values, capacity=capacity, line=line, column=column)

        # insert 10 at 2
        elif token.type == TokenType.INSERT:
            self.advance()
            value = self.parse_value()
            index = None
            if self.current_token and self.current_token.type == TokenType.AT:
                self.advance()
                index = self.expect(TokenType.NUMBER).value
            return InsertOperation(value=value, index=index, line=line, column=column)

        # delete at 2 或 delete 5
        elif token.type == TokenType.DELETE:
            self.advance()
            # 检查是否是 "delete at index" 还是 "delete value"
            if self.current_token and self.current_token.type == TokenType.AT:
                self.advance()  # 跳过 at
                index = self.expect(TokenType.NUMBER).value
                return DeleteOperation(index=index, value=None, line=line, column=column)
            else:
                # 按值删除
                value = self.parse_value()
                return DeleteOperation(index=None, value=value, line=line, column=column)

        # search 10
        elif token.type == TokenType.SEARCH:
            self.advance()
            value = self.parse_value()
            return SearchOperation(value=value, line=line, column=column)

        # clear
        elif token.type == TokenType.CLEAR:
            self.advance()
            return ClearOperation(line=line, column=column)

        # save "file.json"
        elif token.type == TokenType.SAVE:
            self.advance()
            filename = self.expect(TokenType.STRING).value
            return SaveOperation(filename=filename, line=line, column=column)

        # load "file.json"
        elif token.type == TokenType.LOAD:
            self.advance()
            filename = self.expect(TokenType.STRING).value
            return LoadOperation(filename=filename, line=line, column=column)

        # export "file.dsl"
        elif token.type == TokenType.EXPORT:
            self.advance()
            filename = self.expect(TokenType.STRING).value
            return ExportOperation(filename=filename, line=line, column=column)

        # import "file.dsl"
        elif token.type == TokenType.IMPORT:
            self.advance()
            filename = self.expect(TokenType.STRING).value
            return ImportOperation(filename=filename, line=line, column=column)

        # push 10
        elif token.type == TokenType.PUSH:
            self.advance()
            value = self.parse_value()
            return PushOperation(value=value, line=line, column=column)

        # pop
        elif token.type == TokenType.POP:
            self.advance()
            return PopOperation(line=line, column=column)

        # peek
        elif token.type == TokenType.PEEK:
            self.advance()
            return PeekOperation(line=line, column=column)

        # enqueue 10
        elif token.type == TokenType.ENQUEUE:
            self.advance()
            value = self.parse_value()
            return EnqueueOperation(value=value, line=line, column=column)

        # dequeue
        elif token.type == TokenType.DEQUEUE:
            self.advance()
            return DequeueOperation(line=line, column=column)

        # front
        elif token.type == TokenType.FRONT:
            self.advance()
            return FrontOperation(line=line, column=column)

        # rear
        elif token.type == TokenType.REAR:
            self.advance()
            return RearOperation(line=line, column=column)

        # build [1, 2, 3, null, 4]
        elif token.type == TokenType.BUILD:
            self.advance()
            values = self.parse_array()
            return BuildOperation(values=values, line=line, column=column)

        # traverse inorder
        elif token.type == TokenType.TRAVERSE:
            self.advance()
            method_token = self.current_token
            if method_token.type not in [TokenType.PREORDER, TokenType.INORDER,
                                         TokenType.POSTORDER, TokenType.LEVELORDER]:
                self.error("Expected traversal method")
            method = self.advance().value
            return TraverseOperation(method=method, line=line, column=column)

        # height
        elif token.type == TokenType.HEIGHT:
            self.advance()
            return HeightOperation(line=line, column=column)

        # min
        elif token.type == TokenType.MIN:
            self.advance()
            return MinOperation(line=line, column=column)

        # max
        elif token.type == TokenType.MAX:
            self.advance()
            return MaxOperation(line=line, column=column)

        # reverse
        elif token.type == TokenType.REVERSE:
            self.advance()
            return ReverseOperation(line=line, column=column)

        # build_text "HELLO"
        elif token.type == TokenType.BUILD_TEXT:
            self.advance()
            text = self.expect(TokenType.STRING).value
            return BuildTextOperation(text=text, line=line, column=column)

        # 🔥 build_numbers [2, 4, 6, 8]
        elif token.type == TokenType.BUILD_NUMBERS:
            self.advance()
            numbers = self.parse_array()
            return BuildNumbersOperation(numbers=numbers, line=line, column=column)

        # encode "HELLO"
        elif token.type == TokenType.ENCODE:
            self.advance()
            text = self.expect(TokenType.STRING).value
            return EncodeOperation(text=text, line=line, column=column)

        # decode "01010"
        elif token.type == TokenType.DECODE:
            self.advance()
            encoded = self.expect(TokenType.STRING).value
            return DecodeOperation(encoded=encoded, line=line, column=column)

        # show_codes
        elif token.type == TokenType.SHOW_CODES:
            self.advance()
            return ShowCodesOperation(line=line, column=column)

        # insert_head 10
        elif token.type == TokenType.INSERT_HEAD:
            self.advance()
            value = self.parse_value()
            return InsertHeadOperation(value=value, line=line, column=column)

        # insert_tail 10
        elif token.type == TokenType.INSERT_TAIL:
            self.advance()
            value = self.parse_value()
            return InsertTailOperation(value=value, line=line, column=column)

        # delete_head
        elif token.type == TokenType.DELETE_HEAD:
            self.advance()
            return DeleteHeadOperation(line=line, column=column)

        # delete_tail
        elif token.type == TokenType.DELETE_TAIL:
            self.advance()
            return DeleteTailOperation(line=line, column=column)

        # get 2
        elif token.type == TokenType.GET:
            self.advance()
            index = self.expect(TokenType.NUMBER).value
            return GetOperation(index=index, line=line, column=column)

        # size
        elif token.type == TokenType.SIZE:
            self.advance()
            return SizeOperation(line=line, column=column)

        # speed 2x
        elif token.type == TokenType.SPEED:
            self.advance()
            speed = self.parse_value()
            return SpeedOperation(speed=str(speed), line=line, column=column)

        # pause 2s
        elif token.type == TokenType.PAUSE:
            self.advance()
            duration = None
            if self.current_token and self.current_token.type != TokenType.NEWLINE:
                duration = self.parse_value()
            return PauseOperation(duration=str(duration) if duration else None,
                                  line=line, column=column)

        else:
            self.error(f"Unknown operation: {token.type.name}")

    def parse_value(self) -> Any:
        """解析值"""
        if self.current_token.type == TokenType.NUMBER:
            return self.advance().value
        elif self.current_token.type == TokenType.STRING:
            return self.advance().value
        elif self.current_token.type == TokenType.RANDOM:
            # 解析 random(max) 或 random(min, max)
            return self.parse_random_call()
        elif self.current_token.type == TokenType.IDENTIFIER:
            identifier = self.advance().value
            # 处理 null/None
            if identifier.lower() in ['null', 'none']:
                return None
            return identifier
        else:
            self.error(f"Expected value, got {self.current_token.type.name}")

    def parse_random_call(self) -> RandomCall:
        """解析random函数调用 random(max) 或 random(min, max)"""
        line = self.current_token.line
        column = self.current_token.column
        self.advance()  # 跳过 random

        self.expect(TokenType.LPAREN)

        # 读取第一个参数
        first_arg = self.expect(TokenType.NUMBER).value

        # 检查是否有第二个参数
        if self.current_token.type == TokenType.COMMA:
            self.advance()  # 跳过逗号
            second_arg = self.expect(TokenType.NUMBER).value
            self.expect(TokenType.RPAREN)
            return RandomCall(min_value=first_arg, max_value=second_arg, line=line, column=column)
        else:
            self.expect(TokenType.RPAREN)
            return RandomCall(min_value=0, max_value=first_arg, line=line, column=column)

    def parse_array(self) -> List[Any]:
        """解析数组 [1, 2, 3]"""
        self.expect(TokenType.LBRACKET)

        elements = []
        while self.current_token and self.current_token.type != TokenType.RBRACKET:
            elements.append(self.parse_value())

            if self.current_token.type == TokenType.COMMA:
                self.advance()
            elif self.current_token.type != TokenType.RBRACKET:
                self.error("Expected ',' or ']'")

        self.expect(TokenType.RBRACKET)
        return elements


# 测试代码
if __name__ == "__main__":
    test_code = """
    Sequential myList {
        init [1, 2, 3, 4, 5]
        insert 10 at 2
        search 10
        delete at 3
        save "mylist.json"
    }

    BST myBST {
        insert 50
        insert 30
        insert 70
        traverse inorder
    }
    """

    # 词法分析
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()

    # 语法分析
    parser = Parser(tokens)
    ast = parser.parse()

    print("=== AST ===")
    print(ast_to_dict(ast))

