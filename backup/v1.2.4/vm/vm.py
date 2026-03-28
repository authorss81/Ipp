from .bytecode import Chunk, OpCode, OpcodeInfo
from typing import List, Any, Dict, Optional, Callable
import math
import time
import sys
import os


class Profiler:
    def __init__(self):
        self.enabled = False
        self.opcode_counts: Dict[OpCode, int] = {}
        self.function_times: Dict[str, float] = {}
        self.memory_samples: List[int] = []
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
    
    def record_function_time(self, name: str, duration: float):
        if self.enabled:
            self.function_times[name] = self.function_times.get(name, 0) + duration
    
    def record_loop_iteration(self):
        if self.enabled:
            self.loop_iterations += 1
    
    def record_memory(self):
        if self.enabled:
            try:
                import psutil
                process = psutil.Process()
                self.memory_samples.append(process.memory_info().rss)
            except ImportError:
                pass
    
    def get_stats(self) -> dict:
        total_ops = sum(self.opcode_counts.values()) if self.opcode_counts else 0
        elapsed = time.perf_counter() - self.start_time if self.start_time else 0
        
        return {
            'total_instructions': total_ops,
            'elapsed_ms': elapsed * 1000,
            'instructions_per_ms': total_ops / (elapsed * 1000) if elapsed > 0 else 0,
            'opcode_counts': dict(self.opcode_counts),
            'function_calls': dict(self.call_counts),
            'function_times': dict(self.function_times),
            'loop_iterations': self.loop_iterations,
            'memory_samples': list(self.memory_samples),
        }
    
    def print_report(self):
        stats = self.get_stats()
        print("\n=== Profiler Report ===")
        print(f"Total Instructions: {stats['total_instructions']:,}")
        print(f"Elapsed Time: {stats['elapsed_ms']:.2f} ms")
        print(f"Instructions/ms: {stats['instructions_per_ms']:.2f}")
        print(f"Loop Iterations: {stats['loop_iterations']:,}")
        
        if stats['opcode_counts']:
            print("\nTop 10 Opcodes:")
            sorted_ops = sorted(stats['opcode_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
            for opcode, count in sorted_ops:
                pct = (count / stats['total_instructions']) * 100 if stats['total_instructions'] > 0 else 0
                print(f"  {opcode.name}: {count:,} ({pct:.1f}%)")
        
        if stats['function_calls']:
            print("\nFunction Calls:")
            for name, count in sorted(stats['function_calls'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {name}: {count:,}")


class InlineCache:
    def __init__(self, max_size=1024):
        self.cache: Dict[int, Any] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: int) -> Optional[Any]:
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: int, value: Any):
        if len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key] = value
    
    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0


class ObjectPool:
    def __init__(self, factory, max_size=1024):
        self.factory = factory
        self.max_size = max_size
        self.pool: List[Any] = []
        self.allocations = 0
    
    def acquire(self):
        if self.pool:
            return self.pool.pop()
        self.allocations += 1
        return self.factory()
    
    def release(self, obj):
        if len(self.pool) < self.max_size:
            self.pool.append(obj)
    
    def prewarm(self, count: int):
        for _ in range(count):
            self.pool.append(self.factory())


class VMFrame:
    def __init__(self, chunk: Chunk, closure=None, function=None):
        self.chunk = chunk
        self.closure = closure
        self.function = function
        self.ip = 0
        self.stack_base = 0


class Closure:
    def __init__(self, chunk: Chunk, upvalues: List = None):
        self.chunk = chunk
        self.upvalues = upvalues or []


class IppFunction:
    def __init__(self, name: str = "<script>", arity: int = 0, chunk: Chunk = None, is_method: bool = False):
        self.name = name
        self.arity = arity
        self.chunk = chunk
        self.is_method = is_method


class IppClass:
    def __init__(self, name: str, superclass: 'IppClass' = None):
        self.name = name
        self.superclass = superclass
        self.methods: Dict[str, IppFunction] = {}
    
    def get_method(self, name: str) -> Optional[IppFunction]:
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
    
    def get(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        method = self.cls.get_method(name)
        if method:
            if isinstance(method.chunk, Closure):
                return lambda *args: method.chunk.chunk
            return method
        raise VMError(f"Undefined property: {name}")
    
    def set(self, name: str, value: Any):
        self.fields[name] = value


class OptimizedVM:
    CONST_TRUE = True
    CONST_FALSE = False
    CONST_NIL = None
    
    def __init__(self, chunk: Chunk = None):
        self.chunk = chunk
        self.stack: List[Any] = []
        self.frames: List[VMFrame] = []
        self.globals: Dict[str, Any] = {}
        self.open_upvalues: List = []
        self.exception_handler: Optional[tuple] = None
        self.running = True
        self._return_value = None
        
        self.call_count = 0
        self.instruction_count = 0
        
        self._global_cache = InlineCache(max_size=2048)
        self._method_cache = InlineCache(max_size=2048)
        self._string_cache: Dict[str, str] = {}
        self._type_cache: Dict[type, str] = {}
        
        self.profiler = Profiler()
        self._hot_functions: Dict[str, int] = {}
        self._jit_threshold = 100
        
        self._init_builtins()
    
    def _init_builtins(self):
        import random
        import json
        import datetime
        import base64
        import hashlib
        
        self.globals.update({
            'print': self._builtin_print,
            'len': len,
            'type': self._builtin_type,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': self._builtin_sum,
            'range': self._builtin_range,
            'random': random.random,
            'randint': random.randint,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'sqrt': math.sqrt,
            'pow': pow,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'floor': math.floor,
            'ceil': math.ceil,
            'round': round,
            'json_parse': json.loads,
            'json_stringify': json.dumps,
            'datetime_now': datetime.datetime.now,
            'md5': lambda s: hashlib.md5(s.encode()).hexdigest(),
            'sha256': lambda s: hashlib.sha256(s.encode()).hexdigest(),
            'base64_encode': lambda s: base64.b64encode(s.encode()).decode(),
            'base64_decode': lambda s: base64.b64decode(s.encode()).decode(),
            'clock': time.perf_counter,
            'input': input,
        })
        
        for k in self.globals:
            self._global_cache.set(hash(k), self.globals[k])
    
    def _builtin_print(self, *args):
        output = []
        for arg in args:
            if arg is None:
                output.append("nil")
            elif isinstance(arg, bool):
                output.append("true" if arg else "false")
            elif isinstance(arg, (int, float)):
                if isinstance(arg, float) and arg.is_integer():
                    output.append(str(int(arg)))
                else:
                    output.append(str(arg))
            elif isinstance(arg, (list, tuple)):
                output.append(str(arg))
            else:
                output.append(str(arg))
        print(" ".join(output))
        return None
    
    def _builtin_type(self, obj):
        if obj is None:
            return "nil"
        if isinstance(obj, bool):
            return "bool"
        if isinstance(obj, int):
            return "number"
        if isinstance(obj, float):
            return "number"
        if isinstance(obj, str):
            return "string"
        if isinstance(obj, (list, tuple)):
            return "list"
        if isinstance(obj, dict):
            return "dict"
        if isinstance(obj, IppClass):
            return "class"
        if isinstance(obj, IppInstance):
            return "instance"
        return type(obj).__name__
    
    def _builtin_sum(self, *args):
        if len(args) == 1 and hasattr(args[0], '__iter__') and not isinstance(args[0], str):
            return sum(args[0])
        return sum(args)
    
    def _builtin_range(self, *args):
        if len(args) == 1:
            return list(range(args[0]))
        elif len(args) == 2:
            return list(range(args[0], args[1]))
        elif len(args) == 3:
            return list(range(args[0], args[1], args[2]))
        return []
    
    def _intern_string(self, s: str) -> str:
        if s not in self._string_cache:
            self._string_cache[s] = s
        return self._string_cache[s]
    
    def reset(self):
        self.stack.clear()
        self.frames.clear()
        self.open_upvalues.clear()
        self.exception_handler = None
        self.running = True
        self._return_value = None
    
    def run(self, chunk: Chunk = None) -> Any:
        if chunk:
            self.chunk = chunk
        
        if not self.chunk:
            return None
        
        frame = VMFrame(self.chunk)
        self.frames.append(frame)
        frame.stack_base = 0
        
        while self.running and frame.ip < len(frame.chunk.code):
            self.instruction_count += 1
            
            opcode = OpCode(frame.chunk.code[frame.ip])
            
            if self.profiler.enabled:
                self.profiler.record_opcode(opcode)
            
            try:
                result = self._execute_opcode(opcode, frame)
                if result is not None:
                    if result == VM.SUSPEND:
                        continue
                    elif result == VM.RETURN_FRAME:
                        self._return_value = self.stack.pop() if self.stack else None
                        if len(self.frames) > 1:
                            self.frames.pop()
                            frame = self.frames[-1]
                            self.stack.append(self._return_value)
                            continue
                        else:
                            self.running = False
                            return self._return_value
                    else:
                        self.running = False
                        return result
            except Exception as e:
                if self.exception_handler:
                    target_ip, stack_len = self.exception_handler
                    frame.ip = target_ip
                    while len(self.stack) > stack_len:
                        self.stack.pop()
                    self.stack.append(str(e))
                    self.exception_handler = None
                else:
                    raise VMError(str(e))
            
            frame.ip += self._opcode_size(opcode)
        
        if self.frames:
            self.frames.pop()
        return self._return_value if self.stack else None
    
    def _opcode_size(self, opcode: OpCode) -> int:
        if opcode in (OpCode.CONSTANT, OpCode.GET_GLOBAL, OpCode.SET_GLOBAL,
                      OpCode.DEFINE_GLOBAL, OpCode.GET_LOCAL, OpCode.SET_LOCAL,
                      OpCode.GET_PROPERTY, OpCode.SET_PROPERTY, OpCode.GET_METHOD,
                      OpCode.METHOD, OpCode.CLASS, OpCode.SUBCLASS,
                      OpCode.POP, OpCode.LIST, OpCode.DICT, OpCode.TUPLE,
                      OpCode.BREAK, OpCode.CONTINUE, OpCode.RETURN,
                      OpCode.RETURN_VAL, OpCode.THROW):
            return 2
        elif opcode in (OpCode.JUMP_IF_FALSE_POP, OpCode.JUMP_IF_TRUE_POP):
            return 3
        elif opcode in (OpCode.JUMP, OpCode.LOOP, OpCode.TRY, OpCode.CATCH,
                        OpCode.TRY_END, OpCode.MATCH, OpCode.IMPORT, OpCode.END_IMPORT):
            return 4
        elif opcode == OpCode.CONSTANT_LONG:
            return 4
        elif opcode == OpCode.CALL:
            return 2
        return 1
    
    SUSPEND = object()
    RETURN_FRAME = object()
    
    def _execute_opcode(self, opcode: OpCode, frame: VMFrame) -> Any:
        code = frame.chunk.code
        constants = frame.chunk.constants
        
        if opcode == OpCode.HALT:
            self.running = False
            return None
        
        elif opcode == OpCode.NOP:
            pass
        
        elif opcode == OpCode.CONSTANT:
            idx = code[frame.ip + 1]
            self.stack.append(constants[idx])
        
        elif opcode == OpCode.CONSTANT_LONG:
            idx = code[frame.ip + 1] | (code[frame.ip + 2] << 8) | (code[frame.ip + 3] << 16)
            self.stack.append(constants[idx])
        
        elif opcode == OpCode.NIL:
            self.stack.append(self.CONST_NIL)
        elif opcode == OpCode.TRUE:
            self.stack.append(self.CONST_TRUE)
        elif opcode == OpCode.FALSE:
            self.stack.append(self.CONST_FALSE)
        
        elif opcode == OpCode.POP:
            if self.stack:
                self.stack.pop()
        
        elif opcode == OpCode.DUP:
            if self.stack:
                self.stack.append(self.stack[-1])
        
        elif opcode == OpCode.DUP2:
            if len(self.stack) >= 2:
                self.stack.append(self.stack[-2])
                self.stack.append(self.stack[-2])
        
        elif opcode == OpCode.SWAP:
            if len(self.stack) >= 2:
                self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
        
        elif opcode == OpCode.GET_GLOBAL:
            idx = code[frame.ip + 1]
            name = constants[idx]
            cache_key = hash(name)
            
            cached = self._global_cache.get(cache_key)
            if cached is not None:
                self.stack.append(cached)
            elif name in self.globals:
                val = self.globals[name]
                self._global_cache.set(cache_key, val)
                self.stack.append(val)
            else:
                raise VMError(f"Undefined variable: {name}")
        
        elif opcode == OpCode.SET_GLOBAL:
            idx = code[frame.ip + 1]
            name = constants[idx]
            if self.stack:
                self.globals[name] = self.stack[-1]
                self._global_cache.set(hash(name), self.stack[-1])
        
        elif opcode == OpCode.DEFINE_GLOBAL:
            idx = code[frame.ip + 1]
            name = constants[idx]
            if self.stack:
                self.globals[name] = self.stack.pop()
                self._global_cache.set(hash(name), self.globals[name])
            else:
                self.globals[name] = None
        
        elif opcode == OpCode.GET_LOCAL:
            idx = code[frame.ip + 1]
            if idx < len(self.stack):
                self.stack.append(self.stack[idx])
        
        elif opcode == OpCode.SET_LOCAL:
            idx = code[frame.ip + 1]
            if idx < len(self.stack):
                self.stack[idx] = self.stack[-1]
        
        elif opcode == OpCode.GET_UPVALUE:
            idx = code[frame.ip + 1]
            if frame.closure and idx < len(frame.closure.upvalues):
                self.stack.append(frame.closure.upvalues[idx])
        
        elif opcode == OpCode.SET_UPVALUE:
            idx = code[frame.ip + 1]
            if frame.closure and idx < len(frame.closure.upvalues):
                frame.closure.upvalues[idx] = self.stack[-1]
        
        elif opcode == OpCode.GET_PROPERTY:
            idx = code[frame.ip + 1]
            name = constants[idx]
            obj = self.stack[-1]
            
            if isinstance(obj, IppInstance):
                self.stack[-1] = obj.get(name)
            elif hasattr(obj, name):
                self.stack[-1] = getattr(obj, name)
            elif isinstance(obj, dict) and name in obj:
                self.stack[-1] = obj[name]
            else:
                raise VMError(f"Property not found: {name}")
        
        elif opcode == OpCode.SET_PROPERTY:
            idx = code[frame.ip + 1]
            name = constants[idx]
            value = self.stack.pop()
            obj = self.stack[-1]
            
            if isinstance(obj, IppInstance):
                obj.set(name, value)
            elif hasattr(obj, '__dict__'):
                setattr(obj, name, value)
            elif isinstance(obj, dict):
                obj[name] = value
        
        elif opcode == OpCode.GET_SUPER:
            idx = code[frame.ip + 1]
            name = constants[idx]
            obj = self.stack.pop()
            if isinstance(obj, IppClass):
                method = obj.get_method(name)
                self.stack.append(method)
            else:
                raise VMError(f"Cannot get super from non-class")
        
        elif opcode == OpCode.GET_INDEX:
            idx = self.stack.pop()
            obj = self.stack.pop()
            if isinstance(obj, (list, tuple, str)):
                self.stack.append(obj[int(idx)])
            elif isinstance(obj, dict):
                self.stack.append(obj.get(idx))
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
        
        elif opcode == OpCode.ADD:
            b = self.stack.pop()
            a = self.stack.pop()
            if isinstance(a, str) or isinstance(b, str):
                self.stack.append(self._intern_string(str(a) + str(b)))
            elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.stack.append(a + b)
            else:
                try:
                    self.stack.append(a + b)
                except:
                    self.stack.append(str(a) + str(b))
        
        elif opcode == OpCode.SUBTRACT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        
        elif opcode == OpCode.MULTIPLY:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        
        elif opcode == OpCode.DIVIDE:
            b = self.stack.pop()
            a = self.stack.pop()
            if b == 0:
                raise VMError("Division by zero")
            self.stack.append(a / b)
        
        elif opcode == OpCode.MODULO:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a % b)
        
        elif opcode == OpCode.POWER:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a ** b)
        
        elif opcode == OpCode.FLOOR_DIV:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a) // int(b))
        
        elif opcode == OpCode.BIT_AND:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a) & int(b))
        
        elif opcode == OpCode.BIT_OR:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a) | int(b))
        
        elif opcode == OpCode.BIT_XOR:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a) ^ int(b))
        
        elif opcode == OpCode.BIT_NOT:
            a = self.stack.pop()
            self.stack.append(~int(a))
        
        elif opcode == OpCode.SHIFT_LEFT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a) << int(b))
        
        elif opcode == OpCode.SHIFT_RIGHT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a) >> int(b))
        
        elif opcode == OpCode.NEGATE:
            a = self.stack.pop()
            self.stack.append(-a)
        
        elif opcode == OpCode.NOT:
            a = self.stack.pop()
            self.stack.append(not self._is_truthy(a))
        
        elif opcode == OpCode.INCREMENT:
            a = self.stack.pop()
            self.stack.append(a + 1)
        
        elif opcode == OpCode.DECREMENT:
            a = self.stack.pop()
            self.stack.append(a - 1)
        
        elif opcode == OpCode.EQUAL:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a == b)
        
        elif opcode == OpCode.NOT_EQUAL:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a != b)
        
        elif opcode == OpCode.LESS:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a < b)
        
        elif opcode == OpCode.LESS_EQUAL:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a <= b)
        
        elif opcode == OpCode.GREATER:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a > b)
        
        elif opcode == OpCode.GREATER_EQUAL:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a >= b)
        
        elif opcode == OpCode.JUMP:
            offset = frame.chunk.read_int(frame.ip + 1)
            frame.ip = frame.ip + 3 + offset
            return self.SUSPEND
        
        elif opcode == OpCode.JUMP_IF_FALSE:
            offset = frame.chunk.read_int(frame.ip + 1)
            if not self._is_truthy(self.stack[-1]):
                frame.ip = frame.ip + 3 + offset
                return self.SUSPEND
        
        elif opcode == OpCode.JUMP_IF_TRUE:
            offset = frame.chunk.read_int(frame.ip + 1)
            if self._is_truthy(self.stack[-1]):
                frame.ip = frame.ip + 3 + offset
                return self.SUSPEND
        
        elif opcode == OpCode.JUMP_IF_FALSE_POP:
            offset = frame.chunk.read_int(frame.ip + 1)
            val = self.stack.pop()
            if not self._is_truthy(val):
                frame.ip = frame.ip + 3 + offset
                return self.SUSPEND
        
        elif opcode == OpCode.JUMP_IF_TRUE_POP:
            offset = frame.chunk.read_int(frame.ip + 1)
            val = self.stack.pop()
            if self._is_truthy(val):
                frame.ip = frame.ip + 3 + offset
                return self.SUSPEND
        
        elif opcode == OpCode.LOOP:
            offset = frame.chunk.read_int(frame.ip + 1)
            frame.ip = frame.ip - offset - 3
            return self.SUSPEND
        
        elif opcode == OpCode.MATCH:
            pass
        
        elif opcode == OpCode.CALL:
            argc = code[frame.ip + 1]
            
            if len(self.stack) < argc + 1:
                raise VMError("Not enough arguments on stack")
            
            callee = self.stack[-argc - 1] if argc > 0 else self.stack[-1]
            
            if isinstance(callee, IppClass):
                instance = IppInstance(callee)
                init_method = callee.get_method("init")
                if init_method:
                    if isinstance(init_method, IppFunction):
                        self.call_count += 1
                        for _ in range(argc):
                            self.stack.pop()
                        self.stack.pop()
                        self.stack.append(init_method.chunk)
                        self.stack.append(instance)
                        new_frame = VMFrame(init_method.chunk, function=init_method)
                        new_frame.stack_base = len(self.stack)
                        self.frames.append(new_frame)
                        return self.SUSPEND
                for _ in range(argc):
                    self.stack.pop()
                self.stack.pop()
                self.stack.append(instance)
            elif isinstance(callee, IppInstance):
                raise VMError("Cannot call IppInstance directly")
            else:
                args = []
                for _ in range(argc):
                    if self.stack:
                        args.append(self.stack.pop())
                args.reverse()
                callee = self.stack.pop()
                
                if callable(callee):
                    try:
                        if argc == 0:
                            result = callee()
                        else:
                            result = callee(*args)
                        self.stack.append(result)
                    except Exception as e:
                        raise VMError(str(e))
                elif isinstance(callee, IppFunction):
                    self.call_count += 1
                    new_frame = VMFrame(callee.chunk, function=callee)
                    new_frame.stack_base = len(self.stack)
                    self.frames.append(new_frame)
                    return self.SUSPEND
                elif isinstance(callee, Chunk):
                    self.call_count += 1
                    new_frame = VMFrame(callee)
                    new_frame.stack_base = len(self.stack)
                    self.frames.append(new_frame)
                    return self.SUSPEND
                else:
                    raise VMError(f"Cannot call {type(callee)}")
        
        elif opcode == OpCode.INVOKE:
            argc = code[frame.ip + 1]
            args = []
            for _ in range(argc):
                if self.stack:
                    args.append(self.stack.pop())
            args.reverse()
            method_name = constants[code[frame.ip + 2]] if frame.ip + 2 < len(code) else None
            obj = self.stack.pop()
            
            if isinstance(obj, IppInstance):
                method = obj.cls.get_method(method_name)
                if method and method.chunk:
                    new_frame = VMFrame(method.chunk, function=method)
                    new_frame.stack_base = len(self.stack)
                    self.stack.append(obj)
                    for arg in args:
                        self.stack.append(arg)
                    self.frames.append(new_frame)
                    return self.SUSPEND
            raise VMError(f"Method {method_name} not found")
        
        elif opcode == OpCode.SUPER_INVOKE:
            argc = code[frame.ip + 1]
            method_name = constants[code[frame.ip + 2]] if frame.ip + 2 < len(code) else None
            args = []
            for _ in range(argc):
                if self.stack:
                    args.append(self.stack.pop())
            args.reverse()
            superclass = self.stack.pop()
            obj = self.stack.pop()
            
            if isinstance(superclass, IppClass):
                method = superclass.get_method(method_name)
                if method and method.chunk:
                    new_frame = VMFrame(method.chunk, function=method)
                    new_frame.stack_base = len(self.stack)
                    self.stack.append(obj)
                    for arg in args:
                        self.stack.append(arg)
                    self.frames.append(new_frame)
                    return self.SUSPEND
            raise VMError(f"Super method {method_name} not found")
        
        elif opcode == OpCode.TAIL_CALL:
            argc = code[frame.ip + 1]
            args = []
            for _ in range(argc):
                if self.stack:
                    args.append(self.stack.pop())
            args.reverse()
            callee = self.stack.pop()
            
            if isinstance(callee, IppFunction):
                self.call_count += 1
                self.frames.pop()
                new_frame = VMFrame(callee.chunk, function=callee)
                new_frame.stack_base = len(self.stack)
                self.frames.append(new_frame)
                for arg in args:
                    self.stack.append(arg)
                return self.SUSPEND
            elif isinstance(callee, Chunk):
                self.call_count += 1
                self.frames.pop()
                new_frame = VMFrame(callee)
                new_frame.stack_base = len(self.stack)
                self.frames.append(new_frame)
                for arg in args:
                    self.stack.append(arg)
                return self.SUSPEND
            raise VMError(f"Cannot tail call {type(callee)}")
        
        elif opcode == OpCode.CLOSURE:
            idx = code[frame.ip + 1]
            const = constants[idx]
            if isinstance(const, Chunk):
                closure = Closure(const)
                self.stack.append(closure)
            else:
                self.stack.append(const)
        
        elif opcode == OpCode.CLOSE_UPVALUE:
            if self.open_upvalues:
                self.open_upvalues.pop()
        
        elif opcode == OpCode.GET_CAPTURED:
            if frame.closure and frame.closure.upvalues:
                self.stack.append(frame.closure.upvalues[0])
        
        elif opcode == OpCode.RETURN:
            return self.RETURN_FRAME
        
        elif opcode == OpCode.RETURN_VAL:
            return self.RETURN_FRAME
        
        elif opcode == OpCode.YIELD:
            return self.SUSPEND
        
        elif opcode == OpCode.CLASS:
            idx = code[frame.ip + 1]
            name = constants[idx]
            cls = IppClass(name)
            self.stack.append(cls)
        
        elif opcode == OpCode.SUBCLASS:
            superclass = self.stack.pop()
            if isinstance(superclass, IppClass):
                self.stack[-1].superclass = superclass
            else:
                raise VMError("Superclass must be a class")
        
        elif opcode == OpCode.METHOD:
            idx = code[frame.ip + 1]
            name = constants[idx]
            method = self.stack.pop()
            if isinstance(self.stack[-1], IppClass):
                if isinstance(method, Chunk):
                    func = IppFunction(name, 0, method, is_method=True)
                    self.stack[-1].methods[name] = func
                elif callable(method):
                    self.stack[-1].methods[name] = method
        
        elif opcode == OpCode.END_METHOD:
            pass
        
        elif opcode == OpCode.GET_METHOD:
            idx = code[frame.ip + 1]
            name = constants[idx]
            obj = self.stack[-1]
            if isinstance(obj, IppClass):
                method = obj.get_method(name)
                if method:
                    self.stack.append(method)
                else:
                    raise VMError(f"Undefined method: {name}")
            elif isinstance(obj, IppInstance):
                self.stack.append(obj.get(name))
        
        elif opcode == OpCode.IMPORT:
            offset = frame.chunk.read_int(frame.ip + 1)
            idx = code[frame.ip + 2] if frame.ip + 2 < len(code) else 0
            module_path = constants[idx] if idx < len(constants) else ""
            self.stack.append(module_path)
        
        elif opcode == OpCode.END_IMPORT:
            pass
        
        elif opcode == OpCode.LIST:
            count = code[frame.ip + 1]
            if count <= len(self.stack):
                items = self.stack[-count:]
                del self.stack[-count:]
            else:
                items = self.stack[:]
                self.stack.clear()
            self.stack.append(list(items) if items else [])
        
        elif opcode == OpCode.DICT:
            count = code[frame.ip + 1]
            d = {}
            for _ in range(count):
                if self.stack:
                    value = self.stack.pop()
                else:
                    value = None
                if self.stack:
                    key = self.stack.pop()
                else:
                    key = None
                d[key] = value
            self.stack.append(d)
        
        elif opcode == OpCode.TUPLE:
            count = code[frame.ip + 1]
            items = self.stack[-count:] if count <= len(self.stack) else self.stack[:]
            if count <= len(self.stack):
                del self.stack[-count:]
            self.stack.append(tuple(items) if items else ())
        
        elif opcode == OpCode.SPREAD:
            obj = self.stack.pop()
            if hasattr(obj, '__iter__') and not isinstance(obj, str):
                for item in obj:
                    self.stack.append(item)
        
        elif opcode == OpCode.RANGE:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(list(range(int(a), int(b))))
        
        elif opcode == OpCode.NULLISH:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a if a is not None else b)
        
        elif opcode == OpCode.OPTIONAL_CHAIN:
            idx = code[frame.ip + 1]
            name = constants[idx]
            obj = self.stack.pop()
            if obj is None:
                self.stack.append(None)
            elif hasattr(obj, name):
                self.stack.append(getattr(obj, name))
            else:
                self.stack.append(None)
        
        elif opcode == OpCode.OPTIONAL_CHAIN_END:
            pass
        
        elif opcode == OpCode.THROW:
            msg = self.stack.pop() if self.stack else "Unknown error"
            raise VMError(str(msg))
        
        elif opcode == OpCode.TRY:
            offset = frame.chunk.read_int(frame.ip + 1)
            target = frame.ip + 4 + offset
            self.exception_handler = (target, len(self.stack))
        
        elif opcode == OpCode.TRY_END:
            self.exception_handler = None
        
        elif opcode == OpCode.CATCH:
            offset = frame.chunk.read_int(frame.ip + 1)
            target = frame.ip + 4 + offset
            self.exception_handler = (target, len(self.stack))
        
        elif opcode == OpCode.CATCH_END:
            self.exception_handler = None
        
        elif opcode == OpCode.FINALLY:
            pass
        
        elif opcode == OpCode.END_FINALLY:
            pass
        
        elif opcode == OpCode.EXCEPTION:
            self.stack.append("Exception")
        
        elif opcode == OpCode.WITH_ENTER:
            resource = self.stack.pop() if self.stack else None
            self.stack.append(resource)
        
        elif opcode == OpCode.WITH_EXIT:
            pass
        
        elif opcode == OpCode.BREAK:
            pass
        
        elif opcode == OpCode.CONTINUE:
            pass
        
        elif opcode == OpCode.CONCATENATE:
            count = code[frame.ip + 1] if frame.ip + 1 < len(code) else 2
            parts = []
            for _ in range(count):
                if self.stack:
                    parts.append(str(self.stack.pop()))
            parts.reverse()
            self.stack.append(self._intern_string("".join(parts)))
        
        elif opcode == OpCode.CONCAT_COUNT:
            count = code[frame.ip + 1]
            parts = []
            for _ in range(count):
                if self.stack:
                    parts.append(str(self.stack.pop()))
            parts.reverse()
            self.stack.append("".join(parts))
        
        return None
    
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


