<div align="center">

# Ipp Language

<img src="https://img.shields.io/badge/version-1.2.4-blue.svg" alt="Version">
<img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
<img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
<img src="https://img.shields.io/badge/bugs_fixed-57-brightgreen.svg" alt="Bugs Fixed">
<img src="https://img.shields.io/badge/tests-passing-success.svg" alt="Tests">

**A beginner-friendly scripting language for game development.**  
Python-like syntax · Closures · Classes with Inheritance · Pattern Matching · Bytecode VM

</div>

---

## What is Ipp?

Ipp is a dynamically-typed, interpreted scripting language designed to feel like Python and Lua combined, built specifically for game development scripting. It compiles to a custom bytecode VM and also runs on a tree-walking interpreter for rapid development.

**v1.2.4** includes a full bug-fix pass — 57 bugs resolved — and a redesigned Gemini-CLI-inspired REPL with true-colour syntax highlighting.

---

## Quick Start

```bash
# Clone your repo
git clone https://github.com/authorss81/Ipp
cd Ipp

# Run a script
python main.py examples/hello_world.ipp

# Start the REPL
python main.py
```

No dependencies required. Python 3.8+ only.

---

## REPL

```
  ██╗██████╗ ██████╗
  ██║██╔══██╗██╔══██╗
  ██║██████╔╝██████╔╝
  ██║██╔═══╝ ██╔═══╝
  ██║██║     ██║
  ╚═╝╚═╝     ╚═╝

  Ipp  v1.2.0
  A scripting language for game development
──────────────────────────────────────────
  .help  commands   .vars  variables   exit  quit   Tab  autocomplete

  ❯ var x = 2 ** 10
  → 1024  0.1ms

  ❯ var name = "World"
  ❯ print("Hello, " + name + "!")
  Hello, World!

  ❯ .vars
   x       number    1024
```

**REPL commands:**

| Command | Description |
|---|---|
| `.help` | Show help and quick reference |
| `.vars` | List all defined variables with types |
| `.types` | Show the type system |
| `.clear` | Reset the session |
| `.version` | Show version |
| `exit` | Exit |

---

## Language Tour

### Variables

```ipp
var x = 10          # mutable
let y = 20          # immutable binding
var name: string = "Ipp"   # optional type annotation
```

### Compound Assignment *(v1.2.0)*

```ipp
var score = 0
score += 10
score *= 2
score -= 5
print(score)   # 15
```

### Numbers and Literals *(v1.2.0)*

```ipp
var dec  = 1_000_000     # underscores for readability
var hex  = 0xFF          # 255
var oct  = 0o77          # 63
var bin  = 0b1010        # 10
var flt  = 3.14
var pwr  = 2 ** 10       # 1024  (** is power)
var xor  = 5 ^ 3         # 6     (^ is bitwise XOR)
```

### Strings with Escape Sequences *(v1.2.0)*

```ipp
var s = "Hello\nWorld"       # newline
var t = "Tab\there"          # tab
var u = "Quote: \""          # escaped quote
var v = "\u0041"             # unicode → A
```

### Functions and Lambdas

```ipp
func add(a, b) {
    return a + b
}

# Lambda (v1.2.0)
var double = func(x) => x * 2
var square = func(x) => x * x

print(add(3, 4))      # 7
print(double(5))      # 10

# Closures
func make_counter() {
    var count = 0
    func increment() {
        count += 1
        return count
    }
    return increment
}

var c = make_counter()
print(c())   # 1
print(c())   # 2
print(c())   # 3
```

### Classes and Inheritance *(inheritance fixed v1.2.0)*

```ipp
class Animal {
    func init(name, sound) {
        self.name = name
        self.sound = sound
    }

    func speak() {
        return self.name + " says " + self.sound
    }

    func __str__() {
        return "<Animal: " + self.name + ">"
    }
}

class Dog : Animal {
    func init(name) {
        self.name = name
        self.sound = "Woof!"
    }

    func fetch(item) {
        return self.name + " fetches the " + item
    }
}

var dog = Dog("Rex")
print(dog.speak())       # Rex says Woof!
print(dog.fetch("ball")) # Rex fetches the ball
```

### Control Flow

```ipp
# If / elif / else
if x > 100 {
    print("big")
} elif x > 50 {
    print("medium")
} else {
    print("small")
}

# Ternary
var label = x > 0 ? "positive" : "non-positive"

# For loop
for i in 0..10 {
    print(i)
}

# While
while x > 0 {
    x -= 1
}

# Repeat/Until (do-while)
var n = 0
repeat {
    n += 1
} until n >= 5

# Pattern matching
match direction {
    case "up"    => y -= speed
    case "down"  => y += speed
    case "left"  => x -= speed
    case "right" => x += speed
    default      => print("invalid direction")
}
```

### Comprehensions

