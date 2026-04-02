# v1.3.3 Bug Fix Instructions & Contributor Guide

## Current Status: **v1.3.3 RELEASED** ✅ ALL BUGS FIXED

v1.3.3 adds major features: named arguments, tuple unpacking, operator overloading, printf/sprintf, full math/collection libraries, and networking support.

---

## FIXED BUGS

### Bug 1: `and`/`or` Operator Precedence with Comparisons ✅ FIXED

**Symptom:** `1 == 1 and 2 == 2` returned `false`, but `(1 == 1) and (2 == 2)` returned `true`

**Severity:** Medium — workaround existed (use parentheses)

**Root Cause:** `and`/`or` keywords were mapped to `DOUBLE_AMP`/`DOUBLE_PIPE` tokens — the same tokens used by bitwise `&`/`||`. So `and_expr()` consumed the `DOUBLE_AMP` from the `&` layer of the grammar, meaning `1 == 1 and 2 == 2` parsed as `1 == (1 and 2) == 2` — comparing integers, not booleans.

**Fix Applied:**
1. **token.py** — `"and"` → `TokenType.AND`, `"or"` → `TokenType.OR` (dedicated tokens, no longer shared with `&&`/`||`)
2. **parser.py** — `or_expr`/`and_expr` match the new `AND`/`OR` tokens; `&&`/`||` are still matched as aliases
3. **interpreter.py** — `and`/`or` now short-circuit before evaluating both sides (moved before `left = node.left.accept(self)`)

**Verification:**
```ipp
print(1 == 1 and 2 == 2)  # Now prints: true
```

---

### Bug 2: Nested `len(items(d))` IppList Error ✅ FIXED

**Symptom:** `len(items(d))` failed with "Cannot call `<class 'ipp.interpreter.interpreter.IppList'>`"

**Severity:** Low — workaround existed (store in variable first)

**Root Cause:** The `items()` builtin was returning a plain Python list whose class has `__call__` in some Python introspection paths, confusing the `callable()` check.

**Fix Applied:**
1. Added an explicit `IppList` guard in `visit_call_expr` with a clear, actionable error message
2. The nested call now also works directly

**Verification:**
```ipp
var d = {"a": 1, "b": 2}
print(len(items(d)))  # Now prints: 2
```

---

## FIXED in v1.3.3

| Bug | Status | Fix |
|-----|--------|-----|
| BUG-NEW-C3 | ✅ FIXED | Operator overloading now checks `IppInstance.get_method()` |
| BUG-NEW-M4 | ✅ FIXED | Named arguments: `f(name="Alice", greeting="Hi")` |
| BUG-NEW-M7 | ✅ FIXED | Tuple unpacking: `var a, b = [1, 2]` |
| BUG-NEW-N6 | ✅ FIXED | `__str__` method called by `print()` |
| BUG-NEW-N8 | ✅ FIXED | IppList guard in `visit_call_expr`, consistent list wrapping |
| and/or precedence | ✅ FIXED | Dedicated AND/OR tokens, short-circuit before left evaluation |
| nested len(items()) | ✅ FIXED | Explicit IppList guard, nested calls work directly |
| Standard Library | ✅ FIXED | `printf()`, `sprintf()`, `scanf()`, `file_read()`, `file_write()` |
| Data Formats | ✅ FIXED | JSON, XML, YAML, TOML all working |
| Math Library | ✅ FIXED | `lerp`, `clamp`, `distance`, `normalize`, `dot`, `cross`, `sign`, etc. |
| Collections | ✅ FIXED | `set()`, `has_key()`, `keys()`, `values()`, `items()` all work with IppDict |
| Networking | ✅ FIXED | HTTP (GET/POST/PUT/DELETE), FTP, SMTP, URL encoding/decoding |
| `math.sign` bug | ✅ FIXED | `move_towards()` no longer uses nonexistent `math.sign` |

---

## Networking Libraries Implemented ✅

### 1. HTTP Client ✅
- `http_get(url, headers)` — HTTP GET request
- `http_post(url, data, headers)` — HTTP POST request
- `http_put(url, data, headers)` — HTTP PUT request
- `http_delete(url, headers)` — HTTP DELETE request
- `http_request(url, method, data, headers)` — Generic HTTP request

### 2. FTP Client ✅
- `ftp_connect(host, user, password, port)` — Connect to FTP server
- `ftp_disconnect(client)` — Disconnect from FTP server
- `ftp_list(client, path)` — List files on FTP server
- `ftp_get(client, remote_path, local_path)` — Download file from FTP
- `ftp_put(client, local_path, remote_path)` — Upload file to FTP

### 3. SMTP Email ✅
- `smtp_connect(server, port, use_tls, username, password)` — Connect to SMTP server
- `smtp_disconnect(client)` — Disconnect from SMTP server
- `smtp_send(client, from_addr, to_addrs, subject, body)` — Send email

### 4. URL Utilities ✅
- `url_encode(string)` — URL encode a string
- `url_decode(string)` — URL decode a string
- `url_query_build(dict)` — Build query string from dict
- `url_query_parse(string)` — Parse query string to dict

---

## Remaining TODO for Contributors

| Priority | Feature | Complexity | Status |
|----------|---------|------------|--------|
| 🟡 MED | HTTP Server (not just client) | Medium | ⏳ TODO (v1.3.8) |
| 🟡 MED | WebSocket client/server | Medium | ⏳ TODO (v1.3.8) |
| 🟢 LOW | Deque collection type | Low | ✅ DONE (v1.3.4) |
| 🟢 LOW | PriorityQueue collection | Medium | ⏳ TODO (v1.3.8) |
| 🟢 LOW | Tree/Graph data structures | Medium | ⏳ TODO (v1.3.8) |
| 🟢 LOW | Structural pattern matching | Medium | ⏳ TODO |
| 🟢 LOW | Labeled break/continue | Medium | ⏳ TODO |

