from enum import IntEnum
from typing import List, Any


class OpCode(IntEnum):
    # Constants
    CONSTANT = 0
    CONSTANT_LONG = 1
    NIL = 2
    TRUE = 3
    FALSE = 4
    
    # Stack operations
    POP = 5
    DUP = 6
    DUP2 = 7
    SWAP = 8
    
    # Local variables
    GET_LOCAL = 9
    SET_LOCAL = 10
    DELETE_LOCAL = 11
    
    # Global variables
    GET_GLOBAL = 12
    SET_GLOBAL = 13
    DELETE_GLOBAL = 14
    DEFINE_GLOBAL = 15
    
    # Upvalues (for closures)
    GET_UPVALUE = 16
    SET_UPVALUE = 17
    
    # Properties
    GET_PROPERTY = 18
    SET_PROPERTY = 19
    GET_SUPER = 20
    
    # Indexing
    GET_INDEX = 21
    SET_INDEX = 22
    SET_INDEX_POP = 23
    
    # Jumps
    JUMP = 24
    JUMP_IF_FALSE = 25
    JUMP_IF_TRUE = 26
    JUMP_IF_FALSE_POP = 27
    JUMP_IF_TRUE_POP = 28
    LOOP = 29
    MATCH = 30
    
    # Function calls
    CALL = 31
    INVOKE = 32
    SUPER_INVOKE = 33
    TAIL_CALL = 34
    
    # Closures
    CLOSURE = 35
    CLOSE_UPVALUE = 36
    GET_CAPTURED = 37
    
    # Returns
    RETURN = 38
    RETURN_VAL = 39
    YIELD = 40
    
    # Classes
    CLASS = 41
    SUBCLASS = 42
    METHOD = 43
    END_METHOD = 44
    GET_METHOD = 45
    
    # Import
    IMPORT = 46
    END_IMPORT = 47
    
    # Arithmetic
    ADD = 48
    SUBTRACT = 49
    MULTIPLY = 50
    DIVIDE = 51
    MODULO = 52
    POWER = 53
    FLOOR_DIV = 54
    
    # Bitwise
    BIT_AND = 55
    BIT_OR = 56
    BIT_XOR = 57
    BIT_NOT = 58
    SHIFT_LEFT = 59
    SHIFT_RIGHT = 60
    
    # Unary
    NEGATE = 61
    NOT = 62
    INCREMENT = 63
    DECREMENT = 64
    
    # Comparison
    EQUAL = 65
    NOT_EQUAL = 66
    GREATER = 67
    GREATER_EQUAL = 68
    LESS = 69
    LESS_EQUAL = 70
    
    # String
    CONCATENATE = 71
    CONCAT_COUNT = 72
    
    # Range
    RANGE = 73
    
    # Collections
    LIST = 74
    DICT = 75
    TUPLE = 76
    SPREAD = 77
    
    # Nullish
    NULLISH = 78
    
    # Optional chaining
    OPTIONAL_CHAIN = 79
    OPTIONAL_CHAIN_END = 80
    
    # Special
    NOP = 81
    HALT = 99
    
    # Exception handling
    THROW = 82
    TRY = 83
    TRY_END = 84
    CATCH = 85
    CATCH_END = 86
    FINALLY = 87
    END_FINALLY = 88
    EXCEPTION = 89
    
    # With statement
    WITH_ENTER = 90
    WITH_EXIT = 91
    
    # Loop control
    BREAK = 92
    CONTINUE = 93


class OpcodeInfo:
    NAMES = {op: op.name for op in OpCode}
    STACK_EFFECTS = {
        OpCode.HALT: (0, 0),
        OpCode.CONSTANT: (0, 1),
        OpCode.NIL: (0, 1),
        OpCode.TRUE: (0, 1),
        OpCode.FALSE: (0, 1),
        OpCode.POP: (1, 0),
        OpCode.DUP: (0, 1),
        OpCode.ADD: (2, 1),
        OpCode.SUBTRACT: (2, 1),
        OpCode.MULTIPLY: (2, 1),
        OpCode.DIVIDE: (2, 1),
        OpCode.GET_GLOBAL: (0, 1),
        OpCode.SET_GLOBAL: (1, 0),
        OpCode.JUMP: (0, 0),
        OpCode.RETURN: (0, 0),
    }


