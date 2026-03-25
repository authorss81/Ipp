#!/usr/bin/env python3
"""
Ipp - A simple, beginner-friendly scripting language for game development
"""

import sys
import os
import shutil
import builtins

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.interpreter.interpreter import Interpreter

REPL_VERSION = "0.11.2"

try:
    from termcolor import colored
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    def colored(text, color=None, attrs=None):
        return text


def c(text, color=None, attrs=None):
    """Color helper"""
    if HAS_COLOR and color:
        return colored(text, color, attrs=attrs or [])
    return text


def get_terminal_width():
    """Get terminal width"""
    return min(shutil.get_terminal_size().columns or 60, 66)


IPP_LOGO = """
IIIIII  ppppp   ppppp
  I     p    p  p    p
  I     ppppp   ppppp
  I     p       p
IIIIII  p       p"""


def run_file(filepath):
    """Run an Ipp source file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return 1
    except Exception as e:
        print(f"Error reading file: {e}")
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
        print(f"Error: {e}")
        return 1
    
    return 0


def check_file(filepath):
    """Syntax check an Ipp source file without running"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return 1
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1
    
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
        print(f"Syntax OK: {filepath}")
        return 0
    except Exception as e:
        print(f"Syntax Error: {e}")
        return 1


def check_brace_balance(source):
    """Check if braces/brackets/parentheses are balanced"""
    stack = []
    for char in source:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack:
                return False
            opening = stack.pop()
            expected = {'(': ')', '[': ']', '{': '}'}[opening]
            if char != expected:
                return False
    return len(stack) == 0


def is_statement_complete(source):
    """Check if statement is complete"""
    source = source.strip()
    if not source:
        return False
    return check_brace_balance(source)


def get_interpreter_globals(interpreter):
    """Get all defined variables and functions from interpreter"""
    if hasattr(interpreter, 'environment') and interpreter.environment:
        env = interpreter.environment
        result = {}
        while env:
            if hasattr(env, 'values'):
                result.update(env.values)
            env = env.parent
        return result
    return {}


def show_help():
    """Show help message"""
    width = get_terminal_width()
    print(c("=" * width, "cyan"))
    print(c("              Ipp REPL  --  Commands", "white", ["bold"]))
    print(c("=" * width, "cyan"))
    
    sections = [
        ("Session", [
            ".help                   Show this help",
            ".vars                   List all defined variables", 
            ".clear                  Reset session variables",
            "exit  quit              Leave the REPL"
        ]),
        ("Features", [
            "Variables               var, let",
            "Control Flow            if/elif/else, for, while, match",
            "Functions               func, closures",
            "Classes                 class, init, inheritance",
            "Operators               +, -, *, /, //, %, ^, &, |, ^, <<, >>",
            "Ternary                 condition ? true : false",
            "Error Handling          try/catch/finally",
            "Lists/Dicts             [...], {...}",
            "Vectors                 Vector2, Vector3"
        ]),
        ("Tips", [
            "Multi-line: Open a { or ( and press Enter",
            "Up/Down: Navigate history",
            "Auto-print: Bare expressions print their value"
        ])
    ]
    
    for title, items in sections:
        print(c(f"  -- {title} " + "-" * (width - 12 - len(title)), "cyan"))
        for item in items:
            print(c(f"  {item}", "white"))
        print()


def run_repl():
    """Run the Ipp REPL"""
    width = get_terminal_width()
    
    print(c(IPP_LOGO, "cyan"))
    print()
    print(c("+" + "=" * (width - 2) + "+", "cyan"))
    print(c(f"|  >>  A scripting language for game development  v{REPL_VERSION}".ljust(width - 1) + "|", "white", ["bold"]))
    print(c("+" + "=" * (width - 2) + "+", "cyan"))
    print(c("|  Python 3.8+                                     ".ljust(width - 1) + "|", "white"))
    print(c("+" + "=" * (width - 2) + "+", "cyan"))
    print()
    print(c("  .help  commands  ·  exit  quit", "white"))
    print()
    
    buffer = []
    interpreter = Interpreter()
    
    while True:
        try:
            if buffer:
                prompt = c("...", "yellow") + " "
            else:
                prompt = c(">>>", "green", ["bold"]) + " "
            
            line_input = input(prompt)
            
            # Check commands
            is_cmd = line_input.strip() in ("exit()", "exit", "quit", ".exit", ".quit", ".help", ".vars", ".clear", "clear()")
            if is_cmd and not buffer:
                if line_input.strip() in ("exit()", "exit", "quit", ".exit", ".quit"):
                    print(c("Goodbye!", "green"))
                    break
                
                if line_input.strip() == ".help":
                    show_help()
                    continue
                
                if line_input.strip() == ".vars":
                    width = get_terminal_width()
                    vars = get_interpreter_globals(interpreter)
                    print(c("=" * width, "cyan"))
                    print(c(f"  Variables ({len(vars)} defined)", "white", ["bold"]))
                    print(c("=" * width, "cyan"))
                    for name, val in sorted(vars.items()):
                        val_type = type(val).__name__
                        print(c(f"  {name}".ljust(20), "green") + c(f":{val_type}", "cyan"))
                    print(c("=" * width, "cyan"))
                    continue
                
                if line_input.strip() == ".clear":
                    buffer = []
                    interpreter = Interpreter()
                    print(c("Session cleared.", "yellow"))
                    continue
            
            if line_input.strip() == "clear()":
                buffer = []
                print(c("Buffer cleared.", "yellow"))
                continue
            
            if not line_input.strip() and not buffer:
                continue
            
            buffer.append(line_input)
            source = "\n".join(buffer)
            
            # Check if statement is complete (balanced braces)
            if not is_statement_complete(source):
                continue
            
            try:
                tokens = tokenize(source)
                ast = parse(tokens)
                interpreter.run(ast)
                buffer = []
                
                # Auto-print return values and expression results
                if interpreter.return_value is not None:
                    print(c(f"  -> {interpreter.return_value}", "white"))
                elif interpreter.last_value is not None:
                    print(c(f"  -> {interpreter.last_value}", "white"))
                interpreter.return_value = None
                interpreter.last_value = None
                
            except Exception as e:
                error_msg = str(e)
                if "Expect" in error_msg or "Parse error" in error_msg:
                    continue
                else:
                    buffer = []
                    print(c(f"[Error] {e}", "red"))
                    
        except KeyboardInterrupt:
            print()
            if buffer:
                buffer = []
                print(c("^C Buffer cleared.", "yellow"))
            else:
                break
        except EOFError:
            break
        except Exception as e:
            buffer = []
            print(c(f"[Error] {e}", "red"))


def print_help():
    """Print help message"""
    print("Ipp - A simple scripting language for game development")
    print()
    print("Usage: ipp [command] [options]")
    print()
    print("Commands:")
    print("  run <file>      Run an Ipp script file")
    print("  check <file>   Check syntax without running")
    print("  repl           Start the interactive REPL")
    print()
    print("Options:")
    print("  -h, --help     Show this help message")
    print("  -v, --version  Show version information")


def print_version():
    """Print version information"""
    print(f"Ipp {REPL_VERSION}")
    print("A beginner-friendly scripting language for game development")


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
    elif cmd in ("run", "repl", "check"):
        if len(sys.argv) < 3 and cmd != "repl":
            print(f"Error: '{cmd}' requires a file argument")
            print(f"Usage: ipp {cmd} <file>")
            return 1
        
        if cmd == "run":
            return run_file(sys.argv[2])
        elif cmd == "check":
            return check_file(sys.argv[2])
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
