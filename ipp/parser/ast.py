from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Tuple


class ASTNode(ABC):
    line: int = 0

    @abstractmethod
    def accept(self, visitor):
        pass


# ─── Expression nodes ─────────────────────────────────────────────────────────

@dataclass
class NumberLiteral(ASTNode):
    value: float
    line: int = 0
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
class SliceExpr(ASTNode):
    start: ASTNode
    end: ASTNode
    step: Optional[ASTNode] = None
    def accept(self, visitor): return visitor.visit_slice_expr(self)

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
    spread_entries: List[ASTNode] = field(default_factory=list)
    _order: List[str] = field(default_factory=list)
    def accept(self, visitor): return visitor.visit_dict_literal(self)

    def all_entries(self):
        """Yield entries in source order: (is_spread, item).
        For regular entries: (False, (key, value)).
        For spread entries: (True, spread_expr).
        """
        ri = 0
        si = 0
        for t in self._order:
            if t == 'r':
                yield (False, self.entries[ri])
                ri += 1
            else:
                yield (True, self.spread_entries[si])
                si += 1

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    def accept(self, visitor): return visitor.visit_list_literal(self)

@dataclass
class FStringExpr(ASTNode):
    segments: List[ASTNode]
    def accept(self, visitor): return visitor.visit_fstring_expr(self)

@dataclass
class TemplateStringExpr(ASTNode):
    segments: List[ASTNode]
    def accept(self, visitor): return visitor.visit_template_string_expr(self)

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
class SetComprehension(ASTNode):
    element: ASTNode
    variable: str
    iterator: ASTNode
    condition: Optional[ASTNode] = None
    def accept(self, visitor): return visitor.visit_set_comprehension(self)

@dataclass
class IsExpr(ASTNode):
    left: ASTNode
    type_name: str
    negated: bool = False
    def accept(self, visitor): return visitor.visit_is_expr(self)

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

@dataclass
class YieldExpr(ASTNode):
    """Yield expression for generators"""
    value: Optional[ASTNode] = None
    def accept(self, visitor): return visitor.visit_yield_expr(self)

@dataclass
class AwaitExpr(ASTNode):
    """Await expression for async/await"""
    expression: ASTNode
    def accept(self, visitor): return visitor.visit_await_expr(self)

@dataclass
class AsyncFuncDecl(ASTNode):
    """Async function declaration"""
    name: str
    parameters: List[str]
    body: List[ASTNode]
    defaults: List[ASTNode] = field(default_factory=list)
    def accept(self, visitor): return visitor.visit_async_func_decl(self)


# ─── Statement nodes ──────────────────────────────────────────────────────────

@dataclass
class GameLoopStmt(ASTNode):
    """game_loop(fps=N) { body } — v2.0.0"""
    fps: ASTNode
    body: List[ASTNode]
    def accept(self, visitor): return visitor.visit_game_loop_stmt(self)

@dataclass
class SequenceStmt(ASTNode):
    """sequence name { body } — v2.0.8.3 cutscene/timeline block"""
    name: str
    body: List[ASTNode]
    def accept(self, visitor): return visitor.visit_sequence_stmt(self)

@dataclass
class StoryStmt(ASTNode):
    """story name { body } — v2.0.8.4 narrative branching block"""
    name: str
    body: List[ASTNode]
    def accept(self, visitor): return visitor.visit_story_stmt(self)

@dataclass
class NpcStmt(ASTNode):
    """npc 'Name': 'dialogue' — v2.0.8.4 NPC dialogue line"""
    speaker: ASTNode
    text: ASTNode
    def accept(self, visitor): return visitor.visit_npc_stmt(self)

@dataclass
class ChoiceOption:
    text: ASTNode
    body: List[ASTNode]
    guard: Optional[ASTNode] = None

@dataclass
class ChoiceStmt(ASTNode):
    """choice { 'opt' => { ... } ... } — v2.0.8.4 player choice"""
    options: list  # List[ChoiceOption]
    def accept(self, visitor): return visitor.visit_choice_stmt(self)

@dataclass
class FlagStmt(ASTNode):
    """flag name = value — v2.0.8.4 set a story flag"""
    name: str
    value: ASTNode
    def accept(self, visitor): return visitor.visit_flag_stmt(self)

@dataclass
class GotoStmt(ASTNode):
    """goto label_name — v2.0.8.4 jump to label"""
    label: str
    def accept(self, visitor): return visitor.visit_goto_stmt(self)

@dataclass
class SceneStmt(ASTNode):
    """scene 'name' — v2.0.8.4 scene transition"""
    name: ASTNode
    def accept(self, visitor): return visitor.visit_scene_stmt(self)

@dataclass
class LabelStmt(ASTNode):
    """label name — v2.0.8.4 define a jump target"""
    name: str
    def accept(self, visitor): return visitor.visit_label_stmt(self)

@dataclass
class ParallelBlock(ASTNode):
    """parallel { ... } inside a sequence — runs statements concurrently"""
    body: List[ASTNode]
    def accept(self, visitor): return visitor.visit_parallel_block(self)

@dataclass
class VarDecl(ASTNode):
    name: str
    initializer: Optional[ASTNode]
    type_hint: Optional[str] = None
    line: int = 0
    def accept(self, visitor): return visitor.visit_var_decl(self)

@dataclass
class MultiVarDecl(ASTNode):
    """Multiple variable declaration: var a, b = expr FIX: BUG-NEW-M7"""
    names: List[str]
    initializer: ASTNode
    def accept(self, visitor): return visitor.visit_multi_var_decl(self)

