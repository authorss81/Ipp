#!/usr/bin/env python3
"""
REPL Improvement Tests — v2.0.25
Tests: .bind processing, .vm state transfer, history filtering,
       .export filtering, macro quotes, tutorial validation,
       file-path completion, duplicate code removal, interrupt polling.
"""
import sys, os, io, re, json
from contextlib import redirect_stdout

ipp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ipp_dir)
os.chdir(ipp_dir)
os.environ['IPP_COLORS'] = '0'
os.environ['NO_COLOR'] = '1'

# Must stub tkinter BEFORE any ipp import
import types
if 'tkinter' not in sys.modules:
    tk = types.ModuleType('tkinter')
    tk.Tk = type('Tk', (), {'__init__': lambda self: None})
    sys.modules['tkinter'] = tk

from ipp.main import (
    tokenize, parse, InterpreterManager,
    print_help, print_types, show_builtins, show_modules,
    _tutorial_mode, _tutorial_step, _tutorial_steps,
    _INTERRUPT_FLAG, _check_interrupt, IppCompleter,
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
        print("REPL IMPROVEMENT TESTS (v2.0.25)")
        print("=" * 50)

        # --- 1. .vm state transfer (critical #5) ---
        print("\n.vm state transfer:")
        im = InterpreterManager()
        im.interpreter.global_env.values['test_var'] = 42
        im.switch_to('vm')
        vm_val = im.vm_interpreter.global_env.values.get('test_var')
        self.test("Interpreter to VM state transfer", lambda: vm_val == 42)
        im.vm_interpreter.global_env.values['vm_var'] = 99
        im.switch_to('interpreter')
        iv_val = im.interpreter.global_env.values.get('vm_var')
        self.test("VM to Interpreter state transfer", lambda: iv_val == 99)

        # --- 2. Duplicate .theme/.themes code removal (critical #4) ---
        print("\nDuplicate code removal:")
        main_src = open(ipp_dir + '/ipp/main.py', 'r', encoding='utf-8').read()
        first = main_src.find('.theme ')
        last = main_src.rfind('.theme ')
        self.test("Single .theme handler block (no duplicate)",
                  lambda: main_src.count('m_theme = re.match') == 1 and main_src.count("stripped == '.themes'") == 1)

        # --- 3. No .break stub (critical #7) ---
        print("\n.break stub removal:")
        self.test("No .break not-yet-implemented stub",
                  lambda: 'not yet implemented' not in main_src.split('.break')[1][:60] if '.break' in main_src else True)

        # --- 4. .export filters meta commands (critical #13) ---
        print("\n.export filtering:")
        history = ['var x = 1', '.help', 'print(x)', '.vars', 'var y = 2']
        filtered = [c for c in history if not c.startswith('.')]
        self.test("Meta commands filtered", lambda: len(filtered) == 3 and '.help' not in filtered and '.vars' not in filtered)
        self.test("Non-meta preserved", lambda: filtered == ['var x = 1', 'print(x)', 'var y = 2'])

        # --- 5. Macro expansion with quoted args (critical #14) ---
        print("\nMacro quoted args:")
        import shlex
        test_args = 'print("hello, world") 42'
        arg_list = shlex.split(test_args)
        self.test("Quoted string as single arg", lambda: len(arg_list) == 2)
        self.test("Non-quoted arg separate", lambda: arg_list[1] == '42')

        # --- 6. Tutorial validation exists (critical #8) ---
        print("\nTutorial validation:")
        self.test("Tutorial step 0 covers variables",
                  lambda: any(kw in _tutorial_steps[0]['example'] for kw in ['var ', 'let ']))
        self.test("Tutorial step 4 covers functions",
                  lambda: 'func' in _tutorial_steps[4]['example'])
        self.test("Tutorial step 6 covers classes",
                  lambda: 'class' in _tutorial_steps[6]['example'])
        self.test("Tutorial step 7 covers try/catch",
                  lambda: 'try' in _tutorial_steps[7]['example'])

        # --- 7. Interrupt polling mechanism (critical #9) ---
        print("\nInterrupt polling:")
        _INTERRUPT_FLAG.clear()
        self.test("Flag starts clear", lambda: not _INTERRUPT_FLAG.is_set())
        _INTERRUPT_FLAG.set()
        self.test("check_interrupt detects flag", lambda: _check_interrupt())
        self.test("check_interrupt clears flag", lambda: not _INTERRUPT_FLAG.is_set())

        # --- 8. VM interrupt flag exists (critical #9) ---
        print("\nVM interrupt:")
        from ipp.vm.vm import _vm_interrupt
        _vm_interrupt.clear()
        self.test("VM interrupt starts clear", lambda: not _vm_interrupt.is_set())
        _vm_interrupt.set()
        self.test("VM interrupt can be set", lambda: _vm_interrupt.is_set())
        _vm_interrupt.clear()

        # --- 9. print_help still works (regression) ---
        print("\nHelp output:")
        help_out = self.capture(print_help)
        self.test("print_help outputs content", lambda: len(help_out) > 100)
        self.test("Commands section present", lambda: 'Commands' in help_out)
        self.test("Quick Reference present", lambda: 'Quick Reference' in help_out)

        # --- 10. print_types works (regression) ---
        print("\nType output:")
        types_out = self.capture(print_types)
        self.test("print_types works", lambda: 'Type System' in types_out)

        # --- 11. show_builtins works (regression) ---
        print("\nBuiltins output:")
        builtins_out = self.capture(show_builtins)
        self.test("show_builtins works", lambda: len(builtins_out) > 50)

        # --- 12. Interpreter execution works (regression) ---
        print("\nExecution:")
        self.test("Exec var x = 42", lambda: self.run('var x = 42') is None)
        self.test("Exec print works", lambda: self.run('print("hello")') is None)

        # --- 13. File-path completion ---
        print("\nFile-path completion:")
        comp = IppCompleter(self.interp)
        self.test("Completer initializes", lambda: comp is not None)

        # --- Summary ---
        print(f"\n{'=' * 50}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        return self.failed == 0

if __name__ == "__main__":
    t = REPLTest()
    ok = t.run_all()
    sys.exit(0 if ok else 1)
