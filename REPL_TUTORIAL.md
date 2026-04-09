# Ipp REPL Tutorial v1.5.4

A comprehensive guide to the Ipp programming language REPL (Read-Eval-Print Loop).

## Table of Contents
1. [Getting Started](#getting-started)
2. [Keywords](#keywords)
3. [Builtin Functions](#builtin-functions)
4. [REPL Commands](#repl-commands)
5. [Examples](#examples)

---

## Getting Started

```bash
# Start the REPL
python main.py

# Run a script
python main.py examples/hello.ipp

# Install via pip
pip install ipp-lang
ipp repl
```

---

## Keywords

Ipp supports the following keywords (41 total):

### Variable Declarations
| Keyword | Description | Example |
|---------|-------------|---------|
| `var` | Mutable variable | `var x = 10` |
| `let` | Immutable binding | `let PI = 3.14` |

### Control Flow
| Keyword | Description | Example |
|---------|-------------|---------|
| `if` | Conditional | `if x > 0 { print("positive") }` |
| `elif` | Else if branch | `elif x > 0 { ... }` |
| `else` | Else branch | `else { ... }` |
| `match` | Pattern matching | `match x { ... }` |
| `case` | Match case | `case 1 => "one"` |
| `default` | Default case | `default => "other"` |

### Loops
| Keyword | Description | Example |
|---------|-------------|---------|
| `for` | For loop | `for i in 0..10 { print(i) }` |
| `while` | While loop | `while x > 0 { x = x - 1 }` |
| `repeat` | Repeat until | `repeat { ... } until condition` |
| `until` | Until condition | `until x >= 10` |

### Control
| Keyword | Description | Example |
|---------|-------------|---------|
| `break` | Exit loop | `break` |
| `continue` | Next iteration | `continue` |
| `return` | Return value | `return x * 2` |

### Functions
| Keyword | Description | Example |
|---------|-------------|---------|
| `func` | Function declaration | `func add(a, b) { return a + b }` |
| `async` | Async function | `async fetch() { ... }` |
| `await` | Await coroutine | `await async_run(task)` |
| `yield` | Generator yield | `yield i * 2` |

### Classes
| Keyword | Description | Example |
|---------|-------------|---------|
| `class` | Class declaration | `class Dog : Animal { }` |
| `init` | Constructor | `func init() { this.name = "dog" }` |
| `self` / `this` | Instance reference | `self.name` or `this.name` |
| `super` | Parent class | `super.init()` |
| `static` | Static member | `static var count = 0` |

### Exception Handling
| Keyword | Description | Example |
|---------|-------------|---------|
| `try` | Try block | `try { ... }` |
| `catch` | Catch error | `catch e { print(e) }` |
| `finally` | Always runs | `finally { cleanup() }` |
| `throw` | Raise error | `throw("error message")` |

### Other
| Keyword | Description | Example |
|---------|-------------|---------|
| `import` | Import module | `import "module.ipp" as m` |
| `as` | Import alias | `import "lib" as lib` |
| `enum` | Enum declaration | `enum Color { RED, GREEN }` |
| `with` | Context manager | `with open("f") { ... }` |
| `in` | Membership test | `x in list` |
| `and` | Logical AND | `x > 0 and x < 10` |
| `or` | Logical OR | `x < 0 or x > 10` |
| `not` | Logical NOT | `not found` |
| `true` | Boolean true | `true` |
| `false` | Boolean false | `false` |
| `nil` | Null value | `nil` |

---

## Builtin Functions

Ipp includes 233 built-in functions. Here they are organized by category:

### I/O & Printing (5)
```ipp
print("Hello, World!")           # Print with newline
printf("Value: %d", 42)         # Printf-style formatting
sprintf("Value: %d", 42)        # Return formatted string
input("Name: ")                 # Get user input
scanf("%d %s", "10 hello")     # Parse formatted input
```

### Type Conversion (9)
```ipp
type(42)                        # Get type: "int"
str(42)                         # Convert to string
int("42")                       # Convert to integer
float("3.14")                   # Convert to float
bool(1)                         # Convert to boolean
to_number("42")                 # Parse number
to_string(42)                   # Convert to string
to_int(3.14)                   # Convert to int (3)
to_float("3.14")               # Convert to float
```

### Math - Basic (15)
```ipp
abs(-5)                         # Absolute value: 5
min(3, 7)                      # Minimum: 3
max(3, 7)                      # Maximum: 7
round(3.7)                     # Round: 4
floor(3.7)                     # Floor: 3
ceil(3.2)                      # Ceiling: 4
sqrt(16)                       # Square root: 4
pow(2, 8)                      # Power: 256
```

### Math - Trigonometry (10)
```ipp
sin(0)                         # Sine
cos(0)                         # Cosine
tan(0)                         # Tangent
asin(0)                        # Arc sine
acos(0)                        # Arc cosine
atan(0)                        # Arc tangent
atan2(y, x)                    # Two-argument atan2
degrees(3.14)                  # Radians to degrees
radians(180)                   # Degrees to radians
hypot(3, 4)                    # Hypotenuse: 5
```

### Math - Constants (2)
```ipp
pi                             # 3.14159...
e                              # 2.71828...
```

### Math - Advanced (20)
```ipp
log(2.718)                    # Natural log
log10(100)                    # Log base 10
factorial(5)                  # 120
gcd(48, 18)                   # Greatest common divisor: 6
lcm(4, 6)                     # Least common multiple: 12
lerp(0, 10, 0.5)              # Linear interpolation: 5
clamp(15, 0, 10)              # Clamp value: 10
sign(-5)                      # Sign: -1
normal(0, 1)                  # Normal distribution
map_range(5, 0, 10, 0, 100)   # Map range: 50
```

### Math - Easing (5)
```ipp
ease_in(0.5)                  # Ease in quadratic
ease_out(0.5)                 # Ease out quadratic
bounce(0.75)                   # Bounce easing
spring(0.5, 0.5)              # Spring damping
smoothstep(0.5)               # Smooth step
```

### Random & Numbers (8)
```ipp
random()                      # Random float 0-1
randint(1, 10)                # Random integer 1-10
randfloat(0.0, 1.0)           # Random float range
choice([1, 2, 3])             # Random choice
shuffle([1, 2, 3])            # Shuffle list
seed(123)                     # Set random seed
round(3.5)                    # Round to nearest
floor_div(10, 3)              # Floor division: 3
```

### Collection - List (12)
```ipp
len([1, 2, 3])                # Length: 3
sum([1, 2, 3])                # Sum: 6
range(5)                      # Range: [0,1,2,3,4]
range(1, 6, 2)                # Range with step: [1,3,5]
reverse([1, 2, 3])            # Reverse: [3,2,1]
zip_with([1,2], [3,4])        # Zip with function
binary_search([1,2,3], 2)    # Binary search: 1
group_by([1,2,3], fn(x) x%2) # Group by
find_all([1,2,1,3], 1)       # Find all indices: [0,2]
```

### Collection - Dict (4)
```ipp
keys({"a": 1, "b": 2})        # ["a", "b"]
values({"a": 1, "b": 2})       # [1, 2]
items({"a": 1})                # [["a", 1]]
has_key({"a": 1}, "a")        # true
```

### Collection - Set (2)
```ipp
set([1, 2, 2, 3])              # Create set: {1,2,3}
```

### String - Basic (20)
```ipp
len("hello")                   # Length: 5
upper("hello")                 # "HELLO"
lower("HELLO")                 # "hello"
strip("  hello  ")             # "hello"
replace("hello", "l", "r")     # "herro"
replace_all("lol", "l", "w")   # "wow"
starts_with("hello", "he")     # true
ends_with("hello", "lo")       # true
contains("hello", "ell")       # true
find("hello", "ell")           # 1
count("hello", "l")             # 2
split("a,b,c", ",")            # ["a","b","c"]
join(["a", "b"], "-")          # "a-b"
split_lines("a\nb")            # ["a", "b"]
substring("hello", 1, 3)       # "el"
char_at("hello", 0)            # "h"
ascii("A")                     # 65
from_ascii(65)                 # "A"
index_of("hello", "e")         # 1
truncate("hello world", 8)     # "hello..."
```

### String - Advanced (3)
```ipp
pad_left("hi", 5, "0")         # "000hi"
pad_right("hi", 5, "0")        # "hi000"
escape("hello\nworld")         # Escape special chars
```

### JSON & Data (8)
```ipp
json_parse('{"a":1}')          # Parse JSON
json_stringify({"a":1})        # To JSON string
toml_parse("[section]\nx=1")  # Parse TOML
toml_to_string({"x":1})       # To TOML string
yaml_parse("x: 1")            # Parse YAML
yaml_to_string({"x":1})       # To YAML string
csv_parse("a,b\n1,2")         # Parse CSV
csv_to_string([["a","b"]])   # To CSV string
```

### Regex (3)
```ipp
regex_match("abc", r"\w+")    # Match entire string
regex_search("abc123", r"\d+") # Search: "123"
regex_replace("abc", r"b", "X") # "aXc"
```

### Hashing & Crypto (5)
```ipp
md5("hello")                   # MD5 hash
sha1("hello")                  # SHA1 hash
sha256("hello")                # SHA256 hash
sha512("hello")                # SHA512 hash
hash("hello")                  # General hash
```

### Base64 (4)
```ipp
base64_encode("hello")         # "aGVsbG8="
base64_decode("aGVsbG8=")      # "hello"
base64_encode_bytes([1,2,3])   # Encode bytes
base64_decode_bytes("AQID")    # Decode to bytes
```

### Compression (2)
```ipp
gzip_compress("data")          # Compress
gzip_decompress(data)         # Decompress
```

### File Operations (10)
```ipp
file_read("data.txt")          # Read file
file_write("data.txt", "text") # Write file
append_file("data.txt", "text")# Append to file
file_exists("data.txt")        # Check exists
delete_file("data.txt")        # Delete file
read_lines("data.txt")         # Read as lines
list_dir(".")                  # List directory
mkdir("newdir")                # Create directory
path_exists("path")            # Path exists
path_join("a", "b")            # Join paths
```

### URL & Web (15)
```ipp
url_parse("http://a.com?x=1") # Parse URL
url_build({"host":"a.com"})   # Build URL
url_encode("hello world")      # URL encode
url_decode("hello%20world")   # URL decode
url_query_parse("x=1&y=2")    # Parse query
url_query_build({"x":1})      # Build query
http_get("http://example.com")# GET request
http_post("url", "data")       # POST request
http_put("url", "data")        # PUT request
http_delete("url")             # DELETE request
http_request("GET", "url")    # Custom request
http_serve(8080)              # Start HTTP server
```

### Email & FTP (9)
```ipp
smtp_connect("smtp.gmail.com")# Connect SMTP
smtp_disconnect()             # Disconnect
smtp_send(from, to, subject, body) # Send email
ftp_connect("ftp.example.com")# Connect FTP
ftp_disconnect()              # Disconnect
ftp_list("/")                 # List files
ftp_get("/file.txt")          # Download file
ftp_put("local.txt", "/")     # Upload file
```

### WebSocket (4)
```ipp
websocket_connect("ws://...")  # Connect
websocket_send(ws, "msg")     # Send message
websocket_receive(ws)         # Receive message
websocket_close(ws)           # Close
```

### Date & Time (5)
```ipp
now()                         # Current timestamp (ms)
time()                        # Unix timestamp
clock()                       # High-res timer
delta()                       # Time since last call
format_duration(3661)         # "1h 1m 1s"
datetime()                    # Current datetime
datetime_create(2024, 1, 1)  # Create datetime
```

### Graphics & Color (12)
```ipp
canvas_open(800, 600)        # Open canvas window
canvas_rect(x, y, w, h)      # Draw rectangle
canvas_circle(x, y, r)       # Draw circle
canvas_line(x1, y1, x2, y2)  # Draw line
canvas_text(x, y, "text")    # Draw text
canvas_clear()                # Clear canvas
canvas_show()                 # Show/refresh
color(r, g, b, a)            # Create color
blend(c1, c2, t)             # Blend colors
hsl(h, s, l)                 # Create from HSL
to_hex(r, g, b)              # To hex string
from_hex("#FF0000")          # From hex string
```

### Game Math (20)
```ipp
vec2(x, y)                   # 2D vector
vec3(x, y, z)                # 3D vector
distance(p1, p2)             # 2D distance
distance_3d(p1, p2)         # 3D distance
dot(v1, v2)                  # Dot product
dot_3d(v1, v2)              # 3D dot product
cross(v1, v2)                # Cross product
normalize(v)                 # Normalize vector
normalize_3d(v)             # 3D normalize
angle(v1, v2)                # Angle between vectors
rotate(v, angle)             # Rotate 2D
lerp(a, b, t)                # Linear interpolate
move_towards(from, to, dist) # Move toward target
deg_to_rad(180)              # Degrees to radians
rad_to_deg(3.14)             # Radians to degrees
vec3(x, y, z)                # 3D vector
complex(r, i)                # Complex number
rect(x, y, w, h)             # Rectangle
```

### Graph & Data Structures (3)
```ipp
Graph()                      # Create graph
Tree()                       # Create tree
PriorityQueue()              # Priority queue
```

### Async & Concurrency (8)
```ipp
async_run(coroutine)         # Run async function
create_task(coroutine)       # Create task
is_coroutine(obj)            # Check if coroutine
is_generator(obj)            # Check if generator
next(gen)                    # Get next generator value
thread(func)                 # Start thread
thread_current()            # Current thread
thread_sleep(ms)             # Thread sleep
sleep(seconds)               # Sleep
```

### Environment (4)
```ipp
env_get("PATH")              # Get environment var
env_set("KEY", "value")      # Set environment var
list_env()                   # List all env vars
os_platform()                # Get OS platform
os_cwd()                     # Current directory
os_chdir("path")             # Change directory
path()                       # Current path
```

### Process & System (4)
```ipp
exit(0)                      # Exit with code
argparse(["--file", "x"])   # Parse args
args_parse()                 # Parse sys.argv
args_add(args, "--verbose") # Add argument
```

### Logger (1)
```ipp
logger("level", "message")   # Log message
```

### Memory Info (1)
```ipp
memory_info()               # Get memory usage {rss, vms, rss_mb, vms_mb}
```

### Other Utilities (12)
```ipp
type(x)                      # Get type of value
assert(condition, msg)       # Assert condition
assert_eq(a, b)              # Assert equal
inspect(obj)                 # Inspect object
uuid1()                      # UUID v1
uuid4()                      # UUID v4
uuid_nil()                   # Nil UUID
words("hello world")         # Split into words
path_basename("/a/b.txt")   # "b.txt"
path_dirname("/a/b.txt")    # "/a"
pathfind(grid, start, end)  # A* pathfinding
neighbors(x, y, diag)        # Get neighbors
flood_fill(grid, x, y, val) # Flood fill
glob("*.txt")                # Glob pattern match
ordict()                     # Ordered dict
deque()                      # Double-ended queue
```

### Zip & Archive (3)
```ipp
zip_create(files)           # Create zip
zip_extract(zipfile)        # Extract zip
zip_with([1,2], [3,4])       # Zip with function
```

---

## REPL Commands

Ipp REPL includes 50+ commands. Here are all of them:

### Basic Commands
```ipp
.help                   # Show help
.exit or .quit          # Exit REPL
.clear                  # Clear screen
.version                # Show version
.types                  # Show type system
```

### Session Management
```ipp
.vars                   # List user variables
.fns                    # List user functions
.builtins               # List builtin functions (color-coded)
.modules                # List available modules
.history                # Show command history
.history 10             # Last 10 commands
.last or $_              # Reference last result
.undo                   # Undo last command
.redo                   # Redo undone command
```

### File Operations
```ipp
.load file.ipp         # Load and run file (keeps variables)
.save file.txt         # Save command history to file
.import file.ipp       # Import module
```

### Benchmarking & Profiling (v1.5.4)
```ipp
.time expr              # Benchmark expression once
.bench 10 expr          # Benchmark 10 times, show avg/min/max
.profile                # Profile last command
.mem                    # Show memory usage
```

### Debugging
```ipp
.debug start            # Start step-through debugger
.debug stop             # Stop debugger
.break 5                # Set breakpoint at line 5
.watch x                # Watch variable x
.locals                 # Show local variables
.stack                  # Show call stack
.table variable        # Show list/dict as table
```

### Display & Formatting
```ipp
.pretty expr            # Pretty print
.json expr              # JSON formatted
.format expr            # Auto-format code
.colors on              # Enable colors
.colors off             # Disable colors
.theme dark             # Set theme (dark/light/solarized/monokai/gruvbox)
```

### Session State
```ipp
.session save           # Save session
.session load           # Load session
.session clear          # Clear session
.export file.ipp        # Export as script
```

### Directory & System
```ipp
.cd path               # Change directory
.ls                    # List files
.ls path               # List specific directory
.pwd                   # Print working directory
.pipe cmd              # Pipe to shell command
```

### Customization
```ipp
.prompt <fmt>          # Customize prompt
.alias n cmd           # Create alias 'n' for 'cmd'
.bind key cmd          # Set key binding
.doc function          # Show function docs
.search keyword        # Search builtins
```

### Code Editing
```ipp
.edit                  # Edit last command in editor
.format expr           # Format expression
```

### Examples & Learning
```ipp
.examples              # Show code examples
.tutorial               # Start interactive tutorial
.sighelp func          # Signature help
.typehints expr         # Show type hints
```

### Plugin System
```ipp
.plugin load file.py   # Load plugin
```

---

## Examples

### Variables & Types
```ipp
var x = 10
let PI = 3.14159
var name = "World"
var nums = [1, 2, 3, 4, 5]
var person = {"name": "Alice", "age": 30}
var point = (10, 20)  # tuple
```

### Functions
```ipp
func add(a, b) {
    return a + b
}

var multiply = func(a, b) => a * b

func factorial(n) {
    if n <= 1 { return 1 }
    return n * factorial(n - 1)
}
```

### Classes
```ipp
class Animal {
    func init(name) {
        this.name = name
    }
    func speak() {
        return "Some sound"
    }
}

class Dog : Animal {
    func init(name, breed) {
        super.init(name)
        this.breed = breed
    }
    func speak() {
        return this.name + " says woof!"
    }
}

var dog = Dog("Rex", "German Shepherd")
print(dog.speak())
```

### Loops
```ipp
for i in 0..10 {
    print(i)
}

var sum = 0
while sum < 100 {
    sum = sum + 1
}

repeat {
    print("once")
} until true
```

### Pattern Matching
```ipp
var day = 3
var result = match day {
    case 1 => "Monday"
    case 2 => "Tuesday"
    case 3 => "Wednesday"
    default => "Other day"
}
```

### Error Handling
```ipp
try {
    var result = risky_function()
} catch e {
    print("Error: " + str(e))
} finally {
    print("Cleanup")
}
```

### Enums
```ipp
enum Color {
    RED,
    GREEN,
    BLUE
}

var c = Color.RED
```

### List Comprehensions
```ipp
var squares = [x * x for x in 1..6]
var evens = [x for x in 1..10 if x % 2 == 0]
```

### Async/Await
```ipp
async function fetch_data() {
    var data = await http_get("https://api.example.com/data")
    return data
}

var task = async_run(fetch_data())
```

### Canvas Graphics
```ipp
canvas_open(800, 600)
canvas_clear()
canvas_rect(100, 100, 200, 100)
canvas_circle(400, 300, 50)
canvas_text(400, 50, "Hello Ipp!")
canvas_show()
```

---

## v1.5.4 New Features

### Benchmark with Statistics
```ipp
.bench 100 2**1000
# Output:
#   Benchmark: 100 runs
#     avg: 0.05ms  min: 0.03ms  max: 0.12ms
```

### Memory Usage
```ipp
.mem
# Output:
#   Memory Usage:
#     RSS:  45.23 MB
#     VMS:  120.45 MB
```

### Themes
```ipp
.theme monokai      # Set monokai theme
.theme gruvbox     # Set gruvbox theme
.theme solarized   # Set solarized theme
```

---

This tutorial covers all 41 keywords, 233 builtins, and 50+ REPL commands in Ipp v1.5.4.
