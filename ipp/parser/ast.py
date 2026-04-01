from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any


class ASTNode(ABC):
    line: int = 0

    @abstractmethod
    def accept(self, visitor):
        pass


# ─── Expression nodes ─────────────────────────────────────────────────────────

@dataclass
class NumberLiteral(ASTNode):
    value: float
    def accept(self, visitor): return visitor.visit_number_literal(self)

@dataclass
class StringLiteral(ASTNode):
    value: str
    def accept(self, visitor): return visitor.visit_string_literal(self)

@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    def accept(self, visitor): return visitor.visit_boolean_literal(self)

@dataclass
class NilLiteral(ASTNode):
    def accept(self, visitor): return visitor.visit_nil_literal(self)

@dataclass
class Identifier(ASTNode):
    name: str
    def accept(self, visitor): return visitor.visit_identifier(self)

@dataclass
class SelfExpr(ASTNode):
    def accept(self, visitor): return visitor.visit_self_expr(self)

@dataclass
class SuperExpr(ASTNode):
    """super.method() calls. FIX: BUG-C5 — was missing from AST."""
    method: str
    def accept(self, visitor): return visitor.visit_super_expr(self)

@dataclass
class AssignExpr(ASTNode):
    name: str
    value: ASTNode
    def accept(self, visitor): return visitor.visit_assign_expr(self)

@dataclass
class CompoundAssignExpr(ASTNode):
    """+=, -=, *=, /=, %= — FIX: DESIGN-1"""
    name: str
    operator: str   # '+', '-', '*', '/', '%'
    value: ASTNode
    def accept(self, visitor): return visitor.visit_compound_assign_expr(self)

@dataclass
class SetExpr(ASTNode):
    object: ASTNode
    name: str
    value: ASTNode
    def accept(self, visitor): return visitor.visit_set_expr(self)

@dataclass
class CompoundSetExpr(ASTNode):
    """obj.field += val"""
    object: ASTNode
    name: str
    operator: str
    value: ASTNode
    def accept(self, visitor): return visitor.visit_compound_set_expr(self)

