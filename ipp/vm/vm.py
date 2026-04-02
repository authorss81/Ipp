from .bytecode import Chunk, OpCode, opcode_size
from .compiler import FunctionProto
from typing import List, Any, Dict, Optional
import math
import time
import sys
import os

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
        self.cache: Dict[int, Any] = {}
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
    __slots__ = ('chunk', 'closure', 'function', 'ip', 'stack_base', '_method_instance')

    def __init__(self, chunk: Chunk, closure=None, function=None, stack_base: int = 0):
        self.chunk = chunk
        self.closure = closure
        self.function = function
        self.ip = 0
        self.stack_base = stack_base    # FIX: BUG-C2 — locals are relative to this


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
        vm.run()
        result = vm._return_value
        if result is None and vm.stack:
            result = vm.stack[-1]
    except Exception:
        result = f"<{instance.cls.name} instance>"
    finally:
        instance._current_class = None
    return result if result is not None else f"<{instance.cls.name} instance>"
    """Helper to call an Ipp method from Python code."""
    from ipp.vm.vm import VM, Chunk, Closure, IppFunction
    vm = VM()
    if isinstance(method, Chunk):
        chunk = method
    elif isinstance(method, Closure):
        chunk = method.chunk
    else:
        raise VMError(f"Cannot call method of type {type(method).__name__}")
    base = len(vm.stack)
    vm.stack.append(instance)
    frame = VMFrame(chunk, closure=method if isinstance(method, Closure) else None, function=method, stack_base=base)
    vm.frames.append(frame)
    try:
        vm.run()
    except:
        pass
    if vm.stack:
        return vm.stack[-1]
    return None


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
        self.max_depth = 1000

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
            'int': int,
            'float': float,
            'bool': bool,
            'to_number': lambda s: float(s) if '.' in str(s) else int(s),
            'to_int': int,
            'to_float': float,
            'to_bool': bool,
            'to_string': str,
            'sqrt': math.sqrt,
            'pow': pow,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'log10': math.log10,
            'floor': math.floor, 'ceil': math.ceil,
            'round': round,
            'degrees': math.degrees, 'radians': math.radians,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan, 'atan2': math.atan2,
            'pi': lambda: math.pi,
            'e': lambda: math.e,
            'json_parse': json.loads,
            'json_stringify': json.dumps,
            'md5': lambda s: hashlib.md5(str(s).encode()).hexdigest(),
            'sha256': lambda s: hashlib.sha256(str(s).encode()).hexdigest(),
            'sha1': lambda s: hashlib.sha1(str(s).encode()).hexdigest(),
            'sha512': lambda s: hashlib.sha512(str(s).encode()).hexdigest(),
            'hash': hash,
            'base64_encode': lambda s: base64.b64encode(str(s).encode()).decode(),
            'base64_decode': lambda s: base64.b64decode(str(s).encode()).decode(),
            'clock': time_mod.perf_counter,
            'time': time_mod.time,
            'sleep': time_mod.sleep,
            'input': input,
            'exit': sys.exit,
            'assert': self._builtin_assert,
            # String functions
            'upper': str.upper,
            'lower': str.lower,
            'strip': str.strip,
            'split': str.split,
            'join': lambda arr, sep: sep.join(str(x) for x in arr),
            'replace': str.replace,
            'replace_all': str.replace,
            'starts_with': str.startswith,
            'ends_with': str.endswith,
            'startswith': str.startswith,
            'endswith': str.endswith,
            'find': str.find,
            'index_of': str.find,
            'char_at': lambda s, i: s[int(i)] if int(i) < len(s) else '',
            'substring': lambda s, start, length=None: s[int(start):int(start)+int(length)] if length else s[int(start):],
            'count': lambda s, sub: s.count(sub),
            'contains': lambda s, sub: sub in s,
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
            'delete_file': os.remove,
            'list_dir': os.listdir,
            'mkdir': os.makedirs,
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
            'csv_parse': lambda s: [row.split(',') for row in s.strip().split('\n')],
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
        if isinstance(obj, (str, list, dict, tuple)):
            return len(obj)
        if hasattr(obj, '__len__'):
            return len(obj)
        raise VMError(f"len() not supported for {type(obj).__name__}")

    def _builtin_type(self, obj):
        if obj is None:           return "nil"
        if isinstance(obj, bool): return "bool"
        if isinstance(obj, int):  return "int"
        if isinstance(obj, float): return "float"
        if isinstance(obj, str):  return "string"
        if isinstance(obj, (list, tuple)): return "list"
        if hasattr(obj, 'elements'): return "list"   # IppList
        if isinstance(obj, dict): return "dict"
        if hasattr(obj, '_data') and hasattr(obj, 'add'): return "set"  # IppSet (BUG-NEW-M6)
        if hasattr(obj, 'data'): return "dict"       # IppDict
        if isinstance(obj, IppClass): return "class"
        if isinstance(obj, IppInstance): return obj.cls.name
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

    def run(self, chunk: Chunk = None) -> Any:
        if chunk:
            self.chunk = chunk
        if not self.chunk:
            return None

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
            try:
                opcode = OpCode(raw)
            except ValueError:
                raise VMError(f"Unknown opcode {raw} at ip={frame.ip}")

            if self.profiler.enabled:
                self.profiler.record_opcode(opcode)
            self.instruction_count += 1

            try:
                result = self._execute(opcode, frame)
            except VMError:
                raise
            except Exception as e:
                # wrap in VMError for structured handling
                exc = VMError(str(e))
                if self.exception_handlers:
                    self._handle_exception(exc, frame)
                    frame = self.frames[-1]
                    continue
                raise VMError(str(e)) from e

            if result is _RETURN_FRAME:
                ret_val = self.stack.pop() if self.stack else None
                # FIX BUG-NEW-M5: close any upvalues still open in the returning frame
                self._close_frame_upvalues(frame)
                # FIX BUG-N1: clear private-access flag when leaving a method
                if hasattr(frame, '_method_instance') and frame._method_instance is not None:
                    frame._method_instance._current_class = None
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
        # push the exception message for catch var
        self.stack.append(str(exc))
        # restore frame depth
        while len(self.frames) > handler.frame_depth:
            self.frames.pop()
        if not self.frames:
            raise exc
        frame = self.frames[-1]
        frame.ip = handler.target_ip

    def _execute(self, opcode: OpCode, frame: VMFrame) -> Any:
        code = frame.chunk.code
        constants = frame.chunk.constants
        ip = frame.ip

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
            cache_key = hash(name)
            cached = self._global_cache.get(cache_key)
            if cached is not _MISS:              # FIX: BUG-M5
                self.stack.append(cached)
            elif name in self.globals:
                val = self.globals[name]
                self._global_cache.set(cache_key, val)
                self.stack.append(val)
            else:
                raise VMError(f"Undefined variable '{name}'")

        elif opcode == OpCode.SET_GLOBAL:
            idx = code[ip + 1]
            name = constants[idx]
            val = self.stack[-1] if self.stack else None
            self.globals[name] = val
            self._global_cache.set(hash(name), val)

        elif opcode == OpCode.DEFINE_GLOBAL:
            idx = code[ip + 1]
            name = constants[idx]
            val = self.stack.pop() if self.stack else None
            self.globals[name] = val
            self._global_cache.set(hash(name), val)

        elif opcode == OpCode.DELETE_GLOBAL:
            idx = code[ip + 1]
            name = constants[idx]
            self.globals.pop(name, None)
            self._global_cache.cache.pop(hash(name), None)

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
            elif isinstance(obj, dict) and name in obj:
                self.stack[-1] = obj[name]
            elif hasattr(obj, name):
                self.stack[-1] = getattr(obj, name)
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
            if isinstance(obj, (list, tuple, str)):
                self.stack.append(obj[int(idx)])
            elif isinstance(obj, dict):
                self.stack.append(obj.get(idx))
            elif hasattr(obj, 'data'):
                # IppDict
                self.stack.append(obj.data.get(idx))
            elif hasattr(obj, 'elements'):
                # IppList
                self.stack.append(obj.elements[int(idx)])
            else:
                self.stack.append(None)

        elif opcode == OpCode.SET_INDEX:
            value = self.stack.pop()
            idx = self.stack.pop()
            obj = self.stack.pop()
            if isinstance(obj, list):
                obj[int(idx)] = value
            elif isinstance(obj, dict):
                obj[idx] = value
            self.stack.append(value)

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
            args = []
            for _ in range(argc):
                args.append(self.stack.pop() if self.stack else None)
            args.reverse()
            callee = self.stack.pop() if self.stack else None

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
                self.stack.append(Closure(proto.chunk, upvalue_cells))
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
            return _SUSPEND

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
            path_idx = code[ip+1] | (code[ip+2] << 8) | (code[ip+3] << 16)
            module_path = constants[path_idx] if path_idx < len(constants) else ""
            self.stack.append(module_path)

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
            self.stack.append(list(range(int(a), int(b))))

        # ── Arithmetic ───────────────────────────────────────────────────
        elif opcode == OpCode.ADD:
            b, a = self.stack.pop(), self.stack.pop()
            if isinstance(a, str) or isinstance(b, str):
                self.stack.append(self._intern_string(str(a) + str(b)))
            else:
                self.stack.append(a + b)

        elif opcode == OpCode.SUBTRACT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)

        elif opcode == OpCode.MULTIPLY:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)

        elif opcode == OpCode.DIVIDE:
            b, a = self.stack.pop(), self.stack.pop()
            if b == 0: raise VMError("Division by zero")
            self.stack.append(a / b)

        elif opcode == OpCode.MODULO:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a % b)

        elif opcode == OpCode.POWER:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a ** b)

        elif opcode == OpCode.FLOOR_DIV:
            b, a = self.stack.pop(), self.stack.pop()
            if b == 0: raise VMError("Division by zero")
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
            if self.exception_handlers:
                self._handle_exception(exc, frame)
                return _SUSPEND
            raise exc

        elif opcode == OpCode.TRY:
            offset = frame.chunk.read_int(ip + 1)
            target = ip + 4 + offset
            # FIX: BUG-V5 — push onto handler stack
            handler = ExceptionHandler(target, len(self.stack), len(self.frames))
            self.exception_handlers.append(handler)

        elif opcode == OpCode.TRY_END:
            # normal completion — discard handler
            if self.exception_handlers:
                self.exception_handlers.pop()

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
        if callable(callee) and not isinstance(callee, (Closure, IppFunction, IppClass, BoundMethod)):
            # built-in Python callable
            try:
                result = callee(*args)
            except VMError:
                raise
            except Exception as e:
                raise VMError(str(e))
            self.stack.append(result)
            return

        # FIX BUG-N2: recursion depth check for non-builtin calls
        self.call_depth += 1
        if self.call_depth > self.max_depth:
            self.call_depth -= 1
            raise VMError(f"Maximum recursion depth ({self.max_depth}) exceeded")

        if isinstance(callee, BoundMethod):
            self._call_method(callee.instance, callee.method, args, return_frame)
            return

        if isinstance(callee, IppClass):
            # Instantiate
            instance = IppInstance(callee)
            init = callee.get_method("init")
            if init:
                self._call_method(instance, init, args, return_frame)
                # After init, the instance (not init's return) is the value
                # We push instance after init frame completes
                # For now push it here; the RETURN_VAL will pop and re-push
                self.stack.append(instance)
            else:
                self.stack.append(instance)
            return

        if isinstance(callee, Closure):
            chunk = callee.chunk
        elif isinstance(callee, IppFunction):
            chunk = callee.chunk
        elif isinstance(callee, Chunk):
            chunk = callee
        else:
            raise VMError(f"Cannot call {type(callee).__name__}")

        if chunk is None:
            self.stack.append(None)
            return

        # FIX: BUG-M7 — push args onto stack BEFORE creating frame
        base = len(self.stack)
        for a in args:
            self.stack.append(a)

        new_frame = VMFrame(chunk,
                            closure=callee if isinstance(callee, Closure) else None,
                            function=callee,
                            stack_base=base)
        self.frames.append(new_frame)

    def _call_method(self, instance: IppInstance, method, args, return_frame):
        """Call a method with self as first arg. FIX: BUG-V8."""
        # FIX BUG-N2: recursion depth check
        self.call_depth += 1
        if self.call_depth > self.max_depth:
            self.call_depth -= 1
            raise VMError(f"Maximum recursion depth ({self.max_depth}) exceeded")
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
