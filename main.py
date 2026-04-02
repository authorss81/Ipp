#!/usr/bin/env python3
"""
Ipp Language — Main entry point + Gemini-CLI-inspired REPL
"""

import sys
import os
import re
import shutil
import atexit
import unicodedata
import time
import signal
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.interpreter.interpreter import Interpreter

# ─── Interrupt handling ────────────────────────────────────────────────────────
_INTERRUPT_FLAG = threading.Event()
_INTERRUPT_COUNT = 0

def _handle_interrupt(signum, frame):
    global _INTERRUPT_COUNT
    _INTERRUPT_FLAG.set()
    _INTERRUPT_COUNT += 1
    if _INTERRUPT_COUNT >= 2:
        print(f"\n  {colour(C_ERROR, 'Exiting REPL...')}")
        _disable_interrupt_handling()
        sys.exit(0)
    else:
        print(f"\n  {colour(C_WARN, '<< Interrupt! Press Ctrl+C again to exit REPL')}")

def _check_interrupt():
    """Check if interrupt was requested."""
    if _INTERRUPT_FLAG.is_set():
        _INTERRUPT_FLAG.clear()
        return True
    return False

def _enable_interrupt_handling():
    """Enable SIGINT (Ctrl+C) handling."""
    global _INTERRUPT_COUNT
    _INTERRUPT_COUNT = 0
    if sys.platform != "win32":
        signal.signal(signal.SIGINT, _handle_interrupt)
    else:
        try:
            import ctypes
            handler_defined = [False]
            def handler(dwCtrlType):
                if dwCtrlType == 0:
                    _handle_interrupt(None, None)
                    return True
                return False
            kernel32 = ctypes.windll.kernel32
            HANDLER_ROUTINE = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)
            kernel32.SetConsoleCtrlHandler(HANDLER_ROUTINE(handler), True)
        except Exception:
            pass

def _disable_interrupt_handling():
    """Disable interrupt handling."""
    if sys.platform != "win32":
        signal.signal(signal.SIGINT, signal.SIG_DFL)

VERSION = "1.3.8"

# ─── Windows ANSI enablement ──────────────────────────────────────────────────
# Windows 10 supports ANSI but requires ENABLE_VIRTUAL_TERMINAL_PROCESSING.
# Without this, escape codes print as literal garbage.
def _enable_windows_ansi() -> bool:
    """Enable ANSI escape processing on Windows 10+. Returns True if succeeded."""
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        import ctypes.wintypes
        kernel32 = ctypes.windll.kernel32
        hout = kernel32.GetStdHandle(-11)
        if hout == -1:
            return False
        mode = ctypes.wintypes.DWORD()
        if not kernel32.GetConsoleMode(hout, ctypes.byref(mode)):
            return False
        ENABLE_VTP = 0x0004
        if mode.value & ENABLE_VTP:
            return True
        new_mode = mode.value | ENABLE_VTP
        if kernel32.SetConsoleMode(hout, new_mode):
            return True
        return False
    except Exception as e:
        return False

_ANSI_OK = _enable_windows_ansi()
IS_TTY = sys.stdout.isatty()

# Disable ANSI on Windows by default unless explicitly enabled
# This prevents garbage output on terminals that don't properly support ANSI
_FORCE_ANSI = False

def _check_ansi_support():
    """Check if ANSI codes are actually supported by trying to write one."""
    if not sys.stdout.isatty():
        return False
    try:
        import os
        if hasattr(os, 'getenv') and os.getenv('IPP_COLORS', '').lower() in ('1', 'true', 'yes'):
            # Force enable with virtual terminal processing on Windows
            if sys.platform.startswith('win'):
                import ctypes
                kernel32 = ctypes.windll.kernel32
                h = kernel32.GetStdHandle(-11)
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(h, ctypes.byref(mode))
                mode.value |= 4  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                kernel32.SetConsoleMode(h, mode)
            return True
        return _ANSI_OK and not sys.platform.startswith('win')
    except:
        return False

# ─── ANSI colour helpers ──────────────────────────────────────────────────────
# Only enable colors if we're in a TTY AND ANSI is supported
# On Windows, disable by default unless FORCE_ANSI is set
_USE_ANSI = _check_ansi_support() if not _FORCE_ANSI else True

def _fg(n, t):
    if not _USE_ANSI or not IS_TTY:
        return t
    return f"\033[38;5;{n}m{t}\033[0m"

def _rgb(r, g, b, t):
    if not _USE_ANSI or not IS_TTY:
        return t
    return f"\033[38;2;{r};{g};{b}m{t}\033[0m"

def BOLD(t):
    if not _USE_ANSI or not IS_TTY:
        return t
    return f"\033[1m{t}\033[0m"

def DIM(t):
    if not _USE_ANSI or not IS_TTY:
        return t
    return f"\033[2m{t}\033[0m"

def ITALIC(t):
    if not _USE_ANSI or not IS_TTY:
        return t
    return f"\033[3m{t}\033[0m"

