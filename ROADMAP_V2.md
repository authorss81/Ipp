# Ipp Language — Detailed Roadmap v3
> Last Updated: 2026-03-28 | Reflects audit findings through v1.3.0

---

## Version History

| Version | Status | Features |
|---------|--------|----------|
| v0.1.0 | ✅ DONE | Foundation (MVP) |
| v0.2.0 | ✅ DONE | Polish |
| v0.3.0 | ✅ DONE | Stability |
| v0.3.1 | ✅ DONE | Multiline + IppList fixes |
| v0.4.0 | ✅ DONE | CLI + Color/Rect + Module fixes |
| v0.5.0 | ✅ DONE | Ternary, match, bitwise, floor div, try/catch |
| v0.5.1–0.5.4 | ✅ DONE | Various improvements |
| v0.6.0 | ✅ DONE | Type system + Enums |
| v0.6.1 | ✅ DONE | Integer type, type annotations, ** power, fixed XOR |
| v0.7.0 | ✅ DONE | List/Dict Comprehensions |
| v0.8.0 | ✅ DONE | Advanced Operators + Tuples |
| v0.9.0 | ✅ DONE | Control Flow + Exceptions |
| v0.10.0 | ✅ DONE | Functions + OOP Enhancements |
| v0.11.0–0.11.2 | ✅ DONE | Standard Library Expansion |
| v0.12.0 | ✅ DONE | Module System (import, alias, selective) |
| v0.13.0 | ✅ DONE | Professional REPL UI |
| v1.0.0 | ✅ DONE | Bytecode VM Infrastructure |
| v1.0.1 | ✅ DONE | VM Stabilization & Bug Fixes |
| v1.1.0 | ✅ DONE | Performance Optimization & Profiler |
| v1.1.1 | ✅ DONE | Bug Fixes (Dict/Index Assignment) |
| v1.2.0 | ✅ DONE | Benchmark Suite + Full VM Class Support |
| v1.2.4 | ✅ DONE | 57-bug audit pass, Gemini REPL, Windows ANSI fix |
| **v1.3.0** | 🔄 IN PROGRESS | Critical bug fixes from new audit |
| **v1.3.1** | 📋 PLANNED | Closures + f-strings + default params |
| **v1.3.2** | 📋 PLANNED | VM for-loop + type system |
| **v1.3.3** | 📋 PLANNED | Operator overloading + match patterns |
| **v1.4.0** | 📋 PLANNED | Generators + async/await |
| **v1.5.0** | 📋 PLANNED | Package manager + LSP |
| **v2.0.0** | 📋 PLANNED | Game engine integration |
| **v3.0.0** | 📋 PLANNED | C API embedding |

---

## v1.3.0 — Critical Bug Sprint 🔄 IN PROGRESS

**Goal:** Fix all 3 critical bugs identified in the v1.3.0 audit before any feature work.
**Audit reference:** See `AUDIT.md` — BUG-NEW-C1, BUG-NEW-C2, BUG-NEW-C3

### Bug Fixes (Must ship before v1.3.1)

#### BUG-NEW-C1: VM `for` loop compiler stub
- [ ] Implement proper indexed iteration in `compile_for()`
- [ ] Push list + index counter as two locals
- [ ] Each iteration: check `idx < len(list)`, GET_INDEX, increment idx
- [ ] Test: VM for loop gives same results as interpreter for loop
- [ ] Test: `break` and `continue` inside VM for loop work

#### BUG-NEW-C2: Runtime errors report `line 0`
- [ ] Fix `current_line` tracking in `execute()` — set it from the node's `.line` attribute before visiting
- [ ] Propagate line numbers through all `RuntimeError` raises
- [ ] Test: error on line 4 reports `line 4`, not `line 0`

#### BUG-NEW-C3: User-class operator overloading silently broken
- [ ] In `visit_binary_expr`: check if left is `IppInstance` and has method `__add__` / `__sub__` / `__mul__` / `__truediv__` / `__eq__` / `__lt__` / `__le__` / `__gt__` / `__ge__`
- [ ] If yes, dispatch to `call_function(method, [instance, right])`
- [ ] Do NOT use Python's `hasattr(..., '__add__')` — check Ipp method table
- [ ] Test: Vec class with `__add__` can be added with `+`

#### REPL improvements for v1.3.0
- [x] `.vars` - List user-defined variables
- [x] `.fns` - List user-defined functions  
- [x] `.builtins` - List all built-in functions
- [x] `.history N` - Show command history
- [x] `.colors on/off` - Toggle colors
- [x] Ctrl+C interrupt support
- [x] Windows ANSI colour support (via SetConsoleMode)
- [x] ASCII fallback for old terminals
- [ ] `.vm` / `.interp` — switch execution engine mid-session

---

## v1.3.1 — Closures + String Interpolation + Default Parameters 📋 PLANNED

