from .bytecode import Chunk, OpCode, opcode_size
from .compiler import FunctionProto
from typing import List, Any, Dict, Optional
import math
import time
import sys
import os
import random


class _IppSignal:
    def __init__(self, name):
        self.name = name
        self.handlers = []   # list of (handler, vm_ref_or_None)

    def connect(self, handler, vm=None):
        self.handlers.append((handler, vm))

    def emit(self, *args):
        for handler, vm in self.handlers:
            if vm is not None:
                # Dispatch through the VM that connected this handler
                saved_running = vm.running
                vm._call(handler, list(args), None)
                vm.running = True
                vm.run()
                vm.running = saved_running
            elif callable(handler):
                handler(*args)

    def __repr__(self):
        return f"Signal({self.name})"


class _Vec4:
    def __init__(self, x=0, y=0, z=0, w=1):
        self.x, self.y, self.z, self.w = x, y, z, w
    def __repr__(self):
        return f"vec4({self.x}, {self.y}, {self.z}, {self.w})"


class _Mat4:
    def __init__(self, m=None):
        if m is None:
            self.m = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        else:
            self.m = list(m)
    def __repr__(self):
        return f"Matrix4([{', '.join(str(x) for x in self.m[:4])}, ...])"


class _Quat:
    def __init__(self, x=0, y=0, z=0, w=1):
        self.x, self.y, self.z, self.w = x, y, z, w
    def __repr__(self):
        return f"quat({self.x}, {self.y}, {self.z}, {self.w})"


# ─── Sentinel for cache misses (FIX: BUG-M5) ─────────────────────────────────
_MISS = object()


class Profiler:
    def __init__(self):
        self.enabled = False
        self.opcode_counts: Dict[OpCode, int] = {}
        self.function_times: Dict[str, float] = {}
        self.call_counts: Dict[str, int] = {}
        self.loop_iterations = 0
        self.start_time = None

    def start(self):
        self.enabled = True
        self.start_time = time.perf_counter()
        self.opcode_counts.clear()
        self.function_times.clear()
        self.call_counts.clear()
        self.loop_iterations = 0

    def stop(self):
        self.enabled = False

    def record_opcode(self, opcode: OpCode):
        if self.enabled:
            self.opcode_counts[opcode] = self.opcode_counts.get(opcode, 0) + 1

    def record_call(self, name: str):
        if self.enabled:
            self.call_counts[name] = self.call_counts.get(name, 0) + 1

    def get_stats(self) -> dict:
        total_ops = sum(self.opcode_counts.values())
        elapsed = time.perf_counter() - self.start_time if self.start_time else 0
        return {
            'total_instructions': total_ops,
            'elapsed_ms': elapsed * 1000,
            'opcode_counts': dict(self.opcode_counts),
            'function_calls': dict(self.call_counts),
        }


class InlineCache:
    """FIX: BUG-M5 — use _MISS sentinel, not None, to distinguish miss from nil."""

    def __init__(self, max_size=2048):
        self.cache: Dict[str, Any] = {}  # FIX v1.5.31: use str not int
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: int):
        result = self.cache.get(key, _MISS)
        if result is _MISS:
            self.misses += 1
            return _MISS
        self.hits += 1
        return result

    def set(self, key: int, value: Any):
        if len(self.cache) >= self.max_size:
            # evict oldest
            del self.cache[next(iter(self.cache))]
        self.cache[key] = value

    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0


class VMFrame:
    __slots__ = ('chunk', 'closure', 'function', 'ip', 'stack_base', '_method_instance', '_is_init_call')

    def __init__(self, chunk: Chunk, closure=None, function=None, stack_base: int = 0):
        self.chunk = chunk
        self.closure = closure
        self.function = function
        self.ip = 0
        self.stack_base = stack_base    # FIX: BUG-C2 — locals are relative to this
        self._method_instance = None    # FIX BUG-N1/BUG-4: instance being constructed
        self._is_init_call = False      # FIX BUG-4: True when frame is a constructor call


class UpvalueCell:
    """FIX BUG-NEW-M5 — heap cell for a captured variable.

    While the enclosing function is still running (open state) the cell
    holds a reference to the *VM stack list* and an *index* into it.
    When the enclosing function returns (or the variable leaves scope via
    CLOSE_UPVALUE) we copy the value into ``closed_value`` and drop the
    stack reference (closed state).
    """
    __slots__ = ('_stack', '_index', '_closed', '_closed_value')

    _OPEN = object()  # sentinel: cell is still open

    def __init__(self, stack: list, index: int):
        self._stack = stack
        self._index = index
        self._closed = False
        self._closed_value = UpvalueCell._OPEN

    # -- value property -------------------------------------------------------

    @property
    def value(self):
        if not self._closed:
            return self._stack[self._index]
        return self._closed_value

    @value.setter
    def value(self, v):
        if not self._closed:
            self._stack[self._index] = v
        else:
            self._closed_value = v

    def close(self):
        """Snapshot the stack value and detach from the stack."""
        if not self._closed:
            self._closed_value = self._stack[self._index]
            self._closed = True
            self._stack = None   # allow GC

    def __repr__(self):
        state = "closed" if self._closed else f"open@{self._index}"
        return f"<UpvalueCell {state} = {self.value!r}>"


class Closure:
    def __init__(self, chunk: Chunk, upvalues: List = None):
        self.chunk = chunk
        self.upvalues: List[UpvalueCell] = upvalues or []


class IppFunction:
    def __init__(self, name: str = "<script>", arity: int = 0,
                 chunk: Chunk = None, is_method: bool = False):
        self.name = name
        self.arity = arity
        self.chunk = chunk
        self.is_method = is_method


class IppClass:
    def __init__(self, name: str, superclass: 'IppClass' = None):
        self.name = name
        self.superclass = superclass
        self.methods: Dict[str, Any] = {}

    def get_method(self, name: str):
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.get_method(name)
        return None


class IppAsyncCoroutine:
    """Returned when an async function is called — not yet executed."""
    def __init__(self, closure, args):
        self.closure = closure
        self.args = args
    def __repr__(self):
        name = getattr(getattr(self.closure, '_proto', None), 'name', '<async>')
        return f"<coroutine {name}>"


class IppVMGenerator:
    """VM-level generator object — suspends on YIELD, resumes on next()."""
    def __init__(self, closure, args):
        self._closure = closure
        self._args = args
        self._vm = None
        self._done = False

    def _ensure_vm(self):
        if self._vm is None:
            self._vm = VM()
            # Temporarily disable generator detection so _call pushes a real frame
            self._vm._in_generator_call = True
            proto = getattr(self._closure, '_proto', None)
            orig_async = getattr(proto, 'is_async', False)
            if proto: proto.is_async = False
            self._vm._call(self._closure, list(self._args), None)
            if proto: proto.is_async = orig_async
            self._vm._in_generator_call = False
            self._vm.running = True

    def next_value(self):
        if self._done:
            return None
        self._ensure_vm()
        vm = self._vm
        vm._gen_yield_value = None
        vm._gen_yield_hit = False
        vm._gen_active = True   # signal YIELD handler to pause
        vm.running = True
        vm.run()
        vm._gen_active = False

        if vm._gen_yield_hit:
            return vm._gen_yield_value
        else:
            self._done = True
            return None

    def __repr__(self):
        return "<generator>"


def _reorder_named_args(callee, positional, kwargs):
    """Slot kwargs into correct positions using the callee's param list."""
    param_names = []
    # Try FunctionProto first (most reliable)
    if isinstance(callee, Closure):
        proto = getattr(callee, 'proto', None)
        if proto and hasattr(proto, 'param_names'):
            param_names = proto.param_names
    # Fallback: look at _proto attribute stored by CLOSURE handler
    if not param_names and hasattr(callee, '_proto'):
        proto = callee._proto
        if hasattr(proto, 'param_names'):
            param_names = proto.param_names

    if not param_names:
        return positional + list(kwargs.values())

    result = list(positional)
    while len(result) < len(param_names):
        result.append(None)
    for name, val in kwargs.items():
        if name in param_names:
            result[param_names.index(name)] = val
        else:
            result.append(val)
    return result


class VMError(Exception):
    pass


class IppInstance:
    def __init__(self, cls: IppClass):
        self.cls = cls
        self.fields: Dict[str, Any] = {}
        # tracks which class context we're currently inside (set by VM during method calls)
        self._current_class: Optional['IppClass'] = None

    def _is_private(self, name: str) -> bool:
        return name.startswith('__') and not name.endswith('__')

    def get(self, name: str) -> Any:
        if name in self.fields:
            # FIX BUG-N1: block external access to __ private fields
            if self._is_private(name) and self._current_class is None:
                raise VMError(f"Cannot access private field '{name}' from outside class '{self.cls.name}'")
            return self.fields[name]
        method = self.cls.get_method(name)
        if method is not None:
            # FIX: BUG-V8 — return a BoundMethod wrapper, not the raw chunk
            return BoundMethod(self, method)
        raise VMError(f"Undefined property '{name}' on {self.cls.name}")

    def set(self, name: str, value: Any):
        # FIX BUG-N1: block external writes to __ private fields
        if self._is_private(name) and self._current_class is None:
            raise VMError(f"Cannot set private field '{name}' from outside class '{self.cls.name}'")
        self.fields[name] = value

    def __repr__(self):
        return f"<{self.cls.name} instance>"

    def __str__(self):
        # FIX BUG-N6: call user-defined __str__ if it exists
        str_method = self.cls.get_method('__str__')
        if str_method:
            return _call_ipp_method(self, str_method)
        return f"<{self.cls.name} instance>"


def _repr_impl(value):
    """Implementation for repr() builtin - v1.7.8.2"""
    if isinstance(value, IppInstance):
        repr_method = value.cls.get_method('__repr__')
        if repr_method:
            return _call_ipp_method(value, repr_method)
        return f"<{value.cls.name} instance>"
    if isinstance(value, str):
        return '"' + value + '"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "nil"
    return str(value)


