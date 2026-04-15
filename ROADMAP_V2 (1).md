# Ipp Language — Micro-Versioned Roadmap v7
> **Last Updated: 2026-04-12** | Based on Audit v2 — 27 confirmed bugs
> **Philosophy:** One or two problems per version. Every version ships with a passing test.
> **Rule:** A fix is ✅ DONE when (a) code is changed, (b) a test file passes in VM mode, (c) nothing else breaks.

---

## How to Read This Roadmap

Each version entry contains:
- **What breaks** — the exact user-facing symptom
- **Root cause** — exact file, line, and mechanism
- **Exact fix** — the minimal code change required
- **Test that proves it** — runnable `.ipp` code that must pass
- **Risk** — what else could break

Versions follow `MAJOR.MINOR.PATCH.HOTFIX`. Micro-fixes increment the 4th digit. Each digit resets when the one above increments.

---

## Phase A — Emergency Fixes (v1.5.21 – v1.5.28)
> Fix every bug a user encounters in the first 10 minutes.
> Constraint: No new features. Touch the minimum lines for each specific bug.

---

### v1.5.21 — Fix: For-In Loop Never Executes (DONE)

**Symptom:** `for i in [1,2,3] { print(i) }` produces no output. `for i in range(10) { s=s+i }` leaves `s=0`.

**Root cause:**
```
File: ipp/vm/compiler.py, compile_for(), lines 373–384

Emits operands in wrong order:
  GET len(list) → 3   (pushed first)
  GET idx      → 0   (pushed second)
  LESS         → 3 < 0 = FALSE → exit immediately

Correct order:
  GET idx      → 0   (pushed first)
  GET len(list) → 3  (pushed second)
  LESS         → 0 < 3 = TRUE → enter loop
```

**Exact fix:**
```python
# compiler.py lines 373–384 — swap push order:

# DELETE these lines:
self.compile_identifier("len")
self.chunk.write(OpCode.GET_LOCAL, self.current_line)
self.chunk.write(list_slot, self.current_line)
self.chunk.write(OpCode.CALL, self.current_line)
self.chunk.write(1, self.current_line)
self.chunk.write(OpCode.GET_LOCAL, self.current_line)
self.chunk.write(idx_slot, self.current_line)
self.chunk.write(OpCode.LESS, self.current_line)

# REPLACE WITH:
self.chunk.write(OpCode.GET_LOCAL, self.current_line)  # idx first
self.chunk.write(idx_slot, self.current_line)
self.compile_identifier("len")                         # then len(list)
self.chunk.write(OpCode.GET_LOCAL, self.current_line)
self.chunk.write(list_slot, self.current_line)
self.chunk.write(OpCode.CALL, self.current_line)
self.chunk.write(1, self.current_line)
self.chunk.write(OpCode.LESS, self.current_line)       # idx < len → correct
```

**Files changed:** `ipp/vm/compiler.py` (8 lines reordered, net 0 lines added)

**Test — `tests/vm/v1.5.21_for_loop.ipp`:**
```ipp
var result = []
for i in [10, 20, 30] {
    result.append(i)
}
assert len(result) == 3
assert result[0] == 10 and result[2] == 30

var s = 0
for i in range(10) { s = s + i }
assert s == 45

var words = ["a", "b", "c"]
var count = 0
for w in words { count = count + 1 }
assert count == 3
```

**Risk:** LOW. Only reorders two GET pushes in compile_for. While loops, if/else, classes are unaffected.

---

### v1.5.22 — Fix: `pi` and `e` Are Functions, Not Constants (DONE)

**Symptom:** `var area = pi * r * r` crashes: `VMError: unsupported operand type(s) for *: 'function' and 'int'`. Any formula using `pi` or `e` directly fails.

**Root cause:**
```
File: ipp/vm/vm.py, _init_builtins(), lines 382–383

'pi': lambda: math.pi,   ← returns lambda object, not 3.14159
'e':  lambda: math.e,    ← returns lambda object, not 2.71828
```

**Exact fix:**
```python
# vm.py lines 382–383:
'pi': math.pi,   # was: lambda: math.pi
'e':  math.e,    # was: lambda: math.e
```

**Files changed:** `ipp/vm/vm.py` (2 characters changed per line)

**Test — `tests/vm/v1.5.22_math_constants.ipp`:**
```ipp
assert abs(pi - 3.14159265) < 0.0001
assert abs(e  - 2.71828182) < 0.0001

var r = 5
var area = pi * r * r
assert abs(area - 78.5398) < 0.01

var growth = e ** 2
assert abs(growth - 7.389) < 0.01
```

**Risk:** NEGLIGIBLE. Any existing code calling `pi()` as a function was always wrong.

---

### v1.5.23 — Fix: `let` Immutability Is Never Enforced (DONE - function scope only)

**Symptom:** `let x = 5; x = 99; print(x)` prints `99`. The `let` keyword is purely cosmetic.

**Root cause:**
```
File: ipp/vm/compiler.py — Local.is_const stored (line 18) but unused at SET_LOCAL
File: ipp/vm/vm.py — SET_LOCAL (lines 803–809) overwrites without checking is_const

The is_const=True flag is set for LetDecl (compiler.py line 131),
stored in Local.is_const, but the VM's SET_LOCAL handler ignores it.
```

**Exact fix — 3 small changes:**

1. `ipp/vm/bytecode.py` — Add `const_locals` set to Chunk:
```python
class Chunk:
    def __init__(self):
        self.code = []
        self.constants = []
        self.lines = []
        self.const_locals: set = set()   # ADD: slot indices of const locals
```

2. `ipp/vm/compiler.py` — Record const slot after define_local for let:
```python
def compile_var_decl(self, node, is_const=False):
    ...
    if self.depth > 0:
        slot = self.define_local(node.name, is_const)
        if is_const:
            self.chunk.const_locals.add(slot)   # ADD
```

3. `ipp/vm/vm.py` — Enforce in SET_LOCAL:
```python
elif opcode == OpCode.SET_LOCAL:
    idx = code[ip + 1]
    slot = frame.stack_base + idx
    # ADD immutability check:
    if idx in frame.chunk.const_locals:
        if slot < len(self.stack) and self.stack[slot] is not None:
            raise VMError(f"Cannot reassign immutable 'let' variable at slot {idx}")
    if self.stack:
        while len(self.stack) <= slot:
            self.stack.append(None)
        self.stack[slot] = self.stack[-1]
```

