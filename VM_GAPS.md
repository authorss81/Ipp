# VM vs Interpreter — Gap Analysis

## Summary

The VM (bytecode compiler + runtime) handles **all 180 tests** without crashes. Builtins are shared (same `BUILTINS` dict in `ipp/runtime/builtins.py`). The two largest gaps are:

1. **`MatchExpr`** — match used as an expression returns `None` in the VM (compiler misses it, interpreter handles it)
2. **`__radd__`** — reverse addition (`10 + obj`) works in the interpreter but fails in the VM

Beyond these gaps, there are **6 areas where the VM is actually ahead** of the interpreter (compound assignment overloading, `__contains__`, `__bool__`, dict `.get()`, etc.), and **~15 operator overloading dunders** missing in both runtimes (non-blocking for interpreter removal since they affect both equally).

---

## Confirmed Gap

### 1. `MatchExpr` — match as an expression (not statement)

| Area | Status |
|------|--------|
| **Parser** | Produces `MatchExpr` when match appears in expression context (`var x = match y { ... }`) at `parser.py:624-642` |
| **Interpreter** | Handled by `visit_match_expr` at `interpreter.py:1875` |
| **VM Compiler** | **Not handled** — `compile_expr` (`compiler.py:1803`) has no `isinstance(node, MatchExpr)` branch. Falls through, emits no bytecode, leaves `None` on stack |
| **VM Runtime** | `MatchStmt` (statement form) is fully handled via `compile_match` at `compiler.py:1295` with `MATCH` opcode |
| **Tests** | Tests at `v1_5_16/test_vm_v1516.ipp:25` and `v1_5_15/test_syntax_v1515.ipp:39,49` use match-as-expression but only `print()` the result — they pass despite producing `None` instead of the matched value because `run_tests.py` only checks for exceptions |

**Impact**: Any `match` used as an expression returns `None`. Statement-form match (`match x { ... }` without assignment) works correctly.

---

### 2. `__truediv__` vs `__div__` — operator overloading name mismatch **[FIXED]**

| Area | Status |
|------|--------|
| **Interpreter** | Checks `__truediv__` for `/` at `interpreter.py:689-690` |
| **VM** | Was `__div__` at `vm.py:2899-2900` |
| **Fix** | Changed to `__truediv__` in commit (session 2026-06-29) |
| **Tests** | No test for `/` operator overloading exists, so the discrepancy went undetected |

**Impact**: **[RESOLVED]** Now both runtimes check `__truediv__` for division. Class defining `__div__` (Python 2 name) will fail in both — use `__truediv__` instead.

---

### 3. `__radd__` — reverse/right-side addition overloading

| Area | Status |
|------|--------|
| **Interpreter** | Checks `__radd__` on `right` when `left` is not an IppInstance at `interpreter.py:668-675` |
| **VM** | **Not handled** — `ADD` opcode handler at `vm.py:2855-2868` only checks `__add__` on `a` (left operand), never checks `__radd__` on `b` (right operand) |
| **Tests** | No test exercises reverse add on IppInstance |

**Impact**: `10 + obj` (native type + IppInstance) works in the interpreter but raises `VMError` in the VM. The VM is missing right-side operator overloading entirely.

---

### 4. Reverse/subscript operator overloading (`__rsub__`, `__rmul__`, `__rtruediv__`, etc.)

**Impact**: **Missing in both**. Neither the interpreter nor the VM checks any reverse dunder methods (`__rsub__`, `__rmul__`, `__rtruediv__`, `__rmod__`, `__rpow__`, `__rfloordiv__`, `__rlshift__`, `__rrshift__`, `__rand__`, `__ror__`, `__rxor__`). Expressions like `10 - obj`, `3 * obj`, `10 / obj` fail in both.

---

### 5. In-place operator overloading (`__iadd__`, `__isub__`, etc.)

**Impact**: **Missing in both**. Neither runtime checks `__iadd__`, `__isub__`, `__imul__`, `__itruediv__` for compound assignment `+=`, `-=`, `*=`, `/=`. The VM's compound assignment works for IppInstance because it desugars to `a = a + b` which dispatches through `__add__` — but this creates a new object rather than modifying in place.

---

### 6. Structured features broken in both

| Feature | Status |
|---------|--------|
| **Generator `.send()` method** | Not implemented in either — `next(g)` works, `g.send(val)` fails |
| **`del` statement** | Not supported in either (parser does not produce AST for it, or fails at runtime) |
| **`goto`/`label`** | Only supported inside `story {}` blocks, not as standalone statements |
| **Multi-assignment swap** (`a, b = b, a`) | Parser fails — `SyntaxError` at comma |
| **Compound assignment `**=**, `//=`, `<<=`, `>>=`, `&=`, `|=`, `^=`** | Parser fails — these compound operators are not recognized |