def _call_ipp_method(instance: IppInstance, method) -> Any:
    """Helper to call an Ipp method from Python context (e.g. __str__).
    FIX BUG-N6: must push instance as self and capture the return value."""
    from ipp.vm.vm import VM, Chunk, Closure, IppFunction
    if isinstance(method, Chunk):
        chunk = method
        closure = None
    elif isinstance(method, Closure):
        chunk = method.chunk
        closure = method
    elif isinstance(method, IppFunction):
        chunk = method.chunk if method.chunk else None
        closure = None
    else:
        return f"<{instance.cls.name} instance>"

    if chunk is None:
        return f"<{instance.cls.name} instance>"

    # Create a minimal VM with builtins, push self as slot 0, run
    vm = VM()
    # mark instance as inside its own class so private fields work
    instance._current_class = instance.cls
    base = len(vm.stack)
    vm.stack.append(instance)   # slot 0 = self
    frame = VMFrame(chunk, closure=closure, function=method, stack_base=base)
    vm.frames.append(frame)
    try:
        vm.run(chunk)
        result = vm._return_value
        if result is None and vm.stack:
            result = vm.stack[-1]
    except Exception:
        result = f"<{instance.cls.name} instance>"
    finally:
        instance._current_class = None
    return result if result is not None else f"<{instance.cls.name} instance>"


class BoundMethod:
    """FIX: BUG-V8 — wraps instance + method chunk so CALL can dispatch correctly."""

    def __init__(self, instance: IppInstance, method):
        self.instance = instance
        self.method = method   # IppFunction or Closure or Chunk


class ExceptionHandler:
    """FIX: BUG-V5 — stack of exception handlers instead of single scalar."""
    __slots__ = ('target_ip', 'stack_len', 'frame_depth')

    def __init__(self, target_ip: int, stack_len: int, frame_depth: int):
        self.target_ip = target_ip
        self.stack_len = stack_len
        self.frame_depth = frame_depth


# ─── VM sentinel values ───────────────────────────────────────────────────────
_SUSPEND = object()
_RETURN_FRAME = object()

# Opcode lookup cache - v1.5.26 fix for VM performance
_OPCODE_CACHE = {}


