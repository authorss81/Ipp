# Ipp Error Reference

This document lists all error types, their codes, causes, and solutions.

## Error Code Format

Errors use the format: `Error at line X in <file>: <message>`

- **Parse errors**: `Parse error at line X, col Y: <message>`
- **Runtime errors**: `Error at line X in <file>: <message>`

---

## Parse Errors (E001-E099)

### E001 — Unexpected Token

**Message:** `Parse error at line X, col Y: Unexpected token: Token(TYPE, 'value', line=X)`

**Cause:** The parser encountered a token it didn't expect at that position.

**Common causes:**
- Missing closing parenthesis: `func test(`
- Extra comma: `[1, 2, 3,]`
- Wrong keyword: `def x():` (Ipp uses `func`, not `def`)
- Missing operator: `var x = 1 2`

**Fix:** Check the syntax around the reported line and column.

**Examples:**
```ipp
# ❌ Wrong
func test(

# ✅ Correct
func test() { }
```

---

### E002 — Expect Parameter Name

**Message:** `Parse error at line X, col Y: Expect parameter name`

**Cause:** Function parameter list has syntax error — missing parameter name after comma or opening paren.

**Fix:** Add the missing parameter name.

**Examples:**
```ipp
# ❌ Wrong
func test(a, ) { }
func test(, b) { }

# ✅ Correct
func test(a, b) { }
```

---

### E003 — Expect ')' After Parameters

**Message:** `Parse error at line X, col Y: Expect ')' after parameters`

**Cause:** Missing closing parenthesis in function parameter list.

**Fix:** Add the closing `)`.

**Examples:**
```ipp
# ❌ Wrong
func greet(name { }

# ✅ Correct
func greet(name) { }
```

---

### E004 — Expect Expression

**Message:** `Parse error at line X, col Y: Expect expression`

**Cause:** An expression was expected but not found (e.g., after `return`, in assignment).

**Fix:** Add the missing expression.

---

### E005 — Expect Identifier

**Message:** `Parse error at line X, col Y: Expect identifier`

**Cause:** A name/identifier was expected (e.g., variable name, function name).

**Fix:** Add a valid identifier.

---

### E006 — Expect '}' After Block

**Message:** `Parse error at line X, col Y: Expect '}' after block`

**Cause:** Missing closing brace for a block (function body, if/for/while block, class body).

**Fix:** Add the missing `}`.

---

### E007 — Expect ';' or Newline

**Message:** `Parse error at line X, col Y: Expect ';' or newline`

**Cause:** Statement not properly terminated.

**Fix:** Add `;` or put statement on its own line.

---

### E008 — Invalid Number Literal

**Message:** `Parse error at line X, col Y: Invalid number literal`

**Cause:** Number literal has invalid format (e.g., `0xGG`, `0o99`).

**Fix:** Use valid number format:
- Decimal: `123`, `1_000`
- Hex: `0xFF`, `0x1A`
- Octal: `0o77`, `0o10`
- Binary: `0b1010`, `0b1111`
- Float: `3.14`, `1.0e10`

---

## Runtime Errors (E100-E199)

### E100 — Undefined Variable

**Message:** `Error at line X in <file>: Undefined variable: <name>`

**Cause:** Variable has not been defined before use.

**Common causes:**
- Typo in variable name
- Variable defined in different scope
- Variable defined after use

**Fix:** Define the variable before using it, or check for typos.

**Examples:**
```ipp
# ❌ Wrong
print(x)  # x not defined

# ✅ Correct
var x = 10
print(x)
```

---

### E101 — Cannot Call <type>

**Message:** `Error at line X in <file>: Cannot call <class 'type'>`

**Cause:** Attempting to call something that is not a function.

**Common causes:**
- Calling a number: `42()`
- Calling a string: `"hello"()`
- Calling a list: `[1,2,3]()`
- Typo in function name that resolved to a variable

**Examples:**
```ipp
# ❌ Wrong
var x = 42
x()

# ✅ Correct
func greet() { print("Hello") }
greet()
```

---

### E102 — Division by Zero

**Message:** `Error at line X in <file>: Division by zero`

**Cause:** Attempting to divide by zero.

**Fix:** Check divisor before division.

**Examples:**
```ipp
# ❌ Wrong
var result = 10 / 0

# ✅ Correct
var divisor = 0
if divisor != 0 {
    var result = 10 / divisor
}
```

---

### E103 — Only Instances Have Properties

**Message:** `Error at line X in <file>: Only instances have properties, got <class 'type'>`

**Cause:** Attempting to access a property (`.field`) on a non-instance value.

**Common causes:**
- Accessing property on number: `123.foo`
- Accessing property on string: `"hello".length`
- Accessing property on list: `[1,2].foo`

**Fix:** Only access properties on class instances.