class VM(OptimizedVM):
    pass


def execute_bytecode(chunk: Chunk) -> Any:
    vm = VM(chunk)
    return vm.run()


def benchmark_vm(chunk: Chunk, iterations: int = 1000) -> dict:
    vm = VM(chunk)
    
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
        'cache_hits': vm._global_cache.hits,
        'cache_misses': vm._global_cache.misses,
    }


def compare_performance(source: str, iterations: int = 100) -> dict:
    from ipp.lexer.lexer import tokenize
    from ipp.parser.parser import parse
    from ipp.interpreter.interpreter import Interpreter
    
    tokens = tokenize(source)
    ast = parse(tokens)
    
    interpreter_times = []
    for _ in range(iterations):
        interp = Interpreter()
        start = time.perf_counter()
        interp.run(ast)
        end = time.perf_counter()
        interpreter_times.append(end - start)
    
    from .compiler import compile_ast
    chunk = compile_ast(ast)
    
    bytecode_times = []
    for _ in range(iterations):
        vm = VM()
        start = time.perf_counter()
        vm.run(chunk)
        end = time.perf_counter()
        bytecode_times.append(end - start)
    
    interp_avg = sum(interpreter_times) / len(interpreter_times)
    bytecode_avg = sum(bytecode_times) / len(bytecode_times)
    
    return {
        'interpreter_avg_ms': interp_avg * 1000,
        'bytecode_avg_ms': bytecode_avg * 1000,
        'speedup': interp_avg / bytecode_avg if bytecode_avg > 0 else 0,
        'interpreter_total_ms': sum(interpreter_times) * 1000,
        'bytecode_total_ms': sum(bytecode_times) * 1000,
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
    from .compiler import compile_ast
    
    tokens = tokenize(source)
    ast = parse(tokens)
    chunk = compile_ast(ast)
    
    return profile_vm(chunk, iterations)


def profile_and_report(source: str, iterations: int = 100):
    from ipp.lexer.lexer import tokenize
    from ipp.parser.parser import parse
    from .compiler import compile_ast
    
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
