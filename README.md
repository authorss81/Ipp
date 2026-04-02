<div align="center">

# Ipp Language

<img src="https://img.shields.io/badge/version-1.3.8-blue.svg" alt="Version">
<img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
<img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
<img src="https://img.shields.io/badge/builtins-130+-brightgreen.svg" alt="Builtins">
<img src="https://img.shields.io/badge/tests-22%20passing-brightgreen.svg" alt="Tests">
<img src="https://img.shields.io/badge/status-stable-green.svg" alt="Status">

**A beginner-friendly scripting language for game development.**  
Python-like syntax · Closures · Classes with Inheritance · Pattern Matching · Bytecode VM

</div>

---

## What is Ipp?

Ipp is a dynamically-typed, interpreted scripting language designed to feel like Python and Lua combined, built specifically for game development scripting. It compiles to a custom bytecode VM and also runs on a tree-walking interpreter for rapid development.

**v1.3.8** includes HTTP server, PriorityQueue, Tree, Graph data structures, 130+ built-in functions, 25 passing regression tests, REPL enhancements, networking support, and comprehensive standard library coverage.

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

### Core (20 functions)
| Function | Description |
|---|---|
| `print(...)` | Print to console |
| `len(obj)` | Get length |
| `type(obj)` | Get type name |
| `range(start, end, step?)` | Create range list |
| `abs(n)` `min(...)` `max(...)` `sum(...)` | Math helpers |
| `round(n)` `floor(n)` `ceil(n)` | Rounding |
| `sqrt(n)` `pow(a,b)` | Power/roots |
| `str(v)` `int(v)` `float(v)` `bool(v)` | Type conversion |
| `to_number(v)` `to_int(v)` `to_float(v)` `to_bool(v)` `to_string(v)` | Safe conversions |
| `input(prompt?)` | Read user input |
| `exit(code?)` | Exit program |
| `assert(cond, msg?)` | Assertions |

### Math & Trigonometry (22 functions)
| Function | Description |
|---|---|
| `sin(n)` `cos(n)` `tan(n)` | Trigonometry |
| `asin(n)` `acos(n)` `atan(n)` `atan2(y,x)` | Inverse trig |
| `log(n, base?)` `log10(n)` | Logarithms |
| `degrees(n)` `radians(n)` | Angle conversion |
| `pi()` `e()` | Math constants |
| `lerp(a,b,t)` `clamp(v,min,max)` `map_range(v,a,b,c,d)` | Game math |
| `distance(x1,y1,x2,y2)` `distance_3d(...)` | Distance |
| `normalize(x,y)` `dot(x1,y1,x2,y2)` `cross(x1,y1,x2,y2)` | Vector math |
| `sign(n)` `smoothstep(e0,e1,x)` `move_towards(cur,target,max)` | Utilities |
| `angle(x1,y1,x2,y2)` `deg_to_rad(n)` `rad_to_deg(n)` | Angle helpers |
| `factorial(n)` `gcd(a,b)` `lcm(a,b)` `hypot(a,b)` `floor_div(a,b)` | Advanced math |

### String Functions (18 functions)
| Function | Description |
|---|---|
| `upper(s)` `lower(s)` `strip(s)` | Case/whitespace |
| `split(s,sep)` `join(arr,sep)` `split_lines(s)` | Split/join |
| `replace(s,old,new)` `replace_all(s,old,new)` | Replace |
| `starts_with(s,prefix)` `ends_with(s,suffix)` | Prefix/suffix |
| `find(s,sub)` `index_of(s,sub)` `char_at(s,i)` `substring(s,start,len)` | Search/extract |
| `count(s,sub)` `contains(s,sub)` | Count/contains |
| `ascii(c)` `from_ascii(n)` | ASCII conversion |

### File I/O (7 functions)
| Function | Description |
|---|---|
| `read_file(path)` `write_file(path,data)` `append_file(path,data)` | Read/write |
| `file_exists(path)` `delete_file(path)` | Exists/delete |
| `list_dir(path)` `mkdir(path)` | Directory ops |

