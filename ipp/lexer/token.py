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
    SUPER = auto()
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
    STATIC = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()       # ^ bitwise XOR
    DOTDOT = auto()
    QUESTION = auto()
    DOUBLE_COLON = auto()   # ::  (COLONCOLON removed as duplicate)
    ARROW = auto()           # =>
    DOUBLE_AMP = auto()      # &&
    DOUBLE_PIPE = auto()     # ||
    DOUBLE_LESS = auto()     # <<
    DOUBLE_GREATER = auto()  # >>
    TILDE = auto()           # ~
    DOUBLE_SLASH = auto()    # //
    DOUBLE_STAR = auto()     # **  power
    QUESTION_DOT = auto()    # ?.
    DOUBLE_QUESTION = auto() # ??
    TRIPLE_DOT = auto()      # ...
    PIPE = auto()            # |>  pipeline

    EQUAL = auto()
    EQUAL_EQUAL = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Compound assignment  (FIX: BUG-L / DESIGN-1)
    PLUS_EQUAL = auto()      # +=
    MINUS_EQUAL = auto()     # -=
    STAR_EQUAL = auto()      # *=
    SLASH_EQUAL = auto()     # /=
    PERCENT_EQUAL = auto()   # %=

    AND = auto()   # keyword 'and'
    OR = auto()    # keyword 'or'

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
    "super": TokenType.SUPER,
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
    "repeat": TokenType.REPEAT,
    "until": TokenType.UNTIL,
    "throw": TokenType.THROW,
    "with": TokenType.WITH,
    "static": TokenType.STATIC,
    "this": TokenType.SELF,      # alias for self
    "and": TokenType.AND,          # 'and' keyword → dedicated AND token
    "or": TokenType.OR,            # 'or' keyword  → dedicated OR token
    "not": TokenType.BANG,         # 'not' keyword maps to logical NOT
}
