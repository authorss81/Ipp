<div align="center">

# Ipp Language

<img src="https://img.shields.io/badge/version-1.5.4.7-blue.svg" alt="Version">
<img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
<img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
<img src="https://img.shields.io/badge/builtins-163+-brightgreen.svg" alt="Builtins">
<img src="https://img.shields.io/badge/tests-37%20passing-brightgreen.svg" alt="Tests">
<img src="https://img.shields.io/badge/status-stable-green.svg" alt="Status">

**A beginner-friendly scripting language for game development.**  
Python-like syntax · Closures · Classes with Inheritance · Pattern Matching · Bytecode VM · Async/Await · World-Class REPL

</div>

---

## What is Ipp?

Ipp is a dynamically-typed, interpreted scripting language designed to feel like Python and Lua combined, built specifically for game development scripting. It compiles to a custom bytecode VM and also runs on a tree-walking interpreter for rapid development.

**v1.5.4.7** includes Performance Optimizations (Bytecode Cache, .cache command). Previous phases (v1.5.2a, v1.5.2b, v1.5.3a, v1.5.3b) are partially done and need further enhancement.

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/authorss81/Ipp
cd Ipp

# Run a script
python main.py examples/hello_world.ipp

# Start the REPL
python main.py
```

No dependencies required. Python 3.8+ only.

### Install via PyPI
```bash
pip install ipp-lang
ipp repl
ipp run hello.ipp
```

---

## VSCode Extension

> **Note:** VSCode extension marketplace publish coming soon. Currently available for local installation.

Ipp includes a VSCode extension in `vscode-extension/`:

```bash
cd vscode-extension
npm install
npm run compile
code .
```

**Features:**
- Syntax highlighting
- 15 code snippets (func, class, for, while, if, match, try, etc.)
- Task runner for `ipp run` and `ipp check`
- LSP support: go-to-definition, completion, hover, rename

**Commands:**
- `ipp lsp` — Start LSP server
- `F5` — Run current file

---

## REPL Features

Ipp has a world-class REPL with 30+ built-in commands:

```
  ██╗██████╗ ██████╗
  ██║██╔══██╗██╔══██╗
  ██║██████╔╝██████╔╝
  ██║██╔═══╝ ██╔═══╝
  ██║██║     ██║
  ╚═╝╚═╝     ╚═╝

  Ipp  v1.5.4.5
  A scripting language for game development
──────────────────────────────────────────
  ❯ var x = 2 ** 10
  → 1024  0.1ms

  ❯ var name = "World"
  ❯ print("Hello, " + name + "!")
  Hello, World!
