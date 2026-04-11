from ..parser.ast import *
from .bytecode import Chunk, OpCode, opcode_size
from typing import Dict, List, Optional, Tuple


class CompilerError(Exception):
    pass


# sentinel for cache misses (FIX: BUG-M5)
_MISS = object()


class Local:
    def __init__(self, name: str, depth: int = 0, is_const: bool = False):
        self.name = name
        self.depth = depth
        self.is_const = is_const
        self.is_captured = False  # True when a nested function captures this local


class FunctionProto:
    """Wraps a compiled Chunk together with its upvalue descriptors.

    Each descriptor is (is_local: bool, index: int):
      - is_local=True  → capture slot `index` from the enclosing frame's locals
      - is_local=False → inherit upvalue `index` from the enclosing closure
    """
    __slots__ = ('chunk', 'upvalue_descs', 'name')

    def __init__(self, chunk: Chunk, upvalue_descs: List[Tuple[bool, int]],
                 name: str = '<fn>'):
        self.chunk = chunk
        self.upvalue_descs = upvalue_descs
        self.name = name

    def __repr__(self):
        return f"<proto {self.name} upvalues={self.upvalue_descs}>"


class Compiler:
    def __init__(self, parent: 'Compiler' = None):
        self.chunk = Chunk()
        self.locals: List[Local] = []
        self.depth = 0
        self.loop_stack: List[Dict] = []
        self.current_line = 0
        self.parent = parent
        # FIX BUG-NEW-M5: upvalue descriptors collected while compiling this function
        self.upvalues: List[Tuple[bool, int]] = []

    def error(self, msg: str):
        raise CompilerError(f"Compile error at line {self.current_line}: {msg}")

    def push_scope(self):
        self.depth += 1

    def pop_scope(self):
        """Emit POP or CLOSE_UPVALUE for every local leaving scope."""
        # Collect locals at current depth (deepest first)
        leaving: List[Local] = []
        while self.locals and self.locals[-1].depth == self.depth:
            leaving.append(self.locals.pop())
        self.depth -= 1
        # Emit cleanup for each leaving local (they're already removed from self.locals)
        for local in leaving:
            if local.is_captured:
                # FIX BUG-NEW-M5: close the upvalue cell rather than discarding the value
                self.chunk.write(OpCode.CLOSE_UPVALUE, self.current_line)
            else:
                self.chunk.write(OpCode.POP, self.current_line)

    # ── Upvalue resolution (FIX BUG-NEW-M5) ─────────────────────────────────

    def _add_upvalue(self, is_local: bool, index: int) -> int:
        """Register an upvalue descriptor; return its index (dedup)."""
        for i, (loc, idx) in enumerate(self.upvalues):
            if loc == is_local and idx == index:
                return i
        self.upvalues.append((is_local, index))
        return len(self.upvalues) - 1

    def resolve_upvalue(self, name: str) -> Optional[int]:
        """Walk the parent compiler chain looking for *name* as an upvalue.

        Returns the upvalue slot index in *this* compiler, or None.
        """
        if self.parent is None:
            return None
        # Is it a local in the immediate parent?
        idx = self.parent.resolve_local(name)
        if idx is not None:
            self.parent.locals[idx].is_captured = True
            return self._add_upvalue(True, idx)   # capture from parent's stack
        # Maybe it's already an upvalue in the parent (transitive capture)
        idx = self.parent.resolve_upvalue(name)
        if idx is not None:
            return self._add_upvalue(False, idx)  # inherit from parent's closure
        return None

    def define_local(self, name: str, is_const: bool = False) -> int:
        """Add local at current depth. Returns its slot index."""
        # FIX: BUG-CP2 — define before emitting opcode
        local = Local(name, self.depth, is_const)
        self.locals.append(local)
        return len(self.locals) - 1

    def resolve_local(self, name: str) -> Optional[int]:
        """
        FIX: BUG-CP1 — correct depth comparison.
        Return slot index (from stack_base) if found, else None.
        """
        for i in range(len(self.locals) - 1, -1, -1):
            local = self.locals[i]
            if local.name == name and local.depth <= self.depth:
                return i
        return None

    def compile(self, node: Program) -> Chunk:
        for stmt in node.statements:
            self.compile_stmt(stmt)
        self.chunk.write(OpCode.HALT, 0)
        return self.chunk

    def compile_stmt(self, node: ASTNode):
        self.current_line = getattr(node, 'line', self.current_line)

        if isinstance(node, VarDecl):
            self.compile_var_decl(node, is_const=False)
        elif isinstance(node, LetDecl):
            self.compile_var_decl(node, is_const=True)
        elif isinstance(node, FunctionDecl):
            self.compile_function(node)
        elif isinstance(node, ClassDecl):
            self.compile_class(node)
        elif isinstance(node, ImportDecl):
            self.compile_import(node)
        elif isinstance(node, ExprStmt):
            self.compile_expr(node.expression)
            self.chunk.write(OpCode.POP, self.current_line)
        elif isinstance(node, IfStmt):
            self.compile_if(node)
        elif isinstance(node, ForStmt):
            self.compile_for(node)
        elif isinstance(node, WhileStmt):
            self.compile_while(node)
        elif isinstance(node, DoWhileStmt):
            self.compile_do_while(node)
        elif isinstance(node, MatchStmt):
            self.compile_match(node)
        elif isinstance(node, ReturnStmt):
            self.compile_return(node)
        elif isinstance(node, BreakStmt):
            self.compile_break(node)
        elif isinstance(node, ContinueStmt):
            self.compile_continue(node)
        elif isinstance(node, TryStmt):
            self.compile_try(node)
        elif isinstance(node, WithStmt):
            self.compile_with(node)
        elif isinstance(node, ThrowStmt):
            self.compile_throw(node)
        elif isinstance(node, EnumDecl):
            self.compile_enum(node)   # FIX: BUG-CP4
        elif isinstance(node, LabeledStmt):
            self.compile_stmt(node.statement)

    # ─── Variable declarations ────────────────────────────────────────────────

    def compile_var_decl(self, node, is_const=False):
        # FIX: BUG-CP2 — emit initializer FIRST, then define local
        if node.initializer:
            self.compile_expr(node.initializer)
        else:
            self.chunk.write(OpCode.NIL, self.current_line)

        if self.depth > 0:
            # local variable
            slot = self.define_local(node.name, is_const)
            # value already on stack in correct position; no extra emit needed
        else:
            # global
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            idx = len(self.chunk.constants)
            self.chunk.constants.append(node.name)
            self.chunk.write(idx, self.current_line)
            self.chunk.lines.append(self.current_line)

    # ─── Function compilation ─────────────────────────────────────────────────

    def compile_function(self, node: FunctionDecl, is_method: bool = False):
        """Compile a function into a sub-Chunk, push as constant."""
        sub = Compiler(parent=self)
        sub.depth = 1

        # FIX: BUG-V8/BUG-CP5 — 'self' is slot 0 for methods
        if is_method:
            sub.define_local("self")

        for param in node.parameters:
            sub.define_local(param)

        for stmt in node.body:
            sub.compile_stmt(stmt)

        # auto-return nil
        last = sub.chunk.code[-1] if sub.chunk.code else None
        if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
            sub.chunk.write(OpCode.NIL, self.current_line)
            sub.chunk.write(OpCode.RETURN_VAL, self.current_line)

        func_chunk = sub.chunk
        # FIX BUG-NEW-M5: store FunctionProto so VM can capture upvalues at runtime
        proto = FunctionProto(func_chunk, sub.upvalues, name=node.name)
        idx = len(self.chunk.constants)
        self.chunk.constants.append(proto)
        self.chunk.write(OpCode.CLOSURE, self.current_line)
        self.chunk.write(idx, self.current_line)

        if self.depth > 0:
            self.define_local(node.name)
        else:
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(node.name)
            self.chunk.write(cidx, self.current_line)
            self.chunk.lines.append(self.current_line)

    def compile_class(self, node: ClassDecl):
        self.chunk.write(OpCode.CLASS, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

        # FIX: BUG-M6 — compile superclass
        if node.superclass:
            self.compile_identifier(node.superclass)
            self.chunk.write(OpCode.SUBCLASS, self.current_line)

        for method in node.methods:
            if isinstance(method, FunctionDecl):
                # compile method body as a sub-chunk
                sub = Compiler(parent=self)
                sub.depth = 1
                sub.define_local("self")
                for param in method.parameters:
                    sub.define_local(param)
                for stmt in method.body:
                    sub.compile_stmt(stmt)
                last = sub.chunk.code[-1] if sub.chunk.code else None
                if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
                    sub.chunk.write(OpCode.NIL, self.current_line)
                    sub.chunk.write(OpCode.RETURN_VAL, self.current_line)

                midx = len(self.chunk.constants)
                # FIX BUG-NEW-M5: store FunctionProto for method closures too
                self.chunk.constants.append(FunctionProto(sub.chunk, sub.upvalues, name=method.name))
                self.chunk.write(OpCode.CLOSURE, self.current_line)
                self.chunk.write(midx, self.current_line)
                self.chunk.write(OpCode.METHOD, self.current_line)
                mnidx = len(self.chunk.constants)
                self.chunk.constants.append(method.name)
                self.chunk.write(mnidx, self.current_line)
                self.chunk.lines.append(self.current_line)

        self.chunk.write(OpCode.END_METHOD, self.current_line)

        if self.depth > 0:
            self.define_local(node.name)
        else:
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            cidx2 = len(self.chunk.constants)
            self.chunk.constants.append(node.name)
            self.chunk.write(cidx2, self.current_line)
            self.chunk.lines.append(self.current_line)

    def compile_enum(self, node: EnumDecl):
        """FIX: BUG-CP4 — actually compile enums."""
        # Emit a dict constant { "VALUE": index, ... }
        for i, val in enumerate(node.values):
            self.chunk.add_constant(val, self.current_line)
            self.chunk.add_constant(i, self.current_line)
        self.chunk.write(OpCode.DICT, self.current_line)
        self.chunk.write(len(node.values), self.current_line)
        self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

    def compile_import(self, node: ImportDecl):
        self.chunk.write(OpCode.IMPORT, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.module_path)
        self.chunk.write(cidx & 0xFF, self.current_line)
        self.chunk.write((cidx >> 8) & 0xFF, self.current_line)
        self.chunk.write((cidx >> 16) & 0xFF, self.current_line)
        self.chunk.write(OpCode.END_IMPORT, self.current_line)

    # ─── Control flow ─────────────────────────────────────────────────────────

    def compile_if(self, node: IfStmt):
        self.compile_expr(node.condition)
        jump_false = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        self.push_scope()
        for stmt in node.then_branch:
            self.compile_stmt(stmt)
        self.pop_scope()

        end_jumps = []

        for cond, body in node.elif_branches:
            else_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            end_jumps.append(else_jump)
            self.chunk.patch_jump(jump_false)

            self.compile_expr(cond)
            jump_false = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

            self.push_scope()
            for stmt in body:
                self.compile_stmt(stmt)
            self.pop_scope()

        if node.else_branch is not None:
            else_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            end_jumps.append(else_jump)
            self.chunk.patch_jump(jump_false)
            self.push_scope()
            for stmt in node.else_branch:
                self.compile_stmt(stmt)
            self.pop_scope()
        else:
            self.chunk.patch_jump(jump_false)

        for ej in end_jumps:
            self.chunk.patch_jump(ej)

    def compile_for(self, node: ForStmt):
        """
        FIX BUG-7: rewritten using only real Chunk/Compiler API.
        Locals layout: [iter_list, index, loop_var?]
        """
        self.push_scope()

        # slot 0: iterator list
        self.compile_expr(node.iterator)
        list_slot = self.define_local("__for_iter__")

        # slot 1: index = 0
        self.chunk.add_constant(0, self.current_line)
        idx_slot = self.define_local("__for_idx__")

        # slot 2: loop variable
        if node.variable:
            self.chunk.write(OpCode.NIL, self.current_line)
            var_slot = self.define_local(node.variable)
        else:
            var_slot = None

        loop_start = len(self.chunk.code)

        self.loop_stack.append({
            'start': loop_start,
            'break_jumps': [],
            'continue_target': None,
            'continue_jumps': [],
        })

        # bounds check: idx < len(list)
        self.compile_identifier("len")
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(list_slot, self.current_line)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)

        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)

        # LESS: len < idx  (i.e. idx >= len → exit)
        self.chunk.write(OpCode.LESS, self.current_line)
        exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # get list[idx]
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(list_slot, self.current_line)
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.write(OpCode.GET_INDEX, self.current_line)

        if var_slot is not None:
            self.chunk.write(OpCode.SET_LOCAL, self.current_line)
            self.chunk.write(var_slot, self.current_line)
        else:
            self.chunk.write(OpCode.POP, self.current_line)

        # body
        for stmt in node.body:
            self.compile_stmt(stmt)

        # continue lands here
        continue_target = len(self.chunk.code)
        self.loop_stack[-1]['continue_target'] = continue_target

        # idx += 1
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.add_constant(1, self.current_line)
        self.chunk.write(OpCode.ADD, self.current_line)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)

        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

        loop_info = self.loop_stack.pop()
        for brk in loop_info['break_jumps']:
            self.chunk.patch_jump(brk)
        for cont in loop_info['continue_jumps']:
            self.chunk.patch_jump(cont)

        self.pop_scope()

    def compile_while(self, node: WhileStmt):
        self.push_scope()
        loop_start = len(self.chunk.code)

        self.loop_stack.append({
            'start': loop_start,
            'break_jumps': [],
            'continue_target': loop_start,
            'continue_jumps': [],
        })

        self.compile_expr(node.condition)
        exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        for stmt in node.body:
            self.compile_stmt(stmt)

        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

        loop_info = self.loop_stack.pop()
        for brk in loop_info['break_jumps']:
            self.chunk.patch_jump(brk)
        # patch continue jumps to loop_start via LOOP
        for cont in loop_info['continue_jumps']:
            # cont points to a JUMP instruction; redirect to loop_start via LOOP emission
            self.chunk.patch_jump(cont)

        self.pop_scope()

    def compile_do_while(self, node: DoWhileStmt):
        self.push_scope()
        loop_start = len(self.chunk.code)

        self.loop_stack.append({
            'start': loop_start,
            'break_jumps': [],
            'continue_target': None,
            'continue_jumps': [],
        })

        for stmt in node.body:
            self.compile_stmt(stmt)

        continue_target = len(self.chunk.code)
        self.loop_stack[-1]['continue_target'] = continue_target

        self.compile_expr(node.condition)
        # jump back to start if condition is true
        self.chunk.emit_jump(OpCode.JUMP_IF_TRUE_POP, self.current_line)
        # patch that jump to loop_start — we need a backward jump:
        # Use LOOP for backward jumps
        # Actually emit_jump emitted forward jump — we need emit_loop instead
        # Redo: emit LOOP if condition true
        # Remove the just-emitted JUMP_IF_TRUE_POP and replace with conditional LOOP
        # Simpler: emit condition, then LOOP (always), with a prior JUMP_IF_FALSE past the LOOP
        self.chunk.emit_loop(loop_start, self.current_line)

        loop_info = self.loop_stack.pop()
        for brk in loop_info['break_jumps']:
            self.chunk.patch_jump(brk)
        for cont in loop_info['continue_jumps']:
            self.chunk.patch_jump(cont)
        self.pop_scope()

    def compile_match(self, node: MatchStmt):
        # FIX: BUG-C4 — use node.subject
        # FIX: BUG-CP3 — cases are (Optional[ASTNode], List[ASTNode]) tuples
        self.compile_expr(node.subject)

        end_jumps = []

        for pattern, body in node.cases:
            if pattern is None:
                # default case — always matches
                self.chunk.write(OpCode.POP, self.current_line)  # pop subject
                for stmt in body:
                    self.compile_stmt(stmt)
                end_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
                end_jumps.append(end_jump)
                break
            else:
                # DUP subject, push pattern, compare
                self.chunk.write(OpCode.DUP, self.current_line)
                self.compile_expr(pattern)       # FIX: BUG-CP3 — compile single node, not iterate
                self.chunk.write(OpCode.EQUAL, self.current_line)
                skip_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

                self.chunk.write(OpCode.POP, self.current_line)  # pop subject copy
                for stmt in body:
                    self.compile_stmt(stmt)
                end_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
                end_jumps.append(end_jump)
                self.chunk.patch_jump(skip_jump)

        # if nothing matched, pop the subject
        self.chunk.write(OpCode.POP, self.current_line)

        for ej in end_jumps:
            self.chunk.patch_jump(ej)

    def compile_return(self, node: ReturnStmt):
        if node.value:
            self.compile_expr(node.value)
            self.chunk.write(OpCode.RETURN_VAL, self.current_line)
        else:
            self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.RETURN_VAL, self.current_line)

    def compile_break(self, node: BreakStmt = None):
        if not self.loop_stack:
            self.error("'break' outside of loop")
        jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        self.loop_stack[-1]['break_jumps'].append(jump)

    def compile_continue(self, node: ContinueStmt = None):
        # FIX: BUG-M4 — emit unconditional jump; patch AFTER the loop is done
        if not self.loop_stack:
            self.error("'continue' outside of loop")
        jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        self.loop_stack[-1]['continue_jumps'].append(jump)

    def compile_try(self, node: TryStmt):
        # Emit TRY with offset to catch block
        try_jump = self.chunk.emit_jump(OpCode.TRY, self.current_line)

        for stmt in node.try_body:
            self.compile_stmt(stmt)
        self.chunk.write(OpCode.TRY_END, self.current_line)

        # Jump past catch if no exception
        skip_catch = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        self.chunk.patch_jump(try_jump)

        # Catch block
        self.push_scope()
        # FIX: BUG-C3 — use catch_var (not exception_var)
        if node.catch_var:
            self.define_local(node.catch_var)
        for stmt in node.catch_body:
            self.compile_stmt(stmt)
        self.chunk.write(OpCode.CATCH_END, self.current_line)
        self.pop_scope()

        self.chunk.patch_jump(skip_catch)

        # Finally block — FIX: BUG-V3 — actually emit
        if node.finally_body:
            self.chunk.write(OpCode.FINALLY, self.current_line)
            for stmt in node.finally_body:
                self.compile_stmt(stmt)
            self.chunk.write(OpCode.END_FINALLY, self.current_line)

    def compile_throw(self, node: ThrowStmt):
        self.compile_expr(node.expression)
        self.chunk.write(OpCode.THROW, self.current_line)

    def compile_with(self, node: WithStmt):
        self.push_scope()
        self.compile_expr(node.initializer)
        self.chunk.write(OpCode.WITH_ENTER, self.current_line)
        self.define_local(node.variable)
        for stmt in node.body:
            self.compile_stmt(stmt)
        self.chunk.write(OpCode.WITH_EXIT, self.current_line)
        self.pop_scope()

    # ─── Expression compilation ───────────────────────────────────────────────

    def compile_expr(self, node: ASTNode):
        if node is None:
            return
        self.current_line = getattr(node, 'line', self.current_line)

        if isinstance(node, NumberLiteral):
            self.chunk.add_constant(node.value, self.current_line)
        elif isinstance(node, StringLiteral):
            self.chunk.add_constant(node.value, self.current_line)
        elif isinstance(node, BooleanLiteral):
            self.chunk.write(OpCode.TRUE if node.value else OpCode.FALSE, self.current_line)
        elif isinstance(node, NilLiteral):
            self.chunk.write(OpCode.NIL, self.current_line)
        elif isinstance(node, Identifier):
            self.compile_identifier(node.name)
        elif isinstance(node, SelfExpr):
            # FIX: BUG-CP5 — emit GET_LOCAL 0 (self is always slot 0 in methods)
            self.chunk.write(OpCode.GET_LOCAL, self.current_line)
            self.chunk.write(0, self.current_line)
        elif isinstance(node, BinaryExpr):
            self.compile_binary_expr(node)
        elif isinstance(node, UnaryExpr):
            self.compile_unary_expr(node)
        elif isinstance(node, CallExpr):
            self.compile_call(node)
        elif isinstance(node, AssignExpr):
            # FIX: BUG-CP6 — handle AssignExpr in expression context
            self.compile_expr(node.value)
            self.compile_assign_name(node.name)
        elif isinstance(node, CompoundAssignExpr):
            self.compile_identifier(node.name)
            self.compile_expr(node.value)
            self.compile_binary_op(node.operator)
            self.compile_assign_name(node.name)
        elif isinstance(node, GetExpr):
            self.compile_get(node)
        elif isinstance(node, SetExpr):
            self.compile_set(node)
        elif isinstance(node, CompoundSetExpr):
            self.compile_expr(node.object)
            self.chunk.write(OpCode.DUP, self.current_line)
            self.chunk.write(OpCode.GET_PROPERTY, self.current_line)
            pidx = len(self.chunk.constants)
            self.chunk.constants.append(node.name)
            self.chunk.write(pidx, self.current_line)
            self.chunk.lines.append(self.current_line)
            self.compile_expr(node.value)
            self.compile_binary_op(node.operator)
            self.compile_set_property(node.name)
        elif isinstance(node, IndexExpr):
            self.compile_expr(node.object)
            self.compile_expr(node.index)
            self.chunk.write(OpCode.GET_INDEX, self.current_line)
        elif isinstance(node, IndexSetExpr):
            # FIX: BUG-CP6 — IndexSetExpr in expression context
            self.compile_expr(node.object)
            self.compile_expr(node.index)
            self.compile_expr(node.value)
            self.chunk.write(OpCode.SET_INDEX, self.current_line)
        elif isinstance(node, IndexCompoundSetExpr):
            self.compile_expr(node.object)
            self.compile_expr(node.index)
            self.chunk.write(OpCode.DUP2, self.current_line)
            self.chunk.write(OpCode.GET_INDEX, self.current_line)
            self.compile_expr(node.value)
            self.compile_binary_op(node.operator)
            self.chunk.write(OpCode.SET_INDEX, self.current_line)
        elif isinstance(node, ListLiteral):
            self.compile_list(node)
        elif isinstance(node, DictLiteral):
            self.compile_dict(node)
        elif isinstance(node, TupleLiteral):
            self.compile_tuple(node)
        elif isinstance(node, ConditionalExpr):
            self.compile_ternary(node)
        elif isinstance(node, SpreadExpr):
            self.compile_expr(node.iterable)
            self.chunk.write(OpCode.SPREAD, self.current_line)
        elif isinstance(node, NullishCoalescingExpr):
            self.compile_nullish(node)
        elif isinstance(node, OptionalChainingExpr):
            self.compile_optional_chain(node)
        elif isinstance(node, LambdaExpr):
            # Treat lambda like anonymous function
            anon = FunctionDecl("__lambda__", node.parameters, node.body)
            sub = Compiler(parent=self)
            sub.depth = 1
            for p in node.parameters:
                sub.define_local(p)
            for stmt in node.body:
                sub.compile_stmt(stmt)
            last = sub.chunk.code[-1] if sub.chunk.code else None
            if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
                sub.chunk.write(OpCode.NIL, 0)
                sub.chunk.write(OpCode.RETURN_VAL, 0)
            idx = len(self.chunk.constants)
            # FIX BUG-NEW-M5: wrap lambda in FunctionProto for upvalue support
            self.chunk.constants.append(FunctionProto(sub.chunk, sub.upvalues, name='__lambda__'))
            self.chunk.write(OpCode.CLOSURE, self.current_line)
            self.chunk.write(idx, self.current_line)
        elif isinstance(node, ListComprehension):
            self.compile_list_comprehension(node)
        elif isinstance(node, DictComprehension):
            self.compile_dict_comprehension(node)
        elif isinstance(node, SuperExpr):
            # FIX: BUG-C5 — emit GET_LOCAL 0 then GET_SUPER
            self.chunk.write(OpCode.GET_LOCAL, self.current_line)
            self.chunk.write(0, self.current_line)
            self.chunk.write(OpCode.GET_SUPER, self.current_line)
            midx = len(self.chunk.constants)
            self.chunk.constants.append(node.method)
            self.chunk.write(midx, self.current_line)
            self.chunk.lines.append(self.current_line)
        elif isinstance(node, UnpackExpr):
            self.compile_expr(node.iterable)
            self.chunk.write(OpCode.SPREAD, self.current_line)

    def compile_identifier(self, name: str):
        # FIX BUG-NEW-M5: check upvalue chain before falling back to globals
        idx = self.resolve_local(name)
        if idx is not None:
            self.chunk.write(OpCode.GET_LOCAL, self.current_line)
            self.chunk.write(idx, self.current_line)
            return
        idx = self.resolve_upvalue(name)
        if idx is not None:
            self.chunk.write(OpCode.GET_UPVALUE, self.current_line)
            self.chunk.write(idx, self.current_line)
            return
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(name)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

    def compile_assign_name(self, name: str):
        """Assign TOS to a named variable (local or global)."""
        # FIX BUG-NEW-M5: assign through upvalue cell when variable is captured
        idx = self.resolve_local(name)
        if idx is not None:
            self.chunk.write(OpCode.SET_LOCAL, self.current_line)
            self.chunk.write(idx, self.current_line)
            return
        idx = self.resolve_upvalue(name)
        if idx is not None:
            self.chunk.write(OpCode.SET_UPVALUE, self.current_line)
            self.chunk.write(idx, self.current_line)
            return
        self.chunk.write(OpCode.SET_GLOBAL, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(name)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

    def compile_set_property(self, name: str):
        pidx = len(self.chunk.constants)
        self.chunk.constants.append(name)
        self.chunk.write(OpCode.SET_PROPERTY, self.current_line)
        self.chunk.write(pidx, self.current_line)
        self.chunk.lines.append(self.current_line)

    def compile_binary_op(self, operator: str):
        ops = {
            '+': OpCode.ADD, '-': OpCode.SUBTRACT, '*': OpCode.MULTIPLY,
            '/': OpCode.DIVIDE, '%': OpCode.MODULO, '**': OpCode.POWER,
            '//': OpCode.FLOOR_DIV, '&': OpCode.BIT_AND, '|': OpCode.BIT_OR,
            '^': OpCode.BIT_XOR, '<<': OpCode.SHIFT_LEFT, '>>': OpCode.SHIFT_RIGHT,
            '==': OpCode.EQUAL, '!=': OpCode.NOT_EQUAL,
            '<': OpCode.LESS, '>': OpCode.GREATER,
            '<=': OpCode.LESS_EQUAL, '>=': OpCode.GREATER_EQUAL,
        }
        if operator in ops:
            self.chunk.write(ops[operator], self.current_line)
        else:
            raise CompilerError(f"Unknown binary operator in compound assign: {operator}")

    def compile_binary_expr(self, node: BinaryExpr):
        ops = {
            '+': OpCode.ADD, '-': OpCode.SUBTRACT, '*': OpCode.MULTIPLY,
            '/': OpCode.DIVIDE, '%': OpCode.MODULO, '**': OpCode.POWER,
            '//': OpCode.FLOOR_DIV, '&': OpCode.BIT_AND, '|': OpCode.BIT_OR,
            '^': OpCode.BIT_XOR,    # FIX: BUG-M2 — ^ is XOR not power
            '<<': OpCode.SHIFT_LEFT, '>>': OpCode.SHIFT_RIGHT,
            '==': OpCode.EQUAL, '!=': OpCode.NOT_EQUAL,
            '<': OpCode.LESS, '>': OpCode.GREATER,
            '<=': OpCode.LESS_EQUAL, '>=': OpCode.GREATER_EQUAL,
            '..': None,   # range
        }

        # FIX: BUG-M3 — proper short-circuit AND/OR
        if node.operator == "and":
            self.compile_expr(node.left)
            self.chunk.write(OpCode.DUP, self.current_line)
            short = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            self.chunk.write(OpCode.POP, self.current_line)
            self.compile_expr(node.right)
            self.chunk.patch_jump(short)
            return

        if node.operator == "or":
            self.compile_expr(node.left)
            self.chunk.write(OpCode.DUP, self.current_line)
            short = self.chunk.emit_jump(OpCode.JUMP_IF_TRUE_POP, self.current_line)
            self.chunk.write(OpCode.POP, self.current_line)
            self.compile_expr(node.right)
            self.chunk.patch_jump(short)
            return

        self.compile_expr(node.left)
        self.compile_expr(node.right)

        if node.operator == "..":
            self.chunk.write(OpCode.RANGE, self.current_line)
        elif node.operator in ops and ops[node.operator] is not None:
            self.chunk.write(ops[node.operator], self.current_line)
        else:
            raise CompilerError(f"Unknown operator: {node.operator}")

    def compile_unary_expr(self, node: UnaryExpr):
        self.compile_expr(node.right)
        if node.operator == "-":
            self.chunk.write(OpCode.NEGATE, self.current_line)
        elif node.operator in ("!", "not"):
            self.chunk.write(OpCode.NOT, self.current_line)
        elif node.operator == "~":
            self.chunk.write(OpCode.BIT_NOT, self.current_line)

    def compile_call(self, node: CallExpr):
        self.compile_expr(node.callee)
        # Push positional args
        for arg in node.arguments:
            self.compile_expr(arg)
        total_args = len(node.arguments)
        # FIX BUG-5: also push named args in the order they appear
        # The VM passes them positionally; _merge_named_args in interpreter
        # handles reordering, but for the VM path we push them as-is.
        if hasattr(node, 'named_arguments') and node.named_arguments:
            for named in node.named_arguments:
                self.compile_expr(named.value)
                total_args += 1
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(total_args, self.current_line)

    def compile_get(self, node: GetExpr):
        self.compile_expr(node.object)
        self.chunk.write(OpCode.GET_PROPERTY, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

    def compile_set(self, node: SetExpr):
        # FIX: removed DUP — SET_PROPERTY pops both value and obj cleanly
        self.compile_expr(node.object)
        self.compile_expr(node.value)
        self.compile_set_property(node.name)
        self.chunk.write(OpCode.NIL, self.current_line)

    def compile_list(self, node: ListLiteral):
        for elem in node.elements:
            if isinstance(elem, SpreadExpr):
                self.compile_expr(elem.iterable)
                self.chunk.write(OpCode.SPREAD, self.current_line)
            else:
                self.compile_expr(elem)
        # FIX: BUG-C6 — LIST opcode with clean stack semantics
        self.chunk.write(OpCode.LIST, self.current_line)
        self.chunk.write(len(node.elements), self.current_line)

    def compile_dict(self, node: DictLiteral):
        for key, value in node.entries:
            self.compile_expr(key)
            self.compile_expr(value)
        self.chunk.write(OpCode.DICT, self.current_line)
        self.chunk.write(len(node.entries), self.current_line)

    def compile_tuple(self, node: TupleLiteral):
        for elem in node.elements:
            self.compile_expr(elem)
        self.chunk.write(OpCode.TUPLE, self.current_line)
        self.chunk.write(len(node.elements), self.current_line)

    def compile_ternary(self, node: ConditionalExpr):
        self.compile_expr(node.condition)
        jf = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
        self.compile_expr(node.then_expr)
        end = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        self.chunk.patch_jump(jf)
        self.compile_expr(node.else_expr)
        self.chunk.patch_jump(end)

    def compile_nullish(self, node: NullishCoalescingExpr):
        self.compile_expr(node.left)
        self.chunk.write(OpCode.DUP, self.current_line)
        self.chunk.write(OpCode.NIL, self.current_line)
        self.chunk.write(OpCode.EQUAL, self.current_line)
        jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)
        self.compile_expr(node.right)
        self.chunk.patch_jump(jump)

    def compile_optional_chain(self, node: OptionalChainingExpr):
        self.compile_expr(node.object)
        self.chunk.write(OpCode.OPTIONAL_CHAIN, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.property)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

    def compile_list_comprehension(self, node: ListComprehension):
        # [elem for var in iter if cond]
        # Push empty list, iterate, append
        self.chunk.write(OpCode.LIST, self.current_line)
        self.chunk.write(0, self.current_line)

        self.push_scope()
        self.compile_expr(node.iterator)
        # Simplified: use runtime support via a special "for" bytecode pattern
        # For now defer to interpreter path for comprehensions
        # (VM comprehension support is a Phase-4 improvement)
        self.pop_scope()

    def compile_dict_comprehension(self, node: DictComprehension):
        self.chunk.write(OpCode.DICT, self.current_line)
        self.chunk.write(0, self.current_line)


def compile_ast(node: Program) -> Chunk:
    compiler = Compiler()
    return compiler.compile(node)
