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

REPL_VERSION = "v0.5.0"


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
    """Run the Ipp REPL with stylish Gemini-like UI"""
    width = min(shutil.get_terminal_size().columns or 60, 60)
    
    print("=" * width)
    print(f"  Ipp {REPL_VERSION} -- game scripting language")
    print("=" * width)
    print()
    print("  Type help() for commands, exit() to quit")
    print()
    
    buffer = []
    interpreter = Interpreter()  # Persistent interpreter for REPL
    
    while True:
        try:
            if buffer:
                prompt = "... "
            else:
                prompt = "ipp> "
            
            line = input(prompt)
            
            if not buffer and line.strip() in ("exit()", "exit", "quit"):
                print("Goodbye!")
                break
            
            if not buffer and line.strip() == "help()":
                width = min(shutil.get_terminal_size().columns or 60, 60)
                print("-" * width)
                print("  Commands:")
                print("    exit()          - Exit the REPL")
                print("    clear()         - Clear buffer")
                print("    help()          - Show this help")
                print()
                print("  Features:")
                print("    Variables       - var, let")
                print("    Control Flow    - if/elif/else, for, while, match")
                print("    Functions       - func, closures")
                print("    Classes         - class, init, inheritance")
                print("    Operators       - +, -, *, /, //, %, ^, &, |, ^, <<, >>")
                print("    Ternary         - condition ? true : false")
                print("    Error Handling  - try/catch/finally")
                print("    Modules         - import")
                print("    Lists/Dicts     - [...], {...}")
                print("    Vectors         - Vector2, Vector3")
                print("    REPL            - Multiline support")
                print("-" * width)
                continue
            
            if line.strip() == "clear()":
                buffer = []
                print("Buffer cleared.")
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
                    print(interpreter.return_value)
                interpreter.return_value = None  # Reset return value
            except Exception as e:
                error_msg = str(e)
                if "Expect" in error_msg or "Parse error" in error_msg:
                    continue
                else:
                    buffer = []
                    print(f"[Error] {e}")
                    
        except KeyboardInterrupt:
            print()
            if buffer:
                buffer = []
                print("^C Buffer cleared.")
            else:
                break
        except EOFError:
            break
        except Exception as e:
            buffer = []
            print(f"[Error] {e}")


def print_help():
    """Print help message"""
    print("""Ipp - A simple scripting language for game development

Usage: ipp [command] [options]

Commands:
  run <file>      Run an Ipp script file
  check <file>   Check syntax without running
  repl           Start the interactive REPL

Options:
  -h, --help     Show this help message
  -v, --version  Show version information

Examples:
  ipp hello.ipp          Run a script
  ipp run game.ipp      Run a game script
  ipp check script.ipp  Check syntax
  ipp                    Start REPL""")


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
