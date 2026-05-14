# Ipp Language Roadmap v3
> **Current version:** `1.7.5`
> **Based on:** `new2_audit.md` — 22 confirmed open bugs, 45 confirmed working features
> **Start here:** Versions v1.7.6 onward. Everything before v1.7.5 is done or acknowledged.

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

The current baseline is approximately **58 pass / 82 fail** out of 140 tests. Every version must improve or hold this number.

---

## IMMEDIATE ACTION — Version String Fix (Do This Right Now)

Before writing any code for any version below, fix the version string mismatch. This takes 2 minutes.

```python
# In main.py, line ~70:
VERSION = "1.7.5"   # was "1.6.12"

# In ipp/main.py, line ~76:
VERSION = "1.7.5"   # was "1.6.12"
```

```toml
# In pyproject.toml:
version = "1.7.5"   # was "2.0.0"
```

This must be done before any release is tagged. The mismatch (`pyproject.toml` says `2.0.0`, runtime says `1.6.12`) means pip installs produce a version that doesn't match what the running interpreter reports.

---

## Phase A: Critical Crash Fixes (v1.7.6 – v1.7.9)

These four bugs crash programs that any new user will write within their first 10 minutes. They are the highest-priority fixes in the entire language. Each can be fixed in an afternoon.

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

### v1.8.0 — Fix: `str.replace()` and String Method Naming (BUG-005, BUG-011)

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

### v1.8.0.1 — Fix: `str.format()` Named Placeholders Work

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

### v1.8.0.2 — Fix: `str.count()`, `str.rfind()`, `str.rindex()` Methods Added

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

### v1.8.0.3 — Enhancement: `str * n` Repetition Operator

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

### v1.8.1 — Fix: Variadic `...args` Packs a List, Not a Count (BUG-007)

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

### v1.8.1.1 — Enhancement: `list.extend()` and `list.insert()` Methods

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

### v1.8.1.2 — Enhancement: `list.any()`, `list.all()`, `list.min()`, `list.max()`

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

### v1.8.2 — Fix: `var a, b = 1, 2` Literal Multi-Assign (BUG-006)

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

### v1.8.3 — Fix: `list.map()`, `list.filter()`, `list.reduce()` (BUG-008)

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

### v1.8.4 — Fix: `len(IppSet)` Works (BUG-013)

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

### v1.8.5 — Fix: `vec4 + vec4` Arithmetic Wired to Operators (BUG-014)

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

### v1.8.6 — Fix: Spread `[0, ...a, 4]` — Items After Spread (BUG-015)

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

### v1.8.7 — Fix: `prop` Getter Body Parses Correctly (BUG-009)

**Root cause:** The `prop` keyword's parser expects `{ get { ... } }` but fails when the getter body contains a `return` statement. The error `Expect '}' after getter` suggests the parser finds `return` where it expects `}`.

**File to change:** `ipp/parser/parser.py`, the property declaration parser.

**Find the property parser and fix it to correctly parse a block body for the getter and setter:**
```python
def property_declaration(self):
    name = self.consume(IDENTIFIER, "Expect property name")
    self.consume(LEFT_BRACE, "Expect '{' before property body")
    getter = None
    setter = None
    while not self.check(RIGHT_BRACE):
        if self.match_keyword('get'):
            self.consume(LEFT_BRACE, "Expect '{' after 'get'")
            getter = self.block()   # parse full block with statements
        elif self.match_keyword('set'):
            # parse optional parameter name
            self.consume(LEFT_PAREN, "Expect '(' after 'set'")
            param = self.consume(IDENTIFIER, "Expect setter param name").lexeme
            self.consume(RIGHT_PAREN, "Expect ')'")
            self.consume(LEFT_BRACE, "Expect '{' after setter params")
            setter = (param, self.block())
    self.consume(RIGHT_BRACE, "Expect '}' after property body")
    return PropertyDecl(name.lexeme, getter, setter)
```

The key: `self.block()` must call the full statement-parsing block (the same one used by if/while/func bodies), not just expect a single expression or a single `}`.

**Test file: `tests/v1_8_7/test_property.ipp`**
```ipp
class Health {
    func init(max_hp) {
        self._hp = max_hp
        self._max = max_hp
    }
    prop hp {
        get {
            return self._hp
        }
        set(v) {
            if v < 0 { v = 0 }
            if v > self._max { v = self._max }
            self._hp = v
        }
    }
    prop is_alive {
        get {
            return self._hp > 0
        }
    }
}

var h = Health(100)
assert h.hp == 100
assert h.is_alive == true

h.hp = 50
assert h.hp == 50

h.hp = -10
assert h.hp == 0
assert h.is_alive == false

h.hp = 999
assert h.hp == 100
```

---

### v1.8.8 — Fix: `is` Operator Works in All Expression Positions (BUG-010)

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

## Phase C: Standard Library Completeness (v1.9.0 – v1.9.5)

After Phase B, the core language is reliable. Phase C rounds out the standard library.

---

### v1.9.0 — Feature: `list[a..b]` Slice Syntax Fixed (BUG-018)

**Root cause:** The `[a..b]` range is being evaluated to a list object `[a, a+1, ...]` and then passed as the index. The VM's index handler receives a list where it expects an int and fails.

