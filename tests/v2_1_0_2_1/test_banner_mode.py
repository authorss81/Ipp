"""Test v2.1.0.2.1 — REPL banner shows VM / Interpreter mode."""
import sys, os, io, types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

sys.modules['tkinter'] = types.ModuleType('tkinter')

from contextlib import redirect_stdout
from ipp.main import print_banner, VERSION

PASS = 0
FAIL = 0

def check(name, ok):
    global PASS, FAIL
    if ok:
        print(f"  [PASS] {name}")
        PASS += 1
    else:
        print(f"  [FAIL] {name}")
        FAIL += 1

print("=== v2.1.0.2.1 REPL Banner Mode Tests ===")

# Test 1: print_banner with use_vm=True shows VM mode
buf = io.StringIO()
with redirect_stdout(buf):
    print_banner(use_vm=True)
out = buf.getvalue()
check("print_banner(True) shows VM mode", "VM mode" in out)
check("print_banner(True) does NOT show Interpreter", "Interpreter mode" not in out)
check("print_banner(True) shows switch hint", "interpreter to switch" in out)

# Test 2: print_banner with use_vm=False shows Interpreter mode
buf = io.StringIO()
with redirect_stdout(buf):
    print_banner(use_vm=False)
out = buf.getvalue()
check("print_banner(False) shows Interpreter mode", "Interpreter mode" in out)
check("print_banner(False) does NOT show VM", "VM mode" not in out)
check("print_banner(False) shows switch hint", "vm to switch" in out)

# Test 3: VERSION equals 2.1.0.2.1
check("VERSION is 2.1.0.2.1", VERSION == "2.1.0.2.1")

print()
print(f"Passed: {PASS} / {PASS + FAIL}")

if FAIL:
    sys.exit(1)