@dataclass
class ListDestructDecl(ASTNode):
    """var [a, b, ...rest] = expr — v2.0.3 List Destructuring"""
    names: List[str]
    rest_name: Optional[str]
    initializer: ASTNode
    line: int = 0
    def accept(self, visitor): return visitor.visit_list_destruct_decl(self)

@dataclass
class DictDestructKey:
    name: str
    default_value: Optional[ASTNode] = None

@dataclass
class DictDestructDecl(ASTNode):
    """var {name, age, city="Unknown"} = dict — v2.0.3.1"""
    keys: List[DictDestructKey]
    initializer: ASTNode
    line: int = 0
    def accept(self, visitor): return visitor.visit_dict_destruct_decl(self)

@dataclass
class LetDecl(ASTNode):
    name: str
    initializer: Optional[ASTNode]
    type_hint: Optional[str] = None
    def accept(self, visitor): return visitor.visit_let_decl(self)

@dataclass
class AssertStmt(ASTNode):
    condition: ASTNode
    message: Optional[ASTNode] = None
    line: int = 0
    def accept(self, visitor): return visitor.visit_assert_stmt(self)

@dataclass
class FunctionDecl(ASTNode):
    name: str
    parameters: List[str]
    body: List[ASTNode]
    param_types: Optional[List[Optional[str]]] = None   # FIX: BUG-P3
    defaults: Optional[List[Optional['ASTNode']]] = None  # Default values
    return_type: Optional[str] = None
    is_static: bool = False
    decorator: Optional['ASTNode'] = None  # v1.6.2 - decorator expression
    def accept(self, visitor): return visitor.visit_function_decl(self)

@dataclass
class ExportDecl(ASTNode):
    """export func/var/let/class — marks a declaration as public API (v1.9.12)"""
    declaration: ASTNode
    def accept(self, visitor): return visitor.visit_export_decl(self)

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
    superclass: Optional[str] = None
    properties: List['PropDecl'] = field(default_factory=list)
    invariants: List[ASTNode] = field(default_factory=list)
    exports: Dict[str, Tuple[Optional['ASTNode'], Dict[str, Any]]] = field(default_factory=dict)
    onchange_callbacks: Dict[str, str] = field(default_factory=dict)  # func_name -> field_name (v2.0.2.1)
    def accept(self, visitor): return visitor.visit_class_decl(self)

@dataclass
class PropDecl(ASTNode):
    name: str
    getter: Optional[List[ASTNode]] = None
    setter: Optional[List[ASTNode]] = None
    setter_param: Optional[str] = None
    def accept(self, visitor): return visitor.visit_prop_decl(self)

@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_branch: List[ASTNode]
    elif_branches: List[tuple]
    else_branch: Optional[List[ASTNode]]
    def accept(self, visitor): return visitor.visit_if_stmt(self)

@dataclass
class ForStmt(ASTNode):
    variables: List[str]
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
    is_until: bool = False  # True for repeat..until (exit when TRUE), False for do..while (exit when FALSE)
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

# ─── Pattern nodes (v2.0.5) ────────────────────────────────────────────────────

class Pattern:
    """Base class for match patterns (not AST nodes — no visitor pattern)"""
    pass

@dataclass
class MatchValuePat(Pattern):
    """Equality match: case 42 =>"""
    expr: ASTNode

@dataclass
class MatchTypePat(Pattern):
    """Type check, optionally bind: case Int: or case Int a =>"""
    type_name: str
    var_name: Optional[str] = None

@dataclass
class MatchBindPat(Pattern):
    """Binds matched value to a variable: case a =>"""
    name: str

@dataclass
class MatchListPat(Pattern):
    """List destructure: case [a, b, *rest] =>"""
    elements: List[Pattern]
    rest: Optional[str] = None

@dataclass
class MatchDictPat(Pattern):
    """Dict destructure: case {name, age} =>"""
    keys: List[str]

@dataclass
class MatchDefaultPat(Pattern):
    """Default case: case _ => or default =>"""
    pass

# ─── Match case (v2.0.5) ──────────────────────────────────────────────────────

@dataclass
class MatchCase:
    pattern: Pattern
    body: List[ASTNode] = field(default_factory=list)
    guard: Optional[ASTNode] = None

@dataclass
class MatchStmt(ASTNode):
    subject: ASTNode
    cases: List[MatchCase] = field(default_factory=list)
    def accept(self, visitor): return visitor.visit_match_stmt(self)

@dataclass
class MatchExpr(ASTNode):
    subject: ASTNode
    cases: List[MatchCase] = field(default_factory=list)
    def accept(self, visitor): return visitor.visit_match_expr(self)

@dataclass
class TryStmt(ASTNode):
    try_body: List[ASTNode]
    catches: List[tuple]           # List of (catch_type, catch_var, catch_body) - typed catches
    finally_body: List[ASTNode]
    def accept(self, visitor): return visitor.visit_try_stmt(self)

@dataclass
class EnumDecl(ASTNode):
    name: str
    values: Dict[str, int]
    def accept(self, visitor): return visitor.visit_enum_decl(self)

@dataclass
class GlobalDeclStmt(ASTNode):
    """global name — explicit global variable declaration (v1.9.1)"""
    names: List[str]
    def accept(self, visitor): return visitor.visit_global_decl_stmt(self)

@dataclass
class NonlocalDeclStmt(ASTNode):
    """nonlocal name — explicit closure variable declaration (v1.9.1.1)"""
    names: List[str]
    def accept(self, visitor): return visitor.visit_nonlocal_decl_stmt(self)

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
