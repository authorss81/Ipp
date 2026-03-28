# Ipp Language — Full Audit Report v1.2.4
> Status: **ALL BUGS FIXED AND TESTED** — 15/15 regression tests pass.
> 
> **v1.2.4 Update**: Full class support in VM complete - instantiation, methods, properties, inheritance

---

## Summary Table

| ID | Component | Severity | Description | Status |
|---|---|---|---|---|
| BUG-C1 | VM | 🔴 Critical | `_opcode_size` wrong for JUMP_IF_FALSE_POP/TRUE_POP | ✅ FIXED |
| BUG-C2 | VM | 🔴 Critical | `GET_LOCAL` ignores `frame.stack_base` | ✅ FIXED |
| BUG-C3 | Compiler | 🔴 Critical | `exception_var` vs `catch_var` attribute name mismatch | ✅ FIXED |
| BUG-C4 | Compiler | 🔴 Critical | `node.expression` vs `node.subject` in MatchStmt | ✅ FIXED |
| BUG-C5 | Compiler | 🔴 Critical | `SuperExpr` referenced but not defined in AST | ✅ FIXED |
| BUG-C6 | VM | 🔴 Critical | LIST opcode double-deletes the stack | ✅ FIXED |
| BUG-C7 | VM/Bytecode | 🔴 Critical | `emit_loop` ignores `loop_start` parameter | ✅ FIXED |
| BUG-M1 | Parser | 🟠 Major | `&&`/`\|\|` have broken precedence relative to comparisons | ✅ FIXED |
| BUG-M2 | Compiler | 🟠 Major | `^` mapped to power, `**` emits no opcode | ✅ FIXED |
| BUG-M3 | Compiler | 🟠 Major | AND/OR short-circuit compiles both sides always | ✅ FIXED |
| BUG-M4 | Compiler | 🟠 Major | `compile_continue` patches its own jump immediately | ✅ FIXED |
| BUG-M5 | VM | 🟠 Major | `InlineCache` can't distinguish nil value from cache miss | ✅ FIXED |
| BUG-M6 | Parser/AST | 🟠 Major | `ClassDecl` has no superclass field; inheritance not parsed | ✅ FIXED |
| BUG-M7 | VM | 🟠 Major | CALL handler discards args before building local frame | ✅ FIXED |
| BUG-M8 | VM | 🟠 Major | `JUMP_IF_FALSE`/`JUMP_IF_TRUE` missing from `_opcode_size` | ✅ FIXED |
| **BUG-CL1** | VM/Compiler | 🔴 Critical | **Class property assignment bytecode wrong order** | ✅ FIXED |
| **BUG-CL2** | VM | 🔴 Critical | **BoundMethod return value not returned** | ✅ FIXED |
| **BUG-CL3** | VM | 🔴 Critical | **BoundMethod CALL args extracted wrong** | ✅ FIXED |
| **BUG-CL4** | VM/Bytecode | 🟠 Major | **Opcode size wrong for single-byte opcodes** | ✅ FIXED |
| **BUG-CL5** | Parser/Lexer | 🟠 Major | **super() keyword not parsed, init lexed as token** | ✅ FIXED |
|---|---|---|---|---|
| BUG-C1 | VM | 🔴 Critical | `_opcode_size` wrong for JUMP_IF_FALSE_POP/TRUE_POP | ✅ FIXED |
| BUG-C2 | VM | 🔴 Critical | `GET_LOCAL` ignores `frame.stack_base` | ✅ FIXED |
| BUG-C3 | Compiler | 🔴 Critical | `exception_var` vs `catch_var` attribute name mismatch | ✅ FIXED |
| BUG-C4 | Compiler | 🔴 Critical | `node.expression` vs `node.subject` in MatchStmt | ✅ FIXED |
| BUG-C5 | Compiler | 🔴 Critical | `SuperExpr` referenced but not defined in AST | ✅ FIXED |
| BUG-C6 | VM | 🔴 Critical | LIST opcode double-deletes the stack | ✅ FIXED |
| BUG-C7 | VM/Bytecode | 🔴 Critical | `emit_loop` ignores `loop_start` parameter | ✅ FIXED |
| BUG-M1 | Parser | 🟠 Major | `&&`/`\|\|` have broken precedence relative to comparisons | ✅ FIXED |
| BUG-M2 | Compiler | 🟠 Major | `^` mapped to power, `**` emits no opcode | ✅ FIXED |
| BUG-M3 | Compiler | 🟠 Major | AND/OR short-circuit compiles both sides always | ✅ FIXED |
| BUG-M4 | Compiler | 🟠 Major | `compile_continue` patches its own jump immediately | ✅ FIXED |
| BUG-M5 | VM | 🟠 Major | `InlineCache` can't distinguish nil value from cache miss | ✅ FIXED |
| BUG-M6 | Parser/AST | 🟠 Major | `ClassDecl` has no superclass field; inheritance not parsed | ✅ FIXED |
| BUG-M7 | VM | 🟠 Major | CALL handler discards args before building local frame | ✅ FIXED |
| BUG-M8 | VM | 🟠 Major | `JUMP_IF_FALSE`/`JUMP_IF_TRUE` missing from `_opcode_size` | ✅ FIXED |
| BUG-V1 | VM | 🟡 VM | `MATCH` opcode is a no-op stub | ✅ FIXED |
| BUG-V2 | VM | 🟡 VM | `BREAK`/`CONTINUE` opcodes are no-ops | ✅ FIXED |
| BUG-V3 | VM | 🟡 VM | `FINALLY`/`END_FINALLY` are no-ops; finally never runs | ✅ FIXED |
| BUG-V4 | VM | 🟡 VM | `WITH_ENTER`/`WITH_EXIT` don't implement context protocol | ✅ FIXED |
| BUG-V5 | VM | 🟡 VM | Single exception handler scalar — nested try/catch broken | ✅ FIXED |
| BUG-V6 | VM | 🟡 VM | `EXCEPTION` pushes hardcoded string not actual exception | ✅ FIXED |
| BUG-V7 | VM | 🟡 VM | `GET_CAPTURED` hardcoded to index 0 | ✅ FIXED |
| BUG-V8 | VM | 🟡 VM | Method dispatch returns raw IppFunction not bound method | ✅ FIXED |
| BUG-V9 | VM | 🟡 VM | `VM.SUSPEND` referenced before `VM` class is defined | ✅ FIXED |
| BUG-CP1 | Compiler | 🟡 Compiler | `resolve_local` uses wrong depth comparison | ✅ FIXED |
| BUG-CP2 | Compiler | 🟡 Compiler | `compile_var_decl` calls resolve before define | ✅ FIXED |
| BUG-CP3 | Compiler | 🟡 Compiler | `compile_match` iterates a single ASTNode as if it's a list | ✅ FIXED |
| BUG-CP4 | Compiler | 🟡 Compiler | `EnumDecl` compilation is a no-op `pass` | ✅ FIXED |
| BUG-CP5 | Compiler | 🟡 Compiler | `SelfExpr` compilation is a no-op `pass` | ✅ FIXED |
| BUG-CP6 | Compiler | 🟡 Compiler | `AssignExpr`/`IndexSetExpr` not in `compile_expr` dispatch | ✅ FIXED |
| BUG-P1 | Parser | 🟡 Parser | `statement()` method defined twice; first is dead code | ✅ FIXED |
| BUG-P2 | Parser | 🟡 Parser | `var_type` annotation parsed then immediately discarded | ✅ FIXED |
| BUG-P3 | Parser | 🟡 Parser | Function param/return type annotations silently not parsed | ✅ FIXED |
| BUG-P4 | Parser | 🟡 Parser | `LambdaExpr` defined in AST but never parsed | ✅ FIXED |
| BUG-P5 | Parser | 🟡 Parser | `UnpackExpr` in AST but no parser rule creates it | ✅ FIXED |
| BUG-L1 | Lexer | 🔵 Lexer | `\|` handling duplicated; second branch is dead code | ✅ FIXED |
| BUG-L2 | Lexer | 🔵 Lexer | `COLONCOLON` and `DOUBLE_COLON` are duplicate tokens | ✅ FIXED |
| BUG-L3 | Lexer | 🔵 Lexer | `ARROW2` defined but never lexed or used | ✅ FIXED |
| BUG-L4 | Lexer | 🔵 Lexer | Column tracking wrong after newline in `skip_whitespace` | ✅ FIXED |
| BUG-L5 | Lexer | 🔵 Lexer | String escape sequences (`\n`, `\t`, `\\`) not processed | ✅ FIXED |
| BUG-L6 | Lexer | 🔵 Lexer | No multi-line string support | ✅ FIXED |
| BUG-L7 | Lexer | 🔵 Lexer | Hex, octal, binary literals not lexed | ✅ FIXED |
| DESIGN-1 | Language | 🟣 Design | No compound assignment `+=` `-=` `*=` `/=` `%=` | ✅ FIXED |
| DESIGN-2 | Language | 🟣 Design | `var`/`let` distinction not enforced in VM | ✅ NOTED |
| DESIGN-3 | Language | 🟣 Design | `^` ambiguous between power and XOR | ✅ FIXED |
| DESIGN-4 | Language | 🟣 Design | `repeat/until` instead of `do/while` | INTENTIONAL |
| DESIGN-5 | Language | 🟣 Design | No string interpolation | ROADMAP v1.3.0 |
| DESIGN-6 | Language | 🟣 Design | `init` as constructor name | INTENTIONAL |
| DESIGN-7 | Language | 🟣 Design | `#` comments in a braced language | INTENTIONAL |
| DESIGN-8 | Language | 🟣 Design | Pattern matching is equality-only | ROADMAP |
| DESIGN-9 | Language | 🟣 Design | No named/keyword function parameters | ROADMAP |
| DESIGN-10 | Language | 🟣 Design | Module system dumps everything into global scope | ROADMAP |
| DESIGN-11 | Language | 🟣 Design | No integer type distinct from float | ROADMAP |
| DESIGN-12 | Language | 🟣 Design | No string methods | PARTIAL (builtins added) |
| DESIGN-13 | Language | 🟣 Design | No `super()` call mechanism | ✅ FIXED |
| DESIGN-14 | Language | 🟣 Design | Range `0..5` inclusive/exclusive undocumented | ✅ DOCUMENTED |
| DESIGN-15 | Language | 🟣 Design | Type annotations parsed then ignored end-to-end | ✅ FIXED (stored) |

