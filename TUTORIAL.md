# Ipp Getting Started Guide

Welcome to **Ipp** — a beginner-friendly scripting language for game development.

## Installation

### From PyPI (Recommended)
```bash
pip install ipp-lang
```

### From Source
```bash
git clone https://github.com/authorss81/Ipp
cd Ipp
python main.py
```

---

## Your First Program

Create a file called `hello.ipp`:

```ipp
print("Hello, World!")
```

Run it:
```bash
python main.py run hello.ipp
```

Output:
```
Hello, World!
```

---

## Variables

Ipp has two ways to declare variables:

```ipp
var x = 10       # mutable — can be changed
let y = 20       # immutable — cannot be changed

x = 30           # ✅ OK
# y = 40         # ❌ Error: Cannot reassign constant
```

### Types

Ipp is dynamically typed. Common types:

```ipp
var number = 42          # int
var pi = 3.14            # float
var name = "Alice"       # string
var alive = true         # bool
var nothing = nil        # nil

print(type(number))      # int
print(type(pi))          # float
print(type(name))        # string
print(type(alive))       # bool
print(type(nothing))     # nil
```

---

## Operators

### Arithmetic
```ipp
var sum = 10 + 5       # 15
var diff = 10 - 5      # 5
var prod = 10 * 5      # 50
var quot = 10 / 5      # 2.0
var mod = 10 % 3       # 1
var power = 2 ** 10    # 1024
var floor_div = 7 // 3 # 2
```

### Comparison
```ipp
print(1 == 1)          # true
print(1 != 2)          # true
print(1 < 2)           # true
print(1 > 2)           # false
print(1 <= 1)          # true
print(1 >= 2)          # false
```

### Logical
```ipp
print(true and false)  # false
print(true or false)   # true
print(not true)        # false
```

### Bitwise
```ipp
print(0xFF & 0x0F)     # 15
print(0xF0 | 0x0F)     # 255
print(0xFF ^ 0x0F)     # 240
print(1 << 4)          # 16
print(16 >> 2)         # 4
```

---

## Control Flow

### If / Elif / Else
```ipp
var age = 18

if age < 13 {
    print("child")
} elif age < 18 {
    print("teenager")
} else {
    print("adult")
}
```

### Ternary Operator
```ipp
var status = age >= 18 ? "adult" : "minor"
print(status)  # adult
```

### While Loop
```ipp
var i = 0
while i < 5 {
    print(i)
    i = i + 1
}
```

### For Loop (Range)
```ipp
for i in 0..5 {
    print(i)  # 0, 1, 2, 3, 4
}
```

### For Loop (List)
```ipp
var items = [1, 2, 3, 4, 5]
for x in items {
    print(x)
}
```

### For Loop (String)
```ipp
for c in "hello" {
    print(c)  # h, e, l, l, o
}
```

### Match Statement
```ipp
var day = 2

match day {
    case 1 => print("Monday")
    case 2 => print("Tuesday")
    case 3 => print("Wednesday")
    default => print("Other day")
}
```

---

## Functions

### Basic Function
```ipp
func greet(name) {
    return "Hello, " + name
}

print(greet("World"))  # Hello, World
```

### Default Parameters
```ipp
func greet(name, greeting = "Hello") {
    return greeting + ", " + name
}

print(greet("World"))           # Hello, World
print(greet("World", "Hi"))     # Hi, World
```

### Named Arguments
```ipp
func connect(host, port) {
    return host + ":" + str(port)
}

print(connect("localhost", 8080))    # localhost:8080
print(connect(port=9090, host="db")) # db:9090
```

### Lambda Expressions
```ipp
var double = func(x) => x * 2
print(double(5))  # 10
```

### Closures
```ipp
func make_counter() {
    var count = 0
    return func() {
        count = count + 1
        return count
    }
}

var counter = make_counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

### Generators
```ipp
func count_up(max) {
    var i = 0
    while i < max {
        yield i
        i = i + 1
    }
}

# Using next()
var gen = count_up(3)
print(next(gen))  # 0
print(next(gen))  # 1
print(next(gen))  # 2