### Data Formats (15 functions)
| Function | Description |
|---|---|
| `json_parse(s)` `json_stringify(v)` | JSON |
| `xml_parse(s)` `xml_to_string(v)` | XML |
| `yaml_parse(s)` `yaml_to_string(v)` | YAML |
| `toml_parse(s)` `toml_to_string(v)` | TOML |
| `csv_parse(s)` `csv_parse_dict(s)` `csv_to_string(v)` | CSV |
| `regex_match(text,pattern)` `regex_search(text,pattern)` `regex_replace(text,pattern,repl)` | Regex |
| `md5(s)` `sha256(s)` `sha1(s)` `sha512(s)` `hash(s)` | Hashing |
| `base64_encode(s)` `base64_decode(s)` | Base64 |
| `gzip_compress(s)` `gzip_decompress(s)` | GZIP |
| `zip_create(dict)` `zip_extract(data)` | ZIP |

### Collections (12 functions)
| Function | Description |
|---|---|
| `keys(d)` `values(d)` `items(d)` `has_key(d,k)` | Dict ops |
| `set(arr)` | Set type |
| `deque(arr)` | Deque (double-ended queue) |
| `ordict()` | Ordered dict |
| `uuid4()` `uuid1()` `uuid_nil()` | UUID generation |
| `datetime()` `datetime_create(...)` | DateTime |
| `time()` `sleep(s)` `clock()` | Time |

### Networking (12 functions)
| Function | Description |
|---|---|
| `http_get(url,headers?)` `http_post(url,data?,headers?)` | HTTP GET/POST |
| `http_put(url,data?,headers?)` `http_delete(url,headers?)` | HTTP PUT/DELETE |
| `http_request(url,method,data?,headers?)` | Generic HTTP |
| `ftp_connect(host,user,pass?,port?)` `ftp_disconnect(client)` | FTP |
| `ftp_list(client,path?)` `ftp_get(client,remote,local)` `ftp_put(client,local,remote)` | FTP ops |
| `smtp_connect(server,port,tls?,user?,pass?)` `smtp_disconnect(client)` | SMTP |
| `smtp_send(client,from,to,subject,body)` | Send email |

### URL Utilities (6 functions)
| Function | Description |
|---|---|
| `url_parse(url)` `url_build(dict)` | Parse/build URLs |
| `url_encode(s)` `url_decode(s)` | Encode/decode |
| `url_query_parse(s)` `url_query_build(dict)` | Query strings |

### Game Types (4 constructors)
| Function | Description |
|---|---|
| `vec2(x,y)` `vec3(x,y,z)` | Vectors |
| `color(r,g,b,a)` | Color |
| `rect(x,y,w,h)` | Rectangle |
| `complex(real,imag)` | Complex numbers |

### Advanced (8 functions)
| Function | Description |
|---|---|
| `printf(fmt,...)` `sprintf(fmt,...)` `scanf(fmt)` | C-style formatting |
| `logger(name,level)` | Logging |
| `thread(fn,...)` `thread_sleep(s)` `thread_current()` | Threading |
| `argparse()` `args_add(parser,...)` `args_parse(parser)` | Argument parsing |

---

## v1.3.4 Bug Fixes

- **regex argument order**: `regex_match(text, pattern)` now uses intuitive text-first order
- **log/logger conflict**: Renamed logging builtin from `log` to `logger` to preserve math `log()` function
- **and/or precedence**: `1 == 1 and 2 == 2` now correctly returns `true`
- **Nested `len(items(d))`**: Now works without storing intermediate result

---

## Roadmap

| Version | Focus |
|---|---|
| v1.3.0-v1.3.8 | ✅ DONE — REPL, VM, bug fixes, standard library, networking, REPL tools, HTTP server, PriorityQueue, Tree, Graph |
| v1.4.0 | Generators `yield`, Async/Await, Engine integration |
| v1.4.1 | VM Builtin Functions + Dict Access |
| v1.4.2 | VM Functions + Recursion + Classes |
| v1.4.3 | VM For Loops + `--vm` CLI Flag |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Fork → Branch → Fix → Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.