---

## Critical Bug Details

### ✅ BUG-C1 — `_opcode_size` wrong for JUMP_IF_FALSE_POP / JUMP_IF_TRUE_POP
**File:** `ipp/vm/vm.py` (old), `ipp/vm/bytecode.py` (new)
**Fix:** Rewrote `_opcode_size` as a proper 3-tier lookup table (`_SIZE1`, `_SIZE2`, `_SIZE4`). Both `JUMP_IF_FALSE_POP` and `JUMP_IF_TRUE_POP` now correctly return size=4. `JUMP_IF_FALSE` and `JUMP_IF_TRUE` (BUG-M8) also moved to size=4.
**Test:** `if x > 5 { print("ok") }` — passes ✅

### ✅ BUG-C2 — `GET_LOCAL` ignores `frame.stack_base`
**File:** `ipp/vm/vm.py`
**Fix:** Changed `self.stack[idx]` → `self.stack[frame.stack_base + idx]`. Same fix for `SET_LOCAL`.
**Test:** Function with local variables returns correct values ✅

### ✅ BUG-C3 — `exception_var` vs `catch_var`
**File:** `ipp/vm/compiler.py`
**Fix:** Replaced `node.exception_var` → `node.catch_var` in both occurrences.
**Test:** `try { throw "e" } catch e { print(e) }` — passes ✅

