from typing import Dict, List, Any, Optional
from ..parser.ast import *
from ..runtime.builtins import BUILTINS


class IppFunction:
    def __init__(self, parameters: List[str], body: List[ASTNode], closure: 'Environment'):
        self.parameters = parameters
        self.body = body
        self.closure = closure
        self.is_init = False
    
    def __repr__(self):
        return f"<function({self.parameters})>"


class IppClass:
    def __init__(self, name: str, methods: Dict[str, IppFunction]):
        self.name = name
        self.methods = methods
    
    def __repr__(self):
        return f"<class {self.name}>"
    
    def get_method(self, name: str):
        return self.methods.get(name)


class IppInstance:
    def __init__(self, ipp_class: IppClass):
        self.ipp_class = ipp_class
        self.fields = {}
    
    def __repr__(self):
        return f"<{self.ipp_class.name} instance>"
    
    def __str__(self):
        return f"<{self.ipp_class.name} instance>"
    
    def get(self, name: str):
        if name in self.fields:
            return self.fields[name]
        method = self.ipp_class.get_method(name)
        if method:
            return BoundMethod(self, method)
        raise RuntimeError(f"Undefined property: {name}")
    
    def set(self, name: str, value: Any):
        self.fields[name] = value


class IppModule:
    def __init__(self, env: 'Environment', name: str = "module"):
        self._env = env
        self._name = name
    
    def __repr__(self):
        return f"<module '{self._name}'>"
    
    def __str__(self):
        return f"<module '{self._name}'>"
    
    def get(self, name: str):
        if self._env.has(name):
            return self._env.get(name)
        raise RuntimeError(f"Module '{self._name}' has no attribute '{name}'")
    
    def __getattr__(self, name: str):
        if name.startswith('_'):
            raise AttributeError(f"Module '{self._name}' has no attribute '{name}'")
        return self.get(name)


class IppEnum:
    def __init__(self, name: str, values: List[str]):
        self.name = name
        self.values = {}
        for i, v in enumerate(values):
            self.values[v] = IppEnumValue(name, v, i)
    
    def __repr__(self):
        return f"<enum {self.name}>"
    
    def get(self, name: str):
        if name in self.values:
            return self.values[name]
        raise RuntimeError(f"Enum {self.name} has no value {name}")


class IppEnumValue:
    def __init__(self, enum_name: str, name: str, index: int):
        self.enum_name = enum_name
        self.name = name
        self.index = index
    
    def __repr__(self):
        return f"{self.enum_name}.{self.name}"
    
    def __eq__(self, other):
        if isinstance(other, IppEnumValue):
            return self.enum_name == other.enum_name and self.name == other.name
        return False


class BoundMethod:
    def __init__(self, instance: 'IppInstance', method: IppFunction):
        self.instance = instance
        self.method = method


class IppList:
    def __init__(self, elements: List[Any]):
        self.elements = elements
    
    def __iter__(self):
        return iter(self.elements)
    
    def __len__(self):
        return len(self.elements)
    
    def __getitem__(self, index):
        if isinstance(index, float) and index.is_integer():
            index = int(index)
        return self.elements[index]
    
    def __setitem__(self, index, value):
        if isinstance(index, float) and index.is_integer():
            index = int(index)
        self.elements[index] = value
    
    def __repr__(self):
        return f"[{', '.join(repr(e) for e in self.elements)}]"
    
    def append(self, item):
        self.elements.append(item)
    
    def pop(self, index=-1):
        if not self.elements:
            raise RuntimeError("Cannot pop from empty list")
        return self.elements.pop(index)
    
    def push(self, item):
        self.elements.append(item)
    
    def shift(self):
        if not self.elements:
            raise RuntimeError("Cannot shift from empty list")
        return self.elements.pop(0)
    
    def unshift(self, item):
        self.elements.insert(0, item)
    
    def len(self):
        return len(self.elements)
    
    def contains(self, item):
        return item in self.elements
    
    def index_of(self, item):
        try:
            return self.elements.index(item)
        except ValueError:
            return -1
    
    def slice(self, start=0, end=None):
        return self.elements[start:end]
    
    def reverse(self):
        return list(reversed(self.elements))
    
    def join(self, separator=""):
        return separator.join(str(e) for e in self.elements)
    
    def clear(self):
        self.elements = []


