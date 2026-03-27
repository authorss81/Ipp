# Ipp Detailed Roadmap v2

## Version History
| Version | Status | Features |
|---------|--------|----------|
| v0.1.0 | ✅ DONE | Foundation (MVP) |
| v0.2.0 | ✅ DONE | Polish |
| v0.3.0 | ✅ DONE | Stability |
| v0.3.1 | ✅ DONE | Multiline + IppList fixes |
| v0.4.0 | ✅ DONE | CLI + Color/Rect + Module fixes |
| v0.5.0 | ✅ DONE | Ternary, match, bitwise, floor div, try/catch |
| v0.5.1-0.5.4 | ✅ DONE | Various improvements |
| v0.6.0 | ✅ DONE | Type System + Enums |
| v0.6.1 | ✅ DONE | Integer type, type annotations, ** power, fixed XOR |
| v0.7.0 | ✅ DONE | List/Dict Comprehensions |
| v0.8.0 | ✅ DONE | Advanced Operators + Tuples |
| v0.9.0 | ✅ DONE | Control Flow + Exceptions |
| v0.10.0 | ✅ DONE | Functions + OOP Enhancements |
| v0.11.0-0.11.2 | ✅ DONE | Standard Library Expansion |
| v0.12.0 | ✅ DONE | Module System (import, alias, selective) |
| v0.13.0 | ✅ DONE | Professional REPL UI |
| **v1.0.0** | ✅ DONE | Bytecode VM Infrastructure |
| **v1.0.1** | ✅ DONE | VM Stabilization & Bug Fixes |
| **v1.1.0** | ✅ DONE | Performance Optimization & Profiler |
| **v1.2.0** | **PENDING** | Benchmark Suite vs Other Languages |
| **v1.3.0** | **PENDING** | Production Ready |
| **v2.0.0** | **PENDING** | Game Features |

---

## v0.8.0 - Advanced Operators + Tuples ✅ DONE

**Goal**: Fill remaining operator gaps and add tuples

### 3.1 Nullish Coalescing ✅ DONE
```ipp
var value = nil ?? "default"
```

### 3.2 Optional Chaining ✅ DONE
```ipp
var name = user?.profile?.name
```

### 3.3 Spread Operator ✅ DONE
```ipp
var arr = [1, 2, ...other]
```

### 3.4 Pipeline Operator
```ipp
var result = data |> transform |> filter
```
*Note: Not implemented in v0.8.0*

### 3.5 Tuples ✅ DONE
```ipp
var point = (10, 20)
```
```

### 3.6 Runtime Type Checking
```ipp
set_type_check(true)
```

---

## v0.9.0 - Control Flow + Exceptions ✅ DONE

**Goal**: Complete control flow and custom exceptions

### 4.1 Do-While Loop
```ipp
repeat {
    x = x - 1
} until x == 0
```

### 4.2 Labeled Breaks
```ipp
outer: for i in 0..10 {
    for j in 0..10 {
        if j == 5 {
            break outer
        }
    }
}
```

### 4.3 Throw/Raise Custom Exceptions
```ipp
func validate(age) {
    if age < 0 {
        throw "Age cannot be negative"
    }
}

try {
    validate(-5)
} catch e {
    print("Error: " + e)
}
```

### 4.4 With Statement (Context Managers)
```ipp
with open("file.txt") as f {
    var data = f.read()
}
```

---

## v0.10.0 - Functions + OOP Enhancements ✅ DONE

**Goal**: Enhanced functions and OOP

### 5.1 Named Arguments
```ipp
func greet(name, greeting="Hello") {
    return greeting + ", " + name
}
greet(name="World", greeting="Hi")
```

### 5.2 Keyword-Only Arguments
```ipp
func f(a, *, b, c) {
    # b and c must be passed as keywords
}
```

### 5.3 Variadic Arguments
```ipp
func sum(*args) {
    var total = 0
    for x in args {
        total = total + x
    }
    return total
}
```

### 5.4 Generator Functions (yield)
```ipp
func count_to(n) {
    for i in 0..n {
        yield i
    }
}
```

### 5.5 Async/Await
```ipp
async func load_data() {
    var data = await fetch("/api/data")
    return data
}
```

### 5.6 Private/Public Members
```ipp
class Player {
    private health = 100
    