class Chunk:
    def __init__(self):
        self.code: List[int] = []
        self.constants: List[Any] = []
        self.lines: List[int] = []
        self.jumps: dict = {}
    
    def write(self, opcode: OpCode, line: int = 0):
        if isinstance(opcode, int):
            opcode = OpCode(opcode)
        self.code.append(opcode)
        self.lines.append(line)
        return len(self.code) - 1
    
    def add_constant(self, value: Any, line: int = 0):
        self.constants.append(value)
        if len(self.constants) < 256:
            self.write(OpCode.CONSTANT, line)
            self.write(len(self.constants) - 1, line)
        else:
            self.write(OpCode.CONSTANT_LONG, line)
            idx = len(self.constants) - 1
            self.write(idx & 0xFF, line)
            self.write((idx >> 8) & 0xFF, line)
            self.write((idx >> 16) & 0xFF, line)
        return len(self.constants) - 1
    
    def emit_jump(self, opcode: OpCode, line: int = 0) -> int:
        self.write(opcode, line)
        self.write(0, line)
        self.write(0, line)
        return len(self.code) - 2
    
    def patch_jump(self, offset: int):
        jump_target = len(self.code)
        self.code[offset] = (jump_target - offset - 3) & 0xFF
        self.code[offset + 1] = ((jump_target - offset - 3) >> 8) & 0xFF
        self.code[offset + 2] = ((jump_target - offset - 3) >> 16) & 0xFF
    
    def emit_loop(self, loop_start: int, line: int = 0) -> int:
        self.write(OpCode.LOOP, line)
        offset = len(self.code) + 3
        self.write(offset & 0xFF, line)
        self.write((offset >> 8) & 0xFF, line)
        self.write((offset >> 16) & 0xFF, line)
        return len(self.code) - 3
    
    def read_int(self, offset: int) -> int:
        return self.code[offset] | (self.code[offset + 1] << 8) | (self.code[offset + 2] << 16)
    
    def write_int(self, value: int, offset: int):
        self.code[offset] = value & 0xFF
        self.code[offset + 1] = (value >> 8) & 0xFF
        self.code[offset + 2] = (value >> 16) & 0xFF
    
    def disassemble(self) -> str:
        output = []
        output.append("=== BYTECODE ===")
        output.append(f"Constants: {len(self.constants)}")
        for i, const in enumerate(self.constants):
            output.append(f"  {i}: {type(const).__name__} = {repr(const)[:50]}")
        
        output.append("\nCode:")
        i = 0
        while i < len(self.code):
            opcode = OpCode(self.code[i])
            line = self.lines[i] if i < len(self.lines) else 0
            output.append(f"  {i:04d}: {opcode.name} (line {line})")
            
            if opcode in (OpCode.CONSTANT, OpCode.GET_GLOBAL, OpCode.SET_GLOBAL,
                          OpCode.DEFINE_GLOBAL, OpCode.GET_LOCAL, OpCode.SET_LOCAL,
                          OpCode.GET_PROPERTY, OpCode.SET_PROPERTY, OpCode.GET_METHOD,
                          OpCode.METHOD):
                if i + 1 < len(self.code):
                    idx = self.code[i + 1]
                    const_name = f"#{idx}"
                    if idx < len(self.constants):
                        const_name += f"={repr(self.constants[idx])[:20]}"
                    output.append(f"        -> {const_name}")
                    i += 2
                    continue
            elif opcode in (OpCode.JUMP, OpCode.JUMP_IF_FALSE, OpCode.JUMP_IF_TRUE,
                           OpCode.LOOP, OpCode.TRY, OpCode.CATCH, OpCode.TRY_END):
                if i + 3 <= len(self.code):
                    offset = self.read_int(i + 1)
                    target = i + 4 + offset
                    output.append(f"        -> offset={offset} target={target}")
                    i += 4
                    continue
            
            i += 1
        
        return "\n".join(output)
    
    def __repr__(self):
        return f"Chunk(code={len(self.code)}, constants={len(self.constants)})"
