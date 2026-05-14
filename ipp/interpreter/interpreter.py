from typing import Dict, List, Any, Optional
from ..parser.ast import *
from ..runtime.builtins import BUILTINS


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
        raise RuntimeError(f"Undefined variable: '{name}'")
    
    def assign(self, name: str, value: Any):
        if name in self.values:
            if self.constants.get(name, False):
                raise RuntimeError(f"Cannot reassign constant: {name}")
            self.values[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeError(f"Undefined variable: '{name}'")
    
    def has(self, name: str) -> bool:
        return name in self.values or (self.parent and self.parent.has(name))


class IppFunction:
    def __init__(self, parameters, body, closure, defaults=None):
        self.parameters = parameters
        self.body = body
        self.closure = closure
        self.defaults = defaults or []
        self.is_init = False
    
    def __repr__(self):
        return f"<function({self.parameters})>"


class IppClass:
    def __init__(self, name, methods, superclass=None, static_methods=None, properties=None):
        self.name = name
        self.methods = methods
        self.superclass = superclass
        self.static_methods = static_methods or {}
        self.properties = properties or {}
    
    def __repr__(self):
        return f"<class {self.name}>"
    
    def get_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.get_method(name)
        return None
    
    def get_static_method(self, name):
        return self.static_methods.get(name)
    
    def get_property(self, name):
        if name in self.properties:
            return self.properties[name]
        if self.superclass:
            return self.superclass.get_property(name)
        return None


class IppInstance:
    def __init__(self, ipp_class):
        self.ipp_class = ipp_class
        self.fields = {}
    
    def __repr__(self):
        repr_method = self.ipp_class.get_method('__repr__')
        if repr_method:
            new_env = Environment(repr_method.closure)
            new_env.define("self", self, constant=False)
            interp = _ipp_get_interpreter()
            if interp:
                saved = interp.environment
                interp.environment = new_env
                try:
                    for stmt in repr_method.body:
                        stmt.accept(interp)
                        if interp.return_value is not None:
                            return str(interp.return_value)
                finally:
                    interp.environment = saved
        return f"<{self.ipp_class.name} instance>"
    
    def __len__(self):
        # FIX v1.7.8.3: Check for __len__ method
        len_method = self.ipp_class.get_method('__len__')
        if len_method:
            new_env = Environment(len_method.closure)
            new_env.define("self", self, constant=False)
            interp = _ipp_get_interpreter()
            if interp:
                saved = interp.environment
                interp.environment = new_env
                try:
                    for stmt in len_method.body:
                        stmt.accept(interp)
                        if interp.return_value is not None:
                            return interp.return_value
                finally:
                    interp.environment = saved
        raise TypeError(f"len() not supported for {self.ipp_class.name}")
    
    def __str__(self):
        str_method = self.ipp_class.get_method('__str__')
        if str_method:
            new_env = Environment(str_method.closure)
            new_env.define("self", self, constant=False)
            interp = _ipp_get_interpreter()
            if interp:
                saved = interp.environment
                interp.environment = new_env
                try:
                    for stmt in str_method.body:
                        stmt.accept(interp)
                        if interp.return_value is not None:
                            return str(interp.return_value)
                finally:
                    interp.environment = saved
        return self.__repr__()
    
    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        prop = self.ipp_class.get_property(name)
        if prop and prop.getter:
            return self._execute_property_getter(prop)
        method = self.ipp_class.get_method(name)
        if method:
            return BoundMethod(self, method)
        raise AttributeError(f"'{self.ipp_class.name}' object has no attribute '{name}'")
    
    def _execute_property_getter(self, prop):
        new_env = Environment(prop.getter.closure)
        new_env.define("self", self, constant=False)
        interp = _ipp_get_interpreter()
        if interp:
            saved = interp.environment
            saved_ret = interp.return_value
            interp.environment = new_env
            interp.return_value = None
            try:
                for stmt in prop.getter.body:
                    stmt.accept(interp)
                return interp.return_value
            finally:
                interp.environment = saved
                interp.return_value = saved_ret
        return None
    
    def set(self, name, value):
        prop = self.ipp_class.get_property(name)
        if prop and prop.setter:
            self._execute_property_setter(prop, value)
            return
        self.fields[name] = value
    
    def _execute_property_setter(self, prop, value):
        new_env = Environment(prop.setter.closure)
        new_env.define("self", self, constant=False)
        new_env.define("v", value, constant=False)
        interp = _ipp_get_interpreter()
        if interp:
            saved = interp.environment
            saved_ret = interp.return_value
            interp.environment = new_env
            interp.return_value = None
            try:
                for stmt in prop.setter.body:
                    stmt.accept(interp)
            finally:
                interp.environment = saved
                interp.return_value = saved_ret
    
    def get_method(self, name):
        return self.ipp_class.get_method(name)


class IppProperty:
    def __init__(self, name, getter, setter, closure):
        self.name = name
        self.getter = getter
        self.setter = setter
        self.closure = closure


class IppSignal:  # v1.6.6 signal/event
    def __init__(self, name):
        self.name = name
        self.handlers = []
    
    def connect(self, handler):
        self.handlers.append(handler)
    
    def emit(self, *args):
        for handler in self.handlers:
            if callable(handler):
                handler(*args)
    
    def __repr__(self):
        return f"Signal({self.name})"


class IppEnum:
    def __init__(self, name, values):
        self.name = name
        # Convert list to dict if needed
        if isinstance(values, list):
            self.values = {v: v for v in values}
        else:
            self.values = values
    
    def __repr__(self):
        return f"<enum {self.name}>"
    
    def get(self, name):
        if name in self.values:
            return self.values[name]
        raise RuntimeError(f"Enum {self.name} has no value '{name}'")


class IppModule:
    def __init__(self, env, name):
        self.env = env
        self.name = name
    
    def __repr__(self):
        return f"<module {self.name}>"
    
    def get(self, name):
        if self.env.has(name):
            return self.env.get(name)
        raise AttributeError(f"module '{self.name}' has no attribute '{name}'")


class IppSet:
    def __init__(self, items=None):
        self._items = set(items) if items else set()
    
    def add(self, item):
        self._items.add(item)
    
    def remove(self, item):
        self._items.discard(item)
    
    def contains(self, item):
        return item in self._items
    
    def len(self):
        return len(self._items)
    
    def clear(self):
        self._items.clear()
    
    def __repr__(self):
        return f"{{{', '.join(repr(i) for i in self._items)}}}"


class BoundMethod:
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method
    
    def __repr__(self):
        return f"<bound method {self.method}>"


class IppList:
    def __init__(self, elements=None):
        self.elements = list(elements) if elements is not None else []
    
    def __repr__(self):
        return f"[{', '.join(repr(e) for e in self.elements)}]"
    
    def __iter__(self):
        return iter(self.elements)
    
    def __len__(self):
        return len(self.elements)
    
    def __getitem__(self, key):
        return self.elements[key]
    
    def __setitem__(self, key, value):
        self.elements[key] = value
    
    def __eq__(self, other):
        if isinstance(other, IppList):
            return self.elements == other.elements
        if isinstance(other, list):
            return self.elements == other
        return NotImplemented
    
    def __hash__(self):
        return None  # unhashable like list
    
    def append(self, item):
        self.elements.append(item)
    
    def pop(self, index=-1):
        return self.elements.pop(index)
    
    def insert(self, index, item):
        self.elements.insert(index, item)
    
    # v1.6.12 - fluent list methods
    def map(self, fn):
        result = []
        for elem in self.elements:
            result.append(fn(elem))
        return result
    
    def filter(self, fn):
        result = []
        for elem in self.elements:
            if fn(elem):
                result.append(elem)
        return result
    
    def reduce(self, fn, init):
        acc = init
        for elem in self.elements:
            acc = fn(acc, elem)
        return acc
    
    def sort(self):
        self.elements.sort()
    
    def reverse(self):
        self.elements.reverse()
    
    def remove(self, item):
        self.elements.remove(item)


class IppDict:
    def __init__(self, data=None):
        self.data = data or {}
    
    def __repr__(self):
        return f"{{{', '.join(f'{repr(k)}: {repr(v)}' for k, v in self.data.items())}}}"
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value


_ipp_current_interpreter = None


def _ipp_set_interpreter(interp):
    global _ipp_current_interpreter
    _ipp_current_interpreter = interp


def _ipp_get_interpreter():
    return _ipp_current_interpreter


class Interpreter:
    def __init__(self, max_depth: int = 1000):
        global _ipp_current_interpreter
        _ipp_current_interpreter = self
        self.global_env = Environment()
        self.environment = self.global_env
        self.return_value = None
        self.last_value = None
        self.break_flag = False
        self.continue_flag = False
        self.current_line = 0
        self.current_file = None
        self.call_stack = []
        self.call_depth = 0
        self.max_depth = max_depth
        self.current_class = None
        self.yield_flag = False
        self._gen_yield_count = 0
        self._gen_target_yield = 0
        
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
                file_info = f" in {self.current_file}" if self.current_file else ""
                raise RuntimeError(f"Error at line {self.current_line}{file_info} in {stack_info}: {e}")
            raise

    def _get_suggestion(self, name: str, known_names: list) -> str:
        """Suggest similar names for typos"""
        if not known_names:
            return ""
        
        # Simple Levenshtein-like suggestion
        def similarity(a, b):
            if a == b:
                return 1.0
            if a in b or b in a:
                return 0.8
            # Check first character match
            if a and b and a[0] == b[0]:
                return 0.5
            return 0.0
        
        best_match = None
        best_score = 0
        
        for known in known_names:
            score = similarity(name.lower(), known.lower())
            if score > best_score and score > 0.3:
                best_score = score
                best_match = known
        
        if best_match:
            return f". Did you mean '{best_match}'?"
        return ""

    def run_safe(self, program: Program):
        try:
            self.run(program)
        except Exception as e:
            print(f"Runtime error: {e}")

    def execute(self, stmt: ASTNode):
        self.current_line = getattr(stmt, 'line', 0) or 0
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
        self.current_line = getattr(node, 'line', 0) or 0
        return self.environment.get(node.name)

    def visit_assign_expr(self, node: AssignExpr):
        value = node.value.accept(self)
        self.environment.assign(node.name, value)
        return value

    def visit_binary_expr(self, node: BinaryExpr):
        # FIX: and/or must short-circuit — evaluate left first, then decide on right
        if node.operator == "and":
            left = node.left.accept(self)
            return left if not bool(left) else node.right.accept(self)
        if node.operator == "or":
            left = node.left.accept(self)
            return left if bool(left) else node.right.accept(self)

        left = node.left.accept(self)
        right = node.right.accept(self)
        
        def _ipp_has_method(obj, method_name):
            """Check if IppInstance has a method (not Python's dunder methods)."""
            if isinstance(obj, IppInstance):
                method = obj.ipp_class.get_method(method_name)
                return method is not None
            return False
        
        def _ipp_call_method(obj, method_name, arg):
            """Call an IppInstance method."""
            method = obj.ipp_class.get_method(method_name)
            if method:
                bound = BoundMethod(obj, method)
                return self.call_function(bound.method, [obj, arg])
            raise RuntimeError(f"Undefined method: {method_name}")
        
        if node.operator == "+":
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, IppList) and isinstance(right, IppList):
                return IppList(left.elements + right.elements)
            if _ipp_has_method(left, '__add__'):
                return _ipp_call_method(left, '__add__', right)
            if isinstance(left, (int, float, str)):
                return str(left) + str(right)
            return left + right
        elif node.operator == "-":
            if _ipp_has_method(left, '__sub__'):
                return _ipp_call_method(left, '__sub__', right)
            return left - right
        elif node.operator == "*":
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left * right
            if _ipp_has_method(left, '__mul__'):
                return _ipp_call_method(left, '__mul__', right)
            return left * right
        elif node.operator == "/":
            if right == 0:
                raise RuntimeError("Division by zero: cannot divide by 0")
            if _ipp_has_method(left, '__truediv__'):
                return _ipp_call_method(left, '__truediv__', right)
            return left / right
        elif node.operator == "==":
            if _ipp_has_method(left, '__eq__'):
                return _ipp_call_method(left, '__eq__', right)
            return left == right
        elif node.operator == "!=":
            if _ipp_has_method(left, '__ne__'):
                return _ipp_call_method(left, '__ne__', right)
            return left != right
        elif node.operator == "<":
            if _ipp_has_method(left, '__lt__'):
                return _ipp_call_method(left, '__lt__', right)
            return left < right
        elif node.operator == ">":
            if _ipp_has_method(left, '__gt__'):
                return _ipp_call_method(left, '__gt__', right)
            return left > right
        elif node.operator == "<=":
            if _ipp_has_method(left, '__le__'):
                return _ipp_call_method(left, '__le__', right)
            return left <= right
        elif node.operator == ">=":
            if _ipp_has_method(left, '__ge__'):
                return _ipp_call_method(left, '__ge__', right)
            return left >= right
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
        elif node.operator == "and":
            return left if not bool(left) else right
        elif node.operator == "or":
            return left if bool(left) else right
        elif node.operator == "..":
            return list(range(int(left), int(right)))
        
        raise RuntimeError(f"Unknown operator: {node.operator}")

    def visit_unary_expr(self, node: UnaryExpr):
        right = node.right.accept(self)
        if node.operator == "-":
            return -right
        elif node.operator in ("not", "!"):
            return not bool(right)
        elif node.operator == "~":
            return ~int(right)
        raise RuntimeError(f"Unknown unary operator: {node.operator}")

    def visit_call_expr(self, node: CallExpr):
        callee = node.callee.accept(self)
        
        # Evaluate positional arguments
        args = [arg.accept(self) for arg in node.arguments]
        
        # Evaluate named arguments
        named_args = {}
        for named_arg in node.named_arguments:
            named_args[named_arg.name] = named_arg.value.accept(self)
        
        if callable(callee):
            # For Python callables, support both positional and named args
            if named_args:
                try:
                    return callee(*args, **named_args)
                except TypeError:
                    return callee(*args)
            return callee(*args)

        # FIX: IppList returned from a builtin (e.g. items(d)) is not callable
        if isinstance(callee, IppList):
            raise RuntimeError(
                "Cannot call a list as a function. "
                "Store the result first: var tmp = items(d); len(tmp)"
            )

        if isinstance(callee, IppInstance):
            return self.call_method(callee, args)
        
        if isinstance(callee, IppClass):
            instance = IppInstance(callee)
            init_method = callee.get_method("init")
            if init_method:
                # Match named arguments to init parameters
                merged_args = self._merge_named_args(init_method, [instance] + args, named_args)
                self.call_function(init_method, merged_args)
            return instance
        
        if isinstance(callee, IppFunction):
            # Match named arguments to function parameters
            merged_args = self._merge_named_args(callee, args, named_args)
            return self.call_function(callee, merged_args)
        
        if isinstance(callee, IppGenerator):
            # Calling a generator function returns a new generator instance
            # with the provided arguments bound
            new_gen = IppGenerator(callee.parameters, callee.body, callee.closure, callee.func_name)
            # Store arguments for later binding when __next__ is called
            new_gen._pending_args = args
            return new_gen
        
        if isinstance(callee, BoundMethod):
            # Match named arguments to method parameters
            merged_args = self._merge_named_args(callee.method, [callee.instance] + args, named_args)
            return self.call_function(callee.method, merged_args)
        
        raise RuntimeError(f"Cannot call '{type(callee).__name__}'. Expected function, class, or method.")
    
    def _merge_named_args(self, func, positional_args, named_args):
        """Merge positional and named arguments into a final argument list. FIX: BUG-NEW-M4"""
        if not named_args:
            return positional_args
        
        params = func.parameters
        result = list(positional_args)
        
        # Fill in named arguments at their parameter positions
        for name, value in named_args.items():
            if name in params:
                param_idx = params.index(name)
                # Extend result list if needed
                while len(result) <= param_idx:
                    result.append(None)
                result[param_idx] = value
            else:
                raise RuntimeError(f"Unknown named argument: {name}")
        
        return result

    def call_function(self, func: IppFunction, args: List[Any]):
        # FIX BUG-NEW-N2: Check recursion depth
        self.call_depth += 1
        if self.call_depth > self.max_depth:
            self.call_depth -= 1
            raise RuntimeError(f"Maximum recursion depth ({self.max_depth}) exceeded. Possible infinite recursion.")
        
        try:
            new_env = Environment(func.closure)

            instance = None
            param_start = 0
            owning_class = None
            if func.parameters and func.parameters[0] == "self":
                if args and isinstance(args[0], IppInstance):
                    instance = args[0]
                    new_env.define("self", instance, constant=False)
                    param_start = 1
                    owning_class = instance.ipp_class

            # Fill in parameters with provided args, then defaults
            defaults = getattr(func, 'defaults', None) or []
            num_params = len(func.parameters)
            num_args = len(args)
            
            # Check for variadic parameter
            variadic_idx = None
            for i, p in enumerate(func.parameters):
                if p.startswith("..."):
                    variadic_idx = i
                    break
            
            for i in range(param_start, num_params):
                param = func.parameters[i]
                
                if variadic_idx is not None and i == variadic_idx:
                    # Variadic: collect all remaining args
                    param_name = param[3:]  # remove "..."
                    arg_idx = i - param_start
                    if arg_idx < num_args:
                        extra_args = args[arg_idx:]
                    else:
                        extra_args = []
                    new_env.define(param_name, IppList(extra_args))
                else:
                    arg_idx = i
                    if arg_idx < num_args:
                        new_env.define(param, args[arg_idx])
                    elif defaults and i < len(defaults) and defaults[i] is not None:
                        default_val = defaults[i].accept(self)
                        new_env.define(param, default_val)
                    else:
                        raise RuntimeError(f"Missing required argument: {param}")

            saved_env = self.environment
            saved_return = self.return_value
            saved_this = getattr(self, 'this_instance', None)
            saved_class = getattr(self, 'current_class', None)

            self.environment = new_env
            self.return_value = None
            self.this_instance = instance
            self.current_class = owning_class

            for stmt in func.body:
                stmt.accept(self)
                if self.return_value is not None:
                    break

            self.environment = saved_env
            result = self.return_value
            self.return_value = saved_return
            self.this_instance = saved_this
            self.current_class = saved_class
        finally:
            self.call_depth -= 1

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
            raise RuntimeError(f"String index must be integer, got {type(index).__name__}")
        
        raise RuntimeError(f"Cannot index '{type(obj).__name__}'. Only list, dict, string support indexing.")
    
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
            raise RuntimeError(f"List index must be integer, got {type(index).__name__}")
        if isinstance(obj, IppDict):
            obj.set(index, value)
            return value
        
        raise RuntimeError(f"Cannot set index on '{type(obj).__name__}'. Only list and dict support index assignment.")
    
    def visit_get_expr(self, node: GetExpr):
        obj = node.object.accept(self)
        if isinstance(obj, IppInstance):
            return obj.get(node.name)
        if isinstance(obj, IppEnum):
            return obj.get(node.name)
        if isinstance(obj, IppModule):
            return obj.get(node.name)
        if isinstance(obj, IppList):
            return getattr(obj, node.name)
        if isinstance(obj, IppDict):
            return getattr(obj, node.name)
        # FIX v1.5.26: Allow static method access on IppClass
        if isinstance(obj, IppClass):
            method = obj.get_static_method(node.name)
            if method:
                return method
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

    def visit_fstring_expr(self, node: FStringExpr):
        parts = []
        for seg in node.segments:
            val = seg.accept(self)
            parts.append(str(val))
        return ''.join(parts)

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
        defaults = getattr(node, 'defaults', None) or []
        return IppFunction(node.parameters, node.body, closure, defaults)

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


    def visit_super_expr(self, node):
        """FIX: BUG-C5 — handle super.method()"""
        instance = self.this_instance
        if instance is None:
            raise RuntimeError("'super' used outside of a class method")
        superclass = instance.ipp_class.superclass
        if superclass is None:
            raise RuntimeError(f"Class '{instance.ipp_class.name}' has no superclass")
        method = superclass.get_method(node.method)
        if method is None:
            raise RuntimeError(f"Superclass has no method '{node.method}'")
        return BoundMethod(instance, method)

    def visit_compound_assign_expr(self, node):
        """FIX: DESIGN-1 — +=, -=, *=, /=, %="""
        current = self.environment.get(node.name)
        rhs = node.value.accept(self)
        ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b,
               '*': lambda a,b: a*b, '/': lambda a,b: a/b, '%': lambda a,b: a%b}
        result = ops[node.operator](current, rhs)
        self.environment.assign(node.name, result)
        return result

    def visit_compound_set_expr(self, node):
        """FIX: DESIGN-1 — obj.field += val"""
        obj = node.object.accept(self)
        rhs = node.value.accept(self)
        ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b,
               '*': lambda a,b: a*b, '/': lambda a,b: a/b, '%': lambda a,b: a%b}
        if isinstance(obj, IppInstance):
            current = obj.fields.get(node.name)
            result = ops[node.operator](current, rhs)
            obj.set(node.name, result)
            return result
        raise RuntimeError(f"Cannot compound-assign property on {type(obj)}")

    def visit_index_compound_set_expr(self, node):
        """FIX: DESIGN-1 — obj[i] += val"""
        obj = node.object.accept(self)
        index = node.index.accept(self)
        rhs = node.value.accept(self)
        ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b,
               '*': lambda a,b: a*b, '/': lambda a,b: a/b, '%': lambda a,b: a%b}
        if isinstance(obj, IppList):
            idx = int(index)
            result = ops[node.operator](obj.elements[idx], rhs)
            obj.elements[idx] = result
            return result
        if isinstance(obj, IppDict):
            result = ops[node.operator](obj.data.get(index), rhs)
            obj.data[index] = result
            return result
        raise RuntimeError(f"Cannot compound-assign index on {type(obj)}")

    def visit_labeled_stmt(self, node):
        node.statement.accept(self)

    def visit_var_decl(self, node: VarDecl):
        value = None
        if node.initializer:
            value = node.initializer.accept(self)
        self.environment.define(node.name, value, constant=False)

    def visit_multi_var_decl(self, node: MultiVarDecl):
        """Multiple variable declaration: var a, b = expr FIX: BUG-NEW-M7"""
        value = node.initializer.accept(self)
        
        # Handle different types of initializers
        if isinstance(value, (list, tuple)):
            elements = list(value)
        elif isinstance(value, IppList):
            elements = value.elements
        else:
            raise RuntimeError(f"Cannot unpack {type(value)} into multiple variables")
        
        if len(elements) != len(node.names):
            raise RuntimeError(f"Expected {len(node.names)} values, got {len(elements)}")
        
        for name, elem in zip(node.names, elements):
            self.environment.define(name, elem, constant=False)

    def visit_let_decl(self, node: LetDecl):
        value = None
        if node.initializer:
            value = node.initializer.accept(self)
        # FIX v1.5.26: let is immutable
        self.environment.define(node.name, value, constant=True)

    def visit_function_decl(self, node: FunctionDecl):
        closure = Environment(self.environment)
        defaults = getattr(node, 'defaults', None) or []
        
        # Check if function body contains yield - if so, it's a generator
        has_yield = self._check_for_yield(node.body)
        if has_yield:
            func = IppGenerator(node.parameters, node.body, closure, node.name)
        else:
            func = IppFunction(node.parameters, node.body, closure, defaults)
        
        # v1.6.2 - apply decorator if present
        if node.decorator:
            decorator_fn = self.execute(node.decorator)
            if hasattr(decorator_fn, 'call'):
                func = decorator_fn.call([func], {})
        
        self.environment.define(node.name, func, constant=False)
    
    def _check_for_yield(self, body):
        """Check if a body contains yield expressions"""
        for stmt in body:
            if self._stmt_has_yield(stmt):
                return True
        return False
    
    def _stmt_has_yield(self, stmt):
        """Check if a statement contains yield"""
        if isinstance(stmt, ExprStmt):
            return self._expr_has_yield(stmt.expression)
        if isinstance(stmt, IfStmt):
            if self._stmt_has_yield(stmt.then_branch[0]) if stmt.then_branch else False:
                return True
            for _, branch in stmt.elif_branches:
                if self._stmt_has_yield(branch[0]) if branch else False:
                    return True
            if stmt.else_branch and self._stmt_has_yield(stmt.else_branch[0]):
                return True
        if isinstance(stmt, (ForStmt, WhileStmt)):
            if stmt.body and self._stmt_has_yield(stmt.body[0]):
                return True
        return False
    
    def _expr_has_yield(self, expr):
        """Check if an expression contains yield"""
        if isinstance(expr, YieldExpr):
            return True
        if isinstance(expr, CallExpr):
            return self._expr_has_yield(expr.callee) or any(self._expr_has_yield(a) for a in expr.arguments)
        if isinstance(expr, BinaryExpr):
            return self._expr_has_yield(expr.left) or self._expr_has_yield(expr.right)
        if isinstance(expr, UnaryExpr):
            return self._expr_has_yield(expr.right)
        return False

    def visit_class_decl(self, node: ClassDecl):
        superclass = None
        if node.superclass:
            superclass = self.environment.get(node.superclass)
            if not isinstance(superclass, IppClass):
                raise RuntimeError(f"Superclass must be a class, got: {node.superclass}")

        methods = {}
        static_methods = {}
        properties = {}
        
        for method_node in node.methods:
            closure = Environment(self.environment)
            params = method_node.parameters
            defaults = getattr(method_node, 'defaults', None) or []
            
            if getattr(method_node, 'is_static', False):
                func = IppFunction(params, method_node.body, closure, defaults)
                static_methods[method_node.name] = func
                continue
            
            if params and params[0] == "self":
                pass
            else:
                params = ["self"] + list(params)
                defaults = [None] + list(defaults)
            func = IppFunction(params, method_node.body, closure, defaults)
            if method_node.name == "init":
                func.is_init = True
            methods[method_node.name] = func
        
        for prop_node in getattr(node, 'properties', []):
            closure = Environment(self.environment)
            prop = IppProperty(prop_node.name, prop_node.getter, prop_node.setter, closure)
            properties[prop_node.name] = prop

        ipp_class = IppClass(node.name, methods, superclass, static_methods, properties)
        self.environment.define(node.name, ipp_class, constant=False)
        return None

    def visit_enum_decl(self, node: EnumDecl):
        enum_class = IppEnum(node.name, node.values)
        self.environment.define(node.name, enum_class, constant=True)
        return None

    def visit_self_expr(self, node: SelfExpr):
        # FIX: check environment first (self is defined as first local param)
        try:
            val = self.environment.get("self")
            if val is not None:
                return val
        except RuntimeError:
            pass
        if self.this_instance is not None:
            return self.this_instance
        raise RuntimeError("'self' used outside of a class method")

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
        else:
            if node.elif_branches:
                for cond, body in node.elif_branches:
                    if cond.accept(self):
                        for stmt in body:
                            if self.return_value is not None:
                                break
                            stmt.accept(self)
                        return
            if node.else_branch:
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

    def visit_match_expr(self, node: MatchExpr):
        subject_value = node.subject.accept(self)
        
        for pattern, body in node.cases:
            if pattern is None:
                if not body:
                    return None
                result = None
                for stmt in body:
                    if isinstance(stmt, ExprStmt):
                        result = stmt.expression.accept(self)
                    else:
                        stmt.accept(self)
                return result
            
            pattern_value = pattern.accept(self)
            if subject_value == pattern_value:
                if not body:
                    return None
                result = None
                for stmt in body:
                    if isinstance(stmt, ExprStmt):
                        result = stmt.expression.accept(self)
                    else:
                        stmt.accept(self)
                return result
        return None

    def visit_try_stmt(self, node: TryStmt):
        error = None
        try:
            for stmt in node.try_body:
                if self.return_value is not None:
                    break
                stmt.accept(self)
        except Exception as e:
            error = e
        
        # Handle multiple catch blocks with types
        if error and node.catches:
            error_str = str(error)
            for catch_type, catch_var, catch_body in node.catches:
                if error:
                    # Check if typed catch matches
                    if catch_type:
                        # Check if error matches the type (error_str starts with TypeName:)
                        if error_str.startswith(catch_type + ":"):
                            if catch_var:
                                self.environment.define(catch_var, error_str)
                            for stmt in catch_body:
                                if self.return_value is not None:
                                    break
                                stmt.accept(self)
                            error = None  # caught
                            break
                    else:
                        # Untyped catch - catches all
                        if catch_var:
                            self.environment.define(catch_var, error_str)
                        for stmt in catch_body:
                            if self.return_value is not None:
                                break
                            stmt.accept(self)
                        error = None  # caught
                        break
        
        # Finally block
        if node.finally_body:
            for stmt in node.finally_body:
                if self.return_value is not None:
                    break
                stmt.accept(self)
        
        if error:
            raise error

    def visit_for_stmt(self, node: ForStmt):
        iterable = node.iterator.accept(self)
        
        if isinstance(iterable, IppList):
            items = iterable.elements
        elif isinstance(iterable, range):
            items = list(iterable)
        elif isinstance(iterable, list):
            items = iterable
        elif isinstance(iterable, str):
            # FIX: iterate over characters of a string
            items = list(iterable)
        elif isinstance(iterable, IppDict):
            # iterate over dict keys
            items = list(iterable.data.keys())
        elif isinstance(iterable, dict):
            items = list(iterable.keys())
        elif hasattr(iterable, '__iter__') and hasattr(iterable, '__next__'):
            # Generator support
            items = list(iterable)
        elif hasattr(iterable, '__iter__'):
            items = list(iterable)
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
                # Check for yield in generator context - DON'T restore env
                if self.yield_flag:
                    return  # Keep current environment for generator resume
        
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
            
            if not node.condition.accept(self):
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
        self._return_flag = True

    def visit_assert_stmt(self, node: AssertStmt):
        cond = node.condition.accept(self)
        if not cond:
            msg = "Assertion failed"
            if node.message:
                msg = node.message.accept(self)
            raise RuntimeError(str(msg))

    def visit_break_stmt(self, node: BreakStmt):
        self.break_flag = True

    def visit_continue_stmt(self, node: ContinueStmt):
        self.continue_flag = True

    def visit_expr_stmt(self, node: ExprStmt):
        result = node.expression.accept(self)
        self.last_value = result
        return result

    def visit_yield_expr(self, node: YieldExpr):
        """Yield expression - pauses execution and returns value"""
        value = node.value.accept(self) if node.value else None
        self.return_value = value
        self.yield_flag = True
        
        # Track yield count for generator resumption
        current_count = getattr(self, '_gen_yield_count', 0)
        self._gen_yield_count = current_count + 1
        target = getattr(self, '_gen_target_yield', 0)
        
        if current_count < target:
            # Not the target yield yet - continue execution
            self.yield_flag = False
            self.return_value = None
            return value
        else:
            # This is the target yield - stop execution
            return value

    def visit_await_expr(self, node: AwaitExpr):
        """Await expression - yields control to event loop"""
        value = node.expression.accept(self)
        # If it's a sleep call, actually sleep
        if isinstance(value, bool) and value is True:
            pass  # sleep already happened
        self.return_value = value
        self.yield_flag = True
        return value

    def visit_async_func_decl(self, node: AsyncFuncDecl):
        """Async function declaration"""
        closure = Environment(self.environment)
        func = IppCoroutine(node.parameters, node.body, closure, node.name)
        self.environment.define(node.name, func, constant=False)

    def _make_python_generator(self, generator):
        """Legacy - not used anymore"""
        pass
    
    def _execute_gen_body(self, body):
        """Execute generator body, stopping at the target yield count"""
        for stmt in body:
            self.yield_flag = False
            self.return_value = None
            
            try:
                stmt.accept(self)
            except:
                if self.yield_flag:
                    return  # Yield was hit
                raise
            
            if self.yield_flag:
                return  # Yield was hit


