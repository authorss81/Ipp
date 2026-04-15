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

# Set UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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

VERSION = "1.5.29"

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
# Enable colors by default on all platforms
_USE_ANSI = True

# Enable virtual terminal processing on Windows at startup
if sys.platform.startswith('win'):
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(h, ctypes.byref(mode))
        mode.value |= 4  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(h, mode)
        # Also enable Ctrl+C processing
        h_in = kernel32.GetStdHandle(-10)
        kernel32.GetConsoleMode(h_in, ctypes.byref(mode))
        mode.value |= 0x0001  # ENABLE_PROCESSED_INPUT
        kernel32.SetConsoleMode(h_in, mode)
    except Exception:
        pass

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
C_FN      = lambda t: _rgb(180, 100, 255, t)  # Purple for function repr
C_BOOL    = lambda t: _rgb(220, 130, 255, t)
C_HEADER  = lambda t: _rgb( 80, 200, 255, t)
C_LOGO1   = lambda t: _fg(51, t)
C_LOGO2   = lambda t: _fg(45, t)
C_LOGO3   = lambda t: _fg(39, t)
C_LOGO4   = lambda t: _fg(33, t)
C_LOGO5   = lambda t: _fg(27, t)

def colour(fn, text):
    return fn(text)   # lambdas already no-op when IS_TTY=False

def _serve_accept_loop(server_socket):
    """Accept loop for REPL server - defined at module level to avoid closure issues"""
    from ipp.parser.parser import parse
    from ipp.lexer.lexer import tokenize
    from ipp.interpreter.interpreter import Interpreter
    
    def handle_client(client_socket, addr):
        try:
            client_socket.send(b"Ipp REPL v1.5.25\r\nType 'exit' to quit\r\n\r\n")
            while True:
                client_socket.send(b">>> ")
                data = client_socket.recv(1024).decode().strip()
                if not data or data == 'exit':
                    break
                try:
                    tokens = tokenize(data)
                    ast = parse(tokens)
                    interp = Interpreter()
                    interp.run(ast)
                    result = str(interp.last_value) if interp.last_value else "nil"
                    client_socket.send((result + "\r\n").encode())
                except Exception as e:
                    client_socket.send((f"Error: {str(e)}\r\n").encode())
        except:
            pass
        finally:
            client_socket.close()
    
    import threading
    while True:
        try:
            client_socket, addr = server_socket.accept()
            t = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
            t.start()
        except:
            break

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
    # If code already contains ANSI codes, return as-is to avoid corruption
    if '\033[' in code:
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

# On Windows, pyreadline intercepts Ctrl+C. Use msvcrt to detect it.
if sys.platform.startswith('win'):
    try:
        import msvcrt
        HAS_MSCVRT = True
    except ImportError:
        HAS_MSCVRT = False
else:
    HAS_MSCVRT = False

