#!/usr/bin/env python3
"""
Ipp - A simple, beginner-friendly scripting language for game development
"""

import sys
import os
import shutil
import builtins
import re
import unicodedata
import atexit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.interpreter.interpreter import Interpreter

REPL_VERSION = "1.0.1"

try:
    from termcolor import colored
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    def colored(text, color=None, attrs=None):
        return text

try:
    import readline
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

USE_UNICODE = sys.stdout.isatty() and sys.platform != 'win32'

WIDTH = 60

GRADIENT = [
    51, 51, 45, 45, 39, 39, 33, 33, 57, 57, 93, 93, 
    129, 129, 171, 171, 205, 205, 213, 213
]

KEYWORDS = [
    "var", "let", "func", "class", "if", "else", "elif", "for", 
    "while", "match", "case", "default", "try", "catch", "finally", 
    "throw", "return", "break", "continue", "import", "as", "from",
    "nil", "true", "false", "self", "this", "enum", "static"
]

BUILTINS = [
    "print", "len", "type", "range", "random", "randint", "randfloat",
    "choice", "shuffle", "abs", "min", "max", "sum", "round", "floor", 
    "ceil", "sqrt", "pow", "sin", "cos", "tan", "asin", "acos", "atan",
    "atan2", "log", "log10", "degrees", "radians", "pi", "e", "factorial",
    "gcd", "lcm", "hypot", "lerp", "clamp", "map_range", "distance",
    "normalize", "dot", "cross", "sign", "smoothstep", "move_towards",
    "str", "int", "float", "bool", "to_number", "to_string", "to_int",
    "to_float", "to_bool", "split", "join", "upper", "lower", "strip",
    "replace", "starts_with", "ends_with", "find", "contains", "count",
    "substring", "index_of", "char_at", "ascii", "from_ascii",
    "json_parse", "json_stringify", "regex_match", "regex_search", "regex_replace",
    "datetime", "datetime_create", "path", "path_dirname", "path_basename",
    "path_join", "path_exists", "md5", "sha256", "sha1", "sha512", "hash",
    "base64_encode", "base64_decode", "csv_parse", "csv_parse_dict", "csv_to_string",
    "os_platform", "env_get", "env_set", "os_cwd", "os_chdir",
    "complex", "vec2", "vec3", "color", "rect", "deque", "ordict", "log",
    "xml_parse", "xml_to_string", "toml_parse", "toml_to_string",
    "yaml_parse", "yaml_to_string", "uuid4", "uuid1", "uuid_nil",
    "url_parse", "url_encode", "url_decode", "url_query_parse",
    "http_get", "http_post", "gzip_compress", "gzip_decompress",
    "zip_create", "zip_extract", "thread", "thread_sleep",
    "input", "exit", "assert", "file_exists", "read_file", "write_file",
    "mkdir", "list_dir", "delete_file", "time", "sleep", "clock"
]

def _c(code, text):
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"

def _256c(n):
    return f"38;5;{n}"

def grad_line(text, width=WIDTH):
    chars = []
    idx = 0
    for ch in text:
        if ch in ' \t':
            chars.append(ch)
        else:
            c = GRADIENT[idx % len(GRADIENT)]
            chars.append(f"\033[{_256c(c)}m{ch}\033[0m")
            idx += 1
    line = "".join(chars)
    plain = re.sub(r'\033\[[0-9;]*m', '', line)
    dw = sum(2 if unicodedata.east_asian_width(ch) in ('W','F') else 1 for ch in plain)
    pad = max(0, width - dw)
    return line + " " * pad

def box_row(content, width=WIDTH):
    plain = re.sub(r'\033\[[0-9;]*m', '', content)
    dw = sum(2 if unicodedata.east_asian_width(ch) in ('W','F') else 1 for ch in plain)
    pad = max(0, width - dw)
    if USE_UNICODE:
        return f"\u2566{content}{' ' * pad}\u2569"
    return f"|{content}{' ' * pad}|"

def box_line(width=WIDTH):
    return f"{'=' * (width + 4)}"