class VM:
    """
    Stack-based bytecode VM.

    Key invariant: locals for a frame are at positions
        [frame.stack_base, frame.stack_base + n_locals)
    on the value stack.  GET_LOCAL/SET_LOCAL are relative to stack_base.
    """

    def __init__(self, chunk: Chunk = None):
        self.chunk = chunk
        self.stack: List[Any] = []
        self.frames: List[VMFrame] = []
        self.globals: Dict[str, Any] = {}
        # FIX: BUG-V5 — exception handler stack
        self.exception_handlers: List[ExceptionHandler] = []
        self.running = True
        self._return_value = None
        self.call_count = 0
        self.instruction_count = 0
        # FIX BUG-N2: recursion depth tracking
        self.call_depth = 0
        self.max_depth = 2000

        # FIX: BUG-M5 — inline caches use _MISS sentinel
        self._global_cache = InlineCache(max_size=2048)
        self._string_cache: Dict[str, str] = {}

        # FIX BUG-NEW-M5: track open upvalue cells (cells still pointing at stack slots)
        self.open_upvalues: List[UpvalueCell] = []

        self.profiler = Profiler()
        self._init_builtins()

    def _init_builtins(self):
        import random, json, datetime, base64, hashlib, re, os, time as time_mod
        from ipp.runtime.builtins import BUILTINS as _INTERP_BUILTINS
        from ipp.interpreter.interpreter import IppDict, IppList

        def wasm_run(wasm_code):
            import os as os_mod
            if isinstance(wasm_code, str):
                if wasm_code.endswith('.ipp'):
                    with open(wasm_code, 'r') as f:
                        source = f.read()
                    from ipp.lexer.lexer import tokenize
                    from ipp.parser.parser import parse
                    tokens = tokenize(source)
                    ast = parse(tokens)
                    return self.run(ast)
                else:
                    from ipp.lexer.lexer import tokenize
                    from ipp.parser.parser import parse
                    tokens = tokenize(wasm_code)
                    ast = parse(tokens)
                    return self.run(ast)
            return "wasm_run requires file path or source code"

        self.globals.update({
            'print': self._builtin_print,
            'len': self._builtin_len,
            'type': self._builtin_type,
            'set': self._builtin_set,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': self._builtin_sum,
            'range': self._builtin_range,
            'random': random.random,
            'randint': random.randint,
            'randfloat': lambda a, b: random.uniform(a, b),
            'choice': lambda seq: random.choice(seq),
            'shuffle': lambda seq: random.shuffle(seq),
            'str': str,
            'repr': lambda v: _repr_impl(v),
            'int': int,
            'float': float,
            'bool': bool,
            'to_number': lambda s: float(s) if '.' in str(s) else int(s),
            'to_int': int,
            'to_float': float,
            'to_bool': bool,
            'to_string': str,
            'wasm_run': wasm_run,
            'sqrt': math.sqrt,
            'pow': pow,
            'append': lambda lst, item: lst.append(item),
            'slice': lambda lst, start, end=None: lst[start:end] if end is not None else lst[start:],
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'log10': math.log10,
            'floor': math.floor, 'ceil': math.ceil,
            'round': round,
            'degrees': math.degrees, 'radians': math.radians,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan, 'atan2': math.atan2,
            'pi': math.pi,
            'e': math.e,
            'json_parse': json.loads,
            'json_stringify': json.dumps,
            'md5': lambda s: hashlib.md5(str(s).encode()).hexdigest(),
            'sha256': lambda s: hashlib.sha256(str(s).encode()).hexdigest(),
            'sha1': lambda s: hashlib.sha1(str(s).encode()).hexdigest(),
            'sha512': lambda s: hashlib.sha512(str(s).encode()).hexdigest(),
            'hash': lambda s: abs(hash(s)),
            'base64_encode': lambda s: base64.b64encode(str(s).encode()).decode(),
            'base64_decode': lambda s: base64.b64decode(str(s).encode()).decode(),
            'clock': time_mod.perf_counter,
            'time': time_mod.time,
            'sleep': time_mod.sleep,
            'input': input,
            'exit': sys.exit,
            'assert': self._builtin_assert,
            # String functions
            'format': lambda s, *args, **kwargs: s.format(*args) if args else s.format(**kwargs) if kwargs else s,
            'upper': lambda s: str(s).upper(),
            'lower': lambda s: str(s).lower(),
            'strip': lambda s, *a: str(s).strip(*a),
            'split': lambda s, *a: str(s).split(*a),
            'join': lambda arr, sep: sep.join(str(x) for x in arr),
            'replace': lambda s, a, b: str(s).replace(a, b),
            'replace_all': lambda s, a, b: str(s).replace(a, b),
            'starts_with': lambda s, p: str(s).startswith(p),
            'ends_with': lambda s, p: str(s).endswith(p),
            'startswith': lambda s, p: str(s).startswith(p),
            'endswith': lambda s, p: str(s).endswith(p),
            'find': lambda s, *a: str(s).find(*a),
            'index_of': lambda s, *a: str(s).find(*a),
            'char_at': lambda s, i: s[int(i)] if int(i) < len(s) else '',
            'substring': lambda s, start, length=None: s[int(start):int(start)+int(length)] if length else s[int(start):],
            'count': lambda s, sub: str(s).count(sub),
            'contains': lambda s, sub: sub in str(s),
            'split_lines': lambda s: s.split('\n'),
            'ascii': ord,
            'from_ascii': chr,
            # File I/O
            'read_file': self._builtin_read_file,
            'file_read': self._builtin_read_file,
            'write_file': self._builtin_write_file,
            'file_write': self._builtin_write_file,
            'append_file': self._builtin_append_file,
            'file_exists': os.path.exists,
            'delete_file': lambda p: (os.remove(p), True)[1] if os.path.exists(p) else False,
            'list_dir': os.listdir,
            'mkdir': lambda p: (os.makedirs(str(p), exist_ok=True), True)[1],
            # Dict operations
            'keys': lambda d: list(d.keys()) if isinstance(d, dict) else (list(d.data.keys()) if hasattr(d, 'data') else []),
            'values': lambda d: list(d.values()) if isinstance(d, dict) else (list(d.data.values()) if hasattr(d, 'data') else []),
            'items': lambda d: list(d.items()) if isinstance(d, dict) else (list(d.data.items()) if hasattr(d, 'data') else []),
            'has_key': lambda d, k: k in d if isinstance(d, dict) else (k in d.data if hasattr(d, 'data') else False),
            # Regex
            'regex_match': lambda text, pattern: bool(re.match(pattern, text)),
            'regex_search': lambda text, pattern: (m.group() if (m := re.search(pattern, text)) else ''),
            'regex_replace': lambda text, pattern, repl: re.sub(pattern, repl, text),
            # CSV
            'csv_parse': lambda s: [row.split(',') for row in s.strip().split('\n')[1:]],
            'csv_parse_dict': self._builtin_csv_parse_dict,
            # URL
            'url_encode': lambda s: __import__('urllib.parse').parse.quote(str(s)),
            'url_decode': lambda s: __import__('urllib.parse').parse.unquote(str(s)),
            # GZIP
            'gzip_compress': lambda s: base64.b64encode(__import__('gzip').compress(str(s).encode())).decode(),
            'gzip_decompress': lambda s: __import__('gzip').decompress(base64.b64decode(str(s))).decode(),
            # UUID
            'uuid4': lambda: str(__import__('uuid').uuid4()),
            'uuid1': lambda: str(__import__('uuid').uuid1()),
            'uuid_nil': lambda: '00000000-0000-0000-0000-000000000000',
            # Signals (v1.6.6)
            'signal': lambda name: _IppSignal(name),
            'connect': lambda sig, handler: sig.connect(handler, self) if isinstance(sig, _IppSignal) else None,
            'emit': lambda sig, *args: sig.emit(*args) if isinstance(sig, _IppSignal) else None,
            # Mathematics (v1.6.8) - simplified placeholder versions
            'vec4': lambda x=0, y=0, z=0, w=1: _Vec4(x, y, z, w),
            'mat4': lambda: _Mat4(),
            'mat4_identity': lambda: _Mat4(),
            'quat': lambda x=0, y=0, z=0, w=1: _Quat(x, y, z, w),
            # Async (v1.6.9)
            'async_run': self._builtin_async_run,
            'next': self._builtin_next,
            'is_coroutine': lambda obj: isinstance(obj, (IppVMGenerator, IppAsyncCoroutine)),
            # OS
            'os_platform': lambda: os.name,
            'os_cwd': os.getcwd,
            'env_get': os.environ.get,
            # Math helpers
            'lerp': lambda a, b, t: a + (b - a) * t,
            'clamp': lambda v, mn, mx: max(mn, min(mx, v)),
            'sign': lambda n: (n > 0) - (n < 0),
            'factorial': lambda n: math.factorial(int(n)),
            'gcd': math.gcd,
            'hypot': math.hypot,
            # Complex
            'complex': complex,
            # Logging
            'logger': self._builtin_logger,
        })
        
        # Add missing builtins from interpreter's BUILTINS
        missing_builtins = [
            'http_get', 'http_post', 'http_put', 'http_delete', 'http_request', 'http_serve',
            'websocket_connect', 'websocket_send', 'websocket_receive', 'websocket_close',
            'deque', 'datetime', 'datetime_create', 'seed', 'is_coroutine',
            'PriorityQueue', 'Tree', 'Graph',
            'map_range', 'vec3', 'vec2',
            'mat4_look_at', 'mat4_translate', 'mat4_rotate', 'mat4_scale', 'mat4_multiply',
            'mat4_perspective', 'quat_from_axis_angle', 'quat_multiply', 'quat_slerp', 'quat_to_mat4',
            'scene', 'node', 'camera', 'mesh', 'light',
            'mesh_cube', 'mesh_sphere', 'mesh_plane',
        ]
        
        for name in missing_builtins:
            if name in _INTERP_BUILTINS:
                self.globals[name] = _INTERP_BUILTINS[name]
            else:
                # Add placeholder for missing builtins that might not be in BUILTINS dict
                pass
        
        # Add even more missing builtins
        more_missing = [
            'distance', 'distance_3d', 'normalize', 'normalize_3d',
            'normal', 'ordict',
        ]
        
        for name in more_missing:
            if name in _INTERP_BUILTINS:
                self.globals[name] = _INTERP_BUILTINS[name]
        
        # Add ALL missing builtins from interpreter's BUILTINS
        for name, val in _INTERP_BUILTINS.items():
            if name not in self.globals and callable(val):
                try:
                    self.globals[name] = val
                except:
                    pass

    # ─── Built-in helpers ─────────────────────────────────────────────────────

    def _builtin_print(self, *args):
        parts = []
        for a in args:
            if a is None:
                parts.append("nil")
            elif isinstance(a, bool):
                parts.append("true" if a else "false")
            elif isinstance(a, float) and a.is_integer():
                parts.append(str(int(a)))
            elif isinstance(a, IppInstance):
                # FIX BUG-N6: call user-defined __str__ via Python str() which triggers __str__
                parts.append(str(a))
            else:
                parts.append(str(a))
        print(" ".join(parts))
        return None

    def _builtin_len(self, obj):
        # FIX: drain generators to a list (for-loop iterates with len + index)
        if isinstance(obj, IppVMGenerator):
            if not hasattr(obj, '_collected'):
                items = []
                while True:
                    val = obj.next_value()
                    if val is None:
                        break
                    items.append(val)
                obj._collected = items
            return len(obj._collected)
        # FIX v1.7.8.3: Check for __len__ method on IppInstance
        if isinstance(obj, IppInstance):
            len_method = obj.cls.get_method('__len__')
            if len_method:
                result = _call_ipp_method(obj, len_method)
                return result
            raise VMError(f"len() not supported for {obj.cls.name}")
        if isinstance(obj, (str, list, dict, tuple)):
            return len(obj)
        # FIX: IppSet uses _items
        if hasattr(obj, '_items') and isinstance(obj._items, set):
            return len(obj._items)
        # FIX: IppSet may use _data
        if hasattr(obj, '_data') and isinstance(obj._data, set):
            return len(obj._data)
        if hasattr(obj, '__len__'):
            return len(obj)
        raise VMError(f"len() not supported for {type(obj).__name__}")

    def _builtin_next(self, gen, default=None):
        """Get next value from an IppVMGenerator or any Python iterable."""
        if isinstance(gen, IppVMGenerator):
            val = gen.next_value()
            return val if val is not None else default
        elif hasattr(gen, '__next__'):
            try:
                return gen.__next__()
            except StopIteration:
                return default
        return default

    def _builtin_async_run(self, fn, *args):
        """Execute an async function or coroutine synchronously."""
        # IppAsyncCoroutine: call its closure with stored args
        if isinstance(fn, IppAsyncCoroutine):
            return self._builtin_async_run(fn.closure, *fn.args)
        if isinstance(fn, (Closure, IppFunction)):
            saved_stack = list(self.stack)
            saved_frames = list(self.frames)
            saved_running = self.running
            # Temporarily clear async flag so it runs immediately
            proto = getattr(fn, '_proto', None)
            orig_async = getattr(proto, 'is_async', False)
            if proto:
                proto.is_async = False
            self._call(fn, list(args), None)
            self.running = True
            result = self.run()
            self.stack = saved_stack
            self.frames = saved_frames
            self.running = saved_running
            if proto:
                proto.is_async = orig_async
            return result
        elif callable(fn):
            return fn(*args)
        # Already a computed value
        return fn

    def _builtin_type(self, obj):
        if obj is None:           return "nil"
        if isinstance(obj, bool): return "bool"
        if isinstance(obj, int):  return "number"   # FIX: Ipp uses "number" not "int"
        if isinstance(obj, float): return "number"  # FIX: Ipp uses "number" not "float"
        if isinstance(obj, str):  return "string"
        if isinstance(obj, (list, tuple)): return "list"
        if hasattr(obj, 'elements'): return "list"   # IppList
        if isinstance(obj, dict): return "dict"
        if hasattr(obj, '_items') and isinstance(getattr(obj,'_items',None), set): return "set"
        if hasattr(obj, '_data') and hasattr(obj, 'add'): return "set"
        if hasattr(obj, 'data'): return "dict"
        if isinstance(obj, IppClass): return "class"
        if isinstance(obj, IppInstance): return obj.cls.name
        if isinstance(obj, (Closure, IppFunction)): return "function"
        if callable(obj): return "function"
        return type(obj).__name__

    def _builtin_sum(self, *args):
        if len(args) == 1 and hasattr(args[0], '__iter__') and not isinstance(args[0], str):
            return sum(args[0])
        return sum(args)

    def _builtin_range(self, *args):
        if len(args) == 1:   return list(range(int(args[0])))
        if len(args) == 2:   return list(range(int(args[0]), int(args[1])))
        if len(args) == 3:   return list(range(int(args[0]), int(args[1]), int(args[2])))
        return []

    def _builtin_read_file(self, path):
        with open(str(path), 'r', encoding='utf-8') as f:
            return f.read()

    def _builtin_write_file(self, path, data):
        with open(str(path), 'w', encoding='utf-8') as f:
            f.write(str(data))
        return True

    def _builtin_append_file(self, path, data):
        with open(str(path), 'a', encoding='utf-8') as f:
            f.write(str(data))
        return True

    def _builtin_csv_parse_dict(self, s):
        lines = s.strip().split('\n')
        if not lines:
            return []
        headers = [h.strip() for h in lines[0].split(',')]
        result = []
        for line in lines[1:]:
            values = [v.strip() for v in line.split(',')]
            row = {}
            for i, h in enumerate(headers):
                if i < len(values):
                    row[h] = values[i]
            result.append(row)
        return result

    def _builtin_logger(self, name="ipp", level="INFO"):
        import logging
        logger = logging.getLogger(str(name))
        logger.setLevel(getattr(logging, str(level).upper(), logging.INFO))
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        return logger
        return []

    def _builtin_assert(self, cond, msg="Assertion failed"):
        if not self._is_truthy(cond):
            raise VMError(str(msg))
        return None

    def _builtin_set(self, *args):
        """FIX BUG-NEW-M6 — set() / set(iterable) factory."""
        from ipp.interpreter.interpreter import IppSet, IppList
        if not args:
            return IppSet()
        iterable = args[0]
        if isinstance(iterable, IppList):
            return IppSet(iterable.elements)
        if isinstance(iterable, IppSet):
            return IppSet(iterable._data.copy())
        if isinstance(iterable, (list, tuple, set)):
            return IppSet(iterable)
        raise VMError(f"set() argument must be iterable, got {type(iterable).__name__}")

    def _intern_string(self, s: str) -> str:
        if s not in self._string_cache:
            self._string_cache[s] = s
        return self._string_cache[s]

    # ─── Core execution ───────────────────────────────────────────────────────

    def reset(self):
        self.stack.clear()
        self.frames.clear()
        self.exception_handlers.clear()
        self.running = True
        self._return_value = None
        # FIX VM-BUG-1/BUG-6: clear cache so stale entries don't cause "Cannot call int"
        self._global_cache.clear()
        self.call_depth = 0

    def run(self, chunk: Chunk = None) -> Any:
        # If chunk is provided, use it and don't create a new frame if one already exists
        if chunk:
            self.chunk = chunk
        # FIX: if no chunk but frames already exist (e.g. generator resume), still execute
        if not self.chunk and not self.frames:
            return None

        # Only create new frame if no frames exist (allows _call_ipp_method to work)
        if not self.frames:
            frame = VMFrame(self.chunk, stack_base=0)
            self.frames.append(frame)

        while self.running and self.frames:
            frame = self.frames[-1]
            if frame.ip >= len(frame.chunk.code):
                # implicit return from top-level
                if len(self.frames) > 1:
                    self.frames.pop()
                    self.stack.append(None)
                else:
                    self.running = False
                break

            raw = frame.chunk.code[frame.ip]
            # FIX v1.5.26: Cache opcode lookups instead of enum each time
            opcode = _OPCODE_CACHE.get(raw)
            if opcode is None:
                try:
                    opcode = OpCode(raw)
                    _OPCODE_CACHE[raw] = opcode
                except ValueError:
                    raise VMError(f"Unknown opcode {raw} at ip={frame.ip}")

            if self.profiler.enabled:
                self.profiler.record_opcode(opcode)
            self.instruction_count += 1

            try:
                result = self._execute(opcode, frame)
            except VMError as e:
                # FIX VM-BUG-3: route VMError through exception handlers (try/catch support)
                if not hasattr(e, '_thrown_value'):
                    e._thrown_value = str(e)  # FIX R04: runtime errors caught as string message
                if self.exception_handlers:
                    target_ip = self._handle_exception(e, frame)
                    frame = self.frames[-1]
                    frame.ip = target_ip
                    continue
                raise
            except Exception as e:
                # wrap in VMError for structured handling
                exc = VMError(str(e))
                exc._thrown_value = str(e)  # FIX R04
                if self.exception_handlers:
                    target_ip = self._handle_exception(exc, frame)
                    frame = self.frames[-1]
                    frame.ip = target_ip
                    continue
                raise VMError(str(e)) from e

            if result is _RETURN_FRAME:
                ret_val = self.stack.pop() if self.stack else None
                # FIX BUG-NEW-M5: close any upvalues still open in the returning frame
                self._close_frame_upvalues(frame)
                # FIX BUG-N1: clear private-access flag when leaving a method
                if frame._method_instance is not None:
                    frame._method_instance._current_class = None
                # FIX BUG-4: if this was an __init__ call, return the instance not nil
                if frame._is_init_call and frame._method_instance is not None:
                    ret_val = frame._method_instance
                # FIX BUG-1/BUG-6: trim stack back to stack_base to clean up
                # locals/args that were pushed before the frame ran
                while len(self.stack) > frame.stack_base:
                    self.stack.pop()
                # FIX BUG-N2: decrement call depth on return
                if self.call_depth > 0:
                    self.call_depth -= 1
                self.frames.pop()
                if self.frames:
                    self.stack.append(ret_val)
                    frame = self.frames[-1]
                else:
                    self._return_value = ret_val
                    self.running = False
            elif result is _SUSPEND:
                pass  # ip already updated inside handler
            else:
                # normal: advance ip by instruction size
                frame.ip += opcode_size(opcode)

        return self._return_value

    # ── Upvalue helpers (FIX BUG-NEW-M5) ─────────────────────────────────────

    def _capture_upvalue(self, slot: int) -> UpvalueCell:
        """Return an existing open cell for *slot*, or create a new one."""
        for cell in self.open_upvalues:
            if cell._index == slot and not cell._closed:
                return cell
        cell = UpvalueCell(self.stack, slot)
        self.open_upvalues.append(cell)
        return cell

    def _close_upvalues(self, last_slot: int):
        """Close (and remove from open list) all upvalues at index >= last_slot."""
        remaining = []
        for cell in self.open_upvalues:
            if not cell._closed and cell._index >= last_slot:
                cell.close()
            else:
                remaining.append(cell)
        self.open_upvalues = remaining

    def _close_frame_upvalues(self, frame: VMFrame):
        """Close all upvalues whose stack slots belong to *frame*."""
        self._close_upvalues(frame.stack_base)

    def _handle_exception(self, exc: VMError, frame: VMFrame):
        """FIX: BUG-V5 — pop handler stack and jump to catch block."""
        handler = self.exception_handlers.pop()
        # restore stack
        while len(self.stack) > handler.stack_len:
            self.stack.pop()
        # FIX R04: push the actual thrown value, not str(exc)
        # VMError wraps the thrown value; if it came from THROW, recover original
        thrown_val = getattr(exc, '_thrown_value', None)
        if thrown_val is not None:
            self.stack.append(thrown_val)
        else:
            self.stack.append(str(exc))
        # restore frame depth — decrement call_depth for each frame unwound
        frames_to_pop = len(self.frames) - handler.frame_depth
        while len(self.frames) > handler.frame_depth:
            self.frames.pop()
        self.call_depth = max(0, self.call_depth - frames_to_pop)
        if not self.frames:
            raise exc
        # Update the frame reference to use the correct frame after pop
        return handler.target_ip

    def _get_line_info(self, frame: VMFrame) -> str:
        """Get line number info from current frame's chunk."""
        try:
            ip = frame.ip
            lines = frame.chunk.lines
            if ip < len(lines):
                line = lines[ip]
                return f" at line {line}" if line > 0 else ""
            return ""
        except Exception as e:
            return ""

    def _execute(self, opcode: OpCode, frame: VMFrame) -> Any:
        code = frame.chunk.code
        constants = frame.chunk.constants
        ip = frame.ip
        line_info = self._get_line_info(frame)

        # ── Constants ────────────────────────────────────────────────────
        if opcode == OpCode.HALT:
            self.running = False
            return None

        elif opcode == OpCode.NOP:
            pass

        elif opcode == OpCode.CONSTANT:
            idx = code[ip + 1]
            self.stack.append(constants[idx])

        elif opcode == OpCode.CONSTANT_LONG:
            idx = code[ip+1] | (code[ip+2] << 8) | (code[ip+3] << 16)
            self.stack.append(constants[idx])

        elif opcode == OpCode.NIL:   self.stack.append(None)
        elif opcode == OpCode.TRUE:  self.stack.append(True)
        elif opcode == OpCode.FALSE: self.stack.append(False)

        # ── Stack ops ────────────────────────────────────────────────────
        elif opcode == OpCode.POP:
            if self.stack: self.stack.pop()

        elif opcode == OpCode.DUP:
            if self.stack: self.stack.append(self.stack[-1])

        elif opcode == OpCode.DUP2:
            if len(self.stack) >= 2:
                self.stack.append(self.stack[-2])
                self.stack.append(self.stack[-2])

        elif opcode == OpCode.SWAP:
            if len(self.stack) >= 2:
                self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

        # ── Globals ──────────────────────────────────────────────────────
        elif opcode == OpCode.GET_GLOBAL:
            idx = code[ip + 1]
            name = constants[idx]
            cached = self._global_cache.get(name)  # FIX v1.5.31: use name not hash
            if cached is not _MISS:
                self.stack.append(cached)
            elif name in self.globals:
                val = self.globals[name]
                self._global_cache.set(name, val)
                self.stack.append(val)
            else:
                raise VMError(f"Undefined variable '{name}'{line_info}")

        elif opcode == OpCode.SET_GLOBAL:
            idx = code[ip + 1]
            name = constants[idx]
            # FIX v1.5.23: Check for const global
            const_globals = getattr(frame.chunk, 'const_globals', None)
            if const_globals and name in const_globals:
                raise VMError(f"Cannot reassign immutable 'let' variable: {name}{line_info}")
            val = self.stack[-1] if self.stack else None
            self.globals[name] = val
            self._global_cache.set(name, val)  # FIX v1.5.31

        elif opcode == OpCode.DEFINE_GLOBAL:
            idx = code[ip + 1]
            name = constants[idx]
            val = self.stack.pop() if self.stack else None
            self.globals[name] = val
            self._global_cache.set(name, val)  # FIX v1.5.31

        elif opcode == OpCode.DELETE_GLOBAL:
            idx = code[ip + 1]
            name = constants[idx]
            self.globals.pop(name, None)
            self._global_cache.cache.pop(name, None)  # FIX v1.5.31

        # ── Locals — FIX: BUG-C2 use frame.stack_base ───────────────────
        elif opcode == OpCode.GET_LOCAL:
            idx = code[ip + 1]
            slot = frame.stack_base + idx
            if slot < len(self.stack):
                self.stack.append(self.stack[slot])
            else:
                self.stack.append(None)

        elif opcode == OpCode.SET_LOCAL:
            idx = code[ip + 1]
            slot = frame.stack_base + idx
            # Check for const local immutability
            if frame.chunk and hasattr(frame.chunk, 'const_locals') and idx in frame.chunk.const_locals:
                if slot < len(self.stack) and self.stack[slot] is not None:
                    raise VMError(f"Cannot reassign immutable 'let' variable")
            if self.stack:
                while len(self.stack) <= slot:
                    self.stack.append(None)
                self.stack[slot] = self.stack[-1]

        elif opcode == OpCode.DELETE_LOCAL:
            idx = code[ip + 1]
            slot = frame.stack_base + idx
            if slot < len(self.stack):
                self.stack[slot] = None

        # ── Upvalues ─────────────────────────────────────────────────────
        elif opcode == OpCode.GET_UPVALUE:
            # FIX BUG-NEW-M5: read value through UpvalueCell
            idx = code[ip + 1]
            if frame.closure and idx < len(frame.closure.upvalues):
                cell = frame.closure.upvalues[idx]
                self.stack.append(cell.value if isinstance(cell, UpvalueCell) else cell)
            else:
                self.stack.append(None)

        elif opcode == OpCode.SET_UPVALUE:
            # FIX BUG-NEW-M5: write value through UpvalueCell
            idx = code[ip + 1]
            if frame.closure and idx < len(frame.closure.upvalues) and self.stack:
                cell = frame.closure.upvalues[idx]
                if isinstance(cell, UpvalueCell):
                    cell.value = self.stack[-1]
                else:
                    frame.closure.upvalues[idx] = self.stack[-1]

        elif opcode == OpCode.GET_CAPTURED:
            # FIX: BUG-V7 — use operand index, not hardcoded 0
            # FIX BUG-NEW-M5: also read through UpvalueCell
            idx = code[ip + 1]
            if frame.closure and idx < len(frame.closure.upvalues):
                cell = frame.closure.upvalues[idx]
                self.stack.append(cell.value if isinstance(cell, UpvalueCell) else cell)
            else:
                self.stack.append(None)

        elif opcode == OpCode.CLOSE_UPVALUE:
            # FIX BUG-NEW-M5: snapshot top-of-stack into any upvalue cell pointing there,
            # then pop the stack slot.
            if self.stack:
                top_slot = len(self.stack) - 1
                self._close_upvalues(top_slot)
                self.stack.pop()

        # ── Properties ───────────────────────────────────────────────────
        elif opcode == OpCode.GET_PROPERTY:
            idx = code[ip + 1]
            name = constants[idx]
            obj = self.stack[-1]
            if isinstance(obj, IppInstance):
                self.stack[-1] = obj.get(name)
            elif isinstance(obj, IppClass):
                # FIX v1.5.25: Static methods on class
                method = obj.get_method(name)
                if method is not None:
                    # Wrap as BoundMethod with instance=None for static dispatch
                    self.stack[-1] = BoundMethod(None, method)
                else:
                    raise VMError(f"Class '{obj.name}' has no static member '{name}'")
            elif isinstance(obj, _IppSignal):
                # FIX: signal method dispatch with VM reference
                _sig = obj
                _vm = self
                if name == 'connect':
                    self.stack[-1] = lambda handler, _s=_sig, _v=_vm: _s.connect(handler, _v)
                elif name == 'emit':
                    self.stack[-1] = lambda *args, _s=_sig: _s.emit(*args)
                else:
                    raise VMError(f"Signal has no property '{name}'")
            elif hasattr(obj, '_items') and isinstance(getattr(obj, '_items', None), set):
                # FIX: IppSet method dispatch
                _set = obj._items
                _IPPSET_METHODS = {
                    'add':      lambda s, v: s.add(v) or obj,
                    'remove':   lambda s, v: s.discard(v) or obj,
                    'discard':  lambda s, v: s.discard(v) or obj,
                    'has':      lambda s, v: v in s,
                    'contains': lambda s, v: v in s,
                    'clear':    lambda s: s.clear() or obj,
                    'len':      lambda s: len(s),
                    'size':     lambda s: len(s),
                    'to_list':  lambda s: list(s),
                    'union':    lambda s, o: type(obj)(s | (o._items if hasattr(o,'_items') else set(o))),
                    'intersect':lambda s, o: type(obj)(s & (o._items if hasattr(o,'_items') else set(o))),
                    'difference':lambda s, o: type(obj)(s - (o._items if hasattr(o,'_items') else set(o))),
                }
                if name in _IPPSET_METHODS:
                    _fn = _IPPSET_METHODS[name]
                    self.stack[-1] = lambda *args, _f=_fn, _s=_set: _f(_s, *args)
                elif name == 'len':
                    self.stack[-1] = lambda _s=_set: len(_s)
                else:
                    raise VMError(f"Property '{name}' not found on IppSet")
            elif isinstance(obj, str):
                # FIX: string property/method access
                _STR_METHODS = {
                    'upper': lambda s: s.upper(), 'lower': lambda s: s.lower(),
                    'strip': lambda s: s.strip(), 'lstrip': lambda s: s.lstrip(),
                    'rstrip': lambda s: s.rstrip(),
                    'split': lambda s, *a: s.split(*a),
                    'join': lambda s, lst: s.join(str(x) for x in lst),
                    'replace': lambda s, a, b: s.replace(a, b),
                    'startswith': lambda s, p: s.startswith(p),
                    'endswith': lambda s, p: s.endswith(p),
                    'find': lambda s, p: s.find(p),
                    'index': lambda s, p: s.index(p),
                    'contains': lambda s, p: p in s,
                    'count': lambda s, p: s.count(p),
                    'repeat': lambda s, n: s * int(n),
                    'trim': lambda s: s.strip(),
                    'reverse': lambda s: s[::-1],
                    'chars': lambda s: list(s),
                    'to_upper': lambda s: s.upper(),
                    'to_lower': lambda s: s.lower(),
                    'to_int': lambda s: int(s),
                    'to_float': lambda s: float(s),
                    'format': lambda s, *a, **kw: s.format(*a, **kw),
                    'len': lambda s: len(s),
                }
                if name == 'len':
                    self.stack[-1] = (lambda _s: lambda: len(_s))(obj)
                elif name == 'format':
                    # Special case: format needs **kwargs for named args
                    _bound_obj = obj
                    _vm_ref = self
                    def _format_method(_o=obj, _vm=self):
                        def _call(*args, **kw):
                            # Merge _vm._kwargs_for_call into kw
                            extra = getattr(_vm, '_kwargs_for_call', None) or {}
                            _vm._kwargs_for_call = None
                            kw.update(extra)
                            return _o.format(*args, **kw)
                        return _call
                    self.stack[-1] = _format_method()
                elif name in _STR_METHODS:
                    _fn = _STR_METHODS[name]
                    _bound_obj = obj
                    self.stack[-1] = lambda *args, _f=_fn, _o=_bound_obj: _f(_o, *args)
                elif hasattr(obj, name):
                    attr = getattr(obj, name)
                    # Wrap method_descriptor as bound callable
                    if callable(attr) and not isinstance(attr, (str, int, float, bool)):
                        self.stack[-1] = lambda *args, _a=attr: _a(*args)
                    else:
                        self.stack[-1] = attr
                else:
                    raise VMError(f"Property '{name}' not found on str")
            elif isinstance(obj, dict) and name in obj:
                self.stack[-1] = obj[name]
            elif hasattr(obj, name):
                attr = getattr(obj, name)
                # FIX: wrap method_descriptor so it becomes callable from VM
                if hasattr(attr, '__objclass__') or type(attr).__name__ in ('method_descriptor', 'builtin_function_or_method', 'method-wrapper'):
                    _bound_obj = obj
                    self.stack[-1] = lambda *args, _a=attr, _o=_bound_obj: _a(_o, *args) if not callable(_a) else _a(*args)
                else:
                    self.stack[-1] = attr
            else:
                raise VMError(f"Property '{name}' not found on {type(obj).__name__}")

        elif opcode == OpCode.SET_PROPERTY:
            idx = code[ip + 1]
            name = constants[idx]
            value = self.stack.pop()
            # FIX: pop obj too — compile_set no longer emits DUP
            obj = self.stack.pop()
            if isinstance(obj, IppInstance):
                obj.set(name, value)
            elif isinstance(obj, dict):
                obj[name] = value
            else:
                setattr(obj, name, value)
            # property assignment is a statement — push nothing

        elif opcode == OpCode.GET_SUPER:
            idx = code[ip + 1]
            name = constants[idx]
            obj = self.stack.pop()
            if isinstance(obj, IppInstance):
                if obj.cls.superclass:
                    method = obj.cls.superclass.get_method(name)
                    if method:
                        self.stack.append(BoundMethod(obj, method))
                        return None
                raise VMError(f"No superclass method '{name}'")
            raise VMError("GET_SUPER on non-instance")

        # ── Indexing ─────────────────────────────────────────────────────
        elif opcode == OpCode.GET_INDEX:
            idx = self.stack.pop()
            obj = self.stack.pop()
            # FIX: generators are collected to a list by _builtin_len; use that list here
            if isinstance(obj, IppVMGenerator):
                if not hasattr(obj, '_collected'):
                    items = []
                    while True:
                        val = obj.next_value()
                        if val is None:
                            break
                        items.append(val)
                    obj._collected = items
                self.stack.append(obj._collected[int(idx)])
            elif isinstance(obj, (list, tuple, str)):
                self.stack.append(obj[int(idx)])
            elif isinstance(obj, dict):
                # Try integer index first (for list-style dict), then string key
                key = idx
                if isinstance(idx, (int, float)) and int(idx) in obj:
                    self.stack.append(obj[int(idx)])
                else:
                    self.stack.append(obj.get(key))
            elif hasattr(obj, 'data'):
                # IppDict
                self.stack.append(obj.data.get(idx))
            elif hasattr(obj, 'elements'):
                # IppList
                self.stack.append(obj.elements[int(idx)])
            elif isinstance(obj, (int, float, bool)) and int(idx) == 0:
                # FIX: scalar[0] returns the scalar (supports single-value tuple idiom)
                self.stack.append(obj)
            else:
                raise VMError(f"Cannot index {type(obj).__name__} with {idx!r}{line_info}")

        elif opcode == OpCode.SET_INDEX:
            value = self.stack.pop()
            idx = self.stack.pop()
            obj = self.stack.pop()
            if isinstance(obj, list):
                i = int(idx)
                if -len(obj) <= i < len(obj):
                    obj[i] = value
                else:
                    raise VMError(f"Index {i} out of range (length {len(obj)}){line_info}")
            elif isinstance(obj, dict):
                obj[idx] = value
            elif hasattr(obj, 'elements'):
                obj.elements[int(idx)] = value
            elif hasattr(obj, 'data'):
                obj.data[idx] = value
            # No push - assignment is a statement, not expression

        # ── Jumps — FIX: BUG-C1/BUG-M8 all use read_int (3-byte operands) ─
        elif opcode == OpCode.JUMP:
            offset = frame.chunk.read_int(ip + 1)
            frame.ip = ip + 4 + offset
            return _SUSPEND

        elif opcode == OpCode.JUMP_IF_FALSE:
            offset = frame.chunk.read_int(ip + 1)
            if not self._is_truthy(self.stack[-1]):
                frame.ip = ip + 4 + offset
                return _SUSPEND

        elif opcode == OpCode.JUMP_IF_TRUE:
            offset = frame.chunk.read_int(ip + 1)
            if self._is_truthy(self.stack[-1]):
                frame.ip = ip + 4 + offset
                return _SUSPEND

        elif opcode == OpCode.JUMP_IF_FALSE_POP:
            offset = frame.chunk.read_int(ip + 1)
            val = self.stack.pop()
            if not self._is_truthy(val):
                frame.ip = ip + 4 + offset
                return _SUSPEND

        elif opcode == OpCode.JUMP_IF_TRUE_POP:
            offset = frame.chunk.read_int(ip + 1)
            val = self.stack.pop()
            if self._is_truthy(val):
                frame.ip = ip + 4 + offset
                return _SUSPEND

        elif opcode == OpCode.LOOP:
            # FIX: BUG-C7 — backward jump: ip = (ip + 4) - offset = loop_start
            offset = frame.chunk.read_int(ip + 1)
            frame.ip = (ip + 4) - offset
            return _SUSPEND

        elif opcode == OpCode.MATCH:
            pass  # match dispatch handled structurally by compiler now

        # ── Function calls ───────────────────────────────────────────────
        elif opcode == OpCode.CALL:
            argc = code[ip + 1]
            raw = []
            for _ in range(argc):
                raw.append(self.stack.pop() if self.stack else None)
            raw.reverse()
            callee = self.stack.pop() if self.stack else None

            # FIX: split positional from named args using sentinel marker
            if "\x00KWARGS\x00" in raw:
                sentinel_idx = raw.index("\x00KWARGS\x00")
                positional = raw[:sentinel_idx]
                named_pairs = raw[sentinel_idx + 1:]
                kwargs = {}
                for i in range(0, len(named_pairs) - 1, 2):
                    if isinstance(named_pairs[i], str):
                        kwargs[named_pairs[i]] = named_pairs[i + 1]
                # For Ipp closures: reorder positionals using param names
                # For Python builtins: pass as kwargs
                if isinstance(callee, (Closure, IppFunction)):
                    args = _reorder_named_args(callee, positional, kwargs)
                    self._kwargs_for_call = None
                else:
                    args = positional
                    self._kwargs_for_call = kwargs
            else:
                args = raw
                self._kwargs_for_call = None

            frame.ip += 2    # advance past CALL + argc before pushing new frame
            self._call(callee, args, frame)
            return _SUSPEND  # new frame will be executed

        elif opcode == OpCode.INVOKE:
            # Direct method call:  INVOKE argc, name_idx
            argc = code[ip + 1]
            name_idx = code[ip + 2]
            name = constants[name_idx]
            args = []
            for _ in range(argc):
                args.append(self.stack.pop() if self.stack else None)
            args.reverse()
            obj = self.stack.pop()
            if isinstance(obj, IppInstance):
                method = obj.cls.get_method(name)
                if method:
                    frame.ip += 4
                    self._call_method(obj, method, args, frame)
                    return _SUSPEND
            raise VMError(f"Method '{name}' not found on {type(obj).__name__}")

        elif opcode == OpCode.TAIL_CALL:
            argc = code[ip + 1]
            args = []
            for _ in range(argc):
                args.append(self.stack.pop() if self.stack else None)
            args.reverse()
            callee = self.stack.pop() if self.stack else None
            # Replace current frame
            self.frames.pop()
            frame.ip += 2
            self._call(callee, args, self.frames[-1] if self.frames else None)
            return _SUSPEND

        elif opcode == OpCode.CLOSURE:
            # FIX BUG-NEW-M5: FunctionProto carries upvalue descriptors; wire up cells.
            idx = code[ip + 1]
            proto = constants[idx]
            if isinstance(proto, FunctionProto):
                upvalue_cells = []
                for is_local, up_idx in proto.upvalue_descs:
                    if is_local:
                        # Capture a local from the *current* frame's stack
                        slot = frame.stack_base + up_idx
                        upvalue_cells.append(self._capture_upvalue(slot))
                    else:
                        # Inherit an upvalue from the enclosing closure
                        if frame.closure and up_idx < len(frame.closure.upvalues):
                            upvalue_cells.append(frame.closure.upvalues[up_idx])
                        else:
                            # Fallback: create a closed cell with None
                            dummy = UpvalueCell.__new__(UpvalueCell)
                            dummy._stack = None
                            dummy._index = -1
                            dummy._closed = True
                            dummy._closed_value = None
                            upvalue_cells.append(dummy)
                closure = Closure(proto.chunk, upvalue_cells)
                closure._proto = proto  # FIX: store proto for named-arg dispatch
                self.stack.append(closure)
            elif isinstance(proto, Chunk):
                # Legacy bare Chunk (e.g. from backup/v1.2.4 code paths)
                self.stack.append(Closure(proto))
            else:
                self.stack.append(proto)

        elif opcode == OpCode.RETURN:
            return _RETURN_FRAME

        elif opcode == OpCode.RETURN_VAL:
            return _RETURN_FRAME

        elif opcode == OpCode.YIELD:
            val = self.stack.pop() if self.stack else None
            if getattr(self, '_gen_active', False):
                # We're running inside a generator's next_value() call — pause here
                self._gen_yield_value = val
                self._gen_yield_hit = True
                # FIX: push nil as the "result" of the yield expression so that the
                # ExprStmt POP after `yield x` consumes nil, not the local variable below it
                self.stack.append(None)
                frame.ip += 1  # advance past YIELD opcode (size=1)
                self.running = False
                return _SUSPEND
            # Not in a generator context — just push nil (shouldn't happen normally)
            self.stack.append(None)

        # ── Classes ──────────────────────────────────────────────────────
        elif opcode == OpCode.CLASS:
            idx = code[ip + 1]
            name = constants[idx]
            cls = IppClass(name)
            self.stack.append(cls)

        elif opcode == OpCode.SUBCLASS:
            superclass = self.stack.pop()
            if isinstance(superclass, IppClass):
                if isinstance(self.stack[-1], IppClass):
                    self.stack[-1].superclass = superclass
            else:
                raise VMError("Superclass must be a class")

        elif opcode == OpCode.METHOD:
            name_idx = code[ip + 1]
            name = constants[name_idx]
            if self.stack and isinstance(self.stack[-1], Closure):
                method = self.stack.pop()
                if self.stack and isinstance(self.stack[-1], IppClass):
                    self.stack[-1].methods[name] = method
                else:
                    self.stack.append(method)

        elif opcode == OpCode.END_METHOD:
            pass

        elif opcode == OpCode.GET_METHOD:
            idx = code[ip + 1]
            name = constants[idx]
            obj = self.stack[-1]
            if isinstance(obj, IppClass):
                method = obj.get_method(name)
                if method:
                    self.stack.append(method)
                else:
                    raise VMError(f"Undefined method '{name}'")
            elif isinstance(obj, IppInstance):
                self.stack.append(obj.get(name))

        # ── Import ───────────────────────────────────────────────────────
        elif opcode == OpCode.IMPORT:
            path_idx = code[ip + 1] | (code[ip + 2] << 8) | (code[ip + 3] << 16)
            module_path = constants[path_idx] if path_idx < len(constants) else ""

            if not hasattr(self, '_module_cache'):
                self._module_cache = {}
            if module_path in self._module_cache:
                self.globals.update(self._module_cache[module_path])
            else:
                import os
                import sys
                
                # Get directory of current file
                cwd = os.getcwd()
                
                # Try multiple paths
                candidates = [
                    module_path,
                    os.path.join(cwd, module_path),
                    os.path.join(cwd, 'tests', 'v1_5_37', module_path),
                ]
                
                found_path = None
                for candidate in candidates:
                    if os.path.exists(candidate):
                        found_path = candidate
                        break
                
                if not found_path:
                    raise VMError(f"Module not found: '{module_path}'")

                with open(found_path, 'r') as f:
                    src = f.read()

                from ipp.lexer.lexer import tokenize
                from ipp.parser.parser import parse
                from ipp.vm.compiler import compile_ast
                child = VM()
                child.globals.update(self.globals)
                child.run(compile_ast(parse(tokenize(src))))
                new_globals = {k: v for k, v in child.globals.items()
                               if k not in self.globals or child.globals[k] is not self.globals.get(k)}
                self.globals.update(new_globals)
                self._module_cache[module_path] = new_globals

        elif opcode == OpCode.END_IMPORT:
            pass

        # ── Collections — FIX: BUG-C6 ────────────────────────────────────
        elif opcode == OpCode.LIST:
            count = code[ip + 1]
            if count > 0 and count <= len(self.stack):
                items = self.stack[-count:]
                del self.stack[-count:]          # FIX: BUG-C6 — only ONE delete
            else:
                items = []
            self.stack.append(list(items))

        elif opcode == OpCode.LIST_APPEND:
            val = self.stack.pop()
            self.stack[-1].append(val)

        elif opcode == OpCode.LIST_EXTEND:
            iterable = self.stack.pop()
            lst = self.stack[-1]
            if hasattr(iterable, '__iter__') and not isinstance(iterable, (str, dict)):
                lst.extend(list(iterable))

        elif opcode == OpCode.DICT:
            count = code[ip + 1]
            d = {}
            pairs = []
            for _ in range(count):
                v = self.stack.pop() if self.stack else None
                k = self.stack.pop() if self.stack else None
                pairs.append((k, v))
            for k, v in reversed(pairs):
                d[k] = v
            self.stack.append(d)

        elif opcode == OpCode.TUPLE:
            count = code[ip + 1]
            if count > 0 and count <= len(self.stack):
                items = self.stack[-count:]
                del self.stack[-count:]
            else:
                items = []
            self.stack.append(tuple(items))

        elif opcode == OpCode.SPREAD:
            obj = self.stack.pop() if self.stack else None
            if hasattr(obj, '__iter__') and not isinstance(obj, (str, dict)):
                for item in obj:
                    self.stack.append(item)
            else:
                self.stack.append(obj)

        elif opcode == OpCode.RANGE:
            b = self.stack.pop()
            a = self.stack.pop()
            # `..` is exclusive of the end in Ipp — 0..5 = [0,1,2,3,4]
            self.stack.append(list(range(int(a), int(b))))

        # ── Arithmetic ───────────────────────────────────────────────────
        elif opcode == OpCode.ADD:
            b, a = self.stack.pop(), self.stack.pop()
            # FIX: Don't call str() on IppInstance - causes infinite recursion
            if isinstance(a, str) or isinstance(b, str):
                a_str = str(a) if not isinstance(a, IppInstance) else f"<{a.cls.name} instance>"
                b_str = str(b) if not isinstance(b, IppInstance) else f"<{b.cls.name} instance>"
                self.stack.append(self._intern_string(a_str + b_str))
            elif isinstance(a, IppInstance):
                method = a.cls.get_method('__add__')
                if method:
                    bound = BoundMethod(a, method)
                    result = self._call_method(a, bound, [b], None)
                    self.stack.append(result)
                else:
                    self.stack.append(a + b)
            else:
                self.stack.append(a + b)

        elif opcode == OpCode.SUBTRACT:
            b, a = self.stack.pop(), self.stack.pop()
            if isinstance(a, IppInstance):
                method = a.cls.get_method('__sub__')
                if method:
                    bound = BoundMethod(a, method)
                    result = self._call_method(a, bound, [b], None)
                    self.stack.append(result)
                else:
                    self.stack.append(a - b)
            else:
                self.stack.append(a - b)

        elif opcode == OpCode.MULTIPLY:
            b, a = self.stack.pop(), self.stack.pop()
            if isinstance(a, IppInstance):
                method = a.cls.get_method('__mul__')
                if method:
                    bound = BoundMethod(a, method)
                    result = self._call_method(a, bound, [b], None)
                    self.stack.append(result)
                else:
                    self.stack.append(a * b)
            else:
                self.stack.append(a * b)

        elif opcode == OpCode.DIVIDE:
            b, a = self.stack.pop(), self.stack.pop()
            if b == 0: raise VMError(f"Division by zero{line_info}")
            if isinstance(a, IppInstance):
                method = a.cls.get_method('__div__')
                if method:
                    bound = BoundMethod(a, method)
                    result = self._call_method(a, bound, [b], None)
                    self.stack.append(result)
                else:
                    self.stack.append(a / b)
            else:
                self.stack.append(a / b)

        elif opcode == OpCode.MODULO:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a % b)

        elif opcode == OpCode.POWER:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a ** b)

        elif opcode == OpCode.FLOOR_DIV:
            b, a = self.stack.pop(), self.stack.pop()
            if b == 0: raise VMError(f"Division by zero{line_info}")
            self.stack.append(int(a) // int(b))

        # ── Bitwise ──────────────────────────────────────────────────────
        elif opcode == OpCode.BIT_AND:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(int(a) & int(b))
        elif opcode == OpCode.BIT_OR:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(int(a) | int(b))
        elif opcode == OpCode.BIT_XOR:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(int(a) ^ int(b))
        elif opcode == OpCode.BIT_NOT:
            a = self.stack.pop()
            self.stack.append(~int(a))
        elif opcode == OpCode.SHIFT_LEFT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(int(a) << int(b))
        elif opcode == OpCode.SHIFT_RIGHT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(int(a) >> int(b))

        # ── Unary ────────────────────────────────────────────────────────
        elif opcode == OpCode.NEGATE:
            self.stack.append(-self.stack.pop())
        elif opcode == OpCode.NOT:
            self.stack.append(not self._is_truthy(self.stack.pop()))
        elif opcode == OpCode.INCREMENT:
            self.stack.append(self.stack.pop() + 1)
        elif opcode == OpCode.DECREMENT:
            self.stack.append(self.stack.pop() - 1)

        # ── Comparisons ──────────────────────────────────────────────────
        elif opcode == OpCode.EQUAL:
            b, a = self.stack.pop(), self.stack.pop()
            # FIX: normalize IppList for comparison
            from ipp.interpreter.interpreter import IppList as _IppList2
            if isinstance(a, _IppList2): a = a.elements
            if isinstance(b, _IppList2): b = b.elements
            self.stack.append(a == b)
        elif opcode == OpCode.NOT_EQUAL:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a != b)
        elif opcode == OpCode.LESS:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a < b)
        elif opcode == OpCode.LESS_EQUAL:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a <= b)
        elif opcode == OpCode.GREATER:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a > b)
        elif opcode == OpCode.GREATER_EQUAL:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a >= b)

        elif opcode == OpCode.CONTAINS:
            # FIX: 'item in collection' — stack: item, collection → bool
            collection = self.stack.pop()
            item = self.stack.pop()
            if isinstance(collection, (list, tuple, str)):
                self.stack.append(item in collection)
            elif isinstance(collection, dict):
                self.stack.append(item in collection)
            elif hasattr(collection, '_items'):
                self.stack.append(item in collection._items)
            elif hasattr(collection, '_data') and isinstance(collection._data, set):
                self.stack.append(item in collection._data)
            else:
                try:
                    self.stack.append(item in collection)
                except TypeError:
                    self.stack.append(False)

        elif opcode == OpCode.MATCH_EXC_TYPE:
            # Stack: [..., exc, type_str] → pops type_str, peeks exc, pushes bool
            # exc stays on stack so catch_var binding can still use it
            type_str = self.stack.pop()
            exc_val = self.stack[-1]  # peek - don't consume
            matched = False
            if isinstance(exc_val, IppInstance):
                matched = exc_val.cls.name == type_str
            elif isinstance(exc_val, str):
                matched = exc_val.startswith(type_str + ':') or exc_val == type_str
            self.stack.append(matched)  # stack: [..., exc, bool]

        # ── Nullish / optional ───────────────────────────────────────────
        elif opcode == OpCode.NULLISH:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a if a is not None else b)

        elif opcode == OpCode.OPTIONAL_CHAIN:
            idx = code[ip + 1]
            name = constants[idx]
            obj = self.stack.pop()
            if obj is None:
                self.stack.append(None)
            elif isinstance(obj, IppInstance):
                try:
                    self.stack.append(obj.get(name))
                except VMError:
                    self.stack.append(None)
            elif isinstance(obj, dict):
                # FIX: dict?.key lookups
                self.stack.append(obj.get(name, None))
            elif hasattr(obj, name):
                self.stack.append(getattr(obj, name))
            else:
                self.stack.append(None)

        elif opcode == OpCode.OPTIONAL_CHAIN_END:
            pass

        # ── Exception handling — FIX: BUG-V3/V5/V6 ───────────────────────
        elif opcode == OpCode.THROW:
            msg = self.stack.pop() if self.stack else "Unknown error"
            exc = VMError(str(msg))
            exc._thrown_value = msg  # FIX R04: preserve original value for catch binding
            if self.exception_handlers:
                target_ip = self._handle_exception(exc, frame)
                frame.ip = target_ip  # Update current frame's ip
                return _SUSPEND
            raise exc

        elif opcode == OpCode.ASSERT:
            has_message = len(self.stack) >= 2
            if has_message:
                msg = self.stack.pop()
                cond = self.stack.pop()
            else:
                msg = "Assertion failed"
                cond = self.stack.pop() if self.stack else None
            if not self._is_truthy(cond):
                raise VMError(str(msg))

        elif opcode == OpCode.TRY:
            offset = frame.chunk.read_int(ip + 1)
            target = ip + 4 + offset
            # FIX: BUG-V5 — push onto handler stack
            handler = ExceptionHandler(target, len(self.stack), len(self.frames))
            self.exception_handlers.append(handler)

        elif opcode == OpCode.TRY_END:
            # Normal completion only - don't pop if we're in exception path
            # (the handler will be popped by catch block)
            pass

        elif opcode == OpCode.CATCH:
            pass  # catch block entry; exception value already on stack

        elif opcode == OpCode.CATCH_END:
            pass

        elif opcode == OpCode.FINALLY:
            # FIX: BUG-V3 — finally block actually executes because it's emitted as regular code
            pass  # marker only; body follows as regular instructions

        elif opcode == OpCode.END_FINALLY:
            pass

        elif opcode == OpCode.EXCEPTION:
            # FIX: BUG-V6 — push actual exception (already on stack from _handle_exception)
            # This opcode is a no-op; the exception string is already TOS after _handle_exception
            pass

        # ── With statement — FIX: BUG-V4 ────────────────────────────────
        elif opcode == OpCode.WITH_ENTER:
            # Call __enter__ if available, else just use the value
            resource = self.stack[-1]
            if hasattr(resource, '__enter__'):
                entered = resource.__enter__()
                self.stack[-1] = entered
            # else leave resource on stack as-is

        elif opcode == OpCode.WITH_EXIT:
            # Call __exit__ if available
            resource = self.stack.pop() if self.stack else None
            if hasattr(resource, '__exit__'):
                resource.__exit__(None, None, None)

        # ── String ops ───────────────────────────────────────────────────
        elif opcode == OpCode.CONCATENATE:
            count = code[ip + 1] if ip + 1 < len(code) else 2
            parts = []
            for _ in range(count):
                parts.append(str(self.stack.pop() if self.stack else ""))
            parts.reverse()
            self.stack.append(self._intern_string("".join(parts)))

        elif opcode == OpCode.CONCAT_COUNT:
            count = code[ip + 1]
            parts = []
            for _ in range(count):
                parts.append(str(self.stack.pop() if self.stack else ""))
            parts.reverse()
            self.stack.append("".join(parts))

        elif opcode in (OpCode.BREAK, OpCode.CONTINUE):
            pass  # resolved to JUMPs by compiler; these are fallback no-ops

        else:
            pass  # unknown opcode — skip

        return None

    def _call(self, callee, args, return_frame: VMFrame):
        """Push a new call frame for callee with given args."""
        # FIX v1.7.6.2: Special case for dict.get - don't treat first arg as kwarg
        if hasattr(callee, '__self__') and isinstance(callee.__self__, dict) and hasattr(callee, '__name__') and callee.__name__ == 'get':
            try:
                if len(args) == 1:
                    result = callee(args[0])
                elif len(args) == 2:
                    result = callee(args[0], args[1])
                else:
                    raise VMError("dict.get() takes 1 or 2 arguments")
                self.stack.append(result)
                return
            except VMError:
                raise
            except Exception as e:
                raise VMError(str(e))
        
        # FIX: Handle Python callables with kwargs (e.g. str.format(name=val))
        if callable(callee) and not isinstance(callee, (Closure, IppFunction, IppClass, BoundMethod, type(str.format))):
            kwargs = getattr(self, '_kwargs_for_call', None) or {}
            self._kwargs_for_call = None
            try:
                result = callee(*args, **kwargs) if kwargs else callee(*args)
            except VMError:
                raise
            except Exception as e:
                raise VMError(str(e))
            self.stack.append(result)
            return

        # FIX BUG-N2: recursion depth check — incremented only at actual frame-push sites below

        # FIX: detect generator functions (contain YIELD opcode at opcode positions)
        if isinstance(callee, Closure) and not getattr(self, '_in_generator_call', False):
            chunk = callee.chunk
            # Must check YIELD at actual opcode positions, not just any byte
            _has_yield = False
            _ip = 0
            _YIELD_VAL = int(OpCode.YIELD)
            while _ip < len(chunk.code):
                _op_byte = chunk.code[_ip]
                if _op_byte == _YIELD_VAL:
                    _has_yield = True
                    break
                try:
                    _op = OpCode(_op_byte)
                    _ip += opcode_size(_op)
                except Exception:
                    _ip += 1
            if _has_yield:
                self.call_depth -= 1
                gen = IppVMGenerator(callee, list(args))
                self.stack.append(gen)
                return
            # FIX: async functions return a coroutine object, not execute immediately
            proto = getattr(callee, '_proto', None)
            if proto and getattr(proto, 'is_async', False):
                self.call_depth -= 1
                coro = IppAsyncCoroutine(callee, list(args))
                self.stack.append(coro)
                return

        if isinstance(callee, BoundMethod):
            # FIX v1.5.25: Handle static methods (instance=None)
            if callee.instance is None:
                # Static: call without injecting self
                if isinstance(callee.method, Closure):
                    chunk = callee.method.chunk
                    base = len(self.stack)
                    for a in args:
                        self.stack.append(a)
                    new_frame = VMFrame(chunk, closure=callee.method, stack_base=base)
                    # FIX BUG-N2: increment only at frame-push
                    if self.call_depth >= self.max_depth:
                        raise VMError(f"Maximum recursion depth ({self.max_depth}) exceeded")
                    self.call_depth += 1
                    self.frames.append(new_frame)
                else:
                    # IppFunction or Chunk - use generic call
                    self._call(callee.method, args, return_frame)
            else:
                self._call_method(callee.instance, callee.method, args, return_frame)
            return

        if isinstance(callee, IppClass):
            # Instantiate
            instance = IppInstance(callee)
            init = callee.get_method("init")
            if init:
                self._call_method(instance, init, args, return_frame)
                # FIX BUG-4: mark frame as init call so RETURN_FRAME pushes instance
                # NOT premature stack.append(instance) which corrupts stack
                if self.frames:
                    self.frames[-1]._is_init_call = True
            else:
                self.stack.append(instance)
            return

        if isinstance(callee, Closure):
            chunk = callee.chunk
            proto = getattr(callee, '_proto', None)  # FIX: stored as _proto by CLOSURE handler
        elif isinstance(callee, IppFunction):
            chunk = callee.chunk
            proto = getattr(callee, '_proto', None)
        elif isinstance(callee, Chunk):
            chunk = callee
            proto = None
        else:
            raise VMError(f"Cannot call {type(callee).__name__}")

        if chunk is None:
            self.stack.append(None)
            return

        # FIX: BUG-M7 — push args onto stack BEFORE creating frame
        # Handle variadic: pack excess args into list
        variadic_param = getattr(proto, 'variadic_param', None) if proto else None
        proto_param_count = len(getattr(proto, 'param_names', None) or []) if proto else 0
        expected_args = proto_param_count or (len(chunk.locals) if hasattr(chunk, 'locals') else 0)

        from ipp.interpreter.interpreter import IppList as _IppList
        base = len(self.stack)
        if variadic_param:
            normal_count = max(0, expected_args - 1)
            if normal_count == 0:
                self.stack.append(_IppList(list(args)))
            elif len(args) > normal_count:
                for i in range(normal_count):
                    self.stack.append(args[i] if i < len(args) else None)
                self.stack.append(_IppList(list(args[normal_count:])))
            else:
                for a in args:
                    self.stack.append(a)
                while len(self.stack) - base < normal_count:
                    self.stack.append(None)
                self.stack.append(_IppList([]))
        else:
            for a in args:
                self.stack.append(a)
            # FIX: pad missing args with None so default-param guards in function body fire
            if expected_args > len(args):
                for _ in range(expected_args - len(args)):
                    self.stack.append(None)

        new_frame = VMFrame(chunk,
                            closure=callee if isinstance(callee, Closure) else None,
                            function=callee,
                            stack_base=base)
        # FIX BUG-N2: increment ONLY here, once per frame pushed
        if self.call_depth >= self.max_depth:
            raise VMError(f"Maximum recursion depth ({self.max_depth}) exceeded")
        self.call_depth += 1
        self.frames.append(new_frame)

    def _call_method(self, instance: IppInstance, method, args, return_frame):
        """Call a method with self as first arg. FIX: BUG-V8."""
        # FIX BUG-N2: depth incremented only at frame-push below
        
        # Handle BoundMethod
        if isinstance(method, BoundMethod):
            instance = method.instance
            method = method.method
        
        if isinstance(method, Chunk):
            chunk = method
            closure = None
        elif isinstance(method, Closure):
            chunk = method.chunk
            closure = method
        elif isinstance(method, IppFunction):
            chunk = method.chunk
            closure = None
        else:
            raise VMError(f"Cannot call method of type {type(method).__name__}")

        if chunk is None:
            self.stack.append(None)
            return

        # FIX: BUG-N1 — mark instance as being accessed from inside its own class
        instance._current_class = instance.cls

        # FIX: BUG-M7 — push self + args onto stack
        base = len(self.stack)
        self.stack.append(instance)   # slot 0 = self
        for a in args:
            self.stack.append(a)

        new_frame = VMFrame(chunk, closure=closure, function=method, stack_base=base)
        # Store instance on frame so RETURN_VAL can clear _current_class
        new_frame._method_instance = instance
        # FIX BUG-N2: increment only here, once per frame pushed
        if self.call_depth >= self.max_depth:
            raise VMError(f"Maximum recursion depth ({self.max_depth}) exceeded")
        self.call_depth += 1
        self.frames.append(new_frame)

    def _is_truthy(self, value) -> bool:
        if value is None or value is False:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False
        if isinstance(value, str) and len(value) == 0:
            return False
        if isinstance(value, (list, tuple, dict)) and len(value) == 0:
            return False
        return True