**Examples:**
```ipp
# ❌ Wrong
var x = 123
print(x.foo)

# ✅ Correct
class Point {
    func init(x, y) {
        this.x = x
        this.y = y
    }
}
var p = Point(1, 2)
print(p.x)  # 1
```

---

### E104 — Module Not Found

**Message:** `Error at line X in <file>: Module not found: <path>`

**Cause:** Import file does not exist at the specified path.

**Fix:** Check the file path is correct and the file exists.

**Examples:**
```ipp
# ❌ Wrong
import "nonexistent.ipp"

# ✅ Correct
import "mymodule.ipp"  # file exists in same directory
```

---

### E105 — List Index Out of Range

**Message:** `list index out of range`

**Cause:** Accessing a list index that doesn't exist.

**Fix:** Check the index is within bounds (0 to len-1).

**Examples:**
```ipp
# ❌ Wrong
var items = [1, 2, 3]
print(items[10])

# ✅ Correct
var items = [1, 2, 3]
if index < len(items) {
    print(items[index])
}
```

---

### E106 — Dict Key Not Found

**Message:** `dict key not found: <key>`

**Cause:** Accessing a dict key that doesn't exist.

**Fix:** Check the key exists before accessing, or use a default.

**Examples:**
```ipp
# ❌ Wrong
var d = {"a": 1}
print(d["b"])

# ✅ Correct
var d = {"a": 1}
if has_key(d, "b") {
    print(d["b"])
}
```

---

### E107 — Cannot Reassign Constant

**Message:** `Cannot reassign constant: <name>`

**Cause:** Attempting to modify a `let` variable.

**Fix:** Use `var` instead of `let` if you need to reassign.

**Examples:**
```ipp
# ❌ Wrong
let x = 10
x = 20

# ✅ Correct
var x = 10
x = 20
```

---

### E108 — Maximum Recursion Depth Exceeded

**Message:** `Error at line X in <file>: maximum recursion depth exceeded`

**Cause:** Function calls itself too many times without a base case.

**Fix:** Add a base case to stop recursion.

**Examples:**
```ipp
# ❌ Wrong
func factorial(n) {
    return n * factorial(n - 1)  # no base case!
}

# ✅ Correct
func factorial(n) {
    if n <= 1 { return 1 }
    return n * factorial(n - 1)
}
```

---

### E109 — Cannot Iterate Over <type>

**Message:** `Cannot iterate over <class 'type'>`

**Cause:** Attempting to use `for-in` on a non-iterable value.

**Fix:** Only iterate over lists, ranges, strings, dicts, or generators.

**Examples:**
```ipp
# ❌ Wrong
for x in 42 { }

# ✅ Correct
for x in [1, 2, 3] { }
for i in 0..5 { }
for c in "hello" { }
```

---

## VM Errors (E200-E299)

### E200 — Stack Underflow

**Message:** `pop from empty list`

**Cause:** VM stack is empty when a value was expected.

**Common causes:**
- Bug in VM bytecode generation
- Mismatched push/pop in compiler

**Fix:** This is a compiler/VM bug. Report it.

---

### E201 — Undefined Variable (VM)

**Message:** `Undefined variable '<name>'`

**Cause:** Variable not found in VM scope.

**Fix:** Same as E100 — define the variable before use.

---

## Error Suggestions

When you see an error, Ipp may suggest fixes:

- **"Did you mean: ..."** — Suggests similar variable/function names
- **"Tip: Use .builtins to see available functions"** — Lists all builtins
- **"Tip: Check that the variable is a function"** — You're calling a non-function
- **"Tip: Check the types of your operands"** — Type mismatch in operation
- **"Tip: Check the list/dict length with len() before indexing"** — Index out of range

---

## Error Code Index

| Code | Type | Message |
|------|------|---------|
| E001 | Parse | Unexpected Token |
| E002 | Parse | Expect Parameter Name |
| E003 | Parse | Expect ')' After Parameters |
| E004 | Parse | Expect Expression |
| E005 | Parse | Expect Identifier |
| E006 | Parse | Expect '}' After Block |
| E007 | Parse | Expect ';' or Newline |
| E008 | Parse | Invalid Number Literal |
| E100 | Runtime | Undefined Variable |
| E101 | Runtime | Cannot Call <type> |
| E102 | Runtime | Division by Zero |
| E103 | Runtime | Only Instances Have Properties |
| E104 | Runtime | Module Not Found |
| E105 | Runtime | List Index Out of Range |
| E106 | Runtime | Dict Key Not Found |
| E107 | Runtime | Cannot Reassign Constant |
| E108 | Runtime | Maximum Recursion Depth Exceeded |
| E109 | Runtime | Cannot Iterate Over <type> |
| E200 | VM | Stack Underflow |
| E201 | VM | Undefined Variable (VM) |