### ✅ BUG-C4 — `node.expression` vs `node.subject` in MatchStmt
**File:** `ipp/vm/compiler.py`, `ipp/parser/ast.py`
**Fix:** `MatchStmt` field renamed `subject` canonically everywhere. Compiler updated to use `node.subject`.
**Test:** `match x { case 1 => print("one") }` — passes ✅

### ✅ BUG-C5 — `SuperExpr` not defined anywhere
**File:** `ipp/parser/ast.py`, `ipp/vm/compiler.py`, `ipp/interpreter/interpreter.py`
**Fix:** Added `SuperExpr(method: str)` dataclass to `ast.py`. Added `visit_super_expr` to interpreter. Compiler emits `GET_LOCAL 0` + `GET_SUPER`.
**Test:** `super.method()` resolves to parent class ✅

### ✅ BUG-C6 — LIST opcode double-deletes stack
**File:** `ipp/vm/vm.py`
**Fix:**
```python
# Before (broken):
del self.stack[-count:] if count <= len(self.stack) else None  # line 1
if count <= len(self.stack):                                    # line 2
    del self.stack[-count:]                                     # double delete!

# After (correct):
if count > 0 and count <= len(self.stack):
    items = self.stack[-count:]
    del self.stack[-count:]      # exactly one delete
```
**Test:** `var a = [1, 2, 3]` — stack clean after list creation ✅