@dataclass
class BinaryExpr(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    def accept(self, visitor): return visitor.visit_binary_expr(self)

@dataclass
class UnaryExpr(ASTNode):
    operator: str
    right: ASTNode
    def accept(self, visitor): return visitor.visit_unary_expr(self)

@dataclass
class NamedArg(ASTNode):
    """Named argument like f(x=1). FIX: BUG-NEW-M4"""
    name: str
    value: ASTNode
    def accept(self, visitor): return visitor.visit_named_arg(self)

@dataclass
class CallExpr(ASTNode):
    callee: ASTNode
    arguments: List[ASTNode]
    named_arguments: List[NamedArg] = field(default_factory=list)
    def accept(self, visitor): return visitor.visit_call_expr(self)

@dataclass
class IndexExpr(ASTNode):
    object: ASTNode
    index: ASTNode
    def accept(self, visitor): return visitor.visit_index_expr(self)

@dataclass
class IndexSetExpr(ASTNode):
    object: ASTNode
    index: ASTNode
    value: ASTNode
    def accept(self, visitor): return visitor.visit_index_set_expr(self)

@dataclass
class IndexCompoundSetExpr(ASTNode):
    """obj[i] += val"""
    object: ASTNode
    index: ASTNode
    operator: str
    value: ASTNode
    def accept(self, visitor): return visitor.visit_index_compound_set_expr(self)

@dataclass
class GetExpr(ASTNode):
    object: ASTNode
    name: str
    def accept(self, visitor): return visitor.visit_get_expr(self)

@dataclass
class DictLiteral(ASTNode):
    entries: List[tuple]
    def accept(self, visitor): return visitor.visit_dict_literal(self)

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    def accept(self, visitor): return visitor.visit_list_literal(self)

@dataclass
class LambdaExpr(ASTNode):
    parameters: List[str]
    body: List[ASTNode]
    defaults: Optional[List[Optional['ASTNode']]] = None
    def accept(self, visitor): return visitor.visit_lambda_expr(self)

@dataclass
class ListComprehension(ASTNode):
    element: ASTNode
    variable: str
    iterator: ASTNode
    condition: Optional[ASTNode] = None
    def accept(self, visitor): return visitor.visit_list_comprehension(self)

@dataclass
class DictComprehension(ASTNode):
    key: ASTNode
    value: ASTNode
    variable: str
    iterator: ASTNode
    condition: Optional[ASTNode] = None
    def accept(self, visitor): return visitor.visit_dict_comprehension(self)

@dataclass
class ConditionalExpr(ASTNode):
    condition: ASTNode
    then_expr: ASTNode
    else_expr: ASTNode
    def accept(self, visitor): return visitor.visit_conditional_expr(self)

@dataclass
class NullishCoalescingExpr(ASTNode):
    left: ASTNode
    right: ASTNode
    def accept(self, visitor): return visitor.visit_nullish_coalescing_expr(self)

@dataclass
class OptionalChainingExpr(ASTNode):
    object: ASTNode
    property: str
    def accept(self, visitor): return visitor.visit_optional_chaining_expr(self)

@dataclass
class SpreadExpr(ASTNode):
    iterable: ASTNode
    def accept(self, visitor): return visitor.visit_spread_expr(self)

@dataclass
class TupleLiteral(ASTNode):
    elements: List[ASTNode]
    def accept(self, visitor): return visitor.visit_tuple_literal(self)

@dataclass
class UnpackExpr(ASTNode):
    targets: List[str]
    iterable: ASTNode
    def accept(self, visitor): return visitor.visit_unpack_expr(self)


# ─── Statement nodes ──────────────────────────────────────────────────────────

@dataclass
class VarDecl(ASTNode):
    name: str
    initializer: Optional[ASTNode]
    type_hint: Optional[str] = None    # FIX: BUG-P2 — store annotation
    def accept(self, visitor): return visitor.visit_var_decl(self)

@dataclass
class MultiVarDecl(ASTNode):
    """Multiple variable declaration: var a, b = expr FIX: BUG-NEW-M7"""
    names: List[str]
    initializer: ASTNode
    def accept(self, visitor): return visitor.visit_multi_var_decl(self)

@dataclass
class LetDecl(ASTNode):
    name: str
    initializer: Optional[ASTNode]
    type_hint: Optional[str] = None
    def accept(self, visitor): return visitor.visit_let_decl(self)

@dataclass
class FunctionDecl(ASTNode):
    name: str
    parameters: List[str]
    body: List[ASTNode]
    param_types: Optional[List[Optional[str]]] = None   # FIX: BUG-P3
    defaults: Optional[List[Optional['ASTNode']]] = None  # Default values
    return_type: Optional[str] = None
    is_static: bool = False
    def accept(self, visitor): return visitor.visit_function_decl(self)

@dataclass
class ImportDecl(ASTNode):
    module_path: str
    alias: Optional[str] = None
    imports: Optional[List[str]] = None
    def accept(self, visitor): return visitor.visit_import_decl(self)

@dataclass
class ClassDecl(ASTNode):
    name: str
    methods: List[ASTNode]
    superclass: Optional[str] = None    # FIX: BUG-M6 — add superclass field
    def accept(self, visitor): return visitor.visit_class_decl(self)

@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_branch: List[ASTNode]
    elif_branches: List[tuple]
    else_branch: Optional[List[ASTNode]]
    def accept(self, visitor): return visitor.visit_if_stmt(self)

@dataclass
class ForStmt(ASTNode):
    variable: Optional[str]
    iterator: ASTNode
    body: List[ASTNode]
    def accept(self, visitor): return visitor.visit_for_stmt(self)

@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: List[ASTNode]
    def accept(self, visitor): return visitor.visit_while_stmt(self)

@dataclass
class DoWhileStmt(ASTNode):
    body: List[ASTNode]
    condition: ASTNode
    def accept(self, visitor): return visitor.visit_do_while_stmt(self)

@dataclass
class LabeledStmt(ASTNode):
    label: str
    statement: ASTNode
    def accept(self, visitor): return visitor.visit_labeled_stmt(self)

@dataclass
class BreakStmt(ASTNode):
    label: Optional[str] = None
    def accept(self, visitor): return visitor.visit_break_stmt(self)

@dataclass
class ContinueStmt(ASTNode):
    label: Optional[str] = None
    def accept(self, visitor): return visitor.visit_continue_stmt(self)

@dataclass
class ThrowStmt(ASTNode):
    expression: ASTNode
    def accept(self, visitor): return visitor.visit_throw_stmt(self)

@dataclass
class WithStmt(ASTNode):
    variable: str
    initializer: ASTNode
    body: List[ASTNode]
    def accept(self, visitor): return visitor.visit_with_stmt(self)

@dataclass
class MatchStmt(ASTNode):
    subject: ASTNode    # FIX: BUG-C4 — was ambiguously 'expression' in some places
    cases: List[tuple]
    def accept(self, visitor): return visitor.visit_match_stmt(self)

@dataclass
class TryStmt(ASTNode):
    try_body: List[ASTNode]
    catch_var: Optional[str]          # FIX: BUG-C3 — canonical name is catch_var
    catch_body: List[ASTNode]
    finally_body: List[ASTNode]
    catch_types: Optional[List[str]] = None  # optional typed catches
    def accept(self, visitor): return visitor.visit_try_stmt(self)

@dataclass
class EnumDecl(ASTNode):
    name: str
    values: List[str]
    def accept(self, visitor): return visitor.visit_enum_decl(self)

@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode]
    def accept(self, visitor): return visitor.visit_return_stmt(self)

@dataclass
class ExprStmt(ASTNode):
    expression: ASTNode
    def accept(self, visitor): return visitor.visit_expr_stmt(self)

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    def accept(self, visitor): return visitor.visit_program(self)
