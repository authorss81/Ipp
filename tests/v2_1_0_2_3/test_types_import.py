"""Test v2.1.0.2.3 — ipp.runtime.types facade imports."""
import sys, os, types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.modules['tkinter'] = types.ModuleType('tkinter')

PASS = 0; FAIL = 0

def check(name, ok):
    global PASS, FAIL
    if ok:
        print(f"  [PASS] {name}"); PASS += 1
    else:
        print(f"  [FAIL] {name}"); FAIL += 1

print("=== v2.1.0.2.3 runtime.types Import Tests ===")

# 1. Module imports cleanly
try:
    from ipp.runtime import types as rt
    check("ipp.runtime.types imports cleanly", True)
except Exception as e:
    check(f"ipp.runtime.types imports cleanly: {e}", False)

# 2. All expected types are accessible
check("IppList accessible", hasattr(rt, 'IppList'))
check("IppDict accessible", hasattr(rt, 'IppDict'))
check("IppSet accessible", hasattr(rt, 'IppSet'))
check("IppRange accessible", hasattr(rt, 'IppRange'))
check("IppFunction accessible", hasattr(rt, 'IppFunction'))

# 3. Types work correctly (create instances)
lst = rt.IppList()
lst.elements = [1, 2, 3]
check("IppList created and elements set", len(lst.elements) == 3)

d = rt.IppDict()
d.data = {'a': 1}
check("IppDict created", d.data['a'] == 1)

s = rt.IppSet()
s.elements = {1, 2}
check("IppSet created", 1 in s.elements)

r = rt.IppRange(0, 5)
check("IppRange created", len(list(r)) == 5)

# 4. VM can import from the new path (lazy imports in vm.py already changed)
from ipp.vm.vm import VM
vm = VM()
check("VM imports without error", True)

from ipp.runtime.types import IppFunction as _IFn
check("IppFunction alias works", _IFn is not None)

print()
print(f"Passed: {PASS} / {PASS + FAIL}")
if FAIL:
    sys.exit(1)
