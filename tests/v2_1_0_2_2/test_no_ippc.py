"""Test v2.1.0.2.2 — No stale .ippc cache files in tests/."""
import sys, os, glob

PASS = 0; FAIL = 0

def check(name, ok):
    global PASS, FAIL
    if ok:
        print(f"  [PASS] {name}"); PASS += 1
    else:
        print(f"  [FAIL] {name}"); FAIL += 1

print("=== v2.1.0.2.2 Stale .ippc Cleanup Tests ===")

tests_dir = os.path.join(os.path.dirname(__file__), '..')
ippc_files = glob.glob(os.path.join(tests_dir, '**', '*.ippc'), recursive=True)
check("No .ippc files remain in tests/", len(ippc_files) == 0)

print()
print(f"Passed: {PASS} / {PASS + FAIL}")
if FAIL:
    sys.exit(1)
