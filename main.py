#!/usr/bin/env python3
"""
Ipp - A simple, beginner-friendly scripting language for game development
"""

import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.interpreter.interpreter import Interpreter

REPL_VERSION = "0.5.1"

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
    return min(shutil.get_terminal_size().columns or 60, 60)


IPP_LOGO = """
   ___ ___ _  _ ___ ___ ___ 
  / __|_ _| \\| |   \\| __|
 | (_ || || .` | |) | _| 
  \\___|___|_|\\_|___/|_|   
"""


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


def run_repl():
    """Run the Ipp REPL"""
    width = get_terminal_width()
    
    print(c(IPP_LOGO, "cyan"))
    print(c(f"  Ipp {REPL_VERSION}", "cyan", ["bold"]) + c(" - game scripting language", "white"))
    print(c("=" * width, "cyan"))
    print()
    print(c("  Type ", "white") + c("help()", "yellow") + c(" for commands, ", "white") + c("exit()", "red") + c(" to quit", "white"))
    print()
    
    buffer = []
    interpreter = Interpreter()
    
    while True:
        try:
            if buffer:
                prompt = c("...", "yellow") + " "
            else:
                prompt = c(">>>", "green", ["bold"]) + " "
            
            line = input(prompt)
            
            if not buffer and line.strip() in ("exit()", "exit", "quit"):
                print(c("Goodbye!", "green"))
                break
            
            if not buffer and line.strip() == "help()":
                width = get_terminal_width()
                print(c("-" * width, "cyan"))
                print(c("  Commands:", "white", ["bold"]))
                print(c("    exit()          ", "yellow") + c("- Exit the REPL", "white"))
                print(c("    clear()         ", "yellow") + c("- Clear buffer", "white"))
                print(c("    help()          ", "yellow") + c("- Show this help", "white"))
                print()
                print(c("  Features:", "white", ["bold"]))
                print(c("    Variables       ", "green") + c("- var, let", "white"))
                print(c("    Control Flow    ", "green") + c("- if/elif/else, for, while, match", "white"))
                print(c("    Functions       ", "green") + c("- func, closures", "white"))
                print(c("    Classes         ", "green") + c("- class, init, inheritance", "white"))
                print(c("    Operators       ", "green") + c("- +, -, *, /, //, %, ^, &, |, ^, <<, >>", "white"))
                print(c("    Ternary         ", "green") + c("- condition ? true : false", "white"))
                print(c("    Error Handling  ", "green") + c("- try/catch/finally", "white"))
                print(c("    Modules         ", "green") + c("- import", "white"))
                print(c("    Lists/Dicts     ", "green") + c("- [...], {...}", "white"))
                print(c("    Vectors         ", "green") + c("- Vector2, Vector3", "white"))
                print(c("    REPL            ", "green") + c("- Multiline support", "white"))
                print(c("-" * width, "cyan"))
                continue
            
            if line.strip() == "clear()":
                buffer = []
                print(c("Buffer cleared.", "yellow"))
                continue
            
            if not line.strip() and not buffer:
                continue
            
            buffer.append(line)
            source = "\n".join(buffer)
            
            if not check_brace_balance(source):
                continue
            
            try:
                tokens = tokenize(source)
                ast = parse(tokens)
                interpreter.run(ast)
                buffer = []
                if interpreter.return_value is not None:
                    print(c(interpreter.return_value, "white"))
                interpreter.return_value = None
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