def box_double_line(width=WIDTH):
    return f"{'=' * (width + 4)}"

def box_single(width=WIDTH):
    return f"{' ' * (width + 4)}"

def c(text, color=None, attrs=None):
    if HAS_COLOR and color:
        if isinstance(color, int):
            return _c(_256c(color), text)
        return colored(text, color, attrs=attrs or [])
    return text

CYAN = lambda t: _c("36", t)
GREEN = lambda t: _c("32", t)
YELLOW = lambda t: _c("33", t)
RED = lambda t: _c("31", t)
MAGENTA = lambda t: _c("35", t)
BLUE = lambda t: _c("34", t)
WHITE = lambda t: _c("37", t)
DIM = lambda t: _c("2", t)
BOLD = lambda t: _c("1", t)
ORANGE = lambda t: _c(_256c(214), t)
PURPLE = lambda t: _c(_256c(135), t)

def get_terminal_width():
    return min(shutil.get_terminal_size().columns or 60, WIDTH + 4)

def highlight_output(text):
    if not sys.stdout.isatty():
        return text
    
    kw_pat = re.compile(r'\b(' + '|'.join(KEYWORDS) + r')\b')
    num_pat = re.compile(r'\b\d+\.?\d*\b')
    str_pat = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"')
    cmnt_pat = re.compile(r'#.*$')
    fn_pat = re.compile(r'\b([a-z_]\w*)\s*(?=\()')
    bool_pat = re.compile(r'\b(true|false|nil)\b')
    
    lines = text.split('\n')
    result = []
    
    for line in lines:
        r = cmnt_pat.sub(lambda m: DIM(m.group()), line)
        r = str_pat.sub(lambda m: GREEN(m.group()), r)
        r = bool_pat.sub(lambda m: MAGENTA(m.group()), r)
        r = num_pat.sub(lambda m: ORANGE(m.group()), r)
        r = kw_pat.sub(lambda m: CYAN(m.group()), r)
        r = fn_pat.sub(lambda m: BLUE(m.group(1)), r)
        result.append(r)
    
    return '\n'.join(result)

IPP_ASCII = [
    grad_line("  IIIIII  ppppp   ppppp  ", WIDTH),
    grad_line("    I     p    p  p    p ", WIDTH),
    grad_line("    I     ppppp   ppppp  ", WIDTH),
    grad_line("    I     p       p      ", WIDTH),
    grad_line("  IIIIII  p       p      ", WIDTH),
]

def print_banner():
    width = WIDTH + 4
    print(box_line(width))
    for line in IPP_ASCII:
        print(f"  {line}")
    print(box_double_line(width))
    
    subtitle = f"  >> A scripting language for game development  v{REPL_VERSION}"
    print(f"  {subtitle.ljust(width - 1)}")
    print(f"  {'Python 3.8+'.ljust(width - 1)}")
    print(box_double_line(width))
    print()
    print(f"  {DIM('.help')} for commands  ·  {DIM('exit')} to quit  ·  {DIM('Tab')} autocomplete")
    print()

def print_help_box():
    width = WIDTH + 4
    print()
    print(box_line(width))
    print(f"  {BOLD('Commands').ljust(width - 1)}")
    print(box_double_line(width))
    
    commands = [
        (".help", "Show this help"),
        (".vars", "List defined variables"),
        (".clear", "Reset session"),
        (".types", "Show type system"),
        ("exit / quit", "Leave REPL"),
    ]
    for cmd, desc in commands:
        print(f"    {CYAN(cmd.ljust(15))}{WHITE(desc.ljust(width - 22))}")
    
    print(box_double_line(width))
    print()
    print(f"  {BOLD('Quick Reference:')}")
    print(f"    {CYAN('var')} x = 10              {DIM('# variable')}")
    print(f"    {CYAN('func')} add(a, b) = a + b   {DIM('# function')}")
    print(f"    {CYAN('class')} Point {{ ... }}     {DIM('# class')}")
    print(f"    {DIM('>>> 2 ** 10')}              {DIM('# auto-prints: 1024')}")
    print()

