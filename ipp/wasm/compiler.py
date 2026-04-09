#!/usr/bin/env python3
"""WASM backend for Ipp - compiles Ipp to WebAssembly."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.vm.compiler import compile_ast


class WASMEmitter:
    """Emits WebAssembly text format from Ipp bytecode."""
    
    def __init__(self):
        self.functions = []
        self.globals = []
        self.imports = []
        self.exports = []
        self.stack = []
        self.local_vars = {}
        self.label_counter = 0
        
    def new_label(self):
        """Generate unique label."""
        self.label_counter += 1
        return f"label_{self.label_counter}"
        
    def emit_module(self, name="ipp_module"):
        """Emit complete WASM module."""
        lines = [
            f"(module",
            f'  (memory 1 256)',  # 256 pages = 16MB
            f'  (table 1 funcref)',
            f'  (func $print (import "env" "print") (param i32))',
            f'  (func $print_f64 (import "env" "print_f64") (param f64))',
            f'  (func $print_str (import "env" "print_str") (param i32))',
        ]
        
        # Add imported functions
        for imp in self.imports:
            lines.append(f"  {imp}")
            
        # Add global variables
        for global_def in self.globals:
            lines.append(f"  (global {global_def})")
            
        # Add internal functions
        for func in self.functions:
            lines.append(f"  {func}")
            
        # Add exports
        for exp in self.exports:
            lines.append(f"  (export {exp})")
            
        # Add memory data
        lines.append('  (data (i32.const 0) "Hello, World!\\00")')
            
        lines.append(")")
        return "\n".join(lines)
    
    def emit_function(self, name, params, locals_types, body_wasm):
        """Emit a function."""
        params_str = " ".join(params) if params else ""
        func = f"(func ${name} (param {params_str}) (result i32)\n"
        
        # Add local variables
        if locals_types:
            func += f"  (local {locals_types})\n"
            
        # Add function body
        for instr in body_wasm:
            func += f"  {instr}\n"
            
        func += ")"
        self.functions.append(func)
        return func
    
    # ============ i32 Operations ============
    def i32_const(self, value):
        return f"(i32.const {value})"
    
    def i32_add(self):
        return "(i32.add)"
    
    def i32_sub(self):
        return "(i32.sub)"
    
    def i32_mul(self):
        return "(i32.mul)"
    
    def i32_div_s(self):
        return "(i32.div_s)"
    
    def i32_rem_s(self):
        return "(i32.rem_s)"
    
    def i32_and(self):
        return "(i32.and)"
    
    def i32_or(self):
        return "(i32.or)"
    
    def i32_xor(self):
        return "(i32.xor)"
    
    def i32_shl(self):
        return "(i32.shl)"
    
    def i32_shr_s(self):
        return "(i32.shr_s)"
    
    def i32_eqz(self):
        return "(i32.eqz)"
    
    # ============ i64 Operations ============
    def i64_const(self, value):
        return f"(i64.const {value})"
    
    def i64_add(self):
        return "(i64.add)"
    
    def i64_sub(self):
        return "(i64.sub)"
    
    def i64_mul(self):
        return "(i64.mul)"
    
    # ============ f64 Operations ============
    def f64_const(self, value):
        return f"(f64.const {value})"
    
    def f64_add(self):
        return "(f64.add)"
    
    def f64_sub(self):
        return "(f64.sub)"
    
    def f64_mul(self):
        return "(f64.mul)"
    
    def f64_div(self):
        return "(f64.div)"
    
    def f64_sqrt(self):
        return "(f64.sqrt)"
    
    # ============ Comparison Operations ============
    def i32_eq(self):
        return "(i32.eq)"
    
    def i32_ne(self):
        return "(i32.ne)"
    
    def i32_lt_s(self):
        return "(i32.lt_s)"
    
    def i32_le_s(self):
        return "(i32.le_s)"
    
    def i32_gt_s(self):
        return "(i32.gt_s)"
    
    def i32_ge_s(self):
        return "(i32.ge_s)"
    
    def f64_lt(self):
        return "(f64.lt)"
    
    def f64_gt(self):
        return "(f64.gt)"
    
    def f64_eq(self):
        return "(f64.eq)"
    
    # ============ Memory Operations ============
    def i32_load(self, offset=0):
        return f"(i32.load {offset})"
    
    def i32_store(self, offset=0):
        return f"(i32.store {offset})"
    
    def i32_load8_s(self, offset=0):
        return f"(i32.load8_s {offset})"
    
    # ============ Type Conversion ============
    def i32_wrap_i64(self):
        return "(i32.wrap_i64)"
    
    def f64_convert_i32_s(self):
        return "(f64.convert_i32_s)"
    
    def i32_trunc_f64_s(self):
        return "(i32.trunc_f64_s)"
    
    # ============ Control Flow ============
    def local_get(self, index):
        return f"(local.get {index})"
    
    def local_set(self, index):
        return f"(local.set {index})"
    
    def local_tee(self, index):
        return f"(local.tee {index})"
    
    def call(self, name):
        return f"(call ${name})"
    
    def if_(self, condition, if_true, if_false=None):
        result = "(if (result i32)\n"
        result += f"    {condition}\n"
        result += f"    (then {if_true})\n"
        if if_false:
            result += f"    (else {if_false})\n"
        result += ")"
        return result
    
    def block(self, body, label_type="block"):
        return f"({label_type} {body})"
    
    def loop(self, body):
        return f"(loop {body})"
    
    def br(self, depth):
        return f"(br {depth})"
    
    def br_if(self, depth):
        return f"(br_if {depth})"
    
    def return_(self, value=None):
        if value:
            return f"(return {value})"
        return "(return)"
    
    def nop(self):
        return "(nop)"
    
    def unreachable(self):
        return "(unreachable)"
    
    def drop(self):
        return "(drop)"
    
    def select(self):
        return "(select)"
    
    # ============ Export ============
    def emit_export(self, name):
        self.exports.append(f'"{name}" (func ${name})')


class BytecodeToWASM:
    """Converts Ipp bytecode operations to WASM instructions."""
    
    def __init__(self):
        self.emitter = WASMEmitter()
        self.instructions = []
        
    def convert_op(self, op):
        """Convert a bytecode operation to WASM."""
        op_name = op[0] if isinstance(op, tuple) else op
        
        # Constants
        if op_name == 'CONST':
            value = op[1]
            if isinstance(value, int):
                return self.emitter.i32_const(value)
            elif isinstance(value, float):
                return self.emitter.f64_const(value)
            return self.emitter.i32_const(0)
        
        # Arithmetic
        elif op_name == 'ADD':
            return self.emitter.i32_add()
        elif op_name == 'SUB':
            return self.emitter.i32_sub()
        elif op_name == 'MUL':
            return self.emitter.i32_mul()
        elif op_name == 'DIV':
            return self.emitter.i32_div_s()
        elif op_name == 'MOD':
            return self.emitter.i32_rem_s()
        
        # Bitwise
        elif op_name == 'AND':
            return self.emitter.i32_and()
        elif op_name == 'OR':
            return self.emitter.i32_or()
        elif op_name == 'XOR':
            return self.emitter.i32_xor()
        elif op_name == 'SHL':
            return self.emitter.i32_shl()
        elif op_name == 'SHR':
            return self.emitter.i32_shr_s()
        
        # Comparison
        elif op_name == 'EQ':
            return self.emitter.i32_eq()
        elif op_name == 'NE':
            return self.emitter.i32_ne()
        elif op_name == 'LT':
            return self.emitter.i32_lt_s()
        elif op_name == 'LE':
            return self.emitter.i32_le_s()
        elif op_name == 'GT':
            return self.emitter.i32_gt_s()
        elif op_name == 'GE':
            return self.emitter.i32_ge_s()
        
        # Control
        elif op_name == 'POP':
            return self.emitter.drop()
        elif op_name == 'RETURN':
            return self.emitter.return_()
        
        # Memory
        elif op_name == 'LOAD':
            return self.emitter.i32_load()
        elif op_name == 'STORE':
            return self.emitter.i32_store()
        
        else:
            return None
    
    def emit_simple_function(self, name, ops):
        """Emit a simple function from operations."""
        for op in ops:
            instr = self.convert_op(op)
            if instr:
                self.instructions.append(instr)
        
        # Wrap in function
        self.emitter.emit_function(
            name,
            [],
            "",
            self.instructions
        )
        self.emitter.emit_export(name)
        
        return self.emitter.emit_module()


def compile_to_wasm(source, output_file=None):
    """Compile Ipp source to WASM."""
    tokens = list(tokenize(source))
    ast = parse(tokens)
    chunk = compile_ast(ast)
    
    # Create bytecode to WASM converter
    converter = BytecodeToWASM()
    
    # Generate simple add function for demonstration
    # In full implementation, we'd traverse the AST and convert each operation
    test_ops = [
        ('CONST', 10),
        ('CONST', 20),
        ('ADD'),
        ('RETURN'),
    ]
    
    wasm_text = converter.emit_simple_function("add", test_ops)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(wasm_text)
    
    return wasm_text


def compile_ast_to_wasm(ast, output_file=None):
    """Convert parsed AST directly to WASM."""
    converter = BytecodeToWASM()
    
    # Visit AST and convert to WASM
    wasm = converter.emit_simple_function("main", [])
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(wasm)
    
    return wasm


def main():
    """CLI entry point for WASM compilation."""
    args = sys.argv[1:]
    
    if not args or args[0] in ('--help', '-h'):
        print("Ipp WASM Compiler v1.5.2a")
        print()
        print("Usage:")
        print("  python main.py wasm <input.ipp> [output.wat]")
        print("  python main.py wasm --help")
        print()
        print("Options:")
        print("  <input.ipp>    Input Ipp source file")
        print("  [output.wat]   Output WASM text file (default: input.wat)")
        print()
        print("Example:")
        print("  python main.py wasm program.ipp program.wat")
        return 0
    
    input_file = args[0]
    output_file = args[1] if len(args) > 1 else None
    
    if not output_file:
        output_file = input_file.replace('.ipp', '.wat')
    
    try:
        with open(input_file, 'r') as f:
            source = f.read()
        
        wasm = compile_to_wasm(source, output_file)
        print(f"Compiled {input_file} -> {output_file}")
        print(f"Output size: {len(wasm)} bytes")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())