---

## VM BUGFIX INSTRUCTIONS (v1.4.1 - v1.4.3)

The VM (`ipp/vm/vm.py`) has 7 bugs preventing it from being a drop-in replacement for the interpreter. **Do NOT delete any existing code.** Only add or modify the specific sections described.

### VM-BUG-1: Function Calls with Arguments ("Cannot call int") — Target: v1.4.1
**Files:** `ipp/vm/vm.py` (`_call` method), `ipp/vm/compiler.py` (`compile_call`)
**Symptom:** `func add(a, b) { return a + b }` then `print(add(3, 4))` throws "Cannot call int"
**Root Cause:** The global inline cache (`_global_cache`) returns stale values. When `add` is looked up via `GET_GLOBAL`, the cache may have a wrong cached value from before the function was defined.
**Fix:** Ensure `DEFINE_GLOBAL` invalidates the cache entry for that name. Also verify the CALL opcode handler pops callee and args in correct order (callee below all args on stack).
**Test:** `func add(a, b) { return a + b }` + `print(add(3, 4))` should print `7`.

### VM-BUG-2: Dict Index Access ("list index out of range") — Target: v1.4.1
**Files:** `ipp/vm/vm.py` (`GET_INDEX` handler), `ipp/vm/vm.py` (`DICT` handler)
**Symptom:** `var d = {"a": 1}; print(d["a"])` throws "list index out of range"
**Root Cause:** The `GET_INDEX` handler checks `isinstance(obj, dict)` but the stack order or dict creation may be wrong. The `DICT` opcode creates plain Python dicts — verify key-value pairs are pushed/popped correctly.
**Fix:** Verify `GET_INDEX` stack order: `idx = pop(); obj = pop()`. For `d["a"]`, `d` is pushed first, then `"a"`, so popping gives `"a"` first (idx), then `d` (obj). Check `DICT` handler creates dict correctly.
**Test:** `var d = {"a": 1, "b": 2}` + `print(d["a"])` should print `1`.

### VM-BUG-3: Try/Catch Doesn't Catch — Target: v1.4.1
**Files:** `ipp/vm/vm.py` (`GET_GLOBAL`, `TRY`/`CATCH` handlers)
**Symptom:** `try { var x = undef } catch e { print("caught") }` throws "Undefined variable"
**Root Cause:** `GET_GLOBAL` raises `VMError` but the exception handler stack may not be set up correctly, or the error is raised outside the try block scope.
**Fix:** Verify `TRY` opcode pushes exception handler, `GET_GLOBAL`'s `VMError` is caught, and `CATCH` sets up catch block correctly.

### VM-BUG-4: Class Property Access — Target: v1.4.2
**Files:** `ipp/vm/vm.py` (`GET_PROPERTY`/`SET_PROPERTY` handlers)
**Symptom:** `class Dog { func init() { this.name = "rex" } }; var d = Dog(); print(d.name)` fails
**Root Cause:** `SET_PROPERTY`/`GET_PROPERTY` may not handle `IppInstance.fields` correctly. Class instantiation may not bind `self` properly in `init`.
**Fix:** Check `SET_PROPERTY` sets on `IppInstance.fields`, `GET_PROPERTY` reads from `IppInstance.fields`, and class instantiation binds `self` correctly.

### VM-BUG-5: Named Arguments — Target: v1.4.2
**Files:** `ipp/vm/compiler.py` (`compile_call`)
**Symptom:** `func f(x, y) { return x - y }; f(y=1, x=10)` returns NoneType error
**Root Cause:** VM compiler doesn't handle `NamedArg` AST nodes. Named args need to be matched to parameter positions before pushing onto stack.
**Fix:** In `compile_call()`, check `node.named_arguments`, get function's parameter names, match named args to positions, push in correct order.

### VM-BUG-6: Recursion — Target: v1.4.2
**Files:** `ipp/vm/vm.py` (`_call`)
**Symptom:** `func fib(n) { ... return fib(n-1) + fib(n-2) }` fails
**Root Cause:** Same as VM-BUG-1 — `GET_GLOBAL` returns cached wrong value for recursive calls.
**Fix:** Fix VM-BUG-1 first — this should resolve automatically.

### VM-BUG-7: For Loops — Target: v1.4.3
**Files:** `ipp/vm/compiler.py` (`compile_for`)
**Symptom:** `for i in 0..3 { print(i) }` crashes with AttributeError
**Root Cause:** `compile_for` references `emit_get_global` which doesn't exist on `Chunk`.
**Fix:** Replace with proper opcode sequence: `CONSTANT` (range start), `CONSTANT` (range end), `RANGE` opcode, then iterate. Or use `GET_GLOBAL` for `range` builtin + `CALL` + list iteration.

### ⚠️ CRITICAL RULES
1. **DO NOT delete any existing code** — only add or modify specific lines
2. **Test each fix individually** before moving to the next
3. **Run full regression suite** after all fixes: `python tests/regression.py`
4. **Only modify** `ipp/vm/vm.py` and `ipp/vm/compiler.py`
5. **Preserve all existing builtins** — do not remove anything from `_init_builtins()`

---

*Last updated: 2026-04-02 — v1.3.7 release (REPL enhancements: .load, .save, .doc, .time, .which, .undo, .profile, .alias, .edit, .last)*
