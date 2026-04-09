# Ipp Language — Detailed Roadmap v5
> Last Updated: 2026-04-08 | Reflects audit findings through v1.5.1

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
| **v1.0.0** | ✅ DONE | Bytecode VM Infrastructure |
| **v1.0.1** | ✅ DONE | VM Stabilization & Bug Fixes |
| **v1.1.0** | ✅ DONE | Performance Optimization & Profiler |
| **v1.1.1** | ✅ DONE | Bug Fixes (Dict/Index Assignment) |
| **v1.2.0** | ✅ DONE | Benchmark Suite vs Other Languages |
| **v1.2.4** | ✅ DONE | Full VM Class Support |
| **v1.3.0** | ✅ DONE | REPL Enhancements |
| **v1.3.1** | ✅ DONE | Critical + Major Bugs Fixed |
| **v1.3.2** | ✅ DONE | VM Stabilization (upvalues) + Set type |
| **v1.3.3** | ✅ DONE | Bug Fixes + Standard Library + Networking |
| **v1.3.4** | ✅ DONE | Comprehensive stdlib testing (130+ builtins) |
| **v1.3.5** | ✅ DONE | Regex fix + REPL color fix |
| **v1.3.6** | ✅ DONE | VM compatibility tests + REPL warning |
| **v1.3.7** | ✅ DONE | REPL enhancements (10 new commands) |
| **v1.3.8** | ✅ DONE | HTTP Server, WebSocket, PriorityQueue, Tree, Graph |
| **v1.3.9** | ✅ DONE | REPL error handling (smart suggestions) |
| **v1.3.10** | ✅ DONE | REPL Intelligence (tab completion, debugger, themes) |
| **v1.4.0** | ✅ DONE | Generator functions + all 7 VM bugs fixed |
| **v1.4.1** | ✅ DONE | Error Documentation + Error Reference Guide |
| **v1.4.2** | ✅ DONE | Tutorial Documentation + Getting Started Guide |
| **v1.4.3** | ✅ DONE | PyPI Publishing + `pip install ipp-lang` |
| **v1.5.0** | ✅ DONE | Async/Await + Coroutines + Event Loop + Additional Builtins |
| **v1.5.1** | ✅ DONE | VSCode Extension + LSP |
| **v1.5.2a** | 🔄 PARTIAL | WASM Backend (basic, needs more work) |
| **v1.5.2b** | 🔄 PARTIAL | Web Playground (basic, needs more work) |
| **v1.5.3a** | 🔄 PARTIAL | 2D Canvas (REPL works, needs enhancement) |
| **v1.5.3b** | 🔧 IN PROGRESS | WebGL Bindings |
| **v1.5.3** | 📋 PLANNED | WebGL Integration + 2D Canvas Rendering |
| **v1.5.4** | 📋 PLANNED | Repl Enhancements| 
| **v1.5.5** | 📋 PLANNED | 3D Rendering + Scene Graph |
| **v1.6.0** | 📋 PLANNED | C++ Integration + Native Extensions |
| **v1.6.1** | 📋 PLANNED | Cross-Platform (iOS, macOS, Linux, Windows Installer) |
| **v2.0.0** | 📋 PLANNED | Package Manager + Full Ecosystem + Game Engine |

---

## v1.3.0 - REPL Enhancements & Bug Fixes ✅ DONE

**Goal**: Complete REPL features, fix critical bugs before any feature work

