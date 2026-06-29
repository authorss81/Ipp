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
        # v1.9.1: names declared global in this function scope
        self.global_names: set = set()
        # v1.9.1.1: names declared nonlocal in this function scope
        self.nonlocal_names: set = set()

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
        elif isinstance(node, ListDestructDecl):
            self.compile_list_destruct_decl(node)
        elif isinstance(node, DictDestructDecl):
            self.compile_dict_destruct_decl(node)
        elif isinstance(node, FunctionDecl):
            self.compile_function(node)
        elif isinstance(node, AsyncFuncDecl):
            self.compile_function(node, is_async=True)
        elif isinstance(node, ClassDecl):
            self.compile_class(node)
        elif isinstance(node, ExportDecl):
            self.compile_export(node)
        elif isinstance(node, ImportDecl):
            self.compile_import(node)
        elif isinstance(node, GameLoopStmt):
            self.compile_game_loop(node)
        elif isinstance(node, SequenceStmt):
            self.compile_sequence(node)
        elif isinstance(node, StoryStmt):
            self.compile_story(node)
        elif isinstance(node, ParallelBlock):
            self.compile_parallel_block(node)
        elif isinstance(node, NpcStmt):
            self.compile_npc(node)
        elif isinstance(node, ChoiceStmt):
            self.compile_choice(node)
        elif isinstance(node, FlagStmt):
            self.compile_flag(node)
        elif isinstance(node, GotoStmt):
            self.compile_goto(node)
        elif isinstance(node, SceneStmt):
            self.compile_scene(node)
        elif isinstance(node, LabelStmt):
            self.compile_label(node)
        elif isinstance(node, EntityDecl):
            self.compile_entity(node)
        elif isinstance(node, SystemDecl):
            self.compile_system(node)
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
        elif isinstance(node, GlobalDeclStmt):
            for name in node.names:
                self.global_names.add(name)
        elif isinstance(node, NonlocalDeclStmt):
            for name in node.names:
                self.nonlocal_names.add(name)

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

    def compile_list_destruct_decl(self, node: ListDestructDecl):
        """var [a, b, ...rest] = expr — v2.0.3"""
        self.compile_expr(node.initializer)

        # Save list to temp
        if self.depth > 0:
            temp_slot = self.define_local("__listdestruct_temp__")
        else:
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            idx = len(self.chunk.constants)
            self.chunk.constants.append("__listdestruct_temp__")
            self.chunk.write(idx, self.current_line)
            self.chunk.lines.append(self.current_line)
            temp_slot = None

        def load_temp():
            if temp_slot is not None:
                self.chunk.write(OpCode.GET_LOCAL, self.current_line)
                self.chunk.write(temp_slot, self.current_line)
            else:
                self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
                idx = len(self.chunk.constants)
                self.chunk.constants.append("__listdestruct_temp__")
                self.chunk.write(idx, self.current_line)
                self.chunk.lines.append(self.current_line)

        def define_var(name):
            if self.depth > 0:
                self.define_local(name)
            else:
                self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
                idx = len(self.chunk.constants)
                self.chunk.constants.append(name)
                self.chunk.write(idx, self.current_line)
                self.chunk.lines.append(self.current_line)

        # Positional names
        for i, name in enumerate(node.names):
            load_temp()
            self.chunk.add_constant(i, self.current_line)
            self.chunk.write(OpCode.GET_INDEX, self.current_line)
            define_var(name)

        # Rest name (slice temp[i:] where i = len(names))
        if node.rest_name:
            load_temp()
            self.chunk.add_constant(len(node.names), self.current_line)
            self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.BUILD_SLICE, self.current_line)
            self.chunk.write(OpCode.GET_INDEX, self.current_line)
            define_var(node.rest_name)

    def compile_dict_destruct_decl(self, node: DictDestructDecl):
        """var {name, age, city="Unknown"} = dict — v2.0.3.1"""
        self.compile_expr(node.initializer)

        # Save dict to temp
        if self.depth > 0:
            temp_slot = self.define_local("__dictdestruct_temp__")
        else:
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            idx = len(self.chunk.constants)
            self.chunk.constants.append("__dictdestruct_temp__")
            self.chunk.write(idx, self.current_line)
            self.chunk.lines.append(self.current_line)
            temp_slot = None

        def load_temp():
            if temp_slot is not None:
                self.chunk.write(OpCode.GET_LOCAL, self.current_line)
                self.chunk.write(temp_slot, self.current_line)
            else:
                self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
                idx = len(self.chunk.constants)
                self.chunk.constants.append("__dictdestruct_temp__")
                self.chunk.write(idx, self.current_line)
                self.chunk.lines.append(self.current_line)

        def define_var(name):
            if self.depth > 0:
                self.define_local(name)
            else:
                self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
                idx = len(self.chunk.constants)
                self.chunk.constants.append(name)
                self.chunk.write(idx, self.current_line)
                self.chunk.lines.append(self.current_line)

        for key in node.keys:
            if key.default_value is not None:
                # compile as dict.get("key", default)
                load_temp()
                self.chunk.write(OpCode.GET_PROPERTY, self.current_line)
                idx = len(self.chunk.constants)
                self.chunk.constants.append("get")
                self.chunk.write(idx, self.current_line)
                self.chunk.lines.append(self.current_line)
                # push key name
                self.chunk.write(OpCode.CONSTANT, self.current_line)
                kidx = len(self.chunk.constants)
                self.chunk.constants.append(key.name)
                self.chunk.write(kidx, self.current_line)
                self.chunk.lines.append(self.current_line)
                # compile default expression
                self.compile_expr(key.default_value)
                # call with 2 args
                self.chunk.write(OpCode.CALL, self.current_line)
                self.chunk.write(2, self.current_line)
            else:
                # compile as dict["key"]
                load_temp()
                self.chunk.write(OpCode.CONSTANT, self.current_line)
                kidx = len(self.chunk.constants)
                self.chunk.constants.append(key.name)
                self.chunk.write(kidx, self.current_line)
                self.chunk.lines.append(self.current_line)
                self.chunk.write(OpCode.GET_INDEX, self.current_line)
            define_var(key.name)

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

        # Pre-define function name in parent scope for recursion (v2.4.1)
        # Ensures recursive calls inside the function body can resolve the name
        if node.name != "__lambda__" and not is_method:
            if self.depth > 0:
                # Add to parent's locals so sub-compiler can resolve recursive calls
                self.define_local(node.name)
            else:
                # Add a placeholder global constant index
                self._predefine_func_name = node.name

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
                # Skip if already added by pre-define (v2.4.1 fix for recursion)
                if node.name == "__lambda__" or is_method or not any(l.name == node.name for l in self.locals):
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
                variadic_param = None
                _param_names = []
                for param in method.parameters:
                    if param.startswith("..."):
                        variadic_param = param[3:]
                        sub.define_local(variadic_param)
                    else:
                        sub.define_local(param)
                # Build param_names (excluding 'self') for named-arg dispatch
                _param_names = [p.lstrip('.') for p in method.parameters if not p.startswith("...")]
                if not method.is_static and _param_names and _param_names[0] == 'self':
                    _param_names = _param_names[1:]
                for stmt in method.body:
                    sub.compile_stmt(stmt)
                last = sub.chunk.code[-1] if sub.chunk.code else None
                if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
                    sub.chunk.write(OpCode.NIL, self.current_line)
                    sub.chunk.write(OpCode.RETURN_VAL, self.current_line)

                midx = len(self.chunk.constants)
                # FIX BUG-NEW-M5: store FunctionProto for method closures too
                self.chunk.constants.append(FunctionProto(sub.chunk, sub.upvalues, name=method.name, variadic_param=variadic_param, param_names=_param_names))
                self.chunk.write(OpCode.CLOSURE, self.current_line)
                self.chunk.write(midx, self.current_line)
                # v2.0.2.1 — @onchange callback: dup closure before METHOD
                is_onchange = method.name in node.onchange_callbacks
                if is_onchange:
                    self.chunk.write(OpCode.DUP, self.current_line)
                self.chunk.write(OpCode.METHOD, self.current_line)
                mnidx = len(self.chunk.constants)
                self.chunk.constants.append(method.name)
                self.chunk.write(mnidx, self.current_line)
                self.chunk.lines.append(self.current_line)
                # v2.0.2.1 — register onchange callback after METHOD
                if is_onchange:
                    field = node.onchange_callbacks[method.name]
                    fidx = len(self.chunk.constants)
                    self.chunk.constants.append(field)
                    self.chunk.write(OpCode.CONSTANT, self.current_line)
                    self.chunk.write(fidx, self.current_line)
                    self.chunk.write(OpCode.ONCHANGE_DEFINE, self.current_line)

        # v1.8.7: Compile property getters/setters — keep closure on stack via DUP + METHOD
        for prop in node.properties:
            gname = f"__prop_get_{prop.name}"
            sname = f"__prop_set_{prop.name}"
            # Compile getter: push closure, DUP it, METHOD pops one copy, other stays for PROP_DEFINE
            if prop.getter:
                sub = Compiler(parent=self)
                sub.depth = 1
                sub.define_local("self")
                for stmt in prop.getter:
                    sub.compile_stmt(stmt)
                last = sub.chunk.code[-1] if sub.chunk.code else None
                if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
                    sub.chunk.write(OpCode.NIL, self.current_line)
                    sub.chunk.write(OpCode.RETURN_VAL, self.current_line)
                cidx = len(self.chunk.constants)
                self.chunk.constants.append(
                    FunctionProto(sub.chunk, sub.upvalues, name=gname))
                self.chunk.write(OpCode.CLOSURE, self.current_line)
                self.chunk.write(cidx, self.current_line)
                self.chunk.write(OpCode.DUP, self.current_line)
                self.chunk.write(OpCode.METHOD, self.current_line)
                mnidx = len(self.chunk.constants)
                self.chunk.constants.append(gname)
                self.chunk.write(mnidx, self.current_line)
                self.chunk.lines.append(self.current_line)
            else:
                self.chunk.write(OpCode.NIL, self.current_line)
            # Compile setter: same DUP trick
            if prop.setter:
                sub = Compiler(parent=self)
                sub.depth = 1
                sub.define_local("self")
                param_name = prop.setter_param or "v"
                sub.define_local(param_name)
                for stmt in prop.setter:
                    sub.compile_stmt(stmt)
                last = sub.chunk.code[-1] if sub.chunk.code else None
                if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
                    sub.chunk.write(OpCode.RETURN, self.current_line)
                cidx = len(self.chunk.constants)
                self.chunk.constants.append(
                    FunctionProto(sub.chunk, sub.upvalues, name=sname))
                self.chunk.write(OpCode.CLOSURE, self.current_line)
                self.chunk.write(cidx, self.current_line)
                self.chunk.write(OpCode.DUP, self.current_line)
                self.chunk.write(OpCode.METHOD, self.current_line)
                mnidx = len(self.chunk.constants)
                self.chunk.constants.append(sname)
                self.chunk.write(mnidx, self.current_line)
                self.chunk.lines.append(self.current_line)
            else:
                self.chunk.write(OpCode.NIL, self.current_line)
            # Push property name
            pidx = len(self.chunk.constants)
            self.chunk.constants.append(prop.name)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write(pidx, self.current_line)
            # Emit PROP_DEFINE — pops 3: name, setter (or nil), getter (or nil)
            self.chunk.write(OpCode.PROP_DEFINE, self.current_line)

        # v2.0.0.5 — compile invariants
        for inv in node.invariants:
            self.compile_expr(inv)
            self.chunk.write(OpCode.INVARIANT_DEFINE, self.current_line)

        # v2.0.2 — compile @export field metadata
        for name, (default, hints) in node.exports.items():
            if default is not None:
                self.compile_expr(default)
            else:
                self.chunk.write(OpCode.NIL, self.current_line)
            # compile hints dict
            if hints:
                for hk, hv in hints.items():
                    kidx = len(self.chunk.constants)
                    self.chunk.constants.append(hk)
                    self.chunk.write(OpCode.CONSTANT, self.current_line)
                    self.chunk.write(kidx, self.current_line)
                    self.compile_expr(hv)
                self.chunk.write(OpCode.DICT, self.current_line)
                self.chunk.write(len(hints), self.current_line)
            else:
                self.chunk.write(OpCode.NIL, self.current_line)
            name_idx = len(self.chunk.constants)
            self.chunk.constants.append(name)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write(name_idx, self.current_line)
            self.chunk.write(OpCode.EXPORT_DEFINE, self.current_line)

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
        for member_name, member_value in node.values.items():
            self.chunk.add_constant(member_name, self.current_line)
            self.chunk.add_constant(member_value, self.current_line)
        self.chunk.write(OpCode.DICT, self.current_line)
        self.chunk.write(len(node.values), self.current_line)
        self.chunk.add_constant(node.name, self.current_line)
        self.chunk.write(OpCode.ENUM_DECL, self.current_line)
        self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

    def _decl_name(self, node):
        """Get the name of a declaration node (func/var/let/class)."""
        if isinstance(node, (FunctionDecl, AsyncFuncDecl, VarDecl, LetDecl)):
            return node.name
        if isinstance(node, ClassDecl):
            return node.name
        return None

    def compile_export(self, node: ExportDecl):
        inner = node.declaration
        name = self._decl_name(inner)
        if name:
            self.chunk.exports.add(name)
        self.compile_stmt(inner)

    def compile_import(self, node: ImportDecl):
        self.chunk.write(OpCode.IMPORT, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.module_path)
        self.chunk.write(cidx & 0xFF, self.current_line)
        self.chunk.write((cidx >> 8) & 0xFF, self.current_line)
        self.chunk.write((cidx >> 16) & 0xFF, self.current_line)
        # Store alias info in constants so VM can create the alias dict
        alias = getattr(node, 'alias', None)
        names = getattr(node, 'imports', None)  # selective import: import "m" as {a, b}
        alias_cidx = len(self.chunk.constants)
        self.chunk.constants.append(alias)
        self.chunk.write(alias_cidx & 0xFF, self.current_line)
        self.chunk.write((alias_cidx >> 8) & 0xFF, self.current_line)
        self.chunk.write((alias_cidx >> 16) & 0xFF, self.current_line)
        names_cidx = len(self.chunk.constants)
        self.chunk.constants.append(names)
        self.chunk.write(names_cidx & 0xFF, self.current_line)
        self.chunk.write((names_cidx >> 8) & 0xFF, self.current_line)
        self.chunk.write((names_cidx >> 16) & 0xFF, self.current_line)
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
        FIX BUG-023: per-iteration scope for loop variable so closures capture the
        correct value (each iteration gets its own upvalue cell).

        Locals layout: [iter_list, index] in outer scope;
                       [loop_var?] in per-iteration scope;
                       [body_locals...] in body scope.
        """
        self.push_scope()

        # slot 0: iterator list (generators are coerced to list at runtime via GET_LOCAL/len)
        self.compile_expr(node.iterator)
        list_slot = self.define_local("__for_iter__")

        # slot 1: index = 0
        self.chunk.add_constant(0, self.current_line)
        idx_slot = self.define_local("__for_idx__")

        # NO loop variable pre-defined here — defined per-iteration so each
        # closure captures its own upvalue cell (BUG-023 fix)

        loop_start = len(self.chunk.code)

        self.loop_stack.append({
            'start': loop_start,
            'break_jumps': [],
            'continue_target': None,
            'continue_jumps': [],
            'base_local_count': len(self.locals),  # = 2 (iter, idx only)
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

        # ── Per-iteration scope for loop variable (BUG-023) ──
        if node.variables:
            self.push_scope()
            if len(node.variables) == 1:
                self.define_local(node.variables[0])
            else:
                tmp_slot = self.define_local("__for_tmp__")
                for j, var in enumerate(node.variables):
                    self.chunk.write(OpCode.GET_LOCAL, self.current_line)
                    self.chunk.write(tmp_slot, self.current_line)
                    self.chunk.add_constant(j, self.current_line)
                    self.chunk.write(OpCode.GET_INDEX, self.current_line)
                    self.define_local(var)
        else:
            self.chunk.write(OpCode.POP, self.current_line)

        # body
        self.push_scope()   # inner scope for body locals
        for stmt in node.body:
            self.compile_stmt(stmt)
        self._emit_scope_pops()      # clean up body-local vars before idx++
        self._pop_scope_no_emit()    # remove from tracking without double-emit

        if node.variables:
            self.pop_scope()  # pop iteration scope - CLOSE_UPVALUE if captured

        # BUG-21/27: Set continue_target AFTER iteration-scope cleanup so
        # continue jumps past the per-iteration scope
        continue_target = len(self.chunk.code)
        self.loop_stack[-1]['continue_target'] = continue_target
        # Patch all forward continue jumps now that target is known
        for cont in self.loop_stack[-1]['continue_jumps']:
            self.chunk.patch_jump(cont)
        self.loop_stack[-1]['continue_jumps'] = []  # already patched

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
        # BUG-21: patch any forward continue jumps to the idx++ continue_target
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
            'base_local_count': len(self.locals),
        })

        self.compile_expr(node.condition)
        exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        for stmt in node.body:
            self.compile_stmt(stmt)

        # BUG-11/22: emit POPs for body-scope locals BEFORE the backward jump
        # so they are reachable and the stack stays correct on every iteration
        self._emit_scope_pops()

        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

        loop_info = self.loop_stack.pop()
        for brk in loop_info['break_jumps']:
            self.chunk.patch_jump(brk)

        self._pop_scope_no_emit()

    def compile_game_loop(self, node: GameLoopStmt):
        self.push_scope()
        # Store fps in local
        self.compile_expr(node.fps)
        fps_slot = self.define_local("__game_fps__")

        loop_start = len(self.chunk.code)
        self.loop_stack.append({
            'start': loop_start,
            'break_jumps': [],
            'continue_target': loop_start,
            'continue_jumps': [],
            'base_local_count': len(self.locals),
        })

        # while true
        self.chunk.add_constant(True, self.current_line)
        exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # body
        for stmt in node.body:
            self.compile_stmt(stmt)

        # Inject _game_sync(fps) call at end of each frame
        self.compile_identifier("_game_sync")
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(fps_slot, self.current_line)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        self._emit_scope_pops()
        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

        loop_info = self.loop_stack.pop()
        for brk in loop_info['break_jumps']:
            self.chunk.patch_jump(brk)
        self._pop_scope_no_emit()

    def _emit_scope_pops(self):
        """Emit POP/CLOSE_UPVALUE for locals at current depth WITHOUT removing them yet."""
        for local in reversed(self.locals):
            if local.depth == self.depth:
                if local.is_captured:
                    self.chunk.write(OpCode.CLOSE_UPVALUE, self.current_line)
                else:
                    self.chunk.write(OpCode.POP, self.current_line)

    def _pop_scope_no_emit(self):
        """Remove locals at current depth from tracking without emitting POPs."""
        while self.locals and self.locals[-1].depth == self.depth:
            self.locals.pop()
        self.depth -= 1

    def compile_sequence(self, node: SequenceStmt):
        """Compile a sequence as an async function. v2.0.8.3"""
        sub = Compiler(parent=self)
        sub.depth = 1

        for stmt in node.body:
            sub.compile_stmt(stmt)

        last = sub.chunk.code[-1] if sub.chunk.code else None
        if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
            sub.chunk.write(OpCode.NIL, self.current_line)
            sub.chunk.write(OpCode.RETURN_VAL, self.current_line)

        proto = FunctionProto(sub.chunk, sub.upvalues, name=node.name, is_async=True, param_names=[])
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

    def compile_parallel_block(self, node: ParallelBlock):
        """Compile parallel { ... } inside a sequence. v2.0.8.3
        Creates an async lambda for each inner statement, calls them,
        then calls parallel() and awaits the result."""
        par_name_idx = len(self.chunk.constants)
        self.chunk.constants.append("parallel")
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        self.chunk.write(par_name_idx, self.current_line)

        for i, stmt in enumerate(node.body):
            sub = Compiler(parent=self)
            sub.depth = 1
            sub.compile_stmt(stmt)
            sub.chunk.write(OpCode.NIL, self.current_line)
            sub.chunk.write(OpCode.RETURN_VAL, self.current_line)
            proto = FunctionProto(sub.chunk, sub.upvalues, name=f"__seq_par_{i}", is_async=True, param_names=[])
            pidx = len(self.chunk.constants)
            self.chunk.constants.append(proto)
            self.chunk.write(OpCode.CLOSURE, self.current_line)
            self.chunk.write(pidx, self.current_line)
            self.chunk.write(OpCode.CALL, self.current_line)
            self.chunk.write(0, self.current_line)

        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(len(node.body), self.current_line)

        self.chunk.write(OpCode.AWAIT, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

    def compile_story(self, node: StoryStmt):
        """Compile a story as an async function. v2.0.8.4"""
        sub = Compiler(parent=self)
        sub.depth = 1

        for stmt in node.body:
            sub.compile_stmt(stmt)

        last = sub.chunk.code[-1] if sub.chunk.code else None
        if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
            sub.chunk.write(OpCode.NIL, self.current_line)
            sub.chunk.write(OpCode.RETURN_VAL, self.current_line)

        proto = FunctionProto(sub.chunk, sub.upvalues, name=node.name, is_async=True, param_names=[])
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

    def compile_npc(self, node: NpcStmt):
        """Compile npc 'speaker': 'text' — call show_dialogue and await."""
        fn_idx = len(self.chunk.constants)
        self.chunk.constants.append("show_dialogue")
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        self.chunk.write(fn_idx, self.current_line)
        self.compile_expr(node.speaker)
        self.compile_expr(node.text)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(2, self.current_line)
        self.chunk.write(OpCode.AWAIT, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

    def compile_choice(self, node: ChoiceStmt):
        """Compile choice { ... } — push option texts, call show_choice,
        await result, then dispatch to the selected option body.
        v2.0.8.4"""
        fn_idx = len(self.chunk.constants)
        self.chunk.constants.append("show_choice")
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        self.chunk.write(fn_idx, self.current_line)

        # Push all option texts onto stack
        for opt in node.options:
            self.compile_expr(opt.text)

        # push option count
        self.chunk.write(OpCode.CONSTANT, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(len(node.options))
        self.chunk.write(cidx, self.current_line)

        # Stack: [show_choice_fn, opt1, opt2, ..., count]
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(len(node.options) + 1, self.current_line)
        self.chunk.write(OpCode.AWAIT, self.current_line)

        # Stack: selected_index (0-based integer)
        # Build if-elif chain using DUP + EQUAL + JUMP_IF_FALSE_POP
        end_jumps = []
        for i, opt in enumerate(node.options):
            self.chunk.write(OpCode.DUP, self.current_line)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(i)
            self.chunk.write(cidx, self.current_line)
            self.chunk.write(OpCode.EQUAL, self.current_line)

            skip_patch = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

            self.chunk.write(OpCode.POP, self.current_line)

            for stmt in opt.body:
                self.compile_stmt(stmt)

            jmp_pos = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            end_jumps.append(jmp_pos)

            self.chunk.patch_jump(skip_patch)

        self.chunk.write(OpCode.POP, self.current_line)

        for jmp_pos in end_jumps:
            self.chunk.patch_jump(jmp_pos)

    def compile_flag(self, node: FlagStmt):
        """Compile flag name = value — set a story flag."""
        fn_idx = len(self.chunk.constants)
        self.chunk.constants.append("set_story_flag")
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        self.chunk.write(fn_idx, self.current_line)
        self.chunk.write(OpCode.CONSTANT, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)
        self.compile_expr(node.value)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(2, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

    def compile_goto(self, node: GotoStmt):
        """Compile goto label — not supported yet."""
        fn_idx = len(self.chunk.constants)
        self.chunk.constants.append("set_story_goto")
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        self.chunk.write(fn_idx, self.current_line)
        self.chunk.write(OpCode.CONSTANT, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.label)
        self.chunk.write(cidx, self.current_line)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

    def compile_scene(self, node: SceneStmt):
        """Compile scene 'name' — call scene_transition and await."""
        fn_idx = len(self.chunk.constants)
        self.chunk.constants.append("scene_transition")
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        self.chunk.write(fn_idx, self.current_line)
        self.compile_expr(node.name)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)
        self.chunk.write(OpCode.AWAIT, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

    def compile_label(self, node: LabelStmt):
        """Compile label name — no-op."""
        pass

    def compile_entity(self, node: EntityDecl):
        """Compile entity Name { component Foo(x=0) } — v2.0.11 ECS"""
        fn_idx = len(self.chunk.constants)
        self.chunk.constants.append("__entity_create")
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        self.chunk.write(fn_idx, self.current_line)

        self.chunk.write(OpCode.CONSTANT, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)

        for comp in node.components:
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(comp.name)
            self.chunk.write(cidx, self.current_line)
            for field in comp.fields:
                self.chunk.write(OpCode.CONSTANT, self.current_line)
                cidx = len(self.chunk.constants)
                self.chunk.constants.append(field.name)
                self.chunk.write(cidx, self.current_line)
                self.compile_expr(field.default)
            self.chunk.write(OpCode.DICT, self.current_line)
            self.chunk.write(len(comp.fields), self.current_line)
            self.chunk.write(OpCode.LIST, self.current_line)
            self.chunk.write(2, self.current_line)

        self.chunk.write(OpCode.LIST, self.current_line)
        self.chunk.write(len(node.components), self.current_line)

        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(2, self.current_line)

        self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

    def compile_system(self, node: SystemDecl):
        """Compile system Name { requires A, B func update(e, dt) { } } — v2.0.11 ECS"""
        fn_idx = len(self.chunk.constants)
        self.chunk.constants.append("__system_create")
        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        self.chunk.write(fn_idx, self.current_line)

        self.chunk.write(OpCode.CONSTANT, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)

        for req in node.requires:
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(req)
            self.chunk.write(cidx, self.current_line)
        self.chunk.write(OpCode.LIST, self.current_line)
        self.chunk.write(len(node.requires), self.current_line)

        sub = Compiler(parent=self)
        sub.depth = 1
        for param in node.func.parameters:
            sub.define_local(param)
        for stmt in node.func.body:
            sub.compile_stmt(stmt)
        last = sub.chunk.code[-1] if sub.chunk.code else None
        if last not in (int(OpCode.RETURN), int(OpCode.RETURN_VAL)):
            sub.chunk.write(OpCode.NIL, self.current_line)
            sub.chunk.write(OpCode.RETURN_VAL, self.current_line)
        proto = FunctionProto(sub.chunk, sub.upvalues, name=node.func.name, is_async=False, param_names=node.func.parameters)
        idx = len(self.chunk.constants)
        self.chunk.constants.append(proto)
        self.chunk.write(OpCode.CLOSURE, self.current_line)
        self.chunk.write(idx, self.current_line)

        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(3, self.current_line)

        self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append(node.name)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)

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

        # BUG-22: emit scope pops before backward jump so they're reachable each iteration
        self._emit_scope_pops()

        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)

        loop_info = self.loop_stack.pop()
        for brk in loop_info['break_jumps']:
            self.chunk.patch_jump(brk)
        for cont in loop_info['continue_jumps']:
            self.chunk.patch_jump(cont)
        self._pop_scope_no_emit()

    def _compile_body_stmts(self, body, expr_mode=False):
        """Compile body statements. In expr_mode, leaves last value on stack."""
        if not expr_mode:
            for stmt in body:
                self.compile_stmt(stmt)
            return
        if not body:
            self.chunk.write(OpCode.NIL, self.current_line)
            return
        for i, stmt in enumerate(body):
            if i == len(body) - 1 and isinstance(stmt, ExprStmt):
                self.compile_expr(stmt.expression)
            else:
                self.compile_stmt(stmt)

    def compile_match(self, node: MatchStmt):
        self.compile_expr(node.subject)
        end_jumps = []

        for case in node.cases:
            skip_to_next = self._compile_match_case(case)
            if skip_to_next is not None:
                end_jumps.append(skip_to_next)

        self.chunk.write(OpCode.POP, self.current_line)
        for ej in end_jumps:
            self.chunk.patch_jump(ej)

    def compile_match_expr(self, node: MatchExpr):
        self.compile_expr(node.subject)
        end_jumps = []

        for case in node.cases:
            skip_to_next = self._compile_match_case(case, expr_mode=True)
            if skip_to_next is not None:
                end_jumps.append(skip_to_next)

        self.chunk.write(OpCode.POP, self.current_line)
        self.chunk.write(OpCode.NIL, self.current_line)
        for ej in end_jumps:
            self.chunk.patch_jump(ej)

    def _compile_define_var(self, name: str):
        """Define a variable (local or global) with value from stack top."""
        if self.depth > 0:
            self.define_local(name)
        else:
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            gidx = len(self.chunk.constants)
            self.chunk.constants.append(name)
            self.chunk.write(gidx, self.current_line)
            self.chunk.lines.append(self.current_line)

    def _compile_named_case(self, body, guard, bind_after_guard, bind_before_guard=None):
        """Shared helper for cases with optional guard. Returns end_jump offset.
        
        Assumes subject is on stack. After type/value check passes and subject remains.
        bind_after_guard() is called inside the scope (after guard passes).
        bind_before_guard() is called before guard is evaluated.
        Returns end_jump offset for patching.
        """
        if guard:
            if bind_before_guard:
                bind_before_guard()
            if self.depth > 0:
                guard_copy = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
                self.push_scope()
            else:
                self.push_scope()
                self.chunk.write(OpCode.DUP, self.current_line)
                self.compile_expr(guard)
                guard_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
        else:
            self.push_scope()

        if not guard:
            pass
        elif self.depth <= 0:
            pass

        bind_after_guard()

        for stmt in body:
            self.compile_stmt(stmt)
        self.pop_scope()
        end_j = self.chunk.emit_jump(OpCode.JUMP, self.current_line)

        if guard:
            self.chunk.patch_jump(guard_copy if self.depth > 0 else guard_fail)

        return end_j

    def _compile_match_case(self, case, expr_mode=False) -> Optional[int]:
        """Compile a single match case. Returns end_jump offset or None for default."""
        pattern = case.pattern
        body = case.body
        guard = case.guard

        # ── helpers ───────────────────────────────────────────────────────
        def _has_var(p):
            return (isinstance(p, MatchBindPat) or
                    (hasattr(p, 'var_name') and p.var_name is not None))

        def _get_var_name(p):
            if isinstance(p, MatchBindPat):
                return p.name
            return p.var_name  # hasattr guard ensures this exists

        # ── Default/wildcard pattern ──────────────────────────────────────
        if isinstance(pattern, MatchDefaultPat):
            self.chunk.write(OpCode.POP, self.current_line)
            self.push_scope()
            if guard:
                self.compile_expr(guard)
                guard_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
                self._compile_body_stmts(body, expr_mode)
                self.pop_scope()
                end_j = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
                self.chunk.patch_jump(guard_fail)
                self.pop_scope()
                self.chunk.write(OpCode.POP, self.current_line)
                return end_j
            self._compile_body_stmts(body, expr_mode)
            self.pop_scope()
            if expr_mode:
                return self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            return None

        # ── Bind pattern (case v => ...) ──────────────────────────────────
        if isinstance(pattern, MatchBindPat):
            need_survival = guard is not None
            if need_survival:
                self.chunk.write(OpCode.DUP, self.current_line)  # survival copy
            self.push_scope()
            self._compile_define_var(pattern.name)
            guard_fail = None
            if guard:
                self.compile_expr(guard)
                guard_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            self._compile_body_stmts(body, expr_mode)
            self.pop_scope()
            if need_survival:
                self.chunk.write(OpCode.POP, self.current_line)  # success cleanup
            end_j = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            if guard_fail is not None:
                self.chunk.patch_jump(guard_fail)
                self.pop_scope()
            return end_j

        # ── Value pattern (case 42 => ...) ────────────────────────────────
        if isinstance(pattern, MatchValuePat):
            self.chunk.write(OpCode.DUP, self.current_line)
            self.compile_expr(pattern.expr)
            self.chunk.write(OpCode.EQUAL, self.current_line)
            skip_j = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            self.chunk.write(OpCode.POP, self.current_line)
            need_survival = guard is not None
            if need_survival:
                self.chunk.write(OpCode.DUP, self.current_line)
            self.push_scope()
            guard_fail = None
            if guard:
                self.compile_expr(guard)
                guard_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            self._compile_body_stmts(body, expr_mode)
            self.pop_scope()
            if need_survival:
                self.chunk.write(OpCode.POP, self.current_line)
            end_j = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            if guard_fail is not None:
                self.chunk.patch_jump(guard_fail)
                self.chunk.write(OpCode.POP, self.current_line)
            self.chunk.patch_jump(skip_j)
            return end_j

        # ── Type pattern (case int v => ...) ──────────────────────────────
        if isinstance(pattern, MatchTypePat):
            self.chunk.write(OpCode.DUP, self.current_line)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(pattern.type_name)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write(cidx, self.current_line)
            self.chunk.lines.append(self.current_line)
            self.chunk.write(OpCode.IS_CHECK, self.current_line)
            skip_j = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            has_var = pattern.var_name is not None
            need_survival = guard is not None and has_var
            if need_survival:
                self.chunk.write(OpCode.DUP, self.current_line)
            self.push_scope()
            if has_var:
                self._compile_define_var(pattern.var_name)
            guard_fail = None
            if guard:
                self.compile_expr(guard)
                guard_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            self._compile_body_stmts(body, expr_mode)
            self.pop_scope()
            if need_survival:
                self.chunk.write(OpCode.POP, self.current_line)
            end_j = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            if guard_fail is not None:
                self.chunk.patch_jump(guard_fail)
                self.pop_scope()
            self.chunk.patch_jump(skip_j)
            return end_j

        # ── List destructure pattern ──────────────────────────────────────
        if isinstance(pattern, MatchListPat):
            return self._compile_match_list_pat(pattern, body, guard, expr_mode)

        # ── Dict destructure pattern ──────────────────────────────────────
        if isinstance(pattern, MatchDictPat):
            return self._compile_match_dict_pat(pattern, body, guard, expr_mode)

        self.error(f"Unsupported match pattern")
        return None

    def _compile_match_dict_pat(self, pattern: MatchDictPat, body, guard, expr_mode=False) -> int:
        """Compile dict destructure match case."""
        keys = pattern.keys

        # Check type is dict
        self.chunk.write(OpCode.DUP, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append("dict")
        self.chunk.write(OpCode.CONSTANT, self.current_line)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)
        self.chunk.write(OpCode.IS_CHECK, self.current_line)
        type_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # Check each key exists (before binding any)
        # CONTAINS expects stack: [..., item, collection] → bool
        # So DUP subject, push key, SWAP, then CONTAINS
        key_fails = []
        for key in keys:
            self.chunk.write(OpCode.DUP, self.current_line)
            ck = len(self.chunk.constants)
            self.chunk.constants.append(key)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write(ck, self.current_line)
            self.chunk.lines.append(self.current_line)
            self.chunk.write(OpCode.SWAP, self.current_line)
            self.chunk.write(OpCode.CONTAINS, self.current_line)
            kf = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            key_fails.append(kf)

        # All keys exist — store subject in temp local (depth 0)
        subject_slot = self._get_or_create_temp_local()
        base_local_count = len(self.locals)
        self.push_scope()

        # Bind each key's value as a named local
        for key in keys:
            self.chunk.write(OpCode.GET_LOCAL, self.current_line)
            self.chunk.write(subject_slot, self.current_line)
            ck = len(self.chunk.constants)
            self.chunk.constants.append(key)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write(ck, self.current_line)
            self.chunk.lines.append(self.current_line)
            self.chunk.write(OpCode.GET_INDEX, self.current_line)
            self._compile_define_var(key)

        # Guard clause
        guard_fail = None
        if guard:
            self.compile_expr(guard)
            guard_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # Body
        self._compile_body_stmts(body, expr_mode)

        saved_elem_count = len(self.locals) - base_local_count
        self.pop_scope()

        end_j = self.chunk.emit_jump(OpCode.JUMP, self.current_line)

        # Guard fail cleanup
        if guard_fail is not None:
            self.chunk.patch_jump(guard_fail)
            for _ in range(saved_elem_count):
                self.chunk.write(OpCode.POP, self.current_line)

        # Patch all fail jumps to next case
        for kf in key_fails:
            self.chunk.patch_jump(kf)
        self.chunk.patch_jump(type_fail)
        return end_j

    def _get_or_create_temp_local(self) -> int:
        """Return slot of __match_list_subject__ local, creating it at depth 0 if needed."""
        for i, loc in enumerate(self.locals):
            if loc.name == "__match_list_subject__":
                return i
        slot = self.define_local("__match_list_subject__")
        return slot

    def _compile_match_list_pat(self, pattern: MatchListPat, body, guard, expr_mode=False) -> int:
        """Compile list destructure match case.

        The subject is stored in a temp local at depth 0 (outside the match scope)
        so that pop_scope (which removes depth-1 element locals) leaves it intact
        for the next case when the guard fails.
        """
        elements = pattern.elements
        rest_name = pattern.rest
        n = len(elements)

        # Check type is list
        self.chunk.write(OpCode.DUP, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append("list")
        self.chunk.write(OpCode.CONSTANT, self.current_line)
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)
        self.chunk.write(OpCode.IS_CHECK, self.current_line)
        type_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # Check length
        self.chunk.write(OpCode.DUP, self.current_line)
        self.chunk.write(OpCode.LEN, self.current_line)
        self.chunk.add_constant(n, self.current_line)
        if rest_name:
            self.chunk.write(OpCode.GREATER_EQUAL, self.current_line)
        else:
            self.chunk.write(OpCode.EQUAL, self.current_line)
        len_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # Store subject in a temp local at the current depth (will survive pop_scope
        # because element locals are pushed one depth deeper).
        subject_slot = self._get_or_create_temp_local()
        # The subject value is already on the operand stack at base + subject_slot.
        # We register it as a local so that GET_LOCAL in the guard works, but
        # we DON'T push a new scope for it — it lives at the base depth.

        # Open scope for element variables (depth + 1)
        base_local_count = len(self.locals)
        self.push_scope()

        # Helper: re-push the subject onto the operand stack for element extraction
        def _load_subject():
            self.chunk.write(OpCode.GET_LOCAL, self.current_line)
            self.chunk.write(subject_slot, self.current_line)

        # Element extraction
        for i, elem_pat in enumerate(elements):
            if isinstance(elem_pat, MatchBindPat):
                _load_subject()
                self.chunk.add_constant(i, self.current_line)
                self.chunk.write(OpCode.GET_INDEX, self.current_line)
                self._compile_define_var(elem_pat.name)
            elif isinstance(elem_pat, MatchDefaultPat):
                pass
            else:
                self.error(f"List pattern element must be a variable name or _ (got {type(elem_pat).__name__})")

        # Rest variable
        if rest_name:
            _load_subject()
            self.chunk.add_constant(n, self.current_line)
            self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.BUILD_SLICE, self.current_line)
            self.chunk.write(OpCode.GET_INDEX, self.current_line)
            self._compile_define_var(rest_name)

        # Guard clause
        guard_fail = None
        if guard:
            self.compile_expr(guard)
            guard_fail = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        # Compile body
        self._compile_body_stmts(body, expr_mode)

        # How many element locals were added?
        saved_elem_count = len(self.locals) - base_local_count

        # Pop scope: removes element locals from bookkeeping and emits POP for each
        self.pop_scope()

        end_j = self.chunk.emit_jump(OpCode.JUMP, self.current_line)

        # Guard fail — we jumped OVER the body + pop_scope, so element values are
        # still on the runtime stack. Emit POPs to remove them.
        if guard_fail is not None:
            self.chunk.patch_jump(guard_fail)
            for _ in range(saved_elem_count):
                self.chunk.write(OpCode.POP, self.current_line)

        self.chunk.patch_jump(type_fail)
        self.chunk.patch_jump(len_fail)
        return end_j

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
        loop_info = self.loop_stack[-1]
        base = loop_info.get('base_local_count', 0)
        excess = len(self.locals) - base
        # FIX BUG-023: use CLOSE_UPVALUE for captured locals, POP for regular ones
        for i in range(excess):
            local = self.locals[base + i]
            if local.is_captured:
                self.chunk.write(OpCode.CLOSE_UPVALUE, self.current_line)
            else:
                self.chunk.write(OpCode.POP, self.current_line)
        jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        self.loop_stack[-1]['break_jumps'].append(jump)

    def compile_continue(self, node: ContinueStmt = None):
        if not self.loop_stack:
            self.error("'continue' outside of loop")
        loop_info = self.loop_stack[-1]
        base = loop_info.get('base_local_count', 0)
        excess = len(self.locals) - base
        # FIX BUG-023: use CLOSE_UPVALUE for captured locals, POP for regular ones
        for i in range(excess):
            local = self.locals[base + i]
            if local.is_captured:
                self.chunk.write(OpCode.CLOSE_UPVALUE, self.current_line)
            else:
                self.chunk.write(OpCode.POP, self.current_line)
        continue_target = loop_info.get('continue_target')
        if continue_target is not None:
            self.chunk.emit_loop(continue_target, self.current_line)
        else:
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
            self.chunk.write(OpCode.ASSERT_MSG, self.current_line)
        else:
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
        elif isinstance(node, TemplateStringExpr):
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
        elif isinstance(node, AwaitExpr):
            self.compile_expr(node.expression)
            self.chunk.write(OpCode.AWAIT, self.current_line)
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
        elif isinstance(node, IsExpr):
            self.compile_expr(node.left)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(node.type_name)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write(cidx, self.current_line)
            self.chunk.write(OpCode.IS_CHECK, self.current_line)
            if node.negated:
                self.chunk.write(OpCode.NOT, self.current_line)
        elif isinstance(node, SliceExpr):
            self.compile_expr(node.start)
            self.compile_expr(node.end)
            if node.step:
                self.compile_expr(node.step)
            else:
                self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.BUILD_SLICE, self.current_line)
        elif isinstance(node, ConditionalExpr):
            self.compile_ternary(node)
        elif isinstance(node, SpreadExpr):
            self.compile_expr(node.iterable)
            self.chunk.write(OpCode.SPREAD, self.current_line)
        elif isinstance(node, NullishCoalescingExpr):
            self.compile_nullish(node)
        elif isinstance(node, OptionalChainingExpr):
            self.compile_optional_chain(node)
        elif isinstance(node, MatchExpr):
            self.compile_match_expr(node)
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
        elif isinstance(node, SetComprehension):
            self.compile_set_comprehension(node)
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
        # Treat "this" as alias for "self" (slot 0)
        if name == "this":
            name = "self"
        # v1.9.1: If declared global, skip local/upvalue resolution
        if name in self.global_names:
            self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(name)
            self.chunk.write(cidx, self.current_line)
            self.chunk.lines.append(self.current_line)
            return
        # v1.9.1.1: If declared nonlocal, force upvalue resolution
        if name in self.nonlocal_names:
            idx = self.resolve_upvalue(name)
            if idx is None:
                self.error(f"Cannot find enclosing variable for nonlocal '{name}'")
            self.chunk.write(OpCode.GET_UPVALUE, self.current_line)
            self.chunk.write(idx, self.current_line)
            return
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
        # v1.9.1: If declared global, skip local/upvalue resolution
        if name in self.global_names:
            self.chunk.write(OpCode.SET_GLOBAL, self.current_line)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(name)
            self.chunk.write(cidx, self.current_line)
            self.chunk.lines.append(self.current_line)
            return
        # v1.9.1.1: If declared nonlocal, force upvalue resolution
        if name in self.nonlocal_names:
            idx = self.resolve_upvalue(name)
            if idx is None:
                self.error(f"Cannot find enclosing variable for nonlocal '{name}'")
            self.chunk.write(OpCode.SET_UPVALUE, self.current_line)
            self.chunk.write(idx, self.current_line)
            return
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
        # v2.0.25 — detect breakpoint() and emit BREAKPOINT opcode
        if isinstance(node.callee, Identifier) and node.callee.name == "breakpoint":
            if node.arguments:
                self.error("breakpoint() takes no arguments")
            if hasattr(node, 'named_arguments') and node.named_arguments:
                self.error("breakpoint() takes no arguments")
            self.chunk.write(OpCode.BREAKPOINT, self.current_line)
            self.chunk.write(OpCode.NIL, self.current_line)
            return
        self.compile_expr(node.callee)
        # Check if any argument is a spread expression
        has_spread_args = any(isinstance(arg, SpreadExpr) for arg in node.arguments)
        if has_spread_args:
            # Build positional args into a list
            self.chunk.write(OpCode.LIST, self.current_line)
            self.chunk.write(0, self.current_line)
            for arg in node.arguments:
                if isinstance(arg, SpreadExpr):
                    self.compile_expr(arg.iterable)
                    self.chunk.write(OpCode.LIST_EXTEND, self.current_line)
                else:
                    self.compile_expr(arg)
                    self.chunk.write(OpCode.LIST_APPEND, self.current_line)
            total_args = 1  # the list is one item
        else:
            # Fast path: no spread, push individual args
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
        if has_spread_args:
            self.chunk.write(OpCode.CALL_SPREAD, self.current_line)
            self.chunk.write(total_args, self.current_line)
        else:
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
        self.chunk.write(OpCode.DICT, self.current_line)
        self.chunk.write(0, self.current_line)
        for is_spread, item in node.all_entries():
            if is_spread:
                self.compile_expr(item.iterable)
                self.chunk.write(OpCode.DICT_MERGE, self.current_line)
            else:
                key, value = item
                self.compile_expr(key)
                self.compile_expr(value)
                self.chunk.write(OpCode.DICT_UPDATE, self.current_line)

    def compile_tuple(self, node: TupleLiteral):
        has_spread = any(isinstance(e, SpreadExpr) for e in node.elements)
        if has_spread:
            self.chunk.write(OpCode.LIST, self.current_line)
            self.chunk.write(0, self.current_line)
            for elem in node.elements:
                if isinstance(elem, SpreadExpr):
                    self.compile_expr(elem.iterable)
                    self.chunk.write(OpCode.LIST_EXTEND, self.current_line)
                else:
                    self.compile_expr(elem)
                    self.chunk.write(OpCode.LIST_APPEND, self.current_line)
            self.chunk.write(OpCode.LIST_TO_TUPLE, self.current_line)
        else:
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
        self.chunk.write(OpCode.POP, self.current_line)  # discard value pushed by SET_INDEX

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

    def compile_set_comprehension(self, node: SetComprehension):
        self.push_scope()

        self.chunk.write(OpCode.LIST, self.current_line)
        self.chunk.write(0, self.current_line)
        res_slot = self.define_local("__sc_res")

        self.compile_expr(node.iterator)
        src_slot = self.define_local("__sc_src")

        self.chunk.add_constant(0, self.current_line)
        idx_slot = self.define_local("__sc_idx")

        self.chunk.write(OpCode.NIL, self.current_line)
        var_slot = self.define_local(node.variable)

        self.chunk.write(OpCode.NIL, self.current_line)
        elem_slot = self.define_local("__sc_elem")

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

        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(src_slot, self.current_line)
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(idx_slot, self.current_line)
        self.chunk.write(OpCode.GET_INDEX, self.current_line)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(var_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        if_jump = None
        if node.condition:
            self.compile_expr(node.condition)
            if_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)

        self.compile_expr(node.element)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(elem_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(res_slot, self.current_line)
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(elem_slot, self.current_line)
        self.chunk.write(OpCode.LIST_APPEND, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

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

        self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
        cidx = len(self.chunk.constants)
        self.chunk.constants.append("set")
        self.chunk.write(cidx, self.current_line)
        self.chunk.lines.append(self.current_line)
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(res_slot, self.current_line)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)
        self.chunk.write(OpCode.SET_LOCAL, self.current_line)
        self.chunk.write(res_slot, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)

        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(res_slot, self.current_line)
        self.pop_scope()


def compile_ast(node: Program) -> Chunk:
    compiler = Compiler()
    return compiler.compile(node)