def print_types_box():
    width = WIDTH + 4
    print()
    print(box_line(width))
    print(f"  {BOLD('Type System').ljust(width - 1)}")
    print(box_double_line(width))
    
    types_info = [
        ("number", "int/float (unified)"),
        ("string", "text values"),
        ("bool", "true/false"),
        ("nil", "null value"),
        ("list", "[1, 2, 3]"),
        ("dict", "{key: value}"),
        ("tuple", "(1, 2, 3)"),
        ("function", "first-class"),
        ("class", "user-defined"),
        ("vec2/vec3", "Vector2/Vector3"),
        ("color", "RGBA color"),
        ("rect", "Rectangle"),
    ]
    
    for t_type, desc in types_info:
        print(f"    {ORANGE(t_type.ljust(12))}{WHITE(desc.ljust(width - 20))}")
    
    print(box_double_line(width))
    print()

class IppCompleter:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.matches = []
    
    def complete(self, text, state):
        if state == 0:
            buf = readline.get_line_buffer()
            
            dot_match = re.match(r'.*?(\w+)\.([\w]*)$', buf)
            if dot_match:
                obj_name = dot_match.group(1)
                prefix = dot_match.group(2)
                members = self._get_member_names(obj_name)
                self.matches = [m for m in members if m.startswith(prefix)]
            else:
                words = buf.split()
                if not words or (len(words) == 1 and not buf.endswith(' ')):
                    candidates = set(KEYWORDS + BUILTINS)
                    candidates.update(self._get_user_names())
                    self.matches = sorted([c for c in candidates if c.startswith(text)])
                else:
                    self.matches = []
        
        try:
            return self.matches[state]
        except IndexError:
            return None
    
    def _get_user_names(self):
        names = set()
        if hasattr(self.interpreter, 'global_env'):
            env = self.interpreter.global_env
            while env:
                if hasattr(env, 'values'):
                    names.update(env.values.keys())
                env = env.parent
        return names
    
    def _get_member_names(self, obj_name):
        try:
            if hasattr(self.interpreter, 'global_env'):
                obj = None
                env = self.interpreter.global_env
                while env:
                    if hasattr(env, 'values') and obj_name in env.values:
                        obj = env.values[obj_name]
                        break
                    env = env.parent
                
                if obj is None:
                    return []
                
                members = []
                if hasattr(obj, 'fields'):
                    members.extend(obj.fields.keys())
                if hasattr(obj, 'ipp_class') and hasattr(obj.ipp_class, 'methods'):
                    members.extend(obj.ipp_class.methods.keys())
                if hasattr(obj, '__dict__'):
                    members.extend(obj.__dict__.keys())
                if hasattr(obj, '_env') and hasattr(obj._env, 'values'):
                    members.extend(obj._env.values.keys())
                
                return sorted(set(members))
        except:
            pass
        return []

def setup_readline(interpreter):
    if not HAS_READLINE:
        return None
    
    try:
        histdir = os.path.join(os.path.expanduser("~"), ".ipp")
        os.makedirs(histdir, exist_ok=True)
        histfile = os.path.join(histdir, "history")
        
        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            pass
        
        readline.set_history_length(1000)
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set completion-ignore-case on")
        readline.set_completer_delims(" \t\n`~!@#$%^&*()-=+[]{}|;:',.<>?/")
        
        completer = IppCompleter(interpreter)
        readline.set_completer(completer.complete)
        
        atexit.register(readline.write_history_file, histfile)
        
        return completer
    except Exception:
        return None

def run_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"{RED('[Error]')} File not found: {filepath}")
        return 1
    except Exception as e:
        print(f"{RED('[Error]')} Cannot read file: {e}")
        return 1
    
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
        interpreter = Interpreter()
        interpreter.current_file = os.path.abspath(filepath)
        interpreter.run(ast)
        if interpreter.return_value is not None:
            print(interpreter.return_value)
    except Exception as e:
        print(f"{RED('[Error]')} {e}")
        return 1
    
    return 0

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"{RED('[Error]')} File not found: {filepath}")
        return 1
    except Exception as e:
        print(f"{RED('[Error]')} Cannot read file: {e}")
        return 1
    
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
        print(f"{GREEN('[OK]')} Syntax OK: {filepath}")
        return 0
    except Exception as e:
        print(f"{RED('[Error]')} Parse error: {e}")
        return 1

