from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any


class ASTNode(ABC):
    line: int = 0
    
    @abstractmethod
    def accept(self, visitor):
        pass


# Expression nodes
@dataclass
class NumberLiteral(ASTNode):
    value: float
    
    def accept(self, visitor):
        return visitor.visit_number_literal(self)


@dataclass
class StringLiteral(ASTNode):
    value: str
    
    def accept(self, visitor):
        return visitor.visit_string_literal(self)


@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    
    def accept(self, visitor):
        return visitor.visit_boolean_literal(self)


@dataclass
class NilLiteral(ASTNode):
    def accept(self, visitor):
        return visitor.visit_nil_literal(self)


@dataclass
class Identifier(ASTNode):
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)


@dataclass
class SelfExpr(ASTNode):
    def accept(self, visitor):
        return visitor.visit_self_expr(self)


@dataclass
class AssignExpr(ASTNode):
    name: str
    value: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_assign_expr(self)


@dataclass
class SetExpr(ASTNode):
    object: ASTNode
    name: str
    value: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_set_expr(self)


@dataclass
class BinaryExpr(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


@dataclass
class UnaryExpr(ASTNode):
    operator: str
    right: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


@dataclass
class CallExpr(ASTNode):
    callee: ASTNode
    arguments: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_call_expr(self)


@dataclass
class IndexExpr(ASTNode):
    object: ASTNode
    index: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_index_expr(self)


@dataclass
class GetExpr(ASTNode):
    object: ASTNode
    name: str
    
    def accept(self, visitor):
        return visitor.visit_get_expr(self)


@dataclass
class DictLiteral(ASTNode):
    entries: List[tuple[ASTNode, ASTNode]]
    
    def accept(self, visitor):
        return visitor.visit_dict_literal(self)


@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_list_literal(self)


@dataclass
class LambdaExpr(ASTNode):
    parameters: List[str]
    body: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_lambda_expr(self)


# Statement nodes
@dataclass
class VarDecl(ASTNode):
    name: str
    initializer: Optional[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_var_decl(self)


@dataclass
class LetDecl(ASTNode):
    name: str
    initializer: Optional[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_let_decl(self)


@dataclass
class FunctionDecl(ASTNode):
    name: str
    parameters: List[str]
    body: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_function_decl(self)


@dataclass
class ImportDecl(ASTNode):
    module_path: str
    alias: Optional[str]
    
    def accept(self, visitor):
        return visitor.visit_import_decl(self)


@dataclass
class ClassDecl(ASTNode):
    name: str
    methods: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_class_decl(self)


@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_branch: List[ASTNode]
    elif_branches: List[tuple[ASTNode, List[ASTNode]]]
    else_branch: Optional[List[ASTNode]]
    
    def accept(self, visitor):
        return visitor.visit_if_stmt(self)


@dataclass
class ForStmt(ASTNode):
    variable: Optional[str]
    iterator: ASTNode
    body: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_for_stmt(self)


@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_while_stmt(self)


@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_return_stmt(self)


@dataclass
class BreakStmt(ASTNode):
    def accept(self, visitor):
        return visitor.visit_break_stmt(self)


@dataclass
class ContinueStmt(ASTNode):
    def accept(self, visitor):
        return visitor.visit_continue_stmt(self)


@dataclass
class ExprStmt(ASTNode):
    expression: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_expr_stmt(self)


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_program(self)