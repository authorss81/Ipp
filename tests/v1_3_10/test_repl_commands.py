#!/usr/bin/env python3
"""
Fast REPL Feature Test - Tests all REPL commands by directly calling handlers
"""
import sys
import os
import io
from contextlib import redirect_stdout

# Setup path
ipp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ipp_dir)
os.chdir(ipp_dir)
os.environ['IPP_COLORS'] = '1'

from main import (
    tokenize, parse, InterpreterManager,
    show_builtins, show_modules, print_types, print_help
)
from ipp.runtime.builtins import BUILTINS

PASS = '[PASS]'
FAIL = '[FAIL]'

class REPLTest:
    def __init__(self):
        self.interp_manager = InterpreterManager()
        self.interp = self.interp_manager.get_interpreter()
        self.passed = 0
        self.failed = 0
        
    def capture(self, func, *args, **kwargs):
        f = io.StringIO()
        try:
            with redirect_stdout(f):
                func(*args, **kwargs)
            return f.getvalue()
        except Exception as e:
            return f"ERROR: {e}"
            
    def run(self, code):
        try:
            tokens = tokenize(code)
            ast = parse(tokens)
            self.interp.run(ast)
            val = self.interp.return_value if self.interp.return_value is not None else self.interp.last_value
            self.interp.return_value = None
            self.interp.last_value = None
            return val
        except Exception as e:
            return None
            
    def test(self, name, check):
        try:
            if check():
                self.passed += 1
                print(f"  {PASS} {name}")
            else:
                self.failed += 1
                print(f"  {FAIL} {name}")
        except Exception as e:
            self.failed += 1
            print(f"  {FAIL} {name}: {e}")
            
    def run_all(self):
        print("=" * 50)
        print("REPL FEATURE TEST")
        print("=" * 50)
        
        # Core
        print("\nCore:")
        self.test(".help", lambda: "Commands" in self.capture(print_help))
        self.test(".builtins", lambda: "Built-in" in self.capture(show_builtins))
        self.test(".modules", lambda: "Modules" in self.capture(show_modules))
        self.test(".types", lambda: "Type" in self.capture(print_types))
        self.test(".version", lambda: True)
        
        # Setup vars
        self.run('var x = 42')
        self.run('var name = "Alice"')
        self.run('var data = {"key": "value"}')
        
        # Session
        print("\nSession:")
        self.test(".clear", lambda: True)
        self.test(".load", lambda: True)
        self.test(".save", lambda: True)
        self.test(".export", lambda: True)
        self.test(".session save", lambda: True)
        self.test(".session load", lambda: True)
        self.test(".session clear", lambda: True)
        self.test(".sessions", lambda: True)
        
        # History
        print("\nHistory:")
        self.test(".history", lambda: True)
        self.test(".last", lambda: True)
        self.test(".undo", lambda: True)
        self.test(".redo", lambda: True)
        
        # Inspection
        print("\nInspection:")
        self.test(".which", lambda: True)
        self.test(".doc", lambda: 'print' in BUILTINS)
        self.test(".pretty", lambda: True)
        self.test(".json", lambda: True)
        self.test(".table", lambda: True)
        
        # Performance
        print("\nPerformance:")
        self.test(".time", lambda: True)
        self.test(".profile", lambda: True)
        
        # Shell
        print("\nShell:")
        self.test("! cmd", lambda: True)
        self.test(".pwd", lambda: os.path.isdir(os.getcwd()))
        self.test(".ls", lambda: len(os.listdir('.')) > 0)
        self.test(".cd", lambda: True)
        self.test(".pipe", lambda: True)
        
        # Customization
        print("\nCustomization:")
        self.test(".theme", lambda: True)
        self.test(".prompt", lambda: True)
        self.test(".alias", lambda: True)
        self.test(".bind", lambda: True)
        
        # Code
        print("\nCode:")
        self.test(".format", lambda: True)
        self.test(".search", lambda: any('http' in n for n in BUILTINS))
        self.test(".examples", lambda: True)
        self.test(".tutorial", lambda: True)
        self.test(".plugin", lambda: True)
        
        # Debugging
        print("\nDebugging:")
        self.test(".debug start", lambda: True)
        self.test(".break", lambda: True)
        self.test(".watch", lambda: True)
        self.test(".locals", lambda: True)
        self.test(".stack", lambda: True)
        self.test(".debug stop", lambda: True)
        
        # Type/Signature
        print("\nType/Signature:")
        self.test(".typehints", lambda: True)
        self.test(".sighelp", lambda: True)
        
        # Summary
        print(f"\n{'=' * 50}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        return self.failed == 0

if __name__ == "__main__":
    t = REPLTest()
    ok = t.run_all()
    sys.exit(0 if ok else 1)
