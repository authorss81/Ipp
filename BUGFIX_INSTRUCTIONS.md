# v1.3.3 Bug Fix Instructions & Contributor Guide

## Current Status: **v1.3.3 RELEASED** ✅ with Known Issues

v1.3.3 adds major features: named arguments, tuple unpacking, operator overloading, printf/sprintf, and full math/collection libraries.

---

## KNOWN BUG: `and`/`or` Operator Precedence with Comparisons

**Symptom:** `1 == 1 and 2 == 2` returns `false`, but `(1 == 1) and (2 == 2)` returns `true`

**Severity:** Medium — workaround exists (use parentheses)

**Location:** `ipp/interpreter/interpreter.py`, `visit_binary_expr()`, lines ~532-535

### Reproduction
```ipp
# BROKEN — returns false
print(1 == 1 and 2 == 2)

# WORKS — returns true (with parentheses)
print((1 == 1) and (2 == 2))
```

### Workaround
Use intermediate variables or parentheses:
```ipp
# Instead of: if x == 1 and y == 2 { ... }
var a = x == 1
var b = y == 2
if (a) and (b) { ... }
```

---

## KNOWN BUG: Nested function calls with `items()` returns IppList error

**Symptom:** `len(items(d))` fails with "Cannot call <class 'ipp.interpreter.interpreter.IppList'>"

**Severity:** Low — workaround exists (store in variable first)

**Location:** `ipp/interpreter/interpreter.py`, `visit_call_expr()`

### Reproduction
```ipp
var d = {"a": 1, "b": 2}

# BROKEN — Cannot call IppList
print(len(items(d)))

# WORKS — store in variable first
var d_items = items(d)
print(len(d_items))
```

### Root Cause
When a builtin function returning a list is nested inside another function call, the interpreter incorrectly treats the IppList class as a callable rather than the returned list instance.

### Workaround
Store the inner function result in a variable before passing to the outer function:
```ipp
# Instead of: len(items(d))
var d_items = items(d)
len(d_items)
```

### Root Cause
The `and` operator in the interpreter short-circuits incorrectly when the right operand is a comparison expression. The issue is in how `and` returns its result:
```python
elif node.operator == "and":
    return left if not bool(left) else right
```

When `right` is itself a `BinaryExpr` (like `2 == 2`), it seems to not be evaluated correctly in some contexts.

### Files to Check
1. `ipp/interpreter/interpreter.py` — `visit_binary_expr()`, line ~532
2. `ipp/parser/parser.py` — `and_expr()`, line ~403
3. Check if `and` keyword token (`DOUBLE_AMP`) conflicts with `&&` operator

### Verification
```bash
python main.py -c "print(1 == 1 and 2 == 2)"
# Should print: true (currently prints: false)
```

---

## CONTRIBUTOR REQUEST: Networking Libraries

The following networking features are **not yet implemented** and need contributors:

### 1. HTTP Server (`http.server`)
```ipp
var server = http.server(8080)
server.get("/", func(req, res) {
    res.send("Hello World")
})
server.start()
```
**Requirements:**
- Basic HTTP GET/POST support
- Route handling
- Request/response objects
- Python `http.server` or `aiohttp` backend

### 2. WebSocket (`websocket`)
```ipp
var ws = websocket("ws://localhost:8080")
ws.on("message", func(data) {
    print("Received:", data)
})
ws.send("Hello")
```
**Requirements:**
- Client-side WebSocket
- Server-side WebSocket (optional)
- Event-based message handling
- Python `websockets` library backend

### 3. FTP Client (`ftp`)
```ipp
var client = ftp.connect("ftp.example.com", "user", "pass")
client.upload("local.txt", "/remote/path.txt")
client.download("/remote/file.txt", "local_copy.txt")
client.list_dir("/")
client.disconnect()
```
**Requirements:**
- Connect/disconnect
- Upload/download files
- List directory contents
- Python `ftplib` backend

### 4. SMTP Email (`smtp`)
```ipp
smtp.send(
    from="sender@example.com",
    to="recipient@example.com",
    subject="Hello",
    body="This is a test email",
    host="smtp.example.com",
    port=587,
    user="sender@example.com",
    pass="password"
)
```
**Requirements:**
- Send plain text emails
- Send HTML emails
- Attachment support (optional)
- Python `smtplib` backend

### Implementation Guide
1. Add functions to `ipp/runtime/builtins.py`
2. Register in `BUILTINS` dict
3. Add tests to `tests/v1_3_4/`
4. Follow existing patterns (see `ipp_http_get`, `ipp_http_post` for reference)

---

## FIXED in v1.3.3

| Bug | Status | Fix |
|-----|--------|-----|
| BUG-NEW-C3 | ✅ FIXED | Operator overloading now checks `IppInstance.get_method()` |
| BUG-NEW-M4 | ✅ FIXED | Named arguments: `f(name="Alice", greeting="Hi")` |
| BUG-NEW-M7 | ✅ FIXED | Tuple unpacking: `var a, b = [1, 2]` |
| BUG-NEW-N6 | ✅ FIXED | `__str__` method called by `print()` |
| Standard Library | ✅ FIXED | `printf()`, `sprintf()`, `scanf()`, `file_read()`, `file_write()` |
| Data Formats | ✅ FIXED | JSON, XML, YAML, TOML all working |
| Math Library | ✅ FIXED | `lerp`, `clamp`, `distance`, `normalize`, `dot`, `cross`, `sign`, etc. |
| Collections | ✅ FIXED | `set()`, `has_key()`, `keys()`, `values()`, `items()` all work with IppDict |
| `math.sign` bug | ✅ FIXED | `move_towards()` no longer uses nonexistent `math.sign` |

---

## Remaining TODO for Contributors

| Priority | Feature | Complexity |
|----------|---------|------------|
| 🔴 HIGH | Fix `and`/`or` precedence bug | Low |
| 🟡 MED | Fix nested function call IppList error | Low |
| 🟡 MED | Networking: HTTP server | Medium |
| 🟡 MED | Networking: WebSocket | Medium |
| 🟡 MED | Networking: FTP client | Low |
| 🟡 MED | Networking: SMTP email | Low |
| 🟢 LOW | Deque collection type | Low |
| 🟢 LOW | PriorityQueue collection | Medium |
| 🟢 LOW | Tree/Graph data structures | Medium |

---

*Last updated: 2026-04-01 — v1.3.3 release*