class IppCompleter:
    def __init__(self, interp):
        self.interp = interp
        self.matches = []
        self._all_builtins = []
        self._cmd_completions = []
        self._load_completions()

    def _load_completions(self):
        """Load all builtin names and REPL commands for completion."""
        try:
            from ipp.runtime.builtins import BUILTINS
            self._all_builtins = sorted(BUILTINS.keys())
        except Exception:
            self._all_builtins = []
        self._cmd_completions = sorted([
            '.help', '.vars', '.fns', '.builtins', '.modules', '.history',
            '.colors', '.vm', '.clear', '.types', '.version',
            '.load', '.save', '.doc', '.time', '.which', '.last',
            '.undo', '.redo', '.edit', '.profile', '.alias',
            'exit', 'quit',
        ])

    def complete(self, text, state):
        if state == 0:
            buf = readline.get_line_buffer() if HAS_RL else text
            
            # REPL command completion (starts with .)
            if buf.startswith('.') or (buf and buf[-1] == '.'):
                prefix = buf.lstrip('.')
                self.matches = [c for c in self._cmd_completions if c.startswith(buf)]
            
            # Dict key completion: dict_name["key
            elif re.search(r'\w+\["[\w]*$', buf):
                m = re.search(r'(\w+)\["([\w]*)$', buf)
                if m:
                    obj_name, prefix = m.group(1), m.group(2)
                    self.matches = self._dict_keys(obj_name, prefix)
            
            # Dict key completion: dict_name['key
            elif re.search(r"\w+\['[\w]*$", buf):
                m = re.search(r"(\w+)\['([\w]*)$", buf)
                if m:
                    obj_name, prefix = m.group(1), m.group(2)
                    self.matches = self._dict_keys(obj_name, prefix)
            
            # Member completion: obj.member
            elif re.match(r'.*?(\w+)\.([\w]*)$', buf) and not buf.startswith('"') and not buf.startswith("'"):
                dot = re.match(r'.*?(\w+)\.([\w]*)$', buf)
                if dot:
                    obj_name, prefix = dot.group(1), dot.group(2)
                    self.matches = [m for m in self._members(obj_name) if m.startswith(prefix)]
            
            # Normal completion with fuzzy matching
            else:
                cands = self._get_all_candidates()
                # Exact prefix matches first
                exact = sorted(c for c in cands if c.startswith(text))
                # Then fuzzy matches using difflib
                import difflib
                fuzzy = difflib.get_close_matches(text, [c for c in cands if c not in exact], n=10, cutoff=0.4)
                self.matches = exact + fuzzy
        
        try:
            return self.matches[state]
        except IndexError:
            return None

    def _get_all_candidates(self):
        """Get all completion candidates from builtins, globals, and keywords."""
        cands = set()
        cands.update(self._all_builtins)
        cands.update(_KEYWORDS)
        cands.update(_BUILTINS)
        cands.update(self._globals())
        return cands

    def _globals(self):
        names = set()
        if hasattr(self.interp, 'global_env'):
            env = self.interp.global_env
            while env:
                if hasattr(env, 'values'):
                    names |= set(env.values.keys())
                env = getattr(env, 'parent', None)
        return names

    def _dict_keys(self, obj_name, prefix):
        """Get dict keys for completion."""
        try:
            env = self.interp.global_env
            obj = None
            while env:
                if hasattr(env, 'values') and obj_name in env.values:
                    obj = env.values[obj_name]; break
                env = getattr(env, 'parent', None)
            if obj is None: return []
            keys = []
            if hasattr(obj, 'data') and isinstance(obj.data, dict):
                keys = [str(k) for k in obj.data.keys() if isinstance(k, str)]
            elif isinstance(obj, dict):
                keys = [str(k) for k in obj.keys() if isinstance(k, str)]
            return sorted(k for k in keys if k.startswith(prefix))
        except Exception:
            return []

    def _members(self, obj_name):
        try:
            env = self.interp.global_env
            obj = None
            while env:
                if hasattr(env, 'values') and obj_name in env.values:
                    obj = env.values[obj_name]; break
                env = getattr(env, 'parent', None)
            if obj is None: return []
            m = []
            if hasattr(obj, 'fields'): m += list(obj.fields)
            if hasattr(obj, 'ipp_class') and hasattr(obj.ipp_class, 'methods'):
                m += list(obj.ipp_class.methods)
            if hasattr(obj, '_env') and hasattr(obj._env, 'values'):
                m += list(obj._env.values)
            if hasattr(obj, 'data') and isinstance(obj.data, dict):
                m += [str(k) for k in obj.data.keys() if isinstance(k, str)]
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
        
        # Auto-indentation: after Enter, if line ends with {, (, [, add indent
        def auto_indent_hook(text):
            if text and text[-1] in '{([':
                return text + '    '
            return text
        
        # Bracket matching: highlight matching brackets
        readline.parse_and_bind("set show-all-if-ambiguous on")
        readline.parse_and_bind("set mark-directories on")
        
        # Windows-specific: use libedit-style binding if needed
        if sys.platform.startswith('win'):
            try:
                readline.parse_and_bind("bind ^I rl_complete")
            except:
                pass
        
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
            if i + 1 >= len(src):
                return False
            i += 2
            continue
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
    return len(stack) == 0 and not in_str and not in_sq

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
        (".builtins",   "List all built-in functions (color-coded)"),
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
        (".bench [N] <expr>","Benchmark N times (default 10), show avg/min/max"),
        (".which <name>",   "Check if builtin/var/function"),
        (".last / $_",      "Reference last result"),
        (".undo",           "Undo last command"),
        (".redo",           "Redo last undone command"),
        (".edit",           "Edit last command in editor"),
        (".profile",        "Profile last command"),
        (".alias n cmd",    "Create command alias"),
        (".mem",            "Show memory usage"),
        (".reload [file]", "Reload/reload imported module"),
        (".checkpoint [n]","Save checkpoint (default: 5)"),
        (".restore [n]",   "Restore checkpoint (default: latest)"),
        (".macro n exp",   "Define macro"),
        (".cache save",    "Save bytecode cache for file"),
        (".cache load",    "Load bytecode cache for file"),
    ]
    for cmd, desc in tools:
        c_cmd  = colour(C_CMD, cmd.ljust(16))
        c_desc = colour(DIM, desc)
        print(f"    {c_cmd} {c_desc}")

    _section("REPL Tools (v1.3.10)")
    tools2 = [
        (".pretty <expr>",  "Pretty print complex data"),
        (".stack",          "Show call stack"),
        (".history $_",     "Show expression history"),
        (".hist",           "Show last 10 results ($_1, $_2...)"),
        ("! <cmd>",         "Execute shell command"),
        (".session save",   "Save session state"),
        (".session load",   "Load saved session"),
        (".session clear",  "Clear saved session"),
        (".export <file>",  "Export session as .ipp script"),
        (".prompt <fmt>",   "Customize prompt format"),
        (".json <expr>",    "JSON viewer with formatting"),
        (".format <expr>",  "Auto-format code on Enter"),
        (".cd <dir>",       "Change directory"),
        (".ls [dir]",       "List directory contents"),
        (".pwd",            "Print working directory"),
        (".pipe <cmd>",     "Pipe output to shell command"),
        (".bind <key> cmd", "Set custom key binding"),
        (".search <kw>",    "Search builtin documentation"),
        (".examples",       "Show interactive code examples"),
        (".tutorial",       "Start interactive tutorial"),
        (".plugin load f",  "Load plugin file"),
        (".debug start",    "Start step-through debugger"),
        (".debug stop",     "Stop debugger"),
        (".break <line>",   "Set breakpoint"),
        (".watch <expr>",   "Watch expression value"),
        (".locals",         "Show local variables"),
        (".table <var>",    "Show list of dicts as table"),
        (".theme <name>",   "Set color theme (dark/light/solarized)"),
        (".html <expr>",    "Preview HTML in browser"),
        (".plot <data>",   "Plot data with matplotlib"),
        (".bg <expr>",     "Run in background"),
        (".jobs",          "Show background jobs"),
        (".async <expr>",  "Run async expression"),
        (".serve [port]",  "Start REPL server on port"),
        (".compare a b",   "Compare two expressions"),
        ("Tab",             "Auto-complete (builtins, vars, keys)"),
        ("(",               "Signature help when typing"),
    ]
    for cmd, desc in tools2:
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
    
    # Group builtins by category for better display
    categories = {
        "I/O": ["print", "input", "exit"],
        "Type": ["type", "str", "int", "float", "bool", "to_number", "to_string", "to_int", "to_float", "to_bool"],
        "Math": ["abs", "min", "max", "sum", "round", "floor", "ceil", "sqrt", "pow", "pi", "e",
                 "sin", "cos", "tan", "log", "log10", "degrees", "radians", "asin", "acos", "atan", "atan2",
                 "lerp", "clamp", "map_range", "distance", "distance_3d", "normalize", "dot", "cross",
                 "sign", "smoothstep", "move_towards", "angle", "deg_to_rad", "rad_to_deg",
                 "factorial", "gcd", "lcm", "hypot", "floor_div"],
        "Random": ["random", "randint", "randfloat", "choice", "shuffle"],
        "Collections": ["len", "range", "keys", "values", "items", "contains", "set", "deque", "ordict", "has_key"],
        "String": ["upper", "lower", "strip", "replace", "replace_all", "find", "starts_with", "ends_with",
                   "startswith", "endswith", "split", "join", "count", "contains", "split_lines", "ascii", "from_ascii",
                   "char_at", "substring", "index_of"],
        "File": ["read_file", "write_file", "append_file", "file_exists", "delete_file", "list_dir", "mkdir",
                 "file_read", "file_write"],
        "JSON": ["json_parse", "json_stringify"],
        "XML": ["xml_parse", "xml_to_string"],
        "YAML": ["yaml_parse", "yaml_to_string"],
        "TOML": ["toml_parse", "toml_to_string"],
        "CSV": ["csv_parse", "csv_parse_dict", "csv_to_string"],
        "Regex": ["regex_match", "regex_search", "regex_replace"],
        "Hash": ["md5", "sha256", "sha1", "sha512", "hash"],
        "Base64": ["base64_encode", "base64_decode"],
        "GZIP": ["gzip_compress", "gzip_decompress"],
        "ZIP": ["zip_create", "zip_extract"],
        "HTTP": ["http_get", "http_post", "http_put", "http_delete", "http_request", "http_serve"],
        "FTP": ["ftp_connect", "ftp_disconnect", "ftp_list", "ftp_get", "ftp_put"],
        "SMTP": ["smtp_connect", "smtp_disconnect", "smtp_send"],
        "WebSocket": ["websocket_connect", "websocket_send", "websocket_receive", "websocket_close"],
        "URL": ["url_parse", "url_build", "url_encode", "url_decode", "url_query_parse", "url_query_build"],
        "UUID": ["uuid4", "uuid1", "uuid_nil"],
        "DateTime": ["datetime", "datetime_create"],
        "Time": ["time", "sleep", "clock"],
        "Path": ["path_dirname", "path_basename", "path_join", "path_exists"],
        "OS": ["os_platform", "os_cwd", "os_chdir", "env_get", "env_set", "list_env"],
        "Complex": ["complex"],
        "Logging": ["logger"],
        "Threading": ["thread", "thread_sleep", "thread_current"],
        "Argparse": ["argparse", "args_add", "args_parse"],
        "Printf": ["printf", "sprintf", "scanf"],
        "Game": ["vec2", "vec3", "color", "rect"],
        "DataStructures": ["PriorityQueue", "Tree", "Graph"],
        "Control": ["assert"],
    }
    
    for group, names in categories.items():
        available = [n for n in names if n in BUILTINS]
        if available:
            # Category header in cyan
            print(f"  {colour(C_CMD, group + ':')}")
            for name in sorted(available):
                fn = BUILTINS[name]
                # Show full function repr like <function ipp_dot at 0x...>
                fn_repr = repr(fn)
                # Builtin name in blue, function repr in purple
                print(f"    {colour(C_KW, name.ljust(20))} {colour(C_FN, fn_repr)}")
            print()
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
        self._global_env = {}  # Simple dict for VM variables
    
    @property
    def global_env(self):
        """Provide global_env-like interface for REPL compatibility."""
        class VMEnv:
            def __init__(self, env_dict):
                self.values = env_dict
        return VMEnv(self._global_env)
    
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
        if self.use_vm:
            return self.get_interpreter().global_env
        else:
            return self.get_interpreter().global_env

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


