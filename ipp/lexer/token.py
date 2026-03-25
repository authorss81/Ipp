from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    TRUE = auto()
    FALSE = auto()
    NIL = auto()

    # Keywords
    VAR = auto()
    LET = auto()
    FUNC = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    IN = auto()
    IMPORT = auto()
    AS = auto()
    CLASS = auto()
    SELF = auto()
    INIT = auto()
    MATCH = auto()
    CASE = auto()
    DEFAULT = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    ENUM = auto()
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    VOID = auto()
    REPEAT = auto()
    UNTIL = auto()
    THROW = auto()
    WITH = auto()
    COLONCOLON = auto()
    STATIC = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()
    DOTDOT = auto()
    QUESTION = auto()
    DOUBLE_COLON = auto()
    ARROW = auto()
    DOUBLE_AMP = auto()
    DOUBLE_PIPE = auto()
    DOUBLE_LESS = auto()
    DOUBLE_GREATER = auto()
    TILDE = auto()
    DOUBLE_SLASH = auto()
    DOUBLE_STAR = auto()
    QUESTION_DOT = auto()
    DOUBLE_QUESTION = auto()
    TRIPLE_DOT = auto()
    PIPE = auto()
    ARROW2 = auto()

    EQUAL = auto()
    EQUAL_EQUAL = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    AND = auto()
    OR = auto()

    # Delimiters
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()

    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.lexeme!r}, line={self.line})"


KEYWORDS = {
    "var": TokenType.VAR,
    "let": TokenType.LET,
    "func": TokenType.FUNC,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "in": TokenType.IN,
    "import": TokenType.IMPORT,
    "as": TokenType.AS,
    "class": TokenType.CLASS,
    "self": TokenType.SELF,
    "init": TokenType.INIT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "nil": TokenType.NIL,
    "match": TokenType.MATCH,
    "case": TokenType.CASE,
    "default": TokenType.DEFAULT,
    "try": TokenType.TRY,
    "catch": TokenType.CATCH,
    "finally": TokenType.FINALLY,
    "enum": TokenType.ENUM,
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "number": TokenType.NUMBER,
    "string": TokenType.STRING,
    "bool": TokenType.BOOL,
    "void": TokenType.VOID,
    "repeat": TokenType.REPEAT,
    "until": TokenType.UNTIL,
    "throw": TokenType.THROW,
    "with": TokenType.WITH,
    "static": TokenType.STATIC,
}