# Using for-in
for n in count_up(5) {
    print(n)  # 0, 1, 2, 3, 4
}
```

---

## Lists

```ipp
var nums = [1, 2, 3, 4, 5]

print(nums[0])       # 1
print(len(nums))     # 5

nums.append(6)
print(nums)          # [1, 2, 3, 4, 5, 6]

# List Comprehension
var squares = [x*x for x in 1..10]
print(squares)       # [1, 4, 9, 16, 25, 36, 49, 64, 81]
```

---

## Dictionaries

```ipp
var person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

print(person["name"])     # Alice
print(keys(person))       # [name, age, city]
print(values(person))     # [Alice, 30, NYC]

# Dict Comprehension
var doubled = {k: v*2 for k, v in items(person) if type(v) == "int"}
```

---

## Classes

```ipp
class Animal {
    func init(name) {
        this.name = name
    }
    
    func speak() {
        print(this.name + " makes a sound")
    }
}

class Dog : Animal {
    func speak() {
        print(this.name + " says woof!")
    }
}

var dog = Dog("Rex")
dog.speak()  # Rex says woof!
```

### Operator Overloading
```ipp
class Vec2 {
    func init(x, y) {
        this.x = x
        this.y = y
    }
    
    func __add__(other) {
        return Vec2(this.x + other.x, this.y + other.y)
    }
    
    func __str__() {
        return "(" + str(this.x) + ", " + str(this.y) + ")"
    }
}

var v1 = Vec2(1, 2)
var v2 = Vec2(3, 4)
var v3 = v1 + v2
print(v3)  # (4, 6)
```

---

## Error Handling

```ipp
try {
    var result = risky_operation()
} catch e {
    print("Error: " + e)
} finally {
    print("Cleanup")
}
```

---

## Modules

```ipp
# math_utils.ipp
func add(a, b) { return a + b }
func sub(a, b) { return a - b }

# main.ipp
import "math_utils.ipp" as math