def lint_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"{RED('[Error]')} File not found: {filepath}")
        return 1
    except Exception as e:
        print(f"{RED('[Error]')} Cannot read file: {e}")
        return 1
    
    issues = []
    lines = source.split('\n')
    
    for i, line in enumerate(lines, 1):
        stripped = line.rstrip()
        
        if len(stripped) > 120:
            issues.append(f"{YELLOW('warning')}:{i}: Line too long ({len(stripped)} > 120)")
        
        if '\t' in line:
            issues.append(f"{YELLOW('warning')}:{i}: Use spaces instead of tabs")
        
        if stripped.endswith(' ') and stripped.startswith('#'):
            issues.append(f"{YELLOW('warning')}:{i}: Trailing whitespace in comment")
    
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
    except Exception as e:
        issues.append(f"{RED('error')}:0: Parse error: {e}")
    
    if issues:
        for issue in issues:
            print(f"  {issue}")
        print(f"\n{RED('[Lint]')} {len(issues)} issue(s) found")
        return 1
    else:
        print(f"{GREEN('[OK]')} No issues found: {filepath}")
        return 0

def check_brace_balance(source):
    stack = []
    in_str = False
    for ch in source:
        if ch == '"' and (len(stack) == 0 or stack[-1] != '\\'):
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack:
                return False
            opening = stack.pop()
            expected = {'(': ')', '[': ']', '{': '}'}[opening]
            if ch != expected:
                return False
    return len(stack) == 0

def is_statement_complete(source):
    source = source.strip()
    if not source:
        return False
    return check_brace_balance(source)

def get_interpreter_globals(interpreter):
    if hasattr(interpreter, 'environment') and interpreter.environment:
        env = interpreter.environment
        result = {}
        while env:
            if hasattr(env, 'values'):
                result.update(env.values)
            env = env.parent
        return result
    return {}

def show_vars(interpreter):
    width = WIDTH + 4
    vars_dict = get_interpreter_globals(interpreter)
    
    print()
    print(box_line(width))
    print(f"  {BOLD('Variables').ljust(width - 1)}")
    print(f"  {DIM(f'{len(vars_dict)} defined').ljust(width - 1)}")
    print(box_double_line(width))
    
    for name, val in sorted(vars_dict.items()):
        val_type = type(val).__name__
        if hasattr(val, '__class__'):
            val_type = val.__class__.__name__
        
        type_color = {
            'int': ORANGE,
            'float': ORANGE,
            'str': GREEN,
            'bool': MAGENTA,
            'list': CYAN,
            'dict': CYAN,
            'function': PURPLE,
            'IppClass': PURPLE,
            'IppInstance': PURPLE,
        }.get(val_type, WHITE)
        
        val_str = str(val)[:30] + "..." if len(str(val)) > 30 else str(val)
        line = f"  {GREEN(name.ljust(18))}{type_color(val_type.ljust(10))}{DIM(val_str)}"
        plain = re.sub(r'\033\[[0-9;]*m', '', line)
        dw = sum(2 if unicodedata.east_asian_width(ch) in ('W','F') else 1 for ch in plain)
        pad = max(0, width - dw - 2)
        print(f"  {line}{' ' * pad}")
    
    print(box_double_line(width))
    print()