**Fix in `vm.py` GET_INDEX handler:**
```python
elif opcode == OpCode.GET_INDEX:
    index = self.stack.pop()
    obj = self.stack.pop()
    if isinstance(index, IppRange):    # or whatever type [a..b] creates
        self.stack.append(obj[index.start:index.end])
    elif isinstance(index, list):
        self.stack.append(obj[index[0]:index[-1]+1])
    else:
        self.stack.append(obj[index])
```

**Test file: `tests/v1_9_0/test_slice_syntax.ipp`**
```ipp
var lst = [0, 1, 2, 3, 4, 5]

assert lst[1..4] == [1, 2, 3]
assert lst[0..3] == [0, 1, 2]
assert lst[3..6] == [3, 4, 5]

# String slicing
var s = "hello world"
assert s[0..5] == "hello"
assert s[6..11] == "world"

# slice() function still works too
assert slice(lst, 1, 4) == [1, 2, 3]
```

---

### v1.9.1 — Feature: `global` Keyword for Explicit Global Writes

Currently functions can READ globals but writing to a global from inside a function creates a local instead. Add a `global x` declaration:

```ipp
var score = 0
func add_score(n) {
    global score
    score = score + n
}
add_score(10)
add_score(5)
assert score == 15
```

---

### v1.9.2 — Feature: `map()` and `filter()` as Global Builtins (BUG-020)

```ipp
var doubled = map(func(x) { return x * 2 }, [1, 2, 3])
assert doubled == [2, 4, 6]

var evens = filter(func(x) { return x % 2 == 0 }, [1,2,3,4,5])
assert evens == [2, 4]

var total = reduce(func(acc, x) { return acc + x }, [1,2,3,4,5], 0)
assert total == 15
```

---

### v1.9.3 — Feature: Multi-line Strings `"""..."""`

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

---

### v1.9.4 — Feature: Async Return Value Fixed (BUG-016)

`async_run(f())` currently returns `nil`. Fix the coroutine execution to capture and return the function's return value.

```ipp
async func double_async(x) {
    return x * 2
}
var result = async_run(double_async(21))
assert result == 42
```

---

### v1.9.5 — Feature: Set Operations (`union`, `intersect`, `difference`)

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

## Phase D: Game Dev Features (v2.0.0 – v2.0.8)

After Phase C the language is feature-complete for general scripting. Phase D adds game-specific features that make Ipp viable for actual games.


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

## Documentation Fix Checklist

These are zero-code changes that unblock new users immediately. Do them alongside Phase A:

| Doc | Problem | Fix |
|-----|---------|-----|
| `README.md` | Shows `class Cat extends Animal` (broken in v1.7.5 — fixed in v1.7.7) | Add note: "Use `:` syntax until v1.7.7, or update to v1.7.7+" |
| `README.md` | Shows `func method(self, x)` (broken in v1.7.5 — fixed in v1.7.8) | Add note: "Use no explicit `self` until v1.7.8, or update to v1.7.8+" |
| `README.md` | Shows `lst.push(x)` | Change to `lst.append(x)` |
| `README.md` | Shows `lst.len()` | Change to `len(lst)` |
| `TUTORIAL.md` | Shows `case x:` in match | Change to `case x =>` |
| `TUTORIAL.md` | Shows `func method(self, ...)` | Update to no-self style until v1.7.8 |
| `REPL_TUTORIAL.md` | All OOP examples use `extends` | Add `# use : syntax for now` comment |
| All docs | Examples use `;` as separator | Remove semicolons (or note they work from v1.7.6+) |

---

## Version History Summary

| Version | Status | Description |
|---------|--------|-------------|
| v1.7.5 | **CURRENT** | Latest released version. Update main.py VERSION = "1.7.5" |
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
| v1.8.6 | Planned | Spread `[0,...a,4]` (BUG-015) |
| v1.8.7 | Planned | `prop get { }` body (BUG-009) |
| v1.8.8 | Planned | `is` operator everywhere (BUG-010) |
| v1.8.9 | Planned | Typed exception field access (BUG-017) |
| v1.9.0 | Planned | `list[a..b]` syntax (BUG-018) |
| v1.9.1 | Planned | `global` keyword |
| v1.9.2 | Planned | `map/filter/reduce` global builtins |
| v1.9.3 | Planned | Multi-line strings `"""` |
| v1.9.4 | Planned | Async return value |
| v1.9.5 | Planned | Set operations |
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

---

*Roadmap v3 — May 2026 | Starting from Ipp v1.7.5*
*Based on new2_audit.md: 22 open bugs, 45 confirmed working features*
*Phase A (v1.7.6–v1.7.9): ~4 days of work, unblocks all new users*
*Phase B (v1.8.0–v1.8.9): ~2 weeks, makes language reliable*
*Phase C (v1.9.0–v1.9.5): ~1 week, completes standard library*
*Phase D (v2.0.0–v2.0.8): ~1 month, real game dev capability*
*Phase E (v2.1.0+): 3–6 months, native performance*
*Phase F (v1.7.9.1.x): UX & game-dev QoL — keyboard, REPL polish, web playground, docs*