class IppGenerator:
    """Generator object for yield-based generators"""
    def __init__(self, parameters, body, closure, func_name="<generator>"):
        self.parameters = parameters
        self.body = body
        self.closure = closure
        self.func_name = func_name
        self._done = False
        self._yield_count = 0  # Number of yields already consumed
        self._env = None
        self._pending_args = []  # Arguments passed when generator was called
    
    def __repr__(self):
        return f"<generator {self.func_name}>"
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._done:
            raise StopIteration
        
        interp = _ipp_get_interpreter()
        if interp is None:
            raise RuntimeError("No interpreter available for generator")
        
        if self._env is None:
            # First call - set up environment with arguments
            self._env = Environment(self.closure)
            for i, param in enumerate(self.parameters):
                if i < len(self._pending_args):
                    self._env.define(param, self._pending_args[i], constant=False)
                else:
                    self._env.define(param, None, constant=False)
            self._pending_args = []  # Clear pending args after first use
        
        # Execute generator body, tracking yields
        saved_env = interp.environment
        saved_return = interp.return_value
        saved_yield = getattr(interp, 'yield_flag', False)
        
        interp.environment = self._env
        interp.return_value = None
        interp.yield_flag = False
        interp._gen_yield_count = 0
        interp._gen_target_yield = self._yield_count
        
        try:
            interp._execute_gen_body(self.body)
            
            if interp.yield_flag:
                # A yield was hit at the right count
                self._yield_count += 1
                result = interp.return_value
                interp.return_value = saved_return
                interp.yield_flag = saved_yield
                interp.environment = saved_env
                return result
            else:
                # No yield at target count - generator is done
                self._done = True
                interp.return_value = saved_return
                interp.yield_flag = saved_yield
                interp.environment = saved_env
                raise StopIteration
        except StopIteration:
            self._done = True
            interp.return_value = saved_return
            interp.yield_flag = saved_yield
            interp.environment = saved_env
            raise


