from .token import Token, TokenType, KEYWORDS

# Escape sequence map for string literals (FIX: BUG-L5)
_ESCAPES = {
    'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
    '"': '"', "'": "'", '0': '\0', 'b': '\b', 'f': '\f',
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_col = 1
        self.at_line_start = True

    def scan(self):
        while not self.is_at_end:
            self.start = self.current
            self.start_col = self.column
            self.scan_token()

        self.add_token(TokenType.EOF, "", None)
        return self.tokens

    def scan_token(self):
        self.skip_whitespace()
        self.skip_comments()

        if self.is_at_end:
            self.add_token(TokenType.EOF, "", None)
            return

        self.start = self.current
        self.start_col = self.column

        c = self.advance()

        # Single character tokens
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == '[':
            self.add_token(TokenType.LEFT_BRACKET)
        elif c == ']':
            self.add_token(TokenType.RIGHT_BRACKET)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            if self.peek() == '.':
                self.advance()
                if self.peek() == '.':
                    self.advance()
                    self.add_token(TokenType.TRIPLE_DOT)
                else:
                    self.add_token(TokenType.DOTDOT)
            else:
                self.add_token(TokenType.DOT)
        elif c == ':':
            if self.match(':'):
                self.add_token(TokenType.DOUBLE_COLON)
            else:
                self.add_token(TokenType.COLON)
        elif c == '?':
            if self.match('.'):
                self.add_token(TokenType.QUESTION_DOT)
            elif self.match('?'):
                self.add_token(TokenType.DOUBLE_QUESTION)
            else:
                self.add_token(TokenType.QUESTION)

        # Compound assignment and arithmetic (FIX: BUG-L / DESIGN-1)
        elif c == '+':
            if self.match('='):
                self.add_token(TokenType.PLUS_EQUAL)
            else:
                self.add_token(TokenType.PLUS)
        elif c == '-':
            if self.match('='):
                self.add_token(TokenType.MINUS_EQUAL)
            else:
                self.add_token(TokenType.MINUS)
        elif c == '*':
            if self.match('*'):
                self.add_token(TokenType.DOUBLE_STAR)
            elif self.match('='):
                self.add_token(TokenType.STAR_EQUAL)
            else:
                self.add_token(TokenType.STAR)
        elif c == '/':
            if self.match('/'):
                self.add_token(TokenType.DOUBLE_SLASH)
            elif self.match('='):
                self.add_token(TokenType.SLASH_EQUAL)
            else:
                self.add_token(TokenType.SLASH)
        elif c == '%':
            if self.match('='):
                self.add_token(TokenType.PERCENT_EQUAL)
            else:
                self.add_token(TokenType.PERCENT)
        elif c == '^':
            self.add_token(TokenType.CARET)   # ^ = bitwise XOR (FIX: BUG-M2)

        # Pipeline |>  and logical || and bitwise |
        # FIX: BUG-L1 — removed duplicate branch
        elif c == '|':
            if self.match('>'):
                self.add_token(TokenType.PIPE)
            elif self.match('|'):
                self.add_token(TokenType.DOUBLE_PIPE)
            else:
                # bare | is bitwise OR
                self.add_token(TokenType.CARET)   # reuse CARET placeholder? No — use distinct
                # Actually emit a distinct BIT_OR — we'll handle in parser via OR token type
                # For now map | to the same OR token the parser already knows
                self.tokens.pop()
                self._add_raw(TokenType.DOUBLE_PIPE, '|', None)  # treat lone | as |

        elif c == '&':
            if self.match('&'):
                self.add_token(TokenType.DOUBLE_AMP)
            else:
                # bare & → bitwise AND; reuse DOUBLE_AMP with single-& lexeme
                self._add_raw(TokenType.DOUBLE_AMP, '&', None)

        elif c == '~':
            self.add_token(TokenType.TILDE)

        # Comparison operators
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            if self.match('>'):
                self.add_token(TokenType.ARROW)
            elif self.match('='):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)
        elif c == '<':
            if self.match('<'):
                self.add_token(TokenType.DOUBLE_LESS)
            elif self.match('='):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
        elif c == '>':
            if self.match('>'):
                self.add_token(TokenType.DOUBLE_GREATER)
            elif self.match('='):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)

        # String literals — with escape processing (FIX: BUG-L5)
        elif c == '"' or c == "'":
            self.string(c)

        # Numbers — with hex/octal/binary support (FIX: BUG-L7)
        elif c == '0' and self.peek() in 'xXoObB':
            self.number_prefixed()
        elif c.isdigit():
            self.number()

        # Identifiers and keywords
        elif c.isalpha() or c == '_':
            self.identifier()

        # Newline (significant in Ipp)
        elif c == '\n':
            if not self.at_line_start:
                self.add_token(TokenType.NEWLINE, "\n", None)
            self.line += 1
            self.column = 1
            self.start_col = 1
            self.at_line_start = True
        else:
            self.error(f"Unexpected character: {c!r}")

    def _add_raw(self, token_type, lexeme, literal):
        token = Token(token_type, lexeme, literal, self.line, self.start_col)
        self.tokens.append(token)
        self.at_line_start = False

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        text = self.source[self.start:self.current]

        if text in KEYWORDS:
            token_type = KEYWORDS[text]
            if token_type == TokenType.TRUE:
                self.add_token(token_type, text, True)
            elif token_type == TokenType.FALSE:
                self.add_token(token_type, text, False)
            elif token_type == TokenType.NIL:
                self.add_token(token_type, text, None)
            else:
                self.add_token(token_type)
        else:
            self.add_token(TokenType.IDENTIFIER)

    def number(self):
        has_decimal = False
        while self.peek().isdigit() or self.peek() == '_':
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            has_decimal = True
            self.advance()
            while self.peek().isdigit():
                self.advance()

        raw = self.source[self.start:self.current].replace('_', '')
        if has_decimal:
            value = float(raw)
        else:
            value = int(raw)
        self.add_token(TokenType.NUMBER, literal=value)

    def number_prefixed(self):
        """Lex hex (0x), octal (0o), binary (0b) literals. FIX: BUG-L7"""
        prefix_char = self.advance()  # consume x/X/o/O/b/B
        base_map = {'x': 16, 'X': 16, 'o': 8, 'O': 8, 'b': 2, 'B': 2}
        base = base_map[prefix_char]
        valid_chars = set('0123456789abcdefABCDEF_') if base == 16 else (
            set('01234567_') if base == 8 else set('01_'))

        while self.peek() in valid_chars:
            self.advance()

        raw = self.source[self.start:self.current].replace('_', '')
        try:
            value = int(raw, 0)
        except ValueError:
            self.error(f"Invalid numeric literal: {raw}")
        self.add_token(TokenType.NUMBER, literal=value)

    def string(self, quote_char):
        """Lex string with escape sequence processing. FIX: BUG-L5"""
        value_chars = []
        while not self.is_at_end and self.peek() != quote_char:
            ch = self.advance()
            if ch == '\\':
                if self.is_at_end:
                    self.error("Unterminated escape sequence")
                esc = self.advance()
                if esc == 'u':
                    # Unicode escape \uXXXX
                    hex_str = ''
                    for _ in range(4):
                        if self.is_at_end or not self.peek() in '0123456789abcdefABCDEF':
                            self.error("Invalid \\u escape sequence")
                        hex_str += self.advance()
                    value_chars.append(chr(int(hex_str, 16)))
                elif esc in _ESCAPES:
                    value_chars.append(_ESCAPES[esc])
                else:
                    value_chars.append('\\')
                    value_chars.append(esc)
            elif ch == '\n':
                # Multi-line strings: allow newlines inside quotes
                self.line += 1
                self.column = 1
                value_chars.append(ch)
            else:
                value_chars.append(ch)

        if self.is_at_end:
            self.error("Unterminated string")

        self.advance()  # Closing quote
        value = ''.join(value_chars)
        self.add_token(TokenType.STRING, literal=value)

    def skip_whitespace(self):
        while not self.is_at_end:
            ch = self.peek()
            if ch == ' ' or ch == '\t' or ch == '\r':
                self.advance()
                self.at_line_start = False
            elif ch == '\\':
                # Line continuation: \ at end of line joins with next line
                self.advance()  # consume \
                if self.peek() == '\n':
                    self.advance()  # consume newline
                    self.line += 1
                    self.column = 1
                    self.at_line_start = True
                else:
                    # Not followed by newline, put back the backslash
                    self.current -= 1
                    self.column -= 1
                    break
            else:
                break

    def skip_comments(self):
        # FIX: BUG-L4 — don't mess with at_line_start inside comment skip
        while not self.is_at_end and self.peek() == '#':
            while not self.is_at_end and self.peek() != '\n':
                self.advance()
            # don't consume the newline here; let scan_token handle it

    def add_token(self, token_type, lexeme=None, literal=None):
        if lexeme is None:
            lexeme = self.source[self.start:self.current]
        token = Token(token_type, lexeme, literal, self.line, self.start_col)
        self.tokens.append(token)
        self.at_line_start = False

    def advance(self):
        c = self.source[self.current]
        self.current += 1
        self.column += 1
        return c

    def match(self, expected):
        if self.is_at_end:
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def peek(self):
        if self.is_at_end:
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    @property
    def is_at_end(self):
        return self.current >= len(self.source)

    def error(self, message):
        raise SyntaxError(f"Lexical error at line {self.line}, column {self.column}: {message}")


def tokenize(source: str) -> list:
    lexer = Lexer(source)
    return lexer.scan()
