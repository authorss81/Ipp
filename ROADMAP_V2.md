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
| v0.5.1 | ✅ DONE | ASCII logo, colored REPL, >>> prompt |
| v0.5.2 | ✅ DONE | Box UI, .help, .vars, .clear commands |
| v0.5.3 | ✅ DONE | REPL multiline (auto-detect braces) |
| v0.5.4 | ✅ DONE | Fix let reassignment, game math functions |
| v0.6.0 | ✅ DONE | Type System + Enums |
| v0.6.1 | ✅ DONE | Integer type, type annotations, ** power, fixed XOR |
| v0.7.0 | ✅ DONE | List/Dict Comprehensions |
| **v0.8.0** | ✅ DONE | Advanced Operators + Tuples |
| **v0.9.0** | ✅ DONE | Control Flow + Exceptions |
| **v0.10.0** | ✅ DONE | Functions + OOP Enhancements |
| **v0.11.0** | **PENDING | Standard Library Expansion |
| **v0.12.0** | **PENDING** | Module System + Package Manager |
| **v0.13.0** | **PENDING** | Tooling + REPL Improvements |
| **v1.0.0** | **PENDING** | Performance (Bytecode VM) |

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

## v0.11.0 - Standard Library Expansion (PENDING)

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

## v0.12.0 - Module System + Package Manager (PENDING)

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

## v0.13.0 - Tooling + REPL Improvements (PENDING)

**Goal**: Developer experience

### 8.1 REPL with History
- Readline support
- Arrow key navigation
- Command history

### 8.2 REPL Auto-complete
- Tab completion for identifiers
- Built-in function suggestions

### 8.3 Code Formatter
```bash
ipp format file.ipp
```

### 8.4 Linter
```bash
ipp lint file.ipp
```

### 8.5 Type Checker
```bash
ipp check file.ipp
```

---

## v1.0.0 - Performance (PENDING)

**Goal**: Make language fast enough for games

### Bytecode Compiler
- Activate compiler.py
- Compile AST to bytecode
- Store .ipp files as bytecode

### Bytecode VM
- Activate vm.py
- Stack-based VM
- 50+ opcodes

### Optimizations
- Inline caching
- Function call optimization
- Object pooling
- Native extension support (FFI)

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
