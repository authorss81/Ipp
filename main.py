#!/usr/bin/env python3
"""
Ipp - A simple, beginner-friendly scripting language for game development
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.interpreter.interpreter import interpret


def run_file(filepath):
    """Run an Ipp source file"""
    import os
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
        result = interpret(ast, os.path.abspath(filepath))
        if result is not None:
            print(result)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def run_repl():
    """Run the Ipp REPL"""
    print("Ipp v0.3.0 - Type 'help()' for info, 'exit()' to quit")
    print()
    
    buffer = []
    
    while True:
        try:
            if buffer:
                prompt = "... "
            else:
                prompt = "ipp> "
            
            line = input(prompt)
            
            if not buffer and line.strip() in ("exit()", "exit", "quit"):
                break
            
            if line.strip() == "help()":
                print("Ipp v0.3.0")
                print("Commands: exit(), help(), clear()")
                print("Features: strings, lists, dicts, json, regex, files, math, random")
                continue
                
            if line.strip() == "clear()":
                buffer = []
                continue
                
            if not line.strip() and not buffer:
                continue
                
            buffer.append(line)
            
            source = "\n".join(buffer)
            
            try:
                tokens = tokenize(source)
                ast = parse(tokens)
                result = interpret(ast)
                buffer = []
                if result is not None:
                    print(result)
            except Exception as e:
                error_msg = str(e)
                if "Expect" in error_msg or "Parse error" in error_msg:
                    continue
                else:
                    buffer = []
                    print(f"Error: {e}")
                    
        except KeyboardInterrupt:
            print()
            if buffer:
                buffer = []
            else:
                break
        except EOFError:
            break
        except Exception as e:
            buffer = []
            print(f"Error: {e}")


def main():
    if len(sys.argv) == 1:
        run_repl()
    elif len(sys.argv) == 2:
        filepath = sys.argv[1]
        if filepath == "--help" or filepath == "-h":
            print("Usage: ipp [file]")
            print("  Run an Ipp script file, or start REPL if no file provided")
            return 0
        return run_file(filepath)
    else:
        print("Usage: ipp [file]")
        return 1


if __name__ == "__main__":
    sys.exit(main())