def run_repl():
    interpreter = Interpreter()
    completer = setup_readline(interpreter)
    
    print_banner()
    
    buffer = []
    multiline_count = 0
    
    while True:
        try:
            if buffer:
                multiline_count += 1
                prompt = f"{DIM('...' + str(multiline_count))} "
            else:
                multiline_count = 0
                prompt = f"{GREEN('>>> ')}"
            
            line_input = input(prompt)
            
            cmd = line_input.strip()
            
            if not buffer and cmd in ("exit", "exit()", "quit", ".exit", ".quit"):
                print(f"{GREEN('[Ipp]')} Goodbye!")
                break
            
            if not buffer:
                if cmd == ".help":
                    print_help_box()
                    continue
                if cmd == ".vars":
                    show_vars(interpreter)
                    continue
                if cmd == ".types":
                    print_types_box()
                    continue
                if cmd in (".clear", "clear()"):
                    buffer = []
                    interpreter = Interpreter()
                    if completer:
                        completer.interpreter = interpreter
                    print(f"{YELLOW('[Ipp]')} Session cleared.")
                    print()
                    continue
            
            if cmd == "clear()" and buffer:
                buffer = []
                multiline_count = 0
                print(f"{DIM('[Buffer cleared]')}")
                continue
            
            if not cmd and not buffer:
                continue
            
            buffer.append(line_input)
            source = "\n".join(buffer)
            
            if not is_statement_complete(source):
                continue
            
            try:
                tokens = tokenize(source)
                ast = parse(tokens)
                interpreter.run(ast)
                buffer = []
                multiline_count = 0
                
                output = None
                if interpreter.return_value is not None:
                    output = interpreter.return_value
                elif interpreter.last_value is not None:
                    output = interpreter.last_value
                
                if output is not None:
                    output_str = highlight_output(str(output))
                    print(f"  {DIM('->')} {output_str}")
                
                interpreter.return_value = None
                interpreter.last_value = None
                
            except Exception as e:
                buffer = []
                multiline_count = 0
                error_msg = str(e)
                
                if "Expect" in error_msg or "at line 0" not in error_msg and "Parse error" in error_msg:
                    pass
                else:
                    print(f"{RED('[Error]')} {error_msg}")
                    
        except KeyboardInterrupt:
            print()
            if buffer:
                buffer = []
                multiline_count = 0
                print(f"{YELLOW('[Ctrl+C]')} Buffer cleared.")
            else:
                print(f"{DIM('[Ctrl+C]')} Press Ctrl+D or type {CYAN('exit')} to quit.")
        except EOFError:
            print()
            print(f"{GREEN('[Ipp]')} Goodbye!")
            break
        except Exception as e:
            buffer = []
            multiline_count = 0
            print(f"{RED('[Error]')} {e}")

def print_help():
    print(f"""
{BOLD('Ipp')} - A scripting language for game development v{REPL_VERSION}

{BOLD('Usage:')} ipp [command] [options] [file]

{BOLD('Commands:')}
  run <file>      Run an Ipp script
  check <file>    Check syntax
  lint <file>     Lint code
  repl            Start REPL

{BOLD('Options:')}
  -h, --help      Show this help
  -v, --version   Show version

{BOLD('Examples:')}
  ipp script.ipp
  ipp run game.ipp
  ipp check config.ipp
""")

def print_version():
    print(f"Ipp v{REPL_VERSION}")
    print("A beginner-friendly scripting language for game development")
    print()
    print("Features: classes, closures, list comprehensions, match, try/catch")

def main():
    if len(sys.argv) == 1:
        run_repl()
        return 0
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    
    if cmd in ("--help", "-h"):
        print_help()
        return 0
    elif cmd in ("--version", "-v"):
        print_version()
        return 0
    elif cmd in ("run", "repl", "check", "lint"):
        if len(sys.argv) < 3 and cmd != "repl":
            print(f"{RED('[Error]')} '{cmd}' requires a file argument")
            print(f"Usage: ipp {cmd} <file>")
            return 1
        
        if cmd == "run":
            return run_file(sys.argv[2])
        elif cmd == "check":
            return check_file(sys.argv[2])
        elif cmd == "lint":
            return lint_file(sys.argv[2])
        elif cmd == "repl":
            run_repl()
            return 0
    elif cmd and not cmd.startswith("-"):
        return run_file(cmd)
    else:
        print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