def execute_bytecode(chunk: Chunk) -> Any:
    vm = VM(chunk)
    return vm.run()


def benchmark_vm(chunk: Chunk, iterations: int = 100) -> dict:
    vm = VM()
    
    times = []
    for _ in range(iterations):
        vm.reset()
        start = time.perf_counter()
        vm.run(chunk)
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    return {
        'iterations': iterations,
        'avg_ms': avg_time * 1000,
        'min_ms': min_time * 1000,
        'max_ms': max_time * 1000,
        'total_ms': sum(times) * 1000,
        'instructions': vm.instruction_count // iterations,
    }


def profile_vm(chunk: Chunk, iterations: int = 100) -> dict:
    vm = VM(chunk)
    vm.profiler.start()
    
    for _ in range(iterations):
        vm.reset()
        vm.run(chunk)
    
    vm.profiler.stop()
    return vm.profiler.get_stats()


def profile_source(source: str, iterations: int = 100) -> dict:
    from ipp.lexer.lexer import tokenize
    from ipp.parser.parser import parse
    
    tokens = tokenize(source)
    ast = parse(tokens)
    chunk = compile_ast(ast)
    
    return profile_vm(chunk, iterations)


def profile_and_report(source: str, iterations: int = 100):
    from ipp.lexer.lexer import tokenize
    from ipp.parser.parser import parse
    
    tokens = tokenize(source)
    ast = parse(tokens)
    chunk = compile_ast(ast)
    
    vm = VM(chunk)
    vm.profiler.start()
    
    start = time.perf_counter()
    for _ in range(iterations):
        vm.reset()
        vm.run(chunk)
    end = time.perf_counter()
    
    vm.profiler.stop()
    stats = vm.profiler.get_stats()
    
    total_time = (end - start) * 1000
    
    print("\n=== Performance Profile ===")
    print(f"Iterations: {iterations}")
    print(f"Total Time: {total_time:.2f} ms")
    print(f"Avg per iteration: {total_time / iterations:.4f} ms")
    print(f"Total Instructions: {stats['total_instructions']:,}")
    print(f"Instructions/iteration: {stats['total_instructions'] // iterations:,}")
    
    if stats['opcode_counts']:
        print("\nTop 10 Opcodes:")
        sorted_ops = sorted(stats['opcode_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
        for opcode, count in sorted_ops:
            pct = (count / stats['total_instructions']) * 100 if stats['total_instructions'] > 0 else 0
            print(f"  {opcode.name}: {count:,} ({pct:.1f}%)")
    
    return stats