class IppCoroutine:
    """Coroutine object for async/await"""
    def __init__(self, parameters, body, closure, func_name="<coroutine>"):
        self.parameters = parameters
        self.body = body
        self.closure = closure
        self.func_name = func_name
        self._done = False
        self._result = None
        self._env = None
        self._pending_args = []
        self._stmt_idx = 0  # Track execution position
    
    def __repr__(self):
        return f"<coroutine {self.func_name}>"
    
    def __call__(self, *args):
        """Calling a coroutine function creates a new coroutine instance"""
        new_coro = IppCoroutine(self.parameters, self.body, self.closure, self.func_name)
        new_coro._pending_args = list(args)
        return new_coro
    
    def __await__(self):
        return self
    
    def result(self):
        return self._result


class IppEventLoop:
    """Simple event loop for async/await"""
    def __init__(self, interp):
        self.interp = interp
        self._tasks = []
        self._time = 0
    
    def create_task(self, coro):
        self._tasks.append(coro)
        return coro
    
    def run_until_complete(self, coro):
        self._tasks.append(coro)
        max_iterations = 10000  # Prevent infinite loops
        iteration = 0
        while self._tasks and iteration < max_iterations:
            iteration += 1
            task = self._tasks.pop(0)
            if task._done:
                continue
            try:
                result = self._run_coro_step(task)
                if result is not None:
                    # Re-add task - it yielded
                    self._tasks.append(task)
            except StopIteration:
                pass
        return coro._result
    
    def _run_coro_step(self, coro):
        if coro._env is None:
            coro._env = Environment(coro.closure)
            for i, param in enumerate(coro.parameters):
                if i < len(coro._pending_args):
                    coro._env.define(param, coro._pending_args[i], constant=False)
                else:
                    coro._env.define(param, None, constant=False)
            coro._pending_args = []
        
        interp = self.interp
        saved_env = interp.environment
        interp.environment = coro._env
        
        # Execute from current statement index
        body = coro.body
        idx = coro._stmt_idx
        
        while idx < len(body):
            stmt = body[idx]
            coro._stmt_idx = idx + 1
            
            # Don't reset return_value if _return_flag is set
            if not getattr(interp, '_return_flag', False):
                interp.yield_flag = False
                interp.return_value = None
            
            try:
                stmt.accept(interp)
            except Exception as e:
                if interp.yield_flag:
                    result = interp.return_value
                    interp.yield_flag = False
                    interp.environment = saved_env
                    return result
                raise
            
            if interp.yield_flag:
                result = interp.return_value
                interp.yield_flag = False
                interp.environment = saved_env
                return result
            
            # Check if return was set (function/coroutine completed)
            if getattr(interp, '_return_flag', False):
                coro._done = True
                coro._result = interp.return_value
                interp._return_flag = False
                interp.environment = saved_env
                return None
            
            idx = coro._stmt_idx
        
        # Coroutine completed
        coro._done = True
        coro._result = interp.return_value
        interp.environment = saved_env
        return None