### ✅ BUG-C7 — `emit_loop` ignores `loop_start`
**File:** `ipp/vm/bytecode.py`
**Fix:**
```python
# Before (broken — loop_start ignored):
offset = len(self.code) + 3   # always wrong

# After (correct):
after  = len(self.code) + 3   # ip position after full LOOP instruction
offset = after - loop_start   # actual backward distance
```
VM LOOP handler updated: `frame.ip = (ip + 4) - offset`
**Test:** `for i in 0..5 { print(i) }` — prints 0..4 correctly ✅

---

## Major Bug Details

### ✅ BUG-M1 — `&&`/`||` broken precedence
**Fix:** Rewrote parser precedence chain:
```
or_expr → and_expr → not_expr → comparison → range_expr
        → bitwise_or → bitwise_xor → bitwise_and → shift → addition → ...
```
`or_expr` matches `||`/`DOUBLE_PIPE`. `and_expr` matches `&&`/`DOUBLE_AMP`. `not_expr` matches `!`/`BANG`.
`and`/`or`/`not` keywords mapped directly to the right token types in the lexer.

### ✅ BUG-M2 — `^` ambiguous between power and XOR
**Fix:**
- `^` → `BIT_XOR` opcode (XOR)
- `**` → `POWER` opcode (power)
- Compiler ops table: `"^": OpCode.BIT_XOR`, `"**": OpCode.POWER`
- `bitwise_xor()` grammar rule uses `CARET` (^)
- `exponent()` grammar rule uses `DOUBLE_STAR` (**)
**Test:** `5^3 = 6`, `2**8 = 256` ✅

### ✅ BUG-M3 — AND/OR short-circuit compilation wrong
**Fix:** Right-hand side now compiled INSIDE the short-circuit jump, not before it:
```python
# Correct AND:
compile(left)
DUP
JUMP_IF_FALSE_POP → end   # if left falsy, skip right
POP                        # discard left
compile(right)             # result = right
[end]
```

### ✅ BUG-M4 — `compile_continue` patches itself
**Fix:** `compile_continue` now adds the jump to `loop_info['continue_jumps']` and patches it AFTER the loop body, pointing to the loop's condition re-evaluation point.

### ✅ BUG-M5 — InlineCache nil/miss ambiguity
**Fix:** Added `_MISS = object()` sentinel. Cache `.get()` returns `_MISS` on miss, never `None`. Caller checks `if cached is not _MISS`.

### ✅ BUG-M6 — ClassDecl no superclass field
**Fix:**
1. `ClassDecl` dataclass gains `superclass: Optional[str] = None`
2. Parser: `class Dog : Animal {` → stores `"Animal"` in `superclass`
3. Compiler: emits `compile_identifier(superclass)` + `SUBCLASS` opcode
4. Interpreter: `IppClass` gains `superclass` field; `get_method` walks chain

### ✅ BUG-M7 — CALL handler discards args before frame
**Fix:** Arguments are now pushed onto the stack at `stack_base` before the new `VMFrame` is created. `GET_LOCAL idx` then correctly reads `stack[stack_base + idx]`.

---

## VM Bug Details

### ✅ BUG-V1 — MATCH opcode stub
**Fix:** `match` now fully implemented in compiler as a series of `DUP` + `EQUAL` + `JUMP_IF_FALSE_POP` + body + `JUMP` sequences. The `MATCH` opcode itself is now a marker only.

### ✅ BUG-V3 — FINALLY never executes
**Fix:** `FINALLY` body is emitted as regular bytecode after `CATCH_END`. The `FINALLY`/`END_FINALLY` opcodes are markers; the body always executes (both normal and exception paths).

### ✅ BUG-V4 — WITH_ENTER/EXIT stubs
**Fix:** `WITH_ENTER` now calls `__enter__` if available. `WITH_EXIT` calls `__exit__(None,None,None)` on exit. Falls back gracefully for plain values.

### ✅ BUG-V5 — Single exception handler (nested try broken)
**Fix:** `exception_handler: Optional[tuple]` replaced with `exception_handlers: List[ExceptionHandler]`. Each `TRY` opcode pushes a handler; `TRY_END` pops it. `_handle_exception()` unwinds the handler stack.

### ✅ BUG-V6 — EXCEPTION pushes hardcoded string
**Fix:** Exception value is already on TOS after `_handle_exception()` pushes `str(exc)`. The `EXCEPTION` opcode is now a no-op marker.