**Files changed:** `ipp/vm/bytecode.py` (+1 field), `ipp/vm/compiler.py` (+2 lines), `ipp/vm/vm.py` (+4 lines)

**Test — `tests/vm/v1.5.23_let_immutable.ipp`:**
```ipp
let x = 42
assert x == 42

var caught = false
try {
    x = 99
} catch e {
    caught = true
}
assert caught == true
assert x == 42   # must not have changed

let name = "Alice"
assert name == "Alice"
```

**Risk:** MEDIUM. VMFrame must own the chunk reference (it already does via `frame.chunk`). Run all tests afterward — the new check fires at SET_LOCAL which is very hot.

---

### v1.5.24 — Fix: `__str__` Method Always Returns Nothing (DONE)

**Symptom:** Any class with `__str__()` raises `VMError: __str__ returned non-string (type IppInstance)`. `print()` on instances never shows custom formatting.

**Root cause:**
```
File: ipp/vm/vm.py, _call_ipp_method(), lines 228–248

vm = VM()                  ← fresh VM, self.chunk = None
vm.stack.append(instance)
frame = VMFrame(chunk, ...)
vm.frames.append(frame)
vm.run()                   ← BUG: no argument passed
                            → vm.run() checks: if not self.chunk: return None
                            → returns None immediately, body never executes

Also: lines ~251–265 are an exact duplicate of the function body after
the first return. They are dead, unreachable code.
```

**Exact fix:**
```python
# _call_ipp_method(), line ~240:
vm.run()      # BEFORE (broken)
vm.run(chunk) # AFTER (fixed — passes chunk so vm.run sets self.chunk)

# Same fix at line ~257 (second call site in the function).

# Also delete lines ~251–265: the duplicate dead-code block that
# begins with `vm = VM()` after the first `return result` statement.
```

**Files changed:** `ipp/vm/vm.py` (2 calls changed `run()` → `run(chunk)`, ~15 dead lines deleted)

**Test — `tests/vm/v1.5.24_str_method.ipp`:**
```ipp
class Point {
    func init(x, y) { self.x = x\nself.y = y }
    func __str__() {
        return "Point(" + str(self.x) + ", " + str(self.y) + ")"
    }
}
var p = Point(3, 4)
assert str(p) == "Point(3, 4)"

class Token {
    func init(kind, val) { self.kind = kind\nself.val = val }
    func __str__() { return self.kind + ":" + str(self.val) }
}
assert str(Token("NUM", 42)) == "NUM:42"
```

**Risk:** LOW-MEDIUM. The `vm.run(chunk)` change only affects the `_call_ipp_method` helper used for Python-side `str()` calls. Instance method calls dispatched through CALL opcode are unaffected.

---

### v1.5.25 — Fix: Static Methods Inaccessible on Class (DONE)

**Symptom:** `MyClass.static_method()` crashes: `VMError: Property 'square' not found on IppClass`.

**Root cause:**
```
File: ipp/vm/vm.py, GET_PROPERTY handler, lines 856–869

Handler checks isinstance(obj, IppInstance) but not isinstance(obj, IppClass).
Static methods are stored in IppClass.methods but GET_PROPERTY never
looks there when obj is an IppClass — falls through to the error raise.
```

**Exact fix:**
```python
# vm.py GET_PROPERTY handler — add IppClass branch after IppInstance:
elif opcode == OpCode.GET_PROPERTY:
    idx = code[ip + 1]
    name = constants[idx]
    obj = self.stack[-1]
    if isinstance(obj, IppInstance):
        self.stack[-1] = obj.get(name)
    elif isinstance(obj, IppClass):                  # ADD this branch
        method = obj.get_method(name)
        if method is not None:
            # Wrap as BoundMethod with instance=None for static dispatch
            self.stack[-1] = BoundMethod(None, method)
        else:
            raise VMError(f"Class '{obj.name}' has no static member '{name}'")
    elif isinstance(obj, dict) and name in obj:
        self.stack[-1] = obj[name]
    elif hasattr(obj, name):
        self.stack[-1] = getattr(obj, name)
    else:
        raise VMError(f"Property '{name}' not found on {type(obj).__name__}")
```

**Also fix `_call` to handle `BoundMethod` with `instance=None`:**
```python
# vm.py _call():
if isinstance(callee, BoundMethod):
    if callee.instance is None:
        # Static: call without injecting self
        if isinstance(callee.method, Closure):
            chunk = callee.method.chunk
            base = len(self.stack)
            for a in args:
                self.stack.append(a)
            new_frame = VMFrame(chunk, closure=callee.method, stack_base=base)
            self.frames.append(new_frame)
        else:
            self._call(callee.method, args, return_frame)
    else:
        self._call_method(callee.instance, callee.method, args, return_frame)
    return
```

**Files changed:** `ipp/vm/vm.py` (~20 lines in GET_PROPERTY + ~10 lines in _call)

**Test — `tests/vm/v1.5.25_static_methods.ipp`:**
```ipp
class MathHelper {
    static func square(x) { return x * x }
    static func abs(x) { if x < 0 { return -x } return x }
}
assert MathHelper.square(5) == 25
assert MathHelper.abs(-7) == 7

class Counter {
    static func create() { return Counter() }
    func init() { self.n = 0 }
    func inc() { self.n = self.n + 1 }
}
var c = Counter.create()
c.inc()
c.inc()
assert c.n == 2
```

**Risk:** MEDIUM. Changes GET_PROPERTY dispatch order — verify all instance property access still works.

---

### v1.5.26 — Fix: `continue` in While Loop Acts as `break` ✅ DONE (v1.5.26)

**Symptom:** `while i<5 { i=i+1; if i==3 { continue }; r=r+i }` gives `r=3` instead of `r=12`. `continue` exits the loop entirely.

**Root cause:**
```
File: ipp/vm/compiler.py, compile_continue(), lines 541–547

compile_continue emits JUMP and appends its address to continue_jumps.
compile_while then patches those jumps with patch_jump(cont) at loop END.
patch_jump() resolves to the current code length = position AFTER the loop.
Result: continue jumps OUT of the loop = same as break.
```

**Fix:** v1.5.26 - emit LOOP backward-jump directly at continue site

