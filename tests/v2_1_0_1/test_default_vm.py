"""Test v2.1.0.1 — REPL defaults to VM mode."""
import sys, os, types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

sys.modules['tkinter'] = types.ModuleType('tkinter')

from ipp.main import InterpreterManager, VMInterpreter

PASS = 0; FAIL = 0

def check(name, ok):
    global PASS, FAIL
    if ok:
        print(f"  [PASS] {name}"); PASS += 1
    else:
        print(f"  [FAIL] {name}"); FAIL += 1

print("=== v2.1.0.1 REPL Defaults to VM Tests ===")

# 1. Default mode is VM
im = InterpreterManager()
check("InterpreterManager defaults to VM", im.use_vm)
check("get_interpreter returns VMInterpreter", isinstance(im.get_interpreter(), VMInterpreter))

# 2. .vm vm still works (no-op when already VM)
im2 = InterpreterManager()
r = im2.switch_to('vm')
check("switch_to('vm') returns correct message", 'VM' in r)
check("use_vm still True after switch_to('vm')", im2.use_vm)

# 3. .vm interpreter still works (switches to tree-walker)
r2 = im2.switch_to('interpreter')
check("switch_to('interpreter') returns correct message", 'Interpreter' in r2 or 'interpreter' in r2.lower())
check("use_vm is False after switch_to('interpreter')", not im2.use_vm)
check("get_interpreter returns Interpreter", 'Interpreter' in type(im2.get_interpreter()).__name__)

# 4. Switch back to VM
im2.switch_to('vm')
check("use_vm True after switching back", im2.use_vm)

# 5. State transfer: interpreter → VM
im3 = InterpreterManager()
im3.switch_to('interpreter')
im3.interpreter.global_env.values['x'] = 42
im3.switch_to('vm')
check("Variable survives interpreter→VM transfer", im3.vm_interpreter.global_env.values.get('x') == 42)

# 6. State transfer: VM → interpreter
im3.vm_interpreter.global_env.values['y'] = 99
im3.switch_to('interpreter')
check("Variable survives VM→interpreter transfer", im3.interpreter.global_env.values.get('y') == 99)



print()
print(f"Passed: {PASS} / {PASS + FAIL}")
if FAIL:
    sys.exit(1)