**Goal:** Fix the three most painful daily-use gaps.
**Audit reference:** BUG-NEW-M1, BUG-NEW-M3, BUG-NEW-N3

### Real Closure Variable Capture (BUG-NEW-M1)

The current implementation snapshots values. True closures require **cells** — mutable shared references.

**Plan:**
- Introduce a `Cell` class wrapping a mutable value
- Variables that are referenced by inner functions get wrapped in a `Cell` at definition time
- `GET_UPVALUE` / `SET_UPVALUE` read/write through the cell
- Interpreter: `Environment.define_cell()` + `Environment.get_cell()`
- VM: `CLOSE_UPVALUE` must actually capture the live stack slot into the closure's upvalue list

**Test:**
```ipp
func make_counter() {
    var count = 0
    func increment() { count += 1; return count }
    return increment
}
var c = make_counter()
print(c())   # must print 1
print(c())   # must print 2
print(c())   # must print 3
```

### F-strings / String Interpolation (BUG-NEW-N3)

```ipp
var name = "World"
var age = 25
print(f"Hello {name}, you are {age} years old!")
```

**Plan:**
- Lexer: detect `f"..."` prefix — lex as `FSTRING` token type
- Lexer: parse `{expr}` segments inside f-string as sub-tokens
- Parser: `FStringExpr` AST node with list of `(literal_str | ASTNode)` parts
- Interpreter: evaluate each part, call `str()` on non-strings, concatenate
- Compiler: emit CONSTANT for literal parts, compile expr for `{...}` parts, emit CONCATENATE

### Default Parameter Values (BUG-NEW-M3)

```ipp
func greet(name, greeting = "Hello") {
    return greeting + ", " + name + "!"
}
print(greet("World"))           # Hello, World!
print(greet("World", "Hi"))     # Hi, World!
```

**Plan:**
- Parser: in `function_declaration()`, after parameter name, check for `=` → parse default expr
- AST: `FunctionDecl.defaults: List[Optional[ASTNode]]`
- Interpreter: `call_function()` — if fewer args than params, use evaluated defaults
- Compiler: emit defaults as constants, check arg count at call site

### Named/Keyword Arguments (BUG-NEW-M4)

```ipp
func connect(host, port = 8080, timeout = 30) { }
connect(host = "localhost", timeout = 60)
```

**Plan:**
- Parser: detect `identifier =` pattern inside call arguments → `KeywordArg(name, value)` AST node
- Interpreter: in `visit_call_expr()`, separate positional and keyword args, map keyword args to parameter positions
- Error on unknown keyword names

---

## v1.3.2 — VM For Loop + Type System 📋 PLANNED

**Audit reference:** BUG-NEW-C1, BUG-NEW-M2, BUG-NEW-M6, BUG-NEW-N8

### VM For Loop (BUG-NEW-C1 — Full VM Implementation)

```python
# Target bytecode sequence for: for i in list { body }
CONSTANT list_expr       # push iterator list
GET_LEN                  # push len(list)
CONSTANT 0               # push index = 0
# [loop_start]
DUP2                     # dup idx, len
LESS                     # idx < len?
JUMP_IF_FALSE_POP → end  # if not, exit loop
DUP_THIRD                # dup list
GET_IDX_LOCAL            # list[idx]
SET_LOCAL var_slot       # store in loop variable
# ... body ...
INCREMENT_LOCAL idx_slot  # idx += 1
LOOP → loop_start
# [end]
POP × 3                  # clean up list, len, idx
```

### Proper `int` vs `float` Type Distinction (BUG-NEW-M2)

- `type(5)` must return `"int"`, `type(5.0)` must return `"float"`
- `int / int` returns `float` (Python default) — document this clearly
- `int // int` returns `int`
- Add `is_int(x)`, `is_float(x)` builtins
- Update `ipp_type()` in `builtins.py` and VM's `_builtin_type()`

### Set Type (BUG-NEW-M6)

```ipp
var tags = set()
tags.add("player")
tags.add("collidable")
print(tags.contains("player"))   # true
print(len(tags))                  # 2
tags.remove("collidable")
```

**Plan:**
- `IppSet` wrapper class in `interpreter.py`
- Builtin `set()` constructor
- Methods: `add()`, `remove()`, `contains()`, `union()`, `intersect()`, `difference()`
- `type(set()) = "set"`

### IppList / native list unification (BUG-NEW-N8)

- All list-returning builtins should return `IppList`, not Python `list`
- Wrap `range()` output, comprehension results, spread results in `IppList`
- Alternatively: teach `visit_get_expr` to bridge native lists to IppList methods

---

## v1.3.3 — Pattern Matching + Operator Overloading Protocol 📋 PLANNED

**Audit reference:** BUG-NEW-C3, BUG-NEW-N9, BUG-NEW-N10

