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

| Priority | Feature | Complexity |
|----------|---------|------------|
| 🟡 MED | HTTP Server (not just client) | Medium |
| 🟡 MED | WebSocket client/server | Medium |
| 🟢 LOW | Deque collection type | Low |
| 🟢 LOW | PriorityQueue collection | Medium |
| 🟢 LOW | Tree/Graph data structures | Medium |
| 🟢 LOW | Structural pattern matching | Medium |
| 🟢 LOW | Labeled break/continue | Medium |

---

*Last updated: 2026-04-02 — v1.3.3 release (all bugs fixed, networking implemented)*