# ── Palette ───────────────────────────────────────────────────────────────────
C_PROMPT  = lambda t: _rgb(100, 200, 255, t)
C_CONT    = lambda t: _rgb(100, 140, 200, t)
C_RESULT  = lambda t: _rgb(180, 255, 180, t)
C_ERROR   = lambda t: _rgb(255, 100, 100, t)
C_WARN    = lambda t: _rgb(255, 200,  80, t)
C_OK      = lambda t: _rgb( 80, 220, 120, t)
C_CMD     = lambda t: _rgb(150, 120, 255, t)
C_TYPE    = lambda t: _rgb(255, 160,  80, t)
C_KW      = lambda t: _rgb(100, 200, 255, t)
C_STR     = lambda t: _rgb(150, 255, 150, t)
C_NUM     = lambda t: _rgb(255, 180, 100, t)
C_COMMENT = lambda t: _rgb(120, 120, 140, t)
C_FN      = lambda t: _rgb(130, 170, 255, t)
C_BOOL    = lambda t: _rgb(220, 130, 255, t)
C_HEADER  = lambda t: _rgb( 80, 200, 255, t)
C_LOGO1   = lambda t: _fg(51, t)
C_LOGO2   = lambda t: _fg(45, t)
C_LOGO3   = lambda t: _fg(39, t)
C_LOGO4   = lambda t: _fg(33, t)
C_LOGO5   = lambda t: _fg(27, t)

def colour(fn, text):
    return fn(text)   # lambdas already no-op when IS_TTY=False

def strip_ansi(s):
    return re.sub(r'\033\[[0-9;]*m', '', s)

def visible_len(s):
    plain = strip_ansi(s)
    return sum(2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in plain)

def pad_to(s, width):
    return s + ' ' * max(0, width - visible_len(s))

# ─── Syntax highlighter ───────────────────────────────────────────────────────
_KEYWORDS = frozenset([
    "var","let","func","class","if","else","elif","for","while",
    "match","case","default","try","catch","finally","throw","return",
    "break","continue","import","as","in","nil","true","false",
    "self","this","enum","static","repeat","until","and","or","not","with",
])
_BUILTINS = frozenset([
    "print","len","type","range","abs","min","max","sum","round",
    "floor","ceil","sqrt","pow","sin","cos","tan","log","input",
    "str","int","float","bool","randint","random","keys","values",
    "items","contains","split","join","upper","lower","strip",
    "replace","find","starts_with","ends_with","assert","exit",
])

def highlight(code: str) -> str:
    if not _USE_ANSI:
        return code
    lines = code.split('\n')
    out = []
    for line in lines:
        # comment
        ci = line.find('#')
        comment = ''
        if ci >= 0:
            comment = colour(C_COMMENT, line[ci:])
            line = line[:ci]

        # strings
        def repl_str(m):
            return colour(C_STR, m.group())
        line = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', repl_str, line)
        line = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", repl_str, line)

        # booleans / nil
        line = re.sub(r'\b(true|false|nil)\b',
                      lambda m: colour(C_BOOL, m.group()), line)
        # numbers
        line = re.sub(r'\b(0[xXoObB][0-9a-fA-F_]+|\d[\d_]*\.?\d*)\b',
                      lambda m: colour(C_NUM, m.group()), line)
        # keywords
        line = re.sub(r'\b(' + '|'.join(_KEYWORDS) + r')\b',
                      lambda m: colour(C_KW, m.group()), line)
        # builtins
        line = re.sub(r'\b(' + '|'.join(_BUILTINS) + r')\b',
                      lambda m: colour(C_FN, m.group()), line)
        # user function calls
        line = re.sub(r'\b([a-zA-Z_]\w*)\s*(?=\()',
                      lambda m: (colour(C_FN, m.group(1)) + m.group()[len(m.group(1)):]),
                      line)
        out.append(line + comment)
    return '\n'.join(out)

# ─── Banner ───────────────────────────────────────────────────────────────────
# Use Unicode box-drawing on terminals that support it, plain ASCII otherwise
def _supports_unicode():
    """Check if stdout can render Unicode box-drawing characters."""
    try:
        enc = (getattr(sys.stdout, 'encoding', None) or 'ascii').lower()
        return enc in ('utf-8', 'utf8', 'utf-16', 'cp65001')
    except Exception:
        return False

_UNI = _supports_unicode()

if _UNI:
    _LOGO_LINES = [
        ("  IPP  LANG  ",    C_LOGO1),   # compact safe label
        ("  +-----------+  ", C_LOGO2),
        ("  | Ipp v{v}  |  ".format(v=VERSION), C_LOGO3),
        ("  +-----------+  ", C_LOGO4),
    ]
    _LOGO_FULL = [
        ("  ██╗██████╗ ██████╗  ", C_LOGO1),
        ("  ██║██╔══██╗██╔══██╗ ", C_LOGO2),
        ("  ██║██████╔╝██████╔╝ ", C_LOGO3),
        ("  ██║██╔═══╝ ██╔═══╝  ", C_LOGO4),
        ("  ██║██║     ██║      ", C_LOGO5),
        ("  ╚═╝╚═╝     ╚═╝      ", C_LOGO1),
    ]
    _LOGO_LINES = _LOGO_FULL
else:
    # Pure ASCII logo for old Windows console
    _LOGO_LINES = [
        ("  ###  ######  ######  ", C_LOGO1),
        ("  ##   ##  ##  ##  ##  ", C_LOGO2),
        ("  ##   ######  ######  ", C_LOGO3),
        ("  ##   ##      ##      ", C_LOGO4),
        ("  ###  ##      ##      ", C_LOGO5),
    ]

def _bar(ch=None, w=58):
    if ch is None:
        ch = '-' if not _UNI else '─'
    return colour(C_HEADER, ch * w)

