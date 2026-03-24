# Ipp Detailed Roadmap v2

## Version History
- v0.1.0 - Foundation (MVP) ✅ DONE
- v0.2.0 - Polish ✅ DONE
- v0.3.0 - Stability ✅ DONE
- v0.3.1 - Multiline + IppList fixes ✅ DONE
- v0.4.0 - CLI + Color/Rect + Module fixes ✅ DONE
- v0.5.0 - Syntax & Expression Fixes ⏳ IN PROGRESS
- v0.6.0 - Type System ⏳ PLANNED

---

## Phase 1: v0.5.0 - Syntax & Expression Fixes

**Goal**: Fix critical syntax gaps

**Timeline**: 2-3 weeks

### 1.1 Ternary Operator
```ipp
# Before: verbose
if x > 0 {
    result = "positive"
} else {
    result = "negative"
}

# After: concise
var result = x > 0 ? "positive" : "negative"
```

**Implementation**: 
- Add `?` and `:` to lexer
- Parse as ConditionalExpr in parser
- Implement in interpreter

### 1.2 Match/Switch Statement
```ipp
match direction {
    "up" => y += speed
    "down" => y -= speed  
    "left" => x -= speed
    "right" => x += speed
    _ => # default case
}
```

**Implementation**:
- Add MATCH token
- Parse switch-like AST node
- Support pattern matching

### 1.3 Bitwise Operators
```ipp
var flag = 0b1010 & 0b1100  # 0b1000
var shifted = x << 2
```

**Implementation**:
- Add `& | ^ << >> ~` tokens
- Implement in visit_binary_expr

### 1.4 Floor Division
```ipp
var result = 7 // 2  # 3 (not 3.5)
```

### 1.5 Try/Catch/Finally
```ipp
try {
    var data = load_level("level1")
} catch e {
    print("Failed: " + e)
    var data = load_level("default")
} finally {
    cleanup()
}
```

### 1.6 List Comprehensions
```ipp
var squares = [i*i for i in 0..10]
var evens = [x for x in numbers if x % 2 == 0]
```

---

## Phase 2: v0.6.0 - Type System

**Goal**: Add optional typing

### 2.1 Integer Type
- Add separate Integer type
- Distinguish from float
- Enable bitwise operations

### 2.2 Type Annotations
```ipp
var player_name: string = "Hero"
func damage(amount: number): void {
    health -= amount
}
```

### 2.3 Runtime Type Checking
```ipp
set_type_check(true)  # Enable runtime checks
```

### 2.4 Enums
```ipp
enum Direction {
    UP, DOWN, LEFT, RIGHT
}
var d = Direction.UP
```

---

## Phase 3: v1.0.0 - Performance

**Goal**: Make language fast enough for games

### 3.1 Bytecode Compiler
- Activate compiler.py
- Compile AST to bytecode
- Store .ipp files as bytecode

### 3.2 Bytecode VM
- Activate vm.py
- Stack-based VM
- 50+ opcodes

### 3.3 Optimizations
- Inline caching
- Function call optimization  
- Object pooling
- Native extension support (FFI)

---

## Phase 4: v1.3.0 - Tooling

**Goal**: Developer experience

### 4.1 REPL Improvements
- Readline support
- History
- Auto-complete

### 4.2 Debugger
- Breakpoints
- Step-through
- Variable inspection

### 4.3 Profiler
- Function timing
- Memory profiling

### 4.4 Language Server
- LSP implementation
- VS Code extension

---

## Phase 5: v1.6.0 - Ecosystem

**Goal**: Package system

### 5.1 Package Manager
- ippkg command
- Package repository

### 5.2 Standard Library
- datetime
- hashlib
- base64
- csv

---

## Phase 6: v2.0.0 - Game Features

**Goal**: Full game dev support

### 6.1 Math Extensions
- Matrix2x2, Matrix3x3, Matrix4x4
- Quaternion
- Barycentric coordinates

### 6.2 Physics Helpers
- AABB collision
- Sphere collision
- Ray casting

### 6.3 Graphics Utilities
- Easing functions
- Bezier curves
- Perlin noise
- Color conversions

---

## Phase 7: v3.0.0 - Embedding

**Goal**: Production embedding

### 7.1 C API
- ipp_create_vm()
- ipp_load_script()
- ipp_call_function()

### 7.2 Rust Bindings
- ipp crate

### 7.3 Hot Reload
- Script reloading without restart

---

*Last Updated: 2026-03-24*