from .bytecode import Chunk, OpCode, OpcodeInfo
from typing import List, Any, Dict, Optional
import math
import time


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
    def __init__(self, chunk: Chunk, closure: 'Closure' = None):
        self.chunk = chunk
        self.closure = closure
        self.ip = 0
        self.stack_base = 0


class Closure:
    def __init__(self, chunk: Chunk, upvalues: List = None):
        self.chunk = chunk
        self.upvalues = upvalues or []


class IppFunction:
    def __init__(self, name: str = "<script>", arity: int = 0, chunk: Chunk = None):
        self.name = name
        self.arity = arity
        self.chunk = chunk


class VMError(Exception):
    pass


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
        self.exception_handler = None
        self.running = True
        
        self.call_count = 0
        self.instruction_count = 0
        
        self._global_cache = InlineCache(max_size=2048)
        self._method_cache = InlineCache(max_size=2048)
        self._string_cache: Dict[str, str] = {}
        
        self._init_builtins()
    
    def _init_builtins(self):
        import sys
        import os
        import math
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
            'range': range,
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
            'datetime': datetime.datetime.now,
            'md5': lambda s: hashlib.md5(s.encode()).hexdigest(),
            'sha256': lambda s: hashlib.sha256(s.encode()).hexdigest(),
            'base64_encode': lambda s: base64.b64encode(s.encode()).decode(),
            'base64_decode': lambda s: base64.b64decode(s.encode()).decode(),
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
        return type(obj).__name__
    
    def _builtin_sum(self, *args):
        total = 0
        for arg in args:
            if hasattr(arg, '__iter__') and not isinstance(arg, str):
                total += sum(arg)
            else:
                total += arg
        return total
    
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
    
    def run(self, chunk: Chunk = None) -> Any:
        if chunk:
            self.chunk = chunk
        
        if not self.chunk:
            return None
        
        frame = VMFrame(self.chunk)
        self.frames.append(frame)
        
        result = None
        
        while self.running and frame.ip < len(frame.chunk.code):
            self.instruction_count += 1
            
            opcode = OpCode(frame.chunk.code[frame.ip])
            
            try:
                result = self._execute_opcode_fast(opcode, frame)
            except Exception as e:
                if self.exception_handler:
                    frame.ip = self.exception_handler
                    self.stack.append(str(e))
                else:
                    raise VMError(str(e))
            
            if result is not None and result != VM.SUSPEND:
                self.running = False
            
            frame.ip += self._opcode_size(opcode)
        
        self.frames.pop()
        return result if self.stack else result
    
    def _opcode_size(self, opcode: OpCode) -> int:
        if opcode in (OpCode.CONSTANT, OpCode.GET_GLOBAL, OpCode.SET_GLOBAL,
                      OpCode.DEFINE_GLOBAL, OpCode.GET_LOCAL, OpCode.SET_LOCAL,
                      OpCode.GET_PROPERTY, OpCode.SET_PROPERTY, OpCode.GET_METHOD,
                      OpCode.METHOD, OpCode.CALL, OpCode.POP, OpCode.LIST, OpCode.DICT,
                      OpCode.JUMP_IF_FALSE_POP, OpCode.JUMP_IF_TRUE_POP):
            return 2
        elif opcode in (OpCode.JUMP, OpCode.LOOP, OpCode.TRY, OpCode.CATCH,
                        OpCode.TRY_END, OpCode.MATCH):
            return 4
        elif opcode == OpCode.CONSTANT_LONG:
            return 4
        return 1
    
    SUSPEND = object()
    
    def _execute_opcode_fast(self, opcode: OpCode, frame: VMFrame) -> Any:
        code = frame.chunk.code
        constants = frame.chunk.constants
        
        if opcode == OpCode.HALT:
            self.running = False
            return None
        
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
            if idx < len(self.stack) and len(self.stack) > 1:
                self.stack[idx] = self.stack[-1]
        
        elif opcode == OpCode.GET_PROPERTY:
            idx = code[frame.ip + 1]
            name = constants[idx]
            obj = self.stack[-1]
            
            cache_key = hash((id(type(obj)), name))
            cached = self._method_cache.get(cache_key)
            
            if cached is not None:
                self.stack[-1] = cached(obj) if callable(cached) else cached
            elif hasattr(obj, name):
                self._method_cache.set(cache_key, getattr(obj, name))
                self.stack[-1] = getattr(obj, name)
            elif isinstance(obj, dict) and name in obj:
                self._method_cache.set(cache_key, obj[name])
                self.stack[-1] = obj[name]
            else:
                raise VMError(f"Property not found: {name}")
        
        elif opcode == OpCode.SET_PROPERTY:
            idx = code[frame.ip + 1]
            name = constants[idx]
            value = self.stack[-2]
            obj = self.stack[-1]
            if hasattr(obj, '__dict__'):
                setattr(obj, name, value)
            elif isinstance(obj, dict):
                obj[name] = value
        
        elif opcode == OpCode.ADD:
            b = self.stack.pop()
            a = self.stack.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.stack.append(a + b)
            elif isinstance(a, str) and isinstance(b, str):
                self.stack.append(self._intern_string(a + b))
            else:
                self.stack.append(a + b)
        
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
        
        elif opcode == OpCode.NEGATE:
            a = self.stack.pop()
            self.stack.append(-a)
        
        elif opcode == OpCode.NOT:
            a = self.stack.pop()
            self.stack.append(not a)
        
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
            frame.ip = frame.ip + 4 + offset - 1
        
        elif opcode == OpCode.JUMP_IF_FALSE_POP:
            offset = frame.chunk.read_int(frame.ip + 1)
            val = self.stack.pop()
            if not self._is_truthy(val):
                frame.ip = frame.ip + 4 + offset - 1
        
        elif opcode == OpCode.LOOP:
            offset = frame.chunk.read_int(frame.ip + 1)
            frame.ip = frame.ip - offset - 3
        
        elif opcode == OpCode.LIST:
            count = code[frame.ip + 1]
            items = self.stack[-count:]
            del self.stack[-count:]
            self.stack.append(items)
        
        elif opcode == OpCode.DICT:
            count = code[frame.ip + 1]
            d = {}
            for _ in range(count):
                value = self.stack.pop()
                key = self.stack.pop()
                d[key] = value
            self.stack.append(d)
        
        elif opcode == OpCode.RANGE:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(range(int(a), int(b)))
        
        elif opcode == OpCode.CALL:
            argc = code[frame.ip + 1]
            args = self.stack[-argc:]
            del self.stack[-argc:]
            callee = self.stack.pop()
            
            if callable(callee):
                try:
                    result = callee(*args)
                    self.stack.append(result)
                except Exception as e:
                    raise VMError(str(e))
            elif isinstance(callee, IppFunction):
                self.call_count += 1
                new_frame = VMFrame(callee.chunk)
                self.frames.append(new_frame)
                return self.SUSPEND
            else:
                raise VMError(f"Cannot call non-function: {type(callee)}")
        
        elif opcode == OpCode.RETURN_VAL:
            result = self.stack.pop() if self.stack else None
            self.frames.pop()
            if self.frames:
                self.stack.append(result)
            else:
                return result
        
        elif opcode == OpCode.RETURN:
            self.frames.pop()
            if self.frames:
                self.stack.append(None)
            else:
                return None
        
        elif opcode == OpCode.CLASS:
            idx = code[frame.ip + 1]
            name = constants[idx]
            self.stack.append(type(name, (), {}))
        
        elif opcode == OpCode.NOP:
            pass
        
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