**Exact fix:**
```python
# compiler.py — compile_continue():
def compile_continue(self, node: ContinueStmt = None):
    if not self.loop_stack:
        self.error("'continue' outside of loop")
    loop_info = self.loop_stack[-1]
    target = loop_info.get('continue_target')
    if target is not None:
        # Target already known (e.g., while loop has it at loop_start)
        self.chunk.emit_loop(target, self.current_line)
    else:
        # Target not yet known (for-in: idx++ section set after body)
        # Emit a placeholder JUMP and record it for back-patching
        jump = self.chunk.emit_jump(OpCode.JUMP, self.current_line)
        loop_info['continue_jumps'].append(jump)

# compiler.py — compile_while():
# After the loop body and before emit_loop, patch any deferred continue jumps:
# (while loops have continue_target = loop_start, set in loop_stack append)
# No patch needed since compile_continue emits LOOP directly.
# Remove the existing: for cont in loop_info['continue_jumps']: patch_jump(cont)
```

**Files changed:** `ipp/vm/compiler.py` (~15 lines in compile_continue + cleanup in compile_while)

**Test — `tests/vm/v1.5.26_continue_while.ipp`:**
```ipp
var r = 0
var i = 0
while i < 5 {
    i = i + 1
    if i == 3 { continue }
    r = r + i
}
assert r == 12   # 1+2+4+5, skipping 3

# Ensure loop completes to end (not early exit)
var iters = 0
var j = 0
while j < 10 {
    j = j + 1
    if j % 2 == 0 { continue }
    iters = iters + 1
}
assert iters == 5   # only odd iterations counted: 1,3,5,7,9
assert j == 10      # loop ran to completion
```

**Risk:** MEDIUM. Changes continue behavior globally. Test break separately to confirm it still exits properly.

---

### v1.5.27 — Fix: `continue` in For-In Loop — Back-Patch Deferred Jumps ✅ DONE (v1.5.27)

**Symptom:** After v1.5.26, `continue` inside for-in loops may still jump incorrectly because the `continue_target` (the idx++ section) is set AFTER the body is compiled — so `compile_continue` can't emit LOOP immediately.

**Root cause:**
```
File: ipp/vm/compiler.py, compile_for()

continue_target = len(self.chunk.code)   ← set AFTER body compilation
self.loop_stack[-1]['continue_target'] = continue_target

But compile_continue, called DURING body compilation, sees continue_target=None
and falls into the deferred jump path. The jump address is then in continue_jumps,
but needs to be rewritten as a LOOP opcode pointing to the idx++ section.
```

**Exact fix:**
```python
# compiler.py — compile_for(), after setting continue_target:
continue_target = len(self.chunk.code)
self.loop_stack[-1]['continue_target'] = continue_target

# Back-patch any deferred continue jumps to be LOOP backward jumps:
for jump_addr in loop_info.get('continue_jumps', []):
    # The JUMP opcode is at jump_addr (3-byte forward jump)
    # Replace it with LOOP + backward offset to continue_target
    after_instr = jump_addr + 4   # JUMP is 4 bytes (opcode + 3 operand)
    offset = after_instr - continue_target
    self.chunk.code[jump_addr]     = int(OpCode.LOOP)
    self.chunk.code[jump_addr + 1] = offset & 0xFF
    self.chunk.code[jump_addr + 2] = (offset >> 8) & 0xFF
    self.chunk.code[jump_addr + 3] = (offset >> 16) & 0xFF
```

**Files changed:** `ipp/vm/compiler.py` (~10 lines in compile_for)

**Test — `tests/vm/v1.5.27_continue_for.ipp`:**
```ipp
var evens = []
for i in range(10) {
    if i % 2 != 0 { continue }
    evens.append(i)
}
assert len(evens) == 5
assert evens[0] == 0 and evens[4] == 8

var visited = []
for x in [1, 2, 3, 4, 5] {
    if x == 3 { continue }
    visited.append(x)
}
assert visited == [1, 2, 4, 5]
assert len(visited) == 4
```

**Risk:** MEDIUM. In-place bytecode rewriting. Verify LOOP offset calculation doesn't overflow 3 bytes for large functions.

---

### v1.5.28 — Fix: `MultiVarDecl` Not Handled in VM Compiler

**Symptom:** `var a, b = [10, 20]` — variables `a` and `b` are never defined; accessing them raises `VMError: Undefined variable`.

**Root cause:**
```
File: ipp/vm/compiler.py, compile_stmt(), lines 127–165

Parser generates MultiVarDecl(['a','b'], expr).
compile_stmt has no isinstance(node, MultiVarDecl) case.
Node is silently dropped — nothing is emitted.
```

**Exact fix:**
```python
# compiler.py — add to imports:
from ..parser.ast import ..., MultiVarDecl   # ensure imported

# compile_stmt() — add case (after LetDecl, before FunctionDecl):
elif isinstance(node, MultiVarDecl):
    self.compile_multi_var_decl(node)

# New method:
def compile_multi_var_decl(self, node: MultiVarDecl):
    """var a, b, c = [1, 2, 3]  — destructure list into named vars"""
    self.compile_expr(node.initializer)        # evaluate once → stack
    source_slot = self.define_local("__destructure__")

    for i, name in enumerate(node.names):
        # index source[i]
        self.chunk.write(OpCode.GET_LOCAL, self.current_line)
        self.chunk.write(source_slot, self.current_line)
        idx_const = len(self.chunk.constants)
        self.chunk.constants.append(i)
        self.chunk.write(OpCode.CONSTANT, self.current_line)
        self.chunk.write(idx_const, self.current_line)
        self.chunk.write(OpCode.GET_INDEX, self.current_line)
        # GET_INDEX returns None for out-of-bounds → perfect default

        if self.depth > 0:
            self.define_local(name)
        else:
            self.chunk.write(OpCode.DEFINE_GLOBAL, self.current_line)
            cidx = len(self.chunk.constants)
            self.chunk.constants.append(name)
            self.chunk.write(cidx, self.current_line)
            self.chunk.lines.append(self.current_line)
```

**Files changed:** `ipp/vm/compiler.py` (~30 lines added)

**Test — `tests/vm/v1.5.28_multi_var.ipp`:**
```ipp
var a, b = [10, 20]
assert a == 10 and b == 20

var x, y, z = [1, 2, 3]
assert x == 1 and y == 2 and z == 3

# Fewer values: extras get nil
var p, q, r = [99, 88]
assert p == 99 and q == 88 and r == nil
```

