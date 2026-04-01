from typing import Dict, List, Any, Optional
from ..parser.ast import *
from ..runtime.builtins import BUILTINS


class IppFunction:
    def __init__(self, parameters: List[str], body: List[ASTNode], closure: 'Environment', defaults: Optional[List[ASTNode]] = None):
        self.parameters = parameters
        self.body = body
        self.closure = closure
        self.defaults = defaults or []
        self.is_init = False
    
    def __repr__(self):
        return f"<function({self.parameters})>"


class IppClass:
    def __init__(self, name: str, methods: Dict[str, IppFunction], superclass=None):
        self.name = name
        self.methods = methods
        self.superclass = superclass  # FIX: BUG-M6

    def __repr__(self):
        return f"<class {self.name}>"

    def get_method(self, name: str):
        if name in self.methods:
            return self.methods[name]
        # FIX: BUG-M6 — walk superclass chain
        if self.superclass:
            return self.superclass.get_method(name)
        return None


class IppInstance:
    def __init__(self, ipp_class: IppClass):
        self.ipp_class = ipp_class
        self.fields = {}
    
    def __repr__(self):
        return f"<{self.ipp_class.name} instance>"
    
    def __str__(self):
        str_method = self.ipp_class.get_method('__str__')
        if str_method:
            new_env = Environment(str_method.closure)
            new_env.define("self", self, constant=False)
            interp = _ipp_get_interpreter()
            if interp:
                old_env = interp.environment
                old_return = interp.return_value
                interp.environment = new_env
                interp.return_value = None
                result = None
                for stmt in str_method.body:
                    stmt.accept(interp)
                    if interp.return_value is not None:
                        result = interp.return_value
                        break
                interp.environment = old_env
                interp.return_value = old_return
                if result is not None:
                    # FIX BUG-N6: return the actual string result
                    return str(result)
        return f"<{self.ipp_class.name} instance>"
    
    def _is_private(self, name: str) -> bool:
        return name.startswith('__')
    
    def _is_internal_access(self) -> bool:
        interp = _ipp_get_interpreter()
        if interp and hasattr(interp, 'current_class'):
            return interp.current_class == self.ipp_class
        return False
    
    def get(self, name: str):
        if name in self.fields:
            if self._is_private(name) and not self._is_internal_access():
                raise RuntimeError(f"Cannot access private field '{name}' from outside class '{self.ipp_class.name}'")
            return self.fields[name]
        method = self.ipp_class.get_method(name)
        if method:
            return BoundMethod(self, method)
        raise RuntimeError(f"Undefined property: {name}")
    
    def set(self, name: str, value: Any):
        if self._is_private(name) and not self._is_internal_access():
            raise RuntimeError(f"Cannot modify private field '{name}' from outside class '{self.ipp_class.name}'")
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


class IppSet:
    def __init__(self, items: Optional[List[Any]] = None):
        self._items = set()
        if items:
            for item in items:
                self._items.add(self._hashable(item))
    
    def _hashable(self, item):
        if isinstance(item, IppList):
            return tuple(self._hashable(e) for e in item.elements)
        if isinstance(item, IppDict):
            return tuple(sorted((self._hashable(k), self._hashable(v)) for k, v in item.data.items()))
        if isinstance(item, IppSet):
            return frozenset(self._hashable(e) for e in item._items)
        return item
    
    def _unhashable(self, item):
        if isinstance(item, tuple):
            return IppList(list(item))
        if isinstance(item, frozenset):
            return IppSet(list(item))
        return item
    
    def __repr__(self):
        return "{" + ", ".join(str(self._unhashable(e)) for e in self._items) + "}"
    
    def __len__(self):
        return len(self._items)
    
    def add(self, item):
        self._items.add(self._hashable(item))
    
    def remove(self, item):
        h = self._hashable(item)
        if h in self._items:
            self._items.remove(h)
    
    def contains(self, item):
        return self._hashable(item) in self._items
    
    def len(self):
        return len(self._items)
    
    def clear(self):
        self._items = set()
    
    def union(self, other):
        result = IppSet()
        result._items = self._items.copy()
        if isinstance(other, IppSet):
            result._items |= other._items
        elif isinstance(other, list):
            for item in other:
                result._items.add(self._hashable(item))
        return result
    
    def intersection(self, other):
        result = IppSet()
        if isinstance(other, IppSet):
            result._items = self._items & other._items
        return result
    
    def difference(self, other):
        result = IppSet()
        if isinstance(other, IppSet):
            result._items = self._items - other._items
        return result
    
    def is_subset(self, other):
        other_items = other._items if isinstance(other, IppSet) else set(other)
        return self._items <= other_items
    
    def is_superset(self, other):
        other_items = other._items if isinstance(other, IppSet) else set(other)
        return self._items >= other_items


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
        self.call_stack = []
        self.call_depth = 0
        self.max_depth = max_depth
        self.current_class = None
        
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
                raise RuntimeError("Division by zero")
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
            # For Python callables, merge positional and named args
            if named_args:
                raise RuntimeError("Named arguments not supported for built-in functions")
            return callee(*args)
        
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
        
        if isinstance(callee, BoundMethod):
            # Match named arguments to method parameters
            merged_args = self._merge_named_args(callee.method, [callee.instance] + args, named_args)
            return self.call_function(callee.method, merged_args)
        
        raise RuntimeError(f"Cannot call {type(callee)}")
    
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
            
            for i in range(param_start, num_params):
                param = func.parameters[i]
                # args = [self, x, y, ...] so args[i] aligns directly with parameters[i]
                arg_idx = i
                
                if arg_idx < num_args:
                    # Use provided argument
                    new_env.define(param, args[arg_idx])
                elif defaults and i < len(defaults) and defaults[i] is not None:
                    # Use default value
                    default_val = defaults[i].accept(self)
                    new_env.define(param, default_val)
                else:
                    # No argument, no default - error
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
        # let is now mutable like var (for beginner-friendliness)
        self.environment.define(node.name, value, constant=False)

    def visit_function_decl(self, node: FunctionDecl):
        closure = Environment(self.environment)
        defaults = getattr(node, 'defaults', None) or []
        func = IppFunction(node.parameters, node.body, closure, defaults)
        self.environment.define(node.name, func, constant=False)

    def visit_class_decl(self, node: ClassDecl):
        superclass = None
        if node.superclass:
            superclass = self.environment.get(node.superclass)
            if not isinstance(superclass, IppClass):
                raise RuntimeError(f"Superclass must be a class, got: {node.superclass}")

        methods = {}
        for method_node in node.methods:
            closure = Environment(self.environment)
            params = method_node.parameters
            defaults = getattr(method_node, 'defaults', None) or []
            # ALL methods get 'self' as first param (not just init)
            if params and params[0] == "self":
                pass  # already has self
            else:
                params = ["self"] + list(params)
                defaults = [None] + list(defaults)  # self has no default
            func = IppFunction(params, method_node.body, closure, defaults)
            if method_node.name == "init":
                func.is_init = True
            methods[method_node.name] = func

        ipp_class = IppClass(node.name, methods, superclass)
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
    interpreter.run(program)
    return interpreter.return_value