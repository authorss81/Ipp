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

    # Jumps  — ALL use 3-byte (24-bit) operands
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
    GET_CAPTURED = 37      # FIX: BUG-V7 — needs operand

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

    # Nullish / optional
    NULLISH = 78
    OPTIONAL_CHAIN = 79       # 1-byte-operand (constant index)
    OPTIONAL_CHAIN_END = 80

    # Special
    NOP = 81
    HALT = 99

    # Exception handling
    THROW = 82
    TRY = 83          # 3-byte operand: offset to catch block
    TRY_END = 84
    CATCH = 85        # 3-byte operand: offset past catch
    CATCH_END = 86
    FINALLY = 87
    END_FINALLY = 88
    EXCEPTION = 89    # push current exception value

    # With statement
    WITH_ENTER = 90
    WITH_EXIT = 91

    # Loop control (resolved by compiler to JUMPs; these are fallback stubs)
    BREAK = 92
    CONTINUE = 93


# ─── Operand size table (authoritative) ──────────────────────────────────────
# Every opcode is exactly one of: 0-operand (size=1), 1-byte operand (size=2),
# or 3-byte operand (size=4).

_SIZE1 = frozenset([
    OpCode.NIL, OpCode.TRUE, OpCode.FALSE,
    OpCode.POP, OpCode.DUP, OpCode.DUP2, OpCode.SWAP,
    OpCode.ADD, OpCode.SUBTRACT, OpCode.MULTIPLY, OpCode.DIVIDE,
    OpCode.MODULO, OpCode.POWER, OpCode.FLOOR_DIV,
    OpCode.BIT_AND, OpCode.BIT_OR, OpCode.BIT_XOR, OpCode.BIT_NOT,
    OpCode.SHIFT_LEFT, OpCode.SHIFT_RIGHT,
    OpCode.NEGATE, OpCode.NOT, OpCode.INCREMENT, OpCode.DECREMENT,
    OpCode.EQUAL, OpCode.NOT_EQUAL, OpCode.GREATER, OpCode.GREATER_EQUAL,
    OpCode.LESS, OpCode.LESS_EQUAL,
    OpCode.RANGE, OpCode.NULLISH, OpCode.SPREAD,
    OpCode.RETURN, OpCode.RETURN_VAL, OpCode.YIELD,
    OpCode.HALT, OpCode.NOP,
    OpCode.OPTIONAL_CHAIN_END, OpCode.END_METHOD, OpCode.WITH_EXIT,
    OpCode.TRY_END, OpCode.CATCH_END, OpCode.FINALLY, OpCode.END_FINALLY,
    OpCode.EXCEPTION, OpCode.WITH_ENTER, OpCode.DELETE_LOCAL, OpCode.DELETE_GLOBAL,
    OpCode.CLOSE_UPVALUE,
    OpCode.BREAK, OpCode.CONTINUE,
    OpCode.SUBCLASS, OpCode.END_IMPORT,
    # FIX BUG-2: GET_INDEX/SET_INDEX have no operand — they pop from stack
    OpCode.GET_INDEX, OpCode.SET_INDEX, OpCode.SET_INDEX_POP,
])

_SIZE2 = frozenset([
    OpCode.CONSTANT,
    OpCode.GET_GLOBAL, OpCode.SET_GLOBAL, OpCode.DEFINE_GLOBAL,
    OpCode.GET_LOCAL, OpCode.SET_LOCAL,
    OpCode.GET_UPVALUE, OpCode.SET_UPVALUE,
    OpCode.GET_PROPERTY, OpCode.SET_PROPERTY,
    OpCode.GET_METHOD, OpCode.METHOD,
    OpCode.CLASS,
    OpCode.CALL,
    OpCode.LIST, OpCode.DICT, OpCode.TUPLE,
    OpCode.CONCATENATE, OpCode.CONCAT_COUNT,
    OpCode.GET_SUPER,
    OpCode.THROW,
    OpCode.GET_CAPTURED,
    OpCode.CLOSURE,
    OpCode.OPTIONAL_CHAIN,
])

_SIZE4 = frozenset([
    OpCode.CONSTANT_LONG,
    OpCode.JUMP, OpCode.JUMP_IF_FALSE, OpCode.JUMP_IF_TRUE,
    OpCode.JUMP_IF_FALSE_POP, OpCode.JUMP_IF_TRUE_POP,   # FIX: BUG-C1
    OpCode.LOOP,
    OpCode.TRY, OpCode.CATCH,
    OpCode.MATCH,
    OpCode.IMPORT,
    OpCode.INVOKE, OpCode.SUPER_INVOKE, OpCode.TAIL_CALL,
])


def opcode_size(opcode: 'OpCode') -> int:
    """Return total instruction size (opcode byte + operand bytes)."""
    if opcode in _SIZE1:
        return 1
    if opcode in _SIZE2:
        return 2
    if opcode in _SIZE4:
        return 4
    return 1  # safe default


class OpcodeInfo:
    NAMES = {op: op.name for op in OpCode}


