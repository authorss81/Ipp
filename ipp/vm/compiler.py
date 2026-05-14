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
    __slots__ = ('chunk', 'upvalue_descs', 'name', 'variadic_param', 'is_async', 'param_names')

    def __init__(self, chunk: Chunk, upvalue_descs: List[Tuple[bool, int]],
                 name: str = '<fn>', variadic_param: str = None, is_async: bool = False,
                 param_names: list = None):
        self.chunk = chunk
        self.upvalue_descs = upvalue_descs
        self.name = name
        self.variadic_param = variadic_param
        self.is_async = is_async
        self.param_names = param_names or []

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
        slot = len(self.locals) - 1
        # Record const locals for immutability enforcement
        if is_const:
            self.chunk.const_locals.add(slot)
        return slot

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
        elif isinstance(node, MultiVarDecl):
            self.compile_multi_var_decl(node)
        elif isinstance(node, FunctionDecl):
            self.compile_function(node)
        elif isinstance(node, AsyncFuncDecl):
            self.compile_function(node, is_async=True)
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
        elif isinstance(node, AssertStmt):
            self.compile_assert(node)
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
            # FIX v1.5.23: track global const for immutability
            if is_const:
                # For global let, track as const global by name
                if not hasattr(self.chunk, 'const_globals'):
                    self.chunk.const_globals = set()
                self.chunk.const_globals.add(node.name)

    def compile_multi_var_decl(self, node: MultiVarDecl):
        """var a, b, c = [1, 2, 3] — destructure list into named vars"""
        # Compile the initializer (list) - pushes list to stack
        self.compile_expr(node.initializer)
        
        # Save the list to a temp local for indexing
        if self.depth > 0:
            temp_slot = self.define_local("__multivar_temp__")
        else:
            # For global: store in global
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            idx = len(self.chunk.constants)
            self.chunk.constants.append("__multivar_temp__")
            self.chunk.write(idx, self.current_line)
            self.chunk.lines.append(self.current_line)
            temp_slot = None

        # Now destructure each element into its variable
        for i, name in enumerate(node.names):
            # Get list[i]
            if temp_slot is not None:
                self.chunk.write(OpCode.GET_LOCAL, self.current_line)
                self.chunk.write(temp_slot, self.current_line)
            else:
                self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
                idx = len(self.chunk.constants)
                self.chunk.constants.append("__multivar_temp__")
                self.chunk.write(idx, self.current_line)
                self.chunk.lines.append(self.current_line)
            
            # Push index
            self.chunk.add_constant(i, self.current_line)
            self.chunk.write(OpCode.GET_INDEX, self.current_line)
            
            # Define variable
            if self.depth > 0:
                self.define_local(name)
            else:
                self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
                idx = len(self.chunk.constants)
                self.chunk.constants.append(name)
                self.chunk.write(idx, self.current_line)
                self.chunk.lines.append(self.current_line)

    # ─── Function compilation ─────────────────────────────────────────────────

    def compile_function(self, node: FunctionDecl, is_method: bool = False, is_async: bool = False):
        """Compile a function into a sub-Chunk, push as constant."""
        sub = Compiler(parent=self)
        sub.depth = 1

        # FIX: BUG-V8/BUG-CP5 — 'self' is slot 0 for methods
        if is_method:
            sub.define_local("self")

        variadic_param = None
        param_slots = []
        for param in node.parameters:
            if param.startswith("..."):
                variadic_param = param[3:]
                slot = sub.define_local(variadic_param)
            else:
                slot = sub.define_local(param)
            param_slots.append(slot)

        # FIX: emit default value guards at function entry
        # For each param with a default: if param_slot is nil, assign default
        defaults = getattr(node, 'defaults', None) or []
        start_idx = 1 if is_method else 0  # skip 'self' slot
        for i, default_expr in enumerate(defaults):
            if default_expr is None:
                continue
            param_idx = start_idx + i
            if param_idx >= len(param_slots):
                break
            slot = param_slots[param_idx] if not is_method else param_slots[i]
            # if slot == nil: slot = default_expr
            sub.chunk.write(OpCode.GET_LOCAL, sub.current_line)
            sub.chunk.write(slot, sub.current_line)
            sub.chunk.write(OpCode.NIL, sub.current_line)
            sub.chunk.write(OpCode.EQUAL, sub.current_line)
            skip_jump = sub.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, sub.current_line)
            sub.compile_expr(default_expr)
            sub.chunk.write(OpCode.SET_LOCAL, sub.current_line)
            sub.chunk.write(slot, sub.current_line)
            sub.chunk.write(OpCode.POP, sub.current_line)
            sub.chunk.patch_jump(skip_jump)

        for stmt in node.body:
            sub.compile_stmt(stmt)

        # auto-return nil
        last = sub.chunk.code[-1] if sub.chunk.code else None
        if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
            sub.chunk.write(OpCode.NIL, self.current_line)
            sub.chunk.write(OpCode.RETURN_VAL, self.current_line)

        func_chunk = sub.chunk
        # Store param names for named-arg dispatch at call sites
        _param_names = [p.lstrip('.') for p in node.parameters]
        if is_method and _param_names and _param_names[0] == 'self':
            _param_names = _param_names[1:]  # exclude 'self'
        proto = FunctionProto(func_chunk, sub.upvalues, name=node.name,
                              variadic_param=variadic_param, is_async=is_async,
                              param_names=_param_names)
        idx = len(self.chunk.constants)
        self.chunk.constants.append(proto)
        
        # Handle decorators - AsyncFuncDecl may not have this attribute
        decorator = getattr(node, 'decorator', None)
        if decorator:
            # First define global with original closure
            self.chunk.write(OpCode.CLOSURE, self.current_line)
            self.chunk.write(idx, self.current_line)
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            func_name_idx = len(self.chunk.constants)
            self.chunk.constants.append(node.name)
            self.chunk.write(func_name_idx, self.current_line)
            self.chunk.lines.append(self.current_line)
            # Now compile decorator call with decorated function
            self.compile_expr(node.decorator)
            # Get the global we just defined
            self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
            self.chunk.write(func_name_idx, self.current_line)
            self.chunk.lines.append(self.current_line)
            # Call: decorator(function)
            self.chunk.write(OpCode.CALL, self.current_line)
            self.chunk.write(1, self.current_line)
            # Update global with result
            self.chunk.write(OpCode.SET_GLOBAL, self.current_line)
            self.chunk.write(func_name_idx, self.current_line)
            self.chunk.lines.append(self.current_line)
        else:
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
                # FIX v1.5.25: Skip 'self' for static methods
                if not method.is_static:
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

        # slot 0: iterator list (generators are coerced to list at runtime via GET_LOCAL/len)
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
        # FIX: idx first, then len - correct order for LESS
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        
        self.compile_identifier("len")
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(list_slot, self.current_line)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)

        # LESS: idx < len(list)
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
            self.chunk.write(OpCode.POP, self.current_line)  # FIX: SET_LOCAL doesn't pop; clear TOS
        else:
            self.chunk.write(OpCode.POP, self.current_line)

        # body
        for stmt in node.body:
            self.compile_stmt(stmt)

        # FIX v1.5.27: Set continue_target BEFORE idx++ section (so compile_continue can emit LOOP)
        continue_target = len(self.chunk.code)
        self.loop_stack[-1]['continue_target'] = continue_target

        # idx += 1
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.add_constant(1, self.current_line)
        self.chunk.write(OpCode.ADD, self.current_line)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)  # FIX: SET_LOCAL peeks; pop the leaked idx+1

        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

        loop_info = self.loop_stack.pop()
        for brk in loop_info['break_jumps']:
            self.chunk.patch_jump(brk)
        # No special patch needed - compile_continue now checks continue_target before body

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
        # No patch needed for continue - compile_continue emits LOOP directly

        self.pop_scope()

    def compile_do_while(self, node: DoWhileStmt):
        self.push_scope()
        loop_start = len(self.chunk.code)

        self.loop_stack.append({
            'start': loop_start,
            'break_jumps': [],
            'continue_target': loop_start,
            'continue_jumps': [],
        })

        for stmt in node.body:
            self.compile_stmt(stmt)

        continue_target = len(self.chunk.code)
        self.loop_stack[-1]['continue_target'] = continue_target

        self.compile_expr(node.condition)
        # repeat..until exits when condition is TRUE; do..while exits when FALSE
        if getattr(node, 'is_until', False):
            exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_TRUE_POP, self.current_line)
        else:
            exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

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
        # FIX v1.5.26: emit LOOP (backward jump) directly instead of forward JUMP
        if not self.loop_stack:
            self.error("'continue' outside of loop")
        loop_info = self.loop_stack[-1]
        continue_target = loop_info.get('continue_target')
        if continue_target is not None:
            # Direct backward jump - no patching needed
            self.chunk.emit_loop(continue_target, self.current_line)
        else:
            # For-in loop - need to emit forward jump and patch later
            jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            self.loop_stack[-1]['continue_jumps'].append(jump)

    def compile_try(self, node: TryStmt):
        # Emit TRY with offset to first catch
        try_jump = self.chunk.emit_jump(OpCode.TRY, self.current_line)

        for stmt in node.try_body:
            self.compile_stmt(stmt)
        self.chunk.write(OpCode.TRY_END, self.current_line)

        # Jump past all catches if no exception
        skip_catch = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        self.chunk.patch_jump(try_jump)

        # Multiple catch blocks with optional type matching
        end_jumps = []
        for i, catch_info in enumerate(node.catches):
            catch_type = catch_info[0] if len(catch_info) > 0 else None
            catch_var = catch_info[1] if len(catch_info) > 1 else None
            catch_body = catch_info[2] if len(catch_info) > 2 else []
            self.push_scope()
            slot = None

            if catch_type:
                # FIX v1.6.1: typed catch — check if TOS (exception) matches type name
                # Stack has exception on top. Push type name, call MATCH_EXC_TYPE.
                # MATCH_EXC_TYPE: peeks exc, pops type_str, pushes bool. exc remains on stack.
                type_idx = len(self.chunk.constants)
                self.chunk.constants.append(catch_type)
                self.chunk.write(OpCode.CONSTANT, self.current_line)
                self.chunk.write(type_idx, self.current_line)
                self.chunk.lines.append(self.current_line)
                # Stack: [exc, type_str] → MATCH_EXC_TYPE → [exc, bool]
                self.chunk.write(OpCode.MATCH_EXC_TYPE, self.current_line)
                next_catch = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            else:
                next_catch = None

            if catch_var:
                slot = self.define_local(catch_var)
                self.chunk.write(OpCode.SET_LOCAL, self.current_line)
                self.chunk.write(slot, self.current_line)
                self.chunk.lines.append(self.current_line)
                # SET_LOCAL writes TOS → slot. The exception IS at slot 0 (TOS = stack[stack_base+0]).
                # Do NOT POP here — that would destroy the slot value.

            for stmt in catch_body:
                self.compile_stmt(stmt)
            # FIX: pop_scope BEFORE the end-jump so cleanup POPs actually execute
            self.pop_scope()
            # After catch body, jump past ALL remaining catches
            end_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            end_jumps.append(end_jump)

            if next_catch is not None:
                self.chunk.patch_jump(next_catch)
            self.chunk.write(OpCode.CATCH_END, self.current_line)

        # Patch all end-of-catch jumps to here
        for j in end_jumps:
            self.chunk.patch_jump(j)
        self.chunk.patch_jump(skip_catch)

        # Finally block
        if node.finally_body:
            self.chunk.write(OpCode.FINALLY, self.current_line)
            for stmt in node.finally_body:
                self.compile_stmt(stmt)
            self.chunk.write(OpCode.END_FINALLY, self.current_line)

    def compile_throw(self, node: ThrowStmt):
        self.compile_expr(node.expression)
        self.chunk.write(OpCode.THROW, self.current_line)

    def compile_assert(self, node: AssertStmt):
        self.compile_expr(node.condition)
        if node.message:
            self.compile_expr(node.message)
        self.chunk.write(OpCode.ASSERT, self.current_line)

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
        elif isinstance(node, FStringExpr):
            for seg in node.segments:
                self.compile_expr(seg)
                self.compile_identifier("str")
                self.chunk.write(OpCode.SWAP, self.current_line)
                self.chunk.write(OpCode.CALL, self.current_line)
                self.chunk.write(1, self.current_line)
            self.chunk.write(OpCode.CONCAT_COUNT, self.current_line)
            self.chunk.write(len(node.segments), self.current_line)
        elif isinstance(node, BooleanLiteral):
            self.chunk.write(OpCode.TRUE if node.value else OpCode.FALSE, self.current_line)
        elif isinstance(node, NilLiteral):
            self.chunk.write(OpCode.NIL, self.current_line)
        elif isinstance(node, YieldExpr):
            # Compile the yielded value, then emit YIELD
            if node.value is not None:
                self.compile_expr(node.value)
            else:
                self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.YIELD, self.current_line)
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
        elif node.operator == "in":
            # FIX: 'x in collection' → CONTAINS opcode
            self.chunk.write(OpCode.CONTAINS, self.current_line)
        elif node.operator == "not in":
            # FIX: 'x not in collection' → CONTAINS then NOT
            self.chunk.write(OpCode.CONTAINS, self.current_line)
            self.chunk.write(OpCode.NOT, self.current_line)
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
        # FIX: push named args as sentinel+pairs so VM can split correctly
        # Format: [pos0..posN, "\x00KWARGS\x00", name0, val0, name1, val1, ...]
        if hasattr(node, 'named_arguments') and node.named_arguments:
            # Push sentinel to mark start of named args
            sentinel_idx = len(self.chunk.constants)
            self.chunk.constants.append("\x00KWARGS\x00")
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write(sentinel_idx, self.current_line)
            self.chunk.lines.append(self.current_line)
            total_args += 1
            for named in node.named_arguments:
                # Push name as constant
                self.chunk.write(OpCode.CONSTANT, self.current_line)
                name_idx = len(self.chunk.constants)
                self.chunk.constants.append(named.name)
                self.chunk.write(name_idx, self.current_line)
                self.chunk.lines.append(self.current_line)
                # Push value
                self.compile_expr(named.value)
                total_args += 2
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
        # Check for spread in elements
        has_spread = any(isinstance(e, SpreadExpr) for e in node.elements)
        
        if not has_spread:
            # Fast path: no spread, fixed count
            for elem in node.elements:
                self.compile_expr(elem)
            self.chunk.write(OpCode.LIST, self.current_line)
            self.chunk.write(len(node.elements), self.current_line)
        else:
            # Spread path: build empty list, extend/append each element
            self.chunk.write(OpCode.LIST, self.current_line)
            self.chunk.write(0, self.current_line)  # empty list on stack
            for elem in node.elements:
                if isinstance(elem, SpreadExpr):
                    self.compile_expr(elem.iterable)
                    self.chunk.write(OpCode.LIST_EXTEND, self.current_line)
                else:
                    self.compile_expr(elem)
                    self.chunk.write(OpCode.LIST_APPEND, self.current_line)

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
        # FIX: correct stack discipline for [elem for var in iter (if cond)]
        # Pre-allocate 5 locals so nested inner comps start at slot base+5
        self.push_scope()

        # slot 0: result list
        self.chunk.write(OpCode.LIST, self.current_line)
        self.chunk.write(0, self.current_line)
        res_slot = self.define_local("__lc_res")

        # slot 1: source iterable
        self.compile_expr(node.iterator)
        src_slot = self.define_local("__lc_src")

        # slot 2: index = 0
        self.chunk.add_constant(0, self.current_line)
        idx_slot = self.define_local("__lc_idx")

        # slot 3: loop variable
        self.chunk.write(OpCode.NIL, self.current_line)
        var_slot = self.define_local(node.variable)

        # slot 4: element temp — reserves stack slot so nested comps start at 5+
        self.chunk.write(OpCode.NIL, self.current_line)
        elem_slot = self.define_local("__lc_elem")

        loop_start = len(self.chunk.code)

        # while idx < len(src)
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.compile_identifier("len")
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(src_slot, self.current_line)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)
        self.chunk.write(OpCode.LESS, self.current_line)  # idx < len(src)
        exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # var = src[idx]
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(src_slot, self.current_line)
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.write(OpCode.GET_INDEX, self.current_line)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(var_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        # optional filter
        if_jump = None
        if node.condition:
            self.compile_expr(node.condition)
            if_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # compile element into elem_slot (inner comps won't collide — they start at slot 5+)
        self.compile_expr(node.element)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(elem_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        # result.append(element): GET res, GET elem, LIST_APPEND, POP list ref
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(res_slot, self.current_line)
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(elem_slot, self.current_line)
        self.chunk.write(OpCode.LIST_APPEND, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        if if_jump is not None:
            self.chunk.patch_jump(if_jump)

        # idx += 1
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.add_constant(1, self.current_line)
        self.chunk.write(OpCode.ADD, self.current_line)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

        # GET_LOCAL res (copy at top), then pop_scope emits 5 POPs:
        # POP copy_of_res, POP elem, POP var, POP idx, POP src → res remains at slot 0
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(res_slot, self.current_line)
        self.pop_scope()

    def compile_dict_comprehension(self, node: DictComprehension):
        # FIX: same stack discipline as list comprehension
        # result dict defined first (slot 0) so it survives pop_scope
        self.push_scope()

        self.chunk.write(OpCode.DICT, self.current_line)
        self.chunk.write(0, self.current_line)
        result_slot = self.define_local("__dc_res")

        self.compile_expr(node.iterator)
        src_slot = self.define_local("__dc_src")

        self.chunk.add_constant(0, self.current_line)
        idx_slot = self.define_local("__dc_idx")

        self.chunk.write(OpCode.NIL, self.current_line)
        var_slot = self.define_local(node.variable)

        loop_start = len(self.chunk.code)

        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.compile_identifier("len")
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(src_slot, self.current_line)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)
        self.chunk.write(OpCode.LESS, self.current_line)
        exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # var = src[idx]
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(src_slot, self.current_line)
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.write(OpCode.GET_INDEX, self.current_line)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(var_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        if_jump = None
        if hasattr(node, 'condition') and node.condition:
            self.compile_expr(node.condition)
            if_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # result[key] = value  via GET_LOCAL result, compile key, compile val, SET_INDEX
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(result_slot, self.current_line)
        self.compile_expr(node.key)
        self.compile_expr(node.value)
        self.chunk.write(OpCode.SET_INDEX, self.current_line)
        # SET_INDEX pops all 3 (obj,key,val) and pushes nothing — no POP needed

        if if_jump is not None:
            self.chunk.patch_jump(if_jump)

        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.add_constant(1, self.current_line)
        self.chunk.write(OpCode.ADD, self.current_line)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(result_slot, self.current_line)
        self.pop_scope()


def compile_ast(node: Program) -> Chunk:
    compiler = Compiler()
    return compiler.compile(node)