**Risk:** LOW. New code path only — no existing compilation changed.

---

## Phase B — Stub Implementations (v1.5.29 – v1.5.38)
> Replace empty stubs with real implementations. Fix infrastructure bugs.

---

### v1.5.29 — Fix: List Comprehension Is an Empty Stub ⏳ NOT DONE (VM)

**Symptom:** `[x*x for x in range(5)]` returns `[0,1,2,3,4]` (range itself) instead of `[0,1,4,9,16]`.

**Root cause:**
```
File: ipp/vm/compiler.py, compile_list_comprehension(), lines 904–916

def compile_list_comprehension(self, node):
    emit LIST 0                 ← empty list
    compile_expr(node.iterator) ← result lands on stack, becomes "output"
    # "For now defer to interpreter path" ← explicit comment
    # Nothing else. No loop, no element expr, no append.
```

**Exact fix:** Full loop implementation in VM (see Audit v2, Section 9, Tier 1 item #9 for full code pattern). Requires: empty result list local, iterator local, index local, loop var local, bounds check (using fixed order from v1.5.21), GET_INDEX, element expression, append call, idx++, LOOP backward, patch exit, return result.

**Key detail:** `append(list, element)` must be callable as a 2-argument global. Verify `append` is in VM builtins; if not, add: `'append': lambda lst, item: lst.append(item)`.

**Files changed:** `ipp/vm/compiler.py` (~65 lines replacing 10-line stub)

**Test — `tests/vm/v1.5.29_list_comp.ipp`:**
```ipp
var squares = [x * x for x in range(5)]
assert squares == [0, 1, 4, 9, 16]

var doubled = [x * 2 for x in [1, 2, 3]]
assert doubled == [2, 4, 6]

var evens = [x for x in range(10) if x % 2 == 0]
assert evens == [0, 2, 4, 6, 8]

var nested = [i * j for i in range(3) if i > 0 for j in range(1, 3)]
# i=1: j=1→1, j=2→2   i=2: j=1→2, j=2→4
assert nested == [1, 2, 2, 4]
```

---

### v1.5.30 — Fix: Dict Comprehension Is an Empty Stub

**Symptom:** `{k: k*2 for k in range(4)}` returns `{}`.

**Root cause:** `compile_dict_comprehension` emits `DICT 0` and exits.

**Exact fix:** Same loop structure as v1.5.29 but builds a dict: evaluate key expr → store, evaluate value expr → store, then `dict[key] = value` via SET_INDEX (pop obj, idx, value from stack in right order).

**Files changed:** `ipp/vm/compiler.py` (~50 lines replacing 3-line stub)

**Test — `tests/vm/v1.5.30_dict_comp.ipp`:**
```ipp
var doubled = {k: k * 2 for k in range(5)}
assert doubled[0] == 0 and doubled[3] == 6

var filtered = {k: k for k in range(10) if k % 2 == 0}
assert len(filtered) == 5 and filtered[6] == 6
```

---

### v1.5.31 — Fix: Global Cache Uses `hash()` — Hash Collision Risk

**Symptom:** Two variables whose names produce the same Python hash silently return each other's values. Nondeterministic; depends on variable names.

**Root cause:**
```
File: ipp/vm/vm.py, lines 763, 779, 786, 792
cache_key = hash(name)   ← Python hash is not collision-free for strings
```

**Exact fix:** Change all 4 occurrences from `hash(name)` to `name`:
```python
# Line 763: cached = self._global_cache.get(name)
# Line 779: self._global_cache.set(name, val)
# Line 786: self._global_cache.set(name, val)
# Line 792: self._global_cache.cache.pop(name, None)
# Also update InlineCache type hint: Dict[str, Any] (was Dict[int, Any])
```

**Files changed:** `ipp/vm/vm.py` (4 lines + 1 type hint)

**Test — `tests/vm/v1.5.31_cache.ipp`:**
```ipp
var alpha = 1; var beta = 2; var gamma = 3
alpha = 100
assert alpha == 100 and beta == 2 and gamma == 3
beta = 200
assert alpha == 100 and beta == 200 and gamma == 3
```

---

### v1.5.32 — Fix: `SET_INDEX` Pushes Value Back to Stack

**Symptom:** `arr[i] = val` in expression context causes stack imbalance. Compound assignments like `lst[0] = lst[1] = 5` miscount stack depth.

**Root cause:**
```
File: ipp/vm/vm.py, SET_INDEX handler, line 921
self.stack.append(value)   ← assignment is a statement, not an expression
```

**Exact fix:** Remove the `self.stack.append(value)` line. Add proper bounds checking:
```python
elif opcode == OpCode.SET_INDEX:
    value = self.stack.pop()
    idx   = self.stack.pop()
    obj   = self.stack.pop()
    if isinstance(obj, list):
        i = int(idx)
        if -len(obj) <= i < len(obj):
            obj[i] = value
        else:
            raise VMError(f"Index {i} out of range (length {len(obj)})")
    elif isinstance(obj, dict): obj[idx] = value
    elif hasattr(obj, 'elements'): obj.elements[int(idx)] = value
    elif hasattr(obj, 'data'):     obj.data[idx] = value
    # No push — assignment is a statement
```

**Files changed:** `ipp/vm/vm.py` (~12 lines)

**Test — `tests/vm/v1.5.32_set_index.ipp`:**
```ipp
var lst = [1, 2, 3]
lst[0] = 10; lst[-1] = 99
assert lst[0] == 10 and lst[2] == 99

var d = {"x": 0}
d["x"] = 42; d["y"] = 7
assert d["x"] == 42 and d["y"] == 7
```

---

### v1.5.33 — Fix: `do-while` — Add `do { } while` Syntax

**Symptom:** `do { i=i+1 } while i < 5` crashes: `SyntaxError: Expect ':' or 'for' in dict literal`.

**Root cause:**
```
File: ipp/lexer/token.py — "do" not in KEYWORDS dict
File: ipp/parser/parser.py — no DO match in statement()

Note: The existing syntax is "repeat { } until condition" (Lua-style).
This version adds C-style "do { } while condition" as the primary syntax.
"repeat/until" remains as an alias.
```

**Exact fix:**
```python
# token.py — after REPEAT:
DO = auto()              # ADD TokenType.DO

# token.py KEYWORDS dict:
"do": TokenType.DO,      # ADD

# parser.py — statement() — add DO branch:
if self.match(TokenType.DO):
    return self.do_while_statement_c()

# parser.py — new method:
def do_while_statement_c(self):
    """do { body } while condition"""
    self.consume(TokenType.LEFT_BRACE, "Expect '{' after 'do'")
    body = self.block()
    self.consume(TokenType.WHILE, "Expect 'while' after do-body")
    condition = self.expression()
    return DoWhileStmt(body, condition)   # reuses existing AST node + compiler
```

**Files changed:** `ipp/lexer/token.py` (2 lines), `ipp/parser/parser.py` (~10 lines)

**Test — `tests/vm/v1.5.33_do_while.ipp`:**
```ipp
var i = 0
do { i = i + 1 } while i < 5
assert i == 5

var ran = false
do { ran = true } while false
assert ran == true   # must run at least once even when condition is false

var sum = 0
var n = 1
do {
    sum = sum + n
    n = n + 1
} while n <= 10
assert sum == 55
```

---

### v1.5.34 — Fix: Multiple Catch Blocks Not Supported

**Symptom:** `try { } catch A e { } catch B e { }` crashes: `SyntaxError: Unexpected token: Token(CATCH, ...)`.

**Root cause:**
```
File: ipp/parser/parser.py, try_statement(), lines 317–329
Only matches ONE catch then returns. No loop for additional catches.
```

**Exact fix:**
```python
# parser.py — try_statement():
def try_statement(self):
    try_body  = self.block_or_statement()
    catches   = []
    while self.match(TokenType.CATCH):
        catch_var = self.advance().lexeme if self.check(TokenType.IDENTIFIER) else None
        catch_body = self.block_or_statement()
        catches.append((catch_var, catch_body))
    finally_body = []
    if self.match(TokenType.FINALLY):
        finally_body = self.block_or_statement()
    return TryStmt(try_body, catches, finally_body)   # update TryStmt to hold list

# Also update TryStmt in ast.py: catches: List[Tuple[str, List]]
# Update compile_try in compiler.py to iterate catches
```

**Files changed:** `ipp/parser/ast.py` (TryStmt fields), `ipp/parser/parser.py` (~15 lines), `ipp/vm/compiler.py` compile_try (~20 lines)

**Test — `tests/vm/v1.5.34_multi_catch.ipp`:**
```ipp
var log = []
try {
    throw "error one"
} catch e {
    log.append("caught: " + e)
} catch e2 {
    log.append("second catch")   # should not run
}
assert len(log) == 1
assert log[0] == "caught: error one"

# Nested try
try {
    try { throw "inner" } catch e { throw "rethrown" }
} catch e {
    assert e == "rethrown"
}
```

---

### v1.5.35 — Fix: Variadic Parameters (`...args`) Not Supported

**Symptom:** `func log(...args) { }` crashes: `SyntaxError: Expect parameter name`.

**Root cause:**
```
File: ipp/parser/parser.py, function_declaration() parameter loop
TRIPLE_DOT token not handled — parser errors immediately.
```

**Exact fix:**
```python
# parser.py — function parameter parsing loop:
while True:
    is_variadic = self.match(TokenType.TRIPLE_DOT)   # ADD
    p = self.consume(TokenType.IDENTIFIER, "Expect parameter name").lexeme
    parameters.append("..." + p if is_variadic else p)  # mark variadic
    if is_variadic:
        break   # variadic must be last
    ...

# compiler.py — compile_function():
# Detect variadic param (name starts with "..."):
variadic_name = None
clean_params = []
for p in node.parameters:
    if p.startswith("..."):
        variadic_name = p[3:]
        clean_params.append(variadic_name)
    else:
        clean_params.append(p)

# vm.py — _call():
# When calling a function with a variadic final param,
# collect excess args into a list for the last slot.
# Detect: if func's last param slot corresponds to variadic,
# pack remaining args into a list before pushing.
```

**Files changed:** `ipp/parser/parser.py` (~10 lines), `ipp/vm/compiler.py` (~15 lines), `ipp/vm/vm.py` (~20 lines in _call)

**Test — `tests/vm/v1.5.35_variadic.ipp`:**
```ipp
func sum_all(...nums) {
    var total = 0
    for n in nums { total = total + n }
    return total
}
assert sum_all(1, 2, 3) == 6
assert sum_all(10) == 10
assert sum_all() == 0

func head_tail(first, ...rest) {
    return [first, rest]
}
var r = head_tail(1, 2, 3, 4)
assert r[0] == 1 and r[1] == [2, 3, 4]
```

---

### v1.5.36 — Fix: F-Strings Crash the Parser

**Symptom:** `f"Hello {name}!"` crashes: `SyntaxError: Unexpected token: Token(FSTRING, ...)`.

**Root cause:**
```
File: ipp/parser/parser.py — FSTRING token not in any expression rule
File: ipp/vm/compiler.py — no FStringExpr AST node or compile method
```

**Exact fix — 3 files:**

1. `ipp/parser/ast.py` — Add `FStringExpr`:
```python
@dataclass
class FStringExpr(ASTNode):
    segments: List[ASTNode]   # alternating StringLiteral and expression nodes
    def accept(self, visitor): return visitor.visit_fstring_expr(self)
```

2. `ipp/parser/parser.py` — Add FSTRING rule in `primary()`:
```python
if self.match(TokenType.FSTRING):
    return self._parse_fstring(self.previous().literal)

def _parse_fstring(self, raw: str) -> FStringExpr:
    # Parse "Hello {name}, you have {count} messages" into segments
    segments, i, buf = [], 0, []
    while i < len(raw):
        if raw[i] == '{' and i+1 < len(raw) and raw[i+1] != '{':
            if buf: segments.append(StringLiteral(''.join(buf))); buf = []
            j, depth = i+1, 1
            while j < len(raw) and depth:
                if raw[j] == '{': depth += 1
                elif raw[j] == '}': depth -= 1
                j += 1
            from ..lexer.lexer import tokenize as lex
            inner = Parser(lex(raw[i+1:j-1])).expression()
            segments.append(inner); i = j
        elif raw[i:i+2] in ('{{', '}}'):
            buf.append(raw[i]); i += 2
        else:
            buf.append(raw[i]); i += 1
    if buf: segments.append(StringLiteral(''.join(buf)))
    return FStringExpr(segments)
```

3. `ipp/vm/compiler.py` — Add FStringExpr compile:
```python
elif isinstance(node, FStringExpr):
    # Convert each segment to string, then concatenate
    for seg in node.segments:
        self.compile_expr(seg)
        self.compile_identifier("str")
        self.chunk.write(OpCode.SWAP, self.current_line)
        self.chunk.write(OpCode.CALL, self.current_line)
        self.chunk.write(1, self.current_line)
    self.chunk.write(OpCode.CONCAT_COUNT, self.current_line)
    self.chunk.write(len(node.segments), self.current_line)
```

**Files changed:** `ipp/parser/ast.py` (+5 lines), `ipp/parser/parser.py` (~40 lines), `ipp/vm/compiler.py` (~20 lines)

**Test — `tests/vm/v1.5.36_fstrings.ipp`:**
```ipp
var name = "World"
assert f"Hello {name}!" == "Hello World!"

var x = 10; var y = 20
assert f"{x} + {y} = {x + y}" == "10 + 20 = 30"

var items = [1, 2, 3]
assert f"count: {len(items)}" == "count: 3"

assert f"{{escaped braces}}" == "{escaped braces}"
```

---

### v1.5.37 — Fix: VM Import System Is a No-Op

**Symptom:** `import "helpers.ipp"` does nothing. All symbols from the file are undefined.

**Root cause:**
```
File: ipp/vm/vm.py, IMPORT opcode, lines 1089–1094
Pushes module path string and exits. No file loading, no execution, no binding.
```

**Exact fix:** Real implementation in the IMPORT opcode handler:
```python
elif opcode == OpCode.IMPORT:
    path_idx = code[ip+1] | (code[ip+2] << 8) | (code[ip+3] << 16)
    module_path = constants[path_idx] if path_idx < len(constants) else ""

    if not hasattr(self, '_module_cache'): self._module_cache = {}
    if module_path in self._module_cache:
        self.globals.update(self._module_cache[module_path])
    else:
        full = module_path if module_path.endswith('.ipp') else module_path + '.ipp'
        import os
        for candidate in [os.path.join(os.getcwd(), full), full]:
            if os.path.exists(candidate):
                with open(candidate, 'r') as f: src = f.read()
                break
        else:
            raise VMError(f"Module not found: '{module_path}'")

        from ipp.lexer.lexer import tokenize
        from ipp.parser.parser import parse
        from ipp.vm.compiler import compile_ast
        child = VM()
        child.globals.update(self.globals)
        child.run(compile_ast(parse(tokenize(src))))
        new_globals = {k: v for k, v in child.globals.items()
                       if k not in self.globals or child.globals[k] is not self.globals.get(k)}
        self.globals.update(new_globals)
        self._module_cache[module_path] = new_globals
```

**Files changed:** `ipp/vm/vm.py` (~40 lines replacing 4-line stub)

**Test — `tests/vm/helpers.ipp`** (support file):
```ipp
func add(a, b) { return a + b }
var MAGIC_NUMBER = 42
```

**Test — `tests/vm/v1.5.37_import.ipp`:**
```ipp
import "tests/vm/helpers.ipp"
assert add(3, 4) == 7
assert MAGIC_NUMBER == 42
```

---

### v1.5.38 — Fix: Spread Operator `[...lst]` Produces Wrong Results

**Symptom:** `[...a]` crashes; `[...a, 3]` drops elements; `[0, ...a, 4]` corrupts indices.

**Root cause:**
```
File: ipp/vm/compiler.py, compile_list()

Uses fixed-count LIST opcode: LIST with count = len(AST elements).
But SPREAD expands one element to N stack items.
LIST count (AST nodes) ≠ stack items after expansion.
```

**Exact fix:** Detect spread in list literal and use incremental build instead:
```python
def compile_list(self, node: ListLiteral):
    if not any(isinstance(e, SpreadExpr) for e in node.elements):
        # Fast path: no spread, fixed count
        for elem in node.elements: self.compile_expr(elem)
        self.chunk.write(OpCode.LIST, self.current_line)
        self.chunk.write(len(node.elements), self.current_line)
    else:
        # Spread path: build empty list, extend/append each element
        self.chunk.write(OpCode.LIST, self.current_line)
        self.chunk.write(0, self.current_line)        # empty list on stack
        for elem in node.elements:
            if isinstance(elem, SpreadExpr):
                self.compile_expr(elem.iterable)
                self.chunk.write(OpCode.LIST_EXTEND, self.current_line)  # new opcode
            else:
                self.compile_expr(elem)
                self.chunk.write(OpCode.LIST_APPEND, self.current_line)  # new opcode
```

Add `LIST_EXTEND` and `LIST_APPEND` opcodes to bytecode.py. In vm.py:
```python
elif opcode == OpCode.LIST_APPEND:
    val = self.stack.pop()
    self.stack[-1].append(val)   # list is TOS after pop

elif opcode == OpCode.LIST_EXTEND:
    iterable = self.stack.pop()
    lst = self.stack[-1]
    if hasattr(iterable, '__iter__') and not isinstance(iterable, (str, dict)):
        lst.extend(list(iterable))
```

**Files changed:** `ipp/vm/bytecode.py` (+2 opcodes), `ipp/vm/vm.py` (+10 lines), `ipp/vm/compiler.py` (~25 lines in compile_list)

**Test — `tests/vm/v1.5.38_spread.ipp`:**
```ipp
var a = [1, 2, 3]
var b = [...a]
assert b == [1, 2, 3]

var c = [...a, 4, 5]
assert c == [1, 2, 3, 4, 5]

var d = [0, ...a, 4]
assert d == [0, 1, 2, 3, 4]

var e = [...[1, 2], ...[3, 4]]
assert e == [1, 2, 3, 4]
```

---

## Phase C — Game Dev Features (v1.6.0 – v1.6.15)

---

### v1.6.0 — Feature: Operator Overloading

**Design:** When ADD/SUBTRACT/MULTIPLY/DIVIDE/NEGATE/EQUAL encounter an IppInstance, dispatch to `__add__`/`__sub__`/`__mul__`/`__div__`/`__neg__`/`__eq__`. Update stdlib Vector2, Vector3 to use these.

**Test:**
```ipp
class Vec2 {
    func init(x,y) { self.x=x\nself.y=y }
    func __add__(v) { return Vec2(self.x+v.x, self.y+v.y) }
    func __mul__(s) { return Vec2(self.x*s, self.y*s) }
    func __eq__(v)  { return self.x==v.x and self.y==v.y }
}
assert Vec2(1,2) + Vec2(3,4) == Vec2(4,6)
assert Vec2(2,3) * 3          == Vec2(6,9)
```

---

### v1.6.1 — Feature: Exception Type Hierarchy

**Design:** Add typed throw/catch. `throw ValueError("msg")` creates a typed exception object. `catch ValueError e` catches only that type.

**Test:**
```ipp
var kind = ""
try { throw ValueError("bad") } catch ValueError e { kind = "ValueError" } catch e { kind = "other" }
assert kind == "ValueError"
```

---

### v1.6.2 — Feature: Decorator Execution (`@decorator`)

**Design:** `@deco\nfunc f(){}` compiles as `func f(){}; f = deco(f)`.

**Test:**
```ipp
func memoize(f) {
    var cache = {}
    func wrapper(n) {
        if cache[n] == nil { cache[n] = f(n) }
        return cache[n]
    }
    return wrapper
}
@memoize
func fib(n) { if n <= 1 { return n } return fib(n-1) + fib(n-2) }
assert fib(10) == 55
```

---

### v1.6.3 — Feature: Multiple Return Values

**Design:** `return a, b` compiles as implicit list return. Pairs with MultiVarDecl from v1.5.28.

**Test:**
```ipp
func divmod(a, b) { return a // b, a % b }
var q, r = divmod(17, 5)
assert q == 3 and r == 2
```

---

### v1.6.4 — Feature: Named Function Arguments

**Test:**
```ipp
func connect(host, port=80, ssl=false) {
    return host + ":" + str(port)
}
assert connect("x.com", ssl=true, port=443) == "x.com:443"
```

---

### v1.6.5 — Feature: Property Accessors (get/set)

**Test:**
```ipp
class Health {
    func init() { self._hp = 100 }
    prop hp {
        get { return self._hp }
        set(v) { self._hp = clamp(v, 0, 100) }
    }
}
var h = Health()
h.hp = 150
assert h.hp == 100
h.hp = -10
assert h.hp == 0
```

---

### v1.6.6 — Feature: Signal/Event System

**Test:**
```ipp
class Button { signal on_click }
class UI {
    func handle(x, y) { print("click " + str(x)) }
}
var btn = Button()
var ui = UI()
connect(btn.on_click, ui.handle)
emit(btn.on_click, 100, 200)
```

---

### v1.6.7 — Feature: List Slicing `lst[a:b]`

**Test:**
```ipp
var lst = [0,1,2,3,4,5]
assert lst[1:4]  == [1,2,3]
assert lst[:3]   == [0,1,2]
assert lst[3:]   == [3,4,5]
assert lst[::2]  == [0,2,4]
assert lst[-2:]  == [4,5]
```

---

### v1.6.8 — Feature: `Matrix4x4` and `Quaternion` Types

**Test:**
```ipp
var m = mat4_identity()
var v = vec4(1, 0, 0, 1)
var r = m * v
assert r.x == 1 and r.y == 0

var q = quat_from_euler(0, 0, 0)
assert abs(q.w - 1.0) < 0.001
```

---

### v1.6.9 — Feature: Async/Await in VM Compiler

**Test:**
```ipp
async func fetch_data() {
    await delay(0)
    return 42
}
var result = async_run(fetch_data())
assert result == 42
```

---

### v1.6.10 — Fix: IppSet Attribute Unification (`_items` vs `_data`)

**Fix:** Change vm.py `_builtin_type` and `_builtin_set` to use `_items` (matching interpreter.py), or rename `_items` to `_data` in interpreter.py. Pick one, update everywhere.

**Test:**
```ipp
var s = set([1, 2, 3, 2, 1])
assert type(s) == "set"
assert len(s) == 3
var s2 = set(s)
s2.add(4)
assert len(s) == 3 and len(s2) == 4
```

---

### v1.6.11 — Fix: TAIL_CALL Top-Level Frame Crash

**Fix:** After popping current frame, check `self.frames` before doing `self.frames[-1]`. Route to normal `_call` with `None` return frame handled gracefully.

**Test:**
```ipp
func count_down(n) {
    if n == 0 { return "done" }
    return count_down(n - 1)
}
assert count_down(500) == "done"
```

---

### v1.6.12 — Feature: Fluent List Methods

Calling `.sort()`, `.reverse()`, `.map(fn)`, `.filter(fn)`, `.reduce(fn, init)` on list instances.

**Test:**
```ipp
var lst = [3, 1, 4, 1, 5, 9]
lst.sort()
assert lst[0] == 1 and lst[-1] == 9

var doubled = [1,2,3].map(func(x) { return x * 2 })
assert doubled == [2, 4, 6]
```

---

### v1.6.13 — Feature: String Format Method

**Test:**
```ipp
assert "Hello {}!".format("World") == "Hello World!"
assert "x={}, y={}".format(3, 4) == "x=3, y=4"
assert "{name} is {age}".format(name="Alice", age=30) == "Alice is 30"
```

---

### v1.6.14 — Feature: Bytecode Caching (`.ippbc`)

`ipp run file.ipp` checks for a `.ippbc` file newer than the source. If found, loads it directly. `ipp compile file.ipp` explicitly writes the cache.

---

### v1.6.15 — Feature: Static Linter (`ipp check`)

Reports: undefined variables, unused `let` bindings, unreachable code after `return`, function calls with wrong argument count (when determinable statically).

---

## Phase D — Architecture Unification (v1.7.0 – v1.7.5)

---

### v1.7.0 — Archive Tree-Walking Interpreter

Move `ipp/interpreter/interpreter.py` to `ipp/interpreter/legacy.py`. Default execution = VM. Flag `--interp` enables legacy mode. All existing 37 tests must pass without `--interp`.

---

### v1.7.1 — Opcode Unit Test Suite

One Python test file per opcode: `CONSTANT`, `GET_LOCAL`, `SET_LOCAL`, `CLOSURE`, `CALL`, `RETURN`, `JUMP`, `LOOP`, `CLASS`, `METHOD`, `GET_INDEX`, `SET_INDEX`, `SPREAD`, `CLOSURE`, etc. Each test creates a minimal Chunk and runs it through the VM directly.

---

### v1.7.2 — Error Quality: Line Numbers + Call Stack Traces

All VMErrors include source line. Closures track definition line. Stack traces show the full call chain: `  at fib (game.ipp:42)\n  at main (game.ipp:60)`.

---

### v1.7.3 — Package Manager Foundation (`ippkg`)

`ipp install user/package` downloads to `~/.ipp/packages/`. `import "physics2d"` resolves from package dir after stdlib lookup. `ipp.toml` manifest.

---

### v1.7.4 — LSP Completion and Diagnostics

LSP `textDocument/completion` returns builtins + user-defined names. `textDocument/publishDiagnostics` sends undefined-variable errors on save.

---

### v1.7.5 — WASM Backend (Real Implementation)

`WASMVisitor` class with `visit_*` for all AST nodes. `fib(20)` compiles to valid `.wat` runnable in `wasmtime`. Web playground on GitHub Pages.

---

## Phase E — Native VM Performance (v2.0.0+)

---

### v2.0.0 — C Extension VM Core

Rewrite dispatch loop and value stack in C. Expose via cffi. Target: 10× speedup.

Performance target: `fib(25)` ≤ 500ms (currently 5,092ms).

---

### v2.0.1 — SIMD Vector Math

`Vector4` and `Matrix4x4` operations via C extension using SSE/AVX. Target: `vec4_dot()` 100× faster than current Python dict-attribute access.

---

### v2.0.2 — Native Game Loop (SDL2/raylib)

`game_loop(fps=60) { var dt = delta_time(); ... }` construct. `input.is_pressed(KEY_W)`. `audio.play("sfx.wav")`. Backed by SDL2 or raylib C library.

---

### v2.0.3 — Tracing JIT (Long-Term)

Count hot loop iterations. At threshold (e.g., 100), trace and emit native x86/ARM code for the loop body. Target: within 3× of Lua 5.4 for compute-bound loops.

---

## Master Version Summary

| Version | Focus | Bug IDs Fixed | Est. LoC Changed |
|---------|-------|--------------|-----------------|
| **v1.5.21** | For-in loop comparison | BUG-L1 | 8 |
| **v1.5.22** | `pi`/`e` as values | BUG-S6 | 2 |
| **v1.5.23** | `let` immutability | BUG-L8 | ~25 |
| **v1.5.24** | `__str__` VM fix + dead code | BUG-L6, BUG-S1 | ~18 |
| **v1.5.25** | Static method access | BUG-L7 | ~20 |
| **v1.5.26** | `continue` in while | BUG-L4 | ~15 |
| **v1.5.27** | `continue` in for-in | BUG-L4 | ~15 |
| **v1.5.28** | MultiVarDecl compiler | BUG-L9 | ~30 |
| **v1.5.29** | List comprehension impl | BUG-L2 | ~65 |
| **v1.5.30** | Dict comprehension impl | BUG-L3 | ~50 |
| **v1.5.31** | Global cache hash fix | BUG-S2 | 5 |
| **v1.5.32** | SET_INDEX stack fix | BUG-S10 | ~12 |
| **v1.5.33** | `do {} while` syntax | BUG-L5, BUG-L18 | ~12 |
| **v1.5.34** | Multiple catch blocks | BUG-L13 | ~30 |
| **v1.5.35** | Variadic params `...args` | BUG-L15 | ~45 |
| **v1.5.36** | F-strings parse + compile | BUG-L14, BUG-S5 | ~65 |
| **v1.5.37** | VM import system | BUG-S3 | ~45 |
| **v1.5.38** | Spread operator + opcodes | BUG-L10 | ~40 |
| **v1.6.0** | Operator overloading | NEW | ~60 |
| **v1.6.1** | Exception types | NEW | ~40 |
| **v1.6.2** | Decorators | BUG-L12 | ~30 |
| **v1.6.3** | Multiple return values | BUG-L16 | ~25 |
| **v1.6.4** | Named arguments | NEW | ~45 |
| **v1.6.5** | Property accessors | NEW | ~65 |
| **v1.6.6** | Signal system | NEW | ~80 |
| **v1.6.7** | List slicing `[a:b]` | BUG-L11 | ~35 |
| **v1.6.8** | Matrix4x4 + Quaternion | NEW | ~220 |
| **v1.6.9** | Async/await in VM | BUG-S8 | ~110 |
| **v1.6.10** | IppSet unification | BUG-S4 | ~10 |
| **v1.6.11** | TAIL_CALL fix | BUG-S7 | ~10 |
| **v1.6.12** | Fluent list methods | NEW | ~40 |
| **v1.6.13** | String.format() | NEW | ~30 |
| **v1.6.14** | Bytecode caching | NEW | ~80 |
| **v1.6.15** | Static linter | NEW | ~150 |
| **v1.7.0** | Archive interpreter | ARCH | ~80 |
| **v1.7.1** | Opcode unit tests | TEST | ~300 |
| **v1.7.2** | Error quality | NEW | ~50 |
| **v1.7.3** | Package manager | NEW | ~200 |
| **v1.7.4** | LSP completion | NEW | ~150 |
| **v1.7.5** | WASM real impl | BUG-S9 | ~300 |
| **v2.0.0** | C extension VM | PERF | ~3000 C |
| **v2.0.1** | SIMD vectors | PERF | ~500 C |
| **v2.0.2** | Native game loop | NEW | ~400 |
| **v2.0.3** | Tracing JIT | PERF | ~10000 C |

**Total: 43 planned releases | 27 bugs addressed | ~7,300 lines of changes**

---

## The Golden Rule

> **A version ships when:**
> 1. The named fix is in the VM compiler (not interpreter-only)
> 2. The test file `tests/vm/vX.Y.Z.ipp` executes and passes
> 3. All previous version tests still pass (zero regressions)
> 4. `pyproject.toml` version number is updated
>
> **Interpreter-only = ⚠️ PARTIAL. Not in a passing VM test = ⬜ UNVERIFIED. Neither = ✅ DONE.**

---

*Roadmap v7 — April 12, 2026*
*27 bugs → 43 micro-releases → v2.0.3 as performance target*
*Start with v1.5.21. One file change. One test. Ship.*