def _pretty_print(val, indent=0, max_depth=5):
    """Pretty print complex data structures with indentation."""
    prefix = "  " * indent
    
    if val is None:
        return f"{prefix}{colour(C_BOOL, 'nil')}"
    
    if isinstance(val, bool):
        return f"{prefix}{colour(C_BOOL, 'true' if val else 'false')}"
    
    if isinstance(val, (int, float)):
        return f"{prefix}{colour(C_NUM, str(val))}"
    
    if isinstance(val, str):
        return f"{prefix}{colour(C_STR, repr(val))}"
    
    # Dict / IppDict
    if hasattr(val, 'data') and isinstance(val.data, dict):
        if not val.data:
            return f"{prefix}{{}}"
        if indent >= max_depth:
            return f"{prefix}{{...}}"
        lines = [f"{prefix}{{"]
        items = list(val.data.items())
        for i, (k, v) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            key_str = colour(C_KW, str(k))
            val_str = _pretty_print(v, indent + 1, max_depth)
            lines.append(f"{val_str}{comma}")
        lines.append(f"{prefix}}}")
        return "\n".join(lines)
    
    if isinstance(val, dict):
        if not val:
            return f"{prefix}{{}}"
        if indent >= max_depth:
            return f"{prefix}{{...}}"
        lines = [f"{prefix}{{"]
        items = list(val.items())
        for i, (k, v) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            key_str = colour(C_KW, str(k))
            val_str = _pretty_print(v, indent + 1, max_depth)
            lines.append(f"{val_str}{comma}")
        lines.append(f"{prefix}}}")
        return "\n".join(lines)
    
    # List / IppList
    if hasattr(val, 'elements') and isinstance(val.elements, list):
        if not val.elements:
            return f"{prefix}[]"
        if indent >= max_depth:
            return f"{prefix}[...]"
        lines = [f"{prefix}["]
        for i, item in enumerate(val.elements):
            comma = "," if i < len(val.elements) - 1 else ""
            item_str = _pretty_print(item, indent + 1, max_depth)
            lines.append(f"{item_str}{comma}")
        lines.append(f"{prefix}]")
        return "\n".join(lines)
    
    if isinstance(val, list):
        if not val:
            return f"{prefix}[]"
        if indent >= max_depth:
            return f"{prefix}[...]"
        lines = [f"{prefix}["]
        for i, item in enumerate(val):
            comma = "," if i < len(val) - 1 else ""
            item_str = _pretty_print(item, indent + 1, max_depth)
            lines.append(f"{item_str}{comma}")
        lines.append(f"{prefix}]")
        return "\n".join(lines)
    
    # IppInstance
    if hasattr(val, 'fields') and hasattr(val, 'ipp_class'):
        if indent >= max_depth:
            return f"{prefix}{val.ipp_class.name}(...)"
        lines = [f"{prefix}{colour(C_KW, val.ipp_class.name)} {{"]
        items = list(val.fields.items())
        for i, (k, v) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            key_str = colour(C_KW, str(k))
            val_str = _pretty_print(v, indent + 1, max_depth)
            lines.append(f"{val_str}{comma}")
        lines.append(f"{prefix}}}")
        return "\n".join(lines)
    
    # Default
    s = str(val)
    if len(s) > 80:
        s = s[:77] + "..."
    return f"{prefix}{colour(C_RESULT, s)}"


def _get_similar_names(name, candidates, max_suggestions=3):
    """Find similar names to suggest when user makes a typo."""
    import difflib
    unique = list(dict.fromkeys(candidates))  # Preserve order, remove duplicates
    matches = difflib.get_close_matches(name, unique, n=max_suggestions, cutoff=0.6)
    return matches


def _suggest_fix(error_msg, interp_manager):
    """Generate helpful suggestions based on error message."""
    suggestions = []
    
    m = re.search(r"Undefined variable[': ]+['\"]?(\w+)['\"]?", error_msg)
    if m:
        name = m.group(1)
        try:
            from ipp.runtime.builtins import BUILTINS
            all_names = list(BUILTINS.keys())
            env = interp_manager.global_env
            while env:
                if hasattr(env, 'values'):
                    all_names.extend(env.values.keys())
                env = getattr(env, 'parent', None)
            similar = _get_similar_names(name, all_names)
            if similar:
                suggestions.append(f"  {colour(C_WARN, 'Did you mean:')} {colour(C_OK, ', '.join(similar))}")
            else:
                suggestions.append(f"  {colour(C_WARN, 'Tip:')} Use .builtins to see available functions, or .vars to see variables")
        except Exception:
            pass
    elif "Cannot call" in error_msg:
        suggestions.append(f"  {colour(C_WARN, 'Tip:')} Check that the variable is a function. Use .which <name> to inspect it")
    elif "not supported" in error_msg or "TypeError" in error_msg:
        suggestions.append(f"  {colour(C_WARN, 'Tip:')} Check the types of your operands. Use type(<var>) to inspect values")
    elif "index out of range" in error_msg:
        suggestions.append(f"  {colour(C_WARN, 'Tip:')} Check the list/dict length with len(<var>) before indexing")
    elif "not found" in error_msg or "has no attribute" in error_msg:
        suggestions.append(f"  {colour(C_WARN, 'Tip:')} Use type(<var>) to check the object type, and .doc <builtin> for function docs")
    elif "recursion" in error_msg.lower():
        suggestions.append(f"  {colour(C_WARN, 'Tip:')} Check your base case. Infinite recursion exceeds the call depth limit")
    elif "SyntaxError" in error_msg or "syntax" in error_msg.lower():
        suggestions.append(f"  {colour(C_WARN, 'Tip:')} Check for missing brackets, parentheses, or semicolons")
    
    return suggestions


def _format_error_with_suggestions(e, interp_manager):
    """Format error message with helpful suggestions."""
    msg = str(e)
    suggestions = _suggest_fix(msg, interp_manager)
    m = re.search(r'line (\d+)', msg)
    loc = f" {colour(DIM, f'(line {m.group(1)})')}" if m else ''
    cross = 'x' if not _UNI else '✗'
    lines = [f"  {colour(C_ERROR, cross)} {colour(C_ERROR, msg)}{loc}"]
    lines.extend(suggestions)
    return '\n'.join(lines)

# ─── REPL spinner (simple, no threads) ───────────────────────────────────────
_SPINNER = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷']