---

## Where VM Is Ahead of Interpreter

These features work in the VM but are **broken in the interpreter** — important to note for consistency but not a blocker for interpreter removal (the VM is better here):

| Feature | Interpreter | VM | Why |
|---------|-------------|----|-----|
| **Compound assignment with operator overloading** (`a += b` where `a` is IppInstance with `__add__`) | Fails: raw `+` on IppInstance raises `TypeError` | Works: compiles as `a = a + b`, dispatches through `ADD` which checks `__add__` | Interpreter's `visit_compound_assign_expr` does not delegate through `visit_binary_expr` — does raw operation |
| **`__contains__` for `in` operator on IppInstance** | Fails: `TypeError: argument of type 'IppInstance' is not iterable` | Works: `CONTAINS` fallback uses `try: item in collection` which calls Python's `__contains__` on IppInstance (via `__getattr__` delegation) | Interpreter only checks `_items`, `_data`, and standard types — misses IppInstance delegation |
| **`__bool__` for truthiness** | Fails: falls through to `len()` which is not defined on IppInstance | Works: `_is_truthy` method checks `__bool__` on IppInstance before falling back to `len()` | VM has a more complete `_is_truthy` check |
| **Dict `.get()` method with default** | Fails: missing method `get` on dict | Works: Python dict natives accessed via `hasattr` | VM's method resolution catches native Python methods; interpreter's property access fails |
| **F-strings with complex expressions** | Works for simple cases | Works for all cases including method calls | Both handle this, VM has more robust `str()` coercion |
| **Template strings** | Limited support | Full support | Compiler handles `TemplateStringExpr`; interpreter visitor for `visit_template_string_expr` may have edge cases |

## Features in Compiler but NOT in Interpreter

The compiler also **exceeds** the interpreter in these areas — not gaps for removal, but additional evidence the VM is ahead:

- **`ExportDecl`** — `export` declarations (handled by `compile_export` in compiler, no interpreter equivalent)
- **`LambdaExpr`** — Lambda/anonymous functions (`compiler.py:1930-1947`, no interpreter visitor)
- **`ListDestructDecl`** — List destructuring declaration (no interpreter visitor)
- **`DictDestructDecl`** — Dict destructuring declaration (no interpreter visitor)
- **`EntityDecl` / `SystemDecl`** — ECS declarations (compiler-only, scene graph builtins)
- **`PropDecl`** — Handled inline in `compile_class` at `compiler.py:588`
- **Properties with getter/setter** — compiled properly via `PROP_DEFINE` opcode

---

## Missing Operator Overloading in Both Runtimes

These dunder methods are **not checked by either runtime**. Features that exist in the language (the operators work for native types) but are not extensible through Ipp class operator overloading:

### Binary operators

| Operator | Dunder | Has `__add__`-style check in Interpreter? | Has `__add__`-style check in VM? |
|----------|--------|------------------------------------------|----------------------------------|
| `**` | `__pow__` | No (line 717: `left ** right` direct) | No (line 2914: `a ** b` direct) |
| `%` | `__mod__` | No (line 719: `left % right`) | No (line 2912: `a % b`) |
| `//` | `__floordiv__` | No (line 721: `int(left) // int(right)`) | No (line 2921: `int(a) // int(b)`) |
| `<<` | `__lshift__` | No (line 723: `int(left) << int(right)`) | No (line 2938: `int(a) << int(b)`) |
| `>>` | `__rshift__` | No (line 725: `int(left) >> int(right)`) | No (line 2941: `int(a) >> int(b)`) |
| `&` | `__and__` | No (line 727: `int(left) & int(right)`) | No (line 2926: `int(a) & int(b)`) |
| `\|` | `__or__` | No (line 729: `int(left) \| int(right)`) | No (line 2929: `int(a) \| int(b)`) |
| `^` | `__xor__` | No (line 731: `int(left) ^ int(right)`) | No (line 2932: `int(a) ^ int(b)`) |
| `..` | `__range__` | No (line 737: `IppRange(...)`) | No (line 2848: `IppRange(...)`) |

### Unary operators

| Operator | Dunder | Interpreter | VM |
|----------|--------|-------------|----|
| `-` (negate) | `__neg__` | No (line 773: `-right`) | No (line 2945: `-a`) |
| `~` (invert) | `__invert__` | No (line 777: `~int(right)`) | No (line 2935: `~int(a)`) |

### Logical operators via operator overloading

