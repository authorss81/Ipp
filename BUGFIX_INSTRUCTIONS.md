# v1.3.2 Bug Fix Instructions

## Current Status: **BUGS NOT FULLY FIXED** ⚠️

The following bugs from v1.3.2 have issues that need to be resolved.

---

## KNOWN ISSUE: Class Instantiation is Broken

**Symptom:** `a.x` returns `<Vec2 instance>` instead of `1`

**Root Cause:** Extra value pushed on stack during property assignment.

### Debug Output
```
GET_LOCAL idx=0, slot=0, stack=[<Vec2>, 1, 2, <Vec2>], base=0
GET_LOCAL idx=1, slot=1, stack=[<Vec2>, 1, 2, <Vec2>, <Vec2>], base=0  <-- EXTRA <Vec2>!
SET_PROPERTY: value=1, obj=<Vec2 instance>
Error: 'int' object has no attribute 'x'
```

**Problem:** Stack has 5 items instead of 4. An extra Vec2 is pushed between `y` and `self.x`.

---

## FIX REQUIRED

### Step 1: Check compile_set in `ipp/vm/compiler.py`

```python
# Line ~856 - Should NOT have DUP:
def compile_set(self, node: SetExpr):
    # FIX: removed DUP — SET_PROPERTY pops both value and obj cleanly
    self.compile_expr(node.object)
    self.compile_expr(node.value)
    self.compile_set_property(node.name)
```

### Step 2: Check SET_PROPERTY in `ipp/vm/vm.py`

```python
# Line ~706 - Should pop both value AND obj:
elif opcode == OpCode.SET_PROPERTY:
    idx = code[ip + 1]
    name = constants[idx]
    value = self.stack.pop()
    # FIX: pop obj too — compile_set no longer emits DUP
    obj = self.stack.pop()  # NOT self.stack[-1]
    if isinstance(obj, IppInstance):
        obj.set(name, value)
    elif isinstance(obj, dict):
        obj[name] = value
    else:
        setattr(obj, name, value)
```

### Step 3: Check VMFrame in `ipp/vm/vm.py`

```python
# Line ~81 - Must have _method_instance slot:
class VMFrame:
    __slots__ = ('chunk', 'closure', 'function', 'ip', 'stack_base', '_method_instance')
```

---

## Other Bugs - STATUS

| Bug | Status | Notes |
|-----|--------|-------|
| BUG-N1 | ⚠️ Partial | Private field protection exists but class instantiation broken |
| BUG-N2 | ✅ Likely OK | Recursion depth tracking added |
| BUG-N6 | ⚠️ Broken | `__str__` can't work until class instantiation fixed |
| v1.1.0 | ❌ Broken | Class instantiation not working |

---

## Test File

Create and run `test_debug.ipp`:

```ipp
class Vec2 {
    func init(x, y) {
        self.x = x
        self.y = y
    }
}

var a = Vec2(1, 2)
print(a.x)  # Should print: 1
```

**Expected output:**
```
1
```

**Current (broken) output:**
```
<Vec2 instance>
[Error] 'int' object has no attribute 'x'
```

---

## Files to Check

1. `ipp/vm/compiler.py` - Line ~856 (`compile_set`)
2. `ipp/vm/vm.py` - Line ~706 (`SET_PROPERTY`)
3. `ipp/vm/vm.py` - Line ~81 (`VMFrame.__slots__`)
4. `ipp/vm/compiler.py` - Line ~731 (`compile_identifier` - may be pushing extra value)

---

## Verification Steps

After fixing, run:
```bash
python main.py test_debug.ipp
```

Should output: `1`

Then run full test:
```bash
python main.py tests/v1_3_2/test_features.ipp
```

Expected:
```
=== v1.3.2 Bug Fix Tests ===

--- Class instantiation ---
1
2
3
4
6

--- __str__ method ---
Point(5, 10)
Point(5, 10)

--- Private members ---
1000
1000
1234
Private access blocked: true

--- Recursion limit ---
55
Recursion limit hit: true

=== All v1.3.2 tests passed! ===
```