```

### Tab Completion
- **Builtins**: Type `ht` + Tab → `http_get`, `http_post`, `http_put`, etc.
- **Variables**: Type `my` + Tab → `my_variable`, etc.
- **Dict keys**: Type `person["` + Tab → `name`, `age`, `city`
- **Fuzzy matching**: `htgt` → `http_get`, `http_put`
- **REPL commands**: `.h` + Tab → `.help`, `.history`

### REPL Commands

| Category | Commands |
|----------|----------|
| **Core** | `.help`, `.vars`, `.fns`, `.builtins`, `.modules`, `.types`, `.version`, `.clear` |
| **Session** | `.load`, `.save`, `.export`, `.session save/load/clear/export`, `.sessions` |
| **History** | `.history`, `.last`, `$_`, `.history $_` |
| **Undo/Redo** | `.undo`, `.redo` |
| **Debugging** | `.debug start/stop`, `.break <line>`, `.watch <expr>`, `.locals`, `.stack` |
| **Inspection** | `.which <name>`, `.doc <fn>`, `.pretty <expr>`, `.json <expr>`, `.table <var>` |
| **Performance** | `.time <expr>`, `.profile` |
| **Shell** | `! <cmd>`, `.pipe <cmd>`, `.cd <dir>`, `.ls [dir]`, `.pwd` |
| **Customization** | `.theme dark/light/solarized`, `.prompt dir/time/full`, `.alias`, `.bind` |
| **Code** | `.edit`, `.format <expr>`, `.search <kw>`, `.examples`, `.tutorial`, `.plugin load` |

### Prompt Customization
- `.prompt ipp` — Default prompt (`❯`)
- `.prompt dir` — Show current directory (`(Ipp) ❯`)
- `.prompt time` — Show current time (`[14:30:00] ❯`)
- `.prompt full` — Show time + directory (`[14:30:00] C:\Ipp ❯`)

### Color Themes
- `.theme dark` — Dark theme (default)
- `.theme light` — Light theme
- `.theme solarized` — Solarized theme

---

## Language Tour

### Variables

```ipp
var x = 10          # mutable
let y = 20          # immutable binding
var name: string = "Ipp"   # optional type annotation
```

### Compound Assignment

```ipp
var score = 0
score += 10
score *= 2
score -= 5
```

### Functions & Closures

```ipp
func greet(name) {
    return "Hello, " + name
}

# Named arguments
greet(name="Alice", greeting="Hi")

# Closures
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
```

### Lambda Expressions

```ipp
var double = func(x) => x * 2
print(double(5))  # 10
```

### Classes & Inheritance

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

### Pattern Matching

```ipp
var x = 2
match x {
    case 1 => print("one")
    case 2 => print("two")
    case 3 => print("three")
    default => print("other")
}
```

### Error Handling

```ipp
try {
    var result = risky_operation()
} catch e {
    print("Error: " + e)
} finally {
    print("Cleanup")
}
```

### List Comprehensions

```ipp
var squares = [x*x for x in 1..10]
var evens = [x for x in 1..20 if x % 2 == 0]
```

### Nullish Coalescing

```ipp
var name = user_name ?? "Anonymous"
```

### Ternary Operator

```ipp
var status = age >= 18 ? "adult" : "minor"
```

### Tuple Unpacking

```ipp
var a, b = [1, 2]
print(a)  # 1
print(b)  # 2
```

### Operator Overloading

```ipp
class Vector {
    func init(x, y) {
        this.x = x
        this.y = y
    }
    func __add__(other) {
        return Vector(this.x + other.x, this.y + other.y)
    }
}
```

### Custom `__str__` Method

```ipp
class Point {
    func init(x, y) {
        this.x = x
        this.y = y
    }
    func __str__() {
        return "(" + this.x + ", " + this.y + ")"
    }
}
var p = Point(3, 4)
print(p)  # (3, 4)
```

---

## Built-in Functions (130+)

### Core (20)
`print`, `len`, `type`, `input`, `exit`, `assert`, `str`, `int`, `float`, `bool`, `to_number`, `to_int`, `to_float`, `to_bool`, `to_string`, `abs`, `min`, `max`, `sum`, `range`

### Math & Trigonometry (22)
`sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `log`, `log10`, `degrees`, `radians`, `pi`, `e`, `sqrt`, `pow`, `round`, `floor`, `ceil`, `lerp`, `clamp`, `distance`, `normalize`, `dot`, `cross`, `sign`, `smoothstep`, `move_towards`, `angle`, `factorial`, `gcd`, `lcm`, `hypot`, `floor_div`

### Random (5)
`random`, `randint`, `randfloat`, `choice`, `shuffle`

### String (18)
`upper`, `lower`, `strip`, `split`, `join`, `replace`, `replace_all`, `starts_with`, `ends_with`, `find`, `index_of`, `char_at`, `substring`, `count`, `contains`, `split_lines`, `ascii`, `from_ascii`

### File I/O (7)
`read_file`, `write_file`, `append_file`, `file_exists`, `delete_file`, `list_dir`, `mkdir`

### Data Formats (15)
`json_parse`, `json_stringify`, `xml_parse`, `xml_to_string`, `yaml_parse`, `yaml_to_string`, `toml_parse`, `toml_to_string`, `csv_parse`, `csv_parse_dict`, `csv_to_string`, `regex_match`, `regex_search`, `regex_replace`, `hash`

### Hashing & Encoding (8)
`md5`, `sha256`, `sha1`, `sha512`, `base64_encode`, `base64_decode`, `gzip_compress`, `gzip_decompress`

### Collections (12)
`keys`, `values`, `items`, `has_key`, `set`, `deque`, `ordict`, `PriorityQueue`, `Tree`, `Graph`, `uuid4`, `uuid1`

### Networking (12)
`http_get`, `http_post`, `http_put`, `http_delete`, `http_request`, `http_serve`, `ftp_connect`, `ftp_disconnect`, `ftp_list`, `ftp_get`, `ftp_put`, `smtp_connect`, `smtp_disconnect`, `smtp_send`

### WebSocket (4)
`websocket_connect`, `websocket_send`, `websocket_receive`, `websocket_close`

### URL Utilities (6)
`url_parse`, `url_build`, `url_encode`, `url_decode`, `url_query_parse`, `url_query_build`

### Time & OS (10)
`time`, `sleep`, `clock`, `datetime`, `os_platform`, `os_cwd`, `env_get`, `env_set`, `path_dirname`, `path_basename`

### Advanced (8)
`printf`, `sprintf`, `scanf`, `logger`, `thread`, `thread_sleep`, `thread_current`, `argparse`

### Game Types (4)
`vec2`, `vec3`, `color`, `rect`, `complex`

### Generators (2)
`next`, `is_generator`

### Async/Await (4)
`async_run`, `create_task`, `is_coroutine`, `sleep`

### Additional Builtins (31)
`seed`, `normal`, `now`, `delta`, `format_duration`, `from_hex`, `to_hex`, `blend`, `hsl`, `ease_in`, `ease_out`, `bounce`, `spring`, `read_lines`, `words`, `truncate`, `pad_left`, `pad_right`, `reverse`, `binary_search`, `group_by`, `zip_with`, `find_all`, `sub`, `escape`, `glob`, `pathfind`, `neighbors`, `flood_fill`, `assert_eq`, `inspect`

---

## Async/Await + Coroutines

Ipp supports async/await with a built-in event loop:

```ipp
async func fetch_data(url) {
    print("Fetching:", url)
    sleep(0.1)
    return "data from " + url
}

var coro = fetch_data("https://example.com")
var result = async_run(coro)
print(result)  # data from https://example.com
```

### Multiple Workers

```ipp
async func worker(name, delay) {
    print(name, "started")
    sleep(delay)
    print(name, "finished")
    return name + " done"
}

var r1 = async_run(worker("Worker1", 0.01))
var r2 = async_run(worker("Worker2", 0.02))
```

### Built-in Async Functions
| Function | Description |
|----------|-------------|
| `async_run(coro)` | Run a coroutine and wait for result |
| `create_task(coro)` | Create and run a coroutine task |
| `is_coroutine(obj)` | Check if object is a coroutine |
| `sleep(seconds)` | Sleep for given seconds (awaitable) |

---

## Generators

Ipp supports generator functions using the `yield` keyword:

```ipp
func count_up() {
    var i = 0
    while i < 5 {
        yield i
        i = i + 1
    }
}

var gen = count_up()
print(next(gen))  # 0
print(next(gen))  # 1
print(next(gen))  # 2
```

### For-in with Generators

```ipp
func fibonacci(n) {
    var a = 0
    var b = 1
    var count = 0
    while count < n {
        yield a
        var temp = a
        a = b
        b = temp + b
        count = count + 1
    }
}

for n in fibonacci(10) {
    print(n)  # 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
}
```

### Generator Utilities

```ipp
var gen = count_up()
print(is_generator(gen))  # true
print(is_generator(42))   # false
```

---

## Standard Library

### HTTP Client
```ipp
var res = http_get("https://httpbin.org/get")
print(res["status"])
print(res["body"])

var post_res = http_post("https://httpbin.org/post", "data=value")
```

### HTTP Server
```ipp
func handler(method, path, headers, body) {
    return (200, {"Content-Type": "text/plain"}, "Hello from Ipp!")
}
http_serve(handler, "localhost", 8080)
```

### FTP Client
```ipp
var ftp = ftp_connect("ftp.example.com", "user", "pass")
var files = ftp_list(ftp)
ftp_get(ftp, "remote.txt", "local.txt")
ftp_disconnect(ftp)
```

### SMTP Email
```ipp
var smtp = smtp_connect("smtp.gmail.com", 587, true, "user@gmail.com", "password")
smtp_send(smtp, "user@gmail.com", "recipient@example.com", "Subject", "Body")
smtp_disconnect(smtp)
```

### PriorityQueue
```ipp
var pq = PriorityQueue()
pq.push("low", 3)
pq.push("high", 1)
pq.push("medium", 2)
print(pq.pop())  # high
print(pq.pop())  # medium
```

### Tree
```ipp
var root = Tree("root")
root.add_child(Tree("child1"))
root.add_child(Tree("child2"))
print(root.traverse_preorder())
print(root.traverse_bfs())
```

### Graph
```ipp
var g = Graph()
g.add_edge("A", "B", 1)
g.add_edge("B", "C", 2)
g.add_edge("A", "C", 4)
print(g.shortest_path("A", "C"))  # [A, B, C]
```

---

## Version History

| Version | Focus |
|---|---|
| v1.3.0 | String interpolation, REPL redesign |
| v1.3.1 | Performance optimization |
| v1.3.2 | VM upvalues, Set type, bug fixes |
| v1.3.3 | Bug fixes + Standard Library + Networking (HTTP/FTP/SMTP) |
| v1.3.4 | Comprehensive stdlib testing (130+ builtins) |
| v1.3.5 | Regex fix + REPL color fix |
| v1.3.6 | VM compatibility tests + REPL warning |
| v1.3.7 | REPL enhancements (.load, .save, .doc, .time, .which, .undo, .profile, .alias, .edit, .last) |
| v1.3.8 | HTTP Server, WebSocket, PriorityQueue, Tree, Graph |
| v1.3.9 | REPL error handling (smart suggestions, highlight fix, .colors fix) |
| v1.3.10 | REPL Intelligence (tab completion, debugger, pretty printing, shell integration, themes) |
| v1.4.0 | Generator functions (`yield`) + VM Bug Fixes (all 7 VM bugs fixed) |
| v1.4.1 | Error Documentation + Error Reference Guide (ERRORS.md) |
| v1.4.2 | Tutorial Documentation + Getting Started Guide (TUTORIAL.md) |
| v1.4.3 | PyPI Publishing + `pip install ipp-lang` |
| v1.5.0 | Async/Await + Coroutines + Event Loop + Additional Builtins (31 new builtins) |
| v1.5.1 | VSCode Extension + LSP (15 snippets, task runner, LSP server, hover, completion) |
| v1.5.2a | WASM Backend (Partial - needs more work) |
| v1.5.2b | Web Playground (Partial - needs more work) |
| v1.5.3a | 2D Canvas API (Partial - Tkinter works, needs enhancement) |
| v1.5.3b | WebGL Bindings (Partial - needs browser integration) |
| v1.5.4.2 | REPL Performance (.bench, .mem, .reload, .checkpoint, .restore, .macro, theme, elif fix) |
| v1.5.5 | 3D Rendering + Scene Graph (Planned) |
| v1.6.0 | C++ Integration + Native Extensions |
| v1.6.1 | Cross-Platform (iOS, macOS, Linux, Windows Installer) |
| v2.0.0 | Package Manager + Full Ecosystem + Game Engine |

---

## Testing

```bash
# Run all regression tests
python tests/regression.py

# Run a single test
python main.py run tests/v1_3_10/test_repl_intelligence.ipp
```

All 37 test suites pass with zero failures.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Fork → Branch → Fix → Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.