def print_banner():
    W = shutil.get_terminal_size((80, 24)).columns
    pad = max(0, (W - 62) // 2)
    sp = ' ' * pad

    print()
    for text, clr in _LOGO_LINES:
        print(sp + colour(clr, BOLD(text)))
    print()
    bar = _bar(w=54)
    print(sp + bar)
    tag = colour(C_HEADER, BOLD(f"  Ipp  v{VERSION}"))
    sub = DIM("  A scripting language for game development")
    print(sp + tag)
    print(sp + sub)
    print(sp + bar)
    print()
    sep = "   "
    parts = [
        colour(C_CMD, ".help") + " " + DIM("commands"),
        colour(C_CMD, ".vars") + " " + DIM("vars"),
        colour(C_CMD, ".fns") + " " + DIM("fns"),
        colour(C_CMD, "exit")  + " " + DIM("quit"),
    ]
    print(sp + "  " + sep.join(parts))
    print()
    hint = DIM("  .builtins .modules .history .types Tab")
    print(sp + hint)
    print()
    if not _USE_ANSI:
        if not sys.stdout.isatty():
            print(sp + DIM("  (colors disabled - stdout not a terminal)"))
        elif not _ANSI_OK:
            print(sp + DIM("  (colors disabled - ANSI not supported)"))
        print(sp + DIM("  Use .colors on to force colors"))
    else:
        print(sp + colour(C_OK, "  (colors enabled)"))
    print()

# ─── Readline / autocomplete ──────────────────────────────────────────────────
try:
    import readline
    HAS_RL = True
except ImportError:
    HAS_RL = False

class IppCompleter:
    def __init__(self, interp):
        self.interp = interp
        self.matches = []

    def complete(self, text, state):
        if state == 0:
            buf = readline.get_line_buffer() if HAS_RL else text
            dot = re.match(r'.*?(\w+)\.([\w]*)$', buf)
            if dot:
                obj_name, prefix = dot.group(1), dot.group(2)
                self.matches = [m for m in self._members(obj_name) if m.startswith(prefix)]
            else:
                cands = set(list(_KEYWORDS) + list(_BUILTINS)) | self._globals()
                self.matches = sorted(c for c in cands if c.startswith(text))
        try:
            return self.matches[state]
        except IndexError:
            return None

    def _globals(self):
        names = set()
        if hasattr(self.interp, 'global_env'):
            env = self.interp.global_env
            while env:
                if hasattr(env, 'values'):
                    names |= env.values.keys()
                env = env.parent
        return names

    def _members(self, obj_name):
        try:
            env = self.interp.global_env
            obj = None
            while env:
                if hasattr(env, 'values') and obj_name in env.values:
                    obj = env.values[obj_name]; break
                env = env.parent
            if obj is None: return []
            m = []
            if hasattr(obj, 'fields'): m += list(obj.fields)
            if hasattr(obj, 'ipp_class') and hasattr(obj.ipp_class, 'methods'):
                m += list(obj.ipp_class.methods)
            if hasattr(obj, '_env') and hasattr(obj._env, 'values'):
                m += list(obj._env.values)
            return sorted(set(m))
        except Exception:
            return []

def setup_readline(interp):
    if not HAS_RL: return
    try:
        hdir = os.path.join(os.path.expanduser("~"), ".ipp")
        os.makedirs(hdir, exist_ok=True)
        hfile = os.path.join(hdir, "history")
        try: readline.read_history_file(hfile)
        except FileNotFoundError: pass
        readline.set_history_length(2000)
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set completion-ignore-case on")
        readline.set_completer_delims(" \t\n`~!@#$%^&*()-=+[]{}|;:',.<>?/")
        comp = IppCompleter(interp)
        readline.set_completer(comp.complete)
        atexit.register(readline.write_history_file, hfile)
        return comp
    except Exception:
        return None

# ─── Brace balance check ──────────────────────────────────────────────────────
def _balanced(src: str) -> bool:
    stack = []
    in_str = in_sq = False
    i = 0
    while i < len(src):
        c = src[i]
        if c == '\\' and (in_str or in_sq):
            i += 2; continue
        if c == '"' and not in_sq: in_str = not in_str
        elif c == "'" and not in_str: in_sq = not in_sq
        elif not in_str and not in_sq:
            if c in '([{': stack.append(c)
            elif c in ')]}':
                if not stack: return False
                opens = {'(':')', '[':']', '{':'}'}
                if opens[stack[-1]] != c: return False
                stack.pop()
        i += 1
    return len(stack) == 0

def _needs_more(src: str) -> bool:
    src = src.strip()
    if not src: return False
    if not _balanced(src): return True
    # ends with open brace or continuation keywords
    if re.search(r'[\{,]\s*$', src): return True
    return False

# ─── Function color palette (unique colors for each function) ─────────────────
# Each function gets a unique color. The format is:
# <function NAME at 0xADDRESS> where NAME is purple and the rest is colorful
_FN_PALETTE = [
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(200, 120, 255),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(120, 200, 255),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(255, 180, 120),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(120, 255, 180),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(255, 120, 180),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(180, 255, 255),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(255, 255, 120),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(255, 150, 200),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(150, 255, 150),
    (lambda r, g, b: lambda t: _rgb(r, g, b, t))(200, 200, 255),
]

_fn_color_map = {}
_fn_color_idx = 0

def _get_fn_color(fn_id):
    global _fn_color_idx
    if fn_id not in _fn_color_map:
        _fn_color_map[fn_id] = _FN_PALETTE[_fn_color_idx % len(_FN_PALETTE)]
        _fn_color_idx += 1
    return _fn_color_map[fn_id]

def _reset_fn_colors():
    global _fn_color_map, _fn_color_idx
    _fn_color_map = {}
    _fn_color_idx = 0

# ─── Help & meta commands ──────────────────────────────────────────────────────
def _section(title):
    print()
    print("  " + colour(C_CMD, BOLD(f" {title} ")))
    div = '-' * 50 if not _UNI else '─' * 50
    print("  " + colour(DIM, div))

def print_help():
    _section("Commands")
    cmds = [
        (".help",       "Show this help"),
        (".vars",       "List user-defined variables"),
        (".fns",        "List user-defined functions"),
        (".builtins",   "List all built-in functions"),
        (".modules",    "List available modules"),
        (".history",    "Show command history (.history N for N lines)"),
        (".colors",     "Toggle colors (.colors on/off)"),
        (".vm",         "Switch interpreter (.vm interpreter/vm)"),
        (".clear",      "Reset the session"),
        (".types",      "Show the type system"),
        (".version",    f"Show version (v{VERSION})"),
        ("exit / quit", "Exit the REPL"),
    ]
    for cmd, desc in cmds:
        c_cmd  = colour(C_CMD, cmd.ljust(16))
        c_desc = colour(DIM, desc)
        print(f"    {c_cmd} {c_desc}")

    _section("REPL Tools (v1.3.7)")
    tools = [
        (".load <file>",    "Load and execute file (keeps variables)"),
        (".save <file>",    "Save command history to file"),
        (".doc <fn>",       "Show builtin documentation"),
        (".time <expr>",    "Benchmark expression"),
        (".which <name>",   "Check if builtin/var/function"),
        (".last / $_",      "Reference last result"),
        (".undo",           "Undo last command"),
        (".edit",           "Edit last command in editor"),
        (".profile",        "Profile last command"),
        (".alias n cmd",    "Create command alias"),
    ]
    for cmd, desc in tools:
        c_cmd  = colour(C_CMD, cmd.ljust(16))
        c_desc = colour(DIM, desc)
        print(f"    {c_cmd} {c_desc}")

    # Windows color warning
    if sys.platform.startswith('win') and _USE_ANSI:
        print()
        print("  " + colour(C_WARN, "Note: If you see garbage numbers/escape codes, run .colors off"))

    _section("Quick Reference")
    snippets = [
        ("var x = 10",                   "mutable variable"),
        ("let y = 20",                   "immutable binding"),
        ("x += 5",                       "compound assignment"),
        ("func add(a, b) { return a+b }","function"),
        ("var f = func(a) => a*2",       "lambda"),
        ("class Dog : Animal { }",       "class with inheritance"),
        ("2 ** 10",                      "power operator"),
        ("0xFF & 0x0F",                  "hex literals & bitwise"),
        ('var s = "Hi\\nWorld"',         "escape sequences"),
        ("[x*x for x in 1..5]",          "list comprehension"),
        ('nil ?? "default"',             "nullish coalescing"),
        ("try { } catch e { }",          "error handling"),
        ("import \"module.ipp\" as m",   "import local module"),
        ("print(sha256(\"hello\"))",     "use built-in functions"),
        ("1 + \\",                       "multiline (end with \\)"),
    ]
    for code, note in snippets:
        print(f"    {highlight(code.ljust(36))} {colour(DIM, note)}")
    print()

def print_types():
    _section("Type System")
    types_info = [
        ("number",    "42, 3.14, 0xFF, 0b1010"),
        ("string",    '"hello", escape \\n \\t supported'),
        ("bool",      "true / false"),
        ("nil",       "null value"),
        ("list",      "[1, 2, 3]"),
        ("dict",      '{"key": val}'),
        ("tuple",     "(1, 2, 3)"),
        ("function",  "first-class, closures, lambdas"),
        ("class",     "OOP with inheritance"),
        ("enum",      "enum Direction { UP, DOWN }"),
    ]
    for t, desc in types_info:
        print(f"    {colour(C_TYPE, t.ljust(12))} {colour(DIM, desc)}")
    print()

def _is_ipp_function(val):
    return type(val).__name__ == 'IppFunction'

def show_vars(interp):
    _section("User Variables")
    try:
        from ipp.runtime.builtins import BUILTINS as _RUNTIME_BUILTINS
    except ImportError:
        _RUNTIME_BUILTINS = set()
    
    env = interp.global_env
    all_vars = {}
    while env:
        if hasattr(env, 'values'):
            for k, v in env.values.items():
                if k not in all_vars and not k.startswith('_'):
                    all_vars[k] = v
        env = env.parent

    user_vars = {k: v for k, v in all_vars.items()
                 if k not in _RUNTIME_BUILTINS and not callable(v) and not _is_ipp_function(v)}

    if not user_vars:
        print(f"    {colour(DIM, '(none defined yet)')}")
    else:
        for name, val in sorted(user_vars.items()):
            vt = type(val).__name__
            if hasattr(val, 'cls'):  vt = val.cls.name
            elif hasattr(val, 'name') and hasattr(val, 'methods'): vt = 'class'
            val_str = _format_val(val)
            if len(strip_ansi(val_str)) > 40: val_str = _format_val(val, truncate=True)
            print(f"    {colour(C_STR, name.ljust(16))} "
                  f"{colour(C_TYPE, vt.ljust(10))} "
                  f"{val_str}")
    print()

def show_fns(interp):
    _section("User Functions")
    try:
        from ipp.runtime.builtins import BUILTINS as _RUNTIME_BUILTINS
    except ImportError:
        _RUNTIME_BUILTINS = set()
    
    env = interp.global_env
    all_items = {}
    while env:
        if hasattr(env, 'values'):
            for k, v in env.values.items():
                if k not in all_items and not k.startswith('_'):
                    all_items[k] = v
        env = env.parent

    user_fns = {k: v for k, v in all_items.items()
                if k not in _RUNTIME_BUILTINS and (callable(v) or _is_ipp_function(v))}

    if not user_fns:
        print(f"    {colour(DIM, '(none defined yet)')}")
    else:
        for name, val in sorted(user_fns.items()):
            fn_display = _format_fn_display(id(val), name, id(val))
            print(f"    {colour(C_STR, name.ljust(16))} {fn_display}")
    print()

def show_builtins():
    _section("Built-in Functions")
    try:
        from ipp.runtime.builtins import BUILTINS
    except ImportError:
        print(f"    {colour(DIM, '(unable to load builtins)')}")
        print()
        return
    
    for name in sorted(BUILTINS.keys()):
        fn_display = _format_builtin_display(name)
        print(f"    {colour(C_STR, name.ljust(16))} {fn_display}")
    print()

def show_modules():
    _section("Available Modules")
    try:
        from ipp.runtime.builtins import BUILTINS
    except ImportError:
        print(f"    {colour(DIM, '(unable to load modules)')}")
        print()
        return
    
    mod_groups = {
        "I/O": ["print", "input"],
        "Type Conversion": ["str", "int", "float", "bool", "to_number", "to_string", "to_int", "to_float", "to_bool"],
        "Math": ["abs", "min", "max", "sum", "round", "floor", "ceil", "sqrt", "pow", "pi", "e",
                 "sin", "cos", "tan", "log", "log10", "degrees", "radians", "asin", "acos", "atan", "atan2"],
        "Random": ["random", "randint", "randfloat", "choice", "shuffle"],
        "Collections": ["len", "range", "keys", "values", "items", "contains"],
        "String": ["upper", "lower", "strip", "replace", "find", "starts_with", "ends_with", "split", "join"],
        "Control": ["assert", "exit"],
    }
    
    for group, names in mod_groups.items():
        available = [n for n in names if n in BUILTINS]
        if available:
            print(f"  {colour(C_HEADER, group + ':')}")
            for name in sorted(available):
                fn_display = _format_builtin_display(name)
                print(f"    {colour(C_STR, name.ljust(16))} {fn_display}")
            print()
    print()

# ─── VM Interpreter Wrapper ─────────────────────────────────────────────────────
class VMInterpreter:
    """Wrapper around VM to provide Interpreter-like interface for REPL."""
    def __init__(self):
        from ipp.vm import VM
        self.vm = VM()
        self.return_value = None
        self.last_value = None
        self.current_file = None
    
    def run(self, ast):
        from ipp.vm.compiler import compile_ast
        from ipp.parser.ast import Program, ExprStmt, ReturnStmt
        wrapped = self._wrap_for_vm(ast)
        chunk = compile_ast(wrapped)
        self.vm.reset()
        result = self.vm.run(chunk)
        self.return_value = result
        self.last_value = result
    
    def _wrap_for_vm(self, ast):
        """Wrap expression statements in return for VM to return values."""
        from ipp.parser.ast import Program, ExprStmt, ReturnStmt
        if not isinstance(ast, Program):
            return ast
        new_stmts = []
        for stmt in ast.statements:
            if isinstance(stmt, ExprStmt):
                new_stmts.append(ReturnStmt(value=stmt.expression))
            else:
                new_stmts.append(stmt)
        return Program(statements=new_stmts)

# ─── Interpreter Manager ────────────────────────────────────────────────────────
class InterpreterManager:
    """Manages switching between interpreter and VM."""
    def __init__(self):
        self.interpreter = Interpreter()
        self.vm_interpreter = VMInterpreter()
        self.use_vm = False
    
    def get_interpreter(self):
        return self.vm_interpreter if self.use_vm else self.interpreter
    
    def switch_to(self, mode):
        if mode == 'vm':
            self.use_vm = True
            return "Switched to VM interpreter"
        elif mode == 'interpreter':
            self.use_vm = False
            return "Switched to interpreter"
        else:
            return f"Unknown mode: {mode}. Use .vm interpreter or .vm vm"
    
    def reset(self):
        self.interpreter = Interpreter()
        self.vm_interpreter = VMInterpreter()
    
    @property
    def global_env(self):
        return self.get_interpreter().interpreter.global_env if self.use_vm else self.get_interpreter().global_env

# ─── Output formatter ─────────────────────────────────────────────────────────
C_FN_PURPLE = lambda t: _rgb(180, 100, 255, t)  # Purple for <function and >
C_FN_BLUE = lambda t: _rgb(130, 170, 255, t)    # Blue for function NAME
C_FN_CYAN = lambda t: _rgb(100, 200, 200, t)    # Cyan for "at"
C_FN_ORANGE = lambda t: _rgb(255, 180, 100, t)   # Orange for 0x...

def _format_fn_display(fn_id, name, addr=None):
    """Format function display with UNIQUE color per function.
    Used for user-defined functions and function output."""
    fn_color = _get_fn_color(fn_id)  # unique color for NAME
    addr_str = f" at {C_FN_ORANGE(f'0x{addr:X}')}" if addr is not None else ""
    return (
        C_FN_PURPLE("<function ") +
        fn_color(name) +
        C_FN_CYAN(addr_str) +
        C_FN_PURPLE(">")
    )

def _format_builtin_display(name):
    """Format builtin function display with FIXED colors.
    Used for .builtins and .modules commands."""
    return (
        C_FN_PURPLE("<function ") +
        C_FN_BLUE(name) +
        C_FN_PURPLE(">")
    )

def _format_val(val, truncate=False):
    if val is None:            return colour(DIM, 'nil')
    if isinstance(val, bool):  return colour(C_BOOL, 'true' if val else 'false')
    if isinstance(val, (int, float)):
        s = str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
        return colour(C_NUM, s)
    if isinstance(val, str):
        s = repr(val)
        if truncate and len(s) > 40: s = s[:37] + '...'
        return colour(C_STR, s)
    if _is_ipp_function(val):
        fn_id = id(val)
        return _format_fn_display(fn_id, "ipp_function", fn_id)
    if callable(val):
        fn_id = id(val)
        if hasattr(val, '__name__'):
            return _format_fn_display(fn_id, val.__name__, fn_id)
        return _format_fn_display(fn_id, "function", fn_id)
    s = str(val)
    if truncate and len(s) > 40: s = s[:37] + '...'
    return colour(C_RESULT, s)

def format_output(val) -> str:
    return _format_val(val)

# ─── REPL spinner (simple, no threads) ───────────────────────────────────────
_SPINNER = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷']

# ─── Main REPL ────────────────────────────────────────────────────────────────
def run_repl():
    interp_manager = InterpreterManager()
    interp = interp_manager.get_interpreter()
    setup_readline(interp)
    print_banner()
    _enable_interrupt_handling()

    buf = []
    line_num = 0
    _reset_fn_colors()
    _cmd_history = []
    _last_result = None
    _env_snapshots = []  # For .undo
    _aliases = {}  # For .alias

    def show_history(n=20):
        if not _cmd_history:
            print(f"    {colour(DIM, '(no history yet)')}")
            return
        start = max(0, len(_cmd_history) - n)
        for i, cmd in enumerate(_cmd_history[start:], start + 1):
            display = cmd if len(cmd) <= 60 else cmd[:57] + '...'
            print(f"    {colour(DIM, f'{i:4}:')} {display}")

    while True:
        try:
            if buf:
                dot = '...' if not _UNI else '···'
                prompt_txt = colour(C_CONT, f"  {dot} ")
            else:
                arrow = '>>>' if not _UNI else '❯'
                prompt_txt = colour(C_PROMPT, f"  {arrow} ")

            raw = input(prompt_txt)

        except KeyboardInterrupt:
            print()
            if buf:
                buf.clear()
                print(f"  {colour(C_WARN, '<< Buffer cleared')}")
            else:
                print(f"  {colour(DIM, 'Ctrl+C — type exit to quit')}")
            continue
        except EOFError:
            print()
            print(f"  {colour(C_OK, 'Goodbye!')}")
            break

        stripped = raw.strip()
        
        # ── Meta commands (only at fresh prompt) ──────────────────────
        if not buf:
            if stripped in ('exit', 'exit()', 'quit', '.exit', '.quit'):
                print(f"  {colour(C_OK, 'Goodbye!')}")
                break
            if stripped == '.help':        print_help();         continue
            if stripped == '.types':       print_types();         continue
            if stripped == '.vars':         show_vars(interp);    continue
            if stripped == '.fns':          show_fns(interp);    continue
            if stripped == '.builtins':     show_builtins();      continue
            if stripped == '.modules':      show_modules();       continue
            if stripped == '.version':      print(f"  Ipp v{VERSION}"); continue
            if stripped in ('.clear', 'clear()'):
                buf.clear()
                interp_manager.reset()
                interp = interp_manager.get_interpreter()
                setup_readline(interp)
                _reset_fn_colors()
                _cmd_history.clear()
                print(f"  {colour(C_WARN, '>> Session cleared')}")
                continue
            # .vm interpreter/vm command
            m = re.match(r'\.vm\s+(interpreter|vm)$', stripped)
            if m:
                msg = interp_manager.switch_to(m.group(1))
                mode_name = colour(C_OK, m.group(1).upper()) if m.group(1) == 'vm' else colour(C_HEADER, 'INTERPRETER')
                print(f"  {colour(C_OK, '>>')} {msg} ({mode_name})")
                interp = interp_manager.get_interpreter()
                setup_readline(interp)
                continue
            # .vm without args - show current mode
            if stripped == '.vm':
                mode = colour(C_OK, 'VM') if interp_manager.use_vm else colour(C_HEADER, 'INTERPRETER')
                print(f"  Current interpreter: {mode}")
                continue
            # .history command with optional number
            m = re.match(r'\.history\s*(\d+)?$', stripped)
            if m:
                n = int(m.group(1)) if m.group(1) else 20
                show_history(n)
                continue
            # .colors on/off command
            m = re.match(r'\.colors\s+(on|off)$', stripped)
            if m:
                global _USE_ANSI
                if m.group(1) == 'on':
                    _USE_ANSI = True
                    print(f"  {colour(C_OK, 'Colors enabled')}")
                else:
                    _USE_ANSI = False
                    print(f"  {colour(C_WARN, 'Colors disabled')}")
                continue

            # ── v1.3.7 REPL Enhancements ──────────────────────────────

            # .load <file> — Load and execute file in current session
            m = re.match(r'\.load\s+(.+)$', stripped)
            if m:
                filepath = m.group(1).strip().strip('"').strip("'")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        source = f.read()
                    tokens = tokenize(source)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    interp.run(ast)
                    val = interp.return_value if interp.return_value is not None else interp.last_value
                    interp.return_value = None
                    interp.last_value = None
                    if val is not None:
                        print(f"  {colour(DIM, '→')} {format_output(val)}")
                    _cmd_history.append(f".load {filepath}")
                    print(f"  {colour(C_OK, f'Loaded {filepath}')}")
                except FileNotFoundError:
                    print(f"  {colour(C_ERROR, f'File not found: {filepath}')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .save <file> — Save session history to file
            m = re.match(r'\.save\s+(.+)$', stripped)
            if m:
                filepath = m.group(1).strip().strip('"').strip("'")
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(_cmd_history))
                    print(f"  {colour(C_OK, f'Saved {len(_cmd_history)} commands to {filepath}')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, f'Failed to save: {e}')}")
                continue

            # .doc <function> — Show docstring/help for builtin
            m = re.match(r'\.doc\s+(\w+)$', stripped)
            if m:
                fn_name = m.group(1)
                try:
                    from ipp.runtime.builtins import BUILTINS
                    if fn_name in BUILTINS:
                        fn = BUILTINS[fn_name]
                        doc = fn.__doc__ or "No documentation available."
                        print(f"  {colour(C_CMD, fn_name)}: {doc}")
                    else:
                        print(f"  {colour(C_WARN, f'{fn_name} is not a builtin function')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .time <expr> — Benchmark expression
            m = re.match(r'\.time\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                try:
                    tokens = tokenize(expr)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    t_start = time.perf_counter()
                    interp.run(ast)
                    elapsed = time.perf_counter() - t_start
                    val = interp.return_value if interp.return_value is not None else interp.last_value
                    interp.return_value = None
                    interp.last_value = None
                    if val is not None:
                        print(f"  {colour(DIM, '→')} {format_output(val)}")
                    print(f"  {colour(DIM, f'  {elapsed*1000:.2f}ms')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .which <name> — Show if name is builtin/variable/function
            m = re.match(r'\.which\s+(\w+)$', stripped)
            if m:
                name = m.group(1)
                try:
                    from ipp.runtime.builtins import BUILTINS
                    if name in BUILTINS:
                        print(f"  {colour(C_OK, name)} is a {colour(C_CMD, 'builtin function')}")
                    elif name in interp_manager.global_env:
                        val = interp_manager.global_env[name]
                        if callable(val):
                            print(f"  {colour(C_OK, name)} is a {colour(C_CMD, 'user-defined function')}")
                        else:
                            print(f"  {colour(C_OK, name)} is a {colour(C_CMD, 'variable')} = {format_output(val)}")
                    else:
                        print(f"  {colour(C_WARN, f'{name} not found')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .last / $_ — Reference the last result
            if stripped in ('.last', '$_'):
                if _last_result is not None:
                    print(f"  {format_output(_last_result)}")
                else:
                    print(f"  {colour(DIM, '(no last result)')}")
                continue

            # .undo — Undo last command's effect
            if stripped == '.undo':
                if _env_snapshots:
                    snapshot = _env_snapshots.pop()
                    interp = interp_manager.get_interpreter()
                    interp.global_env.values.clear()
                    interp.global_env.values.update(snapshot)
                    print(f"  {colour(C_OK, 'Last command undone')}")
                else:
                    print(f"  {colour(DIM, '(nothing to undo)')}")
                continue

            # .alias <name> <cmd> — Create custom REPL command alias
            m = re.match(r'\.alias\s+(\w+)\s+(.+)$', stripped)
            if m:
                alias_name = m.group(1)
                alias_cmd = m.group(2).strip()
                _aliases[alias_name] = alias_cmd
                print(f"  {colour(C_OK, f'Alias: .{alias_name} → {alias_cmd}')}")
                continue

            # Check if input is an alias
            alias_match = re.match(r'\.(\w+)(.*)', stripped)
            if alias_match:
                alias_name = alias_match.group(1)
                if alias_name in _aliases:
                    stripped = _aliases[alias_name] + alias_match.group(2)

            # .edit — Open last command in editor
            if stripped == '.edit':
                if not _cmd_history:
                    print(f"  {colour(DIM, '(no history to edit)')}")
                else:
                    editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'notepad'))
                    last_cmd = _cmd_history[-1]
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.ipp', delete=False) as f:
                        f.write(last_cmd)
                        tmpfile = f.name
                    import subprocess
                    subprocess.run([editor, tmpfile])
                    with open(tmpfile, 'r') as f:
                        edited = f.read()
                    os.unlink(tmpfile)
                    if edited.strip():
                        stripped = edited.strip()
                    else:
                        continue

            # .profile — Profile last command
            if stripped == '.profile':
                if not _cmd_history:
                    print(f"  {colour(DIM, '(no history to profile)')}")
                else:
                    last_cmd = _cmd_history[-1]
                    try:
                        import cProfile
                        import pstats
                        import io
                        tokens = tokenize(last_cmd)
                        ast = parse(tokens)
                        interp = interp_manager.get_interpreter()
                        pr = cProfile.Profile()
                        pr.enable()
                        interp.run(ast)
                        pr.disable()
                        s = io.StringIO()
                        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
                        ps.print_stats(10)
                        print(s.getvalue())
                    except Exception as e:
                        print(f"  {colour(C_ERROR, str(e))}")
                continue

        if not stripped and not buf:
            continue

        # Check for line continuation with \
        if raw.rstrip('\r\n').endswith('\\'):
            # Keep the backslash - it signals line continuation
            buf.append(raw.rstrip('\r\n'))
            continue

        buf.append(raw)
        source = '\n'.join(buf)

        # Multi-line paste detection: if source has multiple complete statements
        # Auto-execute if it looks like a paste (multiple newlines, no continuation)
        if len(buf) > 1 and not _needs_more(source):
            pass  # Will execute normally

        if _needs_more(source):
            continue

        # ── Execute ───────────────────────────────────────────────────
        # Check for pending interrupts before execution
        if _check_interrupt():
            print(f"  {colour(C_WARN, '<< Interrupted - command cancelled')}")
            buf.clear()
            continue

        interp = interp_manager.get_interpreter()
        t0 = time.perf_counter()
        
        # Save env snapshot for .undo
        snapshot = dict(interp.global_env.values)
        _env_snapshots.append(snapshot)
        if len(_env_snapshots) > 50:
            _env_snapshots.pop(0)
        
        exec_result = [None]  # Container for result and exception
        exec_done = threading.Event()
        
        def run_in_thread():
            try:
                tokens = tokenize(source)
                ast    = parse(tokens)
                interp.run(ast)
                val = interp.return_value if interp.return_value is not None else interp.last_value
                interp.return_value = None
                interp.last_value   = None
                exec_result[0] = ('ok', val)
            except Exception as e:
                exec_result[0] = ('error', e)
            finally:
                exec_done.set()
        
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()
        
        while thread.is_alive():
            thread.join(timeout=0.1)  # Check every 100ms
            if _check_interrupt():
                print(f"\n  {colour(C_WARN, '<< Interrupted!')}")
                buf.clear()
                thread.join(timeout=0.1)  # Let it finish
                interp_manager.reset()
                interp = interp_manager.get_interpreter()
                setup_readline(interp)
                exec_done.set()  # Ensure we exit the loop
                break
        
        if not _INTERRUPT_FLAG.is_set() and exec_result[0]:
            result_type, result_val = exec_result[0]
            elapsed = time.perf_counter() - t0
            
            if result_type == 'ok':
                _cmd_history.append(source)
                if result_val is not None:
                    fmted = format_output(result_val)
                    ms_str = colour(DIM, f"  {elapsed*1000:.1f}ms")
                    arrow2 = '->' if not _UNI else '→'
                    print(f"  {colour(DIM, arrow2)} {fmted}{ms_str}")
                    _last_result = result_val
                buf.clear()
                line_num += 1
            else:
                buf.clear()
                e = result_val
                if isinstance(e, (SyntaxError, RuntimeError)):
                    msg = str(e)
                    m = re.search(r'line (\d+)', msg)
                    loc = f" {colour(DIM, f'(line {m.group(1)})')}" if m else ''
                    cross = 'x' if not _UNI else '✗'
                    print(f"  {colour(C_ERROR, cross)} {colour(C_ERROR, msg)}{loc}")
                else:
                    cross = 'x' if not _UNI else '✗'
                    print(f"  {colour(C_ERROR, cross)} {colour(C_ERROR, str(e))}")

# ─── File runner ──────────────────────────────────────────────────────────────
def run_file(path: str) -> int:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"{colour(C_ERROR, '[Error]')} File not found: {path}")
        return 1

    try:
        tokens = tokenize(source)
        ast    = parse(tokens)
        interp = Interpreter()
        interp.current_file = os.path.abspath(path)
        interp.run(ast)
        return 0
    except Exception as e:
        print(f"{colour(C_ERROR, '[Error]')} {e}")
        return 1

def check_file(path: str) -> int:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            src = f.read()
        tokenize(src); parse(tokenize(src))
        print(f"{colour(C_OK, '✓')} Syntax OK: {path}")
        return 0
    except Exception as e:
        print(f"{colour(C_ERROR, '✗')} {e}")
        return 1

def lint_file(path: str) -> int:
    issues = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            src = f.read()
    except FileNotFoundError:
        print(f"{colour(C_ERROR, '[Error]')} File not found: {path}")
        return 1

    for i, line in enumerate(src.split('\n'), 1):
        if len(line.rstrip()) > 120:
            issues.append(f"line {i}: line too long ({len(line.rstrip())} > 120)")
        if '\t' in line:
            issues.append(f"line {i}: use spaces not tabs")
    try:
        tokenize(src); parse(tokenize(src))
    except Exception as e:
        issues.append(f"syntax: {e}")

    if issues:
        for iss in issues:
            print(f"  {colour(C_WARN, '⚠')} {iss}")
        print(f"\n{colour(C_ERROR, '✗')} {len(issues)} issue(s)")
        return 1
    print(f"{colour(C_OK, '✓')} No issues: {path}")
    return 0

def print_usage():
    print(f"\n{BOLD('Ipp')} v{VERSION} — A scripting language for game development\n")
    print(f"{BOLD('Usage:')}  python main.py [command] [file]\n")
    cmds = [
        ("<file>",    "Run a script"),
        ("run <f>",   "Run a script"),
        ("check <f>", "Syntax check"),
        ("lint <f>",  "Lint code"),
        ("repl",      "Start REPL (default)"),
    ]
    print(BOLD("Commands:"))
    for c, d in cmds:
        print(f"  {colour(C_CMD, c.ljust(14))} {d}")
    print()

def main():
    args = sys.argv[1:]
    if not args:
        run_repl(); return 0

    cmd = args[0]
    if cmd in ('--help', '-h'):
        print_usage(); return 0
    if cmd in ('--version', '-v'):
        print(f"Ipp v{VERSION}"); return 0
    if cmd == 'repl':
        run_repl(); return 0
    if cmd == 'run' and len(args) >= 2:
        return run_file(args[1])
    if cmd == 'check' and len(args) >= 2:
        return check_file(args[1])
    if cmd == 'lint' and len(args) >= 2:
        return lint_file(args[1])
    if not cmd.startswith('-'):
        return run_file(cmd)

    print_usage(); return 1

if __name__ == '__main__':
    sys.exit(main())