### Structural Pattern Matching (BUG-NEW-N9)

Current match is equality-only. Target:

```ipp
match value {
    case int       => print("it's an int")
    case [h, ...t] => print("list starting with " + str(h))
    case Point(x, y) if x > 0 => print("positive x quadrant")
    case "hello" | "hi" => print("greeting")
    default => print("no match")
}
```

**Plan:**
- Extend `MatchStmt` pattern representation to support: type patterns, list destructure, guard clauses, OR patterns
- `visit_match_stmt` evaluates each pattern type differently
- Type pattern: `isinstance(subject, IppClass)` lookup
- List pattern: check length, bind head/tail
- Guard: evaluate `if` condition after structural match

### Full Operator Overload Protocol (BUG-NEW-C3 — interpreter fix is in v1.3.0; this adds VM support)

Define the standard dunder protocol for Ipp:

| Ipp method | Operator |
|---|---|
| `__add__(other)` | `+` |
| `__sub__(other)` | `-` |
| `__mul__(other)` | `*` |
| `__div__(other)` | `/` |
| `__mod__(other)` | `%` |
| `__pow__(other)` | `**` |
| `__eq__(other)` | `==` |
| `__lt__(other)` | `<` |
| `__le__(other)` | `<=` |
| `__neg__()` | unary `-` |
| `__len__()` | `len(obj)` |
| `__str__()` | `print(obj)`, `str(obj)` |
| `__contains__(item)` | `item in obj` |
| `__iter__()` | `for x in obj` |

**Fix `__str__` in print() (BUG-NEW-N6):** Check for user `__str__` method before calling Python's `str()`.

### Labeled Break/Continue (BUG-NEW-N10)

```ipp
outer: for i in 0..5 {
    for j in 0..5 {
        if i + j > 6 {
            break outer
        }
    }
}
```

**Plan:**
- `BreakStmt.label` and `ContinueStmt.label` already parsed and stored
- Interpreter: `break_flag` becomes `break_label: Optional[str]` — unwind until matching label
- Compiler: emit labeled JUMP that skips to end of labeled loop

---

## v1.4.0 — Generators + Async/Await 📋 PLANNED

**Audit reference:** BUG-NEW-N4, BUG-NEW-N7

### Generator Functions (BUG-NEW-N4)

```ipp
func fibonacci() {
    var a = 0
    var b = 1
    while true {
        yield a
        var temp = a
        a = b
        b = temp + b
    }
}

for n in fibonacci() |> take(10) {
    print(n)
}
```

**Plan:**
- `yield` becomes a keyword (TokenType.YIELD)
- Functions containing `yield` produce `IppGenerator` objects, not immediate values
- `IppGenerator` stores: function body AST, current execution position, local environment snapshot
- `next(gen)` resumes execution until next `yield` or return
- `for x in gen` iterates the generator

### Async/Await (BUG-NEW-N7)

```ipp
async func load_level(path) {
    var data = await read_file_async(path)
    return parse_level(data)
}
```

**Plan:**
- `async` / `await` as keywords
- Async functions return `IppFuture` objects
- Basic cooperative multitasking via Python's `asyncio` under the hood
- Game loop integration: `await next_frame()`

---

## v1.5.0 — Package Manager + LSP 📋 PLANNED

### `ippkg` — Package Manager

```bash
ippkg install math-utils
ippkg install game-physics@2.1.0
ippkg publish my-library
ippkg search collision
```

**Plan:**
- Registry: GitHub Packages (free)
- Package format: `ippkg.json` manifest (name, version, dependencies, entry point)
- `ippkg install` downloads `.ipp` files into local `ipp_modules/` directory
- Import resolution: checks `ipp_modules/` before local path
- Semantic versioning with lock file (`ippkg.lock`)

### Language Server Protocol (LSP)

- Completion: variables, functions, class methods
- Hover: show type/signature
- Go to definition
- Find references
- Diagnostics (parse/type errors)
- VS Code extension (free to publish on marketplace)

---

## v2.0.0 — Game Engine Integration 📋 PLANNED

### Engine Bindings

| Engine | Language | Binding Strategy |
|---|---|---|
| Raylib | C | ctypes + cffi |
| Pygame | Python | Direct import via Ipp builtins |
| Godot | GDScript | Ipp as alternative scripting language via GDExtension |
| Love2D | Lua | Not applicable (different host) |

### Math Library (Full)

```ipp
var v1 = vec2(3, 4)
var v2 = vec2(1, 0)
print(v1.length())          # 5.0
print(v1.dot(v2))           # 3.0
print(v1.normalize())       # vec2(0.6, 0.8)
print(v1.lerp(v2, 0.5))     # vec2(2.0, 2.0)

var m = mat4.identity()
m = m.translate(vec3(1, 2, 3))
m = m.rotate_y(45)          # degrees
```