```ipp
# List comprehension
var squares = [i*i for i in 0..10]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition
var evens = [x for x in 1..20 if x % 2 == 0]

# Dict comprehension
var doubled = {k: k*2 for k in 1..5}
```

### Error Handling *(finally fixed v1.2.0)*

```ipp
try {
    var data = load_level("level1")
    process(data)
} catch e {
    print("Failed to load: " + e)
} finally {
    cleanup()     # always runs now (was broken before v1.2.0)
}

# Throw
func divide(a, b) {
    if b == 0 {
        throw "Division by zero"
    }
    return a / b
}
```

### Nullish Coalescing and Optional Chaining

```ipp
# Nullish coalescing
var name = player?.name ?? "Unknown"

# Optional chaining
var hp = player?.stats?.health ?? 100

# Pipeline operator
var result = items |> filter_alive |> sort_by_distance
```

### Enums

```ipp
enum Direction {
    UP, DOWN, LEFT, RIGHT
}

var dir = Direction.UP
match dir {
    case Direction.UP    => move(0, -1)
    case Direction.DOWN  => move(0,  1)
    case Direction.LEFT  => move(-1, 0)
    case Direction.RIGHT => move( 1, 0)
}
```

### Operators

```ipp
# Arithmetic
+  -  *  /  %       # basic
**                   # power  (2 ** 8 = 256)
//                   # floor division  (7 // 2 = 3)

# Bitwise
^   &   |   ~        # XOR, AND, OR, NOT
<<  >>               # shifts

# Logical
and  or  not         # keywords
&&   ||  !           # symbols (same)

# Comparison
==  !=  <  >  <=  >=

# Compound assignment (NEW in v1.2.0)
+=  -=  *=  /=  %=

# Special
?.    # optional chaining
??    # nullish coalescing
...   # spread
|>    # pipeline
..    # range  (0..5 = [0,1,2,3,4])
```

### Modules

```ipp
# Import all
import "math.ipp"

# Import with alias
import "utils.ipp" as utils
utils.helper()

# Selective import
import "math.ipp" as { PI, sin, cos }
print(PI)
```

---

## Built-in Functions

| Function | Description |
|---|---|
| `print(...)` | Print to console |
| `len(obj)` | Get length |
| `type(obj)` | Get type name |
| `range(start, end, step?)` | Create range list |
| `abs(n)` | Absolute value |
| `min(...)` `max(...)` | Min / max |
| `sum(...)` | Sum values |
| `round(n)` `floor(n)` `ceil(n)` | Rounding |
| `sqrt(n)` `pow(a,b)` | Power/roots |
| `sin(n)` `cos(n)` `tan(n)` | Trigonometry |
| `str(v)` `int(v)` `float(v)` `bool(v)` | Type conversion |
| `input(prompt?)` | Read user input |
| `keys(d)` `values(d)` | Dict iteration |
| `randint(a,b)` `random()` | Random numbers |
| `json_parse(s)` `json_stringify(v)` | JSON |
| `md5(s)` `sha256(s)` | Hashing |
| `base64_encode(s)` `base64_decode(s)` | Base64 |
| `upper(s)` `lower(s)` `split(s,sep)` | Strings |
| `assert(cond, msg?)` | Assertions |

---

## v1.2.0 Bug Fixes

57 bugs were identified and fixed in this release. Key highlights:

- **VM loops**: `for` and `while` loops were jumping to wrong addresses — fixed
- **VM locals**: local variables inside functions were reading from wrong stack positions — fixed
- **VM exception handlers**: nested `try/catch` was silently discarding outer handlers — fixed
- **`finally` blocks**: were parsed but never actually executed — fixed
- **`**` power operator**: was silently emitting no bytecode — fixed
- **`^` XOR operator**: was incorrectly mapped to power — fixed
- **`&&`/`||` precedence**: bitwise ops had wrong precedence relative to comparisons — fixed
- **`+=` compound assignment**: not supported — added
- **Hex/octal/binary literals**: not lexed — added
- **Escape sequences**: `\n \t \\` in strings were not processed — fixed
- **Class inheritance**: `class Dog : Animal {}` was not parsed — fixed
- **Lambda expressions**: `func(x) => x*2` was not parsed — added
- **`finally` blocks**: never executed in VM — fixed
- **`with` statement**: resource cleanup was a stub — implemented
- **`self` in methods**: was broken in certain call paths — fixed

See `IPP_FULL_AUDIT.md` for the complete list of all 57 bugs with exact file/line references.

---

## Roadmap

| Version | Focus |
|---|---|
| v1.3.0 | String interpolation `f"Hello {name}"` |
| v1.4.0 | Named parameters `func(x, y=0)` |
| v1.5.0 | Generator functions `yield` |
| v1.6.0 | Async/await |
| v2.0.0 | Game engine integration (Vector2, Physics, Graphics) |
| v3.0.0 | C API for embedding |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Fork → Branch → Fix → Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.
