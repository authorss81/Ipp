# Ipp REPL — Detailed Audit

**Version:** 2.0.25  
**File:** `ipp/main.py` (3371 lines)  
**Supporting:** `ipp/runtime/highlighter.py` (511 lines), `ipp/lsp/server.py` (421 lines)
**Last updated:** 2026-06-29 — All Critical Issues Fixed ✅

---

## Table of Contents

1. [REPL Loop & Architecture](#1-repl-loop--architecture)
2. [Commands Audit](#2-commands-audit)
3. [Tab Completion & Autocomplete](#3-tab-completion--autocomplete)
4. [Error Handling](#4-error-handling)
5. [Multi-line Input](#5-multi-line-input)
6. [History Management](#6-history-management)
7. [Interpreter Switching](#7-interpreter-switching)
8. [Syntax Highlighting](#8-syntax-highlighting)
9. [Session Management](#9-session-management)
10. [Signal/Interrupt Handling](#10-signalinterrupt-handling)
11. [Tutorial System](#11-tutorial-system)
12. [Async/Await Support](#12-asyncawait-support)
13. [File I/O Operations](#13-file-io-operations)
14. [Input Encoding & ANSI](#14-input-encoding--ansi)
15. [LSP Server](#15-lsp-server)
16. [Syntax Highlighter](#16-syntax-highlighter)
17. [Critical Issues Summary](#17-critical-issues-summary)

---

## 1. REPL Loop & Architecture

**Location:** `ipp/main.py:1377-2822`, function `run_repl()`

### How It Works

The REPL initialises an `InterpreterManager`, wires up readline or `prompt_toolkit`, displays the banner, installs interrupt handlers, and enters a `while True` loop. Each iteration:

1. Builds a prompt string (`C_PROMPT` for first line, `C_CONT` for continuation).
2. Reads input from `_hl_session.prompt()` (prompt_toolkit) or `input()`.
3. Checks for meta commands (`.help`, `.vars`, etc.) on a fresh prompt.
4. Accumulates multi-line input into a buffer.
5. Executes via `tokenize → parse → interp.run(ast)`.
6. Prints formatted result and timing.
7. Saves environment snapshots for `.undo`.

### Strengths

- Clean separation: prompt-building, input-reading, meta-command dispatch, execution.
- Prompt differentiation: `❯` (first line) vs `···` (continuation) using Unicode.
- Dynamic prompt formats: `dir`, `time`, `full`, custom arrow symbol.
- Timing display on every expression (`{elapsed*1000:.1f}ms`).
- Expression history (`$_1`, `$_2`, …) auto-injected into globals.
- Environment snapshot for `.undo` with 50-snapshot cap.

### Limitations

| Limitation | Impact | Suggestion |
|---|---|---|
| No async event loop — REPL blocks on every input call | Cannot run background tasks interactively | Add `.bg` / `.jobs` with thread pool (partially exists at line 2505 but not integrated with main loop) |
| No line-editing beyond readline/prompt_toolkit defaults | `.bind` key mappings stored but never processed | Implement key-binding dispatch in the input loop |
| No graceful terminal resize handling | Prompt width may get misaligned | Listen for `SIGWINCH` and recalculate prompt width |
| 10-line forced-execute guard is unconditional | Executes unbalanced code after 10 lines, causing parse errors | Warn before force-executing; allow user to continue editing |
| Macro expansion (`$1`, `$2`) splits on spaces | Breaks quoted arguments containing spaces | Use regex or a proper mini-parser for argument splitting |

---

## 2. Commands Audit

### 2.1 `.help`

**Location:** `pp/main.py:768-873` (`print_help()`)

Displays categorized command tables and a Quick Reference of syntax snippets.

| Aspect | Status |
|---|---|
| Commands section | Lists 13 core dot-commands with descriptions |
| REPL Tools v1.3.7 | 12 tools listed |
| REPL Tools v1.3.10 | 30+ tools listed |
| Quick Reference | 15 syntax snippets |

**Issues:**
- Some listed commands are stubs (`.break` says "not yet implemented")
- Many commands not listed at all: `.mem`, `.highlight`, `.theme`, `.themes`, `.bench`, `.sighelp`, `.typehints`, `.cache`, `.hist`, `.sessions`, `.reload`, `.checkpoint`, `.restore`, `.macro`, `.compare`, `.serve`, `.html`, `.plot`, `.bg`, `.jobs`, `.async`
- `.theme`/`.themes` defined twice — second block is dead code (never reached)

### 2.2 `.vars` (line 1473)

Lists user-defined variables with type and value.

**Limit:** Does not show variables from parent environments. Type detection (`val.cls.name`) is fragile for non-IppInstance objects.

### 2.3 `.fns` (line 1474)

Lists user-defined functions with per-function color palette.

**Limit:** Only shows functions from the immediate global environment.

### 2.4 `.builtins` (line 1475)

Groups builtins into 25+ categories with color-coded display.

**Limit:** Category lists are hard-coded and must be manually kept in sync with `BUILTINS`.

### 2.5 `.modules` (line 1476)

Shows loaded modules.

**Limit:** Subset of `.builtins` — does not show File, JSON, HTTP categories.

### 2.6 `.history` (line 1582)

Shows command history. Supports `.history N` for N lines.

**Limit:** History includes meta commands (`.help`, `.vars`, etc.) — pollutes the list.

### 2.7 `.colors` (line 1588)

Toggles ANSI colors on/off.

**Limit:** Only on/off — no way to toggle specific color elements.

### 2.8 `.vm` (line 1568)

Switches between tree-walking interpreter and bytecode VM.

**Critical limit:** Switching discards ALL state — variables, functions, classes are lost. No state migration.

### 2.9 `.clear` (line 1558)

Resets interpreter, readline, buffer, history, function colors.

**Limit:** Does not clear `_last_results`, `_last_result`, `_undo_stack`, `_env_snapshots`, `_aliases`, `_key_bindings`.

### 2.10 `.types` (line 1472)

Shows a type system summary.

**Limit:** Does not show ECS types (Entity, System, World, Component).

### 2.11 `.load` (line 1603)

Loads and executes an Ipp file.

**Limit:** Does not resolve relative paths. No `import`-style module caching.

### 2.12 `.save` (line 1627)

Saves command history to file.

**Limit:** Includes meta commands which are not valid Ipp syntax. No header or timestamp.

### 2.13 `.doc` (line 1639)

Shows builtin documentation with syntax, description, examples, returns.

**Limit:** Falls back to `fn.__doc__` for undocumented builtins — 259 of 438 builtins have no docstring.

### 2.14 `.time` (line 1667)

Benchmarks a single expression execution.

**Limit:** Single run only — not statistical. No warm-up. Use `.bench` for multi-run stats.

### 2.15 `.which` (line 1688)

Checks if a name is a builtin, variable, or function.

**Limit:** Does not search parent environments.

### 2.16 `.last` / `$_` (line 1708)

References the last result value.

**Strengths:** Simple, well-integrated.

### 2.17 `.undo` / `.redo` (line 1716)

Undo/redo via environment snapshots.

**Limit:** Only captures `global_env`. Does NOT undo imported modules, class definitions, aliases, key bindings, `_last_result`, `_cmd_history`.

### 2.18 `.edit` (line 2369)

Opens the last command in an editor, reads it back, re-executes.

**Limit:** Editing a `.load` or `.save` command will re-execute it as Ipp code, causing errors. No handling for non-zero editor exit code.

### 2.19 `.profile` (line 2390)

Profiles the last command using `cProfile`.

**Limit:** Only works for the tree-walking interpreter, not the VM.

### 2.20 `.alias` (line 1729)

Creates command aliases.

**Limit:** Aliases are never persisted. Expansion happens after most meta-command checks, so some aliases may not work.

### 2.21 `.pretty` (line 1776)

Pretty-prints complex data structures.

**Bug:** Uses a **new** `Interpreter()` for evaluation — session variables are NOT accessible.

### 2.22 `.stack` (line 1796)

Shows session statistics (call depth, variable count, history sizes).

**Misleading name:** Does NOT show an actual call stack. It's a statistics display.

### 2.23 `.session` (line 1810)

Save/load/clear session state.

**Critical bug:** `.session load` creates temporary `Interpreter()` objects instead of using the current session's interpreter — REPL state is never actually restored.
- `.session export` (line 2289) duplicates `.export` functionality.
- No support for named sessions or session switching.

### 2.24 `.export` (line 2186)

Exports history as an `.ipp` script.

**Limit:** Includes meta commands in output. These are not valid Ipp syntax and will error if re-run.

### 2.25 `.prompt` (line 2208)

Customises the prompt format (`ipp`, `dir`, `time`, `full`, custom arrow).

**Strengths:** Clean implementation with 5 modes.

### 2.26 `.json` (line 2134)

Pretty-prints JSON.

**Bug:** Uses a new `Interpreter()` — session variables inaccessible.
- `.format` (line 2167) is regex-based and would corrupt strings containing operator-like patterns.

### 2.27 `.cd` / `.ls` / `.pwd` (line 2223)

Filesystem navigation commands.

**Strengths:** Colorises directories and executables. Error handling for missing paths.

### 2.28 `.pipe` (line 2257)

Pipes last result to a shell command.

**Strengths:** Uses `input=` parameter (safe from shell injection).  
**Limit:** `shell=True` still carries risk if the command string is user-controlled.

### 2.29 `.bind` (line 2279)

Stores key-to-command mappings and processes them on input expansion.

**✅ FIXED:** Key bindings are now expanded when the user enters a bound key string (after alias expansion, before execution). See `main.py:2330-2334`.

### 2.30 `.search` (line 2079)

Searches builtin names and documentation text. Shows up to 20 results.

**Strengths:** Searches both `BUILTIN_DOCS` and raw `__doc__` strings.

### 2.31 `.examples` (line 2111)

Shows 10 categorized Ipp code examples.

**Strengths:** Syntax-highlighted output.

### 2.32 `.tutorial` (line 2017)

Interactive tutorial with 8 lessons.

**Limit:** No code validation — auto-advances on *any* successful execution, even unrelated code. No error guidance.

### 2.33 `.plugin` (line 2062)

Loads and executes Ipp plugin files.

**Limit:** No lifecycle management (no unload, no namespace isolation).

### 2.34 `.debug` (line 1891)

Toggles VM single-step debugging.

**Limit:** Output handled by the VM itself, not the REPL. No source-line display or variable inspection.

### 2.35 ~~`.break` (line 1909)~~ — REMOVED

**✅ FIXED:** The unimplemented stub was removed. Use `breakpoint()` directly in Ipp code instead.

### 2.36 `.watch` (line 1917)

Evaluates an expression and shows its current value.

**Bug:** Single-shot only — does NOT continuously update. Uses a new `Interpreter()`.

### 2.37 `.locals` (line 1938)

Shows local variables.

**Limit:** Same as `.vars` but includes parent environment values.

### 2.38 `.table` (line 1957)

Shows a list of dicts as a formatted table.

**Limit:** Only works with Python-native `list of dict` — not `IppList` of `IppDict`.

### 2.39 `.theme` / `.themes` (line 1527)

Sets color theme from 6 built-in options. Shows color swatches.

**✅ FIXED:** Dead-code duplicate block removed.

### 2.40 `.highlight` (line 1480)

Toggles prompt_toolkit syntax highlighting.

**Strengths:** Clear install instructions when missing. Graceful fallback to plain `input()`.

### 2.41 Other Commands

| Command | Line | Notes |
|---|---|---|
| `.mem` | 1512 | Requires `psutil` — not in requirements |
| `.bench` | 2416 | Multi-run benchmark with stats — robust |
| `.html` | 2442 | Opens temp HTML via `webbrowser` |
| `.plot` | 2467 | Matplotlib plotting to temp PNG |
| `.bg` / `.jobs` | 2505 | Background execution via threads with job queue |
| `.async` | 2548 | Wraps expression in an async function |
| `.serve` | 2577 | TCP REPL server on a port |
| `.compare` | 2604 | Compares two expressions side-by-side |
| `.hist` | 2632 | Shows `_last_results` in reverse |
| `.reload` | 2642 | Clears loaded module cache |
| `.checkpoint` / `.restore` | 2663 | Saves/restores env + history |
| `.macro` | 2700 | Text-macro expansion |
| `.typehints` | 2320 | Shows variable types |
| `.sighelp` | 2346 | Shows function signatures from `__doc__` |

---

## 3. Tab Completion & Autocomplete

**Location:** `ipp/main.py:490-623` (`IppCompleter`), `ipp/runtime/highlighter.py:368-393` (`_IppCompleter`)

### Readline-based (`IppCompleter`)

- Context-sensitive: REPL commands (`.` prefix), dict keys (`dict["key"`), member completion (`obj.member`).
- Fuzzy matching using `difflib.get_close_matches`.
- Sources: builtins, keywords, global variables, functions.
- Dict key completion traverses the environment chain.
- Member completion handles `IppInstance.fields`, `.ipp_class.methods`, `.data` dict keys.

### prompt_toolkit (`_IppCompleter`)

- Context-aware with category metadata (keyword, literal, builtin, type, symbol).
- User symbols pushed via `update_symbols()` / `_refresh_symbols()`.
- `complete_while_typing=False` — Tab-triggered only.

### Limitations

| Limitation | Impact |
|---|---|
| No snippet completion | Cannot expand `func` → `func name(params) { }` |
| No signature help on `(` | No parameter hints for functions |
| No file-path completion | `.load`, `.save`, `.cd`, `.ls` have no path suggestions |
| `readline.set_completer_delims` includes almost all punctuation | Completion won't trigger within `foo.bar` — workaround exists but fuzzy fallback is blocked |
| `_refresh_symbols()` called every prompt | Inefficient for large symbol tables (should be cached) |

---

## 4. Error Handling

**Location:** `ipp/main.py:1286-1333`, `1421`, `2788`

### Architecture

- **Outer try** (line 1421): catches `KeyboardInterrupt` and `EOFError` during input.
- **Inner try** (line 2788): catches exceptions from `tokenize`/`parse`/`eval`.
- **`_format_error_with_suggestions`** (line 1324): formats errors with `✗` prefix.
- **`_suggest_fix`** (line 1286): pattern-matches error messages and provides "Did you mean…" suggestions via `difflib.get_close_matches`.

### Strengths

- Handles undefined variables, call errors, type errors, index errors, attribute errors, recursion limits, syntax errors.
- Suggestions are color-coded with `C_WARN`/`C_OK`.

### Limitations

| Limitation | Impact |
|---|---|
| Pattern matching is fragile | Relies on exact substrings like `"Undefined variable"` — breaks if error format changes |
| No VM-specific error handling | VM has its own error types that aren't formatted |
| Suggestions always shown | Even if the user already knows the fix — no way to suppress |
| Error location extraction is coarse | Regex `r'line (\d+)'` only extracts a single line number — no column info |

---

## 5. Multi-line Input

**Location:** `ipp/main.py:699-728` (`_balanced`, `_needs_more`), `2722-2741` (main loop)

### How It Works

- `_balanced()` tracks brace balance `()[]{}` with string-literal awareness (escaped quotes, single/double quote state).
- `_needs_more()` returns `True` when unbalanced or source ends with `{` or `,`.
- Backslash `\` line ending → append and continue.
- Force-execute after 10 lines.

### Limitations

| Limitation | Impact |
|---|---|
| No heredoc / multi-line strings | Strings cannot span multiple lines |
| Backslash continuation leaves `\` in source | The backslash is preserved verbatim, which may confuse the lexer |
| 10-line force-execute is unconditional | Even unbalanced code is executed, producing parse errors |
| No auto-indent after `{` | User must manually manage continuation indentation |
| No leading-whitespace stripping | Inconsistent indentation across continuation lines |
| No visual balance indicator | No feedback showing which braces are still open |

---

## 6. History Management

**Location:** `ipp/main.py:1395` (`_cmd_history`), `1397` (`_last_results`), `628-659` (readline history)

### Mechanisms

- **`_cmd_history`:** Python list of every executed source string (including meta commands).
- **`_last_results`:** List of `(index, value)` tuples, auto-injected as `$_1`, `$_2`, etc. Capped at 100.
- **readline history:** `~/.ipp/history`, 2000 entries, auto-saved via `atexit`.
- **prompt_toolkit history:** `FileHistory(history_file)`, persistent across sessions.

### Strengths

- Dual history mechanism (readline + prompt_toolkit).
- Expression history accessible as variables (`$_1`, `$_2`, …).
- `.undo` snapshots use `_cmd_history` for state tracking.

### Limitations

| Limitation | Impact |
|---|---|
| No Ctrl+R reverse search for readline users | prompt_toolkit has `enable_history_search=True` but readline does not |
| `_cmd_history` is not persisted by itself | Only readline's internal history file is saved |
| `.save`/`.session save` writes `_cmd_history` but `.load` can't restore it | No way to reload a previous session's history |
| `_last_results` not persisted | Lost on REPL restart |

**✅ FIXED (v2.0.25):** Meta commands (`.help`, `.vars`, etc.) are now filtered from `_cmd_history` — only Ipp code is stored. This keeps history clean for `.load`, `.export`, `.session save`, and `.save`.

---

## 7. Interpreter Switching

**Location:** `ipp/main.py:1056-1128` (`InterpreterManager`, `VMInterpreter`, `_VMGlobalEnvShim`)

### Components

| Component | Purpose |
|---|---|
| `InterpreterManager` | Manages two interpreters (tree-walking + VM) |
| `VMInterpreter` | Wraps `VM` to provide interpreter-compatible interface |
| `_VMGlobalEnvShim` | Exposes `VM.globals` as `.values` dict |

### Switching Mechanism

- `.vm vm` → sets `use_vm = True`
- `.vm interpreter` → sets `use_vm = False`
- `get_interpreter()` returns the active one
- Reset triggers `setup_readline()` to rewire completers

### Critical Limitations

| Limitation | Impact |
|---|---|
| `.undo`/`.redo` uses different dicts per mode | The shim returns a fresh reference each time — may not affect VM internals correctly |
| `VMInterpreter._wrap_for_vm` only handles `ExprStmt` | If a `Program` already contains a `ReturnStmt`, it gets double-wrapped |

**✅ IMPROVED (v2.0.25):** State is now preserved when switching modes — `InterpreterManager.switch_to()` copies `global_env.values` between the tree-walking interpreter and VM before replacing the target, so variables, functions, and classes survive the switch.

---

## 8. Syntax Highlighting

### In-REPL `highlight()` (`ipp/main.py:330-369`)

Regex-based line processor that colors strings, booleans, numbers, keywords, builtins, and function calls.

| Aspect | Detail |
|---|---|
| Approach | Regex substitution, line by line |
| Order | Comment → strings → booleans → numbers → keywords → builtins → function calls |
| Compexity | ~40 lines |

**Limitations:**

| Limitation | Impact |
|---|---|
| Regex-based, not parser-aware | Cannot handle edge cases in string/comment interactions |
| No class/decorator/type highlighting | Missing language features |
| `_KEYWORDS`/`_BUILTINS` sets duplicated across 3 files | Maintenance burden (main.py, highlighter.py, builtins.py) |
| Number regex matches `123.` as valid number | Trailing dot is not a valid Ipp literal |
| User function-call detection is naive | Matches any identifier followed by `(` — including keywords |

### prompt_toolkit `IppLexer` (`ipp/runtime/highlighter.py:358-366`)

Token-based lexer adapted to prompt_toolkit's `Lexer` interface.

| Aspect | Detail |
|---|---|
| Approach | `tokenize_line()` returns `(type, text)` pairs |
| Token categories | 14 types with per-theme styling |
| Themes | 6 built-in themes |
| Output | CSS-style color strings via `lex_document` |

**Limitations:**

| Limitation | Impact |
|---|---|
| Line-scoped — cannot handle multi-line tokens | Multi-line strings or comments break highlighting |
| No string interpolation highlighting | Template strings (`"Hello {name}"`) not colored |
| No error tokens | Malformed syntax silently consumed |
| `_BUILTIN` set includes ECS/scene functions | May not be globally available |
| `_TYPE` set includes error classes | `TypeError`, `ValueError` etc. are error objects, not type names in Ipp |
| No method highlighting | `obj.method()` shows `method` as call but `obj` as identifier |

---

## 9. Session Management

**Location:** `ipp/main.py:1810-1886` (session save/load/clear), `2289-2301` (export), `2303-2317` (list)

### `.session save`

Serializes `_cmd_history[-100:]`, `_last_result`, and variable names as JSON to `~/.ipp/sessions/current_session.json`.

### `.session load`

**Critical bug:** Creates temporary `Interpreter()` objects (not `interp_manager.get_interpreter()`) and re-executes each command. The loaded state accumulates inside temporary interpreters but the REPL's actual environment is **never updated**.

Variable values are saved as `str(v)` — not parseable Ipp literals, so they cannot be restored programmatically.

### `.session clear`

Deletes the session file.

### `.sessions` (line 2303)

Lists files in `~/.ipp/sessions/`. Only shows `current_session.json` — no named session support.

### Limitations Summary

| Issue | Severity |
|---|---|
| `.session load` uses wrong interpreter — state never restored | **Bug** |
| Variable values saved as `str(v)`, not Ipp literals | **Design flaw** |
| No named sessions | Missing feature |
| Sessions directory is hard-coded | Minor |

---

## 10. Signal/Interrupt Handling

**Location:** `ipp/main.py:32-69` (handler), `43-48` (check), `50-69` (enable)

### Architecture

- **First Ctrl+C:** Sets flag, prints "Press Ctrl+C again to exit".
- **Second Ctrl+C:** Calls `sys.exit(0)`.
- **Unix:** `signal.signal(signal.SIGINT, handler)`.
- **Windows:** `SetConsoleCtrlHandler` via `ctypes` (Python's `signal` module doesn't dispatch SIGINT reliably on Windows).

### Strengths

- Double-tap prevents accidental exits.
- Windows support via Win32 API.
- `_check_interrupt()` for cooperative cancellation.

### Limitations

| Limitation | Impact |
|---|---|
| `_INTERRUPT_COUNT` not thread-safe | Race condition under concurrent access |
| Windows `SetConsoleCtrlHandler` handler may be GC'd | Lambda inside function may be garbage-collected |
| No `SIGTERM` handling | Only SIGINT is handled |
| `KeyboardInterrupt` during execution (line 2813) bypasses cleanup | Buffer not cleared, line counter not incremented |

**✅ FIXED (v2.0.25):**
- `_INTERRUPT_FLAG` is now checked **before** each execution in the REPL loop (`main.py:2761-2768`).
- The VM's main execution loop checks `_vm_interrupt.is_set()` every 1000 instructions and stops gracefully (`vm.py:1510-1515`).
- The Ctrl+C handler now also sets `_vm_interrupt` so long-running VM code can be interrupted.

---

## 11. Tutorial System

**Location:** `ipp/main.py:223-314` (steps), `2017-2059` (commands)

### Structure

- 8 lessons: Variables, Data Types, Lists, Dictionaries, Functions, Control Flow, Classes, Error Handling.
- Each lesson has title, description, example code, hint.
- Auto-advance after successful code execution.
- Commands: `.tutorial`, `.tutorial next`, `.tutorial prev`, `.tutorial end`.

### Limitations

| Limitation | Impact |
|---|---|
| No error guidance | Failed code shows generic error, not tutorial-specific help |
| Cannot restart from a specific lesson | Always starts from lesson 1 |
| Only 8 basic lessons | Missing: ECS, modules, I/O, HTTP, file ops, story mode, OOP patterns |

**✅ FIXED (v2.0.25):** Tutorial now validates user code against per-lesson keyword patterns before advancing. If the code doesn't match the current lesson, a hint is displayed instead of advancing. See `main.py:2793-2810`.

---

## 12. Async/Await Support

**Location:** `ipp/main.py:2548-2574`

### `.async` Command

Wraps an expression in an `__async_task__()` function, defines it in the interpreter, then calls it via `async_run()`.

### Limitations

| Limitation | Impact |
|---|---|
| No `await` keyword in REPL | Cannot await manually — only through `.async` meta command |
| Single-shot only | REPL blocks until async task completes |
| `__async_task__` function leaks into globals | Remains after execution |
| No async iteration | No `for await` support |

---

## 13. File I/O Operations

**Location:** Various in `ipp/main.py`

### REPL Commands

- `.load <file>` — load and execute Ipp source.
- `.save <file>` — write `_cmd_history` as text.
- `.export <file>` — write history as `.ipp` script.
- `.edit` — open last command in an editor.

### Builtins

`read_file`, `write_file`, `append_file`, `file_exists`, `delete_file`, `list_dir`, `mkdir`.

### Limitations

| Limitation | Impact |
|---|---|
| No file-path Tab completion | `.load`, `.save`, `.cd`, `.ls` require typing full paths |
| `.load` doesn't support HTTP URLs | Cannot load remote scripts |
| No file watching | No auto-reload on file change |

---

## 14. Input Encoding & ANSI

**Location:** `ipp/main.py:16-20` (UTF-8), `79-103` (ANSI), `108-117` (detection), `126-149` (helpers)

### UTF-8 Setup

- Windows: replaces `sys.stdout`/`sys.stdin` with `TextIOWrapper(encoding='utf-8', errors='replace')`.
- All `open()` calls in core files use `encoding='utf-8'`.

### ANSI Enablement

- `_enable_windows_ansi()` calls `SetConsoleMode` with `ENABLE_VIRTUAL_TERMINAL_PROCESSING` (0x0004).
- `_ANSI_OK` = result of enablement attempt.
- `_ansi_supported()` checks: TTY, `IPP_COLORS` env, `NO_COLOR` env, `_ANSI_OK`.
- `_USE_ANSI` = `_ansi_supported()`.

### ANSI Helpers

- `_fg(n, t)` — 256-color foreground.
- `_rgb(r, g, b, t)` — 24-bit true color.
- `BOLD`, `DIM`, `ITALIC`.
- All no-op when `_USE_ANSI` is False or not a TTY.

### Strengths

- Comprehensive Windows ANSI support.
- Respects `NO_COLOR` standard.
- Graceful degradation on non-TTY.
- `errors='replace'` for encoding robustness.

### Limitations

| Limitation | Impact |
|---|---|
| `sys.stdout` reassignment can break C extensions | Some C libraries cache the FILE* pointer |
| `_ANSI_OK` computed once at module load | Won't re-detect if console is later upgraded |
| No `TERM` variable checking | 24-bit color codes may be sent to limited terminals |
| `IS_TTY` is static | Not re-checked if output is redirected after start |

---

## 15. LSP Server

**Location:** `ipp/lsp/server.py` (421 lines)

### Advertised Capabilities

- `textDocumentSync` (full document sync)
- Goto-definition
- Find references
- Completions (dot-trigger + paren-trigger)
- Hover
- Document symbols
- Rename

### Strengths

- Full LSP protocol over stdin/stdout.
- Symbol extraction via AST visitor with scope tracking.
- Context-aware completions (after `.`, after keywords `func`/`class`/`for`/`if`/`try`).
- Snippet completions for function/class/loop/try templates.

### Limitations

| Limitation | Impact |
|---|---|
| No goto-definition for imports | Cross-file navigation broken |
| No `didOpen` handler | Only `didChange` is implemented |
| No semantic tokens | No rich IDE highlighting |
| No code actions | No quick-fixes or refactoring |
| No workspace symbol search | Document-level only |
| No `textDocument/formatting` | `.format` exists in REPL but not in LSP |
| **No signature help** | Advertises `(` trigger but no handler |
| Range reporting is coarse | Always `character:0` to `character:100` |
| Error squiggles are line-level only | Diagnostic range is always line 0, col 0-10 |
| No thread safety | Plain dicts without locks |
| No codeLens, no folding ranges | Missing IDE features |

---

## 16. Syntax Highlighter

**Location:** `ipp/runtime/highlighter.py` (511 lines)

### Overall Assessment

The highlighter is the most polished component. Features:
- Token-level lexing via `tokenize_line()` (not regex-based).
- Context tracking (`prev_kw`) for `func`/`class` highlighting.
- 14 token categories with per-theme styling.
- 6 themes with comprehensive color definitions.
- `HighlightSession` class encapsulating prompt_toolkit wiring.
- Static `highlight_line()` for ANSI rendering.
- Auto-suggest from history.
- Bracket/quote matching.

### Remaining Issues

| Issue | Detail |
|---|---|
| Line-scoped | Cannot handle multi-line strings, comments, or expressions |
| No escape-sequence highlighting | `\n`, `\t` etc. inside strings not distinguished |
| No error tokens | Malformed syntax silently consumed |
| `_BUILTIN` set has ECS/scene entries | May not be globally available builtins |
| `_TYPE` set includes error classes | Runtime error objects, not Ipp type names |
| No method highlighting | `obj.method()` only highlights `method` as call target |

---

## 17. Critical Issues Summary

| # | Issue | Location | Severity | Status |
|---|---|---|---|---|---|
| 1 | `.bind` stores key bindings but never processes them | Lines 2279-2286 → 2330-2334 | **Bug** | **FIXED** — bindings expanded before execution |
| 2 | `.session load` uses a temporary Interpreter | Lines 1853-1860 | **Bug** | **ALREADY FIXED** — uses `interp_manager.get_interpreter()` correctly |
| 3 | `.pretty`, `.json`, `.watch` create new Interpreter instances | Lines 1782, 2140, 1924 | **Bug** | **ALREADY FIXED** — all use `interp_manager.get_interpreter()` |
| 4 | `.theme`/`.themes` defined twice; second block is dead code | Lines 1527-1557 + 1987-2015 | **Dead code** | **FIXED** — duplicate block removed |
| 5 | `.vm` switching discards all state | Lines 1118-1126 | **Design limitation** | **FIXED** — state transferred between modes |
| 6 | History includes meta commands (`.help`, `.vars`, etc.) | Line 2797 | **Design flaw** | **FIXED** — meta commands filtered from history |
| 7 | `.break` is explicitly unimplemented stub | Lines 1909-1914 | **Stub** | **FIXED** — stub removed; use `breakpoint()` in code |
| 8 | Tutorial auto-advances on any code, not just tutorial code | Lines 2808-2812 | **Design flaw** | **FIXED** — validated against lesson keywords |
| 9 | No `_check_interrupt()` polling during execution | Lines 43-48 | **Missing feature** | **FIXED** — checked before execution + VM polls every 1000 instructions |
| 10 | Multi-line forced execution at 10 lines is unconditional | Line 3732 | **Fragile** | **FIXED** — shows warning when braces are unbalanced |
| 11 | LSP server has coarse range reporting, no signatureHelp | Lines 82-83 | **Incomplete** | **DEFERRED** — separate system, not part of REPL |
| 12 | `_KW`/`_BUILTINS` sets duplicated across 3 files | main.py, highlighter.py, builtins.py | **Maintenance burden** | **DEFERRED** — needs cross-file refactoring |
| 13 | `.export` includes meta commands in output | Line 2186 | **Design flaw** | **FIXED** — meta commands filtered from export |
| 14 | Macro expansion splits on spaces (breaks quoted args) | Lines 2744-2754 | **Bug** | **FIXED** — uses `shlex.split()` for proper quoting |

### Fixed Items Details

| # | Fix | Files Changed |
|---|---|---|
| 1 | Added binding expansion after alias expansion — `_key_bindings[stripped]` → `stripped` | `ipp/main.py:2330-2334` |
| 4 | Removed duplicate `.theme`/`.themes` handler block (lines 1987-2015) | `ipp/main.py` |
| 5 | `InterpreterManager.switch_to()` now copies `global_env.values` between modes | `ipp/main.py:1118-1135` |
| 6 | `_cmd_history.append(source)` guarded by meta-command filter set | `ipp/main.py:2769-2781` |
| 7 | Removed `.break` stub block entirely | `ipp/main.py` |
| 8 | Tutorial auto-advance checks `source` against per-lesson keyword lists | `ipp/main.py:2793-2810` |
| 9 | `_INTERRUPT_FLAG` checked before execution; `_vm_interrupt` set by Ctrl+C handler; VM polls every 1000 ops | `ipp/main.py:43-48, 2761-2768`, `ipp/vm/vm.py:1510-1515` |
| 10 | Force-execute at 10+ lines shows `C_WARN` message if braces unbalanced | `ipp/main.py:2699-2701` |
| 13 | `.export` filters `_cmd_history` with `if not cmd.startswith('.')` | `ipp/main.py:2296-2298` |
| 14 | Macro arg parsing uses `shlex.split()` instead of `str.split()` | `ipp/main.py:2711-2715` |

---

*Generated from code audit — `ipp/main.py`, `ipp/runtime/highlighter.py`, `ipp/lsp/server.py`*