### Physics & Collision

```ipp
var body = RigidBody(mass = 1.0, position = vec2(0, 0))
body.apply_force(vec2(0, -9.8))     # gravity
body.update(delta_time)

var rect_a = Rect(0, 0, 100, 50)
var rect_b = Rect(80, 30, 100, 50)
print(rect_a.overlaps(rect_b))      # true
print(rect_a.intersection(rect_b))  # Rect(80, 30, 20, 20)
```

---

## v3.0.0 — C API / Embedding 📋 PLANNED

### C API Goals

```c
// Embed Ipp in a C/C++ game engine
IppVM* vm = ipp_vm_create();
ipp_vm_register_function(vm, "get_player_pos", my_get_pos);
ipp_vm_exec_file(vm, "game_logic.ipp");
IppValue result = ipp_vm_call(vm, "update", delta_time);
ipp_vm_destroy(vm);
```

### Rust Bindings

```rust
let vm = IppVM::new();
vm.register_fn("draw_sprite", |args| { /* ... */ });
vm.exec("game.ipp")?;
```

---

## Fixed vs Remaining Issues (Audit Tracker)

| Bug ID | Description | Target Version | Status |
|---|---|---|---|
| BUG-NEW-C1 | VM for loop stub | v1.3.0 | 🔴 Open |
| BUG-NEW-C2 | Runtime errors line 0 | v1.3.0 | 🔴 Open |
| BUG-NEW-C3 | Operator overloading broken | v1.3.0 | 🔴 Open |
| BUG-NEW-M1 | Closures capture by value | v1.3.1 | 🟠 Open |
| BUG-NEW-M2 | int/float indistinguishable | v1.3.2 | 🟠 Open |
| BUG-NEW-M3 | No default params | v1.3.1 | 🟠 Open |
| BUG-NEW-M4 | Named args wrong results | v1.3.1 | 🟠 Open |
| BUG-NEW-M5 | VM upvalues by value | v1.3.1 | 🟠 Open |
| BUG-NEW-M6 | No Set type | v1.3.2 | 🟠 Open |
| BUG-NEW-M7 | No tuple unpacking | v1.3.1 | 🟠 Open |
| BUG-NEW-N1 | No private enforcement | v1.5.0 | 🟡 Open |
| BUG-NEW-N2 | No Ipp recursion limit | v1.3.0 | 🟡 Open |
| BUG-NEW-N3 | No f-strings | v1.3.1 | 🟡 Open |
| BUG-NEW-N4 | No generators/yield | v1.4.0 | 🟡 Open |
| BUG-NEW-N5 | Runtime errors no column | v1.3.0 | 🟡 Open |
| BUG-NEW-N6 | __str__ not called by print | v1.3.0 | 🟡 Open |
| BUG-NEW-N7 | No async/await | v1.4.0 | 🟡 Open |
| BUG-NEW-N8 | IppList/native list gap | v1.3.2 | 🟡 Open |
| BUG-NEW-N9 | Match is equality-only | v1.3.3 | 🟡 Open |
| BUG-NEW-N10 | Labeled break silently broken | v1.3.3 | 🟡 Open |

---

## Free Tools Referenced

| Tool | Purpose | URL |
|------|---------|-----|
| GitHub Actions | CI/CD | github.com/features/actions |
| GitHub Pages | Documentation | pages.github.com |
| GitHub Packages | Package registry | github.com/features/packages |
| MkDocs Material | Beautiful docs | squidfunk.github.io/mkdocs-material |
| Read the Docs | OSS docs hosting | readthedocs.org |
| Raylib | Game library | raylib.com |
| Pygame | Python game lib | pygame.org |
| Godot | Game engine | godotengine.org |
| VS Code | IDE | code.visualstudio.com |
| Crafting Interpreters | Language book | craftinginterpreters.com |

---

## Success Metrics

### Technical (by v1.5.0)
- [ ] All 20 new audit bugs resolved
- [ ] VM and interpreter produce identical results on 100% of test cases
- [ ] 200+ test cases with 100% pass rate
- [ ] Benchmarks published: Ipp within 5x of Lua on common game loops

### Community (by v2.0.0)
- [ ] 500 GitHub stars
- [ ] 100 Discord members
- [ ] 25 community contributions
- [ ] 10 example game projects
- [ ] 1 YouTube tutorial series (AI-generated or manual)
- [ ] Featured on Hacker News

### Adoption (by v3.0.0)
- [ ] `ippkg` with 20+ published packages
- [ ] VS Code extension with 1,000+ installs
- [ ] 3 shipped games using Ipp scripting
- [ ] 1 game engine with official Ipp support

---

*Roadmap v3 — 2026-03-28 | Aligned with AUDIT.md v1.3.0 supplement*