print(math.add(3, 4))  # 7
```

---

## Built-in Functions

Ipp has 132+ built-in functions. Here are the most common:

### Core
| Function | Description |
|----------|-------------|
| `print(...)` | Print to console |
| `len(obj)` | Get length |
| `type(obj)` | Get type name |
| `range(n)` | Create range list |
| `abs(n)`, `min(...)`, `max(...)`, `sum(...)` | Math helpers |

### String
| Function | Description |
|----------|-------------|
| `upper(s)`, `lower(s)` | Case conversion |
| `split(s, sep)`, `join(arr, sep)` | Split/join |
| `replace(s, old, new)` | Replace |
| `starts_with(s, prefix)` | Check prefix |

### Data
| Function | Description |
|----------|-------------|
| `json_parse(s)`, `json_stringify(v)` | JSON |
| `regex_match(text, pattern)` | Regex |
| `read_file(path)`, `write_file(path, data)` | File I/O |

### Networking
| Function | Description |
|----------|-------------|
| `http_get(url)` | HTTP GET request |
| `http_post(url, data)` | HTTP POST request |
| `websocket_connect(url)` | WebSocket client |

### Math
| Function | Description |
|----------|-------------|
| `sin(n)`, `cos(n)`, `tan(n)` | Trigonometry |
| `sqrt(n)`, `pow(a, b)` | Power/roots |
| `lerp(a, b, t)`, `clamp(v, min, max)` | Game math |

### 3D Math (v1.5.5+)
| Function | Description |
|----------|-------------|
| `vec4(x, y, z, w)` | 4D vector |
| `vec3(x, y, z)` | 3D vector |
| `vec2(x, y)` | 2D vector |
| `mat4()` | 4x4 identity matrix |
| `mat4_perspective(fov, aspect, near, far)` | Perspective projection |
| `mat4_look_at(eye, target, up)` | View matrix |
| `mat4_translate(x, y, z)` | Translation matrix |
| `mat4_rotate(angle, axis)` | Rotation matrix |
| `mat4_scale(x, y, z)` | Scale matrix |
| `quat(x, y, z, w)` | Quaternion |
| `quat_from_axis_angle(axis, angle)` | Quaternion from axis-angle |
| `quat_slerp(a, b, t)` | Spherical interpolation |

### Scene Graph (v1.5.5+)
| Function | Description |
|----------|-------------|
| `scene(name)` | Create scene |
| `node(name)` | Create scene node |
| `camera(name, fov, aspect, near, far)` | Create camera |
| `mesh(name, vertices, indices)` | Create mesh |
| `mesh_cube(size)` | Cube primitive |
| `mesh_sphere(radius, segments, rings)` | Sphere primitive |
| `mesh_plane(width, height)` | Plane primitive |
| `light(name, type, intensity)` | Create light |
| `scene.add(node)`, `scene.set_camera(cam)` | Scene methods |
| `scene.set_root(node)`, `scene.get_root()` | Scene root management |
| `node.add_child(child)`, `node.remove_child(child)` | Hierarchy management |
| `node.get_parent()`, `node.get_children()` | Hierarchy queries |
| `node.find_node(name)` | Recursive node search |
| `node.get_world_transform()`, `node.get_world_position()` | World-space transforms |
| `scene.render()`, `scene.render_to_canvas(w, h)` | Rendering |

### Canvas 2D
| Function | Description |
|----------|-------------|
| `canvas_open()` | Open canvas window |
| `canvas_rect(x, y, w, h, color)` | Draw rectangle |
| `canvas_circle(x, y, r, color)` | Draw circle |
| `canvas_line(x1, y1, x2, y2, color)` | Draw line |
| `canvas_text(x, y, text, color)` | Draw text |
| `canvas_clear(color)` | Clear canvas |
| `canvas_show()` | Update display |

### HTML/Templates (v1.5.17)
| Function | Description |
|----------|-------------|
| `html_escape(text)` | Escape HTML special characters |
| `html_unescape(text)` | Unescape HTML entities |
| `template(template_str, **kwargs)` | Template interpolation |
| `template_file(path, **kwargs)` | Render template file |

Example:
```ipp
var safe = html_escape("<script>alert('xss')</script>")
# Result: &lt;script&gt;...

var html = template("<h1>Hello {{name}}!</h1>", name="World")
# Result: <h1>Hello World!</h1>
```

### Async/Future (v1.5.17)
| Function | Description |
|----------|-------------|
| `future()` | Create a Future object |
| `event_loop()` | Get asyncio event loop info |
| `async_run(coro)` | Run coroutine |
| `create_task(coro)` | Create async task |
| `is_coroutine(obj)` | Check if object is coroutine |
| `sleep(seconds)` | Async sleep |

### List Comprehensions
```ipp
var squares = [i * i for i in range(10)]
var evens = [x for x in range(20) if x % 2 == 0]
var dict = {k: k*2 for k in range(5)}
```

### Decorators (v1.5.17)
```ipp
@my_decorator
func hello() {
    print("Hello!")
}
```

### Tween System (v2.0.8)
```ipp
tween(player, "x", 300, 1.0)          # Animate x to 300 over 1 second
delay(0.5)                              # Wait 0.5 seconds (awaitable)
```

### Sequence Cutscenes (v2.0.8.3)
```ipp
sequence intro {
    move player, 100, 0
    parallel {
        fade_out 0.5
        play_music "intro.ogg"
    }
    wait(0.5)
}
run_sequence(intro)
```

### Story Narrative (v2.0.8.4)
```ipp
story tavern {
    npc "Bartender": "What'll it be?"
    choice {
        "Ale" => { flag has_ale = true }
        "Wine" => { npc "Bartender": "Good choice!" }
    }
}
run_story(tavern)
```

See [ERRORS.md](ERRORS.md) for a complete error reference.

---

## Next Steps

- Read the [ERRORS.md](ERRORS.md) for error troubleshooting
- Explore the `examples/` directory for more code samples
- Try the REPL: `python main.py`
- Check the [ROADMAP_V2.md](ROADMAP_V2.md) for upcoming features
