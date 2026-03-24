# Ipp Language

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
</p>

Ipp is a simple, beginner-friendly scripting language designed exclusively for high-performance game development. It feels like Python + Lua with modern syntax.

## Features

- **Simple Syntax** - Python-like indentation-based syntax
- **Dynamic Typing** - Easy to learn and use
- **Object-Oriented** - Classes with methods and inheritance
- **First-Class Functions** - Closures and higher-order functions
- **Modules** - Import and reuse code
- **REPL** - Interactive programming
- **Game Dev Focused** - Built for game scripting

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
var num = 42         # Number
var str = "hello"    # String
var flag = true      # Boolean
var nothing = nil    # Nil
var list = [1, 2, 3] # List
var dict = {"a": 1}  # Dictionary
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

See [roadmap.md](roadmap.md) for the full development plan.

- **v0.1.0** - Foundation (current)
- **v1.0.0** - Stable release with modules
- **v2.0.0** - Performance with bytecode
- **v3.0.0** - JIT/AOT compilation

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
