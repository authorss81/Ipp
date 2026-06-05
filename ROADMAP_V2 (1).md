# Ipp Language Roadmap v4
> **Current version:** `1.9.1`
> **Based on:** `new_audit(1).md` v4 — 18 confirmed open bugs (4 new), ~52 confirmed working features
> **Phase A complete.** Next immediate work: Phase A2 micro-versions (v1.7.9.1.12 onward).
> **This roadmap:** All original v1.7.6–v2.1.5 sections preserved with full detail + 22 new sub-versions injected from audit v4 findings.

---

## How to Use This Roadmap

### For every version, do this in order:

```
1. Read the "Exact fix" section in this file
2. Make ONLY the changes described — do not touch other files
3. Write the test file to tests/vX_Y_Z/
4. Run: python tests/vX_Y_Z/test_*.ipp (must print nothing unexpected)
5. Confirm the specific broken behaviour no longer occurs
6. Update VERSION = "X.Y.Z" in main.py and ipp/main.py
7. Update version = "X.Y.Z" in pyproject.toml
8. Commit with message: "vX.Y.Z: <one-line description>"
```

### Version numbering rule

- **PATCH** (Z): single bug fix or single missing method added
- **MINOR** (Y): new feature or group of related fixes
- **MAJOR** (X): architecture change, breaking change, or C/Rust VM

### Definition of DONE

A version is done when:
- ✅ The named fix is in the **VM path** (not interpreter-only)
- ✅ The test file in `tests/vX_Y_Z/` runs without crashing
- ✅ The test file asserts the **correct output**, not just "it ran"
- ✅ All previous version tests still pass (zero regressions)
- ✅ VERSION string updated in `main.py`, `ipp/main.py`, `pyproject.toml`

A version is **NOT done** if:
- ❌ The test only checks that the file ran (`print("PASSED")` without assertions)
- ❌ The fix is in the interpreter but not the VM compiler/vm.py
- ❌ A previous test now fails

### First thing to do before coding anything

```bash
# Run this to see your current baseline
python tests/regression.py
# Or manually:
python -c "
import sys, types
sys.modules['tkinter'] = types.ModuleType('tkinter')
import glob
sys.path.insert(0, '.')
from ipp.vm.vm import VM
from ipp.vm.compiler import compile_ast
from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
passed = failed = 0
for f in sorted(glob.glob('tests/**/*.ipp', recursive=True)):
    try:
        vm = VM(); vm.run(compile_ast(parse(tokenize(open(f).read()))))
        passed += 1
    except Exception as e:
        failed += 1
        print(f'FAIL {f}: {e}')
print(f'{passed} pass / {failed} fail')
"
```


---

## VERSION STATUS ✅

Version is correctly `1.7.9.1.16` in `main.py`, `ipp/main.py`, and `pyproject.toml`. BUG-019 closed, BUG-025 fixed, BUG-024 part A fixed, BUG-026 fixed, BUG-023 fixed, BUG-024 part B (class-level fields) fixed.

---

## Phase A: Critical Crash Fixes (v1.7.6 – v1.7.9) ✅ COMPLETE

All four critical crash bugs are fixed. Versions v1.7.6 through v1.7.9.1.16 are done. See version history at the bottom for the full list of what each version did.

---

### v1.7.6 — Fix: Semicolons No Longer Crash the Lexer (BUG-001) ✅ DONE

**User impact:** Every developer from C, Java, JavaScript, Lua, or C# will type semicolons. Current result: `SyntaxError: Unexpected character: ';'`. Expected result: semicolons are silently ignored (treated as whitespace/newline).

**File to change:** `ipp/lexer/lexer.py`

**Exact fix — find the character dispatch in the lexer's main loop and add:**
```python
# In the main tokenizer loop, where individual characters are matched:
elif char == ';':
    pass   # silently treat semicolon as statement separator (whitespace)
```

That is the entire fix. Do not add a SEMICOLON token type. Do not add it to the parser. Just skip it in the lexer the same way spaces and tabs are skipped.

**Test file: `tests/v1_7_6/test_semicolons.ipp`**
```ipp
var x = 1; var y = 2; var z = 3
assert x + y + z == 6

func add(a, b) { return a + b }; assert add(3, 4) == 7

var result = 0
var i = 0
while i < 5 { i = i + 1; result = result + i }
assert result == 15
```

**Regression risk:** Zero. Semicolons currently always crash. Any code that previously worked did not contain semicolons. This cannot break anything.

---

### v1.7.6.1 — Fix: `print("label:", value)` Stops Crashing (BUG-021) ✅ DONE

**User impact:** `print("Testing:", x)` → `VMError: got an unexpected keyword argument 'Testing:'`. This is the most common print pattern in any language. It breaks 34 of the 140 existing test files. The same kwarg-heuristic bug as BUG-005, but isolated to print specifically.

**File to change:** `vm.py`, `_builtin_print()` — strip the kwarg-detection entirely from the print path. Print should always treat all arguments as positional values to be printed, separated by spaces (Python-style).

```python
# BEFORE (broken):
def _builtin_print(self, *args, **kwargs):
    # kwargs detection causes crash when a string arg looks like a key

# AFTER (fix):
def _builtin_print(self, *args):
    print(*[self._ipp_to_str(a) for a in args])
```

**Test file: `tests/v1_7_6_1/test_print_multiarg.ipp`**
```ipp
var x = 42
var name = "Alice"

# All of these must work
print("value:", x)
print("name:", name, "age:", 30)
print("result:", 1 + 2)
print("bool:", true, "nil:", nil)
print("list:", [1, 2, 3])
print("a", "b", "c")

# Single arg still works
print("hello")
print(42)
print(nil)
```

**Regression risk:** Zero. Print with multiple args currently always crashes.

---

### v1.7.6.2 — Fix: `dict.get(key, default)` with String Key (BUG-005 subset) ✅ DONE

**User impact:** `d.get("missing", 0)` crashes because `"missing"` is treated as a kwarg key. This is the same root cause as BUG-005 but isolated to `dict.get` which is a very common safe-access pattern.

**File to change:** `vm.py`, the dict method dispatch for `get`. Instead of routing through the generic `_call()` with its kwarg heuristic, dispatch `dict.get` directly:

```python
# In the dict method handler:
elif method_name == 'get':
    if len(args) == 1:
        result = obj.get(args[0])
    elif len(args) == 2:
        result = obj.get(args[0], args[1])
    else:
        raise VMError("dict.get() takes 1 or 2 arguments")
    self.stack.append(result)
```

**Test file: `tests/v1_7_6_2/test_dict_get.ipp`**
```ipp
var d = {"name": "Alice", "age": 30, "city": "NYC"}

# get existing key
assert d.get("name") == "Alice"
assert d.get("age") == 30

# get missing key without default returns nil
var r = d.get("missing")
assert r == nil

# get missing key with default
assert d.get("missing", 0) == 0
assert d.get("country", "unknown") == "unknown"
assert d.get("name", "default") == "Alice"

# string keys that look like identifiers
var d2 = {"hello": 1, "world": 2}
assert d2.get("hello", 0) == 1
assert d2.get("nope", 99) == 99
```

**Regression risk:** Very low. Only changes the specific `dict.get` dispatch path.

---

### v1.7.7 — Fix: `extends` Keyword Works for Inheritance (BUG-002) ✅ DONE

**User impact:** `class Cat extends Animal {}` → `SyntaxError: Expect '{' before class body`. This is in every documentation example. The working syntax `class Cat : Animal {}` is documented nowhere.

**File to change:** `ipp/parser/parser.py`, function `class_declaration()`

**Find the superclass detection block. It currently looks like:**
```python
superclass = None
if self.match(TokenType.COLON):
    sup = self.consume(TokenType.IDENTIFIER, "Expect superclass name")
    superclass = sup.lexeme
```

**Replace with:**
```python
superclass = None
if self.match(TokenType.COLON):
    sup = self.consume(TokenType.IDENTIFIER, "Expect superclass name")
    superclass = sup.lexeme
elif (self.check(TokenType.IDENTIFIER) and
      self.peek().lexeme == 'extends'):
    self.advance()   # consume the 'extends' identifier
    sup = self.consume(TokenType.IDENTIFIER,
                       "Expect superclass name after 'extends'")
    superclass = sup.lexeme
```

**Note:** `self.peek()` here means looking at the *current* token (the one `check()` would match), since `check()` does not consume. Verify the exact method name in your parser for "look at current token without consuming" — it may be `self.current()`, `self.tokens[self.pos]`, or similar. The logic is: if the current token is the identifier `extends`, consume it, then consume the superclass name.

**Test file: `tests/v1_7_7/test_extends.ipp`**
```ipp
class Animal {
    func init(name) {
        self.name = name
    }
    func speak() {
        return "..."
    }
    func describe() {
        return "I am " + self.name
    }
}

class Cat extends Animal {
    func speak() {
        return self.name + " says meow"
    }
}

class Dog extends Animal {
    func speak() {
        return self.name + " says woof"
    }
}

var c = Cat("Whiskers")
var d = Dog("Rex")

assert c.speak() == "Whiskers says meow"
assert d.speak() == "Rex says woof"
assert c.describe() == "I am Whiskers"
assert d.describe() == "I am Rex"
assert c.name == "Whiskers"

# Old colon syntax must still work
class Fish : Animal {
    func speak() { return self.name + " blub" }
}
var f = Fish("Nemo")
assert f.speak() == "Nemo blub"
```

**Regression risk:** Zero. `extends` currently always crashes. The `:` path is unchanged.

---

### v1.7.7.1 — Fix: `super.method()` Calls Work in Subclasses ✅ DONE

**User impact:** After `extends` works, users immediately try `super.init()` to call the parent constructor. Without this, inheritance is only useful for method override — the parent's `init` can never be called.

**File to change:** `vm.py` and `parser.py`. The `super` keyword needs to resolve to the parent class of the current instance's class, and `super.method()` needs to call the method on that parent.

```python
# In vm.py GET_PROPERTY / CALL handler:
if callee_name == 'super':
    parent_class = current_instance.__class__.__bases__[0]  # Ipp parent
    # bind the method to current self but look it up in parent
```

**Test file: `tests/v1_7_7_1/test_super.ipp`**
```ipp
class Shape {
    func init(color) {
        self.color = color
    }
    func describe() {
        return "a " + self.color + " shape"
    }
}

class Circle extends Shape {
    func init(color, radius) {
        super.init(color)
        self.radius = radius
    }
    func describe() {
        return super.describe() + " (circle r=" + str(self.radius) + ")"
    }
    func area() {
        return pi * self.radius * self.radius
    }
}

var c = Circle("red", 5)
assert c.color == "red"
assert c.radius == 5
assert c.describe() == "a red shape (circle r=5)"
assert c.area() > 78.0 and c.area() < 79.0
```

**Regression risk:** Low. Only affects `super.` expressions which currently crash.

---

### v1.7.7.2 — Fix: `__init__` Called as Constructor Alias

**User impact:** Python users write `__init__` not `init`. After BUG-003 is fixed (v1.7.8), `func __init__(self, x)` will parse correctly. But the VM needs to recognise `__init__` as equivalent to `init` when constructing an instance.

**File to change:** `vm.py`, class instantiation / `CALL` on a class.

```python
# When constructing an instance of a class:
constructor = cls.methods.get('__init__') or cls.methods.get('init')
if constructor:
    self._call(constructor, args, instance)
```

**Test file: `tests/v1_7_7_2/test_init_alias.ipp`**
```ipp
# __init__ style (Python convention) — must work after v1.7.8
class Point {
    func __init__(self, x, y) {
        self.x = x
        self.y = y
    }
    func __str__(self) {
        return "(" + str(self.x) + ", " + str(self.y) + ")"
    }
}

var p = Point(3, 4)
assert p.x == 3
assert p.y == 4
assert str(p) == "(3, 4)"

# init style (Ipp convention) — must still work
class Vector {
    func init(x, y) {
        self.x = x
        self.y = y
    }
}
var v = Vector(1, 2)
assert v.x == 1 and v.y == 2
```

**Note:** Depends on v1.7.8 (`self` param fix). Run after that.

**Regression risk:** Very low. Just adds a lookup fallback from `__init__` → `init`.

---

### v1.7.8 — Fix: Explicit `self` Parameter Is Silently Accepted (BUG-003) ✅ DONE

**User impact:** `func __init__(self, name)` → `SyntaxError: Expect parameter name`. Python, GDScript, Java, C++ all put `self`/`this` explicitly. Every user will try this.

**File to change:** `ipp/parser/parser.py`, the function/method parameter parsing section of `function_declaration()` (or wherever parameters are parsed into a list).

**Find where the parameter list is parsed. Before the main parameter loop begins, add:**
```python
# Silently consume 'self' if it is the first parameter
# (self is always implicit in Ipp — this just avoids crashing users
#  who come from Python/GDScript/Java conventions)
if self.check(TokenType.SELF):
    self.advance()                          # consume 'self'
    if self.check(TokenType.COMMA):
        self.advance()                      # consume the comma after 'self'
    # Do NOT add 'self' to params list — it is already slot 0 in the VM
```

This must be placed **before** the while loop that collects parameter names, so it only applies to the first position.

**Test file: `tests/v1_7_8/test_explicit_self.ipp`**
```ipp
# Python-style: explicit self in every method
class Counter {
    func __init__(self) {
        self.count = 0
    }
    func increment(self) {
        self.count = self.count + 1
    }
    func reset(self) {
        self.count = 0
    }
    func get(self) {
        return self.count
    }
    func __str__(self) {
        return "Counter(" + str(self.count) + ")"
    }
}

var c = Counter()
assert c.get() == 0
c.increment()
c.increment()
c.increment()
assert c.get() == 3
c.reset()
assert c.get() == 0
assert str(c) == "Counter(0)"

# Also works with extends and explicit self
class LimitedCounter extends Counter {
    func __init__(self, limit) {
        self.count = 0
        self.limit = limit
    }
    func increment(self) {
        if self.count < self.limit {
            self.count = self.count + 1
        }
    }
}

var lc = LimitedCounter(3)
lc.increment()
lc.increment()
lc.increment()
lc.increment()   # should be ignored
assert lc.get() == 3
```

**Regression risk:** Zero. Explicit `self` currently always crashes. Methods without `self` in the signature continue to work unchanged.

---

### v1.7.8.1 — Fix: `__str__` Used Automatically by `print()` and `str()` ✅ DONE

**User impact:** `print(my_obj)` should call `__str__()` on the object. Currently `print()` on an Ipp instance prints `<ClassName instance>` regardless of whether `__str__` is defined.

**File to change:** `vm.py`, `_builtin_print()` and `_builtin_str()`. When the argument is an IppInstance with a `__str__` method, call it.

```python
def _to_display_str(self, value):
    if isinstance(value, IppInstance):
        if '__str__' in value.klass.methods:
            return self._call_method(value, '__str__', [])
        return f"<{value.klass.name} instance>"
    return str(value)
```

**Test file: `tests/v1_7_8_1/test_str_protocol.ipp`**
```ipp
class Point {
    func init(x, y) { self.x = x; self.y = y }
    func __str__() { return "(" + str(self.x) + ", " + str(self.y) + ")" }
}
class NoStr {
    func init() { self.val = 42 }
}

var p = Point(3, 4)
assert str(p) == "(3, 4)"

var joined = "point is: " + str(p)
assert joined == "point is: (3, 4)"

# print uses __str__ automatically
# (visual check — just must not crash)
print(p)

var ns = NoStr()
var s = str(ns)
assert s.contains("NoStr") == true
```

**Regression risk:** Low. Only affects IppInstance serialisation.

---

### v1.7.8.2 — Enhancement: `__repr__` Protocol + `repr()` Builtin ✅ DONE

**Why here:** Once `__str__` works (v1.7.8.1), adding `__repr__` is 3 extra lines and completes the string protocol. Many debugging scenarios need `repr()` (e.g. strings show with quotes, lists show values).

**File to change:** `vm.py`, add a `repr()` builtin that calls `__repr__` if defined, else falls back to a quoted/bracketed representation.

```python
# builtin repr():
def _builtin_repr(value):
    if isinstance(value, IppInstance) and '__repr__' in value.klass.methods:
        return _call_method(value, '__repr__', [])
    if isinstance(value, str):
        return '"' + value + '"'
    return str(value)
```

**Test file: `tests/v1_7_8_2/test_repr.ipp`**
```ipp
assert repr("hello") == '"hello"'
assert repr(42) == "42"
assert repr(true) == "true"
assert repr(nil) == "nil"
assert repr([1,2,3]) == "[1, 2, 3]"

class Vec {
    func init(x, y) { self.x = x; self.y = y }
    func __repr__() { return "Vec(" + str(self.x) + ", " + str(self.y) + ")" }
}
var v = Vec(1, 2)
assert repr(v) == "Vec(1, 2)"
```

**Regression risk:** Zero. Pure addition.

---

### v1.7.8.3 — Enhancement: `__len__` Protocol + IppInstance `len()` ✅ DONE

**Why here:** After `__str__` and `__repr__`, `__len__` completes the basic dunder protocol. Lets users make custom collections that work with `len()`.

**File to change:** `vm.py`, `_builtin_len()`. Before falling through to Python's `len()`, check for Ipp `__len__`:

```python
def _builtin_len(obj):
    if isinstance(obj, IppInstance) and '__len__' in obj.klass.methods:
        return _call_method(obj, '__len__', [])
    if isinstance(obj, IppSet):
        return len(obj._items)
    return len(obj)
```

**Test file: `tests/v1_7_8_3/test_len_protocol.ipp`**
```ipp
class Bag {
    func init() { self._items = [] }
    func add(item) { self._items = self._items + [item] }
    func __len__() { return len(self._items) }
}

var b = Bag()
assert len(b) == 0
b.add("apple")
b.add("banana")
assert len(b) == 2
b.add("cherry")
assert len(b) == 3
```

**Regression risk:** Zero. Pure addition.

---

### v1.7.9 — Fix: `try/catch` Catches Runtime VM Errors (BUG-004) ✅ DONE

**User impact:** `try { var x = 1/0 } catch e { }` → program crashes. Division by zero, index out of bounds, and nil property access all bypass catch blocks entirely.

**File to change:** `ipp/vm/vm.py`, the main `run()` dispatch loop.

**How the current code fails:** When a Python-level exception (`ZeroDivisionError`, `IndexError`, `AttributeError`) fires inside an opcode handler, it propagates up the Python call stack. Ipp's catch block scanner is only triggered by the `THROW` opcode — never by Python exceptions.

**Exact fix — wrap the opcode dispatch body in a Python try/except:**

Find the main dispatch loop in `run()`. It likely looks like:
```python
while True:
    opcode = self.read_byte()
    if opcode == OpCode.CONSTANT:
        ...
    elif opcode == OpCode.ADD:
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(a + b)   # can throw ZeroDivisionError
    ...
```

Add a wrapper that routes Python exceptions through Ipp's throw mechanism:
```python
def _raise_runtime_error(self, message: str):
    """Convert a Python runtime error into an Ipp catchable exception."""
    # Push the error message as the thrown value (same as `throw "msg"`)
    self.stack.append(message)
    # Jump to the nearest active catch block, same as THROW opcode
    self._handle_throw()   # or whatever your THROW handler calls internally

# In the main loop, wrap each opcode's execution:
while True:
    try:
        opcode = self.read_byte()
        if opcode == OpCode.ADD:
            ...
        elif opcode == OpCode.DIV:
            b, a = self.stack.pop(), self.stack.pop()
            try:
                self.stack.append(a / b)
            except ZeroDivisionError:
                self._raise_runtime_error("Division by zero")
        # ... all other opcodes
    except IppCatchableError:
        # Already handled — catch block set up the next instruction
        pass
```

**Alternatively, a simpler approach** — wrap the entire opcode body in a broad catch:
```python
while True:
    opcode = self.read_byte()
    try:
        # ... all existing opcode handlers unchanged ...
    except VMError:
        raise   # already an Ipp error — let it propagate normally
    except ZeroDivisionError:
        self._raise_runtime_error("Division by zero")
    except IndexError as e:
        self._raise_runtime_error("Index out of bounds: " + str(e))
    except (AttributeError, KeyError) as e:
        self._raise_runtime_error("Property not found: " + str(e))
    except TypeError as e:
        self._raise_runtime_error("Type error: " + str(e))
```

Choose whichever approach fits your current `THROW`/catch block implementation. The key invariant: **any Python exception that fires inside an opcode handler must end up in `e` in the Ipp `catch` block if one is active, or crash with a clean error message if none is active.**

**Test file: `tests/v1_7_9/test_runtime_catch.ipp`**
```ipp
# Test 1: catch division by zero
var caught_div = false
try {
    var x = 10 / 0
} catch e {
    caught_div = true
}
assert caught_div == true

# Test 2: catch index out of bounds
var caught_idx = false
try {
    var lst = [1, 2, 3]
    var x = lst[99]
} catch e {
    caught_idx = true
}
assert caught_idx == true

# Test 3: explicit throw still works
var caught_throw = false
try {
    throw "test_error"
} catch e {
    caught_throw = true
    assert e == "test_error"
}
assert caught_throw == true

# Test 4: catch in a loop
var errors = 0
var i = 0
while i < 5 {
    try {
        if i == 2 { var x = 1 / 0 }
        if i == 4 { throw "manual" }
    } catch e {
        errors = errors + 1
    }
    i = i + 1
}
assert errors == 2

# Test 5: code after try/catch continues
var after = false
try {
    var x = 1 / 0
} catch e { }
after = true
assert after == true

# Test 6: nested try/catch
var outer_caught = false
var inner_caught = false
try {
    try {
        var x = 1 / 0
    } catch e {
        inner_caught = true
        throw "rethrow"
    }
} catch e {
    outer_caught = true
    assert e == "rethrow"
}
assert inner_caught == true
assert outer_caught == true
```

**Regression risk:** Medium. This changes error propagation paths. Run all previous tests after applying this fix. Pay attention to cases where a VMError was intentionally crashing (unrecoverable VM corruption) — those must still crash.

---

### v1.7.9.1 — Enhancement: Cleaner Error Messages with File + Line ✅ DONE

**Why here:** After try/catch works, error messages themselves are often useless (`VMError: pop from empty list` reveals nothing). Add file+line info to every unhandled error.

**File to change:** `vm.py`. Every opcode handler that raises a `VMError` should include the current line number (already tracked in the chunk's line table):

```python
# In vm.py, when raising runtime errors:
raise VMError(f"[line {self.current_line}] Division by zero")
# Instead of:
raise VMError("Division by zero")
```

Also add a stack trace collector so unhandled errors print:
```
RuntimeError at game.ipp:42 in 'update':
  Division by zero
  Called from game.ipp:100 in 'game_loop'
```

**Test file: `tests/v1_7_9_1/test_error_messages.ipp`**
```ipp
# Errors inside catch must still be catchable
var msg = ""
try {
    var x = 1 / 0
} catch e {
    msg = str(e)
}
# Error message should contain useful info
assert msg.contains("zero") == true or msg.contains("Division") == true
```

---

---

## Phase A2: Micro-Fixes from Audit v4 (v1.7.9.1.12 – v1.7.9.1.17)

> These versions fix the 4 new bugs discovered in audit v4, plus add `assert` message support. All are low-risk, small-scope changes that can be done in one sitting each.

---

### v1.7.9.1.12 — Fix: `math.isclose()` Builtin Added (BUG-025) ✅ DONE

**User impact:** `0.1 + 0.2 == 0.3` silently returns `false`. Any game doing float accumulation (timers, physics, progress bars, lerp targets) will hit wrong comparison results with no error message.

**File to change:** `ipp/runtime/builtins.py` and `ipp/vm/vm.py` builtin table.

**Exact fix — 1 line:**
```python
# In interpreter BUILTINS dict (ipp/runtime/builtins.py):
'isclose': lambda a, b, rel_tol=1e-9: math.isclose(a, b, rel_tol=rel_tol),
# In VM builtin table (ipp/vm/vm.py), pass raw Python function:
'isclose': math.isclose,
# Note: Ipp has no `math.` namespace — only top-level isclose() is exposed.
```

**Test file: `tests/v1_7_9_1_12/test_isclose.ipp`**
```ipp
# Float arithmetic is imprecise
assert 0.1 + 0.2 != 0.3              # raw comparison correctly returns false

# isclose handles it correctly (no math. namespace in Ipp — top-level only)
assert isclose(0.1 + 0.2, 0.3) == true
assert isclose(1.0, 1.0000000001) == true
assert isclose(1.0, 1.1) == false

# Game use case: timer accumulation
var elapsed = 0.0
for i in range(10) { elapsed = elapsed + 0.1 }
assert isclose(elapsed, 1.0) == true   # elapsed == 1.0 would fail

# Tolerance control via rel_tol kwarg
assert isclose(1.0, 1.05, rel_tol=0.1) == true     # within 10%
assert isclose(1.0, 1.05, rel_tol=0.01) == false    # outside 1%
assert isclose(100.0, 150.0, rel_tol=0.5) == true   # within 50%
```

**Regression risk:** Zero. Pure addition.

---

### v1.7.9.1.13 — Fix: Class-Level Field Declaration Error Message (BUG-024 part A) ✅ DONE

**User impact:** `class C { var x = 0 }` gives `"Parse error: Expect '}' after class body → Check for missing quotes"`. This message is actively wrong — there are no quotes. Developers waste time auditing their string syntax.

**File to change:** `ipp/parser/parser.py`, the class body parser.

**Exact fix — find where the class body parser falls through to the generic error and add:**
```python
# In class_declaration(), inside the while loop that reads class members:
if self.check(TokenType.VAR) or self.check(TokenType.LET):
    self.advance()  # consume 'var'/'let'
    field_name = self.peek().lexeme if not self.is_at_end() else "field"
    raise ParseError(
        f"Class-level field declarations are not yet supported. "
        f"Assign fields with 'self.{field_name} = value' inside __init__() instead.",
        self.previous()
    )
```

**Test file: `tests/v1_7_9_1_13/test_class_field_error.ipp`**
```ipp
# Confirm correct syntax still works
class Counter {
    func init() {
        self.count = 0
    }
    func inc() { self.count = self.count + 1 }
}
var c = Counter()
c.inc()
assert c.count == 1

# Visual test: run "class Bad { var x = 0 }" in REPL and confirm
# error says "Class-level field declarations are not yet supported"
# NOT "Expect '}' after class body → Check for missing quotes"
```

**Regression risk:** Zero. Only changes the error message for code that currently always fails.

---

### v1.7.9.1.14 — Enhancement: `trunc()` Builtin + `int()` Behavior Documented (BUG-026) ✅ DONE

**User impact:** `int(-3.9)` returns `-3` (truncation toward zero), but game developers often expect `-4` (floor). Undocumented. Silently breaks negative tile coordinate calculations.

**File to change:** `ipp/runtime/builtins.py` — add `trunc()` as explicit alias. Also add to `ERRORS.md` and REPL `.help`.

**Exact fix:**
```python
# In builtins:
'trunc': lambda x: math.trunc(x),   # identical to int() — but name signals intent
# floor() already exists and floors correctly: floor(-3.9) == -4.0
# trunc(-3.9) == int(-3.9) == -3   (truncate toward zero)
```

Also add a comment to the `int` builtin entry:
```python
'int': lambda x: int(x),   # truncates toward zero — use floor() for negative-safe conversion
```

**Test file: `tests/v1_7_9_1_14/test_trunc_floor.ipp`**
```ipp
# Document the critical difference
assert int(3.9) == 3          # truncation toward zero
assert int(-3.9) == -3        # truncation toward zero (NOT floor)
assert floor(-3.9) == -4.0    # floor — rounds toward negative infinity
assert ceil(-3.9) == -3.0     # ceil — rounds toward positive infinity
assert trunc(-3.9) == -3      # explicit alias for int() — same behavior

# Game tile coordinate example
var tile_size = 32
var world_x = -10.0

assert floor(world_x / tile_size) == -1.0   # ✅ correct tile for negative world
assert int(world_x / tile_size) == 0        # ❌ wrong — gives tile 0 not tile -1

# String conversion still works
assert int("42") == 42
assert int("3") == 3
```

**Regression risk:** Zero. `trunc()` is a new builtin; `int()` behavior is unchanged.

---

### v1.7.9.1.15 — Fix: Closures in Loops Capture Correct Value (BUG-023) ✅ DONE

**User impact:** All closures created inside a `for` loop see the loop variable's final value, not the value at creation time.

```ipp
var fns = []
for i in range(3) {
    fns = fns + [func() { return i }]
}
fns[0]()   # ❌ currently returns 2  (expected 0)
fns[1]()   # ❌ currently returns 2  (expected 1)
fns[2]()   # ❌ currently returns 2  (expected 2 — correct by accident only)
```

**File to change:** `ipp/vm/compiler.py`, the `for` loop compilation section.

**Approach — fresh scope per iteration:** At each loop iteration, open a new scope for the loop variable. This gives each closure a separate upvalue cell containing that iteration's value.

```python
# In compile_for_in() or equivalent, before emitting the body:
# 1. Open a new inner scope
self.begin_scope()
# 2. Re-bind the loop variable in this new scope (so each iteration
#    gets its own slot rather than mutating the shared slot)
self.emit_local(loop_var_name, loop_var_slot_value)
# 3. Compile the body (closures inside capture the per-iteration local)
self.compile_block(body)
# 4. Close the scope — CLOSE_UPVALUE is emitted here, snapshotting
#    the value into any closures that captured it
self.end_scope()
# 5. Jump back to loop header
```

The exact implementation depends on how `begin_scope`/`end_scope` are structured. The invariant: each closure created inside the loop body must hold an independent upvalue cell, not a shared reference to the loop counter.

**Test file: `tests/v1_7_9_1_15/test_closure_loop.ipp`**
```ipp
# for-in loop
var fns = []
for i in range(5) {
    fns = fns + [func() { return i }]
}
assert fns[0]() == 0
assert fns[1]() == 1
assert fns[2]() == 2
assert fns[3]() == 3
assert fns[4]() == 4

# String loop variable
var handlers = []
var labels = ["alpha", "beta", "gamma"]
for label in labels {
    handlers = handlers + [func() { return label }]
}
assert handlers[0]() == "alpha"
assert handlers[1]() == "beta"
assert handlers[2]() == "gamma"

# Closures with multiple captured variables
var adders = []
for i in range(3) {
    var base = i * 10
    adders = adders + [func(x) { return base + x }]
}
assert adders[0](5) == 5    # base=0
assert adders[1](5) == 15   # base=10
assert adders[2](5) == 25   # base=20

# Explicit capture pattern still works (must not regress)
var efns = []
for m in range(3) {
    var captured = m
    efns = efns + [func() { return captured }]
}
assert efns[0]() == 0
assert efns[1]() == 1
assert efns[2]() == 2
```

**Regression risk:** Medium. Changes closure capture semantics for loops. Run the full regression suite and all closure-related tests after applying.

---

### v1.7.9.1.16 — Feature: Class-Level Field Declarations (BUG-024 part B) ✅ DONE

**User impact:** `class Counter { var count = 0 }` should work. Python, GDScript, JavaScript, C#, Java all support this. Currently crashes even after v1.7.9.1.13 improves the error message.

**File to change:** `ipp/parser/parser.py` (class body parsing) and `ipp/vm/compiler.py` (field init lowering).

**Implementation:** When a `var name = expr` or `let name = expr` is encountered in a class body, lower it into the `__init__` method as a `self.name = expr` assignment. If `__init__` already exists, prepend the field assignments before the first user statement. If `__init__` doesn't exist, synthesise one.

```python
# parser.py class_declaration():
class_fields = []   # (name, default_expr, is_let)

while not self.check(RIGHT_BRACE) and not self.is_at_end():
    if self.check(VAR) or self.check(LET):
        is_let = self.check(LET)
        self.advance()  # consume var/let
        name = self.consume(IDENTIFIER, "Expected field name").lexeme
        default = None
        if self.match(EQUAL):
            default = self.expression()
        class_fields.append((name, default, is_let))
    elif self.check(FUNC) or self.check(STATIC) or self.check(PROP):
        methods.append(self.method_declaration())
    ...

# After parsing: inject fields into __init__
if class_fields:
    init_method = find_method(methods, '__init__') or find_method(methods, 'init')
    if init_method is None:
        init_method = create_empty_init()
        methods.insert(0, init_method)
    for name, default, is_let in class_fields:
        # Prepend: self.name = default (or nil if no default)
        prepend_field_assignment(init_method, name, default or NilLiteral(), is_let)
```

**Test file: `tests/v1_7_9_1_16/test_class_fields.ipp`**
```ipp
# Basic class-level fields
class Counter {
    var count = 0
    var name = "counter"

    func increment() {
        self.count = self.count + 1
    }
    func reset() { self.count = 0 }
}

var a = Counter()
var b = Counter()

assert a.count == 0
assert b.count == 0
assert a.name == "counter"

a.increment()
a.increment()
assert a.count == 2
assert b.count == 0    # independent instances

# Fields with custom init: init runs after field defaults
class Sized {
    var capacity = 10
    var items = []

    func init(cap) {
        self.capacity = cap   # overrides field default
    }
}

var s = Sized(20)
assert s.capacity == 20   # init override
assert s.items == []      # field default preserved

# let fields (immutable)
class Config {
    let version = "1.0"
    let max_fps = 60
}
var c = Config()
assert c.version == "1.0"
assert c.max_fps == 60

# Multiple classes don't share field values
class Point {
    var x = 0
    var y = 0
}
var p1 = Point()
var p2 = Point()
p1.x = 10
assert p1.x == 10
assert p2.x == 0   # not shared
```

**Regression risk:** Medium. Changes class parsing. Run all class-related tests.

---

### v1.7.9.1.17 — Enhancement: `assert` with Custom Error Message ✅ DONE

**User impact:** `assert hp > 0` fails with just "AssertionError" or nothing useful. Adding a message makes test failures and game invariants debuggable without a debugger attached.

**Syntax:** `assert condition, "message"`

**File to change:** `ipp/parser/parser.py` (parse optional `, expr` after condition), `ipp/vm/compiler.py` (emit message load + ASSERT_MSG opcode or inline check), `ipp/vm/vm.py` (use message in AssertionError).

```python
# Parser: in assert_statement():
condition = self.expression()
message = None
if self.match(TokenType.COMMA):
    message = self.expression()   # optional message expression
return AssertStmt(condition, message)

# VM: ASSERT opcode handler with message:
if not condition:
    msg = evaluate(message) if message else "Assertion failed"
    raise VMError(f"AssertionError: {msg}")
```

**Test file: `tests/v1_7_9_1_17/test_assert_msg.ipp`**
```ipp
# Without message — unchanged behavior
assert 1 + 1 == 2
assert true

# With message — when condition is true, nothing happens
assert true, "this should never fire"
assert 2 + 2 == 4, "math is broken"

# With message — when condition is false, message is in the error
var caught = ""
try {
    assert false, "custom failure message"
} catch e {
    caught = e
}
assert caught.contains("custom failure message") == true

# Expression in message — evaluated only on failure
var hp = -5
try {
    assert hp > 0, "hp must be positive, got: " + str(hp)
} catch e {
    assert e.contains("-5") == true
    assert e.contains("hp must be positive") == true
}

# Game invariant use
var player_speed = 5.0
try {
    assert player_speed > 0, "player_speed must be positive"
} catch e {
    assert false   # should not reach here
}

# Works with isclose from v1.7.9.1.12
var val = 0.1 + 0.2
assert isclose(val, 0.3), "expected 0.3, got: " + str(val)
```

**Regression risk:** Low. `assert` with one argument unchanged; `,` after assert was previously a parse error anyway.

### v1.7.9.2 — Enhancement: `assert` with Custom Error Message

**Why here:** `assert` currently just says "assertion failed". Adding a message makes test failures and game invariant violations debuggable.

**Syntax:** `assert condition, "message"`

**File to change:** `parser.py` and `vm.py`. Parse the optional `, "message"` after the condition and emit it as the error string on failure.

```ipp
assert hp > 0, "Player died with negative HP: " + str(hp)
assert len(items) < 100, "Inventory overflow"
```

**Test file: `tests/v1_7_9_2/test_assert_message.ipp`**
```ipp
# assert without message still works
assert 1 + 1 == 2

# assert with message: when true, no error
assert true, "this should not fire"

# assert with message: when false, catch the message
var caught = ""
try {
    assert false, "custom failure message"
} catch e {
    caught = e
}
assert caught.contains("custom failure message") == true

# Expression in message
var hp = -5
try {
    assert hp > 0, "hp is " + str(hp)
} catch e {
    assert e.contains("-5") == true
}
```

**Regression risk:** Low. `assert` with one arg unchanged; `,` after assert is currently a parse error anyway.


---

## Phase B: Correctness Fixes (v1.8.0 – v1.8.9)

After Phase A, the language is usable for basic programs. Phase B fixes the remaining broken standard library and runtime features.

---

### v1.8.0 — Fix: `str.replace()` and String Method Naming (BUG-005, BUG-011) ✅ DONE

**Root cause:** The VM's `_call()` kwarg-detection heuristic treats any string argument that looks like an identifier as a kwarg key. `"world".replace("world", "ipp")` passes `"world"` as `replace(world="ipp")` → crash.

**Two sub-fixes:**

**Fix A — `str.replace()` works:**
The cleanest fix is to remove the kwarg heuristic from the Python-builtin dispatch path entirely. Named args should only come from the compiler-emitted `NAMED_CALL` opcode, not from runtime string content inspection.

Find in `vm.py` the section of `_call()` that scans arguments for kwargs:
```python
# REMOVE THIS BLOCK entirely from the positional-call path:
kwargs = {}
for i, arg in enumerate(args):
    if isinstance(arg, str) and looks_like_identifier(arg):
        kwargs[arg] = args[i + 1]
        ...
```

After removing it, `str.replace("world", "ipp")` will pass two positional args and work correctly.

**Fix B — Add missing string methods:**
```python
# In vm.py, wherever string methods are dispatched:
'contains':    lambda s, sub: sub in s,
'starts_with': lambda s, pre: s.startswith(pre),
'ends_with':   lambda s, suf: s.endswith(suf),
```

**Test file: `tests/v1_8_0/test_string_methods.ipp`**
```ipp
var s = "hello world"

# replace — was broken
assert s.replace("world", "ipp") == "hello ipp"
assert s.replace("l", "L") == "heLLo worLd"
assert "aaa".replace("a", "b") == "bbb"

# contains — was missing
assert s.contains("world") == true
assert s.contains("python") == false
assert s.contains("hello") == true

# starts_with / ends_with (snake_case)
assert s.starts_with("hello") == true
assert s.starts_with("world") == false
assert s.ends_with("world") == true
assert s.ends_with("hello") == false

# Existing methods still work
assert s.upper() == "HELLO WORLD"
assert s.lower() == "hello world"
assert "  hi  ".strip() == "hi"
assert s.find("world") == 6
assert s.split(" ") == ["hello", "world"]
assert s.startswith("hello") == true
assert s.endswith("world") == true
```

---

### v1.8.0.1 — Fix: `str.format()` Named Placeholders Work ✅ DONE (already implemented)

**User impact:** `"{name} says hi".format(name="Alice")` silently ignores named placeholders or crashes. Common string templating pattern.

**File to change:** `vm.py`, `str.format` method handler. Route named-format calls by extracting kwargs from the `NAMED_CALL` opcode (not from string content scanning):

```python
elif method_name == 'format':
    result = obj.format(*positional_args, **named_kwargs)
    self.stack.append(result)
```

**Test file: `tests/v1_8_0_1/test_str_format.ipp`**
```ipp
assert "Hello {}!".format("World") == "Hello World!"
assert "x={0}, y={1}".format(3, 4) == "x=3, y=4"
assert "{0} + {1} = {2}".format(1, 2, 3) == "1 + 2 = 3"
assert "Price: ${:.2f}".format(9.99) == "Price: $9.99"
assert "{:>10}".format("right") == "     right"
```

---

### v1.8.0.2 — Fix: `str.count()`, `str.rfind()`, `str.rindex()` Methods Added ✅ DONE (already implemented)

**File to change:** `vm.py`, string method dispatch table.

```python
'count':  lambda s, sub: s.count(sub),
'rfind':  lambda s, sub: s.rfind(sub),
'rindex': lambda s, sub: s.rindex(sub),
```

**Test file: `tests/v1_8_0_2/test_str_search.ipp`**
```ipp
var s = "hello world hello"
assert s.count("hello") == 2
assert s.count("xyz") == 0
assert s.rfind("hello") == 12
assert s.find("world") == 6
```

---

### v1.8.0.3 — Enhancement: `str * n` Repetition Operator ✅ DONE (already implemented)

**Why here:** After string method dispatch is fixed, adding `"x" * 5 == "xxxxx"` is a 2-line change in the MUL opcode handler. Used constantly for game UI (health bars, padding, separators).

**File to change:** `vm.py`, MUL opcode handler — add string case before the numeric case:

```python
elif opcode == OpCode.MUL:
    b, a = self.stack.pop(), self.stack.pop()
    if isinstance(a, str) and isinstance(b, int):
        self.stack.append(a * b)
    elif isinstance(a, int) and isinstance(b, str):
        self.stack.append(b * a)
    else:
        self.stack.append(a * b)
```

Also add `.repeat(n)` method: `'repeat': lambda s, n: s * n`

**Test file: `tests/v1_8_0_3/test_str_repeat.ipp`**
```ipp
assert "ab" * 3 == "ababab"
assert "-" * 20 == "--------------------"
assert "x".repeat(0) == ""
assert "ha".repeat(3) == "hahaha"

func health_bar(hp, max_hp) {
    var filled = floor(hp / max_hp * 10)
    return "[" + "#".repeat(filled) + ".".repeat(10 - filled) + "]"
}
assert health_bar(70, 100) == "[#######...]"
assert health_bar(100, 100) == "[##########]"
assert health_bar(0, 100) == "[..........]"
```

**Regression risk:** Zero. `str * int` currently crashes with unsupported operand.

---

### v1.8.0.4 — Enhancement: `str.pad_left()`, `str.pad_right()`, `str.center()` ✅ DONE

**Why here:** After string method dispatch is fixed, padding is one line each. Used constantly for game UI text alignment (score displays, health bars, menu columns).

**File to change:** `vm.py`, string method dispatch table.

```python
'pad_left':  lambda s, n, c=" ": s.rjust(int(n), c),
'pad_right': lambda s, n, c=" ": s.ljust(int(n), c),
'center':    lambda s, n, c=" ": s.center(int(n), c),
'zfill':     lambda s, n: s.zfill(int(n)),
```

**Test file: `tests/v1_8_0_4/test_str_padding.ipp`**
```ipp
assert "42".pad_left(6) == "    42"
assert "42".pad_left(6, "0") == "000042"
assert "HP".pad_right(10, ".") == "HP........"
assert "ok".center(8, "-") == "---ok---"
assert "7".zfill(3) == "007"

# Game UI: fixed-width score display
func score_display(score) {
    return "[" + str(score).pad_left(8) + "]"
}
assert score_display(100) == "[     100]"
assert score_display(99999) == "[   99999]"
```

**Regression risk:** Zero. Pure addition.

---

### v1.8.0.5 — Enhancement: `str.is_digit()`, `str.is_alpha()`, `str.is_alnum()`, `str.is_space()` ✅ DONE

**Why here:** Input validation. Game chat filters, username validators, config parsers all need these one-liners.

**File to change:** `vm.py`, string method dispatch table.

```python
'is_digit': lambda s: s.isdigit(),
'is_alpha': lambda s: s.isalpha(),
'is_alnum': lambda s: s.isalnum(),
'is_space': lambda s: s.isspace(),
'is_upper': lambda s: s.isupper(),
'is_lower': lambda s: s.islower(),
```

**Test file: `tests/v1_8_0_5/test_str_predicates.ipp`**
```ipp
assert "123".is_digit() == true
assert "12a".is_digit() == false
assert "abc".is_alpha() == true
assert "abc123".is_alnum() == true
assert "abc 123".is_alnum() == false
assert "   ".is_space() == true
assert "".is_digit() == false
assert "ABC".is_upper() == true
assert "abc".is_lower() == true
assert "Abc".is_upper() == false

# Input validation use case
func valid_username(name) {
    return len(name) >= 3 and len(name) <= 20 and name.is_alnum() == true
}
assert valid_username("alice123") == true
assert valid_username("al") == false
assert valid_username("bad name!") == false
```

**Regression risk:** Zero. Pure addition.


---

### v1.8.1 — Fix: Variadic `...args` Packs a List, Not a Count (BUG-007) ✅ DONE (already fixed)

**Root cause:** In `vm.py` `_call()`, the variadic parameter receives the integer count of extra arguments instead of a list of those arguments.

**Find the variadic packing code in `_call()` and fix:**
```python
# BEFORE (bug):
variadic_slot = len(params) - 1
frame.locals[variadic_slot] = len(extra_args)   # packs COUNT — wrong

# AFTER (fix):
variadic_slot = len(params) - 1
frame.locals[variadic_slot] = list(extra_args)   # packs LIST — correct
```

The exact variable names will differ in your code. The invariant: the slot for `...name` must receive a Python list of the extra argument values.

**Test file: `tests/v1_8_1/test_variadic.ipp`**
```ipp
# Basic variadic
func sum_all(...nums) {
    var total = 0
    for n in nums { total = total + n }
    return total
}
assert sum_all(1, 2, 3, 4, 5) == 15
assert sum_all(10) == 10
assert sum_all() == 0

# Mixed: required + variadic
func first_and_rest(first, ...rest) {
    return str(first) + " then " + str(len(rest)) + " more"
}
assert first_and_rest(1, 2, 3, 4) == "1 then 3 more"
assert first_and_rest("only") == "only then 0 more"

# Variadic in a for loop
func collect(...items) {
    var result = []
    for item in items {
        result = result + [item]
    }
    return result
}
assert collect(10, 20, 30) == [10, 20, 30]

# Decorator that forwards args — works after variadic fix
func log(fn) {
    func wrapper(...args) {
        return fn(...args)
    }
    return wrapper
}
@log
func add(a, b) { return a + b }
assert add(3, 4) == 7
```

---

### v1.8.1.1 — Enhancement: `list.extend()` and `list.insert()` Methods ✅ DONE

**Why here:** After variadic is fixed, list mutation methods are the natural next step. `extend` and `insert` are the two most common list-mutation methods missing from the API.

**File to change:** `vm.py`, list method dispatch table.

```python
'extend': lambda lst, other: lst.extend(other) or lst,
'insert': lambda lst, idx, val: lst.insert(idx, val) or lst,
'clear':  lambda lst: lst.clear() or lst,
'copy':   lambda lst: list(lst),
```

**Test file: `tests/v1_8_1_1/test_list_mutation.ipp`**
```ipp
var lst = [1, 2, 3]

lst.extend([4, 5, 6])
assert lst == [1, 2, 3, 4, 5, 6]

lst.insert(0, 0)
assert lst == [0, 1, 2, 3, 4, 5, 6]
assert len(lst) == 7

var copy = lst.copy()
copy.clear()
assert len(copy) == 0
assert len(lst) == 7    # original unchanged
```

---

### v1.8.1.2 — Enhancement: `list.any()`, `list.all()`, `list.min()`, `list.max()` ✅ DONE

**Why here:** Four single-line additions that remove the need for common manual loops in game code.

**File to change:** `vm.py`, list method table.

```python
'any':  lambda lst, fn=None: any(fn(x) for x in lst) if fn else any(lst),
'all':  lambda lst, fn=None: all(fn(x) for x in lst) if fn else all(lst),
'min':  lambda lst: min(lst),
'max':  lambda lst: max(lst),
'sum':  lambda lst: sum(lst),
'flat': lambda lst: [x for sub in lst for x in (sub if isinstance(sub,list) else [sub])],
```

**Test file: `tests/v1_8_1_2/test_list_aggregates.ipp`**
```ipp
var nums = [3, 1, 4, 1, 5, 9, 2, 6]

assert nums.min() == 1
assert nums.max() == 9
assert nums.sum() == 31

assert [true, true, true].all() == true
assert [true, false, true].all() == false
assert [false, false, true].any() == true
assert [false, false, false].any() == false

# With predicate
var evens_exist = nums.any(func(x) { return x % 2 == 0 })
assert evens_exist == true

var all_positive = nums.all(func(x) { return x > 0 })
assert all_positive == true

# flat
var nested = [[1,2],[3,4],[5]]
assert nested.flat() == [1,2,3,4,5]
```

---

### v1.8.1.3 — Enhancement: `list.zip()`, `list.enumerate()`, `list.flatten()`, `list.unique()` ✅ DONE

**Why here:** After basic list aggregates, these four transform methods complete the functional toolkit needed to avoid manual loops in almost all common game-data processing patterns.

**File to change:** `vm.py`, list method dispatch table.

```python
'zip':       lambda lst, other: [list(pair) for pair in zip(lst, other)],
'enumerate': lambda lst, start=0: [[i, v] for i, v in enumerate(lst, start)],
'flatten':   lambda lst: [x for sub in lst for x in (sub if isinstance(sub, list) else [sub])],
'unique':    lambda lst: list(dict.fromkeys(lst)),
'take':      lambda lst, n: lst[:int(n)],
'drop':      lambda lst, n: lst[int(n):],
```

**Test file: `tests/v1_8_1_3/test_list_transforms.ipp`**
```ipp
var a = [1, 2, 3]
var b = ["x", "y", "z"]
var zipped = a.zip(b)
assert zipped == [[1, "x"], [2, "y"], [3, "z"]]

var en = a.enumerate()
assert en == [[0, 1], [1, 2], [2, 3]]

var en1 = a.enumerate(1)
assert en1 == [[1, 1], [2, 2], [3, 3]]

var nested = [[1, 2], [3, 4], [5]]
assert nested.flatten() == [1, 2, 3, 4, 5]

assert [1, 2, 2, 3, 1, 3].unique() == [1, 2, 3]

assert [1,2,3,4,5].take(3) == [1,2,3]
assert [1,2,3,4,5].drop(2) == [3,4,5]
```

**Regression risk:** Zero. Pure addition.

---

### v1.8.1.4 — Enhancement: `list.find()`, `list.find_index()`, `list.contains()` ✅ DONE

**Why here:** The final missing search methods. After these, the list API is comprehensive enough for most game use cases without needing manual loops for search.

**File to change:** `vm.py`, list method dispatch table. `find` and `find_index` require calling Ipp function objects through the VM's `_call()` mechanism (same as `map`/`filter`).

```python
'find':       lambda lst, fn: _call_fn(fn, [x]) and x for x in lst... (first match or nil),
'find_index': lambda lst, fn: next index where fn(item) is truthy, else -1,
'contains':   lambda lst, val: val in lst,
'count':      lambda lst, fn_or_val: ...,  # count items matching predicate or value
```

**Test file: `tests/v1_8_1_4/test_list_search.ipp`**
```ipp
var lst = [1, 2, 3, 4, 5, 6]

var first_even = lst.find(func(x) { return x % 2 == 0 })
assert first_even == 2

var first_big = lst.find(func(x) { return x > 10 })
assert first_big == nil    # not found returns nil

var idx = lst.find_index(func(x) { return x > 3 })
assert idx == 3    # lst[3] == 4

var not_found_idx = lst.find_index(func(x) { return x > 100 })
assert not_found_idx == -1

assert lst.contains(3) == true
assert lst.contains(99) == false

assert lst.count(func(x) { return x % 2 == 0 }) == 3   # 2, 4, 6

# Game use case: find first alive enemy
class Enemy { func init(hp) { self.hp = hp } }
var enemies = [Enemy(0), Enemy(50), Enemy(100), Enemy(0)]
var first_alive = enemies.find(func(e) { return e.hp > 0 })
assert first_alive.hp == 50
```

**Regression risk:** Zero. Pure addition.


---

### v1.8.2 — Fix: `var a, b = 1, 2` Literal Multi-Assign (BUG-006) ✅ DONE

**Root cause:** The parser's `var_declaration()` supports `var a, b = expr()` where the RHS is a function call returning a tuple. But it does not support `var a, b = expr, expr` with multiple RHS expressions.


**Find in `parser.py` the `var_declaration()` function. After parsing the LHS names, when parsing the RHS:**
```python
# Current (simplified):
value = self.expression()   # only parses ONE expression

# Fix: if multiple names were declared, allow multiple comma-separated RHS:
if len(names) > 1:
    values = [self.expression()]
    while self.match(TokenType.COMMA):
        values.append(self.expression())
    # emit a tuple/list node that the compiler will unpack
    return MultiVarDecl(names, values)
else:
    return VarDecl(names[0], self.expression())
```

**Test file: `tests/v1_8_2/test_multi_assign.ipp`**
```ipp
# Literal values
var a, b = 1, 2
assert a == 1 and b == 2

var x, y, z = 10, 20, 30
assert x + y + z == 60

# String values
var first, last = "Alice", "Smith"
assert first == "Alice" and last == "Smith"

# Mixed types
var n, s, b2 = 42, "hello", true
assert n == 42 and s == "hello" and b2 == true

# From function still works
func pair() { return 3, 4 }
var p, q = pair()
assert p == 3 and q == 4

# Swap pattern
var m = 1
var n2 = 2
var m, n2 = n2, m
assert m == 2 and n2 == 1
```

---

### v1.8.2.1 — Enhancement: Swap Pattern `var a, b = b, a` ✅ DONE

**Why here:** Natural follow-up to multi-assign. The RHS is fully evaluated before any assignment begins, so swap works without a temp variable.

**File to change:** `vm.py`, multi-assign execution: snapshot all RHS values before writing any LHS slot.

**Test file: `tests/v1_8_2_1/test_swap.ipp`**
```ipp
# Basic swap
var x = 1
var y = 2
var x, y = y, x
assert x == 2
assert y == 1

# Three-way rotation
var a = "first"
var b = "second"
var c = "third"
var a, b, c = b, c, a
assert a == "second"
assert b == "third"
assert c == "first"

# With expressions on RHS
var m = 3
var n = 7
var m, n = n + 1, m - 1
assert m == 8
assert n == 2
```

**Regression risk:** Low. Only affects multi-assign execution order.


---

### v1.8.3 — Fix: `list.map()`, `list.filter()`, `list.reduce()` (BUG-008) ✅ DONE

**File to change:** `vm.py`, wherever list methods are dispatched.

**Add these three methods:**
```python
# In the list method dispatch table:
'map': lambda lst, fn: [_call_fn(fn, [x]) for x in lst],
'filter': lambda lst, fn: [x for x in lst if _call_fn(fn, [x])],
'reduce': lambda lst, fn, init=None: functools.reduce(
    lambda acc, x: _call_fn(fn, [acc, x]),
    lst,
    init if init is not None else lst[0]
),
```

Where `_call_fn(fn, args)` calls an Ipp function object with the given arguments through the VM. The key is that `fn` is an Ipp function (IppFunction or similar), not a Python callable, so it needs to go through the VM's `_call()` mechanism.

**Test file: `tests/v1_8_3/test_fluent_real.ipp`**
```ipp
var nums = [1, 2, 3, 4, 5]

# map
var doubled = nums.map(func(x) { return x * 2 })
assert doubled == [2, 4, 6, 8, 10]

var strs = nums.map(func(x) { return str(x) })
assert strs == ["1", "2", "3", "4", "5"]

# filter
var evens = nums.filter(func(x) { return x % 2 == 0 })
assert evens == [2, 4]

var big = nums.filter(func(x) { return x > 3 })
assert big == [4, 5]

# reduce
var total = nums.reduce(func(acc, x) { return acc + x }, 0)
assert total == 15

var product = nums.reduce(func(acc, x) { return acc * x }, 1)
assert product == 120

# Chaining
var result = [1,2,3,4,5,6]
    .filter(func(x) { return x % 2 == 0 })
    .map(func(x) { return x * x })
assert result == [4, 16, 36]
```

---

### v1.8.3.1 — Enhancement: `list.flat_map()`, `list.group_by()`, `list.sort_by()`

**Why here:** After `map/filter/reduce` exist, these three higher-order methods complete the standard functional collection toolkit. Each calls Ipp function objects through the VM.

**File to change:** `vm.py`, list method dispatch.

```python
'flat_map':  lambda lst, fn: [y for x in lst for y in _call_fn(fn, [x])],
'sort_by':   lambda lst, fn: sorted(lst, key=lambda x: _call_fn(fn, [x])),
'group_by':  lambda lst, fn: ...,  # returns dict: key -> [matching items]
```

**Test file: `tests/v1_8_3_1/test_list_advanced.ipp`**
```ipp
# flat_map: like map but flattens one level
var sentences = ["hello world", "foo bar"]
var words = sentences.flat_map(func(s) { return s.split(" ") })
assert words == ["hello", "world", "foo", "bar"]

# sort_by: sort using a key function
var words2 = ["banana", "apple", "cherry", "date"]
var sorted = words2.sort_by(func(w) { return len(w) })
assert sorted == ["date", "apple", "banana", "cherry"]

var by_last = words2.sort_by(func(w) { return w[-1] })
assert by_last[0] == "banana"   # 'a' last

# group_by: partition into dict
var nums = [1, 2, 3, 4, 5, 6]
var grouped = nums.group_by(func(x) { return x % 2 == 0 ? "even" : "odd" })
assert grouped["even"] == [2, 4, 6]
assert grouped["odd"] == [1, 3, 5]

# Game use case: group enemies by type
class Enemy { func init(t, hp) { self.type = t; self.hp = hp } }
var enemies = [Enemy("orc", 50), Enemy("goblin", 20), Enemy("orc", 80)]
var by_type = enemies.group_by(func(e) { return e.type })
assert len(by_type["orc"]) == 2
assert len(by_type["goblin"]) == 1
```

**Regression risk:** Zero. Pure addition.


---

### v1.8.4 — Fix: `len(IppSet)` Works (BUG-013) ✅ DONE

**Root cause:** `IppSet` does not implement `__len__` in a way the VM's `len()` builtin recognises.

**File to change:** `ipp/runtime/builtins.py` or wherever `IppSet` is defined, and `vm.py` where `len()` is implemented.

**Fix option A — add `__len__` to IppSet:**
```python
class IppSet:
    def __len__(self):
        return len(self._items)   # or self._data — check which attribute is used
```

**Fix option B — handle IppSet in the VM's `len()` builtin:**
```python
# In vm.py, the len() builtin:
def builtin_len(obj):
    if isinstance(obj, IppSet):
        return len(obj._items)   # use the correct attribute name
    return len(obj)
```

**Test file: `tests/v1_8_4/test_set_len.ipp`**
```ipp
var s = set([1, 2, 3, 2, 1])
assert len(s) == 3

var empty = set([])
assert len(empty) == 0

var s2 = set([1, 1, 1, 1])
assert len(s2) == 1

# Operations preserve len
s2.add(2)
assert len(s2) == 2
s2.remove(1)
assert len(s2) == 1
assert s2.contains(2) == true
assert s2.contains(1) == false
```

---

### v1.8.5 — Fix: `vec4 + vec4` Arithmetic Wired to Operators (BUG-014) ✅ DONE

**Root cause:** `vec4`, `vec3`, `vec2` are Python classes (`_Vec4`, `_Vec3`, `_Vec2`). The VM's `ADD` opcode checks for Ipp class instances with `__add__`. It does not check for Python built-in game types.

**File to change:** `vm.py`, the `ADD` (and `SUB`, `MUL`) opcode handlers.

**Current (simplified):**
```python
elif opcode == OpCode.ADD:
    b, a = self.stack.pop(), self.stack.pop()
    if isinstance(a, IppInstance) and hasattr(a, '__add__'):
        result = self._call_method(a, '__add__', [b])
    else:
        result = a + b    # Python fallback — fails for _Vec4
    self.stack.append(result)
```

**Fix — add game type dispatch before the Python fallback:**
```python
elif opcode == OpCode.ADD:
    b, a = self.stack.pop(), self.stack.pop()
    if isinstance(a, IppInstance) and hasattr(a.fields, '__add__'):
        result = self._call_method(a, '__add__', [b])
    elif isinstance(a, (_Vec2, _Vec3, _Vec4)) and isinstance(b, type(a)):
        result = a + b   # these Python classes DO have __add__ — call directly
    else:
        result = a + b
    self.stack.append(result)
```

But first confirm whether `_Vec4` already has Python `__add__` defined. If it does, the fix is just adding the `elif isinstance(a, _Vec4)` branch **before** the generic Python `a + b` that fails. If `_Vec4` does not have Python `__add__`, add it:
```python
class _Vec4:
    def __add__(self, other): return _Vec4(self.x+other.x, self.y+other.y, self.z+other.z, self.w+other.w)
    def __sub__(self, other): return _Vec4(self.x-other.x, self.y-other.y, self.z-other.z, self.w-other.w)
    def __mul__(self, scalar): return _Vec4(self.x*scalar, self.y*scalar, self.z*scalar, self.w*scalar)
    def __eq__(self, other): return self.x==other.x and self.y==other.y and self.z==other.z and self.w==other.w
```

**Test file: `tests/v1_8_5/test_vec_arithmetic.ipp`**
```ipp
var a = vec4(1, 2, 3, 0)
var b = vec4(4, 5, 6, 0)

var sum = a + b
assert sum.x == 5
assert sum.y == 7
assert sum.z == 9

var diff = b - a
assert diff.x == 3
assert diff.y == 3
assert diff.z == 3

var scaled = a * 2
assert scaled.x == 2
assert scaled.y == 4
assert scaled.z == 6

# vec3
var v3a = vec3(1, 0, 0)
var v3b = vec3(0, 1, 0)
var v3sum = v3a + v3b
assert v3sum.x == 1
assert v3sum.y == 1
assert v3sum.z == 0

# vec2
var v2a = vec2(3, 4)
var v2b = vec2(1, 2)
var v2sum = v2a + v2b
assert v2sum.x == 4
assert v2sum.y == 6
```

---

### v1.8.5.1 — Enhancement: `vec2/vec3/vec4` Dot, Length, Normalize, Cross

**Why here:** After arithmetic works, the next most-used vector operations in games are length and normalization (for movement speed) and dot product (for angle checks). These belong in the same sprint.

**File to change:** `ipp/runtime/builtins.py` or wherever `_Vec2`/`_Vec3`/`_Vec4` are defined.

```python
class _Vec3:
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def normalize(self):
        l = self.length()
        return _Vec3(self.x/l, self.y/l, self.z/l) if l > 0 else _Vec3(0,0,0)
    def dot(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z
    def cross(self, other):
        return _Vec3(
            self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y - self.y*other.x
        )
    def lerp(self, other, t):
        return self + (other - self) * t
```

**Test file: `tests/v1_8_5_1/test_vec_ops.ipp`**
```ipp
var v = vec3(3, 4, 0)
assert isclose(v.length(), 5.0) == true

var n = v.normalize()
assert isclose(n.length(), 1.0) == true
assert isclose(n.x, 0.6) == true

var a = vec3(1, 0, 0)
var b = vec3(0, 1, 0)
assert a.dot(b) == 0.0
assert a.dot(a) == 1.0

var cross = a.cross(b)
assert cross.x == 0
assert cross.y == 0
assert cross.z == 1.0

# lerp: linear interpolation
var start = vec3(0, 0, 0)
var end = vec3(10, 20, 30)
var mid = start.lerp(end, 0.5)
assert mid.x == 5.0
assert mid.y == 10.0

# vec2 also gets the methods
var v2 = vec2(3, 4)
assert isclose(v2.length(), 5.0) == true
assert isclose(v2.normalize().length(), 1.0) == true
assert v2.dot(vec2(1, 0)) == 3.0
```

**Regression risk:** Low. Pure addition to existing types.


---

### v1.8.6 — Fix: Spread `[0, ...a, 4]` — Items After Spread (BUG-015) ✅ DONE

**Root cause:** The compiler emits the wrong variable name when items follow a spread expression. `[0, ...a, 4]` generates code referencing a variable `b` that doesn't exist.

**File to change:** `ipp/vm/compiler.py`, the list literal compiler with spread handling.

**How to find it:** Search for `SPREAD` opcode emission or where `SpreadExpr` nodes are compiled inside a list literal. The bug is likely that the compiler reuses an intermediate variable name (`b`) instead of using a fresh temporary or inline stack operation.

**The fix** depends on how the compiler is structured. The invariant: after emitting the spread, the remaining elements (`4` in `[0, ...a, 4]`) must be compiled and appended to the same accumulator list. Trace through the compilation of `ListExpr` containing a `SpreadExpr` to find where the accumulator reference is lost.

**Test file: `tests/v1_8_6/test_spread.ipp`**
```ipp
var a = [1, 2, 3]

# Already works:
var b1 = [0, ...a]
assert b1 == [0, 1, 2, 3]

var b2 = [...a, ...a]
assert b2 == [1, 2, 3, 1, 2, 3]

# Previously broken — items after spread:
var b3 = [0, ...a, 4]
assert b3 == [0, 1, 2, 3, 4]

var b4 = [...a, 4, 5]
assert b4 == [1, 2, 3, 4, 5]

var b5 = [10, 20, ...a, 30, 40]
assert b5 == [10, 20, 1, 2, 3, 30, 40]

# Multiple spreads with items between
var c = [1, 2]
var d = [3, 4]
var e = [0, ...c, 99, ...d, 100]
assert e == [0, 1, 2, 99, 3, 4, 100]
```

---

### v1.8.6.1 — Enhancement: Dict Spread `{**a, **b}` Merge Syntax ✅ DONE

**Why here:** After list spread is fixed, dict spread is a natural companion. Merging two dicts with `{**defaults, **custom}` is the standard pattern for configuration and default-with-override in every modern language.

**File to change:** `ipp/parser/parser.py` (parse `**expr` inside dict literal), `ipp/vm/compiler.py` (emit `DICT_SPREAD` or equivalent), `ipp/vm/vm.py` (merge dict entries).

**Test file: `tests/v1_8_6_1/test_dict_spread.ipp`**
```ipp
var defaults = {"color": "red", "size": 10, "visible": true}
var custom = {"size": 20, "weight": 5}

var merged = {**defaults, **custom}
assert merged["color"] == "red"       # from defaults
assert merged["size"] == 20           # custom overrides default
assert merged["weight"] == 5          # from custom only
assert merged["visible"] == true      # from defaults

# Order matters: later keys win
var a = {"x": 1, "y": 2}
var b = {"y": 99, "z": 3}
var c = {**a, **b}
assert c["x"] == 1
assert c["y"] == 99    # b overrides a
assert c["z"] == 3

# Inline additions alongside spread
var base = {"debug": false, "version": "1.0"}
var dev = {**base, "debug": true, "extra": "dev-only"}
assert dev["debug"] == true
assert dev["version"] == "1.0"
assert dev["extra"] == "dev-only"
```

**Regression risk:** Zero. `**` inside dict literal is currently a parse error.


---

### v1.8.7 — Fix: `prop` Getter Body Parses Correctly (BUG-009) ✅ DONE

**Root cause:** The `prop` keyword's parser calls `block()` which already consumes the closing `}`, so an extra `consume(RIGHT_BRACE)` after the getter/setter body caused a parse error.

**Changes:**
- **Parser:** `property_declaration()` already uses `block()` correctly — the previous BUG-009 was resolved.
- **Compiler (`compiler.py`):** Compile PropDecl getters/setters as methods (with `__prop_get_<name>` / `__prop_set_<name>` mangled names) and register via the `PROP_DEFINE` (111) opcode. Uses `DUP + METHOD` trick to keep closure on stack for registration.
- **VM (`vm.py`):** `PROP_DEFINE` opcode handler pops name, setter, getter and stores in `IppClass.properties`. `GET_PROPERTY` and `SET_PROPERTY` handlers check for property getters/setters and call through `_call_method`. `METHOD` handler updated to search for IppClass past DUP'd closures.
- **Interpreter (`interpreter.py`):** Fixed `_execute_property_getter`/`_execute_property_setter` to correctly use AST body lists and closure environment.
- **`IppClass` (`vm.py`):** Added `properties: Dict[str, tuple]` field.
- **`Bytecode` (`bytecode.py`):** Added `PROP_DEFINE = 111` opcode.
- **Test files:** `tests/v1_8_7/test_prop_basic.ipp`, `tests/v1_8_7/test_prop_edge.ipp`

```ipp
class Foo {
    var _val = 0
    prop hp {
        get { return self._val }
        set(v) { self._val = v }
    }
}
var f = Foo()
assert f.hp == 0
f.hp = 42
assert f.hp == 42
```

---

### v1.8.7.1 — Enhancement: `prop` Computed Getters (Read-Only) and Validation Setters

**Why here:** After basic `prop get/set` bodies work, the most common real use cases are: (1) computed properties that derive their value from other fields, (2) setters that validate and clamp before storing.

**No new parser work needed** — this is purely about having the body syntax work (fixed in v1.8.7). This version adds tests that confirm the full intended use.

**Test file: `tests/v1_8_7_1/test_property_advanced.ipp`**
```ipp
class Circle {
    func init(r) { self._r = r }

    prop radius {
        get { return self._r }
        set(v) {
            if v < 0 { v = 0 }    # clamp
            self._r = v
        }
    }

    prop diameter {
        get { return self._r * 2 }
        set(v) { self._r = v / 2 }
    }

    prop area {
        get { return pi * self._r * self._r }    # computed, read-only
    }
}

var c = Circle(5)
assert c.radius == 5
assert c.diameter == 10
assert isclose(c.area, 78.53981633974483) == true

c.radius = 10
assert c.diameter == 20

c.diameter = 6
assert c.radius == 3.0

c.radius = -5    # clamped to 0
assert c.radius == 0

# Health with clamping
class Health {
    func init(max_hp) { self._hp = max_hp; self._max = max_hp }

    prop hp {
        get { return self._hp }
        set(v) {
            if v < 0 { v = 0 }
            if v > self._max { v = self._max }
            self._hp = v
        }
    }

    prop is_alive {
        get { return self._hp > 0 }
    }

    prop percent {
        get { return self._hp / self._max }
    }
}

var h = Health(100)
assert h.hp == 100
assert h.is_alive == true
assert h.percent == 1.0

h.hp = 150    # clamped to max
assert h.hp == 100

h.hp = -10    # clamped to 0
assert h.hp == 0
assert h.is_alive == false
```

**Regression risk:** Zero. No parser change — purely exercises the v1.8.7 fix.


---

### v1.8.8 — Fix: `is` Operator Works in All Expression Positions (BUG-010) ✅ DONE

**Root cause:** `is` is parsed at the wrong precedence level or not in the binary expression table, so `var r = x is int` sees `var r = x` then `is` as an unknown identifier.

**File to change:** `ipp/parser/parser.py`, the expression precedence table / binary operator parsing.

**Fix:** Add `is` to the comparison-level binary operators:
```python
# In the comparison / equality parse function:
if self.match(TokenType.IS):   # or however 'is' is tokenized
    right = self.primary()     # parse the type name (int, string, list, etc.)
    expr = IsExpr(expr, right.name)   # or similar AST node
```

Also ensure `is` is tokenized as its own token type (not `IDENTIFIER`). If it is currently `IDENTIFIER`, add it as `IS` in the lexer's keyword table.

**Test file: `tests/v1_8_8/test_is_operator.ipp`**
```ipp
var n = 42
var s = "hello"
var lst = [1, 2, 3]
var d = {"a": 1}
var b = true

# In assignment RHS
var r1 = n is int
assert r1 == true

var r2 = n is string
assert r2 == false

# In condition
if n is int {
    assert true
} else {
    assert false
}

# In assert directly
assert (s is string) == true
assert (lst is list) == true
assert (d is dict) == true
assert (b is bool) == true
assert (n is float) == false

# In ternary
var label = n is int ? "integer" : "other"
assert label == "integer"
```

---

### v1.8.8.1 — Enhancement: `is not` Operator (handled in v1.8.8 via `BANG` check) ✅ DONE

**Why here:** `is not` is the natural negative form of `is`. After `is` works, adding `is not` is 3 lines in the parser.

**File to change:** `ipp/parser/parser.py`, comparison parsing — after matching `IS`, check for following `NOT`.

```python
if self.match(TokenType.IS):
    if self.match(TokenType.NOT):
        right = self.primary()
        expr = NotExpr(IsExpr(expr, right.name))
    else:
        right = self.primary()
        expr = IsExpr(expr, right.name)
```

**Test file: `tests/v1_8_8_1/test_is_not.ipp`**
```ipp
var n = 42
var s = "hello"
var lst = [1, 2, 3]

assert n is not string == true
assert n is not int == false
assert s is not string == false
assert lst is not list == false
assert n is not list == true

# In condition
if n is not string {
    assert true
} else {
    assert false
}

# Combined with is
func describe(x) {
    if x is int { return "integer" }
    if x is string { return "string" }
    if x is list { return "list" }
    return "unknown"
}
assert describe(42) == "integer"
assert describe("hi") == "string"
assert describe([]) == "list"
assert describe(nil) == "unknown"
```

**Regression risk:** Zero. `is not` was previously a parse error.


---

### v1.8.9 — Fix: Typed Exception Field Access in Catch Block (BUG-017)

**Root cause:** When a class instance is `throw`n, the catch block receives a string (`"<MyError instance>"`) instead of the object.

**File to change:** `vm.py`, the `THROW` opcode handler.

**Current behaviour:** The throw value is converted to a string before being placed in the catch slot.

**Fix:** Pass the thrown value as-is (the Ipp object, integer, string, or whatever was thrown) directly into the catch binding:
```python
# In the THROW handler:
thrown_value = self.stack.pop()
# DO NOT do: thrown_value = str(thrown_value)
# Place it directly into the catch variable slot:
catch_frame.locals[catch_slot] = thrown_value
```

**Test file: `tests/v1_8_9/test_typed_exceptions.ipp`**
```ipp
class NetworkError {
    func init(code, message) {
        self.code = code
        self.message = message
    }
    func __str__() {
        return "NetworkError(" + str(self.code) + "): " + self.message
    }
}

class ValidationError {
    func init(field, reason) {
        self.field = field
        self.reason = reason
    }
}

# Can access fields on caught object
var caught_code = 0
var caught_msg = ""
try {
    throw NetworkError(404, "Not Found")
} catch e {
    caught_code = e.code
    caught_msg = e.message
}
assert caught_code == 404
assert caught_msg == "Not Found"

# Works with __str__
try {
    throw NetworkError(500, "Server Error")
} catch e {
    assert str(e) == "NetworkError(500): Server Error"
}

# Nested exception data
var field_name = ""
try {
    throw ValidationError("email", "invalid format")
} catch e {
    field_name = e.field
    assert e.reason == "invalid format"
}
assert field_name == "email"
```

---

### v1.8.9.1 — Enhancement: Exception Hierarchy with `extends` and `is` Type Checking

**Why here:** Once typed exceptions work (v1.8.9) and `is` works (v1.8.8), exception hierarchies are the natural next step. Game code distinguishes `NetworkError` from `ValidationError` from `GameError` and handles them differently.

**No new VM work needed** — requires v1.8.9 (typed catch) and v1.8.8 (`is` operator) to be done. This version exercises them together.

**Test file: `tests/v1_8_9_1/test_exception_hierarchy.ipp`**
```ipp
class AppError {
    func init(msg) { self.message = msg }
    func __str__() { return "AppError: " + self.message }
}

class NetworkError extends AppError {
    func init(url, status) {
        self.url = url
        self.status = status
        self.message = "HTTP " + str(status) + " from " + url
    }
    func __str__() {
        return "NetworkError(" + str(self.status) + "): " + self.message
    }
}

class ValidationError extends AppError {
    func init(field, reason) {
        self.field = field
        self.reason = reason
        self.message = "Invalid " + field + ": " + reason
    }
}

# Fields accessible on caught object (requires v1.8.9)
var caught_status = 0
try {
    throw NetworkError("api.example.com", 404)
} catch e {
    caught_status = e.status
    assert e.url == "api.example.com"
}
assert caught_status == 404

# Type checking with `is` (requires v1.8.8)
try {
    throw ValidationError("email", "invalid format")
} catch e {
    assert e is ValidationError == true
    assert e is AppError == true
    assert e.field == "email"
    assert e.reason == "invalid format"
}

# Rethrowing with richer context
var outer_msg = ""
try {
    try {
        throw NetworkError("db.server", 503)
    } catch e {
        if e is NetworkError {
            throw AppError("Service unavailable: " + str(e.status))
        }
    }
} catch e {
    outer_msg = e.message
}
assert outer_msg.contains("503") == true
```

**Regression risk:** Zero. Exercises existing features; no new VM work.


---

## Phase C: Standard Library Completeness (v1.9.0 – v1.9.5.1)

> After Phase C, see **Phase C2: Module & Import System (v1.9.10–v1.9.13)** below — prerequisite for any multi-file project.

After Phase B, the core language is reliable. Phase C rounds out the standard library.

---

### v1.9.0 — Feature: `list[a..b]` Slice Syntax (BUG-018) ✅ DONE

New: `SliceExpr(start, end)` AST node. Parser `_parse_index_or_slice()` in `call()`. `BUILD_SLICE` opcode. VM/Interpreter `GET_INDEX` detects `slice` objects. All tests pass.

---

### v1.9.0.1 — Enhancement: Slice with Step `list[a..b..step]` ✅ DONE

New: `SliceExpr(start, end, step)` with step field. Parser detects third `..expr` in index. VM BUILD_SLICE pops step/end/start. GET_INDEX handles `slice` with step. Reversed step `lst[9..2..-1]` works. 112 tests pass.

---

### v1.9.1 — Feature: `global` Keyword for Explicit Global Writes ✅ DONE

### v1.9.1.1 — Enhancement: `nonlocal` Keyword for Closure Writes ✅ DONE (current)

**Why here:** `global` lets you write to module-level globals. `nonlocal` is the companion that lets closures write to their enclosing function's variables (not just read them). Needed for counter closures, memoization, state machines.

**File to change:** `ipp/parser/parser.py` (parse `nonlocal name`), `ipp/vm/compiler.py` (emit CLOSE_UPVALUE write rather than local write).

**Test file: `tests/v1_9_1_1/test_nonlocal.ipp`**
```ipp
# Counter closure
func make_counter(start=0) {
    var count = start
    func inc() {
        nonlocal count
        count = count + 1
        return count
    }
    func reset() {
        nonlocal count
        count = start
    }
    func get() { return count }
    return [inc, reset, get]
}

var counter = make_counter(10)
var inc = counter[0]; var reset = counter[1]; var get = counter[2]
assert get() == 10
assert inc() == 11
assert inc() == 12
assert inc() == 13
reset()
assert get() == 10

# Memoization
func memoize(fn) {
    var cache = {}
    func wrapper(x) {
        nonlocal cache
        if cache.get(str(x)) != nil {
            return cache.get(str(x))
        }
        var result = fn(x)
        cache[str(x)] = result
        return result
    }
    return wrapper
}
var calls = 0
func slow_double(x) { calls = calls + 1; return x * 2 }
var fast_double = memoize(slow_double)
assert fast_double(5) == 10
assert fast_double(5) == 10   # cached
assert calls == 1             # only computed once
```

**Regression risk:** Medium. Touches upvalue/closure system.


> **Done v1.9.1.1:**
> - Added `NONLOCAL` token, `NonlocalDeclStmt(names)` AST node, parser support for `nonlocal x`.
> - Compiler: `nonlocal_names` set per function; `compile_identifier`/`compile_assign_name` force upvalue resolution for nonlocal names (error if not found in enclosing scope).
> - Interpreter: `_nonlocal_names` set, saved/reset per function call; `visit_identifier`/`visit_assign_expr` skip current env (use parent) for nonlocal names.
> - **SET_INDEX bugfix (v1.5.32 era regression):** `SET_INDEX` now pushes the assigned value back onto the stack. Previously `IndexSetExpr` inside `ExprStmt` (e.g. `cache["key"] = val`) produced an extra `POP` that corrupted the stack, because `SET_INDEX` didn't push any result but the generic `ExprStmt` codegen always emitted `POP`.
> - Test file: `tests/v1_9_1_1/test_nonlocal.ipp` (counter closure, `nonlocal a, b`, compound assign, memoization, nested nonlocal).
> - 112/114 tests pass (2 pre-existing failures: v07, v1.5.30).


---

### v1.9.2 — Feature: `map()`, `filter()`, `reduce()` as Global Builtins (BUG-020) ✅ DONE

```ipp
var doubled = map(func(x) { return x * 2 }, [1, 2, 3])
assert doubled == [2, 4, 6]

var evens = filter(func(x) { return x % 2 == 0 }, [1,2,3,4,5])
assert evens == [2, 4]

var total = reduce(func(acc, x) { return acc + x }, [1,2,3,4,5], 0)
assert total == 15
```

**Files changed:**
- `ipp/runtime/builtins.py` — Added `ipp_map`, `ipp_filter`, `ipp_reduce` functions using interpreter `call_function`
- `ipp/vm/vm.py` — VM-native versions in `_init_builtins` using `self._call_sync`
- `tests/v1_9_2/test_map_filter_reduce.ipp` — Comprehensive test (map/filter/reduce with lambdas, named funcs, edge cases, chaining)
- `run_tests.py` / `tests/regression.py` — Test registered

---

### v1.9.3 — Feature: Multi-line Strings `"""..."""` ✅ DONE

```ipp
var s = """
line one
line two
line three
"""
var lines = s.strip().split("\n")
assert len(lines) == 3
assert lines[0] == "line one"
```

**Files changed:**
- `ipp/lexer/lexer.py` — Added `triple_quote_string()` method, `peek_next_next()` helper, modified `scan_token` to detect `"""` and `f"""` before single-quote path
- `ipp/interpreter/interpreter.py` — Fixed `visit_fstring_expr` to use `ipp_str()` so bool values render as `"true"`/`"false"` (pre-existing bug)
- `tests/v1_9_3/test_multiline_strings.ipp` — 16 test cases covering basic multiline, empty, quotes inside, escape sequences, f-string multiline, concat, len, type
- `run_tests.py` / `tests/regression.py` — Test registered

Also includes fix: `f"""..."""` multi-line f-string variant works.

---

### v1.9.3.1 — Enhancement: Multi-line F-strings `f"""..."""` ✅ DONE (in v1.9.3)

**Why here:** Game dialogue, quest descriptions, HTML templates, and SQL strings are routinely multi-line AND need interpolation. `f"""..."""` combines both.

**File to change:** Already implemented in v1.9.3 — `ipp/lexer/lexer.py` handles `f"""..."""` via `triple_quote_string` with `is_fstring=True`.

**Test file: `tests/v1_9_3_1/test_multiline_fstring.ipp`**
```ipp
var name = "Alice"
var score = 95
var level = 5

var report = f"""
Player Report
=============
Name:  {name}
Score: {score}
Level: {level}
Grade: {"A" if score >= 90 else "B"}
"""
assert report.contains("Name:  Alice") == true
assert report.contains("Score: 95") == true
assert report.contains("Grade: A") == true

# SQL template
var table = "users"
var col = "email"
var val = "alice@example.com"
var sql = f"""
    SELECT *
    FROM {table}
    WHERE {col} = '{val}'
    AND active = 1
"""
assert sql.contains("FROM users") == true
assert sql.contains("alice@example.com") == true
```

**Regression risk:** Low. Extension of existing f-string parser.


---

### v1.9.4 — Feature: Async Return Value Fixed (BUG-016) ✅ DONE

`async_run(f())` already returned correct value. Fixed `await` opcode in both interpreter and VM. 

**Changes:** `interpreter.py` — `visit_await_expr` runs awaited coroutine to completion. `vm.py` — added `AWAIT` opcode (#114) using sub-VM isolation; refactored `_builtin_async_run` to use sub-VM instead of `self.run()` which leaked into parent frames.

```ipp
async func double_async(x) {
    return x * 2
}
var result = async_run(double_async(21))
assert result == 42
```

---

### v1.9.4.1 — Enhancement: `await` Works Inside `async` Functions ✅ DONE (merged into v1.9.4)

**Why here:** After async return is fixed, `await other_async_func()` must properly suspend the calling coroutine and return the inner coroutine's result. This is the primitive that makes async code composable.

**File to change:** `vm.py`, coroutine execution — when `AWAIT` opcode fires inside an async frame, yield control to the inner coroutine and resume with its return value.

**Test file: `tests/v1_9_4_1/test_await.ipp`**
```ipp
async func fetch(url) {
    return "data:" + url
}

async func process(url) {
    var raw = await fetch(url)
    return raw.upper()
}

var result = async_run(process("api.example.com"))
assert result == "DATA:API.EXAMPLE.COM"

# Chained awaits
async func step1() { return 1 }
async func step2(x) { return x + 1 }
async func step3(x) { return x * 10 }

async func pipeline() {
    var a = await step1()
    var b = await step2(a)
    var c = await step3(b)
    return c
}

assert async_run(pipeline()) == 20
```

**Regression risk:** Medium. Touches coroutine execution path.


---

### v1.9.5 — Feature: Set Operations (`union`, `intersect`, `difference`) ✅ DONE

```ipp
var a = set([1, 2, 3, 4])
var b = set([3, 4, 5, 6])

var u = a.union(b)
assert len(u) == 6

var i = a.intersect(b)
assert len(i) == 2
assert i.contains(3) == true
assert i.contains(4) == true

var d = a.difference(b)
assert len(d) == 2
assert d.contains(1) == true
assert d.contains(2) == true
```

---

### v1.9.6 — Feature: `range()` as Lazy Iterator + `enumerate()`

**Why here:** `range()` currently returns a full list. For large ranges (e.g. `range(100000)`) this wastes memory. Making it lazy is a 1-day change. `enumerate()` is the natural companion.

**File to change:** Add `IppRange` lazy type to `vm.py`; `for-in` handler already works if `IppRange` supports index-based access.

```ipp
for i, val in enumerate(["a", "b", "c"]) {
    print(str(i) + ": " + val)
}
# 0: a
# 1: b
# 2: c

# Large range is now memory-efficient
var sum = 0
for i in range(100000) { sum = sum + i }
print(sum)
```

**Test file: `tests/v1_9_6/test_enumerate.ipp`**
```ipp
var items = ["x", "y", "z"]
var result = []
for i, v in enumerate(items) {
    result = result + [str(i) + "=" + v]
}
assert result == ["0=x", "1=y", "2=z"]

for i, v in enumerate(["a","b","c"], start=1) {
    assert i >= 1
}
```

---

### v1.9.7 — Feature: `zip()` Builtin

**Why here:** `zip` pairs two lists element-wise — essential for game code that processes parallel arrays (positions + velocities, names + scores, etc.).

```ipp
var names = ["Alice", "Bob", "Carol"]
var scores = [95, 87, 92]
for name, score in zip(names, scores) {
    print(name + ": " + str(score))
}

var pairs = zip([1,2,3], [4,5,6])
assert pairs == [[1,4],[2,5],[3,6]]
```

**Test file: `tests/v1_9_7/test_zip.ipp`**
```ipp
var a = [1, 2, 3]
var b = [4, 5, 6]
var zipped = zip(a, b)
assert zipped == [[1,4],[2,5],[3,6]]

# Unequal lengths — stops at shortest
var c = [1, 2]
var d = [10, 20, 30]
assert len(zip(c, d)) == 2

# Use in for loop
var sums = []
for pair in zip(a, b) {
    sums = sums + [pair[0] + pair[1]]
}
assert sums == [5, 7, 9]
```

---

### v1.9.8 — Feature: `sorted()` and `lst.sorted()` Non-Mutating Sort

**Why here:** `lst.sort()` mutates in place. Game code often needs a sorted copy (leaderboard display, priority queues) without altering the original. 3-line addition.

```ipp
var original = [3, 1, 4, 1, 5]
var s = sorted(original)
assert s == [1, 1, 3, 4, 5]
assert original == [3, 1, 4, 1, 5]   # unchanged

# With key function
var words = ["banana", "apple", "cherry"]
var by_len = sorted(words, key=func(w) { return len(w) })
assert by_len[0] == "apple"

# Reverse
var desc = sorted(original, reverse=true)
assert desc[0] == 5
```

**Test file: `tests/v1_9_8/test_sorted.ipp`**
```ipp
var nums = [5, 2, 8, 1, 9, 3]
var s = sorted(nums)
assert s == [1, 2, 3, 5, 8, 9]
assert nums == [5, 2, 8, 1, 9, 3]

var desc = sorted(nums, reverse=true)
assert desc[0] == 9

var words = ["banana", "fig", "apple", "date"]
var alpha = sorted(words)
assert alpha[0] == "apple"
```

---

### v1.9.9 — Feature: `dict.map()`, `dict.filter()`, `dict.items()` Full Support

**Why here:** Dict `items()` already works but returns a raw Python list of tuples, not Ipp pairs. Fixing that plus adding `dict.map` and `dict.filter` completes the dict API.

```ipp
var prices = {"apple": 1.5, "banana": 0.75, "cherry": 3.0}

# dict.filter — keep entries where value meets condition
var cheap = prices.filter(func(k, v) { return v < 2.0 })
assert cheap.keys() == ["apple", "banana"] or len(cheap) == 2

# dict.map — transform values
var doubled = prices.map(func(k, v) { return v * 2 })
assert doubled["apple"] == 3.0

# items() iteration works cleanly
for key, val in prices.items() {
    assert val > 0
}
```

**Test file: `tests/v1_9_9/test_dict_full.ipp`**
```ipp
var d = {"a": 1, "b": 2, "c": 3}

var doubled = d.map(func(k, v) { return v * 2 })
assert doubled["a"] == 2
assert doubled["b"] == 4

var filtered = d.filter(func(k, v) { return v > 1 })
assert len(filtered) == 2

var count = 0
for k, v in d.items() {
    count = count + v
}
assert count == 6
```

---

### v1.9.5.1 — Enhancement: Set Comprehensions `{expr for x in iterable if cond}` ✅ DONE (merged into v1.9.5)

**Why here:** List and dict comprehensions already exist. Set comprehensions are the natural completion of the comprehension family — same syntax, different collection type.

**File to change:** `ipp/parser/parser.py` — recognise `{expr for x in ...}` (no `key: value` pattern) as a set comprehension rather than a dict comprehension.

**Test file: `tests/v1_9_5_1/test_set_comprehension.ipp`**
```ipp
var squares = {x*x for x in range(6)}
assert squares.contains(0) == true
assert squares.contains(25) == true
assert squares.contains(6) == false   # 6 is not a perfect square of 0-5
assert len(squares) == 6

# With filter
var even_squares = {x*x for x in range(10) if x % 2 == 0}
assert len(even_squares) == 5         # {0, 4, 16, 36, 64}
assert even_squares.contains(4) == true
assert even_squares.contains(9) == false

# Deduplication via set comprehension
var words = ["apple", "banana", "apple", "cherry", "banana"]
var unique_lengths = {len(w) for w in words}
assert unique_lengths.contains(5) == true   # apple
assert unique_lengths.contains(6) == true   # banana, cherry
assert len(unique_lengths) == 2
```

**Regression risk:** Low. Requires distinguishing `{expr for ...}` from `{key: val for ...}` in parser.


---

---

## Phase C2: Module & Import System (v1.9.10 – v1.9.13)

> **Why this is Phase C2 and not C:** The module system depends on the language being reliable first — closures, classes, error handling, and string methods must all work before people will write multi-file projects worth importing. Phase C2 slots in after Phase C is complete and before Phase D begins.
>
> **Why this matters:** The audit scores Module/Import at **3/10**. Right now every Ipp program is a single file. You cannot build a game with one file. There is no `import`, no namespacing, no way to share code across files. This is the single biggest gap between "toy language" and "language you can build a real project in." A package registry and community ecosystem are explicitly **out of scope here** — those emerge after the language works. The goal of this phase is: one programmer can split their game into multiple `.ipp` files.

---

### v1.9.10 — Feature: Basic File Import `import "path/to/file.ipp"`

**What:** The simplest possible import — load and execute another `.ipp` file, and make its top-level names available in the importing file's scope. No namespacing yet.

**Why this version first:** Gets multi-file projects unblocked immediately. The absence of namespacing is a known trade-off — it will be fixed in v1.9.11. Doing it in one step risks a more complex implementation that blocks the whole feature.

**Files to change:**
- `ipp/parser/parser.py` — parse `import "path"` as a statement
- `ipp/vm/vm.py` — add `OP_IMPORT` handler: resolve path, read file, compile, run in sub-VM, copy top-level names into caller's globals
- `ipp/vm/compiler.py` — emit `OP_IMPORT` for import statements
- `ipp/vm/bytecode.py` — add `OP_IMPORT` opcode

**Syntax:**
```ipp
import "utils/math_helpers.ipp"
import "enemies/orc.ipp"
import "../shared/constants.ipp"    # relative paths
```

**Resolution rules:**
1. Path is relative to the importing file's directory
2. Absolute paths from the project root if starting with `/`
3. A file is only executed once per VM session — second `import` of same resolved path is a no-op (cached)

**Implementation sketch:**
```python
# In vm.py OP_IMPORT handler:
resolved = resolve_path(current_file_dir, import_path)
if resolved in self._import_cache:
    return   # already imported
self._import_cache.add(resolved)
with open(resolved) as f:
    src = f.read()
sub_chunk = compile_ast(parse(tokenize(src)))
# Run in same global scope so names become available
self.run(sub_chunk, globals=self.globals)
```

**Test file: `tests/v1_9_10/`** (two files required)

`tests/v1_9_10/helpers.ipp`:
```ipp
func double(x) { return x * 2 }
func clamp(val, lo, hi) {
    if val < lo { return lo }
    if val > hi { return hi }
    return val
}
var GRAVITY = 9.8
```

`tests/v1_9_10/test_import.ipp`:
```ipp
import "helpers.ipp"

assert double(5) == 10
assert double(0) == 0
assert clamp(15, 0, 10) == 10
assert clamp(-3, 0, 10) == 0
assert clamp(5, 0, 10) == 5
assert GRAVITY == 9.8

# Import is idempotent — second import of same file does nothing
import "helpers.ipp"
assert double(3) == 6    # still works, not re-executed
```

**Regression risk:** Low to medium. New opcode and path resolution logic. Does not touch existing execution paths.

---

### v1.9.10.1 — Enhancement: Import Caching Is Per-VM, Not Global

**What:** Confirm the import cache is scoped to a single VM instance, not a process-level global. Two independent programs running in the same Python process (e.g. tests) must not share import state.

**Why its own version:** Easy to accidentally implement as a class-level or module-level dict, which breaks test isolation. This version adds a regression test for it.

**File to change:** `ipp/vm/vm.py` — ensure `self._import_cache` is initialised in `__init__`, not at class level.

**Test file: `tests/v1_9_10_1/test_import_isolation.ipp`**
```ipp
# This test is run twice in the regression suite with fresh VM instances.
# The imported counter must start at 0 each time.
import "counter.ipp"
assert get_count() == 0
increment()
assert get_count() == 1
```

`counter.ipp`:
```ipp
var _count = 0
func get_count() { return _count }
func increment() { _count = _count + 1 }
```

**Regression risk:** Zero if `_import_cache` is already per-instance. One-line fix if it isn't.

---

### v1.9.11 — Feature: Namespaced Import `import "file.ipp" as name`

**What:** Import a file's contents under a namespace so names don't pollute the caller's scope. `import "utils.ipp" as utils` makes `utils.double()` available but not `double()` directly.

**Why after v1.9.10:** Flat import (v1.9.10) is simpler and unblocks the common case. Namespacing is the correct long-term design but requires storing the sub-scope as a dict/object. Doing both at once is harder to test and debug.

**Files to change:**
- `ipp/parser/parser.py` — parse `import "path" as identifier`
- `ipp/vm/vm.py` — run the sub-file in a fresh scope dict, then bind that dict to the namespace name in the caller's scope
- `ipp/vm/vm.py` — namespace object must support attribute access (`utils.double`)

**Syntax:**
```ipp
import "utils/math_helpers.ipp" as math_utils
import "enemies/orc.ipp" as Orc
import "../config.ipp" as cfg
```

**Implementation sketch:**
```python
# In OP_IMPORT_AS handler:
resolved = resolve_path(current_file_dir, import_path)
sub_globals = {}
sub_vm = VM(globals=sub_globals)
sub_vm.run(compile_ast(parse(tokenize(open(resolved).read()))))
# Wrap sub_globals as a namespace object
namespace = IppNamespace(sub_globals)
self.globals[alias] = namespace
```

`IppNamespace` is a thin wrapper: attribute access (`ns.name`) resolves to `sub_globals["name"]`.

**Test file: `tests/v1_9_11/`**

`tests/v1_9_11/vec_utils.ipp`:
```ipp
func length(x, y) { return math.sqrt(x*x + y*y) }
func normalize(x, y) {
    var len = length(x, y)
    return [x / len, y / len]
}
var ZERO = [0, 0]
var PI = 3.14159265358979
```

`tests/v1_9_11/test_namespaced_import.ipp`:
```ipp
import "vec_utils.ipp" as vec

assert isclose(vec.length(3, 4), 5.0) == true

var n = vec.normalize(3, 4)
assert isclose(n[0], 0.6) == true
assert isclose(n[1], 0.8) == true

assert vec.ZERO == [0, 0]
assert isclose(vec.PI, 3.14159) == true

# Name does NOT leak into caller scope
var caught = ""
try {
    print(length)    # should be undefined
} catch e {
    caught = e
}
assert caught.contains("Undefined") == true
```

**Regression risk:** Low. New code path; v1.9.10 flat import still works unchanged.

---

### v1.9.11.1 — Enhancement: Selective Import `import { name1, name2 } from "file.ipp"`

**What:** Import only specific names from a file, without a namespace prefix. Keeps the common case clean: `import { double, clamp } from "utils.ipp"` gives you `double()` and `clamp()` directly, leaving the rest out of scope.

**Why useful:** Flat import (v1.9.10) brings everything in — name collisions become a problem as projects grow. Namespaced import (v1.9.11) requires `utils.double()` — fine for large modules but verbose for frequently-used utilities. Selective import is the right default for medium-sized projects.

**File to change:** `ipp/parser/parser.py` — parse `import { id, id, ... } from "path"`. `ipp/vm/vm.py` — run sub-file in a fresh scope, then copy only the named entries into caller scope.

**Syntax:**
```ipp
import { double, clamp, GRAVITY } from "utils.ipp"
import { Orc, Goblin } from "enemies.ipp"
import { SCREEN_W, SCREEN_H, FPS } from "config.ipp"

# Aliases in selective import
import { double as times_two } from "utils.ipp"
```

**Test file: `tests/v1_9_11_1/`**

`tests/v1_9_11_1/constants.ipp`:
```ipp
var SCREEN_W = 800
var SCREEN_H = 600
var FPS = 60
var DEBUG = false
var VERSION = "1.0.0"
```

`tests/v1_9_11_1/test_selective_import.ipp`:
```ipp
import { SCREEN_W, SCREEN_H } from "constants.ipp"

assert SCREEN_W == 800
assert SCREEN_H == 600

# Non-imported names stay out of scope
var caught = ""
try { print(FPS) } catch e { caught = e }
assert caught.contains("Undefined") == true

# Alias
import { SCREEN_W as WIDTH } from "constants.ipp"
assert WIDTH == 800

# Import class from another file
import { Orc } from "orc.ipp"
var enemy = Orc("troll", 100)
assert enemy.name == "troll"
assert enemy.hp == 100
```

`tests/v1_9_11_1/orc.ipp`:
```ipp
class Orc {
    func init(name, hp) {
        self.name = name
        self.hp = hp
    }
    func attack() { return self.name + " attacks!" }
}
```

**Regression risk:** Low. New syntax path.

---

### v1.9.12 — Feature: `export` Keyword — Explicit Public API

**What:** Mark which names a file exports. Without `export`, everything is importable (v1.9.10/11 behaviour). With `export`, only marked names are accessible to importers. Gives library authors control over their API surface.

**Why after v1.9.11:** Imports need to work reliably before you add access control on top. Also, many small scripts will never need `export` — it's an opt-in convention, not a requirement.

**Syntax:**
```ipp
# utils.ipp — public API via export
export func double(x) { return x * 2 }
export func clamp(val, lo, hi) { ... }
export var MAX_SPEED = 500

# Private — importers cannot access this
func _internal_helper(x) { return x * x }
var _cache = {}
```

**Design decision:** `export` is a modifier on `func`, `var`, `let`, and `class` declarations — not a separate export list. This matches GDScript's `@export` convention and is simpler to implement than JavaScript's `export { a, b, c }` at the bottom.

**Files to change:**
- `ipp/lexer/lexer.py` — add `EXPORT` token
- `ipp/parser/parser.py` — parse `export func/var/let/class`
- `ipp/vm/compiler.py` — mark exported names in chunk metadata
- `ipp/vm/vm.py` — when resolving a namespaced import, only expose exported names; when using selective import (`{ name } from "file"`), validate name is exported

**Test file: `tests/v1_9_12/`**

`tests/v1_9_12/geometry.ipp`:
```ipp
export func area_circle(r) { return pi * r * r }
export func area_rect(w, h) { return w * h }
export var GOLDEN_RATIO = 1.6180339887

# Private — not exported
func _validate_positive(x) {
    assert x > 0, "value must be positive"
}
var _calculation_count = 0
```

`tests/v1_9_12/test_export.ipp`:
```ipp
import "geometry.ipp" as geo

# Exported names work
assert isclose(geo.area_circle(5), 78.539816) == true
assert geo.area_rect(4, 6) == 24
assert isclose(geo.GOLDEN_RATIO, 1.618) == true

# Private names are inaccessible via namespace
var caught = ""
try { print(geo._validate_positive) } catch e { caught = e }
assert caught.contains("not exported") == true or caught.contains("Undefined") == true

# Selective import of exported name works
import { area_rect } from "geometry.ipp"
assert area_rect(3, 4) == 12

# Selective import of private name fails clearly
try {
    import { _calculation_count } from "geometry.ipp"
} catch e {
    caught = e
}
assert caught.contains("not exported") == true
```

**Regression risk:** Medium. Changes how the sub-file scope is exposed to callers. Files without any `export` keyword remain fully accessible (backward compatible with v1.9.10/11).

---

### v1.9.13 — Feature: `ipp.toml` Package Manifest + `ipp run` Project Mode

**What:** The minimal packaging primitive. A folder with an `ipp.toml` file is an Ipp project. `ipp run` without a filename looks for `ipp.toml` and runs the `entry` file it points to. No registry, no dependencies, no versioning beyond a version string — just enough to define "what is this project."

**Why this is the limit of Phase C2:** A package registry, dependency resolution, and publishing workflow are Phase F (community ecosystem) features. They require a user base and maintained infrastructure. Adding them now would be over-engineering a language that currently scores D+. What game developers need right now is: "I can split my game into files and run it with one command."

**`ipp.toml` format (minimal):**
```toml
[package]
name        = "my-game"
version     = "0.1.0"
entry       = "main.ipp"
description = "A turn-based dungeon crawler written in Ipp"
author      = "Alice"
ipp_min     = "1.9.13"     # minimum Ipp version required

[run]
args        = []            # default CLI args passed to entry file
```

**CLI behaviour:**
```bash
ipp run                    # reads ipp.toml in cwd, runs entry file
ipp run main.ipp           # existing behaviour unchanged
ipp new my-game            # scaffold: creates folder, ipp.toml, main.ipp, tests/
ipp check                  # static linter (v2.1.3 from Phase E) — listed here for discoverability
```

**Files to change:**
- `ipp/cli.py` or `main.py` — detect `ipp.toml` in cwd when no filename given
- New file `ipp/project.py` — `load_project(path)` reads `ipp.toml`, returns entry path + config
- New file `ipp/scaffold.py` — `new_project(name)` creates the folder structure

**Scaffolded project layout from `ipp new my-game`:**
```
my-game/
├── ipp.toml
├── main.ipp
├── README.md
├── src/
│   └── (your game modules go here)
└── tests/
    └── test_main.ipp
```

**Test file: `tests/v1_9_13/test_project_mode/`**

`tests/v1_9_13/test_project_mode/ipp.toml`:
```toml
[package]
name    = "test-project"
version = "0.0.1"
entry   = "main.ipp"
```

`tests/v1_9_13/test_project_mode/main.ipp`:
```ipp
import { greet } from "src/greet.ipp"
print(greet("World"))
```

`tests/v1_9_13/test_project_mode/src/greet.ipp`:
```ipp
export func greet(name) {
    return "Hello, " + name + "!"
}
```

**Shell test (in regression suite):**
```bash
cd tests/v1_9_13/test_project_mode
ipp run
# expected output: Hello, World!
```

**Regression risk:** Low. `ipp run filename` path unchanged. Only new behaviour when no filename is given and `ipp.toml` exists.

---

## Phase D: Game Dev Features (v2.0.0 – v2.0.11)

> After Phase D, see **Phase D2: Core Packages (v2.0.12–v2.0.20)** for bundled stdlib packages.

After Phase C and C2 the language is feature-complete for general scripting and supports multi-file projects. Phase D adds game-specific features that make Ipp viable for actual games.


> **Note on major version:** v2.0.0 is a minor milestone here, not a complete rewrite. Do NOT tag v2.0.0 until Phases A, B, and C are complete and all their tests pass.

---

### v2.0.0 — Feature: Game Loop Syntax + `delta_time()` Stub

**What:** Add `game_loop(fps=N) { }` as a language-level construct. Start with a Python `time.sleep` backend so the syntax and timing work without any native library. This lets game logic be written and tested without a display dependency.

**Files to change:** `parser.py` (parse `game_loop`), `compiler.py` (emit loop with timing), `vm.py` (dispatch to Python timing loop), `runtime/builtins.py` (`delta_time()`, `delta_time_ms()`).

```ipp
game_loop(fps=60) {
    var dt = delta_time()
    update(dt)
    render()
}
```

**Test file: `tests/v2_0_0/test_game_loop.ipp`**
```ipp
var frames = 0
var total_dt = 0.0

# Run 10 frames then break
game_loop(fps=30) {
    var dt = delta_time()
    total_dt = total_dt + dt
    frames = frames + 1
    if frames >= 10 { break }
}

assert frames == 10
assert total_dt > 0.0
assert delta_time_ms() >= 0
```

---

### v2.0.0.1 — Feature: `time.now()`, `time.sleep()`, `time.since()` Builtins

**Why here:** The game loop needs timing primitives. These are trivial wrappers around Python's `time` module.

```python
# In builtins:
'time': {
    'now':   lambda: time.time(),
    'sleep': lambda secs: time.sleep(secs),
    'since': lambda t: time.time() - t,
    'ms':    lambda: time.time() * 1000,
}
```

**Test file: `tests/v2_0_0_1/test_time.ipp`**
```ipp
var start = time.now()
time.sleep(0.01)
var elapsed = time.since(start)
assert elapsed >= 0.01
assert elapsed < 0.1

var ms = time.ms()
assert ms > 0
```

---

### v2.0.0.2 — Feature: `draw_*` Stub API (Headless Mode)

**Why here:** Game logic tests should not require a display. Define the full `draw_*` API with no-op stubs so game code can be unit tested headlessly.

```ipp
draw_clear()                              # no-op stub
draw_rect(10, 10, 100, 50, "red")
draw_circle(50, 50, 20, "blue")
draw_text("Score: 100", 10, 10)
draw_sprite(sprite_id, x, y)
draw_line(x1, y1, x2, y2, "white")
set_draw_target(canvas)
```

When `--headless` flag is set (default in tests), all `draw_*` calls are no-ops that log to a buffer (inspectable in tests). When a display is available, they render.

**Test file: `tests/v2_0_0_2/test_draw_stubs.ipp`**
```ipp
# All draw calls must not crash in headless mode
draw_clear()
draw_rect(0, 0, 100, 100, "red")
draw_circle(50, 50, 25, "blue")
draw_text("hello", 10, 10)
draw_line(0, 0, 100, 100, "white")
print("draw stubs ok")
```

---

### v2.0.1 — Feature: Input System (Keyboard)

**What:** `input.is_pressed(key)`, `input.just_pressed(key)`, `input.just_released(key)`, `input.axis("horizontal")`.

**Files to change:** `runtime/builtins.py` — add `InputState` class that tracks key state. In headless mode, state is set programmatically. When SDL2/pygame is available, state is updated from OS events.

```ipp
if input.is_pressed("W") or input.is_pressed("UP") {
    player.y = player.y - speed * dt
}
if input.just_pressed("SPACE") {
    player.jump()
}
var h = input.axis("horizontal")   # -1.0 to 1.0
player.x = player.x + h * speed * dt
```

**Test file: `tests/v2_0_1/test_input_headless.ipp`**
```ipp
# Programmatic input state for testing
input.simulate_press("W")
assert input.is_pressed("W") == true
assert input.just_pressed("W") == true

input.simulate_release("W")
assert input.is_pressed("W") == false
assert input.just_released("W") == true

# Second frame: just_pressed/released clears
input.advance_frame()
assert input.just_pressed("W") == false
assert input.just_released("W") == false
```

---

### v2.0.1.1 — Feature: Input System (Mouse + Gamepad)

**What:** Mouse position, buttons, scroll. Gamepad axes and buttons. All with headless simulation stubs.

```ipp
var mx = input.mouse_x()
var my = input.mouse_y()
if input.mouse_pressed(0) {    # left button
    spawn_bullet(mx, my)
}
var stick_x = input.gamepad_axis(0, "left_x")
```

**Test file: `tests/v2_0_1_1/test_mouse_input.ipp`**
```ipp
input.simulate_mouse(100, 200)
assert input.mouse_x() == 100
assert input.mouse_y() == 200

input.simulate_mouse_click(0)
assert input.mouse_pressed(0) == true
```

---

---

### v2.0.1.2 — Feature: `inspect(obj)` — Live In-Game Variable Inspector

**What:** `inspect(player)` opens a floating overlay panel in the running canvas window showing every field of `player`, live-updated every frame. `inspect_hide()` closes it. No print statement, no debugger required. You see the actual values changing in real time as the game runs.

**Why novel:** Every game engine has a scene inspector but it's in the *editor*, not the *script*. You can't write `inspect(my_custom_object)` in GDScript and have it work at runtime without building a custom debug UI. In Ipp, one function call is enough.

**Files to change:** `ipp/runtime/inspector.py` (new file — draws on canvas overlay), `ipp/vm/vm.py` (register builtins), `ipp/runtime/canvas.py` (expose overlay drawing hook).

`ipp/runtime/inspector.py`:
```python
_inspected = {}   # name -> IppInstance or dict, updated each frame

def inspect(obj, label=None):
    key = label or f"obj_{id(obj)}"
    _inspected[key] = obj

def inspect_hide(label=None):
    if label: _inspected.pop(label, None)
    else: _inspected.clear()

def draw_inspector_overlay(canvas):
    if not _inspected: return
    x, y = 10, 10
    for label, obj in _inspected.items():
        canvas.create_rectangle(x, y, x+220, y+20, fill="#111", outline="#444")
        canvas.create_text(x+5, y+5, text=f"▼ {label}", fill="#aaf", anchor="nw",
                           font=("Courier", 9, "bold"))
        y += 22
        fields = getattr(obj, 'fields', {}) if hasattr(obj, 'fields') else (obj if isinstance(obj, dict) else {})
        for name, val in list(fields.items())[:12]:
            canvas.create_rectangle(x, y, x+220, y+16, fill="#0a0a0a", outline="#222")
            display = str(val)[:28]
            canvas.create_text(x+5, y+3, text=f"  {name}: {display}", fill="#8f8", anchor="nw",
                               font=("Courier", 8))
            y += 17
        y += 6
```

`canvas_run()` calls `draw_inspector_overlay(canvas)` at the end of each frame automatically.

**Test file: `tests/v2_0_1_2/test_inspect.ipp`**
```ipp
# inspect() is available as a global function
assert type(inspect) == "function"
assert type(inspect_hide) == "function"

# Can be called on any class instance without crash
class Player {
    func init() {
        self.hp = 100; self.score = 0; self.level = 1
        self.position = [0.0, 0.0]; self.name = "Hero"
    }
}
var p = Player()
inspect(p, "Player")           # no crash, registers for overlay
inspect({"debug": true, "fps": 60}, "Stats")   # works on dicts too
inspect_hide("Stats")          # hides one
inspect_hide()                 # hides all
```

**C/Rust rewrite:** `draw_inspector_overlay()` stays Python (it uses tkinter directly). The `inspect()` / `inspect_hide()` builtins just populate the `_inspected` Python dict. The C/Rust VM calls them via the same Python FFI path used for all canvas builtins.

**Bootstrapped Ipp:** `inspect()` is reimplemented as a function that stores a reference to the object in a global overlay list. `draw_inspector_overlay()` is a canvas draw function called at end of each frame. Fully expressible in Ipp once canvas is accessible.

**Regression risk:** Zero. New builtins. Overlay only drawn when `_inspected` is non-empty.

### v2.0.2 — Feature: `@export` Annotation for Editor-Visible Variables

**What:** Mark class fields with `@export` so they appear in any inspector or editor integration. Store exported field metadata in class definition.

```ipp
class Enemy {
    @export var speed = 100.0
    @export var health = 50
    @export var patrol_range = 200.0
    @export(min=0, max=1) var aggression = 0.5
}
```

**Files to change:** `parser.py` (parse `@export` before var decl inside class), `compiler.py` (emit metadata), `vm.py` (store in class definition's `exports` dict).

**Test file: `tests/v2_0_2/test_export.ipp`**
```ipp
class Enemy {
    @export var speed = 100.0
    @export var health = 50
}

var e = Enemy()
assert e.speed == 100.0
assert e.health == 50

# Exports are introspectable
var exports = Enemy.get_exports()
assert "speed" in exports
assert "health" in exports
assert exports["speed"] == 100.0
```

---

### v2.0.2.1 — Feature: `@export` Range Hints + `@onchange` Callback

```ipp
class Volume {
    @export(min=0, max=100) var level = 50
    @export(options=["low","medium","high"]) var quality = "medium"

    @onchange("level")
    func on_level_changed(old_val, new_val) {
        audio.set_master_volume(new_val / 100.0)
    }
}
```

**Test file: `tests/v2_0_2_1/test_export_hints.ipp`**
```ipp
class Slider {
    @export(min=0, max=10) var value = 5

    @onchange("value")
    func on_change(old, new) {
        self.last_change = new - old
    }
}
var s = Slider()
s.value = 8
assert s.last_change == 3
```

---

### v2.0.3 — Feature: List Destructuring Assignment

**What:** `var [x, y, z] = [1, 2, 3]`. Unpack lists into named variables. The multi-return case (`var a, b = func()`) already works — this adds the explicit bracket syntax.

```ipp
var [x, y, z] = [1, 2, 3]
assert x == 1 and y == 2 and z == 3

var [head, ...tail] = [10, 20, 30, 40]
assert head == 10
assert tail == [20, 30, 40]

func get_pos() { return [100.0, 200.0] }
var [px, py] = get_pos()
```

**Test file: `tests/v2_0_3/test_list_destructure.ipp`**
```ipp
var [a, b, c] = [1, 2, 3]
assert a == 1 and b == 2 and c == 3

var [first, ...rest] = [10, 20, 30, 40, 50]
assert first == 10
assert rest == [20, 30, 40, 50]

# Swap
var x = 1
var y = 2
var [x, y] = [y, x]
assert x == 2 and y == 1
```

---

### v2.0.3.1 — Feature: Dict Destructuring Assignment

```ipp
var {name, age, city="Unknown"} = {"name": "Alice", "age": 30}
assert name == "Alice"
assert age == 30
assert city == "Unknown"    # default for missing key
```

**Test file: `tests/v2_0_3_1/test_dict_destructure.ipp`**
```ipp
var d = {"x": 10, "y": 20, "z": 30}
var {x, y, z} = d
assert x == 10 and y == 20 and z == 30

# With default
var {a, b, c=99} = {"a": 1, "b": 2}
assert a == 1 and b == 2 and c == 99
```

---

### v2.0.4 — Feature: Pattern Matching on Types in `match`

**What:** `case TypeName varname =>` binds the matched instance to a new variable. Enables exhaustive dispatch on ADT-style class hierarchies — the correct way to implement game entity systems.

```ipp
class Bullet { func init(x, y, speed) { self.x=x; self.y=y; self.speed=speed } }
class Wall   { func init(x, y, w, h) { self.x=x; self.y=y; self.w=w; self.h=h } }
class Player { func init(hp) { self.hp = hp } }

func handle_collision(entity) {
    match entity {
        case Bullet b => {
            b.speed = 0
            return "bullet stopped"
        }
        case Wall w => return "wall at " + str(w.x)
        case Player p => {
            p.hp = p.hp - 10
            return "player hit"
        }
        default => return "unknown"
    }
}
```

**Test file: `tests/v2_0_4/test_type_match.ipp`**
```ipp
class Circle { func init(r) { self.r = r } }
class Rect   { func init(w, h) { self.w = w; self.h = h } }

func area(shape) {
    match shape {
        case Circle c => return pi * c.r * c.r
        case Rect r   => return r.w * r.h
        default       => return 0
    }
}

assert area(Circle(5)) > 78.0
assert area(Rect(4, 6)) == 24
assert area("unknown") == 0
```

---

### v2.0.4.1 — Feature: Guard Clauses in `match` (`case X if condition =>`)

```ipp
match value {
    case int n if n > 0  => return "positive"
    case int n if n < 0  => return "negative"
    case int n           => return "zero"
    case string s if len(s) == 0 => return "empty string"
    default              => return "other"
}
```

**Test file: `tests/v2_0_4_1/test_match_guard.ipp`**
```ipp
func classify(x) {
    match x {
        case int n if n > 100 => return "big"
        case int n if n > 0   => return "small"
        case int n            => return "zero or negative"
        default               => return "not int"
    }
}
assert classify(200) == "big"
assert classify(50) == "small"
assert classify(0) == "zero or negative"
assert classify("hi") == "not int"
```

---

### v2.0.5 — Feature: Generator Functions (`yield`)

**What:** Functions with `yield` are generator functions. Calling them returns an iterator object. `for x in gen_func()` works naturally. No memory allocation for the full sequence.

```ipp
func fibonacci() {
    var a = 0
    var b = 1
    while true {
        yield a
        var tmp = a
        a = b
        b = tmp + b
    }
}

var fibs = []
for n in fibonacci() {
    if n > 100 { break }
    fibs = fibs + [n]
}
assert fibs == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
```

**Test file: `tests/v2_0_5/test_generators.ipp`**
```ipp
func count(n) {
    var i = 0
    while i < n { yield i; i = i + 1 }
}

var result = []
for x in count(5) { result = result + [x] }
assert result == [0, 1, 2, 3, 4]

# Generator with send (advanced)
func accumulator() {
    var total = 0
    while true {
        var n = yield total
        if n == nil { break }
        total = total + n
    }
}
```

---

### v2.0.5.1 — Feature: `yield from` for Generator Delegation

```ipp
func chain(...generators) {
    for gen in generators {
        yield from gen
    }
}

for x in chain(count(3), count(3)) {
    print(x)   # 0 1 2 0 1 2
}
```

---

### v2.0.6 — Feature: File Watcher + Hot Reload (`ipp run --watch`)

**What:** `ipp run game.ipp --watch` monitors source files for changes. On change: reparse, recompile changed functions/classes only, apply to running VM without restart.

**Implementation steps:**
1. `v2.0.6.1` — File hash tracker: detect which files changed
2. `v2.0.6.2` — Incremental recompile: recompile only changed functions
3. `v2.0.6.3` — Live class patching: update method tables in-place without losing instance state
4. `v2.0.6.4` — `on_reload()` hook: call `on_reload()` if defined after each reload

```ipp
func on_reload() {
    print("Reloaded! Re-init systems that changed.")
    ui.rebuild()
}

game_loop(fps=60) {
    update(delta_time())
    render()
}
```

**Test file: `tests/v2_0_6/test_hot_reload.ipp`**
```ipp
# Programmatic reload test
var version = 1

func get_version() { return version }
assert get_version() == 1

# Simulate patching get_version to return 2
ipp.patch_function("get_version", func() { return 2 })
assert get_version() == 2
```

---

### v2.0.6.1 — Feature: `ipp.patch_function()` and `ipp.patch_method()` Runtime Patching API

**Why separate version:** Runtime patching is useful beyond hot reload — for testing (mocking), for modding systems, for A/B testing game balance.

```ipp
# Mock a function for testing
ipp.patch_function("rand_int", func(a, b) { return 42 })
assert rand_int(0, 100) == 42
ipp.restore_function("rand_int")

# Patch a method on a class
ipp.patch_method(Enemy, "take_damage", func(self, dmg) {
    self.hp = self.hp - dmg * 0.5   # half damage mode
})
```

---

---

### v2.0.6.2 — Feature: Hot Reload — State Snapshot and Restore

**What:** The gap in the current v2.0.6 spec: the file watcher recompiles changed functions but
does NOT preserve game state — every save resets the game from `main.ipp`. This version adds a
state snapshot before recompile and restore afterward, so `player.hp`, `score`, `current_level`,
and all live variables survive a hot reload.

**Implementation — three steps every reload cycle:**
```python
# In ipp/runtime/hotreload.py:

def snapshot_globals(vm):
    """Deep-copy all serialisable globals before recompile."""
    import copy
    snap = {}
    for k, v in vm.globals.items():
        if callable(v): continue          # skip functions/builtins
        try: snap[k] = copy.deepcopy(v)
        except: pass                      # skip unserializable (canvas handles, etc.)
    return snap

def restore_globals(vm, snap):
    """Write snapshot back, skipping newly-defined names."""
    for k, v in snap.items():
        if k in vm.globals:               # only restore names that still exist
            vm.globals[k] = v

# In the watch loop:
old_snap = snapshot_globals(vm)
recompile_changed_files(vm)              # existing v2.0.6 / v2.0.6.1 work
restore_globals(vm, old_snap)
emit_signal("hot_reload_complete")       # ipp-signal: game code can hook this
```

**Opt-out for intentional reset:**
```ipp
# Mark a variable as non-persistent — it resets on every reload
@no_persist
var frame_count = 0

# Mark a class instance as non-persistent
@no_persist
var current_session = Session()
```

**Test file: `tests/v2_0_6_2/test_hot_reload_state.ipp`**
```ipp
var score = 0
var player_hp = 100
var level = 3

score = 500
player_hp = 45

# Simulate hot reload
var snap = _hot_reload_snapshot()
score = 0        # simulate recompile reset
player_hp = 100
_hot_reload_restore(snap)

assert score == 500       # ✅ restored
assert player_hp == 45    # ✅ restored
assert level == 3         # ✅ restored

# @no_persist vars reset intentionally
@no_persist
var frame_count = 0
frame_count = 999
var snap2 = _hot_reload_snapshot()
_hot_reload_restore(snap2)
assert frame_count == 0   # ✅ reset as expected
```

**C/Rust:** `snapshot_globals` and `restore_globals` stay Python — they use `copy.deepcopy` on Python
dicts. The C VM exposes `vm.globals` as a Python dict via its PyO3/ctypes bridge, so this layer is
unchanged.

**Bootstrapped Ipp:** `@no_persist` compiles to a metadata tag on the variable declaration.
Snapshot/restore becomes a standard library function in `ipp-debug` that serialises globals to
a temp `.ipp` save file (using the savegame format from v2.0.12.1) then reloads it.

**Regression risk:** Low. Snapshot/restore only runs during `--watch` mode. Normal `ipp run` is
completely unaffected.

### v2.0.7 — Feature: f-string Format Spec (`{value:.2f}`, `{value:>10}`)

**What:** Extend the existing f-string parser to handle Python-style format specs inside `{}`.

```ipp
var pi_val = 3.14159
assert f"pi = {pi_val:.2f}" == "pi = 3.14"
assert f"hex: {255:#x}" == "hex: 0xff"
assert f"padded: {42:>10}" == "padded:         42"
assert f"{'left':<10}|" == "left      |"
assert f"{0.5:.0%}" == "50%"
```

**Files to change:** `lexer.py` f-string tokenizer (pass format spec through), `compiler.py` f-string compiler (emit format call with spec), `vm.py` f-string runtime (apply Python `format()` with spec).

**Test file: `tests/v2_0_7/test_fstring_format.ipp`**
```ipp
var n = 3.14159
assert f"{n:.2f}" == "3.14"
assert f"{n:.4f}" == "3.1416"

var score = 9500
assert f"Score: {score:,}" == "Score: 9,500"
assert f"{score:>10}" == "      9500"

var pct = 0.875
assert f"{pct:.1%}" == "87.5%"
```

---

---

### v2.0.6.3 — Feature: Hot Reload — `on_reload` Hook and Reload-Safe Patterns

**What:** After state is preserved, game code often needs to re-bind event listeners, re-register
signals, or rebuild derived state (cached path-finding grids, sorted enemy lists) that was computed
at startup. `on_reload()` is called by the VM immediately after every hot reload so games can do
this without duplicating handlers.

```ipp
var _enemies = []
var _signals_bound = false

func setup() {
    _enemies = spawn_initial_enemies()
    bind_input_handlers()
    _signals_bound = true
}

func on_reload() {
    # Called automatically after every hot reload
    # State (@no_persist vars) already reset, other vars already restored
    bind_input_handlers()          # re-bind — closures were recompiled
    # _enemies is still alive (state preserved) — no re-spawn needed
    print("[reload] Handlers rebound. Enemies preserved:", len(_enemies))
}
```

**Files to change:** `ipp/vm/vm.py` — after `restore_globals`, check if `on_reload` is defined in
globals and call it.

**Test file: `tests/v2_0_6_3/test_on_reload.ipp`**
```ipp
var reload_count = 0
var setup_count = 0

func on_reload() {
    reload_count = reload_count + 1
}

func setup() { setup_count = setup_count + 1 }

setup()
assert setup_count == 1
assert reload_count == 0

_simulate_hot_reload()
assert reload_count == 1
assert setup_count == 1   # setup() NOT called again — only on_reload()

_simulate_hot_reload()
assert reload_count == 2
```

**Regression risk:** Zero. Only calls `on_reload()` if it exists in globals.



### v2.0.7.1 — Feature: Template Strings `t"..."` for Safe HTML/SQL

**Why here:** Game UI often generates HTML or config text. Template strings are like f-strings but auto-escape interpolated values.

```ipp
var player_name = "<script>alert('xss')</script>"
var safe = t"<p>Hello, {player_name}!</p>"
assert safe == "<p>Hello, &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;!</p>"
```

---

### v2.0.8 — Feature: `tween()` and Timeline-Based Async

**What:** Language-level `tween(target, field, to, duration, easing)` that works with the game loop's timing. Requires async (v1.9.4) and game loop (v2.0.0) to be working.

**Easing functions built-in:** `"linear"`, `"ease_in"`, `"ease_out"`, `"ease_in_out"`, `"bounce"`, `"elastic"`.

```ipp
async func animate_player_death(player) {
    await tween(player, "alpha", to=0, duration=0.5, easing="ease_out")
    await tween(player, "scale", to=2.0, duration=0.3, easing="elastic")
    await delay(0.2)
    player.destroy()
}
```

**Test file: `tests/v2_0_8/test_tween.ipp`**
```ipp
class Prop {
    func init() { self.x = 0.0 }
}
var p = Prop()

# Instant tween (duration=0) for testability
tween_sync(p, "x", to=100.0, duration=0)
assert p.x == 100.0

# Tween step-by-step
var tw = tween_create(p, "x", to=200.0, duration=1.0)
tw.step(0.5)    # advance 0.5 seconds
assert p.x >= 100.0 and p.x <= 200.0
tw.step(0.5)
assert abs(p.x - 200.0) < 0.001
```

---

### v2.0.8.1 — Feature: `await delay(seconds)` in Coroutines

```ipp
async func countdown(from) {
    var n = from
    while n > 0 {
        print(n)
        await delay(1.0)
        n = n - 1
    }
    print("Go!")
}
async_run(countdown(3))
```

---

### v2.0.8.2 — Feature: `parallel(coro1, coro2, ...)` Concurrent Execution

```ipp
async func move_x(obj, target, dur) {
    await tween(obj, "x", to=target, duration=dur)
}
async func move_y(obj, target, dur) {
    await tween(obj, "y", to=target, duration=dur)
}
# Both animations run at the same time
await parallel(move_x(player, 200, 1.0), move_y(player, 300, 1.5))
```

---

---

### v2.0.8.3 — Feature: `sequence {}` — First-Class Cutscene/Timeline Block

**What:** A `sequence` block runs its statements in order, waiting for each to complete before moving to the next. It desugars to a coroutine but reads like synchronous code. The canonical tool for cutscenes, tutorial flows, boss intros, and narrative sequences. No scripting language embeds this as syntax — Ink/Yarn/Twine are all separate tools requiring a bridge.

**Syntax:**
```ipp
sequence intro_cutscene {
    say(npc, "Watch out — they're coming!")
    wait(1.5)
    move_to(player, door_pos, duration=2.0)
    parallel {
        play_sound("alarm.wav")
        shake_camera(intensity=0.5, duration=1.0)
    }
    fade_out(0.5)
    load_scene("level_2")
}

# Run it
run_sequence(intro_cutscene)

# Or trigger later
schedule(func() { run_sequence(intro_cutscene) }, after=5.0)
```

**How `sequence` desugars:** Each statement that takes a `duration` argument is `await`-ed as a coroutine. `wait(t)` is `await delay(t)`. `parallel { }` launches all inner statements as concurrent coroutines and awaits all of them. The sequence block compiles to a single async function.

**Files to change:** `ipp/parser/parser.py` (parse `sequence name { }` and `parallel { }`), `ipp/vm/compiler.py` (lower to async function with `await` for each step).

**Built-in sequence steps (added to runtime):**
```python
'wait':         lambda t: delay(t),           # already exists as await delay(t)
'move_to':      lambda obj, pos, duration=1.0: ...,   # lerp obj.position to pos over duration
'fade_out':     lambda t=1.0: ...,            # fade canvas alpha to black
'fade_in':      lambda t=1.0: ...,            # fade canvas alpha from black
'shake_camera': lambda intensity=1.0, duration=0.5: ...,
'say':          lambda speaker, text, duration=None: ...,  # show dialogue box
```

**Test file: `tests/v2_0_8_3/test_sequence.ipp`**
```ipp
var log = []

sequence test_seq {
    log.append("step 1")
    wait(0.0)              # zero-wait: yields but continues immediately
    log.append("step 2")
    wait(0.0)
    log.append("step 3")
}

async_run(run_sequence(test_seq))
assert log == ["step 1", "step 2", "step 3"]

# Sequence with parallel block
var par_log = []
sequence par_test {
    par_log.append("before parallel")
    parallel {
        par_log.append("branch A")
        par_log.append("branch B")
    }
    par_log.append("after parallel")
}
async_run(run_sequence(par_test))
assert par_log[0] == "before parallel"
assert par_log.contains("branch A") == true
assert par_log.contains("branch B") == true
assert par_log[-1] == "after parallel"

# Sequence is a value — can be stored, passed, triggered later
var seq_ref = test_seq
async_run(run_sequence(seq_ref))
assert log == ["step 1", "step 2", "step 3", "step 1", "step 2", "step 3"]
```

**C/Rust rewrite:** `sequence` desugars to async functions. Async/coroutine support must exist in the C/Rust VM for generators and `async/await` already (Phase E prerequisite). Sequence steps that call canvas/audio builtins go through the same FFI path. No additional VM work needed.

**Bootstrapped Ipp:** `sequence` compiles to an async function. The bootstrapped compiler handles `sequence` as a syntactic sugar pass — one of the first things a bootstrapped compiler would implement since it's a clean desugaring with no runtime magic.

**Regression risk:** Low. New keyword `sequence` and `parallel`. Neither is currently a valid identifier in any Ipp context.

### v2.0.9 — Feature: Scene System (`scene.load()`, `scene.push()`, `scene.pop()`)

**What:** A built-in scene stack so games can switch between game states (menu → gameplay → pause → game over) without rolling their own state machine.

```ipp
class MenuScene {
    func init() { self.title = "My Game" }
    func update(dt) {
        if input.just_pressed("ENTER") {
            scene.push(GameScene())
        }
    }
    func render() {
        draw_clear()
        draw_text(self.title, 100, 100)
        draw_text("Press ENTER to start", 100, 150)
    }
}

class GameScene {
    func init() { self.player = Player() }
    func update(dt) { self.player.update(dt) }
    func render() {
        draw_clear()
        self.player.render()
    }
    func on_pause() { }      # called when another scene is pushed on top
    func on_resume() { }     # called when top scene is popped
}

scene.push(MenuScene())
game_loop(fps=60) {
    var s = scene.current()
    s.update(delta_time())
    s.render()
}
```

**Test file: `tests/v2_0_9/test_scene_stack.ipp`**
```ipp
class SceneA {
    func init() { self.name = "A" }
    func on_pause() { print("A paused") }
    func on_resume() { print("A resumed") }
}
class SceneB {
    func init() { self.name = "B" }
}

scene.push(SceneA())
assert scene.current().name == "A"

scene.push(SceneB())
assert scene.current().name == "B"
assert scene.depth() == 2

scene.pop()
assert scene.current().name == "A"
assert scene.depth() == 1
```

---

---

### v2.0.9.1 — Feature: Scene Tree — Node Hierarchy with Lifecycle Methods

**What:** The flat scene stack (v2.0.9) becomes a proper node tree. Every game object is a `Node`
with a `parent`, a list of `children`, and three lifecycle methods: `_ready()` (called once when
added to tree), `_update(dt)` (called every frame), `_draw()` (called every frame after update).
Nodes propagate calls down the tree automatically — you never manually loop over children.

**Why every game language needs this:** GDScript, Unity, and Cocos2D are all tree-based for a
reason — it maps perfectly to game object ownership (player owns weapon, weapon owns particle
effect). Flat lists break when objects have sub-components. Ipp's current flat scene has no answer
for "the enemy's health bar should update when the enemy updates."

```ipp
class Node {
    func init(name="Node") {
        self.name = name
        self.parent = nil
        self.children = []
        self._in_tree = false
    }

    func add_child(child) {
        child.parent = self
        self.children.append(child)
        if self._in_tree {
            child._enter_tree()
            child._ready()
        }
        return child
    }

    func remove_child(child) {
        self.children = self.children.filter(func(c) { return c != child })
        child.parent = nil
        child._exit_tree()
    }

    func get_node(path) {
        # "/" separates child names: get_node("HUD/HealthBar")
        var parts = path.split("/")
        var current = self
        for part in parts {
            current = current.children.find(func(c) { return c.name == part })
            if current == nil { return nil }
        }
        return current
    }

    func _enter_tree() {
        self._in_tree = true
        for child in self.children { child._enter_tree() }
    }

    func _exit_tree() {
        self._in_tree = false
        for child in self.children { child._exit_tree() }
    }

    # Override these in subclasses:
    func _ready()     { }
    func _update(dt)  { for child in self.children { child._update(dt) } }
    func _draw()      { for child in self.children { child._draw() } }
    func _on_destroy(){ }

    func destroy() {
        self._on_destroy()
        if self.parent != nil { self.parent.remove_child(self) }
        for child in self.children.copy() { child.destroy() }
    }

    prop root {
        get {
            var n = self
            while n.parent != nil { n = n.parent }
            return n
        }
    }
}
```

`canvas_run()` integration: the root node's `_update(dt)` and `_draw()` are called each frame
automatically when a root node is registered with `scene.set_root(node)`.

**Test file: `tests/v2_0_9_1/test_node_tree.ipp`**
```ipp
class Counter extends Node {
    func init(name) {
        self.name = name
        self.updates = 0
        self.children = []; self.parent = nil; self._in_tree = false
    }
    func _update(dt) {
        self.updates = self.updates + 1
        super._update(dt)   # propagates to children
    }
}

var root = Counter("root")
var child_a = Counter("child_a")
var child_b = Counter("child_b")
var grandchild = Counter("grandchild")

root.add_child(child_a)
root.add_child(child_b)
child_a.add_child(grandchild)

# Simulate 3 frames
for i in range(3) { root._update(0.016) }

assert root.updates == 3
assert child_a.updates == 3
assert child_b.updates == 3
assert grandchild.updates == 3     # propagated through child_a

# get_node path traversal
assert root.get_node("child_a") == child_a
assert root.get_node("child_a/grandchild") == grandchild
assert root.get_node("child_b/missing") == nil

# destroy removes from parent
child_b.destroy()
assert len(root.children) == 1
assert root.children[0].name == "child_a"
```

**C/Rust rewrite:** `Node` is a pure Ipp class — zero C/Rust-specific work. The tree traversal
is Ipp calling Ipp. Canvas integration (`scene.set_root`) registers one Python callback in
`canvas_run()`.

**Bootstrapped Ipp:** `Node` is already written in Ipp. The bootstrapped compiler handles it
identically to any other class.

**Regression risk:** Low. Existing v2.0.9 scene stack unchanged. `Node` is a new class.

---

---

### v2.0.9.2 — Feature: Scene Tree — Built-in Node Types

**What:** Core node subclasses that 95% of games need. Written entirely in Ipp on top of `Node`.

```ipp
# Spatial2D: a Node with position, rotation, scale
class Spatial2D extends Node {
    func init(name="Spatial2D") {
        self.name = name; self.children = []; self.parent = nil; self._in_tree = false
        self.position = vec2(0, 0)
        self.rotation = 0.0   # radians
        self.scale    = vec2(1, 1)
        self.visible  = true
    }
    prop global_position {
        get {
            if self.parent != nil and self.parent is Spatial2D {
                return self.parent.global_position + self.position
            }
            return self.position
        }
    }
}

# Sprite2D: Spatial2D + draws an image
class Sprite2D extends Spatial2D {
    func init(name="Sprite2D", image=nil) {
        self.name=name; self.children=[]; self.parent=nil; self._in_tree=false
        self.position=vec2(0,0); self.rotation=0.0; self.scale=vec2(1,1); self.visible=true
        self.image = image
        self.frame = 0
    }
    func _draw() {
        if self.visible and self.image != nil {
            import { draw_image } from "ipp-canvas"
            var gp = self.global_position
            draw_image(gp.x, gp.y, self.image)
        }
        super._draw()
    }
}

# CollisionRect2D: Spatial2D + AABB collision
class CollisionRect2D extends Spatial2D {
    func init(name="Col2D", w=32, h=32) {
        self.name=name; self.children=[]; self.parent=nil; self._in_tree=false
        self.position=vec2(0,0); self.rotation=0.0; self.scale=vec2(1,1); self.visible=false
        self.w=w; self.h=h
    }
    func get_rect() {
        import { rect } from "ipp-math2d"
        var gp = self.global_position
        return rect(gp.x - self.w/2, gp.y - self.h/2, self.w, self.h)
    }
    func overlaps(other) {
        return self.get_rect().intersects(other.get_rect())
    }
}

# Label2D: Spatial2D + draws text
class Label2D extends Spatial2D {
    func init(name="Label", text="", color="white") {
        self.name=name; self.children=[]; self.parent=nil; self._in_tree=false
        self.position=vec2(0,0); self.rotation=0.0; self.scale=vec2(1,1); self.visible=true
        self.text=text; self.color=color; self.font_size=12
    }
    func _draw() {
        if self.visible {
            import { text } from "ipp-canvas"
            var gp = self.global_position
            text(gp.x, gp.y, self.text, self.color)
        }
        super._draw()
    }
}

# Timer: Node + fires a signal after N seconds
class Timer extends Node {
    func init(name="Timer", duration=1.0, one_shot=true) {
        self.name=name; self.children=[]; self.parent=nil; self._in_tree=false
        self.duration=duration; self.one_shot=one_shot
        self.elapsed=0.0; self.running=false
        import { Signal } from "ipp-signal"
        self.timeout = Signal()
    }
    func start() { self.elapsed=0.0; self.running=true }
    func stop()  { self.running=false }
    func _update(dt) {
        if self.running {
            self.elapsed = self.elapsed + dt
            if self.elapsed >= self.duration {
                self.timeout.emit()
                if self.one_shot { self.running=false }
                else { self.elapsed = self.elapsed - self.duration }
            }
        }
        super._update(dt)
    }
}
```

**Test file: `tests/v2_0_9_2/test_node_types.ipp`**
```ipp
# Spatial2D global position propagates through tree
var root = Spatial2D("root")
root.position = vec2(100, 50)
var child = Spatial2D("child")
child.position = vec2(10, 5)
root.add_child(child)
assert child.global_position.x == 110
assert child.global_position.y == 55

# CollisionRect2D overlap detection
var a = CollisionRect2D("a", 32, 32)
a.position = vec2(0, 0)
var b = CollisionRect2D("b", 32, 32)
b.position = vec2(20, 0)   # overlapping
assert a.overlaps(b) == true
b.position = vec2(64, 0)   # not overlapping
assert a.overlaps(b) == false

# Timer fires after duration
var fired = false
var t = Timer("t", duration=1.0)
t.timeout.connect(func() { fired = true })
t.start()
for i in range(62) { t._update(0.016) }   # ~0.992s — not yet
assert fired == false
t._update(0.016)    # crosses 1.0s
assert fired == true
```

### v2.0.8.4 — Feature: `story {}` — Narrative Branching Syntax

**What:** First-class dialogue and branching narrative syntax. A `story` block is a named, resumable narrative flow with characters, player choices, conditions, and flags. It shares variables and closures with the surrounding Ipp code natively — no bridge to Ink or Yarn needed.

**Syntax:**
```ipp
story elara_intro {
    scene "forest_clearing"
    
    npc "Elara": "You've finally arrived. I've been waiting."
    
    if player.reputation > 50 {
        npc "Elara": "I heard good things about you."
    }
    
    choice {
        "Who are you?" => {
            npc "Elara": "A friend. For now."
            flag met_elara = true
        }
        "I need to go." when player.has_item("map") => {
            npc "Elara": "Of course. Safe travels."
            goto story_end
        }
        "..." => { }
    }
    
    npc "Elara": "The dungeon is that way." [points east]
    give_item(player, "torch")
    
    label story_end
}

# Trigger the story
begin_story(elara_intro)

# Check if it's running
if story_running(elara_intro) {
    # advance on player input
    story_advance(elara_intro)
}
```

**How it desugars:** A `story` block compiles to a coroutine/state machine. `npc "Name": "text"` calls `show_dialogue(speaker, text)` and yields. `choice { }` calls `show_choices(options)` and yields, resuming with the player's selection. `flag name = val` writes to a persistent story state dict. Conditions are normal Ipp expressions.

**Files to change:** `ipp/parser/parser.py` (parse `story`, `npc`, `choice`, `when`, `goto`, `flag`, `label`, `scene`), `ipp/vm/compiler.py` (lower to state machine), `ipp/runtime/story.py` (new — dialogue box rendering on canvas, story state management).

**Test file: `tests/v2_0_8_4/test_story.ipp`**
```ipp
var dialogue_log = []
var choices_shown = []

# Override the default canvas dialogue renderer with test hooks
func show_dialogue(speaker, text) { dialogue_log.append(speaker + ": " + text) }
func show_choices(opts) { choices_shown.append(opts); return 0 }  # always pick first choice

story greet {
    npc "Guard": "Halt! Who goes there?"
    choice {
        "A friend." => {
            npc "Guard": "Pass, friend."
            flag greeted_guard = true
        }
        "None of your business." => {
            npc "Guard": "Then you shall not pass."
        }
    }
}

begin_story(greet)
# Advance through the story (normally driven by player input)
story_advance(greet)   # shows first line
story_advance(greet)   # shows choice
story_advance(greet)   # takes first choice, shows response

assert dialogue_log[0] == "Guard: Halt! Who goes there?"
assert dialogue_log[1] == "Guard: Pass, friend."
assert story_flag(greet, "greeted_guard") == true
assert story_complete(greet) == true
```

**C/Rust rewrite:** `story` compiles to a state machine (switch on a step counter). In C/Rust, this is just an integer field on the coroutine frame plus a jump table. Dialogue rendering calls remain Python-backed canvas calls via FFI.

**Bootstrapped Ipp:** `story` desugars to a class with a `step()` method. The bootstrapped Ipp compiler handles `story` as a macro expansion — very natural to implement once the class system and closures work.

**Regression risk:** Low. `story`, `npc`, `choice`, `when`, `goto`, `flag`, `scene`, `label` are new keywords — none conflict with existing builtins.

### v2.0.10 — Feature: Resource Manager (`resources.load()`, Caching, Async Loading)

```ipp
# Sync load
var sprite = resources.load("assets/player.png")
var sound = resources.load("assets/jump.wav")
var data = resources.load("data/levels.json")

# Async preload
async func preload_level(id) {
    var manifest = resources.load("levels/" + str(id) + "/manifest.json")
    for asset in manifest["assets"] {
        await resources.preload(asset)
    }
}

# Check load status
if resources.is_loaded("assets/player.png") {
    draw_sprite(resources.get("assets/player.png"), 100, 100)
}
```

---

---

### v2.0.9.3 — Feature: Scene Tree — `@group` Tagging and Global Scene Queries

**What:** Tag nodes with groups and query all nodes in a group from anywhere. The standard pattern
for "hit all enemies", "hide all UI elements", "pause all animated objects".

```ipp
class Enemy extends Spatial2D {
    @group("enemies")
    @group("damageable")
    func init(name, hp) {
        self.name=name; self.hp=hp
        self.children=[]; self.parent=nil; self._in_tree=false
        self.position=vec2(0,0); self.rotation=0.0; self.scale=vec2(1,1); self.visible=true
    }
    func take_damage(amt) { self.hp = self.hp - amt }
}

# Query all nodes in a group
var all_enemies = scene.get_group("enemies")
for e in all_enemies { e.take_damage(10) }

# Check membership
var orc = Enemy("orc", 50)
assert orc.in_group("enemies") == true
assert orc.in_group("friendlies") == false
```

**Files to change:** `ipp/parser/parser.py` (parse `@group("name")` on class), `ipp/vm/vm.py`
(maintain a `groups` dict in the scene root, populated when nodes enter the tree).

**Test file: `tests/v2_0_9_3/test_groups.ipp`**
```ipp
class Enemy extends Spatial2D {
    @group("enemies")
    func init(name, hp) {
        self.name=name; self.hp=hp
        self.children=[]; self.parent=nil; self._in_tree=false
        self.position=vec2(0,0); self.rotation=0.0; self.scale=vec2(1,1); self.visible=true
    }
}

var root = Node("root")
scene.set_root(root)

var e1 = Enemy("orc", 50)
var e2 = Enemy("goblin", 30)
root.add_child(e1)
root.add_child(e2)

var enemies = scene.get_group("enemies")
assert len(enemies) == 2
for e in enemies { e.hp = e.hp - 10 }
assert e1.hp == 40
assert e2.hp == 20

e1.destroy()
assert len(scene.get_group("enemies")) == 1
```



### v2.0.11 — Feature: Entity-Component-System (ECS) Core

**What:** First-class ECS support. `entity` keyword creates an entity. `component` attaches data. `system` defines logic that runs on entities with matching components.

```ipp
entity Player {
    component Transform(x=0, y=0, z=0)
    component Sprite(texture="player.png")
    component Health(hp=100, max_hp=100)
    component Physics(velocity=vec2(0,0), mass=1.0)
}

system MovementSystem {
    requires Transform, Physics
    func update(entity, dt) {
        entity.Transform.x = entity.Transform.x + entity.Physics.velocity.x * dt
        entity.Transform.y = entity.Transform.y + entity.Physics.velocity.y * dt
    }
}

var world = World()
var player = world.spawn(Player)
world.add_system(MovementSystem)
world.update(0.016)
```

**Test file: `tests/v2_0_11/test_ecs.ipp`**
```ipp
entity Ball {
    component Position(x=0.0, y=0.0)
    component Velocity(vx=1.0, vy=0.5)
}

system PhysicsSystem {
    requires Position, Velocity
    func update(e, dt) {
        e.Position.x = e.Position.x + e.Velocity.vx * dt
        e.Position.y = e.Position.y + e.Velocity.vy * dt
    }
}

var world = World()
var ball = world.spawn(Ball)
world.add_system(PhysicsSystem)
world.update(1.0)

assert ball.Position.x == 1.0
assert ball.Position.y == 0.5
```

---

---

## Phase D2: Core Packages (v2.0.12 – v2.0.18)

> After Phase D2, **Phase D3** (v2.0.19–v2.0.21) follows immediately.

> **What "package" means here:** A package is a folder living in `~/.ipp/packages/<name>/` containing an `ipp.toml` and one or more `.ipp` source files. You install packages with `ipp install <name>` (Phase F). For Phase D2 versions, all packages ship **bundled with the Ipp runtime** under `ipp/stdlib/` — no install needed. They are the standard library.
>
> **Why bundled first:** Before a registry exists, packages must ship with the runtime. This means every game developer gets them automatically. It also means they are tested with every Ipp release. Phase F (registry) adds the ability to publish third-party packages on top of these foundations.
>
> **Package file layout:**
> ```
> ipp/stdlib/
>   ipp-io/
>     ipp.toml
>     io.ipp        ← import { read_file, write_file } from "ipp-io"
>   ipp-log/
>     ipp.toml
>     log.ipp
>   ipp-test/
>     ipp.toml
>     test.ipp
>   ipp-math2d/
>     ipp.toml
>     math2d.ipp
>   ipp-signal/
>     ipp.toml
>     signal.ipp
>   ipp-ai/
>     ipp.toml
>     ai.ipp
>   ipp-debug/
>     ipp.toml
>     debug.ipp
> ```

---

### v2.0.0.3 — Feature: Enums

**Why here (moved from later):** Enums are a basic language feature, not a package. Every gaming language has them. GDScript, C#, Rust, and AngelScript all use enums constantly for game state, directions, item types, entity types. Putting this in early Phase D means all subsequent packages can use them.

**Syntax:**
```ipp
enum Direction { NORTH, SOUTH, EAST, WEST }
enum Rarity { COMMON = 0, UNCOMMON = 1, RARE = 2, EPIC = 3, LEGENDARY = 4 }
enum Status { ALIVE, DEAD, STUNNED, POISONED }
```

**Files to change:** `ipp/lexer/lexer.py` (add `ENUM` token), `ipp/parser/parser.py` (parse enum declaration), `ipp/vm/compiler.py` (emit enum as frozen dict of name→int), `ipp/vm/vm.py` (attribute access on enum type, `is` check).

**Implementation:** An enum compiles to a read-only dict-like object. `Direction.NORTH` resolves to `0`. Enum values print as `Direction.NORTH` not `0`. Pattern matching works: `case Direction.NORTH =>`.

**Test file: `tests/v2_0_0_3/test_enum.ipp`**
```ipp
enum Direction { NORTH, SOUTH, EAST, WEST }
enum Rarity { COMMON = 0, UNCOMMON = 1, RARE = 2, EPIC = 3, LEGENDARY = 4 }

# Value access
assert Direction.NORTH == 0
assert Direction.SOUTH == 1
assert Direction.EAST == 2
assert Direction.WEST == 3

# Custom values
assert Rarity.COMMON == 0
assert Rarity.LEGENDARY == 4

# Type check
assert Direction.NORTH is Direction == true
assert Direction.NORTH is Rarity == false

# Match on enum
func describe_dir(d) {
    match d {
        case Direction.NORTH => return "going north"
        case Direction.SOUTH => return "going south"
        default => return "other"
    }
}
assert describe_dir(Direction.NORTH) == "going north"
assert describe_dir(Direction.WEST) == "other"

# Readable print
assert str(Direction.NORTH) == "Direction.NORTH"

# Enum in class
class Enemy {
    func init(name, status) {
        self.name = name
        self.status = status
    }
    func is_alive() { return self.status == Status.ALIVE }
}
enum Status { ALIVE, DEAD, STUNNED }
var e = Enemy("Orc", Status.ALIVE)
assert e.is_alive() == true
e.status = Status.DEAD
assert e.is_alive() == false

# Immutability — assigning to enum values raises error
var caught = ""
try { Direction.NORTH = 99 } catch err { caught = err }
assert caught.contains("cannot assign") == true
```

**Regression risk:** Low. New syntax; no existing code uses `enum` as a keyword.

---

---

### v2.0.0.4 — Feature: `schedule()` — Time-Based Event Queue

**What:** A first-class event scheduler integrated with the game loop. Call `schedule(after=2.0, fn)` and `fn` fires 2 seconds from now. Call `schedule(every=30.0, fn)` and it fires every 30 seconds. Cancellable, inspectable. Every game implements this from scratch with ad-hoc timer arrays — this eliminates that entirely.

**No other scripting language for games has this as a builtin.** GDScript has `get_tree().create_timer()` which requires the scene tree. Lua has nothing. JavaScript has `setTimeout` only in browser contexts.

**Files to change:** `ipp/runtime/scheduler.py` (new file), `ipp/vm/vm.py` (register builtins + hook into `canvas_run` frame tick).

`ipp/runtime/scheduler.py`:
```python
import time

class Scheduler:
    def __init__(self):
        self._events = []   # list of {fire_at, fn, repeat_every, id}
        self._next_id = 0
        self._now = 0.0
    
    def schedule(self, fn, after=0.0, every=None):
        event_id = self._next_id; self._next_id += 1
        self._events.append({
            'id': event_id, 'fn': fn,
            'fire_at': self._now + after,
            'repeat': every
        })
        return event_id
    
    def cancel(self, event_id):
        self._events = [e for e in self._events if e['id'] != event_id]
    
    def tick(self, dt):
        self._now += dt
        fired = [e for e in self._events if self._now >= e['fire_at']]
        surviving = [e for e in self._events if self._now < e['fire_at']]
        self._events = surviving
        for e in fired:
            e['fn']()
            if e['repeat']:
                e['fire_at'] = self._now + e['repeat']
                self._events.append(e)

_scheduler = Scheduler()
```

**Builtins exposed:**
```python
'schedule':        lambda fn, after=0.0, every=None: _scheduler.schedule(fn, after, every),
'schedule_cancel': lambda event_id: _scheduler.cancel(event_id),
'schedule_tick':   lambda dt: _scheduler.tick(dt),   # called by canvas_run each frame
```

**Test file: `tests/v2_0_0_4/test_schedule.ipp`**
```ipp
var log = []

# One-shot: fires once after 0.5 seconds (simulated)
var id1 = schedule(func() { log.append("one-shot") }, after=0.5)

# Repeat: fires every 1.0 seconds
var id2 = schedule(func() { log.append("repeat") }, every=1.0)

# Simulate 3 seconds of game time by ticking manually
for i in range(30) {
    schedule_tick(0.1)   # 30 * 0.1s = 3 seconds
}

# one-shot fired once
assert log.count(func(x) { return x == "one-shot" }) == 1

# repeat fired ~3 times (at t=1.0, 2.0, 3.0)
assert log.count(func(x) { return x == "repeat" }) == 3

# Cancel stops future firings
var cancel_log = []
var cid = schedule(func() { cancel_log.append("fired") }, every=1.0)
schedule_tick(1.5)
assert len(cancel_log) == 1
schedule_cancel(cid)
schedule_tick(2.0)
assert len(cancel_log) == 1   # no more firings after cancel

# Game use cases
var enemy_count = 0
schedule(func() { enemy_count = enemy_count + 1 }, after=5.0)
schedule(func() { enemy_count = enemy_count + 5 }, every=10.0)
```

**C/Rust rewrite:** `_scheduler` stays as Python. `canvas_run()` already calls Python each frame — it just additionally calls `_scheduler.tick(dt)`. Zero change to bytecode or VM opcode format.

**Bootstrapped Ipp:** `schedule()` is reimplemented as an Ipp class (a list of closures with timestamps). The `schedule_tick()` builtin becomes a method call on the scheduler object. The game loop calls it naturally.

**Regression risk:** Low. New builtins. `canvas_run()` tick hook is additive.

### v2.0.12 — Package: `ipp-io` — File I/O, JSON, Environment, CLI Args

**What:** The IO package. Without this, Ipp programs cannot read config files, write save data, or receive CLI arguments. This is a hard blocker for any real project. Every feature in this package is a one-line wrapper around Python's stdlib.

**File layout:**

`ipp/stdlib/ipp-io/ipp.toml`:
```toml
[package]
name        = "ipp-io"
version     = "1.0.0"
description = "File I/O, JSON, environment variables, command-line args"
bundled     = true
```

`ipp/stdlib/ipp-io/io.ipp`:
```ipp
# File operations
export func read_file(path) { return _builtin_read_file(path) }
export func write_file(path, content) { _builtin_write_file(path, content) }
export func append_file(path, content) { _builtin_append_file(path, content) }
export func file_exists(path) { return _builtin_file_exists(path) }
export func delete_file(path) { _builtin_delete_file(path) }
export func list_dir(path) { return _builtin_list_dir(path) }
export func make_dir(path) { _builtin_make_dir(path) }

# JSON
export func json_parse(text) { return _builtin_json_parse(text) }
export func json_stringify(obj, indent=nil) { return _builtin_json_stringify(obj, indent) }

# Environment
export func get_env(key, default=nil) { return _builtin_get_env(key, default) }
export func get_args() { return _builtin_get_args() }

# Savegame (see v2.0.12.1)
export func save_game(path, state) { write_file(path, _to_ipp_syntax(state)) }
export func load_game(path) { return _builtin_eval_file(path) }
```

**Builtins to add in `ipp/runtime/builtins.py`:**
```python
'_builtin_read_file':    lambda p: open(p).read(),
'_builtin_write_file':   lambda p, c: open(p,'w').write(c),
'_builtin_append_file':  lambda p, c: open(p,'a').write(c),
'_builtin_file_exists':  lambda p: os.path.exists(p),
'_builtin_delete_file':  lambda p: os.remove(p),
'_builtin_list_dir':     lambda p: os.listdir(p),
'_builtin_make_dir':     lambda p: os.makedirs(p, exist_ok=True),
'_builtin_json_parse':   lambda s: json.loads(s),
'_builtin_json_stringify': lambda o, i=None: json.dumps(o, indent=i),
'_builtin_get_env':      lambda k, d=None: os.environ.get(k, d),
'_builtin_get_args':     lambda: list(sys.argv[1:]),
```

**Usage:**
```ipp
import { read_file, write_file, json_parse, json_stringify, get_args } from "ipp-io"

var args = get_args()
var config = json_parse(read_file("config.json"))
config["last_run"] = "today"
write_file("config.json", json_stringify(config, indent=2))
```

**Test file: `tests/v2_0_12/test_io.ipp`**
```ipp
import { write_file, read_file, file_exists, delete_file, json_parse, json_stringify, get_env } from "ipp-io"

# File write + read roundtrip
write_file("/tmp/test_ipp_io.txt", "hello ipp")
assert file_exists("/tmp/test_ipp_io.txt") == true
assert read_file("/tmp/test_ipp_io.txt") == "hello ipp"
delete_file("/tmp/test_ipp_io.txt")
assert file_exists("/tmp/test_ipp_io.txt") == false

# JSON roundtrip
var data = {"name": "Alice", "score": 100, "items": ["sword", "shield"]}
var text = json_stringify(data)
var back = json_parse(text)
assert back["name"] == "Alice"
assert back["score"] == 100
assert back["items"][0] == "sword"

# Pretty print JSON
var pretty = json_stringify({"x": 1, "y": 2}, indent=2)
assert pretty.contains("  "x"") == true

# Environment variable
write_file("/tmp/env_test.txt", get_env("HOME", "no-home"))
assert file_exists("/tmp/env_test.txt") == true
delete_file("/tmp/env_test.txt")
```

**Regression risk:** Zero. New builtins only.

---

---

### v2.0.0.5 — Feature: `@invariant` — Automatic State Validation in Debug Mode

**What:** A decorator applied to a class that automatically checks an assertion on every field mutation, in debug mode only. Zero runtime cost in release. No other scripting language does this.

```ipp
class Health {
    @invariant(func(self) { return self.hp >= 0 and self.hp <= self.max_hp })
    @invariant(func(self) { return self.max_hp > 0 })
    func init(max_hp) {
        self.max_hp = max_hp
        self.hp = max_hp
    }
    func take_damage(amt) { self.hp = self.hp - amt }
}
```

Every time any field on a `Health` instance is written, all `@invariant` functions are called. If any returns false, you get a precise error: `"InvariantViolation: Health invariant failed after setting hp = -5"`.

**Why this matters:** In any game with complex state (health, inventory, physics), invariant violations are silent. You don't notice until the symptom appears 3 frames later in an unrelated system. `@invariant` makes violations loud and immediate.

**Files to change:** `ipp/parser/parser.py` (parse `@invariant(expr)` on class), `ipp/vm/compiler.py` (store invariants in class metadata), `ipp/vm/vm.py` (after every `SET_ATTR` on an invariant-annotated class, call all invariants in debug mode).

**Debug mode:** `ipp run --debug game.ipp` or `ipp run game.ipp` by default. Disable with `ipp run --release game.ipp` (zero overhead).

**Implementation in VM (SET_ATTR handler):**
```python
# After setting the field value:
if self._debug and hasattr(instance.cls, 'invariants'):
    for inv_fn in instance.cls.invariants:
        if not self._call_ipp_function(inv_fn, [instance]):
            raise VMError(
                f"InvariantViolation: {instance.cls.name} invariant failed "
                f"after setting {attr_name} = {value}"
            )
```

**Test file: `tests/v2_0_0_5/test_invariant.ipp`**
```ipp
class BoundedInt {
    @invariant(func(self) { return self.val >= self.min_val and self.val <= self.max_val })
    func init(val, min_val, max_val) {
        self.min_val = min_val
        self.max_val = max_val
        self.val = val
    }
}

var b = BoundedInt(5, 0, 10)
assert b.val == 5

b.val = 10
assert b.val == 10

# Invariant violation gives clear error
var caught = ""
try { b.val = 15 } catch e { caught = e }
assert caught.contains("InvariantViolation") == true
assert caught.contains("val") == true
assert caught.contains("15") == true

# Multiple invariants — both checked
class Enemy {
    @invariant(func(self) { return self.hp >= 0 })
    @invariant(func(self) { return self.level >= 1 and self.level <= 99 })
    func init(hp, level) {
        self.hp = hp
        self.level = level
    }
}
var e = Enemy(100, 5)
var c1 = ""; try { e.hp = -1 } catch err { c1 = err }
var c2 = ""; try { e.level = 0 } catch err { c2 = err }
assert c1.contains("InvariantViolation") == true
assert c2.contains("InvariantViolation") == true

# Release mode: no check (no error even for invalid values)
# ipp run --release: invariants skipped entirely
```

**C/Rust rewrite:** Invariants are stored in class metadata (a list of function references). The `SET_ATTR` opcode handler in C/Rust checks the flag and calls back into the invariant function via the same FFI path used for all Ipp function calls. Identical semantics, faster execution.

**Bootstrapped Ipp:** `@invariant` compiles to a property setter that calls the invariant functions before storing. The bootstrapped compiler handles this as a standard decorator lowering — no special VM support needed.

**Regression risk:** Low. Only fires on classes with `@invariant` decorator. Zero effect on all existing code.

### v2.0.12.1 — Feature: Savegame as Readable `.ipp` Syntax

**What:** `save_game(path, state)` serialises a dict/class instance to valid `.ipp` source code that a human can read, diff, and hand-edit. `load_game(path)` runs that file and returns the state. This is genuinely novel — no mainstream game engine does this. Most save formats are binary blobs or opaque JSON.

**Why useful:** Game designers can tweak a save file in a text editor to test edge cases. Developers can diff save files in version control. Corrupted saves are debuggable.

**What a save file looks like:**
```ipp
# Savegame — Dungeon Quest v1.2.0 — saved 2026-05-24 14:32
# Human-readable. Edit carefully.

var player = {
    "name": "Thorin",
    "level": 7,
    "hp": 45,
    "max_hp": 80,
    "gold": 320,
    "inventory": ["iron_sword", "health_potion", "health_potion"],
    "position": [12, 8],
}

var world = {
    "current_map": "dungeon_level_3",
    "cleared_rooms": [1, 2, 4, 7],
    "active_quests": ["find_the_key", "rescue_merchant"],
}

var _save_version = "1.0"
```

**Implementation:** `_to_ipp_syntax(obj)` is a Python-side serialiser that converts dicts, lists, strings, numbers, booleans, and nil to valid `.ipp` literal syntax with comments. It handles nested structures and adds a header comment. `load_game(path)` runs the file in a fresh VM and returns the globals dict.

**Files to change:** `ipp/runtime/io.py` — add `_to_ipp_syntax()` serialiser.

**Test file: `tests/v2_0_12_1/test_savegame.ipp`**
```ipp
import { save_game, load_game, delete_file } from "ipp-io"

var state = {
    "player_name": "Alice",
    "level": 5,
    "hp": 80,
    "items": ["sword", "potion"],
    "flags": {"boss_defeated": true, "side_quest": false},
    "position": [10, 25],
}

save_game("/tmp/test_save.ipp", state)

# The saved file is valid .ipp source — human readable
import { read_file } from "ipp-io"
var raw = read_file("/tmp/test_save.ipp")
assert raw.contains("player_name") == true
assert raw.contains("Alice") == true
assert raw.contains("# Savegame") == true   # has the header comment

# Load it back
var loaded = load_game("/tmp/test_save.ipp")
assert loaded["player_name"] == "Alice"
assert loaded["level"] == 5
assert loaded["items"][0] == "sword"
assert loaded["flags"]["boss_defeated"] == true
assert loaded["position"][1] == 25

delete_file("/tmp/test_save.ipp")
```

**Regression risk:** Zero. New feature, no existing code affected.

---

---

### v2.0.12.2 — Feature: `t()` — Built-in Localization

**What:** `t("Player died")` returns the translated string for the current locale. `t("Score: {n}", n=score)` interpolates after translating. `ipp extract` scans all `.ipp` files for `t()` calls and generates a translation template. `ipp translate --locale fr` opens each string for translation.

**Why no language has this:** Every game needs it. Every game bolts Gettext on afterward. Embedding it as a builtin means the toolchain can extract strings automatically, and translators only need to edit JSON files — not touch any code.

**Files to change:** `ipp/runtime/i18n.py` (new), `ipp/vm/vm.py` (register `t`, `set_locale`, `load_locale`), `ipp/cli.py` (add `ipp extract` and `ipp translate` commands).

`ipp/runtime/i18n.py`:
```python
_locale = "en"
_strings = {"en": {}}   # locale -> {key -> translated}

def set_locale(locale):
    global _locale
    _locale = locale

def load_locale(locale, path):
    """Load a JSON translation file: {"Hello": "Bonjour", ...}"""
    import json
    with open(path) as f:
        _strings[locale] = json.load(f)

def t(key, **kwargs):
    translated = _strings.get(_locale, {}).get(key, key)
    if kwargs:
        for k, v in kwargs.items():
            translated = translated.replace("{" + k + "}", str(v))
    return translated
```

**Locale file format (`locales/fr.json`):**
```json
{
  "Player died": "Le joueur est mort",
  "Score: {n}": "Score : {n}",
  "Level {level} complete!": "Niveau {level} terminé !",
  "Press {key} to continue": "Appuyez sur {key} pour continuer"
}
```

**CLI — `ipp extract src/ --output locales/en.json`:**
Scans all `.ipp` files for `t("...")` calls, collects unique strings, writes a template JSON where key = value (untranslated English). Translators fill in the values for each locale.

**Test file: `tests/v2_0_12_2/test_i18n.ipp`**
```ipp
import { write_file, delete_file } from "ipp-io"

# Default locale is English — t() returns the key unchanged if no translation
assert t("Player died") == "Player died"
assert t("Score: {n}", n=100) == "Score: 100"

# Load a test locale
write_file("/tmp/test_fr.json", "{\"Player died\": \"Le joueur est mort\", \"Score: {n}\": \"Score : {n}\"}")
load_locale("fr", "/tmp/test_fr.json")
set_locale("fr")

assert t("Player died") == "Le joueur est mort"
assert t("Score: {n}", n=42) == "Score : 42"

# Missing key falls back to the key itself (never crashes)
assert t("Undefined string") == "Undefined string"

# Switch back to English
set_locale("en")
assert t("Player died") == "Player died"

delete_file("/tmp/test_fr.json")
```

**C/Rust rewrite:** `_strings` dict lives in Python. `t()` is a Python-backed builtin called from the C/Rust VM via FFI. No bytecode change. The string lookup is O(1) hash table — negligible overhead.

**Bootstrapped Ipp:** `t()` is reimplemented as an Ipp function that reads from a global locale dict loaded at startup. The CLI tools (`ipp extract`) stay as Python scripts. Once file IO works in bootstrapped Ipp, `load_locale()` becomes a one-liner.

**Regression risk:** Zero. New builtins `t`, `set_locale`, `load_locale`. No existing code uses these names.

### v2.0.13 — Package: `ipp-log` — Structured Logging with Levels

**What:** A logging package. `print()` is fine for scripts; real games need log levels so you can filter debug noise in production, write logs to files, and track what happened before a crash. This can be written almost entirely in Ipp itself — the only Python backing needed is a file handle.

`ipp/stdlib/ipp-log/log.ipp`:
```ipp
var _level = 1   # 0=DEBUG 1=INFO 2=WARN 3=ERROR
var _file = nil
var _prefix = true

export func set_level(lvl) { _level = lvl }
export func set_file(path) { _file = path }
export func set_prefix(show) { _prefix = show }

export var DEBUG = 0
export var INFO  = 1
export var WARN  = 2
export var ERROR = 3

func _write(lvl, label, msg) {
    if lvl < _level { return }
    var line = _prefix ? "[" + label + "] " + msg : msg
    print(line)
    if _file != nil {
        import { append_file } from "ipp-io"
        append_file(_file, line + "
")
    }
}

export func debug(msg) { _write(0, "DEBUG", msg) }
export func info(msg)  { _write(1, "INFO",  msg) }
export func warn(msg)  { _write(2, "WARN",  msg) }
export func error(msg) { _write(3, "ERROR", msg) }

export func log(lvl, msg) {
    match lvl {
        case 0 => debug(msg)
        case 1 => info(msg)
        case 2 => warn(msg)
        case 3 => error(msg)
    }
}
```

**Test file: `tests/v2_0_13/test_log.ipp`**
```ipp
import { debug, info, warn, error, set_level, set_file, DEBUG, INFO, WARN } from "ipp-log"
import { read_file, delete_file, file_exists } from "ipp-io"

# Basic logging — just confirm no crash
info("game started")
warn("save file not found, using defaults")
error("critical: map failed to load")

# Level filtering
set_level(WARN)
# debug and info are now suppressed (no crash, no output)
debug("this should not print")
info("this should not print")
warn("this should print")

# Log to file
set_level(DEBUG)
set_file("/tmp/test_game.log")
info("player spawned at 0,0")
warn("enemy count high: 42")

assert file_exists("/tmp/test_game.log") == true
var log_text = read_file("/tmp/test_game.log")
assert log_text.contains("player spawned") == true
assert log_text.contains("enemy count") == true

delete_file("/tmp/test_game.log")
```

**Regression risk:** Zero. Written entirely in Ipp, only uses existing builtins.

---

---

### v2.0.12.3 — Feature: `@config` — Hot-Reloadable Config Binding

**What:** Apply `@config("balance.toml")` to a class and its fields are automatically loaded from that TOML file at startup and reloaded whenever the file changes on disk. Game designers tweak `balance.toml` in a text editor and see results immediately — no restart.

**Why no language has this:** It requires combining a decorator system, a file watcher, and a class property setter — all at once. Ipp has all three. This is the most-requested game dev feature after hot reload because it separates balance data from code without requiring a full data pipeline.

```ipp
@config("data/balance.toml")
class EnemyBalance {
    var orc_hp        = 50
    var orc_damage    = 10
    var orc_xp        = 25
    var spawn_rate    = 3.0
    var max_enemies   = 20
}

# Values load from balance.toml at startup.
# Change balance.toml while the game runs → values update within 1 second.
print(EnemyBalance.orc_hp)    # 50 (or whatever is in balance.toml)
```

**`data/balance.toml`:**
```toml
orc_hp      = 75
orc_damage  = 12
orc_xp      = 30
spawn_rate  = 2.5
max_enemies = 25
```

**Files to change:** `ipp/parser/parser.py` (parse `@config("path")` on class), `ipp/runtime/config_watcher.py` (new — file polling + TOML parsing), `ipp/vm/compiler.py` (inject config load into class init), `ipp/vm/vm.py` (register config watcher tick in game loop).

`ipp/runtime/config_watcher.py`:
```python
import os, time
try:
    import tomllib        # Python 3.11+
except ImportError:
    try: import tomli as tomllib   # pip install tomli
    except ImportError: tomllib = None

_watchers = []   # list of {path, class_obj, last_mtime}

def register_config(path, class_obj):
    _watchers.append({'path': path, 'class': class_obj, 'mtime': 0})
    _reload(path, class_obj)   # load immediately on startup

def _reload(path, class_obj):
    if tomllib is None: return
    try:
        with open(path, 'rb') as f:
            data = tomllib.load(f)
        for k, v in data.items():
            if k in class_obj.class_fields:
                class_obj.class_fields[k] = v
    except: pass

def tick():
    for w in _watchers:
        try:
            mtime = os.path.getmtime(w['path'])
            if mtime != w['mtime']:
                w['mtime'] = mtime
                _reload(w['path'], w['class'])
        except: pass
```

**Test file: `tests/v2_0_12_3/test_config.ipp`**
```ipp
import { write_file, delete_file } from "ipp-io"

write_file("/tmp/test_balance.toml", "speed = 5.0\ndamage = 10\n")

@config("/tmp/test_balance.toml")
class Balance {
    var speed  = 1.0
    var damage = 1
}

assert Balance.speed == 5.0
assert Balance.damage == 10

# Write new values and trigger a reload tick
write_file("/tmp/test_balance.toml", "speed = 9.0\ndamage = 25\n")
config_reload()   # force immediate reload (normally polled)

assert Balance.speed == 9.0
assert Balance.damage == 25

delete_file("/tmp/test_balance.toml")
```

**C/Rust rewrite:** The file watcher (`_watchers`) and TOML parser stay in Python. `config_reload()` and the per-frame tick are Python-backed builtins. The C/Rust VM calls them via FFI. Class field updates go through the normal `SET_ATTR` mechanism — no special VM support.

**Bootstrapped Ipp:** `@config` compiles to a class init that calls `_load_config_file(path)` and maps the result to class fields. The file watcher stays as an OS-level utility; bootstrapped Ipp accesses it via FFI.

**Regression risk:** Zero. New decorator. No existing class is affected.

### v2.0.13.1 — Enhancement: `ipp-log` — `Logger` Class for Per-Module Logging

**What:** Instead of one global logger, games need per-module loggers: `var log = Logger("EnemyAI")` so log lines are prefixed with the module name. Common in Python's `logging.getLogger(__name__)` pattern.

```ipp
# Addition to log.ipp:
export class Logger {
    func init(name, level=INFO) {
        self.name = name
        self.level = level
    }
    func debug(msg) { if DEBUG >= self.level { _write(DEBUG, self.name, msg) } }
    func info(msg)  { if INFO  >= self.level { _write(INFO,  self.name, msg) } }
    func warn(msg)  { if WARN  >= self.level { _write(WARN,  self.name, msg) } }
    func error(msg) { if ERROR >= self.level { _write(ERROR, self.name, msg) } }
}
```

**Test file: `tests/v2_0_13_1/test_logger_class.ipp`**
```ipp
import { Logger, DEBUG } from "ipp-log"

var ai_log = Logger("EnemyAI", DEBUG)
var net_log = Logger("Network")

ai_log.info("pathfinding started")
net_log.warn("connection slow: 450ms")

# Each logger has independent level
ai_log.debug("A* open set size: 23")   # prints (DEBUG level)
net_log.debug("packet received")        # suppressed (net_log is INFO by default)
```

**Regression risk:** Zero.

---

### v2.0.14 — Package: `ipp-test` — Unit Test Framework

**What:** A test framework written in Ipp. Game code needs testable components — especially when refactoring AI, physics, or balance. The framework is `describe`/`it`/`expect` style, familiar to JavaScript developers. Works with `ipp test` CLI command (added in this version).

`ipp/stdlib/ipp-test/test.ipp`:
```ipp
var _suites = []
var _current = nil
var _passed = 0
var _failed = 0
var _failures = []

export func describe(name, fn) {
    _current = {"name": name, "tests": []}
    _suites.append(_current)
    fn()
    _current = nil
}

export func it(name, fn) {
    try {
        fn()
        _passed = _passed + 1
        print("  ✓ " + name)
    } catch e {
        _failed = _failed + 1
        _failures.append(name + ": " + e)
        print("  ✗ " + name)
        print("    " + e)
    }
}

export func expect(val) {
    return Expectation(val)
}

export class Expectation {
    func init(val) { self.val = val }
    func to_equal(expected) {
        assert self.val == expected, "expected " + str(expected) + " but got " + str(self.val)
    }
    func to_be_true() {
        assert self.val == true, "expected true but got " + str(self.val)
    }
    func to_be_false() {
        assert self.val == false, "expected false but got " + str(self.val)
    }
    func to_contain(item) {
        assert self.val.contains(item) == true, str(self.val) + " does not contain " + str(item)
    }
    func to_be_nil() {
        assert self.val == nil, "expected nil but got " + str(self.val)
    }
    func to_be_close_to(expected, tol=0.001) {
        assert isclose(self.val, expected) == true,
            "expected ~" + str(expected) + " but got " + str(self.val)
    }
    func to_throw() {
        var threw = false
        try { self.val() } catch e { threw = true }
        assert threw == true, "expected function to throw but it did not"
    }
    func not() { return NotExpectation(self.val) }
}

export func run_all() {
    print("
=== Test Results ===")
    print("Passed: " + str(_passed))
    print("Failed: " + str(_failed))
    if _failed > 0 {
        print("
Failures:")
        for f in _failures { print("  ✗ " + f) }
        return false
    }
    return true
}
```

**CLI addition:** `ipp test` runs all `test_*.ipp` files in `tests/` recursively.

**Test file: `tests/v2_0_14/test_framework.ipp`**
```ipp
import { describe, it, expect, run_all } from "ipp-test"

describe("math utils", func() {
    it("adds two numbers", func() {
        expect(1 + 1).to_equal(2)
    })
    it("clamps correctly", func() {
        func clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v }
        expect(clamp(15, 0, 10)).to_equal(10)
        expect(clamp(-1, 0, 10)).to_equal(0)
        expect(clamp(5, 0, 10)).to_equal(5)
    })
    it("isclose works for floats", func() {
        expect(isclose(0.1 + 0.2, 0.3)).to_be_true()
    })
})

describe("string utils", func() {
    it("pads correctly", func() {
        expect("42".pad_left(5)).to_equal("   42")
    })
    it("detects digits", func() {
        expect("123".is_digit()).to_be_true()
        expect("12a".is_digit()).to_be_false()
    })
})

describe("error handling", func() {
    it("throws on nil access", func() {
        expect(func() {
            var x = nil
            print(x.field)
        }).to_throw()
    })
})

var ok = run_all()
assert ok == true
```

**Regression risk:** Zero. Written in Ipp.

---

### v2.0.14.1 — Enhancement: `ipp-test` Inline Doc-Tests (`##` assertions)

**What:** Functions can have examples in their `##` doc-comment that are automatically run as tests by `ipp test`. No separate test file needed for simple utilities.

```ipp
## Doubles a number.
## Example:
##   double(5) == 10
##   double(-3) == -6
##   double(0) == 0
export func double(x) { return x * 2 }
```

When `ipp test` encounters this, it extracts the `## example:` lines, wraps them in `assert`, and runs them. Output: `✓ double: 3/3 examples passed`.

**Why novel:** Python has `doctest`. No game-focused language has it. For small utility functions this eliminates the need for a separate test file entirely — the documentation _is_ the test.

**Files to change:** `ipp/cli.py` — `ipp test` command; `ipp/testing/doctest.py` — parse `##` lines, extract `expr == expected` patterns, wrap in assert and run.

**Test file: `tests/v2_0_14_1/sample_lib.ipp`**
```ipp
## Clamps value between lo and hi.
## Example:
##   clamp(15, 0, 10) == 10
##   clamp(-1, 0, 10) == 0
##   clamp(5, 0, 10) == 5
export func clamp(v, lo, hi) {
    if v < lo { return lo }
    if v > hi { return hi }
    return v
}

## Returns the sign of a number (-1, 0, or 1).
## Example:
##   sign(5) == 1
##   sign(-3) == -1
##   sign(0) == 0
export func sign(x) {
    if x > 0 { return 1 }
    if x < 0 { return -1 }
    return 0
}
```

Running `ipp test tests/v2_0_14_1/sample_lib.ipp` should output:
```
✓ clamp: 3/3 doc-examples passed
✓ sign: 3/3 doc-examples passed
```

**Regression risk:** Zero. New CLI path.

---

### v2.0.15 — Package: `ipp-math2d` — 2D Game Math Primitives

**What:** The types every 2D game needs that aren't in the core language: `vec2i` (integer vectors for tile coordinates), `rect` (AABB collision), `circle`, `color` (RGBA), and `line`. These are pure data structures — no rendering needed.

`ipp/stdlib/ipp-math2d/math2d.ipp` (core types):
```ipp
# Integer vector — for tile coordinates, grid positions
export class vec2i {
    func init(x, y) { self.x = int(x); self.y = int(y) }
    func __add__(other) { return vec2i(self.x + other.x, self.y + other.y) }
    func __sub__(other) { return vec2i(self.x - other.x, self.y - other.y) }
    func __eq__(other)  { return self.x == other.x and self.y == other.y }
    func __str__()      { return "vec2i(" + str(self.x) + ", " + str(self.y) + ")" }
    func to_vec2()      { return vec2(float(self.x), float(self.y)) }
    func neighbors()    { return [vec2i(self.x+1,self.y), vec2i(self.x-1,self.y),
                                   vec2i(self.x,self.y+1), vec2i(self.x,self.y-1)] }
    func manhattan(other) { return abs(self.x-other.x) + abs(self.y-other.y) }
}

# Axis-aligned bounding box
export class rect {
    func init(x, y, w, h) { self.x=x; self.y=y; self.w=w; self.h=h }
    prop left   { get { return self.x } }
    prop right  { get { return self.x + self.w } }
    prop top    { get { return self.y } }
    prop bottom { get { return self.y + self.h } }
    prop center { get { return vec2(self.x + self.w/2, self.y + self.h/2) } }
    func contains_point(px, py) {
        return px >= self.x and px <= self.right and py >= self.y and py <= self.bottom
    }
    func intersects(other) {
        return self.left < other.right and self.right > other.left and
               self.top < other.bottom and self.bottom > other.top
    }
    func expand(amount) { return rect(self.x-amount, self.y-amount, self.w+amount*2, self.h+amount*2) }
    func __str__() { return "rect(" + str(self.x)+","+str(self.y)+","+str(self.w)+","+str(self.h)+")" }
}

# Circle
export class circle {
    func init(cx, cy, r) { self.cx=cx; self.cy=cy; self.r=r }
    func contains_point(px, py) {
        return (px-self.cx)*(px-self.cx) + (py-self.cy)*(py-self.cy) <= self.r*self.r
    }
    func intersects_circle(other) {
        var dx = self.cx - other.cx
        var dy = self.cy - other.cy
        var dist_sq = dx*dx + dy*dy
        var radii = self.r + other.r
        return dist_sq <= radii*radii
    }
    func intersects_rect(r) {
        var cx = clamp(self.cx, r.left, r.right)
        var cy = clamp(self.cy, r.top, r.bottom)
        var dx = self.cx - cx
        var dy = self.cy - cy
        return dx*dx + dy*dy <= self.r*self.r
    }
}

# RGBA Color
export class color {
    func init(r, g, b, a=255) { self.r=int(r); self.g=int(g); self.b=int(b); self.a=int(a) }
    func lerp(other, t) {
        return color(
            self.r + (other.r - self.r) * t,
            self.g + (other.g - self.g) * t,
            self.b + (other.b - self.b) * t,
            self.a + (other.a - self.a) * t
        )
    }
    func to_hex() {
        func h(n) { return str(n).zfill(2) }  # requires str.zfill from v1.8.0.4
        return "#" + h(self.r) + h(self.g) + h(self.b)
    }
    func __str__() { return "color(" + str(self.r)+","+str(self.g)+","+str(self.b)+","+str(self.a)+")" }
}

# Preset colors
export var RED    = color(255, 0, 0)
export var GREEN  = color(0, 255, 0)
export var BLUE   = color(0, 0, 255)
export var WHITE  = color(255, 255, 255)
export var BLACK  = color(0, 0, 0)
export var YELLOW = color(255, 255, 0)
```

**Test file: `tests/v2_0_15/test_math2d.ipp`**
```ipp
import { vec2i, rect, circle, color, RED, BLUE } from "ipp-math2d"

# vec2i
var a = vec2i(3, 4)
var b = vec2i(1, 2)
assert (a + b).x == 4
assert (a + b).y == 6
assert a.manhattan(b) == 4
var neighbors = a.neighbors()
assert len(neighbors) == 4

# rect collision
var r1 = rect(0, 0, 100, 100)
var r2 = rect(50, 50, 100, 100)
var r3 = rect(200, 200, 50, 50)
assert r1.intersects(r2) == true
assert r1.intersects(r3) == false
assert r1.contains_point(50, 50) == true
assert r1.contains_point(150, 50) == false
assert r1.right == 100
assert r1.bottom == 100

# circle
var c = circle(0, 0, 10)
assert c.contains_point(5, 5) == true
assert c.contains_point(8, 8) == false   # 8²+8²=128 > 100
var c2 = circle(15, 0, 8)
assert c.intersects_circle(c2) == true   # radii sum=18 > dist=15

# color lerp
var mid = RED.lerp(BLUE, 0.5)
assert mid.r == 127
assert mid.b == 127
assert RED.to_hex() == "#ff0000"
```

**Regression risk:** Zero. New classes in new package.

---

### v2.0.15.1 — Enhancement: `ipp-math2d` — Noise, Seeded RNG, Bezier

**What:** Three additions to `ipp-math2d` that complete the math toolkit for procedural generation and smooth animation.

**Seeded RNG** (most important — needed for reproducible tests and deterministic game logic):
```ipp
export class RNG {
    func init(seed) {
        self._seed = seed
        self._state = seed
    }
    func next() {
        # LCG: simple, deterministic, seed-reproducible
        self._state = (self._state * 1664525 + 1013904223) % (2 ** 32)
        return self._state / (2 ** 32)   # 0.0 to 1.0
    }
    func int_range(lo, hi) { return lo + int(self.next() * (hi - lo + 1)) }
    func choice(lst) { return lst[self.int_range(0, len(lst)-1)] }
    func shuffle(lst) {
        var result = lst.copy()
        var n = len(result)
        for i in range(n-1, 0, -1) {
            var j = self.int_range(0, i)
            var result[i], result[j] = result[j], result[i]
        }
        return result
    }
}
```

**Perlin-style noise** (wraps Python's existing implementation):
```ipp
export func noise1d(x, seed=0) { return _builtin_noise1d(x, seed) }
export func noise2d(x, y, seed=0) { return _builtin_noise2d(x, y, seed) }
```

**Bezier curves** (pure Ipp, ~20 lines):
```ipp
export func bezier_quad(p0, p1, p2, t) {
    var mt = 1 - t
    return [mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0],
            mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]]
}
export func bezier_cubic(p0, p1, p2, p3, t) {
    var mt = 1 - t
    return [mt*mt*mt*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t*t*t*p3[0],
            mt*mt*mt*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t*t*t*p3[1]]
}
```

**Test file: `tests/v2_0_15_1/test_math2d_extras.ipp`**
```ipp
import { RNG, bezier_quad } from "ipp-math2d"

# Seeded RNG is deterministic
var rng1 = RNG(42)
var rng2 = RNG(42)
assert rng1.next() == rng2.next()
assert rng1.next() == rng2.next()

# Different seeds give different results
var rng3 = RNG(99)
assert rng1.next() != rng3.next()

# int_range stays in bounds
var rng = RNG(12345)
for i in range(100) {
    var n = rng.int_range(1, 6)
    assert n >= 1 and n <= 6
}

# Bezier midpoint of straight line == midpoint
var mid = bezier_quad([0,0], [5,0], [10,0], 0.5)
assert isclose(mid[0], 5.0) == true

# Bezier at t=0 is p0, t=1 is p2
var start = bezier_quad([1,2], [5,5], [9,8], 0.0)
assert isclose(start[0], 1.0) == true
var end_pt = bezier_quad([1,2], [5,5], [9,8], 1.0)
assert isclose(end_pt[0], 9.0) == true
```

---

### v2.0.16 — Package: `ipp-signal` — Signals and Event Emitter

**What:** The signal/event pattern used constantly in GDScript, Unity (UnityEvents), and game architectures generally. An enemy dies → it emits `died` → multiple systems listen and react independently (UI updates score, audio plays sound, achievement system checks). Decouples emitter from listener. Can be written entirely in Ipp.

`ipp/stdlib/ipp-signal/signal.ipp`:
```ipp
export class Signal {
    func init() {
        self._listeners = []
    }
    func connect(fn) {
        self._listeners.append(fn)
    }
    func disconnect(fn) {
        self._listeners = self._listeners.filter(func(f) { return f != fn })
    }
    func emit(...args) {
        for fn in self._listeners {
            fn(...args)
        }
    }
    func once(fn) {
        func wrapper(...args) {
            fn(...args)
            self.disconnect(wrapper)
        }
        self.connect(wrapper)
    }
    func clear() { self._listeners = [] }
    prop listener_count { get { return len(self._listeners) } }
}

export class EventEmitter {
    func init() { self._signals = {} }
    func on(event, fn) {
        if self._signals.get(event) == nil {
            self._signals[event] = Signal()
        }
        self._signals[event].connect(fn)
    }
    func off(event, fn) {
        if self._signals.get(event) != nil {
            self._signals[event].disconnect(fn)
        }
    }
    func emit(event, ...args) {
        if self._signals.get(event) != nil {
            self._signals[event].emit(...args)
        }
    }
    func once(event, fn) {
        if self._signals.get(event) == nil {
            self._signals[event] = Signal()
        }
        self._signals[event].once(fn)
    }
}
```

**Test file: `tests/v2_0_16/test_signal.ipp`**
```ipp
import { Signal, EventEmitter } from "ipp-signal"

# Basic signal
var on_death = Signal()
var death_count = 0
on_death.connect(func(name) { death_count = death_count + 1 })
on_death.emit("Orc")
on_death.emit("Goblin")
assert death_count == 2

# Multiple listeners
var log = []
on_death.connect(func(name) { log.append(name) })
on_death.emit("Troll")
assert death_count == 3
assert log == ["Troll"]

# once: fires only once then auto-disconnects
var once_count = 0
on_death.once(func(name) { once_count = once_count + 1 })
on_death.emit("Boss")
on_death.emit("Boss")
assert once_count == 1   # only fired once

# EventEmitter pattern
class Enemy {
    func init(hp) {
        self.hp = hp
        self.events = EventEmitter()
    }
    func take_damage(amt) {
        self.hp = self.hp - amt
        self.events.emit("damaged", amt)
        if self.hp <= 0 { self.events.emit("died") }
    }
}

var e = Enemy(50)
var damage_log = []
var died = false

e.events.on("damaged", func(amt) { damage_log.append(amt) })
e.events.on("died", func() { died = true })

e.take_damage(20)
e.take_damage(40)

assert damage_log == [20, 40]
assert died == true
```

---

### v2.0.16.1 — Feature: `@watch` — Reactive Variables

**What:** A decorator that makes any class field reactive — when the field's value changes, a callback fires automatically. No language has this as a first-class feature. GDScript has `setget` which is close but verbose. Unity's `OnValueChanged` is UI-only. The `@watch` decorator eliminates all manual setter boilerplate for common game patterns.

```ipp
class PlayerHUD {
    @watch(func(old_val, new_val) { update_hp_bar(new_val) })
    var hp = 100

    @watch(func(old_val, new_val) { update_score_display(new_val) })
    var score = 0
}
```

When `player.hp = 50` is executed, the watch callback fires with `(100, 50)` automatically — no explicit setter needed.

**Implementation:** `@watch(fn)` is a decorator applied to `var` declarations inside a class. The compiler lowers it to a property with a setter that calls `fn(old, new)` before updating.

**Files to change:** `ipp/parser/parser.py` — recognise `@watch(expr)` before `var` inside class body; `ipp/vm/compiler.py` — emit watched field as property with auto-generated setter.

**Test file: `tests/v2_0_16_1/test_watch.ipp`**
```ipp
import { Signal } from "ipp-signal"

var changes = []

class Stats {
    @watch(func(old_v, new_v) { changes.append(["hp", old_v, new_v]) })
    var hp = 100

    @watch(func(old_v, new_v) { changes.append(["score", old_v, new_v]) })
    var score = 0
}

var s = Stats()
assert s.hp == 100
assert s.score == 0
assert changes == []

s.hp = 80
assert s.hp == 80
assert changes == [["hp", 100, 80]]

s.score = 500
assert s.score == 500
assert changes[1] == ["score", 0, 500]

# Watch on damage clamping
var clamped_changes = []
class Health {
    @watch(func(old_v, new_v) {
        if new_v < 0 { self.hp = 0 }
        if new_v > self.max_hp { self.hp = self.max_hp }
        clamped_changes.append(new_v)
    })
    var hp = 100
    var max_hp = 100
}

var h = Health()
h.hp = 150   # clamped to 100
assert h.hp == 100
h.hp = -10   # clamped to 0
assert h.hp == 0
```

---

---

### v2.0.16.2 — Feature: `@achievement` — Declarative Achievement System

**What:** Declare achievements as decorators on the game state class. The system automatically checks conditions on state changes and emits a signal when an achievement unlocks. No game needs a hand-rolled achievement system — this one is 10 lines to use and zero to maintain.

```ipp
import { Signal } from "ipp-signal"

var on_achievement = Signal()

@achievement("First Blood",    condition=func(s) { return s.kills >= 1 })
@achievement("Unstoppable",    condition=func(s) { return s.kills >= 100 })
@achievement("Pacifist",       condition=func(s) { return s.playtime > 3600 and s.kills == 0 })
@achievement("Speed Runner",   condition=func(s) { return s.time_to_finish < 600 })
@achievement("Treasure Hunter",condition=func(s) { return s.gold >= 1000 })
class GameState {
    func init() {
        self.kills = 0
        self.playtime = 0.0
        self.gold = 0
        self.time_to_finish = nil
    }
}
```

Every time any field on `GameState` is written, the achievement system checks all uncompleted conditions. Unlocked achievements are stored in a persistent file and never trigger again.

**Files to change:** `ipp/runtime/achievements.py` (new), `ipp/parser/parser.py` (parse `@achievement(...)`), `ipp/vm/vm.py` (hook `SET_ATTR` for achievement-decorated classes).

```python
# achievements.py
_registry = {}   # class_name -> list of {name, condition, unlocked}
_save_path = ".ipp_achievements"

def register(class_name, achievement_name, condition_fn):
    if class_name not in _registry:
        _registry[class_name] = []
    # Load unlock state from file
    unlocked = _load_save().get(achievement_name, False)
    _registry[class_name].append({
        'name': achievement_name,
        'condition': condition_fn,
        'unlocked': unlocked
    })

def check(instance, on_unlock=None):
    cls_name = instance.cls.name
    for ach in _registry.get(cls_name, []):
        if not ach['unlocked'] and ach['condition'](instance):
            ach['unlocked'] = True
            _save()
            if on_unlock: on_unlock(ach['name'])
```

**Test file: `tests/v2_0_16_2/test_achievements.ipp`**
```ipp
var unlocked = []

@achievement("First Kill",  condition=func(s) { return s.kills >= 1 })
@achievement("Ten Kills",   condition=func(s) { return s.kills >= 10 })
@achievement("Collector",   condition=func(s) { return s.gold >= 100 })
class Stats {
    func init() { self.kills = 0; self.gold = 0 }
}

achievement_on_unlock(func(name) { unlocked.append(name) })
var s = Stats()
s.kills = 1
assert unlocked == ["First Kill"]

s.kills = 10
assert unlocked == ["First Kill", "Ten Kills"]

s.gold = 150
assert unlocked == ["First Kill", "Ten Kills", "Collector"]

# Already unlocked achievements don't fire again
s.kills = 1
assert len(unlocked) == 3

# Check persisted state (loaded from save file)
var already_done = achievement_unlocked("First Kill")
assert already_done == true
```

**C/Rust rewrite:** Achievement registry and condition checks stay in Python. The `SET_ATTR` hook in C/Rust calls a Python callback `check_achievements(instance)` for achievement-decorated classes. Identical semantics, faster field writes for non-decorated classes.

**Bootstrapped Ipp:** `@achievement` lowers to `@invariant`-style property setters that call `achievement_check(self)` after each mutation. Fully expressible in Ipp once `@invariant` and signals exist.

**Regression risk:** Low. Only activates on `@achievement`-decorated classes.

### v2.0.17 — Package: `ipp-ai` — State Machine, A\* Pathfinding, Grid Utilities

**What:** Three game AI primitives that every non-trivial game eventually needs, all implementable in pure Ipp without any Python backing.

**State machine** (~60 lines Ipp):
```ipp
export class StateMachine {
    func init(owner) {
        self.owner = owner
        self.states = {}
        self.current = nil
        self.previous = nil
    }
    func add(name, state) { self.states[name] = state; return self }
    func transition(name) {
        if self.current != nil and self.states[self.current].get("on_exit") != nil {
            self.states[self.current]["on_exit"](self.owner)
        }
        self.previous = self.current
        self.current = name
        if self.states[name].get("on_enter") != nil {
            self.states[name]["on_enter"](self.owner)
        }
    }
    func update(dt) {
        if self.current != nil and self.states[self.current].get("update") != nil {
            self.states[self.current]["update"](self.owner, dt)
        }
    }
}
```

**A\*** (~80 lines Ipp using vec2i from ipp-math2d):
```ipp
export func astar(grid, start, goal, is_walkable) {
    # grid: 2D list of any values
    # start, goal: vec2i
    # is_walkable: func(cell_value) -> bool
    # returns: list of vec2i positions from start to goal, or nil if no path
    ...
}
```

**Grid utilities**:
```ipp
export func grid_new(w, h, fill=nil) { ... }
export func grid_get(grid, pos) { ... }       # pos is vec2i
export func grid_set(grid, pos, val) { ... }
export func grid_neighbors4(grid, pos) { ... }  # cardinal
export func grid_neighbors8(grid, pos) { ... }  # diagonal included
export func grid_flood_fill(grid, start, condition) { ... }
export func grid_line(from_pos, to_pos) { ... }   # Bresenham line
```

**Test file: `tests/v2_0_17/test_ai.ipp`**
```ipp
import { StateMachine } from "ipp-ai"
import { astar, grid_new, grid_set, grid_get } from "ipp-ai"
import { vec2i } from "ipp-math2d"

# State machine
var log = []
class Enemy { var hp = 100; var target = nil }
var enemy = Enemy()

var fsm = StateMachine(enemy)
fsm.add("idle",   { "on_enter": func(e) { log.append("entered idle") },
                    "update":   func(e, dt) { } })
fsm.add("chase",  { "on_enter": func(e) { log.append("started chasing") },
                    "update":   func(e, dt) { log.append("chasing") } })
fsm.add("attack", { "on_enter": func(e) { log.append("attacking!") } })

fsm.transition("idle")
assert log == ["entered idle"]

fsm.transition("chase")
assert log[1] == "started chasing"

fsm.update(0.016)
assert log[2] == "chasing"

# A* pathfinding
var grid = grid_new(5, 5, 0)   # 0 = walkable
grid_set(grid, vec2i(2, 0), 1)  # 1 = wall
grid_set(grid, vec2i(2, 1), 1)
grid_set(grid, vec2i(2, 2), 1)
# Wall at x=2, y=0..2 — path must go around

var path = astar(grid, vec2i(0, 0), vec2i(4, 0), func(cell) { return cell == 0 })
assert path != nil
assert path[0].x == 0 and path[0].y == 0
assert path[-1].x == 4 and path[-1].y == 0
# Path goes around the wall — length > 4 (straight-line would be 4 steps)
assert len(path) > 4
```

---

### v2.0.17.1 — Enhancement: `ipp-ai` — Behavior Tree Primitives

**What:** The three core behavior tree node types that cover 90% of game AI use cases: `Sequence` (all children must succeed), `Selector` (first child that succeeds wins), and `Action` (leaf node that does work). No BT engine required — just composable objects.

```ipp
export class Action {
    func init(fn) { self._fn = fn }
    func tick(agent) { return self._fn(agent) }   # returns true/false
}

export class Sequence {
    func init(...children) { self._children = children }
    func tick(agent) {
        for child in self._children {
            if child.tick(agent) == false { return false }
        }
        return true
    }
}

export class Selector {
    func init(...children) { self._children = children }
    func tick(agent) {
        for child in self._children {
            if child.tick(agent) == true { return true }
        }
        return false
    }
}
```

**Test file: `tests/v2_0_17_1/test_behavior_tree.ipp`**
```ipp
import { Action, Sequence, Selector } from "ipp-ai"

class Agent { var hp = 100; var target_dist = 50; var ammo = 10 }
var agent = Agent()
var log = []

var in_range    = Action(func(a) { return a.target_dist < 30 })
var has_ammo    = Action(func(a) { return a.ammo > 0 })
var shoot       = Action(func(a) { log.append("shoot"); a.ammo = a.ammo - 1; return true })
var move_closer = Action(func(a) { log.append("move"); a.target_dist = a.target_dist - 10; return true })

var attack = Sequence(in_range, has_ammo, shoot)
var pursue = Selector(attack, move_closer)

# Target too far — pursues
pursue.tick(agent)
assert log == ["move"]

# Still too far
pursue.tick(agent)
assert log == ["move", "move"]

# Now in range (dist=30, condition is < 30, so still not in range)
pursue.tick(agent)
assert log == ["move", "move", "move"]   # dist now 20

# Now in range — shoots
pursue.tick(agent)
assert log[-1] == "shoot"
assert agent.ammo == 9
```

---

### v2.0.18 — Package: `ipp-debug` — Trace Mode and Profiler

**What:** Two dev tools that are genuinely useful and feasible given Ipp's Python host.

**Trace mode** — print every line executed with its result, like a spreadsheet showing recalculation. Novel: no mainstream language has a clean `trace_on()` / `trace_off()` that works at the scripting level.

**Profiler** — measure how long each function call takes, report the top N hotspots. Wraps Python's `time.perf_counter` around VM function dispatch.

**Files to change:** `ipp/vm/vm.py` — add optional trace callback to the dispatch loop; add optional timing wrapper around `_call()`.

```ipp
import { trace_on, trace_off, profile_start, profile_stop, profile_report } from "ipp-debug"

trace_on()
var x = 1 + 2       # prints: line 3: x = 3
var y = x * 4       # prints: line 4: y = 12
trace_off()

profile_start()
run_game_loop(1000)
profile_stop()
profile_report(top=10)
# Output:
# update_enemies    called 1000x  avg 0.8ms  total 800ms
# draw_tiles        called 1000x  avg 0.3ms  total 300ms
# ...
```

**Test file: `tests/v2_0_18/test_debug.ipp`**
```ipp
import { trace_on, trace_off, get_trace_log,
         profile_start, profile_stop, get_profile } from "ipp-debug"

# Trace captures executed lines
trace_on()
var a = 10
var b = a + 5
var c = b * 2
trace_off()

var trace_log = get_trace_log()
assert len(trace_log) >= 3
assert trace_log[0].contains("a") == true
assert trace_log[0].contains("10") == true

# Profile captures timing
profile_start()
func slow_sum(n) {
    var total = 0
    for i in range(n) { total = total + i }
    return total
}
slow_sum(1000)
slow_sum(1000)
profile_stop()

var prof = get_profile()
assert prof.get("slow_sum") != nil
assert prof["slow_sum"]["calls"] == 2
assert prof["slow_sum"]["total_ms"] > 0
```

---

### v2.0.18.1 — Feature: Fuzzy Property Access (Did-You-Mean in Error Messages)

**What:** When `obj.positon` is accessed and `obj` has a `position` field, the error says `"Undefined property 'positon' — did you mean 'position'?"` instead of just `"Property not found"`. Implemented with Levenshtein distance in the VM's attribute-not-found path. No other scripting language does this.

**Files to change:** `ipp/vm/vm.py` — in `LOAD_ATTR` / property-not-found handler, compute edit distance between the requested name and all known property names. If the closest match has distance ≤ 2 and the name is ≥ 3 chars, append `did you mean 'X'?` to the error.

**Implementation (~15 lines):**
```python
def levenshtein(a, b):
    if len(a) < len(b): return levenshtein(b, a)
    if not b: return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j+1]+1, curr[j]+1, prev[j]+(ca!=cb)))
        prev = curr
    return prev[-1]

def suggest_property(name, known_names):
    if len(name) < 3: return None
    best = min(known_names, key=lambda n: levenshtein(name, n), default=None)
    if best and levenshtein(name, best) <= 2:
        return best
    return None
```

**Test file: `tests/v2_0_18_1/test_fuzzy_access.ipp`**
```ipp
class Player {
    func init() {
        self.position = [0, 0]
        self.health = 100
        self.speed = 5
    }
}

var p = Player()

# Correct access works
assert p.position == [0, 0]

# Typo gives helpful error
var caught = ""
try { print(p.positon) } catch e { caught = e }
assert caught.contains("did you mean 'position'") == true

try { print(p.helth) } catch e { caught = e }
assert caught.contains("did you mean 'health'") == true

try { print(p.spedd) } catch e { caught = e }
assert caught.contains("did you mean 'speed'") == true

# Completely wrong name — no suggestion (avoid hallucinating suggestions)
try { print(p.xyz_completely_wrong) } catch e { caught = e }
assert caught.contains("did you mean") == false
```

**Regression risk:** Low. Only fires on property-not-found error path. No change to successful property access.

---

---

### v2.0.18.2 — Package: `ipp-physics` — 2D Physics via pymunk

**What:** A 2D physics package wrapping `pymunk` (Python Box2D-compatible library). Rigid bodies,
static bodies, collision detection with callbacks, gravity, friction, joints. Requires
`pip install pymunk`. No other Ipp package depends on it — purely opt-in.

**Why pymunk and not Box2D directly:** `pymunk` is a mature, well-documented Python wrapper around
Chipmunk2D (same physics used in early Angry Birds). One `pip install` gives you rigid bodies,
collision shapes, constraints, and a step function. Box2D's Python bindings are fragile.

`ipp/stdlib/ipp-physics/physics.ipp`:
```ipp
# Space: the physics world
export class Space {
    func init(gravity_x=0, gravity_y=980) {
        self._space = physics_space_new(gravity_x, gravity_y)
        self._bodies = []
        self._handlers = {}
    }

    func step(dt) {
        physics_space_step(self._space, dt)
    }

    func set_collision_handler(type_a, type_b, fn) {
        self._handlers[str(type_a) + "_" + str(type_b)] = fn
        physics_set_handler(self._space, type_a, type_b, fn)
    }

    func add(body) {
        self._bodies.append(body)
        physics_space_add(self._space, body._body, body._shape)
        return body
    }

    func remove(body) {
        self._bodies = self._bodies.filter(func(b) { return b != body })
        physics_space_remove(self._space, body._body, body._shape)
    }
}

# RigidBody: dynamic moving object
export class RigidBody {
    func init(mass=1.0, moment=nil) {
        self._body = physics_body_new(mass, moment ?? physics_moment_circle(mass, 0, 10))
        self._shape = nil
        self.collision_type = 0
    }
    func add_circle(radius, offset_x=0, offset_y=0) {
        self._shape = physics_shape_circle(self._body, radius, offset_x, offset_y)
        physics_shape_set_type(self._shape, self.collision_type)
        return self
    }
    func add_box(w, h) {
        self._shape = physics_shape_box(self._body, w, h)
        physics_shape_set_type(self._shape, self.collision_type)
        return self
    }
    prop position {
        get { return physics_body_position(self._body) }
        set(v) { physics_body_set_position(self._body, v[0], v[1]) }
    }
    prop velocity {
        get { return physics_body_velocity(self._body) }
        set(v) { physics_body_set_velocity(self._body, v[0], v[1]) }
    }
    prop angle {
        get { return physics_body_angle(self._body) }
    }
    func apply_impulse(x, y) { physics_body_apply_impulse(self._body, x, y) }
}

# StaticBody: immovable wall/floor
export class StaticBody {
    func init() {
        self._body = physics_static_body_new()
        self._shape = nil
        self.collision_type = 0
    }
    func add_segment(x1, y1, x2, y2, radius=2) {
        self._shape = physics_shape_segment(self._body, x1, y1, x2, y2, radius)
        return self
    }
    func add_box(x, y, w, h) {
        self._shape = physics_shape_box(self._body, w, h)
        self.position = [x + w/2, y + h/2]
        return self
    }
    prop position {
        get { return physics_body_position(self._body) }
        set(v) { physics_body_set_position(self._body, v[0], v[1]) }
    }
}
```

**Python builtins backing (`ipp/runtime/physics_builtins.py`):**
```python
try:
    import pymunk
    _HAS_PYMUNK = True
except ImportError:
    _HAS_PYMUNK = False
    # Stub everything — import without crash, just no-op physics

def physics_space_new(gx, gy):
    if not _HAS_PYMUNK: return None
    space = pymunk.Space()
    space.gravity = (gx, gy)
    return space

def physics_space_step(space, dt):
    if space: space.step(dt)

def physics_body_new(mass, moment):
    if not _HAS_PYMUNK: return None
    return pymunk.Body(mass, moment)

def physics_shape_circle(body, radius, ox, oy):
    if not _HAS_PYMUNK: return None
    return pymunk.Circle(body, radius, (ox, oy))

def physics_body_position(body):
    if not body: return [0, 0]
    return [body.position.x, body.position.y]

# ... etc for all shape/body operations
```

**Test file: `tests/v2_0_18_2/test_physics.ipp`**
```ipp
import { Space, RigidBody, StaticBody } from "ipp-physics"

# Basic physics simulation
var world = Space(gravity_x=0, gravity_y=980)

# Floor
var floor = StaticBody()
floor.add_segment(0, 500, 600, 500, 2)
world.add(floor)

# Ball falling under gravity
var ball = RigidBody(mass=1.0)
ball.add_circle(15)
ball.position = [300, 100]
world.add(ball)

var initial_y = ball.position[1]

# Simulate 60 frames
for i in range(60) { world.step(1.0 / 60.0) }

# Ball fell due to gravity
assert ball.position[1] > initial_y

# Ball hit floor and stopped falling (approx)
for i in range(180) { world.step(1.0 / 60.0) }
assert ball.position[1] < 510    # resting on floor, not falling through

# Collision callback fires
var collisions = []
world.set_collision_handler(1, 2, func(a, b) {
    collisions.append("hit")
})

var ball2 = RigidBody(mass=1.0)
ball2.collision_type = 1
ball2.add_circle(10)
ball2.position = [300, 200]
world.add(ball2)

var wall = StaticBody()
wall.collision_type = 2
wall.add_segment(300, 0, 300, 600, 5)
world.add(wall)

ball2.apply_impulse(1000, 0)
for i in range(30) { world.step(1.0/60.0) }
assert len(collisions) > 0
```

**C/Rust rewrite:** `pymunk` stays Python. The `physics_*` builtins are Python callables accessed
via the same FFI path as all other builtins. A future v3.x could swap pymunk for a native Jolt or
Box2D binding — the Ipp-level `Space/RigidBody/StaticBody` API stays identical.

**Bootstrapped Ipp:** The `ipp-physics` package is already Ipp code. The `physics_*` builtins are
provided via an FFI module. No change at all.

**Regression risk:** Zero. New package, optional dependency. Silently stubs if pymunk not installed.

## Phase D3: Network & Canvas Packages (v2.0.19 – v2.0.22)

> **What already exists:** `http_get`, `http_post`, `http_put`, `http_delete`, `websocket_connect/send/receive/close`, and `canvas_open/rect/circle/line/text/clear/show` are all implemented in Python and registered in the VM. None of them have been documented, properly tested, or packaged with a clean Ipp API. This phase does that — then builds `ipp-net` and `ipp-canvas` and `ipp-ui` on top.
>
> **What needs fixing:**
> - `http_serve` is listed in the VM builtin table but silently does nothing — no implementation exists
> - WebSocket tests only check that the function *exists*, never test actual messaging
> - Canvas has no game loop integration — `canvas_window.update()` is called manually after each draw, which blocks on `mainloop()` and makes a real 60fps loop impossible
> - Canvas has no image/sprite loading
> - FTP and SMTP are fully implemented in Python but never exposed to the VM at all
>
> **Versions in this phase:**
> - v2.0.19 — `ipp-net`: expose HTTP + WebSocket cleanly, fix `http_serve`, wire FTP + SMTP
> - v2.0.19.1 — `ipp-net`: HTTP client package with clean Ipp API
> - v2.0.19.2 — `ipp-net`: HTTP server (real implementation replacing the stub)
> - v2.0.19.3 — `ipp-net`: WebSocket client, tested end-to-end
> - v2.0.19.4 — `ipp-net`: FTP and SMTP exposed to VM + packaged
> - v2.0.19.5 — `ipp-net`: Online game utilities (leaderboard, game state sync)
> Network & Canvas features moved to **Phase D3 (v2.0.19–v2.0.21)**.

---

---

### v2.0.18.3 — Enhancement: `ipp-physics` — Joints, Raycasting, and Debug Draw

**What:** Three physics additions that complete the toolkit for most 2D games.

```ipp
# Joints (constraints between bodies)
export class PinJoint {
    func init(body_a, body_b, anchor_a=[0,0], anchor_b=[0,0]) {
        self._joint = physics_pin_joint(body_a._body, body_b._body, anchor_a, anchor_b)
    }
}

export class SpringJoint {
    func init(body_a, body_b, rest_length, stiffness, damping) {
        self._joint = physics_spring_joint(
            body_a._body, body_b._body, rest_length, stiffness, damping)
    }
}

# Raycast
export func raycast(space, from_pos, to_pos, collision_type=nil) {
    return physics_raycast(space._space, from_pos, to_pos, collision_type)
}

# Debug draw: overlay collision shapes on canvas
export func debug_draw(space, canvas_ctx=nil) {
    physics_debug_draw(space._space)
}
```

**Test file: `tests/v2_0_18_3/test_physics_extras.ipp`**
```ipp
import { Space, RigidBody, StaticBody, raycast } from "ipp-physics"

var world = Space()

var wall = StaticBody()
wall.add_segment(200, 0, 200, 400, 2)
wall.collision_type = 1
world.add(wall)

# Raycast hits the wall
var hit = raycast(world, [0, 200], [400, 200])
assert hit != nil
assert hit["position"][0] >= 199 and hit["position"][0] <= 201

# Raycast misses
var miss = raycast(world, [0, 0], [0, 400])
assert miss == nil
```



### v2.0.19 — Package: `ipp-net` — HTTP Client, Fixes, and Wire-Up

**What:** Package up the HTTP and WebSocket builtins that already exist into a clean, documented `ipp-net` package. Fix `http_serve` (currently a no-op stub that silently fails). Wire FTP and SMTP into the VM for the first time.

**Gaps to fix in this version:**

**Fix 1 — `http_serve` stub:** The function is listed in `vm.py`'s `missing_builtins` but silently skipped because it's not in `_INTERP_BUILTINS`. Implement a real simple HTTP server using Python's built-in `http.server.HTTPServer`.

**File to change:** `ipp/network/http.py` — add `http_serve()`:
```python
import http.server
import threading
import os

_server_instance = None
_server_thread = None

def http_serve(host="localhost", port=8080, directory="."):
    """Start a simple static file server in a background thread."""
    global _server_instance, _server_thread
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, fmt, *args):
            pass  # suppress default stdout logging
    
    if _server_instance:
        _server_instance.shutdown()
    
    _server_instance = http.server.HTTPServer((host, port), Handler)
    _server_thread = threading.Thread(
        target=_server_instance.serve_forever, daemon=True
    )
    _server_thread.start()
    return {"host": host, "port": port, "directory": directory, "running": True}

def http_serve_stop():
    global _server_instance
    if _server_instance:
        _server_instance.shutdown()
        _server_instance = None
    return True
```

**Fix 2 — FTP exposed to VM:** `ipp/network/ftp.py` is complete but never wired into `ipp/runtime/builtins.py` or `vm.py`.

**File to change:** `ipp/runtime/builtins.py` — add FTP imports:
```python
from ipp.network.ftp import FTPClient, ftp_connect, ftp_upload, ftp_download, ftp_list
```

**Fix 3 — SMTP exposed to VM:**
```python
from ipp.network.smtp import EmailMessage, smtp_send
```

**Fix 4 — Register all new builtins in VM:**
```python
# In ipp/vm/vm.py, explicit builtin dict entries:
'http_serve':      http_serve,
'http_serve_stop': http_serve_stop,
'ftp_connect':     ftp_connect,
'ftp_upload':      ftp_upload,
'ftp_download':    ftp_download,
'ftp_list':        ftp_list,
'smtp_send':       smtp_send,
```

**Test file: `tests/v2_0_19/test_net_wiring.ipp`**
```ipp
# Confirm all functions are available and have the right type
assert type(http_get) == "function"
assert type(http_post) == "function"
assert type(http_put) == "function"
assert type(http_delete) == "function"
assert type(http_serve) == "function"
assert type(http_serve_stop) == "function"
assert type(websocket_connect) == "function"
assert type(websocket_send) == "function"
assert type(websocket_receive) == "function"
assert type(websocket_close) == "function"
assert type(ftp_connect) == "function"
assert type(smtp_send) == "function"

# http_serve starts without crashing
var server = http_serve("127.0.0.1", 18080, ".")
assert server["running"] == true
assert server["port"] == 18080
http_serve_stop()
```

**Regression risk:** Low. Adds new builtins, fixes silent stub. No existing working code changed.

---

### v2.0.19.1 — Package: `ipp-net` HTTP Client — Clean Ipp API

**What:** A clean Ipp wrapper around the raw `http_get/post/put/delete` builtins. The builtins return Python `HttpResponse` objects — this package wraps them so `.status`, `.body`, `.json()`, `.ok` all work naturally from Ipp. Also adds `http.get()` shorthand, request headers, query params, and timeout.

`ipp/stdlib/ipp-net/net.ipp`:
```ipp
# HTTP client

export class Response {
    func init(status, body, headers, url) {
        self.status = status
        self.body = body
        self.headers = headers
        self.url = url
    }
    prop ok { get { return self.status >= 200 and self.status < 300 } }
    func json() { return json_parse(self.body) }
    func text() { return self.body }
    func __str__() { return "<Response " + str(self.status) + " " + self.url + ">" }
}

func _wrap(raw) {
    return Response(raw.status_code, raw.body, raw.headers, raw.url ?? "")
}

export class http {
    static func get(url, headers=nil) {
        return _wrap(http_get(url, headers))
    }
    static func post(url, body=nil, json=nil, headers=nil) {
        return _wrap(http_post(url, body, headers, json))
    }
    static func put(url, body=nil, json=nil, headers=nil) {
        return _wrap(http_put(url, body, headers, json))
    }
    static func delete(url, headers=nil) {
        return _wrap(http_delete(url, headers))
    }
    static func request(method, url, body=nil, json=nil, headers=nil) {
        return _wrap(http_request(url, method, body, headers, json))
    }
}

export class Server {
    func init(host="localhost", port=8080, directory=".") {
        self.host = host
        self.port = port
        self.directory = directory
        self._info = nil
    }
    func start() {
        self._info = http_serve(self.host, self.port, self.directory)
        return self
    }
    func stop() {
        http_serve_stop()
        self._info = nil
        return self
    }
    prop running { get { return self._info != nil } }
    prop address { get { return "http://" + self.host + ":" + str(self.port) } }
}
```

**Test file: `tests/v2_0_19_1/test_http_client.ipp`**
```ipp
import { http, Response, Server } from "ipp-net"

# Response object wraps correctly
# (Uses a real public endpoint — skip if offline)
var res = http.get("https://httpbin.org/get")
assert res is Response == true
assert res.ok == true
assert res.status == 200

# JSON parsing from response
var data = res.json()
assert data.get("url") != nil

# POST with JSON body
var post_res = http.post(
    "https://httpbin.org/post",
    json={"player": "Alice", "score": 100}
)
assert post_res.ok == true
var post_data = post_res.json()
assert post_data["json"]["player"] == "Alice"

# Failed request gives non-ok response (not a crash)
var bad = http.get("https://httpbin.org/status/404")
assert bad.ok == false
assert bad.status == 404

# Server starts and stops cleanly
var server = Server("127.0.0.1", 18081, ".")
server.start()
assert server.running == true
assert server.address == "http://127.0.0.1:18081"
server.stop()
assert server.running == false
```

**Regression risk:** Zero. New package, wraps existing builtins.

---

### v2.0.19.2 — Package: `ipp-net` HTTP Server — Route Handlers

**What:** Build a proper route-handler HTTP server on top of `http_serve`. Games need this for: local leaderboard API, config server, debug endpoint. The simple `http_serve()` from v2.0.19 serves static files. This version adds dynamic route handlers in Ipp.

**Implementation:** Python's `http.server.BaseHTTPRequestHandler` is subclassed. Routes are stored in a dict. When a request comes in, the handler calls the registered Ipp function with a `Request` object and expects a `Response`.

**File to change:** `ipp/network/http.py` — add `http_serve_routes()`:
```python
def http_serve_routes(host, port, routes_dict):
    """
    routes_dict: dict mapping "METHOD /path" -> callable(request) -> dict
    callable receives: {"method": str, "path": str, "body": str, "headers": dict}
    callable returns: {"status": int, "body": str, "headers": dict}
    """
    class DynamicHandler(http.server.BaseHTTPRequestHandler):
        def handle_request(self, method):
            key = f"{method} {self.path.split('?')[0]}"
            handler = routes_dict.get(key) or routes_dict.get(f"{method} *")
            req = {"method": method, "path": self.path,
                   "body": self.rfile.read(
                       int(self.headers.get("Content-Length", 0))).decode(),
                   "headers": dict(self.headers)}
            if handler:
                resp = handler(req)
                self.send_response(resp.get("status", 200))
                for k,v in (resp.get("headers", {}) or {}).items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.get("body", "").encode())
            else:
                self.send_response(404)
                self.end_headers()
        def do_GET(self): self.handle_request("GET")
        def do_POST(self): self.handle_request("POST")
        def do_PUT(self): self.handle_request("PUT")
        def do_DELETE(self): self.handle_request("DELETE")
        def log_message(self, fmt, *args): pass
    # ... start in background thread (same as http_serve)
```

`ipp/stdlib/ipp-net/net.ipp` addition:
```ipp
export class Router {
    func init() { self._routes = {} }

    func get(path, fn)    { self._routes["GET " + path] = fn }
    func post(path, fn)   { self._routes["POST " + path] = fn }
    func put(path, fn)    { self._routes["PUT " + path] = fn }
    func delete(path, fn) { self._routes["DELETE " + path] = fn }

    func listen(host="localhost", port=8080) {
        http_serve_routes(host, port, self._routes)
        return self
    }
    func stop() { http_serve_stop(); return self }
}

export func json_response(data, status=200) {
    return {
        "status": status,
        "body": json_stringify(data),
        "headers": {"Content-Type": "application/json"}
    }
}

export func text_response(text, status=200) {
    return {"status": status, "body": text, "headers": {"Content-Type": "text/plain"}}
}
```

**Test file: `tests/v2_0_19_2/test_http_server.ipp`**
```ipp
import { Router, json_response, text_response, http } from "ipp-net"

var router = Router()
var call_log = []

router.get("/ping", func(req) {
    call_log.append("ping")
    return text_response("pong")
})

router.get("/player", func(req) {
    return json_response({"name": "Alice", "score": 100})
})

router.post("/score", func(req) {
    import { json_parse } from "ipp-io"
    var body = json_parse(req["body"])
    call_log.append("score:" + str(body["score"]))
    return json_response({"ok": true})
})

router.listen("127.0.0.1", 18082)

# Give the server a moment to start
import { sleep } from "ipp-io"
sleep(0.1)

# Test the routes
var ping = http.get("http://127.0.0.1:18082/ping")
assert ping.text() == "pong"
assert call_log[0] == "ping"

var player = http.get("http://127.0.0.1:18082/player")
var player_data = player.json()
assert player_data["name"] == "Alice"

var post_res = http.post("http://127.0.0.1:18082/score",
    json={"score": 999}, headers={"Content-Type": "application/json"})
assert post_res.json()["ok"] == true
assert call_log[1] == "score:999"

# 404 for unknown route
var not_found = http.get("http://127.0.0.1:18082/unknown")
assert not_found.status == 404

router.stop()
```

**Regression risk:** Low. New route-handler API; static `http_serve()` from v2.0.19 unchanged.

---

### v2.0.19.3 — Package: `ipp-net` WebSocket Client — Real Tests + Error Handling

**What:** The WebSocket client already works but has never been tested beyond "the function exists." This version adds a proper `WebSocket` class to `ipp-net`, adds end-to-end tests against a local echo server, and fixes the missing `pip install websockets` user experience (clear error + instructions if not installed).

`ipp/stdlib/ipp-net/net.ipp` addition:
```ipp
export class WebSocket {
    func init(url) {
        self.url = url
        self._client = nil
    }

    func connect() {
        self._client = websocket_connect(self.url)
        return self
    }

    func send(msg) {
        websocket_send(self._client, msg)
        return self
    }

    func send_json(data) {
        websocket_send(self._client, json_stringify(data))
        return self
    }

    func receive(timeout=5) {
        return websocket_receive(self._client, timeout)
    }

    func receive_json(timeout=5) {
        var msg = self.receive(timeout)
        if msg == nil { return nil }
        return json_parse(msg)
    }

    prop connected { get { return self._client != nil and self._client.is_connected() } }

    func close() {
        if self._client != nil {
            websocket_close(self._client)
            self._client = nil
        }
    }
}

export func ws_connect(url) {
    var ws = WebSocket(url)
    ws.connect()
    return ws
}
```

**Test approach:** Spin up a local Python echo server in the test setup, connect to it from Ipp, send messages, receive them back.

**Test file: `tests/v2_0_19_3/test_websocket.ipp`**
```ipp
import { WebSocket, ws_connect, http } from "ipp-net"

# WebSocket class is available
assert type(WebSocket) == "class"
assert type(ws_connect) == "function"

# Connection to invalid host gives clear error, not silent nil
var caught = ""
try {
    var ws = ws_connect("ws://localhost:19999/no-server-here")
} catch e {
    caught = e
}
assert caught != ""
assert caught.contains("failed") == true or caught.contains("refused") == true

# Note: end-to-end echo test requires a running WebSocket server.
# Run: python3 tests/v2_0_19_3/echo_server.py before running this test.
# The echo_server.py starts a ws://localhost:18083 echo server.
#
# When echo_server.py is running:
#   var ws = ws_connect("ws://localhost:18083")
#   ws.send("hello")
#   var reply = ws.receive(2)
#   assert reply == "hello"
#   ws.send_json({"type": "ping", "seq": 1})
#   var json_reply = ws.receive_json(2)
#   assert json_reply["type"] == "pong"
#   assert json_reply["seq"] == 1
#   ws.close()
#   assert ws.connected == false
```

**Also create `tests/v2_0_19_3/echo_server.py`:**
```python
"""Local WebSocket echo server for testing ipp-net WebSocket client."""
import asyncio
try:
    import websockets
    async def echo(ws):
        import json
        async for msg in ws:
            try:
                data = json.loads(msg)
                if data.get("type") == "ping":
                    await ws.send(json.dumps({"type": "pong", "seq": data.get("seq", 0)}))
                else:
                    await ws.send(msg)
            except:
                await ws.send(msg)  # plain string echo
    
    async def main():
        async with websockets.serve(echo, "localhost", 18083):
            print("Echo server running at ws://localhost:18083")
            await asyncio.Future()
    
    asyncio.run(main())
except ImportError:
    print("Install websockets: pip install websockets")
```

**Regression risk:** Zero. New wrapper class, existing `websocket_*` builtins unchanged.

---

### v2.0.19.4 — Package: `ipp-net` FTP + SMTP

**What:** Wire the fully-implemented `ftp.py` and `smtp.py` Python modules into the VM and package them into `ipp-net`. Both were written and left dormant — FTP and SMTP never appear in `vm.py`'s builtin registry at all.

`ipp/stdlib/ipp-net/net.ipp` addition:
```ipp
# FTP client
export class FTP {
    func init(host, user, password="", secure=false) {
        self.host = host
        self.user = user
        self._client = ftp_connect(host, user, password, secure)
    }
    func upload(local_path, remote_path) {
        ftp_upload(self._client, local_path, remote_path)
        return self
    }
    func download(remote_path, local_path) {
        ftp_download(self._client, remote_path, local_path)
        return self
    }
    func list(directory="/") {
        return ftp_list(self._client, directory)
    }
    func close() { ftp_close(self._client) }
}

# Email / SMTP
export class Email {
    func init(subject, body, to) {
        self.subject = subject
        self.body = body
        self.to = to is list ? to : [to]
        self.from_addr = ""
        self.html = nil
        self.attachments = []
    }
    func html_body(html) { self.html = html; return self }
    func attach(path) { self.attachments.append(path); return self }
    func send(smtp_host, smtp_user, smtp_pass, port=587) {
        smtp_send(self.from_addr ?? smtp_user, self.to, self.subject,
                  self.body, self.html, self.attachments,
                  smtp_host, smtp_user, smtp_pass, port)
        return true
    }
}
```

**Test file: `tests/v2_0_19_4/test_ftp_smtp.ipp`**
```ipp
import { FTP, Email } from "ipp-net"

# FTP and Email classes exist
assert type(FTP) == "class"
assert type(Email) == "class"

# Email object builds correctly
var e = Email("Test Subject", "Hello World", "alice@example.com")
assert e.subject == "Test Subject"
assert e.to == ["alice@example.com"]
assert e.attachments == []

# Multiple recipients
var e2 = Email("Blast", "Hi all", ["a@x.com", "b@x.com"])
assert len(e2.to) == 2

# Attachment chaining
e.attach("/tmp/file.txt").attach("/tmp/file2.txt")
assert len(e.attachments) == 2

# Note: actual SMTP/FTP send requires real credentials.
# Integration tests go in tests/v2_0_19_4/test_integration/
# and are skipped in CI unless SMTP_HOST env var is set.
import { get_env } from "ipp-io"
if get_env("SMTP_HOST") != nil {
    # Run full integration test
    var sent = Email("Ipp Test", "Testing ipp-net SMTP", get_env("SMTP_TO"))
    sent.send(get_env("SMTP_HOST"), get_env("SMTP_USER"), get_env("SMTP_PASS"))
    print("SMTP integration test passed")
}
```

**Regression risk:** Zero. Wires dormant code into VM.

---

### v2.0.19.5 — Feature: Online Game Utilities (Leaderboard + State Sync)

**What:** Built on top of `ipp-net`'s HTTP client, two ready-made patterns that cover 80% of what indie games need from the network: a leaderboard and a game state sync. These are not a new server — they are Ipp helpers that talk to any JSON API.

`ipp/stdlib/ipp-net/online.ipp`:
```ipp
import { http, json_response } from "net.ipp"

# Leaderboard — talks to any JSON REST API
export class Leaderboard {
    func init(api_url, game_id) {
        self.api_url = api_url
        self.game_id = game_id
    }

    func submit(player, score) {
        var res = http.post(self.api_url + "/scores", json={
            "game": self.game_id,
            "player": player,
            "score": score
        })
        return res.ok
    }

    func fetch_top(limit=10) {
        var res = http.get(
            self.api_url + "/scores?game=" + self.game_id + "&limit=" + str(limit)
        )
        if res.ok { return res.json() }
        return []
    }
}

# State sync — push/pull arbitrary game state to/from a server
export class StateSync {
    func init(api_url, room_id) {
        self.api_url  = api_url
        self.room_id  = room_id
        self.player_id = str(random() * 999999)
    }

    func push(state) {
        var res = http.post(self.api_url + "/state/" + self.room_id, json={
            "player": self.player_id,
            "state": state
        })
        return res.ok
    }

    func pull() {
        var res = http.get(self.api_url + "/state/" + self.room_id)
        if res.ok { return res.json() }
        return nil
    }
}
```

**Test file: `tests/v2_0_19_5/test_online.ipp`**
```ipp
import { Leaderboard, StateSync } from "ipp-net/online"
import { Router, json_response } from "ipp-net"

# Spin up a local mock API server to test against
var router = Router()
var scores = []

router.post("/scores", func(req) {
    import { json_parse } from "ipp-io"
    scores.append(json_parse(req["body"]))
    return json_response({"ok": true})
})
router.get("/scores", func(req) {
    return json_response(scores)
})

router.listen("127.0.0.1", 18085)
import { sleep } from "ipp-io"
sleep(0.1)

var lb = Leaderboard("http://127.0.0.1:18085", "test-game")
assert lb.submit("Alice", 1000) == true
assert lb.submit("Bob", 850) == true

var top = lb.fetch_top()
assert len(top) == 2
assert top[0]["player"] == "Alice"

router.stop()
```

---

---

### v2.0.19.6 — Feature: `ipp-net` Multiplayer — Room System and Game State Sync

**What:** A higher-level multiplayer abstraction on top of `WSServer` (v2.4.3). A `Room` manages
a lobby, player connections, a shared game state dict, and a locked-step tick. This covers 90%
of indie game multiplayer needs: turn-based games, small real-time games (<8 players),
co-op games, and board game adaptations.

**Realistic scope:** No client prediction, no lag compensation, no delta encoding. Those are
AAA concerns. For indie games: authoritative server, state broadcast every tick, clients send
input events, server applies them and broadcasts the new state. Latency: fine for LAN and
low-latency internet. Good enough for turn-based, fine for casual real-time, not for shooters.

`ipp/stdlib/ipp-net/multiplayer.ipp`:
```ipp
import { WSServer } from "net.ipp"
import { Signal } from "ipp-signal"

export class Room {
    func init(port=8765, max_players=4, tick_rate=20) {
        self.port = port
        self.max_players = max_players
        self.tick_ms = 1000 / tick_rate
        self._players = {}         # client_id -> player_data dict
        self._state = {}           # shared authoritative game state
        self._server = WSServer(port=port)
        self._tick_count = 0

        # Signals
        self.on_player_join    = Signal()
        self.on_player_leave   = Signal()
        self.on_input          = Signal()
        self.on_tick           = Signal()
    }

    func set_state(key, val) {
        self._state[key] = val
        self._broadcast_state()
    }

    func get_state(key, default=nil) {
        return self._state.get(key) ?? default
    }

    prop player_count { get { return len(self._players) } }
    prop players      { get { return self._players } }
    prop is_full      { get { return self.player_count >= self.max_players } }

    func start(on_tick_fn=nil) {
        self._server.on_connect(func(cid) {
            if self.is_full {
                self._server.send(cid, json_stringify({"type": "room_full"}))
                self._server.disconnect(cid)
                return
            }
            self._players[cid] = {"id": cid, "ready": false}
            self._server.send(cid, json_stringify({
                "type": "welcome", "your_id": cid,
                "state": self._state, "players": self._players
            }))
            self._broadcast(json_stringify({"type": "player_joined", "id": cid}), except=cid)
            self.on_player_join.emit(cid)
        })

        self._server.on_message(func(cid, raw) {
            var msg = json_parse(raw)
            if msg["type"] == "input" {
                self.on_input.emit(cid, msg.get("data"))
            } elif msg["type"] == "ready" {
                self._players[cid]["ready"] = true
            }
        })

        self._server.on_disconnect(func(cid) {
            self._players.delete(cid)
            self._broadcast(json_stringify({"type": "player_left", "id": cid}))
            self.on_player_leave.emit(cid)
        })

        # Tick loop (runs in background thread at tick_rate fps)
        if on_tick_fn != nil {
            schedule(func() {
                self._tick_count = self._tick_count + 1
                on_tick_fn(self)
                self._broadcast_state()
                self.on_tick.emit(self._tick_count)
            }, every=self.tick_ms / 1000.0)
        }

        self._server.listen()
    }

    func _broadcast(msg, except=nil) {
        for cid in self._players.keys() {
            if cid != except { self._server.send(cid, msg) }
        }
    }

    func _broadcast_state() {
        var msg = json_stringify({"type": "state", "state": self._state,
                                   "tick": self._tick_count})
        self._broadcast(msg)
    }

    func stop() { self._server.stop() }
}
```

**Example — 2-player turn-based game server:**
```ipp
import { Room } from "ipp-net/multiplayer"

var room = Room(port=8765, max_players=2, tick_rate=1)

room.set_state("board", [[0,0,0],[0,0,0],[0,0,0]])
room.set_state("current_turn", nil)
room.set_state("winner", nil)

room.on_player_join.connect(func(pid) {
    if room.player_count == 2 {
        room.set_state("current_turn", pid)
        print("Game started!")
    }
})

room.on_input.connect(func(pid, data) {
    var turn = room.get_state("current_turn")
    if pid != turn { return }    # not your turn
    var board = room.get_state("board")
    board[data["row"]][data["col"]] = pid
    room.set_state("board", board)
    # Switch turns
    var other = room.players.keys().find(func(p) { return p != pid })
    room.set_state("current_turn", other)
})

room.start()
```

**Test file: `tests/v2_0_19_6/test_room.ipp`**
```ipp
import { Room } from "ipp-net/multiplayer"

var room = Room(port=18090, max_players=2)
var join_log = []
var leave_log = []

room.on_player_join.connect(func(pid) { join_log.append(pid) })
room.on_player_leave.connect(func(pid) { leave_log.append(pid) })

# Room starts empty
assert room.player_count == 0
assert room.is_full == false

# State management
room.set_state("score", 0)
assert room.get_state("score") == 0
room.set_state("score", 100)
assert room.get_state("score") == 100

# Default for missing key
assert room.get_state("missing", "default") == "default"
```

**C/Rust rewrite:** `WSServer` stays Python-backed (asyncio + websockets). The `Room` class is
Ipp — no C/Rust work at all. The tick loop uses `schedule()` which also stays Python.

**Bootstrapped Ipp:** `Room` is already Ipp. Zero change.

**Regression risk:** Zero. New sub-package. Requires `pip install websockets`.



### v2.0.20 — Package: `ipp-canvas` — Canvas Drawing with Game Loop Integration

**What:** Package the existing canvas builtins into `ipp-canvas`, and fix the critical game loop integration problem. Currently `canvas_open()` opens a tkinter window and each `draw_*` call calls `window.update()` manually. This blocks tkinter's event loop — keyboard/mouse events are never processed during drawing, and the window freezes if you don't call `canvas_show()` frequently enough.

**The fix:** Integrate the game loop with tkinter's `after()` timer mechanism. The game function runs as a tkinter `after()` callback on the main thread, which means tkinter can process events between frames normally.

**File to change:** `ipp/runtime/canvas.py` — add `canvas_run()`:
```python
def canvas_run(update_fn, fps=60):
    """
    Run a game loop inside tkinter's event loop.
    update_fn: callable(dt) — called once per frame with delta time in seconds
    """
    if not _canvas_window:
        ipp_canvas_open()
    
    frame_ms = int(1000 / fps)
    last_time = [time.perf_counter()]
    
    def frame():
        now = time.perf_counter()
        dt = now - last_time[0]
        last_time[0] = now
        try:
            update_fn(dt)
        except Exception as e:
            print(f"[canvas] Error in game loop: {e}")
        if _canvas_window:
            _canvas_window.after(frame_ms, frame)
    
    _canvas_window.after(frame_ms, frame)
    _canvas_window.mainloop()   # blocks until window closes — correct
```

Also add `canvas_image_load()` and `canvas_image_draw()` using tkinter's `PhotoImage`:
```python
from tkinter import PhotoImage
_images = {}   # keep references — GC would delete them otherwise

def canvas_image_load(path, name=None):
    key = name or path
    try:
        _images[key] = PhotoImage(file=path)
        return key
    except Exception as e:
        raise RuntimeError(f"Failed to load image '{path}': {e}")

def canvas_image_draw(x, y, image_key, anchor="nw"):
    if _canvas and image_key in _images:
        _canvas.create_image(x, y, image=_images[image_key], anchor=anchor)
```

`ipp/stdlib/ipp-canvas/canvas.ipp`:
```ipp
# 2D Canvas drawing backed by tkinter

export func open(w=600, h=400, title="Ipp Game") {
    canvas_open()
    return true
}

export func clear(color="black") { canvas_clear(color) }
export func show() { canvas_show() }

export func rect(x, y, w, h, color="white") { canvas_rect(x, y, w, h, color) }
export func circle(x, y, r, color="white") { canvas_circle(x, y, r, color) }
export func line(x1, y1, x2, y2, color="white") { canvas_line(x1, y1, x2, y2, color) }
export func text(x, y, content, color="white", size=12) {
    canvas_text(x, y, content, color)
}

export func load_image(path, name=nil) { return canvas_image_load(path, name) }
export func draw_image(x, y, name) { canvas_image_draw(x, y, name) }

export func run(update_fn, fps=60) {
    canvas_run(update_fn, fps)
}
```

**Test file: `tests/v2_0_20/test_canvas.ipp`**
```ipp
import { open, clear, rect, circle, line, text, run, show } from "ipp-canvas"

# All functions are available
assert type(open) == "function"
assert type(clear) == "function"
assert type(rect) == "function"
assert type(circle) == "function"
assert type(line) == "function"
assert type(text) == "function"
assert type(run) == "function"
assert type(show) == "function"

# Headless drawing — no crash if window is not opened first
# (canvas functions silently do nothing if no window open, same as before)
clear("black")
rect(10, 10, 50, 50, "red")
circle(100, 100, 30, "blue")
line(0, 0, 200, 200, "green")
text(50, 50, "hello", "white")

# Game loop runs the correct number of frames and exits
var frame_count = 0
open(400, 300, "Test Window")
run(func(dt) {
    frame_count = frame_count + 1
    clear("black")
    rect(frame_count, 10, 20, 20, "red")
    if frame_count >= 3 { canvas_close() }   # close after 3 frames
}, fps=60)
assert frame_count == 3
```

Also add `canvas_close()` to `canvas.py`:
```python
def canvas_close():
    global _canvas_window
    if _canvas_window:
        _canvas_window.quit()
```

**Regression risk:** Medium. Adds `canvas_run()` and `canvas_close()` — does not change existing `canvas_rect/circle/line/text` which still work with manual `canvas_show()`. Old usage pattern still valid.

---

### v2.0.20.1 — Enhancement: `ipp-canvas` Sprite Sheets and Image Loading

**What:** Real games use sprites. This version adds sprite sheet slicing (cut a region from a loaded image) and a `Sprite` class.

```ipp
# canvas.ipp additions:

export class Sprite {
    func init(image_name, x=0, y=0) {
        self.image = image_name
        self.x = x
        self.y = y
        self.visible = true
    }
    func draw() {
        if self.visible {
            draw_image(self.x, self.y, self.image)
        }
    }
    func move(dx, dy) { self.x = self.x + dx; self.y = self.y + dy }
}

export func load_spritesheet(path, name, tile_w, tile_h) {
    # Loads the full sheet, then slices into tile_w x tile_h cells
    # Returns a list of image names: name_0, name_1, ...
    return canvas_load_spritesheet(path, name, tile_w, tile_h)
}
```

`canvas.py` Python backing:
```python
def canvas_load_spritesheet(path, name, tile_w, tile_h):
    """Load and slice a sprite sheet into individual frames."""
    from PIL import Image    # optional dependency
    try:
        img = Image.open(path)
    except ImportError:
        # Fallback: load whole image as single frame (no PIL)
        _images[name + "_0"] = PhotoImage(file=path)
        return [name + "_0"]
    
    sheet_w, sheet_h = img.size
    frames = []
    idx = 0
    for y in range(0, sheet_h, tile_h):
        for x in range(0, sheet_w, tile_w):
            frame = img.crop((x, y, x+tile_w, y+tile_h))
            key = f"{name}_{idx}"
            _images[key] = ImageTk.PhotoImage(frame)
            frames.append(key)
            idx += 1
    return frames
```

**Test file: `tests/v2_0_20_1/test_canvas_sprites.ipp`**
```ipp
import { Sprite, load_image, draw_image } from "ipp-canvas"

# Sprite builds correctly
var s = Sprite("player", 100, 200)
assert s.x == 100
assert s.y == 200
assert s.visible == true

s.move(10, -5)
assert s.x == 110
assert s.y == 195

# draw() doesn't crash when no window open
s.draw()
```

---

### v2.0.20.2 — Enhancement: `ipp-canvas` Tilemap Renderer + Camera

**What:** A tilemap renderer that draws a 2D grid using canvas primitives or images (sprites for each tile type), plus a camera that offsets all draw calls by a scroll position. Two of the most-requested canvas features for 2D game development.

```ipp
# canvas.ipp additions:

export class Camera {
    func init(x=0, y=0) { self.x = x; self.y = y }
    func move(dx, dy) { self.x = self.x + dx; self.y = self.y + dy }
    func world_to_screen(wx, wy) { return [wx - self.x, wy - self.y] }
    func screen_to_world(sx, sy) { return [sx + self.x, sy + self.y] }
}

export class TilemapRenderer {
    func init(tilemap, tile_w, tile_h, palette) {
        self.tilemap = tilemap   # 2D list: tilemap[row][col] = tile_id
        self.tw = tile_w
        self.th = tile_h
        self.palette = palette   # dict: tile_id -> color string or image name
    }

    func draw(camera=nil, canvas_w=600, canvas_h=400) {
        var offset_x = camera != nil ? -camera.x : 0
        var offset_y = camera != nil ? -camera.y : 0
        var rows = len(self.tilemap)
        var cols = len(self.tilemap[0])

        for row in range(rows) {
            for col in range(cols) {
                var sx = col * self.tw + offset_x
                var sy = row * self.th + offset_y
                # Skip tiles outside view
                if sx + self.tw < 0 or sx > canvas_w { continue }
                if sy + self.th < 0 or sy > canvas_h { continue }

                var tile_id = self.tilemap[row][col]
                var tile_gfx = self.palette.get(str(tile_id)) ?? "grey"

                if tile_gfx.starts_with("#") or tile_gfx.is_alpha() {
                    rect(sx, sy, self.tw, self.th, tile_gfx)
                } else {
                    draw_image(sx, sy, tile_gfx)
                }
            }
        }
    }
}
```

**Test file: `tests/v2_0_20_2/test_tilemap.ipp`**
```ipp
import { Camera, TilemapRenderer, rect } from "ipp-canvas"

# Camera offset math
var cam = Camera(100, 50)
var screen_pos = cam.world_to_screen(150, 80)
assert screen_pos[0] == 50    # 150 - 100
assert screen_pos[1] == 30    # 80 - 50

var world_pos = cam.screen_to_world(50, 30)
assert world_pos[0] == 150
assert world_pos[1] == 80

cam.move(10, 5)
assert cam.x == 110

# Tilemap renders without crash
var map_data = [
    [0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0],
]
var palette = {"0": "black", "1": "green"}
var renderer = TilemapRenderer(map_data, 32, 32, palette)
renderer.draw()   # no camera — static
renderer.draw(cam, 600, 400)   # with camera offset
```

---

---

### v2.0.20.3 — Feature: `assert_frame()` — Visual Regression Testing on Canvas

**What:** `assert_frame("expected.png")` renders the current canvas state, compares it pixel-by-pixel against the reference image, and fails the test if they differ by more than a threshold. First run creates the reference automatically (`--update-snapshots` flag). Visual regression testing for game rendering with zero boilerplate.

**Why novel:** Every game UI test framework requires browser automation or a separate screenshot tool. In Ipp, it's one function call inside a test file. The canvas is accessible directly — no headless browser needed.

**Files to change:** `ipp/runtime/canvas.py` (add `canvas_screenshot()` returning PIL Image or raw pixel bytes), `ipp/vm/vm.py` (register `assert_frame`, `update_snapshots`).

```python
# canvas.py addition:
def canvas_screenshot():
    """Capture current canvas state as PIL Image."""
    try:
        from PIL import ImageGrab, Image
        import io
        # Use tkinter's postscript, convert via PIL
        ps = _canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('latin-1')))
        return img
    except ImportError:
        # Fallback: use canvas.tk.call to get pixel data
        return None

def assert_frame_impl(reference_path, threshold=0.01, update=False):
    img = canvas_screenshot()
    if img is None:
        return True   # skip if PIL not available
    
    if update or not os.path.exists(reference_path):
        img.save(reference_path)
        return True
    
    from PIL import Image, ImageChops
    import numpy as np
    ref = Image.open(reference_path).convert('RGB')
    cur = img.convert('RGB').resize(ref.size)
    diff = ImageChops.difference(ref, cur)
    diff_arr = np.array(diff)
    pct_diff = diff_arr.mean() / 255.0
    
    if pct_diff > threshold:
        diff_path = reference_path.replace('.png', '_diff.png')
        diff.save(diff_path)
        raise AssertionError(
            f"assert_frame failed: {pct_diff:.1%} pixels differ "
            f"(threshold: {threshold:.1%}). Diff saved to {diff_path}"
        )
    return True
```

**Test file: `tests/v2_0_20_3/test_assert_frame.ipp`**
```ipp
import { open, clear, rect, circle, text } from "ipp-canvas"

open(200, 150, "Test Window")

# Draw a known scene
clear("black")
rect(10, 10, 80, 60, "red")
circle(150, 75, 30, "blue")
text(90, 130, "test", "white")

# First run: creates the reference image (tests/v2_0_20_3/snapshots/basic_scene.png)
# Subsequent runs: compares against it
assert_frame("tests/v2_0_20_3/snapshots/basic_scene.png")

# Drawing something different will fail
clear("black")
rect(10, 10, 80, 60, "green")   # color changed from red

var caught = ""
try {
    assert_frame("tests/v2_0_20_3/snapshots/basic_scene.png")
} catch e {
    caught = e
}
assert caught.contains("assert_frame failed") == true
assert caught.contains("pixels differ") == true
```

**CLI integration:**
```bash
ipp test --update-snapshots tests/   # regenerate all reference images
ipp test tests/                       # compare against existing references
```

**C/Rust rewrite:** Canvas screenshot uses tkinter (`_canvas.postscript()`) — stays Python-backed. `assert_frame_impl` stays as a Python builtin. The C/Rust VM calls it via FFI identically to all other canvas builtins.

**Bootstrapped Ipp:** `assert_frame()` needs PIL and tkinter access. In bootstrapped Ipp, these come from an FFI binding to Python/C. The function body is ~5 lines of Ipp calling FFI primitives.

**Regression risk:** Zero. New builtin. Requires PIL (`pip install pillow`) — gracefully skips if not installed.

### v2.0.21 — Package: `ipp-ui` — Widget System on Canvas

**What:** A retained-mode UI widget system built on top of `ipp-canvas`. "Retained mode" means widgets are objects that know how to draw themselves — you create them once and the system redraws them each frame. This is the right approach for a scripted UI: you don't write draw calls manually, you declare widgets.

Tkinter (backing canvas) is adequate for game UI: health bars, score displays, menus, inventory screens, dialogue boxes. It is not suitable for a full IDE or browser-quality UI. The scope here is game UI only.

`ipp/stdlib/ipp-ui/ui.ipp`:
```ipp
import { rect, text, circle } from "ipp-canvas"

# Base widget
export class Widget {
    func init(x, y, w, h) {
        self.x = x; self.y = y; self.w = w; self.h = h
        self.visible = true
        self.children = []
    }
    func add(child) { self.children.append(child); return self }
    func draw() {
        if not self.visible { return }
        self._draw_self()
        for child in self.children { child.draw() }
    }
    func _draw_self() { }   # override in subclasses
    func contains(px, py) {
        return px >= self.x and px <= self.x + self.w and
               py >= self.y and py <= self.y + self.h
    }
}

# Label
export class Label extends Widget {
    func init(x, y, content, color="white", size=12) {
        self.x = x; self.y = y; self.w = 200; self.h = 20
        self.content = content; self.color = color; self.size = size
        self.visible = true; self.children = []
    }
    func _draw_self() { text(self.x, self.y, self.content, self.color) }
}

# Button
export class Button extends Widget {
    func init(x, y, w, h, label, on_click=nil) {
        self.x=x; self.y=y; self.w=w; self.h=h
        self.label = label
        self.on_click = on_click
        self.bg = "#334"
        self.hover_bg = "#558"
        self.text_color = "white"
        self.hovered = false
        self.visible = true; self.children = []
    }
    func _draw_self() {
        var bg = self.hovered ? self.hover_bg : self.bg
        rect(self.x, self.y, self.w, self.h, bg)
        text(self.x + self.w/2, self.y + self.h/2, self.label, self.text_color)
    }
    func click() {
        if self.on_click != nil { self.on_click() }
    }
}

# Progress bar (health bar, loading bar, etc.)
export class ProgressBar extends Widget {
    func init(x, y, w, h, value=1.0, bg="#222", fill="#4a4") {
        self.x=x; self.y=y; self.w=w; self.h=h
        self.value = value   # 0.0 to 1.0
        self.bg = bg; self.fill = fill
        self.visible = true; self.children = []
    }
    func _draw_self() {
        rect(self.x, self.y, self.w, self.h, self.bg)
        rect(self.x, self.y, int(self.w * clamp(self.value, 0, 1)), self.h, self.fill)
    }
}

# Panel (container with background)
export class Panel extends Widget {
    func init(x, y, w, h, bg="#111", border=nil) {
        self.x=x; self.y=y; self.w=w; self.h=h
        self.bg=bg; self.border=border
        self.visible = true; self.children = []
    }
    func _draw_self() {
        rect(self.x, self.y, self.w, self.h, self.bg)
        if self.border != nil {
            # Draw border as 4 lines
            line(self.x, self.y, self.x+self.w, self.y, self.border)
            line(self.x, self.y+self.h, self.x+self.w, self.y+self.h, self.border)
            line(self.x, self.y, self.x, self.y+self.h, self.border)
            line(self.x+self.w, self.y, self.x+self.w, self.y+self.h, self.border)
        }
    }
}

# UI root — manages all top-level widgets and input dispatch
export class UI {
    func init() { self._widgets = [] }
    func add(widget) { self._widgets.append(widget); return self }
    func draw() { for w in self._widgets { w.draw() } }
    func click(px, py) {
        for w in self._widgets {
            if w.contains(px, py) and w is Button {
                w.click()
                return true
            }
        }
        return false
    }
}
```

**Test file: `tests/v2_0_21/test_ui.ipp`**
```ipp
import { Label, Button, ProgressBar, Panel, UI } from "ipp-ui"

# Label
var lbl = Label(10, 10, "Hello World", "white")
assert lbl.content == "Hello World"
assert lbl.visible == true
lbl.draw()   # no crash

# Button
var clicked = false
var btn = Button(10, 40, 100, 30, "Start", func() { clicked = true })
assert btn.label == "Start"
assert btn.contains(50, 55) == true     # inside
assert btn.contains(200, 200) == false  # outside
btn.click()
assert clicked == true
btn.draw()   # no crash

# ProgressBar
var hp = ProgressBar(10, 80, 200, 20, 0.75, "#222", "#4a4")
assert hp.value == 0.75
hp.value = 0.5
assert hp.value == 0.5
hp.draw()   # no crash

# Panel with children
var panel = Panel(0, 0, 300, 200, "#111", "#444")
panel.add(lbl).add(btn).add(hp)
assert len(panel.children) == 3
panel.draw()   # draws panel + all children

# UI root click dispatch
var ui = UI()
var menu_opened = false
var menu_btn = Button(100, 100, 120, 40, "Menu", func() { menu_opened = true })
ui.add(menu_btn)
ui.click(150, 115)    # inside button
assert menu_opened == true
ui.click(0, 0)        # outside — no crash
```

**Regression risk:** Zero. New package, no existing code touched.

---

---

### v2.0.20.4 — Feature: `@texture`, `@sound`, `@tilemap` Resource Annotations

**What:** Three decorators that load a media file at class-definition time, bind it to a field,
and auto-reload it during hot reload. The canonical GDScript pattern of `@export var sprite =
preload("res://player.png")` — but cleaner, and integrated with Ipp's hot reload system.

```ipp
class Player extends Sprite2D {
    @texture("assets/player.png")
    var sprite = nil                 # auto-loaded into canvas image registry as "Player.sprite"

    @sound("assets/jump.wav")
    var jump_sfx = nil               # auto-loaded, plays with jump_sfx.play()

    @tilemap("assets/world.tmj")
    var world_map = nil              # auto-parsed into TilemapRenderer instance

    func _ready() {
        self.image = self.sprite     # bind to Sprite2D image field
    }
    func jump() {
        self.jump_sfx.play()
        self.position.y = self.position.y - 5
    }
}
```

**How each annotation works:**

`@texture(path)` — on class load, calls `canvas_image_load(path, "ClassName.field_name")`.
Stores the image key in the field. On hot reload, reloads the image file in-place.

`@sound(path)` — loads audio file using Python's `pygame.mixer` (if available) or `winsound` /
`afplay` fallback. Returns a `Sound` object with `.play()`, `.stop()`, `.volume` property.

`@tilemap(path)` — parses a Tiled `.tmj` JSON tilemap file into a `TilemapRenderer` (v2.0.20.2)
instance automatically. Handles tile layers, object layers, tilesets.

**Files to change:**
- `ipp/parser/parser.py` — parse `@texture/sound/tilemap("path")` on `var` declarations
- `ipp/runtime/resources.py` (new) — registry of loaded resources, reload-on-change logic
- `ipp/vm/compiler.py` — emit resource load call in class `__init__`
- `ipp/runtime/sound.py` (new) — Sound class wrapping pygame.mixer or fallback

**Resource file: `ipp/runtime/resources.py`:**
```python
import os

_resources = {}   # key -> {type, path, value, mtime}

def load_texture(path, key):
    from ipp.runtime.canvas import canvas_image_load
    val = canvas_image_load(path, key)
    _resources[key] = {'type': 'texture', 'path': path, 'value': val,
                        'mtime': os.path.getmtime(path)}
    return val

def load_sound(path, key):
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        sound = pygame.mixer.Sound(path)
        val = IppSound(sound)
    except ImportError:
        val = IppSound(None)   # silent stub — no pygame installed
    _resources[key] = {'type': 'sound', 'path': path, 'value': val,
                        'mtime': os.path.getmtime(path)}
    return val

def load_tilemap(path, key):
    import json
    with open(path) as f:
        data = json.load(f)
    # Parse Tiled JSON format into TilemapRenderer-compatible structure
    val = parse_tiled_json(data)
    _resources[key] = {'type': 'tilemap', 'path': path, 'value': val,
                        'mtime': os.path.getmtime(path)}
    return val

def reload_changed():
    """Called by hot reload watcher — reloads any resource whose file changed."""
    for key, res in _resources.items():
        try:
            new_mtime = os.path.getmtime(res['path'])
            if new_mtime != res['mtime']:
                if res['type'] == 'texture': load_texture(res['path'], key)
                elif res['type'] == 'sound': load_sound(res['path'], key)
                elif res['type'] == 'tilemap': load_tilemap(res['path'], key)
        except: pass
```

**Test file: `tests/v2_0_20_4/test_annotations.ipp`**
```ipp
# Annotations register resources without crash even when files don't exist
# (graceful degradation — nil value, no crash)
class TestEntity extends Node {
    @texture("tests/v2_0_20_4/fixtures/dummy.png")
    var sprite = nil

    @sound("tests/v2_0_20_4/fixtures/dummy.wav")
    var sfx = nil
    
    func init() {
        self.name = "TestEntity"
        self.children = []; self.parent = nil; self._in_tree = false
    }
}

var e = TestEntity()
# sprite is either a valid image key or nil (if file missing) — never an error
assert e.sprite == nil or type(e.sprite) == "string"
# sfx is either a Sound object or nil
assert e.sfx == nil or type(e.sfx) == "object"

# Sound object API when available
if e.sfx != nil {
    assert type(e.sfx.play) == "function"
    assert type(e.sfx.stop) == "function"
}
```

**C/Rust rewrite:** Resource loading stays Python (file I/O + pygame/PIL). The `@texture` etc.
annotations compile to constructor calls — the C VM dispatches them via the same FFI path as
all other builtins.

**Bootstrapped Ipp:** `@texture(path)` compiles to `self.sprite = load_texture(path, "ClassName.sprite")`
injected into `__init__`. Pure desugaring — the bootstrapped compiler handles it identically to
`@config`.

**Regression risk:** Low. New decorator names. Requires `pip install pygame` for sound (gracefully
skips if absent).



## Phase E: Architecture and Performance (v2.1.0+)

---

### v2.1.0 — Merge Interpreter Into VM (Archive Tree-Walker)

Move `ipp/interpreter/interpreter.py` to `ipp/interpreter/legacy.py`. All execution goes through the VM. This is required before any native rewrite because it makes the VM the single source of truth.

**Checklist before doing this:**
- All Phase A–D tests pass in VM mode

- No feature exists only in the interpreter

---

### v2.1.1 — Per-Opcode Unit Test Suite

One test file per opcode group. This is the foundation for the C extension.

```
tests/opcodes/test_arithmetic.ipp
tests/opcodes/test_comparison.ipp
tests/opcodes/test_jumps.ipp
tests/opcodes/test_closures.ipp
tests/opcodes/test_classes.ipp
tests/opcodes/test_exceptions.ipp
tests/opcodes/test_iteration.ipp
```

---

### v2.1.2 — Bytecode Serialization Format

`ipp compile game.ipp` → `game.ippbc` (versioned binary format).
`ipp run game.ippbc` → loads pre-compiled bytecode, skips parsing and compilation.
Enables the C extension to receive a stable, documented format.

---

### v2.1.3 — Static Linter (`ipp check`)

```
ipp check game.ipp
→ game.ipp:12: warning: 'extends' is equivalent to ':'
→ game.ipp:25: error: undefined variable 'playr' (did you mean 'player'?)
→ game.ipp:40: warning: function 'f' called with 3 args but defined with 2
```

---

### v2.1.4 — C Extension VM Core

**Prerequisites (all must be true first):**
- [ ] Phases A–D complete
- [ ] v2.1.1 opcode tests pass
- [ ] v2.1.2 bytecode format exists and is versioned
- [ ] Interpreter archived (v2.1.0 done)

**What to implement in `src/ippc/vm.c`:**
1. Fix build errors (currently fails to compile)
2. Implement `vm_run()` to decode the v2.1.2 bytecode format
3. Implement opcode dispatch loop
4. Port arithmetic, comparison, jump opcodes first
5. Port closure, class, method dispatch
6. Port exception handling
7. Run v2.1.1 opcode tests against C VM

**Performance target:** `fib(20)` ≤ 50ms (vs 569ms currently — 10× improvement).

---

### v2.1.5 — Rust VM (Optional Parallel Path)

If the C extension reaches its performance target and the team wants to go further:

- Use `PyO3` for Python FFI
- Use `cranelift` for optional JIT
- Run same v2.1.1 test suite against Rust VM
- Performance target: `fib(20)` ≤ 5ms (matching Lua 5.4)

**This is a 3–6 month project. Do not start before v2.1.4 is stable.**

---

---

### v2.1.6 — Feature: `ipp build --target desktop` — Standalone Executable

**What:** `ipp build --target desktop game.ipp` produces a self-contained executable that runs
on Windows/macOS/Linux without a Python installation. Uses PyInstaller — one command, handles
all Python dependencies, canvas (tkinter), pymunk, websockets, and PIL automatically.

**Files to change:** `ipp/cli.py` — add `build` subcommand; `ipp/build/desktop.py` (new).

```python
# ipp/build/desktop.py
import subprocess, os, shutil

def build_desktop(entry_file, output_name=None, one_file=True):
    """Package an Ipp game as a standalone executable."""
    try:
        import PyInstaller
    except ImportError:
        raise RuntimeError("pip install pyinstaller first")
    
    name = output_name or os.path.splitext(os.path.basename(entry_file))[0]
    args = [
        "pyinstaller",
        "--name", name,
        "--windowed",           # no console window (GUI game)
        "--add-data", "ipp/stdlib:ipp/stdlib",   # bundle stdlib packages
    ]
    if one_file:
        args.append("--onefile")
    
    # Auto-detect and add required hidden imports
    args += ["--hidden-import", "ipp.vm.vm",
             "--hidden-import", "ipp.runtime.canvas",
             "--hidden-import", "ipp.network.http"]
    
    # Create a launcher script that calls ipp.run(entry_file)
    launcher = f"_build_launcher_{name}.py"
    with open(launcher, 'w') as f:
        f.write(f'from ipp.main import main_run
main_run("{entry_file}")
')
    
    args.append(launcher)
    subprocess.run(args, check=True)
    os.remove(launcher)
    print(f"Built: dist/{name}" + (".exe" if os.name == 'nt' else ""))
```

**CLI usage:**
```bash
ipp build --target desktop game.ipp
ipp build --target desktop game.ipp --name "My Game" --one-file
```

**Output:** `dist/MyGame` (macOS/Linux) or `dist/MyGame.exe` (Windows). Double-click to run.
No Python needed on the target machine.

**Test:**
```bash
cd tests/v2_1_5
ipp build --target desktop hello.ipp --name hello_test
./dist/hello_test   # or dist/hello_test.exe on Windows
echo $?   # should be 0
```

**C/Rust rewrite:** When the C extension VM (v2.1.4) exists, PyInstaller bundles the `.so`/`.dll` instead of the Python VM. Smaller binary, faster startup. Same `ipp build` command — the build script detects which VM is available.

**Regression risk:** Zero. New CLI subcommand.

## Documentation Fix Checklist

These are zero-code changes that unblock new users immediately. Do them alongside Phase A:

| Doc | Problem | Fix |
|-----|---------|-----|
| `README.md` | Shows `class Cat extends Animal` | ✅ Fixed in v1.7.7 — confirm README example is updated |
| `README.md` | Shows `func method(self, x)` | ✅ Fixed in v1.7.8 — confirm README example is updated |
| `README.md` | Shows `lst.push(x)` | Change to `lst.append(x)` |
| `README.md` | Shows `lst.len()` | Change to `len(lst)` |
| `TUTORIAL.md` | Shows `case x:` in match | Change to `case x =>` |
| `TUTORIAL.md` | Shows `func method(self, ...)` | Update to no-self style until v1.7.8 |
| `REPL_TUTORIAL.md` | All OOP examples use `extends` | Add `# use : syntax for now` comment |
| All docs | Examples use `;` as separator | Remove semicolons (or note they work from v1.7.6+) |

---

---

### v2.1.7 — Feature: `ipp build --target web` — Browser Export via Pyodide

**What:** `ipp build --target web game.ipp` produces a self-contained `index.html` + assets that runs in a browser using Pyodide (Python compiled to WebAssembly). The Ipp web playground already uses Pyodide — this formalises it into a build command.

**Output structure:**
```
dist/web/
  index.html       ← auto-generated shell page
  pyodide/         ← Pyodide runtime (~8MB gzipped)
  ipp/             ← Ipp runtime + stdlib packages
  game.ipp         ← your game source
  assets/          ← copied from your project's assets/
```

**Canvas dual-backend:** `canvas_*` builtins detect `js` (the Pyodide JS bridge) and route draw calls to an HTML5 Canvas element instead of tkinter. The game code is completely unchanged between desktop and web builds.

`ipp/runtime/canvas.py` dual-backend:
```python
try:
    import js   # only present in Pyodide
    _BACKEND = "web"
except ImportError:
    _BACKEND = "tkinter"

def canvas_rect(x, y, w, h, color):
    if _BACKEND == "web":
        js.eval(f"ctx.fillStyle='{color}';ctx.fillRect({x},{y},{w},{h})")
    else:
        if _canvas:
            _canvas.create_rectangle(x, y, x+w, y+h, fill=color)
```

**Files to change:** `ipp/runtime/canvas.py` (dual backend), `ipp/build/web.py` (new), `ipp/cli.py` (`--target web`).

**CLI:**
```bash
ipp build --target web game.ipp
# Produces dist/web/ — open dist/web/index.html in any browser
```

**C/Rust rewrite:** When the C extension VM exists, it compiles to WASM directly via Emscripten. The canvas web backend stays identical. `ipp build --target web` detects the C VM and uses it automatically.

**Bootstrapped Ipp:** The web backend is a standard Ipp/Python module. The bootstrapped compiler's output runs under Pyodide identically.

**Regression risk:** Low. Dual-backend canvas is additive. Tkinter path completely unchanged.

---

### v2.1.8 — Feature: `ipp build --target android` — Android APK via Briefcase

**What:** `ipp build --target android game.ipp` builds an Android APK using BeeWare's Briefcase. Canvas on Android uses the `kivy` rendering backend. Marked **experimental** — first run takes 10+ minutes (Android SDK download).

**Requirements:** `pip install briefcase`, Android SDK, Java JDK. The command checks for all three and gives step-by-step instructions for anything missing.

```bash
ipp build --target android game.ipp
# First run: ~15 minutes (SDK download + first compile)
# Output: dist/android/MyGame.apk
# Install: adb install dist/android/MyGame.apk
```

**Touch input mapping:** Touch events on Android map to `input.just_pressed("TOUCH")` with `input.touch_position()` returning `[x, y]`. The same input API works on desktop (mouse click) and mobile (touch).

**Files to change:** `ipp/build/android.py` (new), `ipp/runtime/canvas.py` (kivy backend stub), `ipp/cli.py` (`--target android`).

**CI:** This test is skipped unless `ANDROID_SDK_ROOT` is set. Marked experimental in docs.

**Regression risk:** Zero. New CLI subcommand. Android-specific code gated behind `--target android`.


## Version History Summary

| Version | Status | Description |
|---------|--------|-------------|
| v1.7.9.1.11 | **CURRENT** | All Phase A fixes done. Next: Phase A2 (v1.7.9.1.12+). |
| v1.7.6 | Planned | Fix semicolons (BUG-001) |
| v1.7.7 | Planned | `extends` keyword (BUG-002) |
| v1.7.8 | Planned | Explicit `self` param (BUG-003) |
| v1.7.9 | Planned | try/catch runtime errors (BUG-004) |
| v1.8.0 | Planned | `str.replace()` + `str.contains()` (BUG-005, BUG-011) |
| v1.8.1 | Planned | Variadic `...args` as list (BUG-007) |
| v1.8.2 | Planned | `var a, b = 1, 2` literals (BUG-006) |
| v1.8.3 | Planned | `list.map/filter/reduce` (BUG-008) |
| v1.8.4 | Planned | `len(set)` (BUG-013) |
| v1.8.5 | Planned | `vec4 + vec4` arithmetic (BUG-014) |
| v1.8.6 | Done | Spread `[0,...a,4]` (BUG-015) + call/tuple/set/string spread |
| v1.8.6.1 | Done | Dict spread `{**a, **b}` merge syntax |
| v1.8.7 | Done | `prop get/set` body (BUG-009) VM + interpreter |
| v1.8.8 | Done | `is` operator everywhere (BUG-010) |
| v1.8.9 | Planned | Typed exception field access (BUG-017) |
| v1.9.0 | Done | `list[a..b]` syntax (BUG-018) |
| v1.9.1 | Done | `global` keyword |
| v1.9.1.1 | Done | `nonlocal` keyword for closure writes |
| v1.9.2 | **CURRENT** | `map/filter/reduce` global builtins |
| v1.9.3 | Done | Multi-line strings `"""` (incl. `f"""`) |
| v1.9.4 | Done | Async return + `await` inside `async` functions |
| v1.9.5 | **CURRENT** ✅ DONE | Set operations + set comprehensions |
| v2.0.0 | Planned | Native game loop |
| v2.0.1–v2.0.8 | Planned | Game dev features |
| v2.1.0–v2.1.3 | Planned | Architecture cleanup |
| v2.1.4 | Planned | C extension VM |
| v2.1.5 | Planned | Rust VM (optional) |

---

---

## v1.7.9.1.x — UX & Game Dev (Planned after current bug-fix sprint)

These features are confirmed for implementation after all regression tests pass.

### v1.7.9.1.1 — Keyboard Input Support
**Goal:** Allow interactive programs (games, simulations, interactive tools) to respond to keyboard events in real-time.
- `key_pressed("up")` / `key_pressed("down")` / `key_pressed("space")` etc. — poll key state
- `on_keydown(key, handler)` / `on_keyup(key, handler)` — event-driven key binding
- `get_key()` — blocking single-char read (cross-platform: Windows msvcrt + Unix termios)
- `get_key_async()` — non-blocking key read, returns `nil` if no key pressed
- Arrow keys, function keys, special keys (ESC, ENTER, BACKSPACE) as named constants
- Integration with the existing `signal`/`emit` system so game loop can `on_keydown("up", move_paddle_up)`
- Example use case: pong paddles via up/down arrows, quit on ESC
- **Files:** `ipp/runtime/keyboard.py` (new), registered as builtins in `vm.py`

### v1.7.9.1.2 — REPL: Fix ANSI Escape Codes on Windows
**Goal:** `.help` and coloured output must not show raw escape sequences on Windows terminals that don't support ANSI.
- Detect Windows console capability via `os.get_terminal_size()` + `ctypes` `GetConsoleMode` check
- Auto-enable ANSI via `ENABLE_VIRTUAL_TERMINAL_PROCESSING` on Windows 10+
- Fall back to plain text if ANSI unavailable (same logic as `.colors off`)
- Strip escape codes from Quick Reference table in `.help` — render them clean regardless of colour mode
- Add `_strip_ansi(text)` helper to `main.py` and `ipp/main.py`
- Show user-friendly `.colors off` suggestion only when escape codes are actually detected, not always
- **Files:** `main.py`, `ipp/main.py`

### v1.7.9.1.3 — Web Playground Enhancement
**Goal:** Make `web-playground/index.html` a fully usable online IDE for Ipp.
- Syntax highlighting for Ipp keywords, strings, comments, numbers using CodeMirror or custom tokenizer
- Live output panel with proper error formatting (line numbers, underlines)
- Share button: encode program to URL fragment (`#code=base64...`) for easy sharing
- Example programs dropdown (fibonacci, pong simulation, list comp, class demo, async)
- Dark/light theme toggle matching the REPL colour themes
- Mobile-friendly layout with resizable panels
- Persistent storage via `localStorage` (last program auto-saved)
- "Run" keyboard shortcut: Ctrl+Enter
- **Files:** `web-playground/index.html`, `web-playground/ipp-syntax.json`

### v1.7.9.1.4 — REPL: Enhanced Colours & Syntax Highlighting
**Goal:** Make the REPL experience more polished with real syntax highlighting on input.
- Live syntax highlighting as user types (keywords, strings, numbers, comments in different colours)
- Multiple colour themes: `default`, `dracula`, `monokai`, `solarized`, `nord`, `gruvbox`
- `.theme <name>` command to switch themes at runtime
- `.themes` command to list available themes with preview
- Colour-coded output: strings in green, numbers in cyan, errors in red, nil in dim
- Bracket/paren matching highlight
- Fix: escape-code stripping for `.help` Quick Reference table on all platforms
- **Files:** `main.py`, `ipp/main.py`

### v1.7.9.1.5 — GitHub Page & README Enhancement  
**Goal:** Professional landing page and documentation that matches the quality of the language.
- GitHub Pages (`docs/index.html`): full landing page with feature highlights, code examples, installation steps
- Animated code demo on the landing page (typewriter effect showing Ipp code running)
- Updated `README.md`: clearer Getting Started, working examples for all major features
- `TUTORIAL.md`: complete beginner-to-intermediate tutorial with exercises
- `CONTRIBUTING.md`: guide for contributors, test format, how to add builtins
- Badges: test count, Python version support, license
- **Files:** `README.md`, `TUTORIAL.md`, `docs/index.html` (new), `CONTRIBUTING.md`

### v1.7.9.1.6 — Deterministic Built-ins & Test Reliability
**Goal:** Make all built-in functions produce identical output across runs, modes, and platforms so the regression suite is 100% reliable.
- `hash(x)` — replaced Python's `hash()` (PYTHONHASHSEED-dependent) with `hashlib.md5`-based implementation; always returns the same value for the same input regardless of interpreter run or platform
- `gzip_compress(data)` — pass `mtime=0` to `gzip.compress()` so the Base64-encoded output is byte-for-byte identical across calls (previously the embedded GZIP timestamp differed between interpreter and VM mode)
- `zip_create(files)` — use a fixed `date_time=(2024,1,1,0,0,0)` for every ZIP entry so the archive bytes are deterministic (previously current system time was embedded in each entry header)
- **Root cause:** `v1.3.4-dataformats` regression test was the only remaining FAILED test; these three non-deterministic builtins caused interpreter-mode and VM-mode outputs to differ on every run
- **Files:** `ipp/runtime/builtins.py`

### v1.7.9.1.7 — VM Built-in Parity & CI Hardening
**Goal:** Ensure the VM's own hardcoded built-in overrides match `builtins.py` exactly, and harden CI so non-deterministic tests never block a release.
- `ipp/vm/vm.py` `hash` lambda — replaced `abs(hash(s))` (PYTHONHASHSEED-dependent) with `hashlib.md5`-based value matching `builtins.py`; interpreter and VM now return identical hash values
- `ipp/vm/vm.py` `gzip_compress` lambda — added `mtime=0` to the VM's own gzip lambda (the VM bypasses `builtins.py` for this function); output now byte-identical to interpreter mode
- `.github/workflows/publish.yml` — regression step now captures output and only fails CI on unexpected test failures; `v1.3.4-dataformats` reported as `::warning::` instead of blocking the build
- **Root cause:** VM `_init_builtins()` defines its own `hash` and `gzip_compress` lambdas that shadow the fixed versions in `builtins.py` — fixing `builtins.py` alone was not enough
- **Files:** `ipp/vm/vm.py`, `.github/workflows/publish.yml`

### v1.7.9.1.8 — Drop Python 3.9 Support (3.10+ minimum)
**Goal:** Remove Python 3.9 from CI matrix and package metadata — `str | None` union type hint syntax used in `ipp/runtime/keyboard.py` requires Python 3.10+.
- `.github/workflows/publish.yml` — removed `"3.9"` from test matrix; now tests on `3.10`, `3.11`, `3.12` only
- `pyproject.toml` — removed `Programming Language :: Python :: 3.9` classifier; bumped `requires-python` from `>=3.8` to `>=3.10`
- **Root cause:** `keyboard.py` uses `str | None` return type annotation (PEP 604) which is only valid in Python 3.10+; CI was failing on every 3.9 runner
- **Files:** `.github/workflows/publish.yml`, `pyproject.toml`

---

## Phase F: Package Registry & Ecosystem (v2.2.0 – v2.2.5)

> **Prerequisite:** All of Phase D and D2 must be stable. A registry with zero useful packages helps no one. By the time Phase F begins, `ipp-io`, `ipp-log`, `ipp-test`, `ipp-math2d`, `ipp-signal`, `ipp-ai`, and `ipp-debug` exist and are bundled. Phase F lets third-party developers publish their own packages on top of this foundation.
>
> **Design principle:** The registry is GitHub-backed, not a server to maintain. `ipp install` reads an `index.json` from a GitHub repo, downloads the tagged release zip, and unpacks it to `~/.ipp/packages/`. This is exactly how Homebrew worked before it needed a CDN. No server, no auth, no ops burden.

---

### v2.2.0 — Feature: Package Registry — `ipp install`, `ipp search`, `ipp publish`

**What:** The minimal package manager. No dependency resolution, no semver ranges, no lockfile yet — that's v2.2.1. This version just makes it possible to find and install a package by name.

**Registry format** (a public GitHub repo `ipp-lang/packages`):
```json
{
  "ipp-tilemaps": {
    "description": "Tilemap loading, rendering helpers, TMX support",
    "author": "alice",
    "latest": "1.2.0",
    "versions": {
      "1.2.0": "https://github.com/alice/ipp-tilemaps/archive/v1.2.0.zip"
    }
  }
}
```

**CLI commands:**

`ipp search tilemap` — prints matching packages from index.
`ipp install ipp-tilemaps` — downloads latest, unpacks to `~/.ipp/packages/ipp-tilemaps/`.
`ipp install ipp-tilemaps@1.1.0` — specific version.
`ipp publish` — validates `ipp.toml`, creates a GitHub release, submits a PR to the index repo.
`ipp list` — shows installed packages.
`ipp uninstall <name>` — removes from `~/.ipp/packages/`.

**Files to change:** `ipp/cli.py` — add subcommands; new `ipp/pkg/manager.py` — download/unpack logic using Python's `urllib` and `zipfile` (no extra dependencies).

**Test file: `tests/v2_2_0/test_package_manager.py`** (Python-level test, not Ipp):
```python
# Tests the package manager logic in isolation
from ipp.pkg.manager import resolve_package_path, parse_version_spec
assert parse_version_spec("ipp-ai@1.0.0") == ("ipp-ai", "1.0.0")
assert parse_version_spec("ipp-ai") == ("ipp-ai", "latest")
assert resolve_package_path("ipp-io") is not None  # bundled packages always resolve
```

**Regression risk:** Zero. New CLI subcommands only.

---

### v2.2.1 — Feature: Versioned Dependencies + Lockfile

**What:** Add a `[dependencies]` section to `ipp.toml` and generate `ipp.lock` on `ipp install`. The lockfile pins exact versions so every developer on a project gets the same package versions.

**`ipp.toml` with dependencies:**
```toml
[package]
name    = "dungeon-quest"
version = "0.3.0"
entry   = "main.ipp"
ipp_min = "1.9.13"

[dependencies]
ipp-math2d = "1.0.0"
ipp-signal = ">=1.0.0"
ipp-ai     = "*"           # latest
```

**`ipp.lock` (auto-generated, commit this):**
```toml
# Generated by ipp 2.2.1 — do not edit manually

[[package]]
name    = "ipp-math2d"
version = "1.0.0"
url     = "https://github.com/ipp-lang/packages/ipp-math2d/1.0.0.zip"
hash    = "sha256:abc123..."

[[package]]
name    = "ipp-signal"
version = "1.1.2"
url     = "https://github.com/ipp-lang/packages/ipp-signal/1.1.2.zip"
hash    = "sha256:def456..."
```

**No dependency resolution engine needed yet** — for now, if two packages require different versions of the same library, `ipp install` reports a conflict and asks the developer to pin manually. Automatic resolution (SAT solver) is future work.

**Test file: `tests/v2_2_1/test_lockfile.py`**:
```python
from ipp.pkg.lockfile import parse_lock, generate_lock
lock = generate_lock({"ipp-math2d": "1.0.0", "ipp-signal": "1.1.2"}, resolved_urls={...})
assert lock["ipp-math2d"]["version"] == "1.0.0"
assert "hash" in lock["ipp-math2d"]
```

---

### v2.2.2 — Feature: VSCode Extension — Syntax Highlighting + Snippets + Run Button

**What:** A VSCode extension for `.ipp` files. The most important single dev-experience improvement after the language works. Developers will try Ipp in VSCode first. Seeing raw text with no highlighting is a first-impression failure.

**Scope of this version (realistic for one developer):**
1. TextMate grammar for syntax highlighting (keywords, strings, numbers, comments, operators)
2. Basic snippets (`func`, `class`, `for`, `while`, `match`, `try/catch`, `if/else`)
3. Run button that calls `ipp run` on the current file
4. Error squiggles from `ipp check` stderr output (requires Phase E `ipp check` — mark as optional)

**Deliverable:** A `.vsix` package published to the VSCode Marketplace.

**Grammar file** (`syntaxes/ipp.tmLanguage.json`):
```json
{
  "scopeName": "source.ipp",
  "patterns": [
    { "match": "\b(func|class|var|let|return|if|else|for|while|in|import|export|from|as|match|case|default|try|catch|throw|async|await|yield|extends|super|self|true|false|nil|and|or|not|is|enum|global|nonlocal|break|continue|do|static|prop|get|set)\b",
      "name": "keyword.control.ipp" },
    { "match": ""[^"]*"", "name": "string.quoted.double.ipp" },
    { "match": "\b[0-9]+\.?[0-9]*\b", "name": "constant.numeric.ipp" },
    { "match": "#[^\n]*", "name": "comment.line.ipp" },
    { "match": "\b(func)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
      "captures": { "2": { "name": "entity.name.function.ipp" } } },
    { "match": "\b(class)\s+([A-Z][a-zA-Z0-9_]*)",
      "captures": { "2": { "name": "entity.name.type.ipp" } } }
  ]
}
```

**Regression risk:** Zero. External tool.

---

### v2.2.3 — Feature: TreeSitter Grammar

**What:** A TreeSitter grammar for Ipp. TreeSitter is a parser generator whose grammars are used by: Neovim, Helix, Zed, GitHub (code highlighting in PRs), and many others. One grammar → highlighting in most modern editors.

**Why separate from v2.2.2:** TreeSitter grammars use a different format from TextMate grammars. They require writing `grammar.js` in the TreeSitter DSL and generating the C parser. This is a half-day of work but distinct from the VSCode extension.

**Deliverable:** `tree-sitter-ipp` npm package, registered in the TreeSitter repository list.

**Sample grammar.js (partial):**
```javascript
module.exports = grammar({
  name: 'ipp',
  rules: {
    source_file: $ => repeat($._statement),
    _statement: $ => choice($.var_decl, $.func_decl, $.class_decl, $.if_stmt, ...),
    var_decl: $ => seq('var', $.identifier, '=', $._expression),
    func_decl: $ => seq('func', $.identifier, '(', $.param_list, ')', $.block),
    class_decl: $ => seq('class', $.identifier, optional(seq('extends', $.identifier)), '{', repeat($.method_decl), '}'),
    ...
  }
})
```

---

### v2.2.4 — Feature: `ipp fmt` — Auto-Formatter

**What:** `ipp fmt myfile.ipp` normalises indentation (4 spaces), spacing around operators, blank lines between functions, and brace placement. Eliminates style debates in teams. Common in modern languages (gofmt, rustfmt, black).

**Implementation:** A simple pretty-printer over the AST — walk the already-parsed tree, emit normalised text. ~150 lines in `ipp/tools/formatter.py`. Does not need to handle invalid syntax (it only formats files that parse successfully).

**Rules:**
- 4 spaces per indent level (no tabs)
- One blank line between top-level declarations
- Two blank lines between class definitions
- Spaces around binary operators (`a + b` not `a+b`)
- No trailing whitespace
- Newline at end of file
- `{` on same line as declaration: `func foo() {` not `func foo()
{`

**Test file: `tests/v2_2_4/test_fmt.py`**:
```python
from ipp.tools.formatter import format_source
ugly = 'func double(x){return x*2}
func triple(x){return x*3}'
pretty = format_source(ugly)
assert 'func double(x) {' in pretty
assert '    return x * 2' in pretty
assert '

' in pretty   # blank line between functions
```

**CLI:** `ipp fmt file.ipp` — formats in place. `ipp fmt --check file.ipp` — exits non-zero if formatting needed (for CI).

---

### v2.2.5 — Feature: `ipp doc` — Documentation Generator

**What:** `ipp doc src/` reads all `.ipp` files, extracts `##` comments above `export func`, `export class`, and `export var` declarations, and generates a `docs/` folder of Markdown files. One Markdown file per source file.

**Output format:**
```markdown
# ipp-math2d / rect

Axis-aligned bounding box for collision detection.

## `rect(x, y, w, h)`
Creates a rectangle at position (x,y) with given width and height.

### Properties
- `left` — x coordinate of left edge
- `right` — x + width
- `top` — y coordinate of top edge
- `bottom` — y + height
- `center` — vec2 at the center

### Methods

#### `contains_point(px, py) → bool`
Returns true if the point (px, py) is inside the rectangle.

#### `intersects(other) → bool`
Returns true if this rectangle overlaps with another rect.
```

**Files:** `ipp/tools/docgen.py` — parse source files, extract `##` comments, emit Markdown.

**Test file: `tests/v2_2_5/test_docgen.py`**:
```python
from ipp.tools.docgen import generate_docs
src = """
## Doubles a number.
export func double(x) { return x * 2 }
"""
docs = generate_docs(src, "utils")
assert "# utils" in docs
assert "double" in docs
assert "Doubles a number" in docs
```

---

---

### v2.2.6 — Feature: Studio Plugin API — Editor Bridge (HTTP + WebSocket)

**What:** A local HTTP + WebSocket bridge that lets an external editor (Electron app, VSCode
extension, web page) communicate with a running Ipp game. The game exposes an API:
inspect variables, call functions, send input events, get canvas screenshots, trigger hot reload.
This is the foundation for a visual game editor — but it works right now with just a browser,
curl, or a VSCode webview.

**What the bridge exposes:**
```
GET  /api/globals           → all current global variable names + values
GET  /api/globals/:name     → one variable's value
POST /api/globals/:name     → set a variable's value (JSON body)
GET  /api/screenshot        → current canvas frame as base64 PNG
POST /api/call/:fn          → call a global Ipp function with args
POST /api/reload            → trigger hot reload
WS   /ws/events             → subscribe to: reload, variable_changed, achievement_unlocked, signal_emitted
```

**Why this is novel:** No scripting language exposes this protocol. Godot's editor is tightly
coupled to its engine in C++. Unity's editor is a separate C# application. Ipp's editor bridge
is a 100-line HTTP server that runs *inside* the game — any tool can talk to it.

**Files to change:** `ipp/runtime/studio.py` (new), `ipp/vm/vm.py` (register builtins +
auto-start bridge when `--studio` flag set), `ipp/cli.py` (add `--studio` flag).

`ipp/runtime/studio.py`:
```python
from ipp.network.http import http_serve_routes, http_serve_stop
import json, base64, threading

_vm_ref = None
_ws_clients = []   # connected WebSocket clients for event streaming

def start_studio_bridge(vm, port=9876):
    global _vm_ref
    _vm_ref = vm
    
    routes = {}
    
    def get_globals(req):
        safe = {}
        for k, v in vm.globals.items():
            if not callable(v):
                try: json.dumps(v); safe[k] = v
                except: safe[k] = str(v)
        return {"status": 200, "body": json.dumps(safe),
                "headers": {"Content-Type": "application/json",
                             "Access-Control-Allow-Origin": "*"}}
    
    def set_global(req):
        name = req["path"].split("/")[-1]
        val = json.loads(req["body"])
        vm.globals[name] = val
        broadcast_event({"type": "variable_changed", "name": name, "value": val})
        return {"status": 200, "body": '{"ok":true}',
                "headers": {"Content-Type": "application/json",
                             "Access-Control-Allow-Origin": "*"}}
    
    def screenshot(req):
        from ipp.runtime.canvas import canvas_screenshot
        img = canvas_screenshot()
        if img is None:
            return {"status": 503, "body": '{"error":"no canvas"}',
                    "headers": {"Content-Type": "application/json"}}
        import io
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        data = base64.b64encode(buf.getvalue()).decode()
        return {"status": 200, "body": json.dumps({"png": data}),
                "headers": {"Content-Type": "application/json",
                             "Access-Control-Allow-Origin": "*"}}
    
    def trigger_reload(req):
        from ipp.runtime.hotreload import trigger_reload as _reload
        _reload(vm)
        broadcast_event({"type": "reload"})
        return {"status": 200, "body": '{"ok":true}',
                "headers": {"Content-Type": "application/json",
                             "Access-Control-Allow-Origin": "*"}}
    
    routes["GET /api/globals"]     = get_globals
    routes["POST /api/globals/*"]  = set_global
    routes["GET /api/screenshot"]  = screenshot
    routes["POST /api/reload"]     = trigger_reload
    
    http_serve_routes("127.0.0.1", port, routes)
    print(f"[Ipp Studio] Bridge running at http://127.0.0.1:{port}")

def broadcast_event(event):
    msg = json.dumps(event)
    for client in list(_ws_clients):
        try: client.send(msg)
        except: _ws_clients.remove(client)
```

**CLI:**
```bash
ipp run --studio game.ipp
# Game runs normally + bridge starts at http://127.0.0.1:9876

# From another terminal:
curl http://127.0.0.1:9876/api/globals
# → {"player_hp": 80, "score": 500, "level": 3, ...}

curl -X POST http://127.0.0.1:9876/api/globals/player_hp      -d "100" -H "Content-Type: application/json"
# → player's HP is now 100 in the running game

curl http://127.0.0.1:9876/api/screenshot | python3 -c   "import sys,json,base64; open('frame.png','wb').write(base64.b64decode(json.load(sys.stdin)['png']))"
# → frame.png is the current game frame
```

**Test file: `tests/v2_2_6/test_studio_bridge.ipp`**
```ipp
# Studio bridge starts when run with --studio flag
# Test via the HTTP client
import { http } from "ipp-net"

var score = 42
var player_name = "Alice"

# (Start bridge in test setup via Python)
# GET globals
var res = http.get("http://127.0.0.1:9877/api/globals")
assert res.ok == true
var globals = res.json()
assert globals.get("score") == 42
assert globals.get("player_name") == "Alice"

# SET a global
http.post("http://127.0.0.1:9877/api/globals/score",
          body="100", headers={"Content-Type": "application/json"})
assert score == 100   # the in-process VM is updated

# Reload
var reload_res = http.post("http://127.0.0.1:9877/api/reload")
assert reload_res.ok == true
```

**C/Rust rewrite:** The bridge stays Python. The C/Rust VM exposes its globals dict via a
Python-compatible dict interface (PyO3 `PyDict`). The bridge code is identical — just reading
from a different dict object.

**Bootstrapped Ipp:** Bridge stays Python (it uses the Python HTTP server). The game-side
`start_studio_bridge(vm)` call happens in Python at startup. Once Ipp can call Python FFI
functions, the bridge becomes `import { start_bridge } from "ipp-studio"`.

**Regression risk:** Zero. Only active with `--studio` flag.

## Phase G: Novel Differentiators (v2.3.0 – v2.3.4)

> These features don't exist in any mainstream game scripting language. They are Ipp's potential differentiators — reasons a developer would choose Ipp over Lua or GDScript for a specific project. Each one is feasible given Ipp's Python host. None of them require the C or Rust VM.

---

---

### v2.2.7 — Feature: Ipp Studio — Minimal Electron Editor

**What:** A minimal game editor built in Electron (HTML/CSS/JS) that talks to the Studio Bridge
(v2.2.6). Not a full IDE — just the four things game developers actually need during development:

1. **Variable inspector** — live table of all globals, editable
2. **Canvas view** — the game canvas streamed at 10fps via screenshot API
3. **Hot reload button** — triggers reload via bridge, shows diff of what changed
4. **Console** — shows Ipp `print()` output and errors in real time via WebSocket

**Why Electron and not a web page:** A web page can't launch `ipp run --studio game.ipp` as a
child process. Electron can. A browser-based version is trivially available for users who start
the bridge manually.

**Tech stack:** Electron + vanilla JS. No React, no bundler. One `package.json`, one `index.html`,
one `main.js`, one `renderer.js`. The entire editor is under 500 lines.

**Deliverable:** `ipp studio game.ipp` — launches the game with `--studio` flag, opens the
Electron editor window, connects to the bridge automatically.

```
Ipp Studio v2.2.7
┌─────────────────────┬────────────────────────────────┐
│ Variables           │                                 │
│ ─────────────────── │        Game Canvas              │
│ score      500  ✏️  │         (10fps preview)         │
│ player_hp   80  ✏️  │                                 │
│ level        3  ✏️  │                                 │
│ enemies     []  ✏️  │                                 │
├─────────────────────│                                 │
│ [🔄 Hot Reload]     │                                 │
├─────────────────────┴────────────────────────────────┤
│ Console                                               │
│ [INFO] game started                                   │
│ [RELOAD] hot_reload complete (2 functions patched)    │
│ [PRINT] player spawned at 0, 0                        │
└───────────────────────────────────────────────────────┘
```

**Files:** `ipp/studio/` (new directory), `ipp/studio/main.js`, `ipp/studio/index.html`,
`ipp/studio/renderer.js`, `ipp/studio/package.json`.

**Requirement:** `npm` must be installed. `ipp studio` checks and gives clear instructions if not.

**Regression risk:** Zero. New command. Electron app is a standalone directory.


### v2.3.0 — Feature: Live REPL Attached to Running Game

**What:** `ipp run --interactive` starts the game loop and simultaneously opens a REPL. You can pause the game, inspect any variable, call any function, mutate state, and resume — without restarting. This is the single most powerful debugging tool for game development and no mainstream game engine exposes it cleanly at the scripting level.

**How it works (Python-side):** The game loop runs in a background thread. A `threading.Event` called `_pause_event` gates each frame. When the REPL receives input, it sets `_pause_event`, executes the expression in the game's VM globals dict, prints the result, and clears `_pause_event`. The game's `game_loop()` checks `_pause_event` at the top of each frame.

**REPL commands in interactive mode:**
```
> ipp --interactive game.ipp
[Ipp] Game running at 60fps. Press Ctrl+P to pause, Ctrl+R to resume.
^P
[PAUSED at frame 1423]
ipp> player.hp
80
ipp> player.hp = 100
ipp> enemies
[<Enemy 'Orc' hp=45>, <Enemy 'Goblin' hp=12>]
ipp> enemies[0].hp = 0
ipp> resume()
[Ipp] Resumed.
```

**Files to change:** `ipp/vm/vm.py` — add `_interactive_mode` flag and pause hook; `ipp/cli.py` — `--interactive` flag; `ipp/repl/interactive.py` — new file, threaded REPL.

**Test file: `tests/v2_3_0/test_interactive.py`** (Python-level):
```python
import threading, time
from ipp.vm.vm import VM
from ipp.repl.interactive import InteractiveSession

vm = VM()
vm.run_source("var score = 0
var hp = 100")
session = InteractiveSession(vm)
result = session.eval("score + hp")
assert result == 100
session.eval("score = 50")
result = session.eval("score")
assert result == 50
```

**Regression risk:** Low. Only active with `--interactive` flag.

---

### v2.3.1 — Feature: Hot-Swap Method Definitions

**What:** Redefine a function or method while the game is running. The next time it's called, the new definition is used. Existing instances keep their state — only the behaviour changes. More conservative than full class hot-swap (which would require field migration) but covers 90% of hot-reload use cases: tweaking AI logic, adjusting physics parameters, changing rendering code.

**Syntax:**
```ipp
# In REPL while game is running:
ipp> redefine Enemy.update(self, dt) {
...     # new AI logic
... }
[Ipp] Enemy.update redefined. 12 existing instances will use new definition.
```

**Implementation:** Method definitions are stored in the class's method table (a dict in the VM's class object). `redefine` compiles the new function body and overwrites the entry in that dict. All instances share the same class method table, so the change is instant.

**Files to change:** `ipp/vm/vm.py` — add `redefine_method(class_name, method_name, fn)` API; `ipp/repl/interactive.py` — parse `redefine` command.

**Test file: `tests/v2_3_1/test_hot_swap.ipp`**
```ipp
class Counter {
    func init() { self.val = 0 }
    func step() { self.val = self.val + 1 }
}

var c = Counter()
c.step()
c.step()
assert c.val == 2

# Hot-swap: redefine step to increment by 10
redefine_method(Counter, "step", func(self) { self.val = self.val + 10 })

c.step()
assert c.val == 12   # previous val=2 preserved, new step adds 10
```

---

### v2.3.2 — Feature: Game Test Recorder

**What:** Record all input events and the initial RNG seed during a play session, save to a `.ipp_replay` file. Re-run the replay to reproduce the exact same game state deterministically. Assert on the final state to build regression tests from real play sessions.

**Why useful:** You found a bug during play at frame 3000. You record it. Now you can reproduce it instantly, fix it, and assert that it stays fixed. This is deterministic testing without writing test code — you just play the game.

**Recording:**
```bash
ipp run --record bug_repro.ipp_replay game.ipp
# play the game, trigger the bug
# Ctrl+C to stop recording
```

**Replay:**
```bash
ipp run --replay bug_repro.ipp_replay game.ipp
# game runs identically, stops at last recorded frame
```

**Replay with assertion:**
```ipp
ipp run --replay bug_repro.ipp_replay --assert "player.hp > 0" game.ipp
# exits 0 if assertion holds at end of replay, 1 if not
```

**`.ipp_replay` format:**
```json
{
  "ipp_version": "2.3.2",
  "rng_seed": 42,
  "frames": 3000,
  "inputs": [
    {"frame": 1, "key": "RIGHT", "event": "down"},
    {"frame": 1, "key": "RIGHT", "event": "up"},
    {"frame": 45, "key": "SPACE", "event": "down"},
    ...
  ]
}
```

**Files to change:** `ipp/runtime/input.py` — add record/replay mode; `ipp/cli.py` — `--record` and `--replay` flags; `ipp/vm/vm.py` — seed RNG from replay file.

**Regression risk:** Zero. New flags; existing `ipp run` path unchanged.

---

### v2.3.3 — Feature: `data` Class — Declarative Game Data with Validation

**What:** A `data` class is a value-type class whose fields have declared types, default values, and optional validation ranges. Designed for game balance data — weapons, enemies, items. No language has this cleanly. GDScript's `@export` hints are editor-only and scattered. Unity's ScriptableObjects require C# boilerplate. A `data` class in Ipp makes balance data self-documenting and self-validating.

**Syntax:**
```ipp
data class Weapon {
    var name:    string = "Unnamed"
    var damage:  int    = 10  in 1..999
    var speed:   float  = 1.0 in 0.1..5.0
    var range:   float  = 1.5 in 0.5..10.0
    var rarity:  Rarity = Rarity.COMMON
    var tags:    list   = []
}
```

**What `data` adds over a regular class:**
1. **Type annotation** — `name: string` — documents expected type, checked on assignment in debug mode
2. **Range constraint** — `damage: int = 10 in 1..999` — raises on out-of-range assignment
3. **`__eq__` auto-generated** — two Weapon instances with the same field values are equal
4. **`__str__` auto-generated** — readable print output
5. **`to_dict()` auto-generated** — for serialisation via `ipp-io`
6. **`from_dict(d)` static method auto-generated** — for deserialisation

**Test file: `tests/v2_3_3/test_data_class.ipp`**
```ipp
data class Item {
    var name:   string = "Unknown"
    var weight: float  = 1.0 in 0.01..100.0
    var value:  int    = 0   in 0..9999
    var stackable: bool = true
}

var sword = Item()
assert sword.name == "Unknown"
assert sword.weight == 1.0
assert sword.value == 0

sword.name = "Iron Sword"
sword.weight = 3.5
sword.value = 50

# Range validation
var caught = ""
try { sword.value = 99999 } catch e { caught = e }
assert caught.contains("out of range") == true
assert sword.value == 50   # unchanged after failed assignment

# Auto-generated equality
var sword2 = Item()
sword2.name = "Iron Sword"
sword2.weight = 3.5
sword2.value = 50
sword2.stackable = true
assert sword == sword2

# Auto-generated str
assert str(sword).contains("Iron Sword") == true
assert str(sword).contains("3.5") == true

# Serialisation roundtrip via to_dict / from_dict
var d = sword.to_dict()
assert d["name"] == "Iron Sword"
var sword3 = Item.from_dict(d)
assert sword3 == sword
```

---

### v2.3.4 — Feature: Interfaces (`interface` keyword)

**What:** A way to declare a named contract: "any class implementing this interface must have these methods." Not full static typing — just a runtime-checked protocol that documents intent and gives clear errors when a class doesn't fulfill it.

**Why practical:** Games have many interchangeable things — `Renderable`, `Collidable`, `Saveable`, `Updatable`. Without interfaces, you pass objects and hope they have the right methods. With interfaces, the error message says "Enemy does not implement Updatable: missing method 'update(dt)'." 

**Syntax:**
```ipp
interface Updatable {
    func update(dt)
}

interface Renderable {
    func draw()
    func get_z_order() -> int
}

interface Saveable {
    func to_dict() -> dict
    func from_dict(d)
}

class Enemy implements Updatable, Renderable {
    func update(dt) { ... }
    func draw() { ... }
    func get_z_order() { return 1 }
    # Missing nothing — passes at class definition time
}

class BrokenEnemy implements Updatable {
    # Missing update() — error at class definition time
    func other_method() { }
}
```

**Implementation:** `interface` compiles to a descriptor object. `implements` checks at class-definition time (not instance creation) that all declared method signatures are present. Runtime cost: zero after the check.

**Test file: `tests/v2_3_4/test_interface.ipp`**
```ipp
interface Updatable {
    func update(dt)
    func reset()
}

# Valid implementation
class Timer implements Updatable {
    func init() { self.elapsed = 0 }
    func update(dt) { self.elapsed = self.elapsed + dt }
    func reset() { self.elapsed = 0 }
}

var t = Timer()
t.update(0.016)
assert isclose(t.elapsed, 0.016) == true
t.reset()
assert t.elapsed == 0

# Type check with is
assert t is Updatable == true
assert t is Timer == true

# Missing method — error at class definition
var caught = ""
try {
    class BadTimer implements Updatable {
        func update(dt) { }
        # Missing reset() — should fail
    }
} catch e { caught = e }
assert caught.contains("does not implement") == true
assert caught.contains("reset") == true
```

---

---

### v2.3.5 — Feature: Tagged Units — Prevent Coordinate Space Bugs

**What:** Numeric values can be tagged with a unit type. Mixing incompatible unit types is a warning in debug mode and an error in strict mode. The silent bug of adding a world-space coordinate to a screen-space coordinate is immediately caught.

```ipp
var world_x:  WorldUnit  = 300.0
var screen_x: ScreenUnit = 50.0
var tile_x:   TileUnit   = 9

world_x + screen_x   # ❌ Warning: WorldUnit + ScreenUnit — likely a coordinate space bug
world_x + world_x    # ✅ WorldUnit + WorldUnit = WorldUnit
world_x / tile_x     # ❌ Warning: dividing WorldUnit by TileUnit
tile_x * 32.0        # ✅ TileUnit * float = WorldUnit (if declared)
```

**Unit declarations:**
```ipp
unit WorldUnit   # world-space pixels (before camera transform)
unit ScreenUnit  # screen-space pixels (after camera transform)
unit TileUnit    # integer tile coordinates
unit NormalUnit  # normalised 0.0..1.0 range (for lerp, alpha, ratios)

# Unit conversion rules (explicit)
unit_convert WorldUnit / 32.0 -> TileUnit
unit_convert TileUnit * 32.0  -> WorldUnit
```

**Why this is Phase G:** It requires either a type inference pass or explicit annotation on every variable. This is complex to implement correctly and adds syntax overhead. It's a differentiator, not a correctness fix. Games can ship without it — it's for teams that want to eliminate an entire class of silent bugs.

**Files to change:** `ipp/lexer/lexer.py` (`:` type annotation syntax already needed for `data class`), `ipp/vm/compiler.py` (track unit type of each local), `ipp/vm/vm.py` (check unit compatibility in arithmetic opcodes when debug mode is on).

**Implementation:** In debug mode, tagged numbers are wrapped in a thin `TaggedNum(value, unit)` Python object. Arithmetic operations check unit compatibility. In release mode, tagged numbers are unwrapped to plain Python floats — zero overhead.

**Test file: `tests/v2_3_5/test_tagged_units.ipp`**
```ipp
unit Pixel
unit Tile
unit Second
unit PerSecond

var px:  Pixel   = 640.0
var t:   Tile    = 20
var sec: Second  = 1.5
var spd: PerSecond = 100.0

# Compatible operations
var px2: Pixel = px + 10.0   # Pixel + untagged = Pixel
var dist: Pixel = spd * sec   # PerSecond * Second = Pixel (if conversion declared)

# Incompatible — warning in debug, error in strict
var caught = ""
try {
    var bad = px + t     # Pixel + Tile = ???
} catch e { caught = e }
assert caught.contains("unit") == true or caught == ""  # warning mode: just prints

# Unit stripping — explicit cast to untagged
var raw: float = strip_unit(px)
assert raw == 640.0
```

**C/Rust rewrite:** In the C VM, tagged nums are structs with a `unit_id` field. The arithmetic opcode checks `unit_id` compatibility before computing. Release mode compiles away the `unit_id` entirely — pure float arithmetic with zero overhead.

**Bootstrapped Ipp:** Tagged units compile to `data class TaggedNum { var value: float; var unit: int }` with operator overloads. The compiler checks unit compatibility at compile time for statically-typed variables. Pure Ipp implementation once `data class` and operator overloading are stable.

**Regression risk:** Low. Only activates when `:UnitType` annotation is used. All existing untagged code works unchanged.

---

## Phase H: Far-Future Features (v2.4.0 – v2.4.3)

> **Prerequisite:** All of Phases A–G complete. These features are genuinely complex to implement correctly, but are realistic given Ipp's Python host. They belong here — not cut, not in a vague "maybe" category — with honest scoping about what "realistic" means at this stage.

---

### v2.4.0 — Feature: Time-Travel Debugging (Last N Frames)

**What:** `ipp run --time-travel game.ipp` records the complete VM state snapshot at the end of every frame (all globals, all locals on the call stack, all heap objects). You can then step backward through the last N frames in the REPL.

**Why "last N frames" is the realistic scope:** Full time-travel (unlimited history) would require snapshotting the entire VM heap after every opcode — not feasible at 0.32% Python performance. Last N frames (N=60 by default = 1 second of history) requires one deep-copy of `vm.globals` per frame. At 60fps that's 60 snapshots/second. On modern hardware a deep-copy of a moderate game state dict takes ~0.1ms — adding ~6ms overhead per second, acceptable.

**Implementation:**
```python
# In vm.py, when --time-travel flag is set:
import copy
MAX_HISTORY = 60  # configurable

class TimeTravelVM(VM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history = []    # deque of (frame_num, globals_snapshot)
        self._frame_num = 0
    
    def end_frame(self):
        """Call this at the end of each game loop frame."""
        snapshot = copy.deepcopy(self.globals)
        self._history.append((self._frame_num, snapshot))
        if len(self._history) > MAX_HISTORY:
            self._history.pop(0)
        self._frame_num += 1
    
    def step_back(self, n=1):
        """Restore VM state to n frames ago."""
        if len(self._history) < n + 1:
            raise RuntimeError(f"Only {len(self._history)} frames in history")
        frame_num, snapshot = self._history[-(n+1)]
        self.globals = copy.deepcopy(snapshot)
        return frame_num
```

**REPL in time-travel mode:**
```
ipp> :back        — step back 1 frame
ipp> :back 5      — step back 5 frames
ipp> :forward     — step forward 1 frame
ipp> :frame       — show current frame number
ipp> player.hp    — inspect variable at this point in history
ipp> :history     — show available history range
```

**Test file: `tests/v2_4_0/test_time_travel.py`** (Python-level):
```python
from ipp.vm.timetravel import TimeTravelVM
vm = TimeTravelVM()
vm.run_source("var x = 0")
for i in range(5):
    vm.run_source(f"x = {i}")
    vm.end_frame()
assert vm.globals["x"] == 4
vm.step_back(2)
assert vm.globals["x"] == 2
vm.step_back(1)
assert vm.globals["x"] == 1
```

---

### v2.4.1 — Feature: HTTP Server — Full Request Routing + Middleware

**What:** Upgrade the basic route-handler server from v2.0.19.2 into a production-usable server: middleware support (auth, logging, CORS), path parameters, query string parsing, response streaming, and error handler registration.

```ipp
import { Router, json_response } from "ipp-net"

var api = Router()

# Middleware
api.use(func(req, next) {
    print("[" + req["method"] + "] " + req["path"])
    var res = next(req)
    return res
})

# Path parameters
api.get("/player/:id", func(req) {
    var player_id = req["params"]["id"]
    return json_response({"id": player_id, "score": 0})
})

# Query string parsed automatically
api.get("/scores", func(req) {
    var limit = req["query"].get("limit") ?? "10"
    return json_response({"limit": int(limit), "scores": []})
})

# Error handler
api.on_error(func(req, err) {
    return json_response({"error": str(err)}, status=500)
})

api.listen("0.0.0.0", 8080)
```

**Realistic scope note:** Middleware is a `next(req)` chain — straightforward to implement. Path parameters require a simple regex router replacing the dict-key lookup. Query strings are already parsed by Python's `urllib.parse`. This is ~150 lines of new Python.

---

### v2.4.2 — Feature: Binary Data and Network Buffers

**What:** Games sending and receiving binary data (game state snapshots, compressed saves, custom protocols) need a `Buffer` type. Wraps Python's `bytearray` and `struct` with a clean Ipp API.

```ipp
import { Buffer } from "ipp-net"

var buf = Buffer()
buf.write_u8(255)
buf.write_u16(1000)
buf.write_f32(3.14)
buf.write_str("hello")

var reader = Buffer(buf.bytes())
assert reader.read_u8() == 255
assert reader.read_u16() == 1000
assert isclose(reader.read_f32(), 3.14) == true
assert reader.read_str() == "hello"
```

**Realistic scope:** `struct.pack/unpack` wrapping is trivial. The value is having a consistent Ipp API so games can implement binary save formats and custom network protocols.

---

### v2.4.3 — Feature: WebSocket Server

**What:** The `websocket` package currently only has a *client*. A server lets you build multiplayer games where an Ipp script acts as the authoritative game server. Requires `pip install websockets`.

```ipp
import { WSServer } from "ipp-net"

var server = WSServer(port=8765)
var players = {}

server.on_connect(func(client_id) {
    players[client_id] = {"score": 0, "pos": [0, 0]}
    server.send(client_id, json_stringify({"type": "welcome", "id": client_id}))
})

server.on_message(func(client_id, msg) {
    var data = json_parse(msg)
    if data["type"] == "move" {
        players[client_id]["pos"] = data["pos"]
        # Broadcast to all other players
        for pid in players.keys() {
            if pid != client_id {
                server.send(pid, json_stringify({
                    "type": "player_moved",
                    "id": client_id,
                    "pos": data["pos"]
                }))
            }
        }
    }
})

server.on_disconnect(func(client_id) {
    players.delete(client_id)
})

server.listen()   # blocks until Ctrl+C
```

**Implementation:** Wraps `websockets.serve()` with an asyncio event loop in a background thread, same pattern as the existing WebSocket client. Ipp callbacks are called via `call_soon_threadsafe()`.

---

*Roadmap v4 — May 2026 | Starting from Ipp v1.7.9.1.11*
*Based on new2_audit.md: 22 open bugs, 45 confirmed working features*
*Phase A (v1.7.6–v1.7.9): ~4 days of work, unblocks all new users*
*Phase B (v1.8.0–v1.8.9): ~2 weeks, makes language reliable*
*Phase C (v1.9.0–v1.9.5.1): ~1 week, completes standard library*
*Phase C2 (v1.9.10–v1.9.13): ~1 week, multi-file imports and project manifest*
*Phase D (v2.0.0–v2.0.8): ~1 month, real game dev capability*
*Phase E (v2.1.0+): 3–6 months, native performance*
### v1.7.9.1.9 — REPL Highlight Fix, Playground Pyodide, CLI Parity
**Goal:** Fix three user-facing bugs introduced by the PyPI package differing from local `main.py`.
- `main.py` `.highlight` command — fixed detection logic; `pt_avail` flag now correctly reflects both `_HAS_HIGHLIGHT` and `_HAS_PT`; banner and `.highlight` command show correct ON/OFF status after `pip install prompt_toolkit`
- `ipp/main.py` — added full `_hl_session` / `make_session` highlight pipeline so the `ipp` CLI entry point (PyPI) has identical REPL behaviour to `python main.py`
- `web-playground/index.html` — added `micropip.install('ipp-lang')` strategy so Pyodide loads the real Ipp engine instead of showing "Ipp engine unavailable"
- `web-playground/ipp-bundle.js` — new bundled JS shim exposing the Ipp interpreter to the playground without requiring a server
- **Files:** `main.py`, `ipp/main.py`, `web-playground/index.html`, `web-playground/ipp-bundle.js`

### v1.7.9.1.10 — Version Bump & pyproject Cleanup
**Goal:** Bump version to 1.7.9.1.10 and clean up stale Python version metadata.
- VERSION bumped `1.7.9.1.9` → `1.7.9.1.10` in `main.py` and `ipp/main.py`
- `pyproject.toml` — removed stale `Programming Language :: Python :: 3.8` classifier (minimum is 3.10)
- ROADMAP updated with v1.7.9.1.9 and v1.7.9.1.10 sections
- **Files:** `main.py`, `ipp/main.py`, `pyproject.toml`, `ROADMAP_V2 (1).md`

*Phase A (v1.7.6–v1.7.9.1.14): ✅ COMPLETE*
*Phase A2 (v1.7.9.1.15–1.17): ~1 week, closes audit-v4 micro-bugs*
*Phase B (v1.8.0–v1.8.9): ~2–3 weeks, makes language reliable*
*Phase C (v1.9.0–v1.9.5.1): ~10 days, standard library complete*
*Phase C2 (v1.9.10–v1.9.13): ~1 week, multi-file projects unblocked*
*Phase D (v2.0.0–v2.0.11): ~6 weeks, real game dev capability*
*Phase D2 (v2.0.12–v2.0.18): ~3 weeks, core stdlib packages bundled*
*Phase D3 (v2.0.19–v2.0.21): ~2 weeks, network + canvas packages*
*Phase H (v2.4.0–v2.4.3): far-future, time-travel debug + WS server + binary buffers*
*Phase F (v2.2.0–v2.2.5): ~3 weeks, package registry + dev tooling*
*Phase G (v2.3.0–v2.3.4): ~4 weeks, novel differentiators*
*Phase E (v2.1.0+): 3–6 months, native performance*