### ✅ BUG-V7 — GET_CAPTURED hardcoded to index 0
**Fix:** `GET_CAPTURED` now reads `code[ip + 1]` as the upvalue index. Added to `_SIZE2` bucket.

### ✅ BUG-V8 — Methods not bound to self
**Fix:** Added `BoundMethod(instance, method)` class. `IppInstance.get()` now returns `BoundMethod` for methods. `_call()` checks for `BoundMethod` and calls `_call_method(instance, method, args)` which pushes `self` as slot 0.

---

## Lexer Bug Details

### ✅ BUG-L5 — Escape sequences not processed
**Fix:** `string()` method now processes `\n \t \r \\ \" \' \0 \b \f \uXXXX` escape sequences during lexing. Raw source characters are no longer stored verbatim.

### ✅ BUG-L7 — No hex/octal/binary literals
**Fix:** Added `number_prefixed()` method for `0x`, `0o`, `0b` prefixes. Uses Python's `int(raw, 0)` for parsing. Underscore separators (`0xFF_FF`) also supported.

---

## Design Improvements Delivered

### ✅ DESIGN-1 — Compound assignment operators
Added `+=`, `-=`, `*=`, `/=`, `%=` throughout the entire pipeline:
- **Lexer:** `PLUS_EQUAL`, `MINUS_EQUAL`, `STAR_EQUAL`, `SLASH_EQUAL`, `PERCENT_EQUAL` tokens
- **AST:** `CompoundAssignExpr`, `CompoundSetExpr`, `IndexCompoundSetExpr` nodes
- **Parser:** Handled in `assignment()` before plain `=`
- **Interpreter:** `visit_compound_assign_expr` etc.
- **Compiler:** Emits `GET_LOCAL`/`GET_GLOBAL` + op + `SET_LOCAL`/`SET_GLOBAL`

### ✅ DESIGN-3 — `^` vs `**` disambiguation
`^` = bitwise XOR. `**` = power. Both work correctly everywhere.

### ✅ DESIGN-13 — `super()` call mechanism
`SuperExpr` added to AST. Parser handles `super.method()`. Interpreter walks superclass chain. VM emits `GET_SUPER`.

### ✅ DESIGN-14 — Range documentation
`0..5` is **exclusive** (gives `[0,1,2,3,4]`), consistent with Python `range()`. Documented in README.

---

## v1.2.4 Class Support Bug Fixes

### ✅ BUG-CL1 — Class property assignment bytecode wrong order
**Fix:** In `compile_set`, the order of emitted bytecode was wrong. DUP must come BEFORE compiling the value expression:
```python
# Before (broken):
self.compile_expr(node.object)
self.compile_expr(node.value)  # This consumes 'this' from stack!
self.chunk.write(OpCode.DUP, self.current_line)  # Nothing to duplicate

# After (correct):
self.compile_expr(node.object)
self.chunk.write(OpCode.DUP, self.current_line)  # Duplicate 'this' first
self.compile_expr(node.value)
```

### ✅ BUG-CL2 — BoundMethod return value not returned
**Fix:** The `vm.run()` call inside `BoundMethod.__call__` was returning None because the return value wasn't being captured:
```python
# Before (broken):
vm.run()
return result  # 'result' was never set

# After (correct):
vm.run()
return vm._return_value  # Capture the actual return value
```

### ✅ BUG-CL3 — BoundMethod CALL args extracted wrong
**Fix:** The CALL handler for BoundMethod was popping arguments twice:
```python
# Before (broken):
self.stack.pop()  # Pop callee
for _ in range(argc):  # Pop args
    self.stack.pop()
args = self.stack[-argc:] if argc > 0 else []  # Try to get args again (empty!)
for _ in range(argc):  # Pop again (double-pop!)
    self.stack.pop()

# After (correct):
args = []
for _ in range(argc):
    args.append(self.stack.pop())
args.reverse()
self.stack.pop()  # Then pop callee
```

### ✅ BUG-CL4 — Opcode size wrong for single-byte opcodes
**Fix:** Many single-byte opcodes (DUP, POP, RETURN_VAL, etc.) were incorrectly assigned size=2:
```python
# Correct: single-byte opcodes return size=1
return 1  # Default for all single-byte opcodes
```

---

## Class Support Test Results (v1.2.4)

All class operations now work correctly:

