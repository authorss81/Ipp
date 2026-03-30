# v1.3.2 Bug Fix Release - CRITICAL ISSUES

## Release: https://github.com/authorss81/Ipp/releases/tag/v1.3.2-bugfix

## ⚠️ URGENT: Multiple Features Incomplete

The following features from v1.3.2 requirements are **partially implemented** and need to be completed:

---

## 1. BUG-N1: Private Member Name Mangling

### Status: PARTIAL (interpreter only)

**What's implemented (interpreter):**
- `_is_private()` checks for names starting with `__`
- `_is_internal_access()` tracks `current_class`
- `IppInstance.get()` and `IppInstance.set()` block external access to private fields

**What's MISSING (VM):**
- The VM's `IppInstance` class does NOT have private field protection
- The VM is the default execution path in `main.py`

### Fix Required:
Add private field protection to `ipp/vm/vm.py`:
```python
class IppInstance:
    def get(self, name: str) -> Any:
        if name in self.fields:
            # TODO: Add private field check here
            return self.fields[name]
        # ... rest of method
    
    def set(self, name: str, value: Any):
        # TODO: Add private field check here
        self.fields[name] = value
```

### Test Case:
```ipp
class Bank {
    func init(balance) {
        self.balance = balance      # public
        self.__pin = 1234           # private
    }
    
    func getBalance() {
        return self.balance         # OK - internal access
    }
    
    func getPin() {
        return self.__pin           # OK - internal access
    }
}

var account = Bank(1000)
print(account.balance)      # Should work - public
print(account.getBalance()) # Should work - method access
# print(account.__pin)      # Should ERROR - external access to private
```

---

## 2. BUG-N2: Recursion Limit

### Status: PARTIAL (interpreter only)

**What's implemented:**
- `call_depth` tracking in `Interpreter`
- `max_depth` attribute (default ~1000)
- Error raised when depth exceeded

**What's MISSING (VM):**
- VM does NOT track recursion depth
- Infinite recursion in VM will crash Python

### Fix Required:
Add recursion tracking to `ipp/vm/vm.py`:
```python
class VM:
    def __init__(self, ...):
        # ... existing init
        self.call_depth = 0
        self.max_depth = 1000
    
    # In _call_method:
    def _call_method(self, ...):
        self.call_depth += 1
        if self.call_depth > self.max_depth:
            self.call_depth -= 1
            raise VMError(f"Maximum recursion depth ({self.max_depth}) exceeded")
        try:
            # ... existing code
        finally:
            self.call_depth -= 1
```

### Test Case:
```ipp
func fib(n) {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

print(fib(10))  # Should work
# fib(1000)     # Should error with recursion limit
```

---

## 3. BUG-N6: __str__ Method

### Status: PARTIAL (incomplete)

**What's implemented:**
- `IppInstance.__str__()` in interpreter.py calls the method
- `IppInstance.__str__()` in vm.py partially implemented

**What's MISSING:**
- VM's `_call_ipp_method()` helper is incomplete
- print() does NOT call __str__ on user classes

### Fix Required:
Complete the `__str__` implementation in `ipp/vm/vm.py`:
```python
class IppInstance:
    def __str__(self):
        str_method = self.cls.get_method('__str__')
        if str_method:
            return _call_ipp_method(self, str_method)
        return f"<{self.cls.name} instance>"
```

### Test Case:
```ipp
class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    
    func __str__() {
        return "(" + self.x + ", " + self.y + ")"
    }
}

var a = Vec2(1, 2)
print(a)  # Should print "(1, 2)"
```

---

## 4. v1.1.0 Test Bug: Operator Overloading / Class Methods

### Status: BROKEN

**Problem:**
Class instantiation is completely broken. This affects ALL class features including operator overloading.

### Bug #1: compile_set Emits Wrong Bytecode

**File:** `ipp/vm/compiler.py`, lines 856-860

**Current (broken):**
```python
def compile_set(self, node: SetExpr):
    self.compile_expr(node.object)     # Push self
    self.compile_expr(node.value)     # Push x
    self.chunk.write(OpCode.DUP)      # Duplicate x - WRONG!
    self.compile_set_property(node.name)  # SET_PROPERTY pops x, keeps self
```

**Fixed (Option A - recommended):**
```python
def compile_set(self, node: SetExpr):
    self.compile_expr(node.object)
    self.compile_expr(node.value)
    self.compile_set_property(node.name)
    self.chunk.write(OpCode.POP)  # Remove the value from stack
```

**OR Option B - Fix the VM:**
```python
elif opcode == OpCode.SET_PROPERTY:
    idx = code[ip + 1]
    name = constants[idx]
    value = self.stack.pop()
    obj = self.stack.pop()  # Pop object, not peek
    if isinstance(obj, IppInstance):
        obj.set(name, value)
    # Don't push anything - property assignment returns nil
```

### Test Case:
```ipp
class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    
    func __add__(other) {
        return Vec2(self.x + other.x, self.y + other.y)
    }
}

var a = Vec2(1, 2)
var b = Vec2(3, 4)
var c = a + b  # Should create Vec2(4, 6)
print(c.x)     # Should print 4
```

---

## Test File to Create

Create `tests/v1_3_2/test_features.ipp`:
```ipp
# BUG-N1: Private member test
class Bank {
    func init(balance) {
        self.balance = balance
        self.__secret = "hidden"
    }
    func getSecret() {
        return self.__secret
    }
}
var b = Bank(100)
# print(b.__secret)  # Should error

# BUG-N2: Recursion limit test
func recursive(n) {
    if n <= 0 { return 0 }
    return recursive(n - 1)
}
# recursive(1000)  # Should error

# BUG-N6: __str__ test
class Point {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __str__() {
        return "(" + self.x + ", " + self.y + ")"
    }
}
var p = Point(1, 2)
# print(p)  # Should print "(1, 2)"

# v1.1.0: Operator overloading test
class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
    func __add__(other) {
        return Vec2(self.x + other.x, self.y + other.y)
    }
}
var a = Vec2(1, 2)
var b = Vec2(3, 4)
var c = a + b
# print(c.x)  # Should print 4

print("All tests would pass if bugs were fixed!")
```

---

## Priority Order to Fix

1. **FIRST: v1.1.0 class instantiation bug** - Everything depends on this working
2. **SECOND: BUG-N6 __str__** - Depends on class instantiation
3. **THIRD: BUG-N1 private members** - Can test after class instantiation
4. **FOURTH: BUG-N2 recursion limit** - Independent, but VM needs it

---

## Files to Modify

| File | What to Fix |
|------|-------------|
| `ipp/vm/compiler.py:856-860` | `compile_set` method |
| `ipp/vm/vm.py` | Add `__str__`, private fields, recursion limit |
| `tests/v1_3_2/test_features.ipp` | Create test file |
| `tests/regression.py` | Add regression tests |

## DO NOT DELETE

- Any existing test files or test infrastructure
- The partial fixes already made to `arg_idx`, `__str__` in interpreter, `current_class` tracking
- Any working functionality

## Verification

After each fix, run:
```bash
python main.py tests/v1_3_2/test_features.ipp
python main.py test_vec2.ipp
python main.py tests/regression.py
```