class Chunk:
    def __init__(self):
        self.code: List[int] = []
        self.constants: List[Any] = []
        self.lines: List[int] = []

    def write(self, opcode, line: int = 0):
        if isinstance(opcode, OpCode):
            self.code.append(int(opcode))
        else:
            self.code.append(opcode)
        self.lines.append(line)
        return len(self.code) - 1

    def add_constant(self, value: Any, line: int = 0) -> int:
        """Append constant and emit CONSTANT/CONSTANT_LONG instruction."""
        self.constants.append(value)
        idx = len(self.constants) - 1
        if idx < 256:
            self.write(OpCode.CONSTANT, line)
            self.write(idx, line)
        else:
            self.write(OpCode.CONSTANT_LONG, line)
            self.write(idx & 0xFF, line)
            self.write((idx >> 8) & 0xFF, line)
            self.write((idx >> 16) & 0xFF, line)
        return idx

    def emit_jump(self, opcode, line: int = 0) -> int:
        """Emit a jump instruction with placeholder 3-byte offset. Returns patch offset."""
        self.write(opcode, line)
        self.write(0xFF, line)
        self.write(0xFF, line)
        self.write(0xFF, line)
        return len(self.code) - 3   # index of first operand byte

    def patch_jump(self, offset: int):
        """Back-patch a jump to point to the current end of code."""
        jump_target = len(self.code)
        # offset stored is relative to the instruction AFTER the operand bytes
        delta = jump_target - (offset + 3)
        if delta < 0:
            raise ValueError(f"Negative jump delta {delta} at patch offset {offset}")
        self.code[offset]     =  delta        & 0xFF
        self.code[offset + 1] = (delta >> 8)  & 0xFF
        self.code[offset + 2] = (delta >> 16) & 0xFF

    def emit_loop(self, loop_start: int, line: int = 0) -> int:
        """
        FIX: BUG-C7 — correctly compute backward jump offset using loop_start.
        The LOOP opcode jumps backward. The offset stored is:
            (current_position_after_operands) - loop_start
        so the VM does:  ip = ip_after_instruction - offset  = loop_start
        """
        self.write(OpCode.LOOP, line)
        # After writing the 3 operand bytes, ip will be at len(self.code)+3
        # We want to reach loop_start
        after = len(self.code) + 3    # ip position after the full LOOP instruction
        offset = after - loop_start
        if offset < 0:
            raise ValueError(f"Invalid loop offset {offset}")
        self.code.append(offset & 0xFF)
        self.lines.append(line)
        self.code.append((offset >> 8) & 0xFF)
        self.lines.append(line)
        self.code.append((offset >> 16) & 0xFF)
        self.lines.append(line)
        return len(self.code) - 3

    def read_int(self, offset: int) -> int:
        """Read a 3-byte little-endian unsigned integer."""
        return self.code[offset] | (self.code[offset + 1] << 8) | (self.code[offset + 2] << 16)

    def write_int(self, value: int, offset: int):
        self.code[offset]     =  value        & 0xFF
        self.code[offset + 1] = (value >> 8)  & 0xFF
        self.code[offset + 2] = (value >> 16) & 0xFF

    def disassemble(self) -> str:
        output = ["=== BYTECODE ===", f"Constants: {len(self.constants)}"]
        for i, c in enumerate(self.constants):
            output.append(f"  {i}: {type(c).__name__} = {repr(c)[:50]}")
        output.append("\nCode:")
        i = 0
        while i < len(self.code):
            op = OpCode(self.code[i])
            ln = self.lines[i] if i < len(self.lines) else 0
            size = opcode_size(op)
            if size == 1:
                output.append(f"  {i:04d}: {op.name} (line {ln})")
            elif size == 2:
                idx = self.code[i + 1] if i + 1 < len(self.code) else 0
                extra = f"#{idx}"
                if op in (OpCode.CONSTANT, OpCode.GET_GLOBAL, OpCode.SET_GLOBAL,
                          OpCode.DEFINE_GLOBAL, OpCode.GET_PROPERTY, OpCode.SET_PROPERTY):
                    if idx < len(self.constants):
                        extra += f"={repr(self.constants[idx])[:20]}"
                output.append(f"  {i:04d}: {op.name} {extra} (line {ln})")
            elif size == 4:
                offset = self.read_int(i + 1) if i + 3 < len(self.code) else 0
                output.append(f"  {i:04d}: {op.name} offset={offset} (line {ln})")
            i += size
        return "\n".join(output)

    def __repr__(self):
        return f"Chunk(code={len(self.code)}, constants={len(self.constants)})"

    def serialize(self) -> bytes:
        """Serialize chunk to bytes for caching."""
        import pickle
        data = {
            'code': self.code,
            'constants': self.constants,
            'lines': self.lines
        }
        return pickle.dumps(data)

    @staticmethod
    def deserialize(data: bytes) -> 'Chunk':
        """Deserialize chunk from bytes."""
        import pickle
        data = pickle.loads(data)
        chunk = Chunk()
        chunk.code = data['code']
        chunk.constants = data['constants']
        chunk.lines = data['lines']
        return chunk