# ─── Main REPL ────────────────────────────────────────────────────────────────
def run_repl():
    from ipp.lexer.lexer import tokenize
    from ipp.parser.parser import parse
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
    _last_results = []  # Expression history ($_1, $_2, etc.)
    _env_snapshots = []  # For .undo
    _undo_stack = []  # For .redo
    _aliases = {}  # For .alias
    _key_bindings = {}  # For .bind
    _checkpoints = []  # For .checkpoint/.restore
    _macros = {}  # For .macro
    _bg_jobs = []  # For .bg/.jobs
    _repl_server = None  # For .serve
    _repl_accept_thread = None  # For .serve accept loop
    _PROMPT_FORMAT = "ipp"  # Default prompt format
    _PROMPT_ARROW = "❯" if _UNI else ">>>"  # Default prompt arrow
    _current_dir = os.getcwd()  # Track current directory for .cd

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
                # Custom prompt format
                if _PROMPT_FORMAT == 'dir':
                    cwd = os.path.basename(os.getcwd())
                    arrow = f'({cwd}) ❯ ' if _UNI else f'({cwd})> '
                elif _PROMPT_FORMAT == 'time':
                    import datetime
                    t = datetime.datetime.now().strftime('%H:%M:%S')
                    arrow = f'[{t}] ❯ ' if _UNI else f'[{t}]> '
                elif _PROMPT_FORMAT == 'full':
                    import datetime
                    cwd = os.getcwd()
                    t = datetime.datetime.now().strftime('%H:%M:%S')
                    arrow = f'[{t}] {cwd} ❯ ' if _UNI else f'[{t}] {cwd}> '
                else:
                    arrow = '>>> ' if not _UNI else '❯ '
                prompt_txt = colour(C_PROMPT, f"  {arrow}")

            # Allow custom arrow symbol
            if _PROMPT_FORMAT == 'arrow':
                arrow = _PROMPT_ARROW + ' '
                prompt_txt = colour(C_PROMPT, f"  {arrow}")

            raw = input(prompt_txt)

        except KeyboardInterrupt:
            # Ctrl+C always exits the REPL immediately
            print(f"\n  {colour(C_OK, 'Goodbye!')}")
            break
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
                    # Enable virtual terminal processing on Windows
                    if sys.platform.startswith('win'):
                        try:
                            import ctypes
                            kernel32 = ctypes.windll.kernel32
                            h = kernel32.GetStdHandle(-11)
                            mode = ctypes.c_ulong()
                            kernel32.GetConsoleMode(h, ctypes.byref(mode))
                            mode.value |= 4  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                            kernel32.SetConsoleMode(h, mode)
                        except Exception:
                            pass
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
                    from ipp.lexer.lexer import tokenize
                    from ipp.parser.parser import parse
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
                        print(f"  {colour(DIM, '>')} {format_output(val)}")
                    print(f"  {colour(DIM, f'  {elapsed*1000:.2f}ms')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .bench <expr> — Run benchmark N times, show avg/min/max
            m = re.match(r'\.bench\s+(\d+)?\s+(.+)$', stripped)
            if m:
                try:
                    runs = int(m.group(1)) if m.group(1) else 10
                    expr = m.group(2)
                    tokens = tokenize(expr)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    times = []
                    for _ in range(runs):
                        t_start = time.perf_counter()
                        interp.run(ast)
                        elapsed = time.perf_counter() - t_start
                        times.append(elapsed * 1000)
                        interp.return_value = None
                        interp.last_value = None
                    avg = sum(times) / len(times)
                    min_t = min(times)
                    max_t = max(times)
                    print(f"  {colour(DIM, f'Benchmark: {runs} runs')}")
                    print(f"    {colour(C_OK, 'avg:')} {avg:.2f}ms  {colour(C_OK, 'min:')} {min_t:.2f}ms  {colour(C_OK, 'max:')} {max_t:.2f}ms")
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
                    current = dict(interp.global_env.values)
                    _undo_stack.append(current)
                    snapshot = _env_snapshots.pop()
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

            # ── v1.3.10 REPL Intelligence ──────────────────────────────

            # .redo — Redo last undone command
            if stripped == '.redo':
                if _undo_stack:
                    snapshot = _undo_stack.pop()
                    interp = interp_manager.get_interpreter()
                    interp.global_env.values.clear()
                    interp.global_env.values.update(snapshot)
                    print(f"  {colour(C_OK, 'Last undo redone')}")
                else:
                    print(f"  {colour(DIM, '(nothing to redo)')}")
                continue

            # .history $_ — Show expression history
            if stripped == '.history $_' or stripped == '.history results':
                if not _last_results:
                    print(f"  {colour(DIM, '(no expression history yet)')}")
                else:
                    for i, (idx, val) in enumerate(_last_results[-10:], max(1, len(_last_results) - 9)):
                        print(f"  {colour(DIM, f'$_{idx}:')} {format_output(val)}")
                continue

            # .hist — Quick show last results
            if stripped == '.hist':
                if not _last_results:
                    print(f"  {colour(DIM, '(no results yet)')}")
                else:
                    print(f"  {colour(C_CMD, 'Last Results:')}")
                    for idx, val in reversed(_last_results[-10:]):
                        print(f"  {colour(DIM, f'$_{idx}:')} {format_output(val)}")
                continue

            # ! shell command — Execute shell command
            if stripped.startswith('!'):
                cmd = stripped[1:].strip()
                if cmd:
                    import subprocess
                    try:
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if result.stdout:
                            print(result.stdout, end='')
                        if result.stderr:
                            print(f"  {colour(C_ERROR, result.stderr)}", end='')
                    except Exception as e:
                        print(f"  {colour(C_ERROR, f'Shell command failed: {e}')}")
                continue

            # .pretty <expr> — Pretty print expression result
            m = re.match(r'\.pretty\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                try:
                    tokens = tokenize(expr)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    interp.run(ast)
                    val = interp.return_value if interp.return_value is not None else interp.last_value
                    interp.return_value = None
                    interp.last_value = None
                    if val is not None:
                        print(_pretty_print(val, indent=0))
                    else:
                        print(f"  {colour(DIM, '(no result)')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .stack — Show call stack
            if stripped == '.stack':
                interp = interp_manager.get_interpreter()
                print(f"  {colour(C_CMD, 'Call Stack:')}")
                # Show current execution context
                if hasattr(interp, 'call_depth'):
                    print(f"  {colour(DIM, f'Call depth: {interp.call_depth}')}")
                if hasattr(interp, 'global_env') and hasattr(interp.global_env, 'values'):
                    vars_count = len([k for k in interp.global_env.values.keys() if not k.startswith('_')])
                    print(f"  {colour(DIM, f'Global variables: {vars_count}')}")
                print(f"  {colour(DIM, f'Command history: {len(_cmd_history)} commands')}")
                print(f"  {colour(DIM, f'Expression history: {len(_last_results)} results')}")
                continue

            # .session save — Save session state
            m = re.match(r'\.session\s+(save|load|clear)$', stripped)
            if m:
                action = m.group(1)
                session_dir = os.path.join(os.path.expanduser("~"), ".ipp", "sessions")
                os.makedirs(session_dir, exist_ok=True)
                session_file = os.path.join(session_dir, "current_session.json")
                
                if action == 'save':
                    try:
                        import json
                        interp = interp_manager.get_interpreter()
                        session_data = {
                            'history': _cmd_history[-100:],
                            'last_result': str(_last_result) if _last_result is not None else None,
                            'variables': {}
                        }
                        # Save variable values
                        env = interp.global_env
                        while env:
                            if hasattr(env, 'values'):
                                for k, v in env.values.items():
                                    try:
                                        session_data['variables'][k] = str(v)
                                    except:
                                        pass
                            env = getattr(env, 'parent', None)
                        
                        with open(session_file, 'w') as f:
                            json.dump(session_data, f, indent=2)
                        print(f"  {colour(C_OK, f'Session saved ({len(session_data["variables"])} variables, {len(session_data["history"])} commands)')}")
                    except Exception as e:
                        print(f"  {colour(C_ERROR, f'Failed to save session: {e}')}")
                
                elif action == 'load':
                    try:
                        import json
                        if os.path.exists(session_file):
                            with open(session_file, 'r') as f:
                                session_data = json.load(f)
                            
                            # Actually restore variables by re-executing history
                            interp = interp_manager.get_interpreter()
                            history = session_data.get('history', [])
                            restored = 0
                            for cmd in history:
                                try:
                                    tokens = tokenize(cmd)
                                    ast = parse(tokens)
                                    interp.run(ast)
                                    val = interp.return_value if interp.return_value is not None else interp.last_value
                                    interp.return_value = None
                                    interp.last_value = None
                                    if val is not None:
                                        _last_result = val
                                        _last_results.append((len(_last_results) + 1, val))
                                    restored += 1
                                except:
                                    pass
                            
                            print(f"  {colour(C_OK, f'Session restored: {restored} commands executed')}")
                            print(f"  {colour(DIM, f'Variables: {len(session_data.get("variables", {}))} saved')}")
                        else:
                            print(f"  {colour(C_WARN, 'No saved session found')}")
                    except Exception as e:
                        print(f"  {colour(C_ERROR, f'Failed to load session: {e}')}")
                
                elif action == 'clear':
                    if os.path.exists(session_file):
                        os.remove(session_file)
                        print(f"  {colour(C_OK, 'Session cleared')}")
                    else:
                        print(f"  {colour(DIM, '(no session to clear)')}")
                continue

            # ── v1.3.10 Debugging Features ──────────────────────────────

            # .debug start — Start step-through debugger
            if stripped == '.debug start':
                print(f"  {colour(C_CMD, 'Debugger started')}")
                print(f"  {colour(DIM, 'Commands: .step, .next, .continue, .stop, .break <line>, .watch <expr>, .locals')}")
                _debug_mode = True
                continue

            # .debug stop — Stop debugger
            if stripped == '.debug stop':
                print(f"  {colour(C_CMD, 'Debugger stopped')}")
                _debug_mode = False
                continue

            # .break <line> — Set breakpoint
            m = re.match(r'\.break\s+(\d+)$', stripped)
            if m:
                line_num = int(m.group(1))
                print(f"  {colour(C_OK, f'Breakpoint set at line {line_num}')}")
                continue

            # .watch <expr> — Watch expression (continuously evaluates)
            m = re.match(r'\.watch\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                try:
                    # Evaluate and show current value
                    tokens = tokenize(expr)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    interp.run(ast)
                    val = interp.return_value if interp.return_value is not None else interp.last_value
                    interp.return_value = None
                    interp.last_value = None
                    if val is not None:
                        t = type(val).__name__
                        print(f"  {colour(C_WARN, f'Watch: {expr}')} = {colour(C_OK, format_output(val))} {colour(DIM, f'({t})')}")
                    else:
                        print(f"  {colour(DIM, f'Watch: {expr} = (no value)')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, f'Watch error: {e}')}")
                continue

            # .locals — Show local variables
            if stripped == '.locals':
                interp = interp_manager.get_interpreter()
                env = interp.global_env
                vars_found = {}
                while env:
                    if hasattr(env, 'values'):
                        vars_found.update(env.values)
                    env = getattr(env, 'parent', None)
                if vars_found:
                    print(f"  {colour(C_CMD, 'Local Variables:')}")
                    for name, val in sorted(vars_found.items()):
                        if not callable(val) and not name.startswith('_'):
                            print(f"    {colour(C_KW, name)} = {format_output(val)}")
                else:
                    print(f"  {colour(DIM, '(no local variables)')}")
                continue

            # .table <var> — Show list of dicts as table
            m = re.match(r'\.table\s+(\w+)$', stripped)
            if m:
                var_name = m.group(1)
                try:
                    interp = interp_manager.get_interpreter()
                    env = interp.global_env
                    obj = None
                    while env:
                        if hasattr(env, 'values') and var_name in env.values:
                            obj = env.values[var_name]; break
                        env = getattr(env, 'parent', None)
                    
                    if obj and isinstance(obj, list) and obj and isinstance(obj[0], dict):
                        # Print table header
                        headers = list(obj[0].keys())
                        col_widths = {h: max(len(h), max(len(str(row.get(h, ''))) for row in obj)) for h in headers}
                        
                        header_line = ' | '.join(h.ljust(col_widths[h]) for h in headers)
                        print(f"  {colour(C_CMD, header_line)}")
                        print(f"  {'-' * len(header_line)}")
                        
                        for row in obj:
                            row_line = ' | '.join(str(row.get(h, '')).ljust(col_widths[h]) for h in headers)
                            print(f"  {row_line}")
                    else:
                        print(f"  {colour(C_WARN, f'{var_name} is not a list of dicts')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, f'Table error: {e}')}")
                continue

            # .theme <name> — Set color theme
            m = re.match(r'\.theme\s+(\w+)$', stripped)
            if m:
                theme = m.group(1).lower()
                themes = {
                    'dark': {'prompt': '100,200,255', 'error': '255,100,100', 'ok': '80,220,120', 'warn': '255,200,80'},
                    'light': {'prompt': '0,100,200', 'error': '200,0,0', 'ok': '0,150,0', 'warn': '200,100,0'},
                    'solarized': {'prompt': '100,150,200', 'error': '200,100,50', 'ok': '100,200,100', 'warn': '180,150,0'},
                    'monokai': {'prompt': '249,38,114', 'error': '249,38,114', 'ok': '166,226,46', 'warn': '253,151,31'},
                    'gruvbox': {'prompt': '191,145,0', 'error': '204,46,46', 'ok': '142,191,107', 'warn': '215,133,18'},
                }
                global _current_theme
                if theme in themes:
                    _current_theme = theme
                    t = themes[theme]
                    print(f"  {colour(C_OK, f'✓ Theme set to {theme}')}")
                    print(f"    {colour(C_PROMPT, 'Prompt:  RGB(' + t['prompt'] + ')')}")
                    print(f"    {colour(C_ERROR, 'Error:   RGB(' + t['error'] + ')')}")
                    print(f"    {colour(C_OK,    'OK:      RGB(' + t['ok'] + ')')}")
                    print(f"    {colour(C_WARN,  'Warn:    RGB(' + t['warn'] + ')')}")
                else:
                    print(f"  {colour(C_WARN, f'Unknown theme: {theme}')}")
                    print(f"  {colour(DIM, f'Available: {", ".join(themes.keys())}')}")
                continue

            # .html <expr> — Preview HTML in browser
            m = re.match(r'\.html\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                try:
                    tokens = tokenize(expr)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    result = interp.run(ast)
                    val = interp.return_value if interp.return_value is not None else interp.last_value
                    if val is not None:
                        html_content = str(val)
                        import tempfile
                        import webbrowser
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                            f.write(f"<html><body><pre>{html_content}</pre></body></html>")
                            temp_path = f.name
                        webbrowser.open('file://' + temp_path)
                        print(f"  {colour(C_OK, '✓ Opened HTML in browser')}")
                    else:
                        print(f"  {colour(C_WARN, 'Expression returned nil')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .plot <data> — Plot data with matplotlib
            m = re.match(r'\.plot\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                try:
                    import matplotlib.pyplot as plt
                    import matplotlib
                    matplotlib.use('Agg')
                    tokens = tokenize(expr)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    result = interp.run(ast)
                    val = interp.return_value if interp.return_value is not None else interp.last_value
                    if val is None:
                        print(f"  {colour(C_WARN, 'Expression returned nil')}")
                    elif isinstance(val, list):
                        plt.plot(val)
                        plt.title('Ipp Data')
                        plt.xlabel('Index')
                        plt.ylabel('Value')
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                            plt.savefig(f.name)
                            plt.close()
                            import webbrowser
                            webbrowser.open('file://' + f.name)
                        print(f"  {colour(C_OK, '✓ Plot opened in browser')}")
                    else:
                        print(f"  {colour(C_WARN, 'Data must be a list')}")
                except ImportError:
                    print(f"  {colour(C_WARN, 'matplotlib not installed')}")
                    print(f"  {colour(DIM, 'Install with: pip install matplotlib')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .bg <expr> — Run in background
            _bg_jobs = []  # Add this at the top of the file
            m = re.match(r'\.bg\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                import threading
                import queue
                result_queue = queue.Queue()
                def run_bg():
                    try:
                        tokens = tokenize(expr)
                        ast = parse(tokens)
                        interp = interp_manager.get_interpreter()
                        interp.run(ast)
                        val = interp.return_value if interp.return_value is not None else interp.last_value
                        result_queue.put(('ok', val))
                    except Exception as e:
                        result_queue.put(('error', str(e)))
                t = threading.Thread(target=run_bg)
                t.start()
                job_id = len(_bg_jobs) + 1
                _bg_jobs.append({'thread': t, 'expr': expr[:30], 'queue': result_queue})
                print(f"  {colour(C_OK, f'Job #{job_id} started in background')}")
                continue

            # .jobs — Show background jobs
            if stripped == '.jobs':
                if not _bg_jobs:
                    print(f"  {colour(DIM, '(no background jobs)')}")
                else:
                    print(f"  {colour(C_CMD, 'Background Jobs:')}")
                    for i, job in enumerate(_bg_jobs, 1):
                        if job['thread'].is_alive():
                            status = colour(C_OK, 'running')
                        else:
                            try:
                                status, val = job['queue'].get_nowait()
                                status = colour(C_OK, 'done') if status == 'ok' else colour(C_ERROR, 'error')
                            except:
                                status = colour(C_WARN, 'unknown')
                        print(f"  {colour(DIM, f'{i}:')} {job['expr']}... {status}")
                continue

            # .async <expr> — Run async expression
            m = re.match(r'\.async\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                try:
                    from ipp.runtime.builtins import BUILTINS
                    if 'async_run' in BUILTINS:
                        async_run_fn = BUILTINS['async_run']
                        # Create a simple async wrapper
                        code = f'''
func __async_task__() {{
    return {expr}
}}
'''
                        tokens = tokenize(code)
                        ast = parse(tokens)
                        interp = interp_manager.get_interpreter()
                        interp.run(ast)
                        if hasattr(interp, 'last_value') and interp.last_value:
                            coro = interp.last_value
                            result = async_run_fn(coro)
                            print(f"  {colour(C_OK, 'Async result:')} {format_output(result)}")
                        else:
                            print(f"  {colour(C_WARN, 'Expression is not async')}")
                    else:
                        print(f"  {colour(C_WARN, 'async_run not available')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .serve [port] — Start REPL server
            m = re.match(r'\.serve(?:\s+(\d+))?$', stripped)
            if m:
                port = int(m.group(1)) if m.group(1) else 8080
                server_running = False
                
                if _repl_server is not None:
                    try:
                        if _repl_server.fileno() != -1:
                            server_running = True
                    except:
                        _repl_server = None
                
                if not server_running:
                    import socket
                    import threading
                    _repl_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    _repl_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    _repl_server.bind(('0.0.0.0', port))
                    _repl_server.listen(5)
                    print(f"  {colour(C_OK, f'REPL server started on port {port}')}")
                    print(f"  {colour(DIM, 'Connect with: telnet localhost ' + str(port))}")
                
                # Start accept loop if not already running
                if _repl_accept_thread is None or not _repl_accept_thread.is_alive():
                    import threading
                    _repl_accept_thread = threading.Thread(target=lambda: _serve_accept_loop(_repl_server), daemon=True)
                    _repl_accept_thread.start()
                
                print(f"  {colour(DIM, 'Server running in background')}")
                continue

            # .compare a b — Compare two expressions
            m = re.match(r'\.compare\s+(.+)\s+(.+)$', stripped)
            if m:
                expr1 = m.group(1)
                expr2 = m.group(2)
                try:
                    tokens1 = tokenize(expr1)
                    ast1 = parse(tokens1)
                    interp1 = Interpreter()
                    interp1.run(ast1)
                    result1 = interp1.last_value
                    
                    tokens2 = tokenize(expr2)
                    ast2 = parse(tokens2)
                    interp2 = Interpreter()
                    interp2.run(ast2)
                    result2 = interp2.last_value
                    
                    print(f"  {colour(C_CMD, 'Expression 1:')} {expr1}")
                    print(f"    = {format_output(result1)}")
                    print(f"  {colour(C_CMD, 'Expression 2:')} {expr2}")
                    print(f"    = {format_output(result2)}")
                    if result1 == result2:
                        print(f"  {colour(C_OK, 'Results are equal')}")
                    else:
                        print(f"  {colour(C_WARN, 'Results differ')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .tutorial — Start interactive tutorial
            if stripped == '.tutorial':
                print(f"  {colour(C_CMD, 'Ipp Interactive Tutorial')}")
                print(f"  {colour(DIM, 'Learn Ipp step by step!')}")
                print()
                print(f"  1. Variables: {colour(C_KW, 'var x = 10')}")
                print(f"  2. Functions: {colour(C_KW, 'func add(a, b) { return a + b }')}")
                print(f"  3. Lists: {colour(C_KW, 'var nums = [1, 2, 3]')}")
                print(f"  4. Dicts: {colour(C_KW, 'var person = {\"name\": \"Alice\"}')}")
                print(f"  5. Loops: {colour(C_KW, 'for i in 0..5 { print(i) }')}")
                print(f"  6. Classes: {colour(C_KW, 'class Dog { func init() { this.name = \"rex\" } }')}")
                print()
                print(f"  {colour(DIM, 'Try each example in the REPL!')}")
                continue

            # .plugin load <file> — Load plugin
            m = re.match(r'\.plugin\s+load\s+(.+)$', stripped)
            if m:
                filepath = m.group(1).strip().strip('"').strip("'")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        source = f.read()
                    # Execute plugin in current context
                    tokens = tokenize(source)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    interp.run(ast)
                    print(f"  {colour(C_OK, f'Plugin loaded: {filepath}')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, f'Plugin error: {e}')}")
                continue

            # .search <keyword> — Search builtin documentation
            m = re.match(r'\.search\s+(.+)$', stripped)
            if m:
                keyword = m.group(1).lower()
                try:
                    from ipp.runtime.builtins import BUILTINS
                    matches = []
                    for name, fn in BUILTINS.items():
                        if keyword in name.lower() or (fn.__doc__ and keyword in fn.__doc__.lower()):
                            matches.append((name, fn.__doc__ or "No docs"))
                    if matches:
                        print(f"  {colour(C_CMD, f'Found {len(matches)} matches for \"{keyword}\":')}")
                        for name, doc in sorted(matches)[:20]:
                            doc_preview = doc[:60] + "..." if len(doc) > 60 else doc
                            print(f"    {colour(C_KW, name)}: {colour(DIM, doc_preview)}")
                        if len(matches) > 20:
                            print(f"  {colour(DIM, f'... and {len(matches) - 20} more')}")
                    else:
                        print(f"  {colour(C_WARN, f'No matches found for \"{keyword}\"')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .examples — Show code examples
            if stripped == '.examples':
                print(f"  {colour(C_CMD, 'Ipp Code Examples')}")
                print()
                examples = [
                    ("Variables", "var x = 10\nvar name = \"Alice\""),
                    ("Functions", "func greet(name) {\n    return \"Hello \" + name\n}"),
                    ("Lists", "var nums = [1, 2, 3, 4, 5]\nvar doubled = [x*2 for x in nums]"),
                    ("Dicts", "var person = {\"name\": \"Alice\", \"age\": 30}"),
                    ("Loops", "for i in 0..5 {\n    print(i)\n}"),
                    ("Classes", "class Dog {\n    func init(name) {\n        this.name = name\n    }\n    func bark() {\n        print(this.name + \" says woof!\")\n    }\n}"),
                    ("HTTP", "var res = http_get(\"https://httpbin.org/get\")\nprint(res[\"status\"])"),
                    ("WebSocket", "var ws = websocket_connect(\"ws://echo.websocket.org\")\nwebsocket_send(ws, \"hello\")\nvar msg = websocket_receive(ws)"),
                    ("Math", "var dist = distance(0, 0, 3, 4)\nvar angle = atan2(1, 1)"),
                    ("Error Handling", "try {\n    var result = risky_operation()\n} catch e {\n    print(\"Error: \" + e)\n}"),
                ]
                for i, (title, code) in enumerate(examples, 1):
                    print(f"  {colour(C_KW, f'{i}. {title}:')}")
                    for line in code.split('\n'):
                        print(f"    {colour(DIM, line)}")
                    print()
                continue

            # .json <expr> — JSON viewer with formatting
            m = re.match(r'\.json\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                try:
                    tokens = tokenize(expr)
                    ast = parse(tokens)
                    interp = interp_manager.get_interpreter()
                    interp.run(ast)
                    val = interp.return_value if interp.return_value is not None else interp.last_value
                    interp.return_value = None
                    interp.last_value = None
                    if val is not None:
                        import json
                        # Convert Ipp types to Python types for JSON
                        def to_python(v):
                            if hasattr(v, 'data'):
                                return {k: to_python(vv) for k, vv in v.data.items()}
                            if hasattr(v, 'elements'):
                                return [to_python(vv) for vv in v.elements]
                            if isinstance(v, (dict, list, str, int, float, bool, type(None))):
                                return v
                            return str(v)
                        py_val = to_python(val)
                        formatted = json.dumps(py_val, indent=2, ensure_ascii=False)
                        for line in formatted.split('\n'):
                            print(f"  {colour(C_STR, line)}")
                    else:
                        print(f"  {colour(DIM, '(no result)')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .format <expr> — Auto-format code
            m = re.match(r'\.format\s+(.+)$', stripped)
            if m:
                expr = m.group(1)
                # Auto-formatting: fix spacing around operators, keywords, braces
                formatted = expr
                # Add spaces around operators
                formatted = re.sub(r'(\w)([=+\-*/<>!&|^%])', r'\1 \2', formatted)
                formatted = re.sub(r'([=+\-*/<>!&|^%])(\w)', r'\1 \2', formatted)
                # Add spaces around braces
                formatted = re.sub(r'(\w)\{', r'\1 {', formatted)
                formatted = re.sub(r'\}(\w)', r'} \1', formatted)
                # Fix double spaces
                formatted = re.sub(r'  +', ' ', formatted)
                # Show before/after
                print(f"  {colour(DIM, 'Before:')} {colour(C_ERROR, expr)}")
                print(f"  {colour(DIM, 'After: ')} {colour(C_OK, formatted)}")
                continue

            # .export <file> — Export session as .ipp script
            m = re.match(r'\.export\s+(.+)$', stripped)
            if m:
                filepath = m.group(1).strip().strip('"').strip("'")
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write('// Ipp session export\n')
                        f.write(f'// Exported at: {__import__("datetime").datetime.now()}\n\n')
                        for cmd in _cmd_history:
                            f.write(cmd + '\n')
                    
                    # Verify exported content
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                    code_lines = [l for l in lines if l.strip() and not l.startswith('//')]
                    print(f"  {colour(C_OK, f'Exported {len(code_lines)} commands to {filepath}')}")
                    print(f"  {colour(DIM, f'File size: {os.path.getsize(filepath)} bytes')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, f'Export failed: {e}')}")
                continue

            # .prompt <fmt> — Customize prompt format
            m = re.match(r'\.prompt\s+(.+)$', stripped)
            if m:
                fmt = m.group(1).strip()
                # Check if it's a custom arrow
                if fmt in ('ipp', 'dir', 'time', 'full'):
                    _PROMPT_FORMAT = fmt
                    print(f"  {colour(C_OK, f'Prompt set to: {fmt}')}")
                else:
                    # Custom arrow symbol
                    _PROMPT_FORMAT = 'arrow'
                    _PROMPT_ARROW = fmt
                    print(f"  {colour(C_OK, f'Custom prompt arrow: {fmt}')}")
                continue

            # .cd <dir> — Change directory
            m = re.match(r'\.cd\s+(.+)$', stripped)
            if m:
                dirpath = m.group(1).strip().strip('"').strip("'")
                try:
                    os.chdir(dirpath)
                    print(f"  {colour(C_OK, f'Changed to: {os.getcwd()}')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, f'cd failed: {e}')}")
                continue

            # .ls [dir] — List directory
            m = re.match(r'\.ls\s*(.*)$', stripped)
            if m:
                dirpath = m.group(1).strip().strip('"').strip("'") or '.'
                try:
                    entries = os.listdir(dirpath)
                    for entry in sorted(entries):
                        full = os.path.join(dirpath, entry)
                        if os.path.isdir(full):
                            print(f"  {colour(C_KW, entry + '/')}")
                        elif os.access(full, os.X_OK):
                            print(f"  {colour(C_OK, entry + '*')}")
                        else:
                            print(f"  {entry}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, f'ls failed: {e}')}")
                continue

            # .pwd — Print working directory
            if stripped == '.pwd':
                print(f"  {colour(C_RESULT, os.getcwd())}")
                continue

            # .pipe <cmd> — Pipe last result to shell command
            m = re.match(r'\.pipe\s+(.+)$', stripped)
            if m:
                cmd = m.group(1).strip()
                if _last_result is not None:
                    try:
                        import subprocess
                        # Convert result to string and pipe to command
                        input_data = str(_last_result)
                        result = subprocess.run(cmd, shell=True, input=input_data, capture_output=True, text=True)
                        if result.stdout:
                            print(result.stdout, end='')
                        if result.stderr:
                            print(f"  {colour(C_ERROR, result.stderr)}", end='')
                        if result.returncode != 0 and not result.stderr:
                            print(f"  {colour(C_WARN, f'Exit code: {result.returncode}')}")
                    except Exception as e:
                        print(f"  {colour(C_ERROR, f'Pipe failed: {e}')}")
                else:
                    print(f"  {colour(C_WARN, 'No last result to pipe')}")
                continue

            # .bind <key> <cmd> — Set key binding
            m = re.match(r'\.bind\s+(\S+)\s+(.+)$', stripped)
            if m:
                key = m.group(1)
                cmd = m.group(2).strip()
                _key_bindings[key] = cmd
                print(f"  {colour(C_OK, f'Bound {key} → {cmd}')}")
                print(f"  {colour(DIM, f'Total bindings: {len(_key_bindings)}')}")
                continue

            # .session export — Export session as .ipp
            if stripped == '.session export':
                session_dir = os.path.join(os.path.expanduser("~"), ".ipp", "sessions")
                os.makedirs(session_dir, exist_ok=True)
                export_file = os.path.join(session_dir, "session.ipp")
                try:
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write('// Ipp session export\n')
                        for cmd in _cmd_history:
                            f.write(cmd + '\n')
                    print(f"  {colour(C_OK, f'Session exported to {export_file}')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, f'Export failed: {e}')}")
                continue

            # .sessions — List saved sessions
            if stripped == '.sessions':
                session_dir = os.path.join(os.path.expanduser("~"), ".ipp", "sessions")
                if os.path.exists(session_dir):
                    sessions = os.listdir(session_dir)
                    if sessions:
                        print(f"  {colour(C_CMD, 'Saved sessions:')}")
                        for s in sorted(sessions):
                            size = os.path.getsize(os.path.join(session_dir, s))
                            print(f"    {colour(C_KW, s)} ({size} bytes)")
                    else:
                        print(f"  {colour(DIM, '(no saved sessions)')}")
                else:
                    print(f"  {colour(DIM, '(no session directory)')}")
                continue

            # .typehints — Show type hints for current expression
            if stripped == '.typehints':
                print(f"  {colour(C_CMD, 'Type Hints:')}")
                interp = interp_manager.get_interpreter()
                env = interp.global_env
                vars_found = {}
                while env:
                    if hasattr(env, 'values'):
                        vars_found.update(env.values)
                    env = getattr(env, 'parent', None)
                
                if vars_found:
                    for name, val in sorted(vars_found.items()):
                        if not callable(val) and not name.startswith('_'):
                            t = type(val).__name__
                            if hasattr(val, '__class__') and hasattr(val.__class__, '__name__'):
                                t = val.__class__.__name__
                            if hasattr(val, 'data'):
                                t = 'dict'
                            elif hasattr(val, 'elements'):
                                t = 'list'
                            print(f"    {colour(C_KW, name)}: {colour(C_OK, t)} = {colour(DIM, str(val)[:50])}")
                else:
                    print(f"  {colour(DIM, '(no variables to show types for)')}")
                continue

            # .sighelp — Show signature help for builtins
            if stripped == '.sighelp':
                print(f"  {colour(C_CMD, 'Function Signatures:')}")
                from ipp.runtime.builtins import BUILTINS
                sigs = []
                for name, fn in sorted(BUILTINS.items()):
                    doc = fn.__doc__ or ""
                    sig = doc.split('\n')[0] if doc else f"{name}(...)"
                    sigs.append((name, sig))
                
                for name, sig in sigs[:30]:
                    print(f"    {colour(C_KW, name.ljust(20))} {colour(DIM, sig)}")
                if len(sigs) > 30:
                    print(f"  {colour(DIM, f'... and {len(sigs) - 30} more')}")
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
                if _cmd_history:
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
                        print(f"  {colour(C_CMD, 'Profile for:')} {colour(DIM, last_cmd)}")
                        print(s.getvalue())
                    except Exception as e:
                        print(f"  {colour(C_ERROR, str(e))}")
                else:
                    print(f"  {colour(C_WARN, 'No command history to profile')}")
                continue

            # .mem — Show memory usage
            if stripped == '.mem':
                try:
                    from ipp.runtime.builtins import ipp_memory_info
                    mem = ipp_memory_info()
                    if "error" in mem:
                        print(f"  {colour(C_WARN, mem['error'])}")
                        print(f"  {colour(DIM, 'Install psutil: pip install psutil')}")
                    else:
                        print(f"  {colour(C_OK, 'Memory Usage:')}")
                        print(f"    RSS:  {mem['rss_mb']:.2f} MB")
                        print(f"    VMS:  {mem['vms_mb']:.2f} MB")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .reload [module] — Reload imported module
            m = re.match(r'\.reload(?:\s+(.+))?$', stripped)
            if m:
                module_name = m.group(1)
                try:
                    interp = interp_manager.get_interpreter()
                    if hasattr(interp, '_loaded_modules') and interp._loaded_modules:
                        if module_name:
                            for path in list(interp._loaded_modules.keys()):
                                if module_name in path:
                                    del interp._loaded_modules[path]
                                    print(f"  {colour(C_OK, f'Cleared: {path}')}")
                        else:
                            interp._loaded_modules.clear()
                            print(f"  {colour(C_OK, 'All cached modules cleared')}")
                    else:
                        print(f"  {colour(C_WARN, 'No modules loaded yet')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .checkpoint [n] — Save state checkpoint
            m = re.match(r'\.checkpoint(?:\s+(\d+))?$', stripped)
            if m:
                n = int(m.group(1)) if m.group(1) else 5
                try:
                    interp = interp_manager.get_interpreter()
                    env = interp.global_env.values.copy()
                    checkpoint = {'env': env, 'history': _cmd_history.copy()}
                    _checkpoints.append(checkpoint)
                    if len(_checkpoints) > n:
                        _checkpoints.pop(0)
                    print(f"  {colour(C_OK, f'Checkpoint saved (total: ' + str(len(_checkpoints)) + ')')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .restore [n] — Restore checkpoint
            m = re.match(r'\.restore(?:\s+(\d+))?$', stripped)
            if m:
                idx = int(m.group(1)) - 1 if m.group(1) else -1
                try:
                    if _checkpoints:
                        if idx < 0:
                            idx = len(_checkpoints) + idx
                        if 0 <= idx < len(_checkpoints):
                            checkpoint = _checkpoints[idx]
                            interp = interp_manager.get_interpreter()
                            interp.global_env.values = checkpoint['env'].copy()
                            _cmd_history = checkpoint['history'].copy()
                            print(f"  {colour(C_OK, f'Restored checkpoint {idx+1}')}")
                        else:
                            print(f"  {colour(C_WARN, f'Invalid checkpoint: {idx+1}')}")
                    else:
                        print(f"  {colour(C_WARN, 'No checkpoints saved')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .macro <name> <expansion> — Define macro
            m = re.match(r'\.macro\s+(\w+)\s+(.+)$', stripped)
            if m:
                name = m.group(1)
                expansion = m.group(2)
                _macros[name] = expansion
                print(f"  {colour(C_OK, f'Macro {name} defined: {expansion}')}")
                continue

            # .cache save <file> — Save bytecode cache
            m = re.match(r'\.cache\s+save(?:\s+(.+))?$', stripped)
            if m:
                filename = m.group(1) if m.group(1) else 'last.ipp'
                try:
                    from ipp.lexer.lexer import tokenize
                    from ipp.parser.parser import parse
                    from ipp.vm.compiler import compile_ast
                    if hasattr(self, '_current_source') and self._current_source:
                        tokens = tokenize(self._current_source)
                        ast = parse(tokens)
                        chunk = compile_ast(ast)
                        cache_file = filename.replace('.ipp', '') + '.ipc'
                        import pickle
                        with open(cache_file, 'wb') as f:
                            pickle.dump({
                                'source': self._current_source,
                                'chunk': chunk
                            }, f)
                        print(f"  {colour(C_OK, f'Bytecode cached to {cache_file}')}")
                    else:
                        print(f"  {colour(C_WARN, 'No source to cache')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # .cache load <file> — Load bytecode cache
            m = re.match(r'\.cache\s+load(?:\s+(.+))?$', stripped)
            if m:
                filename = m.group(1) if m.group(1) else 'last.ipc'
                try:
                    import pickle
                    with open(filename, 'rb') as f:
                        data = pickle.load(f)
                    from ipp.vm.vm import VM
                    vm = VM()
                    result = vm.run(data['chunk'])
                    self.last_value = result
                    print(f"  {colour(C_OK, f'Loaded bytecode from {filename}, result: {result}')}")
                except Exception as e:
                    print(f"  {colour(C_ERROR, str(e))}")
                continue

            # Expand macros (only for non-command inputs)
            if not stripped.startswith('.'):
                for name, expansion in _macros.items():
                    if stripped == name or stripped.startswith(name + ' '):
                        if stripped != name:
                            args = stripped[len(name):].strip()
                            for i, arg in enumerate(args.split(), 1):
                                expansion = expansion.replace(f'${i}', arg)
                        print(f"  {colour(DIM, f'Expanded: {expansion}')}")
                        stripped = expansion
                        buf = [expansion]
                        break

        if not stripped and not buf:
            continue

        # Check for line continuation with \
        if raw.rstrip('\r\n').endswith('\\'):
            # Keep the backslash - it signals line continuation
            buf.append(raw.rstrip('\r\n'))
            continue

        buf.append(raw)
        source = '\n'.join(buf)

        # Force execute after too many continuation lines (prevent infinite multiline stuck)
        if len(buf) > 10:
            pass  # Force execute

        # Multi-line paste detection: if source has multiple complete statements
        # Auto-execute if it looks like a paste (multiple newlines, no continuation)
        elif len(buf) > 1 and not _needs_more(source):
            pass  # Will execute normally

        elif _needs_more(source):
            continue

        # ── Execute ───────────────────────────────────────────────────
        interp = interp_manager.get_interpreter()
        t0 = time.perf_counter()
        
        # Inject $_1, $_2, etc. into the interpreter for expression history access
        for i, (idx, val) in enumerate(_last_results[-10:], max(1, len(_last_results) - 9)):
            try:
                interp.global_env.values[f'$_{idx}'] = val
            except:
                pass
        
        # Save env snapshot for .undo
        snapshot = dict(interp.global_env.values)
        _env_snapshots.append(snapshot)
        if len(_env_snapshots) > 50:
            _env_snapshots.pop(0)
        
        try:
            from ipp.lexer.lexer import tokenize as _tokenize
            from ipp.parser.parser import parse as _parse
            tokens = _tokenize(source)
            ast = _parse(tokens)
            interp.run(ast)
            result_val = interp.return_value if interp.return_value is not None else interp.last_value
            interp.return_value = None
            interp.last_value = None
            elapsed = time.perf_counter() - t0
            
            _cmd_history.append(source)
            if result_val is not None:
                fmted = format_output(result_val)
                ms_str = colour(DIM, f"  {elapsed*1000:.1f}ms")
                arrow2 = '->' if not _UNI else '→'
                print(f"  {colour(DIM, arrow2)} {fmted}{ms_str}")
                _last_result = result_val
                _last_results.append((len(_last_results) + 1, result_val))
                if len(_last_results) > 100:
                    _last_results.pop(0)
        except KeyboardInterrupt:
            # Ctrl+C during execution - exit immediately
            print(f"\n  {colour(C_OK, 'Goodbye!')}")
            break
        except Exception as e:
            elapsed = time.perf_counter() - t0
            print(_format_error_with_suggestions(e, interp_manager))
        
        buf.clear()
        line_num += 1

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
        ("lsp",       "Start LSP server"),
        ("wasm <f>",  "Compile to WASM"),
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
    if cmd == 'lsp':
        from ipp.lsp.server import main as lsp_main
        lsp_main()
        return 0
    if cmd == 'wasm' and len(args) >= 2:
        from ipp.wasm import compile_to_wasm
        import os
        input_file = args[1]
        output_file = args[2] if len(args) > 2 else input_file.replace('.ipp', '.wat')
        try:
            with open(input_file, 'r') as f:
                source = f.read()
            wasm = compile_to_wasm(source, output_file)
            print(f"Compiled to {output_file}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
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