Short-circuit `&&`, `||` work through truthiness — no `__and__`/`__or__` dunder (standard Ipp behavior, same as Python).

### Right-side operator overloading

| Dunder | Interpreter | VM |
|--------|-------------|-----|
| `__radd__` | **Yes** (line 668-675: checks when `+` fails) | No |
| `__rsub__`, `__rmul__`, `__rtruediv__`, `__rmod__`, `__rpow__`, `__rfloordiv__`, `__rlshift__`, `__rrshift__`, `__rand__`, `__ror__`, `__rxor__` | No | No |
| `__rshift__`, `__rlshift__` (reverse bit shift) | No | No |
| `__rand__`, `__ror__`, `__rxor__` (reverse bitwise) | No | No |

### In-place operator overloading

| Dunder | Interpreter | VM |
|--------|-------------|-----|
| `__iadd__`, `__isub__`, `__imul__`, `__itruediv__` | No | No |

Note: The VM's compound assignment (`a += b`) compiles as `a = a + b` which dispatches through the regular binary operator `ADD` handler (checking `__add__`). In-place dunders like `__iadd__` are not checked — the VM always creates a new object rather than mutating in place.

---

## Other Missing Features (Both Runtimes)

| Feature | Expected Syntax | Status |
|---------|----------------|--------|
| **Generator `.send()`** | `gen.send(val)` | Not implemented — `next(gen)` and `for-in` work |
| **`del` statement** | `del x['key']` or `del x.prop` | Not implemented at parser level |
| **`goto`/`label`** | `label start; goto start` | Only inside `story {}` blocks |
| **Multi-assignment swap** | `a, b = b, a` | Parser fails on comma syntax |
| **Compound `**=`** | `x **= 2` | Parser fails |
| **Compound `//=`** | `x //= 2` | Parser fails |
| **Compound `<<=` / `>>=`** | `x <<= 2` | Parser fails |
| **Compound `&=` / `|=` / `^=`** | `x &= 2` | Parser fails |
| **Custom iterable via `__iter__`/`__next__`** | `for x in obj` where obj is IppInstance | Not supported |

---

## Verified: No Other Gaps

All 70+ remaining interpreter `visit_*` methods have equivalent compiler handling:

| Category | Covered |
|----------|---------|
| **Literals** | Number, String, Boolean, Nil, List, Dict, Tuple, FString, TemplateString |
| **Expressions** | Binary, Unary, Call, Index, IndexSet, Get, Set, CompoundAssign, CompoundSet, IndexCompoundSet, Is, Slice, Conditional, NullishCoalescing, OptionalChain, Spread, Unpack, Super, Self, Yield, Await |
| **Statements** | If, For, While, DoWhile, Try, Catch, Throw, With, Return, Break, Continue, Assert, ExprStmt |
| **Declarations** | Var, Let, MultiVar, Function, AsyncFunc, Class, Enum, Import, Global, Nonlocal |
| **Comprehensions** | List, Dict, Set |
| **Story/Scene** | Sequence, Story, Npc, Choice, Flag, Goto, Scene, Label, Parallel, GameLoop |

---

## Builtins

Builtins are **identical** between interpreter and VM — both load from `ipp/runtime/builtins.py:BUILTINS`. The VM additionally has a `missing_builtins` fallback list at `vm.py:951` that dynamically adds builtins found via `Closure.__call__`.

---

## REPL Compatibility

The REPL's `VMInterpreter` wrapper (`main.py:1063-1096`) provides `run(ast)` and `global_env` — the only two interfaces the REPL needs. All attribute accesses (`call_depth`, `_loaded_modules`, etc.) are `hasattr`-guarded. No REPL functionality would break by removing the interpreter.

---

## Action Required for Interpreter Removal

### Must-fix (VM produces wrong output)

1. **Fix `compile_expr` to handle `MatchExpr`** — wrap `compile_match` logic to push the matched value instead of discarding it (currently `compile_match` ends with `POP` + jump patching; expression form needs the value to survive on stack).

### Nice-to-fix (VM fails, interpreter works)

2. **Add `__radd__` check to VM's ADD handler** — check `__radd__` on `b` (right operand) when `a` fails to resolve via `__add__`. Pattern: `if isinstance(b, IppInstance) and hasattr(b, '__radd__'): ...`.

### Trivial

3. Default `InterpreterManager.use_vm` to `True`.
4. Optionally delete `ipp/interpreter/` directory.

### When to fix the "missing in both" features

The operator overloading gaps (`__pow__`, `__mod__`, `__floordiv__`, etc.) affect both runtimes equally — they are not blockers for interpreter removal. Fix these as feature work when needed (e.g., when a user defines a class that needs `**` overloading).
