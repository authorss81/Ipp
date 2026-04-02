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
    ("v0.9.0", "tests/v09/test_features.ipp"),
    ("v0.10.0", "tests/v10/test_features.ipp"),
    ("v0.11.0", "tests/v11/test_features.ipp"),
    ("v0.12.0", "tests/v12/test_features.ipp"),
    ("v1.0.0", "tests/v1/test_features.ipp"),
    ("v1.0.1", "tests/v1_0_1/test_features.ipp"),
    ("v1.1.0", "tests/v1_1_0/test_features.ipp"),
    ("v1.1.1", "tests/v1_1_1/test_features.ipp"),
    ("v1.3.2", "tests/v1_3_2/test_features.ipp"),
    ("v1.3.3", "tests/v1_3_3/test_features.ipp"),
    ("v1.3.3-network", "tests/v1_3_3/test_network.ipp"),
    ("v1.3.4-core", "tests/v1_3_4/test_core_builtins.ipp"),
    ("v1.3.4-string", "tests/v1_3_4/test_string_functions.ipp"),
    ("v1.3.4-fileio", "tests/v1_3_4/test_file_io.ipp"),
    ("v1.3.4-dataformats", "tests/v1_3_4/test_data_formats.ipp"),
    ("v1.3.4-math", "tests/v1_3_4/test_math_library.ipp"),
    ("v1.3.4-collections", "tests/v1_3_4/test_collections.ipp"),
    ("v1.3.4-advanced", "tests/v1_3_4/test_advanced_features.ipp"),
    ("v1.3.7-repl", "tests/v1_3_7/test_repl_enhancements.ipp"),
    ("v1.3.8", "tests/v1_3_8/test_networking_collections.ipp"),
    ("v1.3.9", "tests/v1_3_9/test_error_handling.ipp"),
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