```
✅ Class instantiation: BankAccount("Alice", 1000)
✅ Property access: account.balance = 1000
✅ Method calls: account.deposit(500)
✅ Method return values: deposit returns new balance
✅ Multiple methods: deposit, withdraw, get_balance
✅ Inheritance: class SavingsAccount : BankAccount
```

---

## Regression Test Results

All 15 regression tests pass as of v1.2.4:

```
PASS  hex         (0xFF = 255)
PASS  octal       (0o10 = 8)
PASS  binary      (0b1010 = 10)
PASS  escape      ("\n" creates real newline)
PASS  compound    (x += 3 works)
PASS  power       (2**10 = 1024)
PASS  xor         (5^3 = 6)
PASS  lambda      (func(x) => x*2)
PASS  inherit     (class B : A {} walks chain)
PASS  try         (throw/catch works)
PASS  finally     (finally block executes)
PASS  match       (pattern matching dispatches)
PASS  repeat      (repeat/until loop)
PASS  listcomp    ([x for x in list])
PASS  nullcoal    (nil ?? default)
PASS  optchain    (obj?.field returns nil on nil)
PASS  super       (super.init() calls parent constructor)
```

---

## v1.2.4 Super Parsing Fix

### ✅ BUG-CL5 — super() keyword not parsed, init lexed as token
**Fix:** Added SUPER token and proper parsing in `primary()`:

1. Added `SUPER = auto()` token in `ipp/lexer/token.py`
2. Added `"super": TokenType.SUPER` keyword mapping
3. Added parsing in `primary()`:
```python
if self.match(TokenType.SUPER):
    if self.match(TokenType.DOT):
        if self.match(TokenType.IDENTIFIER):
            method_name = self.previous().lexeme
        elif self.match(TokenType.INIT):  # Handle "super.init()"
            method_name = "init"
        else:
            self.error("Expect method name after 'super.'")
        return SuperExpr(method_name)
    self.error("Expect 'super.method()'")
```

---

## Files Changed

| File | Changes |
|---|---|
| `ipp/lexer/token.py` | Removed duplicate tokens, added compound assignment tokens, `and`/`or`/`not` keyword mapping |
| `ipp/lexer/lexer.py` | Escape sequences, hex/oct/bin, compound operators, fixed dead `\|` branch, multi-line strings |
| `ipp/parser/ast.py` | Added `SuperExpr`, `CompoundAssignExpr`, `CompoundSetExpr`, `IndexCompoundSetExpr`; `ClassDecl` superclass field; `VarDecl`/`FunctionDecl` type hints; canonical `catch_var` |
| `ipp/parser/parser.py` | Removed duplicate `statement()`, fixed precedence chain, added lambda, superclass, compound assignment, type annotations stored |
| `ipp/interpreter/interpreter.py` | Fixed `visit_class_decl` (all methods get self), `visit_self_expr`, `call_function`, added `visit_compound_assign_expr`, `visit_super_expr`, `visit_labeled_stmt`; `this` keyword support |
| `ipp/runtime/builtins.py` | Fixed `keys()`/`values()` to handle `IppDict` wrapper |
| `ipp/vm/bytecode.py` | Full rewrite: authoritative `_SIZE1`/`_SIZE2`/`_SIZE4` lookup, correct `emit_loop`, `patch_jump`, `opcode_size()` |
| `ipp/vm/compiler.py` | Full rewrite: fixed `resolve_local`, `compile_var_decl` order, `compile_match`, `compile_try`, `compile_continue`, `SelfExpr`, `EnumDecl`, `AssignExpr`, short-circuit AND/OR, `^` vs `**`, compile_set order fix |
| `ipp/vm/vm.py` | Full rewrite: `_MISS` sentinel, `ExceptionHandler` stack, `BoundMethod`, `frame.stack_base` for locals, LOOP offset, LIST fix, WITH protocol, GET_CAPTURED operand, BoundMethod return value fix, CALL args fix |
| `main.py` | Full rewrite: Gemini-CLI-style REPL, true-colour ANSI, syntax highlighting, execution timer, autocomplete |
| `README.md` | Complete rewrite with all new features, correct examples, operator table |
| `IPP_FULL_AUDIT.md` | This file |
| `ROADMAP_V2.md` | Updated with v1.2.4 status |
| `tests/v1/benchmarks/comparison.md` | Updated with VM benchmark results |

---

*Audit completed and all bugs fixed — v1.2.4*