    func get_health() {
        return this.health
    }
}
```

### 5.7 Static Methods/Properties
```ipp
class Math {
    static func abs(n) {
        return n < 0 ? -n : n
    }
}
Math.abs(-5)
```

### 5.8 Super() Shorthand
```ipp
class Dog < Animal {
    func bark() {
        super.speak()
        print("Woof!")
    }
}
```

### 5.9 Property Decorators
```ipp
class Rectangle {
    init(width, height) {
        this._width = width
        this._height = height
    }
    
    var area {
        get { return this._width * this._height }
    }
}
```

### 5.10 __str__ and __repr__
```ipp
class Point {
    init(x, y) {
        this.x = x
        this.y = y
    }
    
    func __str__() {
        return "Point(" + this.x + ", " + this.y + ")"
    }
}
```

---

## v0.11.0 - Standard Library Expansion ✅ DONE

**Goal**: Rich standard library for game dev

### 6.1 DateTime Utilities
```ipp
var now = datetime.now()
var formatted = now.format("%Y-%m-%d")
```

### 6.2 Path Utilities
```ipp
var dir = path.dirname("/game/sprites/player.png")
var base = path.basename("/game/sprites/player.png")
var joined = path.join("game", "assets", "image.png")
```

### 6.3 Hash Functions
```ipp
var hash = md5("password")
var sha = sha256("data")
```

### 6.4 Base64 Encoding
```ipp
var encoded = base64_encode("Hello")
var decoded = base64_decode(encoded)
```

### 6.5 CSV Parsing
```ipp
var data = csv_parse("name,age\nAlice,25\nBob,30")
```

### 6.6 OS Utilities
```ipp
var env_var = env.get("PATH")
var platform = os.platform()
```

### 6.7 Complex Numbers
```ipp
var c = complex(3, 4)
var result = c * c
```

---

## v0.12.0 - Module System + Tooling ✅ DONE

**Goal**: Package ecosystem like pip/npm

### 7.1 Package Manager (ippkg)
```bash
ippkg install game-utils
ippkg publish my-package
```

### 7.2 Standard Library Modules
- `datetime` - Date/time operations
- `path` - Path manipulation
- `hashlib` - Hash functions
- `base64` - Encoding/decoding
- `csv` - CSV parsing
- `os` - OS utilities
- `json` - JSON (already exists as functions)

### 7.3 Virtual Environments
```bash
ipp venv myenv
ipp activate myenv
```

### 7.4 Module Aliasing
```ipp
import "math" as m
import "utils" as { helper, loader }
```

### 7.5 Conditional/Dynamic Imports
```ipp
if platform == "windows" {
    import "platform/windows.ipp"
}
```

---

## v0.13.0 - Tooling + REPL Improvements ✅ DONE

**Goal**: Developer experience

### 8.1 REPL with History ✅
- Readline support
- Arrow key navigation
- Command history (persistent)

### 8.2 REPL Auto-complete ✅
- Tab completion for identifiers
- Built-in function suggestions
- Member completion (obj.)

### 8.3 Professional REPL UI ✅
- Gradient ASCII logo with 256-color ANSI
- Box drawing UI with proper padding
- Syntax highlighting for output
- Multi-line prompts (...1, ...2)
- Help box, Types box, Vars box

### 8.4 Linter ✅
```bash
ipp lint file.ipp
```

---

## v1.0.0 - Performance (DONE)

**Goal**: Make language fast enough for games

### Bytecode Compiler ✅
- Complete compiler with 90+ opcodes
- Compiles AST to bytecode chunks
- Support for all Ipp expressions and statements
- Jump patching for control flow

### Bytecode VM ✅
- Stack-based VM with fast opcode dispatch
- 90+ opcodes (arithmetic, bitwise, control flow, etc.)
- Global and local variable access
- Property/index operations

### Optimizations ✅
- Inline caching for global lookups
- String interning
- Constant pooling
- Optimized opcode dispatch

### Benchmarks ✅
- Benchmark suite at `tests/v1/benchmark.py`
- Performance comparison tools

---

## v1.0.1 - VM Stabilization ✅ DONE

**Goal**: Fix bugs, complete missing features, stabilize VM

### VM Bug Fixes ✅
- [x] Fix opcode conflicts and duplicate values
- [x] Fix constant pool index handling
- [x] Fix jump instruction handling
- [x] Fix function call/return
- [x] Fix class instantiation
- [x] Fix list index type checking in interpreter

### Missing Features Implemented ✅
- [x] Complete FOR loop support
- [x] Complete TRY/CATCH exception handling
- [x] Complete CLASS/METHOD implementation
- [x] Complete IMPORT statement
- [x] Complete BREAK/CONTINUE
- [x] Complete WHILE/DO-WHILE loops
- [x] Complete MATCH statement

### Testing ✅
- [x] Comprehensive VM tests (`tests/v1_0_1/test_features.ipp`)
- [x] Integration tests via regression suite
- [x] All regression tests pass

---

## v1.1.0 - Performance Optimization (DONE)

**Goal**: Optimize VM performance, add JIT compilation

### VM Optimizations ✅
- [x] Method dispatch caching
- [x] Type cache for fast lookups
- [x] Hot function tracking
- [x] Object pooling infrastructure

### Profiler ✅
- [x] Built-in profiler (`Profiler` class)
- [x] Opcode count statistics
- [x] Function call tracking
- [x] `profile_vm()` and `profile_source()` functions
- [x] `profile_and_report()` for detailed reports

### JIT Infrastructure
- [ ] Basic JIT for hot functions (future)
- [ ] Native code generation (future)
- [ ] Dynamic recompilation (future)
- [ ] Inline caching optimization (future)

---

## v1.2.0 - Benchmark Suite (PENDING)

**Goal**: Comprehensive benchmarks vs Lua, Python, GDScript

### Benchmark Categories
1. **Micro Benchmarks**
   - Integer arithmetic
   - Floating point math
   - String operations
   - Function calls
   - Property access

2. **Game-Specific Benchmarks**
   - Physics simulation (collision detection)
   - Pathfinding (A*, Dijkstra)
   - Particle systems
   - Game loop performance
   - Entity component updates

3. **Language Comparison**
   - vs Lua/LuaJIT
   - vs Python/PyPy
   - vs GDScript
   - vs AngelScript

### Benchmark Suite Features
- [ ] `tests/v1/benchmarks/` directory
- [ ] Lua comparison scripts
- [ ] Python comparison scripts
- [ ] HTML report generation
- [ ] CI/CD integration

---

## v1.3.0 - Production Ready (PENDING)

**Goal**: VM production-ready, stable release

### Stability
- [ ] All regression tests pass on VM
- [ ] Memory safety verified
- [ ] Stack overflow protection
- [ ] Exception safety

### Features
- [ ] Bytecode serialization (`.ipbc` files)
- [ ] VM CLI flag (`--vm` to use VM)
- [ ] Hot reload support
- [ ] Debugger support

### Documentation
- [ ] VM internals documentation
- [ ] Opcode reference
- [ ] Performance tuning guide
- [ ] Migration guide from interpreter

---

## v2.0.0 - Game Features (PENDING)

**Goal**: Full game dev support

### Math Extensions
- Matrix2x2, Matrix3x3, Matrix4x4
- Quaternion
- Barycentric coordinates

### Physics Helpers
- AABB collision
- Sphere collision
- Ray casting

### Graphics Utilities
- Easing functions
- Bezier curves
- Perlin noise
- Color conversions (HSL, HSV)

---

## v3.0.0 - Embedding (PENDING)

**Goal**: Production embedding

### C API
- ipp_create_vm()
- ipp_load_script()
- ipp_call_function()

### Rust Bindings
- ipp crate

### Hot Reload
- Script reloading without restart

---

*Last Updated: 2026-03-25*