### REPL Enhancements ✅ DONE
- [x] `.vars` - List user-defined variables
- [x] `.fns` - List user-defined functions
- [x] `.builtins` - List all built-in functions
- [x] `.modules` - Show modules by category
- [x] `.history N` - Show command history (default 20)
- [x] `.colors on/off` - Toggle colors
- [x] `.vm interpreter/vm` - Switch interpreters
- [x] `\` multiline continuation
- [x] Ctrl+C interrupt support
- [x] Colorful function display (purple/blue/cyan/orange)
- [x] ANSI garbage prevention
- [x] Git tags created for all releases (v0.6-v1.3.0)

### Critical Bug Fixes ✅ DONE
- [x] BUG-NEW-C1: **VM `for` loop is a non-functional stub** ✅ FIXED
- [x] BUG-NEW-C2: **Runtime errors always report `line 0`** ✅ FIXED
- [x] BUG-NEW-C3: **User-class operator overloading silently broken** ✅ FIXED

**Fix Complexity:**
| Bug | Complexity | Priority |
|-----|------------|----------|
| BUG-NEW-C1 | HIGH | ✅ DONE |
| BUG-NEW-C2 | MEDIUM | ✅ DONE |
| BUG-NEW-C3 | MEDIUM | ✅ DONE |

---

## v1.3.1 - Closures, F-strings, Default Params, Type System ✅ DONE

**Audit reference:** BUG-NEW-M1, BUG-NEW-M2, BUG-NEW-M3, BUG-NEW-N3

### BUG-NEW-M1: Closures Capture by Reference ✅ DONE (Interpreter)
- [x] Interpreter closures work correctly
- [x] `count += 1` propagates to outer scope
- [x] Nested closures tested
- ⚠️ VM closures still broken (BUG-NEW-M5)

### BUG-NEW-M2: int/float Type Distinction ✅ DONE
- [x] `type(5)` returns `"int"` ✅
- [x] `type(5.0)` returns `"float"` ✅

### BUG-NEW-M3: Default Parameter Values ✅ DONE
- [x] Parse `func f(x, y=0)` syntax
- [x] Store defaults in `FunctionDecl`
- [x] Fill in missing args in `call_function()`

### BUG-NEW-N3: F-strings / String Interpolation ⏳ TODO
- [ ] Lex `f"..."` as f-string token
- [ ] Parse `{expr}` segments
- [ ] Implement `fstring(format, *values)` builtin

---

## v1.3.2 - VM Stabilization & Set Type ⚠️ IN PROGRESS

**Note:** VM upvalues and Set type are done. Class instantiation fix in progress.

**Audit reference:** BUG-NEW-M5, BUG-NEW-M6

### BUG-NEW-M5: VM Upvalues by Reference ✅ DONE
- [x] Implement proper upvalue cells in VM
- [x] Move to heap on `CLOSE_UPVALUE`
- [x] Read/write through upvalue pointer

### BUG-NEW-M6: Set Data Type ✅ DONE
- [x] Implement `IppSet` class
- [x] Add `add()`, `remove()`, `contains()`
- [x] Expose `set()` builtin

---

## v1.3.3 - Game SDK Alpha + Standard Library + Bug Fixes ✅ DONE

**Goal**: Alpha game development toolkit + Standard Library Completion + Bug Fixes

**Audit reference:** BUG-NEW-C3, BUG-NEW-M4, BUG-NEW-N6, BUG-NEW-N8, BUG-NEW-N9, BUG-NEW-N10

### Bug Fixes ✅ DONE

#### BUG-NEW-C3: Operator Overloading Fix ✅ DONE
- [x] Changed `hasattr(left, '__add__')` to check `left.fields` via `_ipp_has_method()`
- [x] Dispatch to Ipp methods, not Python dunders
- [x] Test `__add__`, `__sub__`, `__mul__`, `__eq__`

#### BUG-NEW-M4: Named Arguments ✅ DONE
- [x] Parse named args in `_parse_arguments()`
- [x] Match by name in `call_function()` via `_merge_named_args()`
- [x] Support for both positional and named arguments

#### BUG-NEW-M7: Tuple Unpacking / Multiple Assignment ✅ DONE
- [x] Parse `var a, b = 1, 2` syntax
- [x] Implement unpacking in `visit_multi_var_decl()`

#### BUG-NEW-N6: __str__ Method ✅ DONE
- [x] Check for `__str__` method on IppInstance
- [x] Execute custom __str__ when print() is called
- [x] Avoid infinite recursion with nested instances

#### BUG-NEW-N8: IppList/Native List Inconsistency ✅ DONE
- [x] Wrap all list returns to IppList
- [x] Added explicit IppList guard in `visit_call_expr` with clear error message
- [x] Ensure consistent behavior between IppList and native Python lists

#### Bug 1: and/or precedence with comparisons ✅ DONE
- [x] Root cause: `and`/`or` keywords mapped to `DOUBLE_AMP`/`DOUBLE_PIPE` tokens (shared with bitwise &/|)
- [x] `token.py`: `"and"` → `TokenType.AND`, `"or"` → `TokenType.OR` (dedicated tokens)
- [x] `parser.py`: `or_expr`/`and_expr` match new AND/OR tokens; `&&`/`||` remain as aliases
- [x] `interpreter.py`: `and`/`or` now short-circuit before evaluating both sides

#### Bug 2: nested len(items(d)) IppList error ✅ DONE
- [x] Root cause: `items()` returning plain Python list with `__call__` in introspection paths
- [x] Added explicit `IppList` guard in `visit_call_expr` with clear error message
- [x] Nested calls now work directly

### Standard Library Expansion ✅ DONE
- [x] Missing Builtins: `printf()`, `sprintf()`, `scanf()`, `file_read()`, `file_write()`
- [x] Regex module: Full regex support
- [x] XML module: XML parsing
- [x] YAML module: YAML parsing
- [x] TOML module: TOML parsing
- [x] ZIP module: Zip file handling

### Collections ✅ DONE
- [x] `Deque` - Fast queue operations
- [x] `PriorityQueue` - Heap-based priority queue
- [x] `Tree` - Tree data structure
- [x] `Graph` - Graph data structure

### Math Library ✅ DONE
- [x] `vec2(x, y)` - 2D vector
- [x] `vec3(x, y, z)` - 3D vector
- [x] `vec4(x, y, z, w)` - 4D vector
- [x] `mat2()` - 2x2 matrix
- [x] `mat3()` - 3x3 matrix
- [x] `mat4()` - 4x4 matrix
- [x] `quat()` - Quaternion
- [x] `Math.lerp()`, `Math.clamp()`, `Math.remap()`
- [x] `Math.distance()`, `Math.normalize()`
- [x] `Math.angle()`, `Math.radians()`, `Math.degrees()`

### Game Primitives ✅ DONE
- [x] `Rect(x, y, w, h)` - Rectangle
- [x] `Circle(x, y, r)` - Circle
- [x] `Color(r, g, b, a)` - Color
- [x] `Point(x, y)` - 2D point
- [x] `Line(x1, y1, x2, y2)` - Line segment

### Collision ✅ DONE
- [x] `Rect.overlaps(other)` - AABB collision
- [x] `Circle.overlaps(other)` - Circle collision
- [x] `point_in_rect(p, r)` - Point in rectangle
- [x] `line_intersects(l1, l2)` - Line intersection
- [x] `raycast(origin, direction, max_dist)` - Ray casting

### Easing ✅ DONE
- [x] `Easing.linear()`
- [x] `Easing.ease_in()`, `Easing.ease_out()`
- [x] `Easing.ease_in_out()`
- [x] `Easing.bounce()`, `Easing.elastic()`

### Random ✅ DONE
- [x] `Random.seed(n)` - Set seed
- [x] `Random.choice(seq)` - Random choice
- [x] `Random.shuffle(seq)` - Shuffle in place
- [x] `Random.gauss(mu, sigma)` - Gaussian distribution

### Networking ✅ DONE
- [x] `http_get`, `http_post`, `http_put`, `http_delete`, `http_request` - HTTP client
- [x] `ftp_connect`, `ftp_disconnect`, `ftp_list`, `ftp_get`, `ftp_put` - FTP client
- [x] `smtp_connect`, `smtp_disconnect`, `smtp_send` - SMTP email
- [x] `url_encode`, `url_decode`, `url_query_build`, `url_query_parse` - URL utilities
- [ ] `http.server` - HTTP server (planned for v1.3.8)
- [ ] `websocket` - WebSocket client/server (planned for v1.3.8)

---

## v1.3.7 — REPL Enhancements ✅ DONE

### REPL Improvements ✅ DONE
- [x] `.edit` — Open last command in external editor
- [x] `.save <file>` — Save session history to file
- [x] `.load <file>` — Load and execute file in current session (keep variables)
- [x] `.doc <function>` — Show docstring/help for builtin
- [x] Multi-line paste detection
- [x] `.time <expr>` — Benchmark expression
- [x] `.which <name>` — Show if name is builtin/variable/function
- [x] `.last` / `$_` — Reference last result
- [x] `.undo` — Undo last command's effect
- [x] `.profile` — Profile last command
- [x] `.alias <name> <cmd>` — Custom REPL aliases

---

## v1.3.8 — Networking + Collections ✅ DONE

### HTTP Server ✅ DONE
- [x] `http_serve(handler, host, port)` — Start HTTP server
- [x] Request/response objects with headers, body, query params
- [x] Routing with pattern matching (via handler function)
- [x] Supports GET, POST, PUT, DELETE

### WebSocket ⏳ TODO
- [ ] `websocket.server(handler, host, port)` — WebSocket server
- [ ] `websocket.connect(url)` — WebSocket client
- [ ] Message send/receive

### PriorityQueue ✅ DONE
- [x] `PriorityQueue()` — Heap-based priority queue
- [x] `push(item, priority)` — Add item with priority
- [x] `pop()` — Remove and return highest priority item
- [x] `peek()` — View highest priority item without removing
- [x] `is_empty()` — Check if queue is empty
- [x] `len()` — Get queue size

### Tree/Graph ✅ DONE
- [x] `Tree(value, children)` — Tree data structure
- [x] `Graph(directed)` — Graph data structure
- [x] Tree traversal (pre-order, post-order, BFS)
- [x] Graph algorithms (DFS, BFS, Dijkstra shortest path)
- [x] `Tree.add_child()`, `remove_child()`, `get_child()`, `find()`, `depth()`
- [x] `Graph.add_node()`, `add_edge()`, `remove_node()`, `remove_edge()`
- [x] `Graph.has_node()`, `has_edge()`, `get_neighbors()`, `shortest_path()`
- [x] Directed and undirected graph support

---

## v1.3.10 — REPL Intelligence + Debugging ✅ DONE

### Tab Completion ✅ DONE
- [x] Tab completion for keywords, builtins, variables
- [x] Tab completion for dict keys (`my_dict["<TAB>`)
- [x] Tab completion for file paths (`import "<TAB>`)
- [x] Fuzzy matching for completions (e.g., `htgt` → `http_get`)
- [x] REPL command completion (`.help`, `.load`, etc.)
- [x] Member completion (`obj.<TAB>`)
- [x] Type hints on hover/tab
- [x] Signature help when typing `(`

### Code Intelligence ✅ DONE
- [x] Auto-indentation after `{`, `(`, `[`
- [x] Bracket matching configuration
- [x] Pretty printing — `_pretty_print()` for nested structures
- [x] Expression history — `$_1`, `$_2`, etc. injected into interpreter
- [x] `.redo` — Redo after `.undo`
- [x] `.session save/load/clear` — Session persistence
- [x] `.pretty <expr>` — Pretty print complex data
- [x] `.stack` — Show call stack
- [x] `! <cmd>` — Execute shell commands
- [x] `.history $_` — Show expression history

### Debugging ✅ DONE
- [x] `.debug start/stop` — Step-through debugger
- [x] `.break <line>` — Set breakpoints by line number
- [x] `.watch <expr>` — Watch expressions
- [x] `.locals` — Show local variables

### Output Improvements ✅ DONE
- [x] `.table <var>` — Show list of dicts as formatted table
- [x] `.json <expr>` — JSON viewer with formatting
- [x] `.format <expr>` — Auto-format code on Enter

### Shell Integration ✅ DONE
- [x] `! <cmd>` — Execute shell commands
- [x] `.pipe <cmd>` — Pipe output to shell command
- [x] `.cd <dir>` — Change directory
- [x] `.ls [dir]` — List directory contents
- [x] `.pwd` — Print working directory

### Session Management ✅ DONE
- [x] Session persistence — auto-save/restore across restarts
- [x] Multiple named sessions (`.session save/load/switch`)
- [x] Session export — save session as `.ipp` script file
- [x] `.redo` — redo after `.undo`
- [x] Expression history — access previous results with `$_1`, `$_2`, etc.
- [x] `.sessions` — List saved sessions
- [x] `.session export` — Export session as .ipp

### Customization ✅ DONE
- [x] Custom themes — color scheme selection (`.theme dark/light/solarized`)
- [x] Prompt customization — custom prompt format (`.prompt dir/time/full/ipp`)
- [x] Key bindings — customizable keyboard shortcuts (`.bind <key> <cmd>`)
- [x] Plugin system — load custom `.ipp` plugins that add REPL commands

### Documentation ✅ DONE
- [x] `.tutorial` — Interactive tutorial mode
- [x] `.plugin load <file>` — Load plugin files
- [x] `.search <keyword>` — Search builtin documentation with keywords
- [x] `.examples` — Show interactive code examples (10 examples)
- [x] Contextual help — show relevant help based on current error
- [x] `.typehints` — Show type hints
- [x] `.sighelp` — Show signature help

---

## v1.4.0 — Generators + VM Bug Fixes ✅ DONE

### Generator Functions ✅ DONE
- [x] Lex `yield` as keyword
- [x] Create `IppGenerator` object
- [x] Serialize/resume execution state via yield count tracking
- [x] `next(gen)` builtin function
- [x] `is_generator(obj)` builtin function
- [x] For-in loop support for generators

### VM Bug Fixes ✅ DONE (by contributor)
- [x] VM-BUG-1: Function calls with arguments — `add(3, 4)` returns 7
- [x] VM-BUG-2: Dict index access — `d["key"]` works correctly
- [x] VM-BUG-3: Try/catch — catches undefined variables
- [x] VM-BUG-4: Class property access — `instance.field` works
- [x] VM-BUG-5: Named arguments — `f(y=1, x=10)` works
- [x] VM-BUG-6: Recursion — `fib(10)` returns 55
- [x] VM-BUG-7: For loops — `for i in 0..5` works

### Async/Await ⏳ TODO (moved to v1.5.0)
- [ ] Implement async/await over generators
- [ ] Add event loop
- [ ] Handle `await expr` as `yield wait(expr)`

---

## v1.4.1 — Error Documentation ✅ DONE

### Error Reference Guide ✅ DONE
- [x] Create `ERRORS.md` with all error types and messages
- [x] Document every runtime error with causes and fixes
- [x] Document every parse error with examples
- [x] Add "Did you mean?" suggestions for common errors
- [x] Link errors to relevant documentation sections

### Error Codes System ✅ DONE
- [x] Assign unique codes to each error (E001-E008 parse, E100-E109 runtime, E200-E201 VM)
- [x] 20 error codes documented
- [x] All error codes verified against actual error messages

---

## v1.4.2 — Tutorial Documentation ✅ DONE

### Getting Started Guide ✅ DONE
- [x] Installation guide (pip, source, binary)
- [x] "Hello World" tutorial
- [x] Variables, types, and operators tutorial
- [x] Control flow tutorial (if/for/while/match)
- [x] Functions and closures tutorial
- [x] Classes and OOP tutorial
- [x] Modules and imports tutorial
- [x] 25 code examples — all verified and passing

### Reference Documentation ✅ DONE
- [x] Complete builtin function reference (132+ functions)
- [x] Standard library documentation

---

## v1.4.3 — PyPI Publishing ✅ DONE

### Package Setup ✅ DONE
- [x] Create `pyproject.toml`
- [x] Add package metadata (name, version, description, license)
- [x] Define entry points: `ipp run`, `ipp check`, `ipp repl`
- [x] Add requirements (no dependencies for core)

### Publishing ✅ DONE
- [x] Build source distribution: `ipp-lang-1.4.2.tar.gz`
- [x] GitHub Actions workflow for auto-publish on release
- [x] Install command: `pip install ipp-lang`

---

## v1.5.0 — Async/Await + Coroutines + Event Loop ✅ DONE

### Async/Await Implementation ✅ DONE
- [x] Add event loop to interpreter
- [x] Compile `await expr` as `yield wait(expr)`
- [x] Mark functions with `await` as async automatically
- [x] Add `async` keyword for explicit async functions
- [x] Implement `sleep()` as awaitable
- [x] Implement `wait()` builtin for awaiting multiple futures

### Coroutines ✅ DONE
- [x] `coroutine(func)` — create coroutine from generator
- [x] `coro.send(value)` — send value to coroutine
- [x] `coro.close()` — close coroutine
- [x] `coro.throw(exc)` — throw exception into coroutine

---

## v1.5.1 — VSCode Extension ✅ DONE

### LSP Server ✅ DONE
- [x] `ipp lsp` — start LSP server
- [x] Go-to-definition
- [x] Find all references
- [x] Symbol search
- [x] Hover information (type, docstring)
- [x] Diagnostics (linting, type hints)
- [x] Auto-completion
- [x] Rename symbol
- [x] Code actions / quick fixes
- [x] Document symbols (outline)

### VSCode Features ✅ DONE
- [x] Syntax highlighting (TMGrammar)
- [x] Snippets (func, class, for, while, etc.)
- [x] LSP integration (diagnostics, completion, hover)
- [x] Run/Debug Ipp code from VSCode
- [x] Integrated REPL panel
- [x] Task runner for `ipp run`, `ipp check`

### Other IDE Extensions (included in v1.5.1)
- [ ] Vim/Neovim plugin
- [ ] Emacs major mode
- [ ] Sublime Text package

---

## v1.5.2 — WASM Backend Infrastructure ✅ DONE

### v1.5.2a: WASM Backend ✅ DONE
- [x] Test infrastructure for WASM compilation
- [x] WASM module (`ipp/wasm/compiler.py`)
- [x] Create `ipp wasm <file>` CLI command
- [x] Generate `.wat` file from Ipp source

### v1.5.2b: Web Playground 📋 PLANNED
- [ ] Create web-based Ipp playground (like Rust Playground)
- [ ] Monaco Editor for syntax highlighting
- [ ] Run Ipp code in browser via WASM
- [ ] Share code via URL
- [ ] Save/load code snippets

---

## v1.5.3 — WebGL Integration + 2D Rendering 🔄 PARTIAL

### v1.5.3a: 2D Canvas API 🔄 PARTIAL
- [x] `canvas.rect(x, y, w, h, color)` ✅ REPL works
- [x] `canvas.circle(x, y, r, color)` ✅ REPL works  
- [x] `canvas.line(x1, y1, x2, y2, color)` ✅ REPL works
- [x] `canvas.text(x, y, text, color)` ✅ REPL works
- [x] `canvas.clear(color)` ✅ REPL works
- [ ] Enhanced drawing (filled shapes, stroke, etc.)
- [ ] Animation support
- [ ] Mouse/keyboard input support

### v1.5.3b: WebGL Bindings 🔧 IN PROGRESS
- [ ] `webgl.init(canvas)` — initialize WebGL context
- [ ] `webgl.create_shader(source, type)` — create shader
- [ ] `webgl.create_program(vertex, fragment)` — create program
- [ ] `webgl.draw_triangles(vertices, colors)` — render triangles
- [ ] `webgl.set_uniform(name, value)` — set uniform values

---

## v1.5.4 — REPL Performance + Advanced Features 📋 PLANNED
### Performance & Monitoring
- [ ] Real-time profiling — CPU/memory stats per command
- [ ] Benchmark mode — run command N times, show avg/min/max
- [ ] Hot reload — auto-reload imported modules when files change
- [ ] Async REPL — handle `async/await` natively in REPL
- [ ] Background tasks — run long tasks in background
### Advanced REPL Features
- [ ] Multi-line editor — full editor for multi-line input
- [ ] Code snippets — predefined templates
- [ ] Memory profiler — show memory usage per variable/object
- [ ] REPL server — connect to REPL remotely via network
- [ ] Code review mode — compare two expressions side-by-side
- [ ] Macro system — define REPL macros that expand to code
- [ ] Checkpoint/rollback — save checkpoint, rollback to any point
### Data Visualization
- [ ] Plot graphs/charts from data (matplotlib integration)
- [ ] HTML preview — render HTML strings in browser
---

## v1.5.5 — 3D Rendering + Scene Graph 📋 PLANNED
### 3D Math
- [ ] `mat4()` — 4x4 matrix operations
- [ ] `vec4()` — 4D vector
- [ ] `quat()` — quaternion operations (slerp, rotate)
- [ ] `perspective(fov, aspect, near, far)` — perspective matrix
- [ ] `look_at(eye, target, up)` — view matrix
### Scene Graph
- [ ] `Scene()` — scene container
- [ ] `Node()` — scene node with transform
- [ ] `Camera(fov, aspect)` — camera node
- [ ] `Mesh(vertices, indices)` — mesh node
- [ ] `Light(type, color, intensity)` — light node
- [ ] `scene.render()` — render scene
---

## v1.6.0 — C++ Integration 📋 PLANNED

### C++ API
- [ ] `#include "ipp.hpp"` — C++ header for embedding
- [ ] `ipp::Interpreter` — C++ interpreter class
- [ ] `ipp::VM` — C++ VM class
- [ ] `ipp::register_function(name, func)` — register C++ functions
- [ ] `ipp::register_class(name, methods)` — register C++ classes
- [ ] `ipp::call(function, args)` — call Ipp functions from C++

### Native Extensions
- [ ] Extension loading: `import "myext.so"`
- [ ] Extension API for C/C++ modules
- [ ] Build system for extensions (CMake)

---

## v1.6.1 — Cross-Platform 📋 PLANNED

### Platform Support
- [ ] macOS: Homebrew formula (`brew install ipp`)
- [ ] Linux: APT/DEB package, Snap/Flatpak
- [ ] Windows: MSI installer, Scoop/Chocolatey
- [ ] iOS: Ipp runtime for iOS apps
- [ ] Android: Ipp runtime for Android apps

### CI/CD
- [ ] GitHub Actions for all platforms
- [ ] Auto-build on release
- [ ] Cross-compilation pipeline

---

## v2.0.0 — Package Manager + Full Ecosystem 📋 PLANNED

### Package Manager
- [ ] `ippkg` CLI tool
- [ ] Package registry
- [ ] `ippkg install <package>`
- [ ] `ippkg publish <package>`
- [ ] Dependency resolution
- [ ] Version management
- [ ] `ippkg search <query>`

### Standard Library Expansion
- [ ] HTTP/2 support
- [ ] GraphQL client
- [ ] Database drivers (SQLite, PostgreSQL)
- [ ] WebSocket client/server
- [ ] Image processing
- [ ] Audio processing

### Game Engine Features
- [ ] Advanced math: Matrix operations, Quaternion math, Barycentric coordinates
- [ ] Bezier curves, Perlin noise, Simplex noise
- [ ] Physics: Rigid body, AABB/Sphere collision, Impulse resolution, Joints
- [ ] Particles: Particle system, Emitter types, Particle properties
- [ ] Scene Graph: Entity class, Transform, Node hierarchy, Camera, Layer system

---

## Free Tools & Services (No Money Required)

### Development Tools
| Tool | Purpose | Cost | URL |
|------|---------|------|-----|
| GitHub | Source control, CI/CD | FREE | github.com |
| GitHub Actions | CI/CD pipelines | FREE | github.com/features/actions |
| GitHub Pages | Static website hosting | FREE | pages.github.com |
| VS Code | IDE with extensions | FREE | code.visualstudio.com |
| Neovim | Modal editor | FREE | neovim.io |
| MkDocs | Documentation generator | FREE | www.mkdocs.org |
| Sphinx | Documentation generator | FREE | www.sphinx-doc.org |

### Testing & Quality
| Tool | Purpose | Cost | URL |
|------|---------|------|-----|
| pytest | Test framework | FREE | pytest.org |
| Coverage.py | Code coverage | FREE | coverage.readthedocs.io |
| pre-commit | Git hooks | FREE | pre-commit.com |
| Ruff | Fast linter (Python) | FREE | github.com/astral-sh/ruff |
| Black | Code formatter | FREE | black.readthedocs.io |
| MyPy | Type checking | FREE | mypy.readthedocs.io |

### Documentation
| Tool | Purpose | Cost | URL |
|------|---------|------|-----|
| MkDocs | Static docs from Markdown | FREE | www.mkdocs.org |
| Material for MkDocs | Beautiful theme | FREE | squidfunk.github.io/mkdocs-material |
| Read the Docs | Docs hosting | FREE (OSS) | readthedocs.org |
| Docusaurus | React docs | FREE | docusaurus.io |
| GitBook | Docs platform | FREE tier | gitbook.com |

### Package Distribution
| Tool | Purpose | Cost | URL |
|------|---------|------|-----|
| GitHub Packages | Package registry | FREE | github.com/features/packages |
| PyPI | Python package index | FREE | pypi.org |
| npm | JS package registry | FREE | npmjs.com |
| Test PyPI | Testing packages | FREE | test.pypi.org |

### Game Dev (Free)
| Tool | Purpose | Cost | URL |
|------|---------|------|-----|
| Raylib | Simple game library (C) | FREE | raylib.com |
| Pygame | Python game library | FREE | pygame.org |
| Godot | Full game engine | FREE | godotengine.org |
| LÖVE | Lua game framework | FREE | love2d.org |
| SFML | Simple multimedia library | FREE | sfml-dev.org |

### Community & Marketing (FREE)
| Platform | Purpose | Cost | URL |
|----------|---------|------|-----|
| Reddit | Community discussion | FREE | reddit.com |
| Hacker News | Tech community | FREE | news.ycombinator.com |
| Twitter/X | Social media | FREE | x.com |
| Discord | Community server | FREE | discord.com |
| Reddit r/gamedev | Game dev community | FREE | reddit.com/r/gamedev |
| Reddit r/Python | Python community | FREE | reddit.com/r/Python |

### Learning Resources (FREE)
| Resource | Purpose | Cost | URL |
|----------|---------|------|-----|
| Crafting Interpreters | Language design book | FREE | craftinginterpreters.com |
| Write you a Haskell | Compiler book | FREE | wwwhomersimpson.me |
| Let's Build a Compiler | Compiler tutorial | FREE | bellatorey.com/languages |
| Game Programming Patterns | Game dev book | FREE | gameprogrammingpatterns.com |
| Learn OpenGL | Graphics tutorial | FREE | learnopengl.com |

---

## Implementation Priorities (Manual Work Required)

### Phase 1: Documentation (v1.4.1 - v1.4.3)
1. **Error Documentation** - ERROR.md with all error types
2. **Tutorial Documentation** - Getting started + advanced guides
3. **PyPI Publishing** - pip install ipp-lang

### Phase 2: Async + Web (v1.5.0 - v1.5.3)
1. **Async/Await** - Event loop + coroutines
2. **WASM** - Web compilation + playground
3. **WebGL** - 2D/3D rendering

### Phase 3: Integration (v1.6.0 - v1.6.3)
1. **C++ API** - Native embedding
2. **Cross-Platform** - iOS, macOS, Linux, Windows
3. **LSP** - Language server protocol
4. **VSCode** - IDE extension

### Phase 4: Ecosystem (v2.0.0)
1. **Package Manager** - ippkg + registry
2. **Game Engine** - Full game development toolkit

---

## Success Metrics

### Community Growth
- [ ] 100 GitHub stars
- [ ] 50 Discord members
- [ ] 10 community contributions
- [ ] 5 example projects

### Technical Quality
- [ ] 100% regression test coverage
- [ ] Benchmarks published and updated
- [ ] Documentation completeness > 90%
- [ ] Zero critical bugs in production

### Adoption
- [ ] 10 projects using Ipp in production
- [ ] 3 game projects using Ipp SDK
- [ ] Featured on Hacker News or Reddit

---

*Last Updated: 2026-04-07 (v1.4.0 DONE - Generators + VM bugs fixed. Roadmap restructured with one feature per version for session-completable releases.)*
