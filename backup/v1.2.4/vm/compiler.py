from ..parser.ast import *
from .bytecode import Chunk, OpCode
from typing import Dict, List, Optional


class CompilerError(Exception):
    pass


class Local:
    def __init__(self, name: str, depth: int = 0, is_captured: bool = False):
        self.name = name
        self.depth = depth
        self.is_captured = is_captured


class Compiler:
    def __init__(self):
        self.chunk = Chunk()
        self.locals: List[Local] = []
        self.scopes = [{}]
        self.depth = 0
        self.loop_stack: List[Dict] = []
        self.jumps_to_patch: List[tuple] = []
        self.current_line = 0
        self.functions: List[Chunk] = []
        
    def error(self, msg: str):
        raise CompilerError(f"Compile error at line {self.current_line}: {msg}")
    
    def push_scope(self):
        self.scopes.append({})
        self.depth += 1
    
    def pop_scope(self):
        while self.locals and self.locals[-1].depth >= self.depth:
            self.locals.pop()
        if self.scopes:
            self.scopes.pop()
        self.depth = max(0, self.depth - 1)
    
    def define_local(self, name: str):
        if name not in [l.name for l in self.locals if l.depth == self.depth]:
            self.locals.append(Local(name, self.depth))
        if self.scopes:
            self.scopes[-1][name] = len(self.locals) - 1
    
    def resolve_local(self, name: str) -> Optional[int]:
        for i in range(len(self.locals) - 1, -1, -1):
            if self.locals[i].name == name and self.locals[i].depth < self.depth:
                return len(self.locals) - 1 - i
        return None
    
    def compile(self, node: Program) -> Chunk:
        for stmt in node.statements:
            self.compile_stmt(stmt)
        
        self.chunk.write(OpCode.HALT, 0)
        return self.chunk
    
    def compile_stmt(self, node: ASTNode):
        self.current_line = getattr(node, 'line', 0)
        
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
            self.compile_break()
        elif isinstance(node, ContinueStmt):
            self.compile_continue()
        elif isinstance(node, TryStmt):
            self.compile_try(node)
        elif isinstance(node, WithStmt):
            self.compile_with(node)
        elif isinstance(node, ThrowStmt):
            self.compile_throw(node)
        elif isinstance(node, EnumDecl):
            pass
    
    def compile_var_decl(self, node, is_const=False):
        idx = self.resolve_local(node.name)
        if idx is not None:
            if node.initializer:
                self.compile_expr(node.initializer)
            else:
                self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.SET_LOCAL, self.current_line)
            self.chunk.write(idx, self.current_line)
        else:
            if node.initializer:
                self.compile_expr(node.initializer)
            else:
                self.chunk.write(OpCode.NIL, self.current_line)
            name_idx = self.chunk.add_constant(node.name, self.current_line)
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            self.chunk.write(name_idx, self.current_line)
        
        self.define_local(node.name)
    
    def compile_function(self, node: FunctionDecl):
        func_chunk = Chunk()
        old_chunk = self.chunk
        old_locals = list(self.locals)
        old_depth = self.depth
        old_scopes = list(self.scopes)
        
        self.chunk = func_chunk
        self.locals = []
        self.scopes = [{}]
        self.depth = 1
        
        for param in node.parameters:
            self.define_local(param)
        
        for stmt in node.body:
            self.compile_stmt(stmt)
        
        if not func_chunk.code or func_chunk.code[-1] not in (OpCode.RETURN.value, OpCode.RETURN_VAL.value):
            self.chunk.write(OpCode.NIL, 0)
            self.chunk.write(OpCode.RETURN_VAL, 0)
        
        self.chunk = old_chunk
        const_idx = self.chunk.add_constant(func_chunk, self.current_line)
        self.chunk.write(OpCode.CONSTANT, self.current_line)
        self.chunk.write(const_idx, self.current_line)
        
        self.locals = old_locals
        self.depth = old_depth
        self.scopes = old_scopes
    
    def compile_class(self, node: ClassDecl):
        self.chunk.write(OpCode.CLASS, self.current_line)
        const_idx = self.chunk.add_constant(node.name, self.current_line)
        self.chunk.write(const_idx, self.current_line)
        
        for method in node.methods:
            if isinstance(method, FunctionDecl):
                self.compile_function(method)
                self.chunk.write(OpCode.METHOD, self.current_line)
                const_idx = self.chunk.add_constant(method.name, self.current_line)
                self.chunk.write(const_idx, self.current_line)
        
        self.chunk.write(OpCode.END_METHOD, self.current_line)
        
        idx = self.resolve_local(node.name)
        if idx is not None:
            self.chunk.write(OpCode.SET_LOCAL, self.current_line)
            self.chunk.write(idx, self.current_line)
        else:
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            const_idx = self.chunk.add_constant(node.name, self.current_line)
            self.chunk.write(const_idx, self.current_line)
        
        self.define_local(node.name)
    
    def compile_import(self, node: ImportDecl):
        const_idx = self.chunk.add_constant(node.module_path, self.current_line)
        self.chunk.write_constant(const_idx, self.current_line)
        self.chunk.write(OpCode.IMPORT, self.current_line)
        
        if node.alias:
            const_idx = self.chunk.add_constant(node.alias, self.current_line)
            self.chunk.write_constant(const_idx, self.current_line)
        elif node.imports:
            for imp_name in node.imports:
                const_idx = self.chunk.add_constant(imp_name, self.current_line)
                self.chunk.write_constant(const_idx, self.current_line)
        
        self.chunk.write(OpCode.END_IMPORT, self.current_line)
    
    def compile_if(self, node: IfStmt):
        self.compile_expr(node.condition)
        jump_false = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
        
        for stmt in node.then_branch:
            self.compile_stmt(stmt)
        
        end_jumps = []
        
        if node.elif_branches:
            for cond, body in node.elif_branches[:-1]:
                else_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
                end_jumps.append(else_jump)
                self.chunk.patch_jump(jump_false)
                
                self.compile_expr(cond)
                jump_false = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
                
                for stmt in body:
                    self.compile_stmt(stmt)
            
            cond, body = node.elif_branches[-1]
            self.chunk.patch_jump(jump_false)
            
            self.compile_expr(cond)
            jump_false = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            
            for stmt in body:
                self.compile_stmt(stmt)
            
            end_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            end_jumps.append(end_jump)
            self.chunk.patch_jump(jump_false)
        
        if node.else_branch:
            self.chunk.patch_jump(jump_false)
            for stmt in node.else_branch:
                self.compile_stmt(stmt)
        else:
            self.chunk.patch_jump(jump_false)
        
        for ej in end_jumps:
            self.chunk.patch_jump(ej)
    
    def compile_for(self, node: ForStmt):
        self.push_scope()
        
        if node.variable:
            self.define_local(node.variable)
            var_idx = self.resolve_local(node.variable)
        else:
            var_idx = None
        
        self.compile_expr(node.iterator)
        
        loop_start = len(self.chunk.code)
        
        self.loop_stack.append({
            'start': loop_start,
            'body': len(self.chunk.code),
            'break_jumps': [],
            'continue_jumps': [],
            'variable': node.variable,
            'var_idx': var_idx
        })
        
        self.chunk.write(OpCode.DUP, self.current_line)
        check_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
        
        if var_idx is not None:
            self.chunk.write(OpCode.GET_LOCAL, self.current_line)
            self.chunk.write(var_idx, self.current_line)
        
        for stmt in node.body:
            self.compile_stmt(stmt)
        
        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(check_jump)
        
        if var_idx is not None:
            self.chunk.write(OpCode.POP, self.current_line)
        
        for brk in self.loop_stack.pop()['break_jumps']:
            self.chunk.patch_jump(brk)
        
        self.pop_scope()
    
    def compile_while(self, node: WhileStmt):
        self.push_scope()
        
        loop_start = len(self.chunk.code)
        
        self.compile_expr(node.condition)
        exit_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
        
        self.loop_stack.append({
            'start': loop_start,
            'body': len(self.chunk.code),
            'break_jumps': [],
            'continue_jumps': []
        })
        
        for stmt in node.body:
            self.compile_stmt(stmt)
        
        self.chunk.emit_loop(loop_start, self.current_line)
        self.chunk.patch_jump(exit_jump)
        
        for brk in self.loop_stack.pop()['break_jumps']:
            self.chunk.patch_jump(brk)
        
        self.pop_scope()
    
    def compile_do_while(self, node: DoWhileStmt):
        self.push_scope()
        
        loop_start = len(self.chunk.code)
        
        self.loop_stack.append({
            'start': loop_start,
            'body': len(self.chunk.code),
            'break_jumps': [],
            'continue_jumps': []
        })
        
        for stmt in node.body:
            self.compile_stmt(stmt)
        
        self.compile_expr(node.condition)
        self.chunk.emit_loop(loop_start, self.current_line)
        
        for brk in self.loop_stack.pop()['break_jumps']:
            self.chunk.patch_jump(brk)
        
        self.pop_scope()
    
    def compile_match(self, node: MatchStmt):
        self.compile_expr(node.expression)
        
        exit_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        
        for case, body in node.cases:
            self.chunk.write(OpCode.MATCH, self.current_line)
            
            for val in case:
                self.compile_expr(val)
            
            case_jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            
            for stmt in body:
                self.compile_stmt(stmt)
            
            body_end_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
            self.chunk.patch_jump(case_jump)
            self.chunk.patch_jump(body_end_jump)
        
        self.chunk.write(OpCode.POP, self.current_line)
        self.chunk.patch_jump(exit_jump)
    
    def compile_return(self, node: ReturnStmt):
        if node.value:
            self.compile_expr(node.value)
            self.chunk.write(OpCode.RETURN_VAL, self.current_line)
        else:
            self.chunk.write(OpCode.NIL, self.current_line)
            self.chunk.write(OpCode.RETURN_VAL, self.current_line)
    
    def compile_break(self):
        if not self.loop_stack:
            self.error("break outside of loop")
        loop_info = self.loop_stack[-1]
        jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        loop_info['break_jumps'].append(jump)
    
    def compile_continue(self):
        if not self.loop_stack:
            self.error("continue outside of loop")
        loop_info = self.loop_stack[-1]
        jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        loop_info['continue_jumps'].append(jump)
        self.chunk.patch_jump(jump)
        self.chunk.emit_loop(loop_info['start'], self.current_line)
    
    def compile_try(self, node: TryStmt):
        try_jump = self.chunk.emit_jump(OpCode.TRY, self.current_line)
        
        for stmt in node.try_body:
            self.compile_stmt(stmt)
        
        self.chunk.write(OpCode.TRY_END, self.current_line)
        
        skip_catch = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        
        catch_target = len(self.chunk.code)
        if node.catch_body:
            self.chunk.patch_jump(try_jump)
            self.chunk.write(OpCode.CATCH, self.current_line)
            
            if node.exception_var:
                self.define_local(node.exception_var)
            
            for stmt in node.catch_body:
                self.compile_stmt(stmt)
            
            self.chunk.write(OpCode.CATCH_END, self.current_line)
        
        self.chunk.patch_jump(skip_catch)
        
        if node.finally_body:
            self.chunk.write(OpCode.FINALLY, self.current_line)
            for stmt in node.finally_body:
                self.compile_stmt(stmt)
            self.chunk.write(OpCode.END_FINALLY, self.current_line)
    
    def compile_throw(self, node: ThrowStmt):
        self.compile_expr(node.expression)
        self.chunk.write(OpCode.THROW, self.current_line)
    
    def compile_with(self, node: WithStmt):
        self.compile_expr(node.resource)
        self.chunk.write(OpCode.WITH_ENTER, self.current_line)
        
        if node.variable:
            self.define_local(node.variable)
        
        for stmt in node.body:
            self.compile_stmt(stmt)
        
        self.chunk.write(OpCode.WITH_EXIT, self.current_line)
    
    def compile_expr(self, node: ASTNode):
        if node is None:
            return
        
        self.current_line = getattr(node, 'line', self.current_line)
        
        if isinstance(node, NumberLiteral):
            const_idx = self.chunk.add_constant(node.value, self.current_line)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write_constant(const_idx, self.current_line)
        elif isinstance(node, StringLiteral):
            const_idx = self.chunk.add_constant(node.value, self.current_line)
            self.chunk.write(OpCode.CONSTANT, self.current_line)
            self.chunk.write_constant(const_idx, self.current_line)
        elif isinstance(node, BooleanLiteral):
            self.chunk.write(OpCode.TRUE if node.value else OpCode.FALSE, self.current_line)
        elif isinstance(node, NilLiteral):
            self.chunk.write(OpCode.NIL, self.current_line)
        elif isinstance(node, Identifier):
            self.compile_identifier(node.name)
        elif isinstance(node, BinaryExpr):
            self.compile_binary_expr(node)
        elif isinstance(node, UnaryExpr):
            self.compile_unary_expr(node)
        elif isinstance(node, CallExpr):
            self.compile_call(node)
        elif isinstance(node, GetExpr):
            self.compile_get(node)
        elif isinstance(node, SetExpr):
            self.compile_set(node)
        elif isinstance(node, ListLiteral):
            self.compile_list(node)
        elif isinstance(node, DictLiteral):
            self.compile_dict(node)
        elif isinstance(node, TupleLiteral):
            self.compile_tuple(node)
        elif isinstance(node, ConditionalExpr):
            self.compile_ternary(node)
        elif isinstance(node, SpreadExpr):
            self.compile_spread(node)
        elif isinstance(node, NullishCoalescingExpr):
            self.compile_nullish(node)
        elif isinstance(node, OptionalChainingExpr):
            self.compile_optional_chain(node)
        elif isinstance(node, SelfExpr):
            pass
        elif isinstance(node, AssignExpr):
            self.compile_assign(node)
    
    def compile_identifier(self, name: str):
        idx = self.resolve_local(name)
        if idx is not None:
            self.chunk.write(OpCode.GET_LOCAL, self.current_line)
            self.chunk.write(idx, self.current_line)
        else:
            const_idx = self.chunk.add_constant(name, self.current_line)
            self.chunk.write(OpCode.GET_GLOBAL, self.current_line)
            self.chunk.write(const_idx, self.current_line)
    
    def compile_binary_expr(self, node: BinaryExpr):
        self.compile_expr(node.left)
        self.compile_expr(node.right)
        
        ops = {
            "+": OpCode.ADD,
            "-": OpCode.SUBTRACT,
            "*": OpCode.MULTIPLY,
            "/": OpCode.DIVIDE,
            "%": OpCode.MODULO,
            "^": OpCode.POWER,
            "//": OpCode.FLOOR_DIV,
            "&": OpCode.BIT_AND,
            "|": OpCode.BIT_OR,
            "<<": OpCode.SHIFT_LEFT,
            ">>": OpCode.SHIFT_RIGHT,
        }
        
        comp_ops = {
            "==": OpCode.EQUAL,
            "!=": OpCode.NOT_EQUAL,
            "<": OpCode.LESS,
            ">": OpCode.GREATER,
            "<=": OpCode.LESS_EQUAL,
            ">=": OpCode.GREATER_EQUAL,
        }
        
        if node.operator in ops:
            self.chunk.write(ops[node.operator], self.current_line)
        elif node.operator in comp_ops:
            self.chunk.write(comp_ops[node.operator], self.current_line)
        elif node.operator == "and":
            self.chunk.write(OpCode.DUP, self.current_line)
            jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
            self.chunk.write(OpCode.POP, self.current_line)
            self.chunk.patch_jump(jump)
        elif node.operator == "or":
            self.chunk.write(OpCode.DUP, self.current_line)
            jump = self.chunk.emit_jump(OpCode.JUMP_IF_TRUE_POP, self.current_line)
            self.chunk.write(OpCode.POP, self.current_line)
            self.chunk.patch_jump(jump)
        elif node.operator == "..":
            self.chunk.write(OpCode.RANGE, self.current_line)
    
    def compile_unary_expr(self, node: UnaryExpr):
        self.compile_expr(node.right)
        
        if node.operator == "-":
            self.chunk.write(OpCode.NEGATE, self.current_line)
        elif node.operator == "not":
            self.chunk.write(OpCode.NOT, self.current_line)
        elif node.operator == "~":
            self.chunk.write(OpCode.BIT_NOT, self.current_line)
        elif node.operator == "++":
            self.chunk.write(OpCode.INCREMENT, self.current_line)
        elif node.operator == "--":
            self.chunk.write(OpCode.DECREMENT, self.current_line)
    
    def compile_call(self, node: CallExpr):
        self.compile_expr(node.callee)
        
        for arg in node.arguments:
            self.compile_expr(arg)
        
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(len(node.arguments), self.current_line)
    
    def compile_get(self, node: GetExpr):
        self.compile_expr(node.object)
        const_idx = self.chunk.add_constant(node.name, self.current_line)
        self.chunk.write(OpCode.GET_PROPERTY, self.current_line)
        self.chunk.write(const_idx, self.current_line)
    
    def compile_set(self, node: SetExpr):
        self.compile_expr(node.object)
        self.compile_expr(node.value)
        self.chunk.write(OpCode.DUP, self.current_line)
        const_idx = self.chunk.add_constant(node.name, self.current_line)
        self.chunk.write(OpCode.SET_PROPERTY, self.current_line)
        self.chunk.write(const_idx, self.current_line)
    
    def compile_assign(self, node: AssignExpr):
        self.compile_expr(node.value)
        idx = self.resolve_local(node.name)
        if idx is not None:
            self.chunk.write(OpCode.SET_LOCAL, self.current_line)
            self.chunk.write(idx, self.current_line)
        else:
            const_idx = self.chunk.add_constant(node.name, self.current_line)
            self.chunk.write(OpCode.SET_GLOBAL, self.current_line)
            self.chunk.write(const_idx, self.current_line)
    
    def compile_list(self, node: ListLiteral):
        for elem in node.elements:
            self.compile_expr(elem)
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
        jump_false = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
        
        self.compile_expr(node.then_branch)
        end_jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        
        self.chunk.patch_jump(jump_false)
        self.compile_expr(node.else_branch)
        self.chunk.patch_jump(end_jump)
    
    def compile_spread(self, node: SpreadExpr):
        self.compile_expr(node.expression)
        self.chunk.write(OpCode.SPREAD, self.current_line)
    
    def compile_nullish(self, node: NullishCoalescingExpr):
        self.compile_expr(node.left)
        self.chunk.write(OpCode.DUP, self.current_line)
        self.chunk.write(OpCode.NIL, self.current_line)
        
        jump = self.chunk.emit_jump(OpCode.JUMP_IF_FALSE_POP, self.current_line)
        self.chunk.write(OpCode.POP, self.current_line)
        self.compile_expr(node.right)
        self.chunk.patch_jump(jump)
    
    def compile_optional_chain(self, node: OptionalChainingExpr):
        self.compile_expr(node.object)
        
        for access in node.accesses:
            if isinstance(access, str):
                const_idx = self.chunk.add_constant(access, self.current_line)
                self.chunk.write(OpCode.OPTIONAL_CHAIN, self.current_line)
                self.chunk.write(const_idx, self.current_line)
            else:
                self.compile_expr(access)
                self.chunk.write(OpCode.GET_INDEX, self.current_line)
        
        self.chunk.write(OpCode.OPTIONAL_CHAIN_END, self.current_line)


def compile_ast(ast: Program) -> Chunk:
    compiler = Compiler()
    return compiler.compile(ast)
