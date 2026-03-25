from typing import List
from ..lexer.token import Token, TokenType
from .ast import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        statements = []
        
        while True:
            self.skip_newlines()
            if self.is_at_end():
                break
            statements.append(self.declaration())
        
        return Program(statements)

    def skip_newlines(self):
        while not self.is_at_end() and self.check(TokenType.NEWLINE):
            self.advance()

    # Declaration parsing
    def declaration(self):
        if self.match(TokenType.VAR):
            return self.var_declaration()
        if self.match(TokenType.LET):
            return self.let_declaration()
        if self.match(TokenType.FUNC):
            return self.function_declaration()
        if self.match(TokenType.CLASS):
            return self.class_declaration()
        if self.match(TokenType.ENUM):
            return self.enum_declaration()
        if self.match(TokenType.IMPORT):
            return self.import_declaration()
        
        return self.statement()

    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect class name")
        
        methods = []
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body")
        self.skip_newlines()
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            self.skip_newlines()
            if self.match(TokenType.FUNC):
                method = self.function_declaration()
                methods.append(method)
            else:
                break
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body")
        
        return ClassDecl(name.lexeme, methods)

    def enum_declaration(self):
        name_token = self.consume(TokenType.IDENTIFIER, "Expect enum name")
        name = name_token.lexeme
        
        values = []
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before enum body")
        self.skip_newlines()
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            value_name = self.consume(TokenType.IDENTIFIER, "Expect enum value name")
            values.append(value_name.lexeme)
            self.skip_newlines()
            if self.match(TokenType.COMMA):
                self.skip_newlines()
            elif not self.check(TokenType.RIGHT_BRACE):
                break
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after enum body")
        
        return EnumDecl(name, values)

    def import_declaration(self):
        module_path_token = self.consume(TokenType.STRING, "Expect module path")
        module_path = module_path_token.literal
        
        alias = None
        if self.match(TokenType.AS):
            alias_token = self.consume(TokenType.IDENTIFIER, "Expect alias name")
            alias = alias_token.lexeme
        
        return ImportDecl(module_path, alias)

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name")
        
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        return VarDecl(name.lexeme, initializer)

    def let_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name")
        
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        return LetDecl(name.lexeme, initializer)

    def function_declaration(self):
        if self.check(TokenType.INIT):
            name = "init"
            self.advance()
        else:
            name = self.consume(TokenType.IDENTIFIER, "Expect function name").lexeme
        
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name")
        
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            self.skip_newlines()
            while True:
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name").lexeme)
                if not self.match(TokenType.COMMA):
                    break
                self.skip_newlines()
        
        self.skip_newlines()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters")
        self.skip_newlines()
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before function body")
        
        body = self.block()
        
        return FunctionDecl(name, parameters, body)

    # Statement parsing
    def statement(self):
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.MATCH):
            return self.match_statement()
        if self.match(TokenType.TRY):
            return self.try_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.BREAK):
            return BreakStmt()
        if self.match(TokenType.CONTINUE):
            return ContinueStmt()
        
        return self.expression_statement()

    def if_statement(self):
        condition = self.expression()
        
        then_branch = self.block_or_statement()
        
        elif_branches = []
        else_branch = None
        
        while self.match(TokenType.ELIF):
            elif_cond = self.expression()
            elif_body = self.block_or_statement()
            elif_branches.append((elif_cond, elif_body))
        
        if self.match(TokenType.ELSE):
            else_branch = self.block_or_statement()
        
        return IfStmt(condition, then_branch, elif_branches, else_branch)

    def for_statement(self):
        var_name = None
        if not self.check(TokenType.IN):
            var_token = self.consume(TokenType.IDENTIFIER, "Expect loop variable")
            var_name = var_token.lexeme
            self.consume(TokenType.IN, "Expect 'in' after variable")
        
        iterator = self.expression()
        
        body = self.block_or_statement()
        
        return ForStmt(var_name, iterator, body)

    def while_statement(self):
        condition = self.expression()
        body = self.block_or_statement()
        
        return WhileStmt(condition, body)

    def match_statement(self):
        subject = self.expression()
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after match subject")
        self.skip_newlines()
        
        cases = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            self.skip_newlines()
            
            if not self.match(TokenType.CASE) and not self.match(TokenType.DEFAULT):
                break
            
            pattern = None
            if self.previous().type == TokenType.CASE:
                pattern = self.expression()
            
            self.consume(TokenType.ARROW, "Expect '=>' after case pattern")
            
            body = self.block_or_statement()
            cases.append((pattern, body))
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after match cases")
        
        return MatchStmt(subject, cases)

    def try_statement(self):
        try_body = self.block_or_statement()
        
        catch_var = None
        catch_body = []
        if self.match(TokenType.CATCH):
            if self.match(TokenType.IDENTIFIER):
                catch_var = self.previous().lexeme
            catch_body = self.block_or_statement()
        
        finally_body = []
        if self.match(TokenType.FINALLY):
            finally_body = self.block_or_statement()
        
        return TryStmt(try_body, catch_var, catch_body, finally_body)

    def return_statement(self):
        value = None
        self.skip_newlines()
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.EOF) and not self.check(TokenType.RIGHT_BRACE):
            value = self.expression()
        
        return ReturnStmt(value)

    def block(self):
        statements = []
        
        self.skip_newlines()
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.check(TokenType.EOF):
                break
            statements.append(self.declaration())
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block")
        
        return statements

    def block_or_statement(self):
        if self.match(TokenType.LEFT_BRACE):
            return self.block()
        else:
            return [self.statement()]

    def statement(self):
        self.skip_newlines()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.MATCH):
            return self.match_statement()
        if self.match(TokenType.TRY):
            return self.try_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.BREAK):
            return BreakStmt()
        if self.match(TokenType.CONTINUE):
            return ContinueStmt()
        
        return self.expression_statement()

    def expression_statement(self):
        self.skip_newlines()
        expr = self.expression()
        return ExprStmt(expr)

    # Expression parsing
    def expression(self):
        return self.assignment()
    
    def assignment(self):
        left = self.ternary()
        
        if self.match(TokenType.EQUAL):
            if isinstance(left, Identifier):
                value = self.assignment()
                return AssignExpr(left.name, value)
            if isinstance(left, GetExpr):
                value = self.assignment()
                return SetExpr(left.object, left.name, value)
        
        return left

    def ternary(self):
        left = self.or_expr()
        
        if self.match(TokenType.QUESTION):
            then_expr = self.ternary()
            self.consume(TokenType.COLON, "Expect ':' after ternary then-expression")
            else_expr = self.ternary()
            return ConditionalExpr(left, then_expr, else_expr)
        
        return left

    def or_expr(self):
        left = self.and_expr()
        
        while self.match(TokenType.OR):
            right = self.and_expr()
            left = BinaryExpr(left, "or", right)
        
        return left

    def and_expr(self):
        left = self.comparison()
        
        while self.match(TokenType.AND):
            right = self.comparison()
            left = BinaryExpr(left, "and", right)
        
        return left

    def comparison(self):
        left = self.range_expr()
        
        while self.match_in(TokenType.GREATER, TokenType.GREATER_EQUAL,
                           TokenType.LESS, TokenType.LESS_EQUAL,
                           TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator = self.previous().lexeme
            right = self.range_expr()
            left = BinaryExpr(left, operator, right)
        
        return left

    def range_expr(self):
        left = self.bitwise_or()
        
        if self.match(TokenType.DOTDOT):
            right = self.bitwise_or()
            return BinaryExpr(left, "..", right)
        
        return left

    def addition(self):
        left = self.multiplication()
        
        while self.match_in(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().lexeme
            right = self.multiplication()
            left = BinaryExpr(left, operator, right)
        
        return left

    def multiplication(self):
        left = self.unary()
        
        while self.match_in(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.DOUBLE_SLASH):
            operator = self.previous().lexeme
            right = self.unary()
            left = BinaryExpr(left, operator, right)
        
        return left

    def bitwise_or(self):
        left = self.bitwise_xor()
        
        while self.match_in(TokenType.OR, TokenType.DOUBLE_PIPE):
            operator = self.previous().lexeme
            right = self.bitwise_xor()
            left = BinaryExpr(left, operator, right)
        
        return left

    def bitwise_xor(self):
        left = self.bitwise_and()
        
        while self.match(TokenType.CARET):
            operator = self.previous().lexeme
            right = self.bitwise_and()
            left = BinaryExpr(left, operator, right)
        
        return left

    def bitwise_and(self):
        left = self.bitwise_shift()
        
        while self.match_in(TokenType.AND, TokenType.DOUBLE_AMP):
            operator = self.previous().lexeme
            right = self.bitwise_shift()
            left = BinaryExpr(left, operator, right)
        
        return left

    def bitwise_shift(self):
        left = self.addition()
        
        while self.match_in(TokenType.DOUBLE_LESS, TokenType.DOUBLE_GREATER):
            operator = self.previous().lexeme
            right = self.addition()
            left = BinaryExpr(left, operator, right)
        
        return left

    def unary(self):
        if self.match_in(TokenType.BANG, TokenType.MINUS):
            operator = self.previous().lexeme
            right = self.unary()
            return UnaryExpr(operator, right)
        
        return self.exponent()

    def exponent(self):
        left = self.call()
        
        if self.match(TokenType.CARET):
            right = self.unary()
            return BinaryExpr(left, "^", right)
        
        return left

    def call(self):
        expr = self.primary()
        
        while True:
                if self.match(TokenType.LEFT_PAREN):
                    arguments = []
                    self.skip_newlines()
                    if not self.check(TokenType.RIGHT_PAREN):
                        while True:
                            self.skip_newlines()
                            arguments.append(self.expression())
                            self.skip_newlines()
                            if not self.match(TokenType.COMMA):
                                break
                    self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")
                    expr = CallExpr(expr, arguments)
                elif self.match(TokenType.LEFT_BRACKET):
                    index = self.expression()
                    self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after index")
                    expr = IndexExpr(expr, index)
                elif self.match(TokenType.DOT):
                    name = self.consume(TokenType.IDENTIFIER, "Expect property name")
                    if self.match(TokenType.LEFT_PAREN):
                        arguments = []
                        if not self.check(TokenType.RIGHT_PAREN):
                            while True:
                                arguments.append(self.expression())
                                if not self.match(TokenType.COMMA):
                                    break
                        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")
                        expr = CallExpr(GetExpr(expr, name.lexeme), arguments)
                    else:
                        expr = GetExpr(expr, name.lexeme)
                else:
                    break
        
        return expr

    def primary(self):
        if self.match(TokenType.NUMBER):
            return NumberLiteral(self.previous().literal)
        
        if self.match(TokenType.STRING):
            return StringLiteral(self.previous().literal)
        
        if self.match(TokenType.TRUE):
            return BooleanLiteral(True)
        
        if self.match(TokenType.FALSE):
            return BooleanLiteral(False)
        
        if self.match(TokenType.NIL):
            return NilLiteral()
        
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.previous().lexeme)
        
        if self.match(TokenType.SELF):
            return SelfExpr()
        
        if self.match(TokenType.LEFT_PAREN):
            self.skip_newlines()
            expr = self.expression()
            self.skip_newlines()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return expr
        
        if self.match(TokenType.LEFT_BRACKET):
            return self.list_literal()
        
        if self.match(TokenType.LEFT_BRACE):
            return self.dict_literal()
        
        self.error(f"Unexpected token: {self.peek()}")

    def list_literal(self):
        elements = []
        
        if not self.check(TokenType.RIGHT_BRACKET):
            self.skip_newlines()
            while True:
                elements.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
                self.skip_newlines()
        
        self.skip_newlines()
        self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after list elements")
        return ListLiteral(elements)

    def dict_literal(self):
        entries = []
        
        if not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            while True:
                key = self.expression()
                self.consume(TokenType.COLON, "Expect ':' after key in dict")
                value = self.expression()
                entries.append((key, value))
                
                if not self.match(TokenType.COMMA):
                    break
                self.skip_newlines()
        
        self.skip_newlines()
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after dict entries")
        return DictLiteral(entries)

    # Helper methods
    def match(self, *types):
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def match_in(self, *types):
        return self.match(*types)

    def check(self, t):
        if self.is_at_end():
            return False
        return self.peek().type == t

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def consume(self, t, message):
        if self.check(t):
            return self.advance()
        self.error(message)

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, message):
        token = self.peek()
        line = token.line if hasattr(token, 'line') else 1
        column = token.column if hasattr(token, 'column') else 1
        raise RuntimeError(f"Parse error at line {line}, column {column}: {message}")


def parse(tokens: List[Token]) -> Program:
    parser = Parser(tokens)
    return parser.parse()