def ipp_sleep(seconds):
    """Sleep for given seconds (awaitable)"""
    import time
    time.sleep(float(seconds))
    return True

def ipp_async_run(coro):
    """Run an async coroutine"""
    from ipp.interpreter.interpreter import IppCoroutine, IppEventLoop, _ipp_get_interpreter
    if isinstance(coro, IppCoroutine):
        interp = _ipp_get_interpreter()
        loop = IppEventLoop(interp)
        return loop.run_until_complete(coro)
    raise RuntimeError("async_run() expects a coroutine")

def ipp_create_task(coro):
    """Create a task from coroutine"""
    from ipp.interpreter.interpreter import IppCoroutine, IppEventLoop, _ipp_get_interpreter
    if isinstance(coro, IppCoroutine):
        interp = _ipp_get_interpreter()
        loop = IppEventLoop(interp)
        loop.create_task(coro)
        return loop.run_until_complete(coro)
    raise RuntimeError("create_task() expects a coroutine")

def ipp_is_coroutine(obj):
    """Check if object is a coroutine"""
    from ipp.interpreter.interpreter import IppCoroutine
    return isinstance(obj, IppCoroutine)


def interpret(program: Program, current_file: str = None) -> Any:
    interpreter = Interpreter()
    if current_file:
        interpreter.current_file = current_file
    interpreter.run(program)
    return interpreter.return_value
    interpreter.run(program)
    return interpreter.return_value