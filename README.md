# Ipp Language

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
 </p>

Ipp is a simple, beginner-friendly scripting language designed exclusively for high-performance game development. It feels like Python + Lua with modern syntax.

## Features

- **Simple Syntax** - Python-like syntax with braces
- **Dynamic Typing** - Easy to learn and use
- **Type Annotations** - Optional type hints (v0.6.0)
- **Object-Oriented** - Classes with methods and inheritance
- **First-Class Functions** - Closures and higher-order functions
- **Modules** - Import and reuse code
- **REPL** - Interactive programming with history
- **Pattern Matching** - match...case statements (v0.5.0)
- **Error Handling** - try...catch...finally (v0.5.0)
- **Enums** - Type-safe enumerated values (v0.6.0)
- **List Comprehensions** - Python-style `[x*x for x in list]` (v0.7.0)
- **Dict Comprehensions** - `{k: v*2 for k, v in pairs}` (v0.7.0)
- **Nullish Coalescing** - `nil ?? "default"` (v0.8.0)
- **Optional Chaining** - `user?.profile?.name` (v0.8.0)
- **Spread Operator** - `[...arr1, ...arr2]` (v0.8.0)
- **Tuples** - `(1, 2, 3)` (v0.8.0)
- **Do-While Loop** - `repeat { } until condition` (v0.9.0)
- **Throw/RAISE** - `throw "error"` (v0.9.0)
- **With Statement** - `with f = open("file") { }` (v0.9.0)
- **Custom __str__** - `func __str__() { }` (v0.10.0)
- **Game Dev Focused** - Built for game scripting

## Installation

### Download from GitHub

```bash
# Clone the repository
git clone https://github.com/anomalyco/Ipp.git
cd Ipp

# Run a script
python main.py your_script.ipp

# Start the REPL
python main.py
```

Or download as ZIP:
1. Go to (https://github.com/authorss81/Ipp)
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract and run `python main.py`

## Quick Start

```bash
# Run a script
python main.py examples/hello_world.ipp

# Start REPL
python main.py
```

## Hello World

```ipp
# Hello World in Ipp
print("Hello, World!")

# Variables
var x = 10
let name = "Ipp"

# Functions
func add(a, b) {
    return a + b
}

# Classes
class Dog {
    func init(name) {
        self.name = name
    }
    
    func bark() {
        return "Woof!"
    }
}

var dog = Dog("Buddy")
print(dog.bark())
```

## Language Basics

### Variables

```ipp
var x = 10           # Mutable variable
let y = 20           # Immutable binding
```

### Types

```ipp
var num = 42         # Integer (v0.6.0)
var flt = 3.14       # Float
var str = "hello"    # String
var flag = true      # Boolean
var nothing = nil    # Nil
var list = [1, 2, 3] # List
var dict = {"a": 1}  # Dictionary

# Type annotations (v0.6.0)
var count: int = 10
var name: string = "Ipp"
func add(a: int, b: int): int {
    return a + b
}
```

### Comprehensions (v0.7.0)

```ipp
# List comprehension
var squares = [i*i for i in 0..10]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# With condition
var evens = [x for x in 1..20 if x % 2 == 0]
# [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

# Dict comprehension
var doubled = {k: k*2 for k in 1..5}
# {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}

# Nested comprehension
var matrix = [[i*j for j in 1..4] for i in 1..4]
# [[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12], [4, 8, 12, 16]]
```

### Control Flow

```ipp
# If statement
if x > 5 {
    print("big")
} elif x > 10 {
    print("very big")
} else {
    print("small")
}

# For loop
for i in 0..10 {
    print(i)
}

# While loop
while x > 0 {
    x = x - 1
}

# Ternary operator
var result = x > 0 ? "positive" : "negative"

# Pattern matching
match direction {
    "up" => y += speed
    "down" => y -= speed
    "left" => x -= speed
    "right" => x += speed
    default => print("invalid")
}

# Error handling
try {
    var data = load_level("level1")
} catch e {
    print("Failed: " + e)
    var data = load_level("default")
} finally {
    cleanup()
}

# Enums
enum Direction {
    UP, DOWN, LEFT, RIGHT
}
var dir = Direction.UP
```

### Enums

```ipp
enum Direction {
    UP, DOWN, LEFT, RIGHT
}

var dir = Direction.UP
print(dir)           # Direction.UP
print(dir == Direction.UP)  # true

match direction {
    Direction.UP => print("going up")
    Direction.DOWN => print("going down")
}
```

### Operators

```ipp
# Arithmetic
var a = 10 + 5       # 15
var b = 10 // 3      # 3 (floor division)
var c = 2 ** 3       # 8 (power)

# Bitwise
var d = 5 & 3        # 1 (AND)
var e = 5 | 3        # 7 (OR)
var f = 5 ^ 3        # 6 (XOR)
var g = 2 << 3       # 16 (left shift)
var h = 8 >> 1       # 4 (right shift)

# Logical
var i = true && false   # false
var j = true || false   # true
```

### Functions

```ipp
func greet(name) {
    return "Hello, " + name + "!"
}

# Closures
func make_counter() {
    var count = 0
    func increment() {
        count = count + 1
        return count
    }
    return increment
}
```

### Classes

```ipp
class Person {
    func init(name, age) {
        self.name = name
        self.age = age
    }
    
    func greet() {
        return "Hi, I'm " + self.name
    }
}

var alice = Person("Alice", 25)
print(alice.greet())
```

### Modules

```ipp
# math.ipp
func add(a, b) {
    return a + b
}
var PI = 3.14159

# main.ipp
import "math.ipp"
print(add(5, 3))
print(PI)
```

## Built-in Functions

- `print(...)` - Print to console
- `len(obj)` - Get length
- `type(obj)` - Get type
- `range(start, end)` - Create range
- `abs()`, `min()`, `max()`, `round()`
- `sqrt()`, `pow()`, `sin()`, `cos()`, `tan()`
- `input(prompt)` - Read user input

## Installation

```bash
# Clone the repository
git clone https://github.com/authorss81/Ipp.git
cd Ipp

# Run
python main.py your_script.ipp
```

## Roadmap

See [ROADMAP_V2.md](ROADMAP_V2.md) for the detailed development plan.

### Current Release
- **v0.7.0** - Comprehensions (List/Dict comprehensions, type annotations, enums)

### Coming Releases
- **v0.8.0** - Advanced Operators (nullish coalescing, optional chaining, spread, tuples)
- **v0.9.0** - Control Flow (do-while, labeled breaks, throw/raise)
- **v0.10.0** - Functions + OOP (generators, async/await, private members, static methods)
- **v0.11.0** - Standard Library (datetime, path, hashlib, csv)
- **v0.12.0** - Package Manager (ippkg, virtual environments)
- **v0.13.0** - Tooling (REPL history, autocomplete, formatter)
- **v1.0.0** - Performance (Bytecode VM)
- **v2.0.0** - Game Features (Matrix, Physics, Graphics)
- **v3.0.0** - Embedding (C API, Rust bindings)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
