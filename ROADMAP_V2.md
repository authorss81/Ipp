# Ipp Language — Detailed Roadmap v3
> Last Updated: 2026-03-29 | Reflects audit findings through v1.3.2

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
| **v1.3.0** | ✅ DONE | REPL Enhancements (`.vars`, `.fns`, `.history`, `.vm`, `\`, Ctrl+C, colors) |
| **v1.3.1** | ✅ DONE | Critical + Major Bugs Fixed (for-loop, line 0, overload, defaults, int/float, closures) |
| **v1.3.2** | ✅ DONE | VM Stabilization (upvalues) + Set type + Class Fix |
| **v1.3.3** | ✅ DONE | Bug Fixes + Standard Library + Math + Collections + Networking |
| **v1.4.0** | 📋 PLANNED | Generators + Engine Integration |
| **v2.0.0** | 📋 PLANNED | Advanced Game Features |

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

## v1.4.0 — Generators + Async/Await + Engine Integration 📋 PLANNED

**Audit reference:** BUG-NEW-N4, BUG-NEW-N7

### BUG-NEW-N4: Generator Functions ⏳ TODO
- [ ] Lex `yield` as keyword
- [ ] Create `IppGenerator` object
- [ ] Serialize/resume execution state

### BUG-NEW-N7: Async/Await ⏳ TODO
- [ ] Implement async/await over generators
- [ ] Add event loop
- [ ] Handle `await expr` as `yield wait(expr)`

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

### Engine Bindings (FREE Options) ⏳ TODO
- [ ] Pygame integration (free, Python)
- [ ] Godot GDScript alternative (free, open source)
- [ ] Raylib binding (free, C library)
- [ ] SFML binding (free, C++ library)
- [ ] Love2D integration (free, Lua-based)

### Editor Integration ⏳ TODO
- [ ] VSCode extension (free)
- [ ] Vim/Neovim plugin (free)
- [ ] Emacs major mode (free)
- [ ] LSP server (free)

### Package Manager ⏳ TODO
- [ ] `ippkg` - Package manager (build with Python, free)
- [ ] Public package registry (GitHub Packages, free)
- [ ] `ippkg install <package>`
- [ ] `ippkg publish <package>`
- [ ] `ippkg search <query>`

```ipp
var body = RigidBody(mass = 1.0, position = vec2(0, 0))
body.apply_force(vec2(0, -9.8))     # gravity
body.update(delta_time)
```

---

## v2.0.0 - Game Features 📋 PLANNED

**Goal**: Full game development support

### Advanced Math ⏳ TODO
- [ ] Matrix operations (multiply, inverse, transpose)
- [ ] Quaternion math (multiply, slerp, axis-angle)
- [ ] Barycentric coordinates
- [ ] Bezier curves
- [ ] Perlin noise
- [ ] Simplex noise

### Physics ⏳ TODO
- [ ] Rigid body basics
- [ ] AABB collision response
- [ ] Sphere collision response
- [ ] Impulse resolution
- [ ] Joints (distance, spring, hinge)

### Particles ⏳ TODO
- [ ] Particle system
- [ ] Emitter types (point, line, rect, circle)
- [ ] Particle properties (lifetime, velocity, color, size)

### Scene Graph ⏳ TODO
- [ ] Entity class
- [ ] Transform (position, rotation, scale)
- [ ] Node hierarchy (parent/children)
- [ ] Camera system
- [ ] Layer system

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

### Phase 1: Production Ready (v1.3.0)
1. **VM Test Suite** - Write comprehensive VM tests
2. **Memory Safety** - Add bounds checking, overflow protection
3. **Bytecode Serialization** - Compile to .ipbc files
4. **CLI Flags** - --vm, --no-color, etc.

### Phase 2: Critical Bugs Fixed (v1.3.1) ✅ DONE
1. **BUG-NEW-C1** - VM for loop fixed ✅
2. **BUG-NEW-C2** - Runtime error line numbers fixed ✅
3. **BUG-NEW-C3** - Operator overloading fixed ✅

### Phase 3: Documentation (v1.3.2)
1. **Language Tutorial** - Getting started guide
2. **API Reference** - Auto-generate from docstrings
3. **Examples Repository** - github.com/ipp-lang/examples
4. **Website** - MkDocs + GitHub Pages (FREE)

### Phase 3: Standard Library (v1.3.2+) ✅ DONE (Set type)
- [x] `Set` type - Unordered unique elements (BUG-NEW-M6) ✅
- [ ] Missing Builtins - File I/O, regex, networking
- [ ] Collection Types - Deque, priority queue, tree, graph
- [ ] Data Formats - JSON, XML, YAML, TOML parsers

### Notable Bug Fixes (Standard Library)
- [ ] BUG-NEW-N1: **No access control enforcement** (`__field` name mangling)
- [ ] BUG-NEW-N2: **No Ipp-level recursion limit** (add `max_depth` config)
- [ ] BUG-NEW-N5: **Runtime errors lack column info** (add column tracking)
- [ ] BUG-NEW-N8: **IppList/native list inconsistency** (wrap all list returns)

### Phase 4: Game SDK (v1.3.3)
1. **Math Library** - vec2, vec3, mat4, quat
2. **Collision** - AABB, circle, raycast
3. **Easing** - Animation curves
4. **Particles** - Basic particle system

### Phase 5: Ecosystem (v1.4.0)
1. **Package Manager** - ippkg with GitHub Packages
2. **Editor Extensions** - VS Code, Neovim LSP
3. **Engine Bindings** - Raylib, Pygame, Godot
4. **CI/CD Pipeline** - GitHub Actions automated tests

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

*Last Updated: 2026-03-29 (v1.3.2 DONE - VM upvalues fixed, Set type added! Roadmap cleaned up and merged.)*