class IppDict:
    def __init__(self, data: Dict[Any, Any]):
        self.data = data
    
    def __repr__(self):
        return f"{{{', '.join(f'{k}: {v}' for k, v in self.data.items())}}}"
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value):
        self.data[key] = value
    
    def len(self):
        return len(self.data)
    
    def keys(self):
        return list(self.data.keys())
    
    def values(self):
        return list(self.data.values())
    
    def items(self):
        return list(self.data.items())
    
    def has(self, key):
        return key in self.data
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
    
    def clear(self):
        self.data = {}


class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.values: Dict[str, Any] = {}
        self.parent = parent
        self.constants: Dict[str, bool] = {}  # Track let vs var
    
    def define(self, name: str, value: Any, constant: bool = False):
        self.values[name] = value
        self.constants[name] = constant
    
    def get(self, name: str):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")
    
    def assign(self, name: str, value: Any):
        if name in self.values:
            if self.constants.get(name, False):
                raise RuntimeError(f"Cannot reassign constant: {name}")
            self.values[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeError(f"Undefined variable: {name}")
    
    def has(self, name: str) -> bool:
        return name in self.values or (self.parent and self.parent.has(name))


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.environment = self.global_env
        self.return_value = None
        self.last_value = None
        self.break_flag = False
        self.continue_flag = False
        self.current_line = 0
        self.call_stack = []
        
        for name, func in BUILTINS.items():
            self.global_env.define(name, func, constant=False)

    def run(self, program: Program):
        try:
            for stmt in program.statements:
                if self.return_value is not None:
                    break
                self.execute(stmt)
        except RuntimeError as e:
            error_msg = str(e)
            if "Error at line" not in error_msg:
                stack_info = " -> ".join(self.call_stack) if self.call_stack else "main"
                raise RuntimeError(f"Error at line {self.current_line} in {stack_info}: {e}")
            raise

    def run_safe(self, program: Program):
        try:
            self.run(program)
        except Exception as e:
            print(f"Runtime error: {e}")

    def execute(self, stmt: ASTNode):
        return stmt.accept(self)

    def visit_program(self, node: Program):
        for stmt in node.statements:
            if self.return_value is not None:
                break
            stmt.accept(self)

    def visit_number_literal(self, node: NumberLiteral):
        return node.value

    def visit_string_literal(self, node: StringLiteral):
        return node.value

    def visit_boolean_literal(self, node: BooleanLiteral):
        return node.value

    def visit_nil_literal(self, node: NilLiteral):
        return None

    def visit_identifier(self, node: Identifier):
        return self.environment.get(node.name)

    def visit_assign_expr(self, node: AssignExpr):
        value = node.value.accept(self)
        self.environment.assign(node.name, value)
        return value

    def visit_binary_expr(self, node: BinaryExpr):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if node.operator == "+":
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, IppList) and isinstance(right, IppList):
                return IppList(left.elements + right.elements)
            if hasattr(left, '__add__'):
                return left + right
            return str(left) + str(right)
        elif node.operator == "-":
            if hasattr(left, '__sub__'):
                return left - right
            return left - right
        elif node.operator == "*":
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left * right
            if hasattr(left, '__mul__'):
                return left * right
            if hasattr(right, '__rmul__'):
                return right * left
            return left * right
        elif node.operator == "/":
            if right == 0:
                raise RuntimeError("Division by zero")
            if hasattr(left, '__truediv__'):
                return left / right
            return left / right
        elif node.operator == "**":
            return left ** right
        elif node.operator == "%":
            return left % right
        elif node.operator == "//":
            return int(left) // int(right)
        elif node.operator == "<<":
            return int(left) << int(right)
        elif node.operator == ">>":
            return int(left) >> int(right)
        elif node.operator == "&":
            return int(left) & int(right)
        elif node.operator == "|":
            return int(left) | int(right)
        elif node.operator == "^":
            return int(left) ^ int(right)
        elif node.operator == "==":
            return left == right
        elif node.operator == "!=":
            return left != right
        elif node.operator == "<":
            return left < right
        elif node.operator == ">":
            return left > right
        elif node.operator == "<=":
            return left <= right
        elif node.operator == ">=":
            return left >= right
        elif node.operator == "and":
            return bool(left) and bool(right)
        elif node.operator == "or":
            return bool(left) or bool(right)
        elif node.operator == "..":
            return list(range(int(left), int(right)))
        elif node.operator == "&&":
            return bool(left) and bool(right)
        elif node.operator == "||":
            return bool(left) or bool(right)
        
        raise RuntimeError(f"Unknown operator: {node.operator}")

    def visit_unary_expr(self, node: UnaryExpr):
        right = node.right.accept(self)
        
        if node.operator == "-":
            return -right
        elif node.operator == "not":
            return not right
        
        raise RuntimeError(f"Unknown unary operator: {node.operator}")

    def visit_call_expr(self, node: CallExpr):
        callee = node.callee.accept(self)
        
        args = [arg.accept(self) for arg in node.arguments]
        
        if callable(callee):
            return callee(*args)
        
        if isinstance(callee, IppInstance):
            return self.call_method(callee, args)
        
        if isinstance(callee, IppClass):
            instance = IppInstance(callee)
            init_method = callee.get_method("init")
            if init_method:
                self.this_instance = instance
                self.call_function(init_method, [instance] + args)
                self.this_instance = None
            return instance
        
        if isinstance(callee, IppFunction):
            return self.call_function(callee, args)
        
        if isinstance(callee, BoundMethod):
            return self.call_function(callee.method, [callee.instance] + args)
        
        raise RuntimeError(f"Cannot call {type(callee)}")

    def call_function(self, func: IppFunction, args: List[Any]):
        new_env = Environment(func.closure)
        
        instance = args[0] if args and isinstance(args[0], IppInstance) else None
        for param, arg in zip(func.parameters, args):
            new_env.define(param, arg)
        
        saved_env = self.environment
        saved_return = self.return_value
        saved_this = getattr(self, 'this_instance', None)
        
        self.environment = new_env
        self.return_value = None
        self.this_instance = instance
        
        if instance:
            new_env.define("this", instance, constant=False)
        
        for stmt in func.body:
            stmt.accept(self)
            if self.return_value is not None:
                break
        
        self.environment = saved_env
        result = self.return_value
        self.return_value = saved_return
        self.this_instance = saved_this
        
        return result

    def visit_index_expr(self, node: IndexExpr):
        obj = node.object.accept(self)
        index = node.index.accept(self)
        
        if isinstance(obj, IppList):
            if isinstance(index, int):
                return obj.elements[index]
            if isinstance(index, float) and index.is_integer():
                return obj.elements[int(index)]
            raise RuntimeError("List index must be integer")
        if isinstance(obj, IppDict):
            return obj.get(index)
        if isinstance(obj, str):
            if isinstance(index, int):
                return obj[index]
            if isinstance(index, float) and index.is_integer():
                return obj[int(index)]
            raise RuntimeError("String index must be integer")
        
        raise RuntimeError(f"Cannot index {type(obj)}")
    
    def visit_index_set_expr(self, node: IndexSetExpr):
        obj = node.object.accept(self)
        index = node.index.accept(self)
        value = node.value.accept(self)
        
        if isinstance(obj, IppList):
            if isinstance(index, float) and index.is_integer():
                index = int(index)
            if isinstance(index, int):
                obj.elements[index] = value
                return value
            raise RuntimeError("List index must be integer")
        if isinstance(obj, IppDict):
            obj.set(index, value)
            return value
        
        raise RuntimeError(f"Cannot set index on {type(obj)}")
    
    def visit_get_expr(self, node: GetExpr):
        obj = node.object.accept(self)
        if isinstance(obj, IppInstance):
            return obj.get(node.name)
        if isinstance(obj, IppEnum):
            return obj.get(node.name)
        if isinstance(obj, IppList):
            return getattr(obj, node.name)
        if isinstance(obj, IppDict):
            return getattr(obj, node.name)
        if hasattr(obj, node.name):
            return getattr(obj, node.name)
        raise RuntimeError(f"Only instances have properties, got {type(obj)}")

    def visit_set_expr(self, node: SetExpr):
        obj = node.object.accept(self)
        value = node.value.accept(self)
        if isinstance(obj, IppInstance):
            obj.set(node.name, value)
            return value
        raise RuntimeError("Only instances have properties")

    def visit_list_literal(self, node: ListLiteral):
        result = []
        for elem in node.elements:
            if isinstance(elem, SpreadExpr):
                spread_result = elem.accept(self)
                if hasattr(spread_result, '__iter__'):
                    result.extend(spread_result)
            else:
                result.append(elem.accept(self))
        return IppList(result)

    def visit_list_comprehension(self, node: ListComprehension):
        result = []
        iterable = node.iterator.accept(self)
        
        if hasattr(iterable, '__iter__'):
            iterable = list(iterable)
        
        old_env = self.environment
        self.environment = Environment(self.environment)
        
        try:
            for item in iterable:
                self.environment.define(node.variable, item, constant=False)
                
                if node.condition:
                    cond = node.condition.accept(self)
                    if not cond:
                        continue
                
                value = node.element.accept(self)
                result.append(value)
        finally:
            self.environment = old_env
        
        return IppList(result)

    def visit_dict_comprehension(self, node: DictComprehension):
        result = {}
        iterable = node.iterator.accept(self)
        
        if hasattr(iterable, '__iter__'):
            iterable = list(iterable)
        
        old_env = self.environment
        self.environment = Environment(self.environment)
        
        try:
            for item in iterable:
                self.environment.define(node.variable, item, constant=False)
                
                if node.condition:
                    cond = node.condition.accept(self)
                    if not cond:
                        continue
                
                key = node.key.accept(self)
                value = node.value.accept(self)
                result[key] = value
        finally:
            self.environment = old_env
        
        return IppDict(result)

    def visit_dict_literal(self, node: DictLiteral):
        data = {}
        for key_node, value_node in node.entries:
            key = key_node.accept(self)
            value = value_node.accept(self)
            data[key] = value
        return IppDict(data)

    def visit_lambda_expr(self, node: LambdaExpr):
        closure = Environment(self.environment)
        return IppFunction(node.parameters, node.body, closure)

    def visit_conditional_expr(self, node: ConditionalExpr):
        condition = node.condition.accept(self)
        if condition:
            return node.then_expr.accept(self)
        else:
            return node.else_expr.accept(self)

    def visit_nullish_coalescing_expr(self, node: NullishCoalescingExpr):
        left = node.left.accept(self)
        if left is None:
            return node.right.accept(self)
        return left

    def visit_optional_chaining_expr(self, node: OptionalChainingExpr):
        obj = node.object.accept(self)
        if obj is None:
            return None
        if hasattr(obj, 'get'):
            return obj.get(node.property)
        if isinstance(obj, dict) and node.property in obj:
            return obj[node.property]
        return None

    def visit_spread_expr(self, node: SpreadExpr):
        iterable = node.iterable.accept(self)
        if hasattr(iterable, '__iter__'):
            return list(iterable)
        return []

    def visit_tuple_literal(self, node: TupleLiteral):
        return tuple(elem.accept(self) for elem in node.elements)

    def visit_unpack_expr(self, node: UnpackExpr):
        iterable = node.iterable.accept(self)
        if hasattr(iterable, '__iter__'):
            iterable = list(iterable)
        old_env = self.environment
        self.environment = Environment(self.environment)
        try:
            for i, target in enumerate(node.targets):
                if i < len(iterable):
                    self.environment.define(target, iterable[i], constant=False)
                else:
                    self.environment.define(target, None, constant=False)
        finally:
            self.environment = old_env
        return None

    def visit_var_decl(self, node: VarDecl):
        value = None
        if node.initializer:
            value = node.initializer.accept(self)
        self.environment.define(node.name, value, constant=False)

    def visit_let_decl(self, node: LetDecl):
        value = None
        if node.initializer:
            value = node.initializer.accept(self)
        # let is now mutable like var (for beginner-friendliness)
        self.environment.define(node.name, value, constant=False)

    def visit_function_decl(self, node: FunctionDecl):
        closure = Environment(self.environment)
        func = IppFunction(node.parameters, node.body, closure)
        self.environment.define(node.name, func, constant=False)

    def visit_class_decl(self, node: ClassDecl):
        methods = {}
        for method_node in node.methods:
            func = IppFunction(method_node.parameters, method_node.body, self.environment)
            if method_node.name == "init":
                func.is_init = True
                func.parameters = ["self"] + func.parameters
            methods[method_node.name] = func
        
        ipp_class = IppClass(node.name, methods)
        self.environment.define(node.name, ipp_class, constant=False)
        return None

    def visit_enum_decl(self, node: EnumDecl):
        enum_class = IppEnum(node.name, node.values)
        self.environment.define(node.name, enum_class, constant=True)
        return None

    def visit_self_expr(self, node: SelfExpr):
        return self.this_instance

    def visit_import_decl(self, node: ImportDecl):
        import os
        
        module_path = node.module_path
        if not module_path.endswith('.ipp'):
            module_path += '.ipp'
        
        base_path = getattr(self, 'current_file', None)
        if base_path:
            module_dir = os.path.dirname(base_path)
            full_path = os.path.join(module_dir, module_path)
        else:
            full_path = module_path
        
        full_path = os.path.abspath(full_path)
        
        if not os.path.exists(full_path):
            raise RuntimeError(f"Module not found: {full_path}")
        
        loading = getattr(self, '_loading_modules', set())
        if full_path in loading:
            raise RuntimeError(f"Cyclic import detected: {module_path}")
        
        if not hasattr(self, '_loaded_modules'):
            self._loaded_modules = {}
        
        if full_path in self._loaded_modules:
            module_env = self._loaded_modules[full_path]
            self._import_to_environment(module_env, node)
            return
        
        self._loading_modules = loading | {full_path}
        
        with open(full_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        from ipp.lexer.lexer import tokenize
        from ipp.parser.parser import parse
        
        saved_file = getattr(self, 'current_file', None)
        saved_env = self.global_env
        
        self.current_file = full_path
        self.global_env = Environment(self.global_env)
        
        tokens = tokenize(source)
        ast = parse(tokens)
        
        for stmt in ast.statements:
            stmt.accept(self)
        
        module_env = self.global_env
        self._loaded_modules[full_path] = module_env
        
        self.global_env = saved_env
        self.current_file = saved_file
        self._loading_modules = loading
        
        self._import_to_environment(module_env, node)
    
    def _import_to_environment(self, module_env, node):
        module_name = node.module_path.replace('.ipp', '')
        if node.imports:
            for name in node.imports:
                if module_env.has(name):
                    value = module_env.get(name)
                    self.global_env.define(name, value, constant=False)
                else:
                    raise RuntimeError(f"Module '{node.module_path}' does not export '{name}'")
        elif node.alias:
            module = IppModule(module_env, module_name)
            self.global_env.define(node.alias, module, constant=False)
        else:
            for name, value in module_env.values.items():
                self.global_env.define(name, value, constant=False)
        
        return None

    def visit_if_stmt(self, node: IfStmt):
        if node.condition.accept(self):
            for stmt in node.then_branch:
                if self.return_value is not None:
                    break
                stmt.accept(self)
        elif node.elif_branches:
            for cond, body in node.elif_branches:
                if cond.accept(self):
                    for stmt in body:
                        if self.return_value is not None:
                            break
                        stmt.accept(self)
                    return
        elif node.else_branch:
            for stmt in node.else_branch:
                if self.return_value is not None:
                    break
                stmt.accept(self)

    def visit_match_stmt(self, node: MatchStmt):
        subject_value = node.subject.accept(self)
        
        for pattern, body in node.cases:
            if pattern is None:
                for stmt in body:
                    if self.return_value is not None:
                        break
                    stmt.accept(self)
                return
            
            pattern_value = pattern.accept(self)
            if subject_value == pattern_value:
                for stmt in body:
                    if self.return_value is not None:
                        break
                    stmt.accept(self)
                return

    def visit_try_stmt(self, node: TryStmt):
        error = None
        try:
            for stmt in node.try_body:
                if self.return_value is not None:
                    break
                stmt.accept(self)
        except Exception as e:
            error = e
            if node.catch_body:
                if node.catch_var:
                    self.environment.define(node.catch_var, str(e))
                for stmt in node.catch_body:
                    if self.return_value is not None:
                        break
                    stmt.accept(self)
        finally:
            if node.finally_body:
                for stmt in node.finally_body:
                    if self.return_value is not None:
                        break
                    stmt.accept(self)
        
        if error and not node.catch_body:
            raise error

    def visit_for_stmt(self, node: ForStmt):
        iterable = node.iterator.accept(self)
        
        if isinstance(iterable, IppList):
            items = iterable.elements
        elif isinstance(iterable, range):
            items = list(iterable)
        elif isinstance(iterable, list):
            items = iterable
        else:
            raise RuntimeError(f"Cannot iterate over {type(iterable)}")
        
        saved_env = self.environment
        
        for item in items:
            if node.variable:
                new_env = Environment(saved_env)
                new_env.define(node.variable, item)
                self.environment = new_env
            else:
                self.environment = saved_env
            
            for stmt in node.body:
                if self.break_flag:
                    self.break_flag = False
                    self.environment = saved_env
                    return
                if self.continue_flag:
                    self.continue_flag = False
                    break
                stmt.accept(self)
                if self.return_value is not None:
                    self.environment = saved_env
                    return
        
        self.environment = saved_env

    def visit_while_stmt(self, node: WhileStmt):
        saved_env = self.environment
        
        while node.condition.accept(self):
            for stmt in node.body:
                if self.break_flag:
                    self.break_flag = False
                    self.environment = saved_env
                    return
                if self.continue_flag:
                    self.continue_flag = False
                    break
                stmt.accept(self)
                if self.return_value is not None:
                    self.environment = saved_env
                    return
        
        self.environment = saved_env

    def visit_do_while_stmt(self, node: DoWhileStmt):
        saved_env = self.environment
        
        while True:
            for stmt in node.body:
                if self.break_flag:
                    self.break_flag = False
                    self.environment = saved_env
                    return
                if self.continue_flag:
                    self.continue_flag = False
                stmt.accept(self)
                if self.return_value is not None:
                    self.environment = saved_env
                    return
            
            if node.condition.accept(self):
                break
        
        self.environment = saved_env

    def visit_throw_stmt(self, node: ThrowStmt):
        value = node.expression.accept(self)
        raise RuntimeError(str(value))

    def visit_with_stmt(self, node: WithStmt):
        saved_env = self.environment
        self.environment = Environment(self.environment)
        
        try:
            value = node.initializer.accept(self)
            self.environment.define(node.variable, value, constant=False)
            
            for stmt in node.body:
                stmt.accept(self)
                if self.return_value is not None:
                    break
        finally:
            self.environment = saved_env

    def visit_return_stmt(self, node: ReturnStmt):
        if node.value:
            self.return_value = node.value.accept(self)
        else:
            self.return_value = None

    def visit_break_stmt(self, node: BreakStmt):
        self.break_flag = True

    def visit_continue_stmt(self, node: ContinueStmt):
        self.continue_flag = True

    def visit_expr_stmt(self, node: ExprStmt):
        result = node.expression.accept(self)
        self.last_value = result
        return result


def interpret(program: Program, current_file: str = None) -> Any:
    interpreter = Interpreter()
    if current_file:
        interpreter.current_file = current_file
    interpreter.run(program)
    return interpreter.return_value