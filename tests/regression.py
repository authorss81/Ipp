#!/usr/bin/env python3
"""
Regression Test Runner
Runs all version tests to verify nothing is broken
"""

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TESTS = [
    ("v0.5.0", "tests/v05/test_features.ipp"),
    ("v0.6.0", "tests/v06/test_features.ipp"),
    ("v0.7.0", "tests/v07/test_features.ipp"),
    ("v0.8.0", "tests/v08/test_features.ipp"),
]

def run_test(version, filepath):
    print("=" * 50)
    print(f"Testing {version}")
    print("=" * 50)
    result = subprocess.run(
        ["python", "main.py", "run", filepath],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"FAILED: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    print("\n" + "=" * 50)
    print("REGRESSION TEST SUITE")
    print("=" * 50 + "\n")
    
    failed = []
    for version, filepath in TESTS:
        if not run_test(version, filepath):
            failed.append(version)
    
    print("=" * 50)
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    else:
        print("ALL TESTS PASSED!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
