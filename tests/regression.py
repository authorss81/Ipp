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
    # ("v1.3.3-network", "tests/v1_3_3/test_network.ipp"),  # requires internet
    ("v1.3.4-core", "tests/v1_3_4/test_core_builtins.ipp"),
    ("v1.3.4-string", "tests/v1_3_4/test_string_functions.ipp"),
    ("v1.3.4-fileio", "tests/v1_3_4/test_file_io.ipp"),
    ("v1.3.4-dataformats", "tests/v1_3_4/test_data_formats.ipp"),
    ("v1.3.4-math", "tests/v1_3_4/test_math_library.ipp"),
    ("v1.3.4-collections", "tests/v1_3_4/test_collections.ipp"),
    ("v1.3.4-advanced", "tests/v1_3_4/test_advanced_features.ipp"),
    ("v1.3.7-repl", "tests/v1_3_7/test_repl_enhancements.ipp"),
    ("v1.3.7-vm", "tests/v1_3_7/test_vm_bugs.ipp"),
    ("v1.3.8", "tests/v1_3_8/test_networking_collections.ipp"),
    ("v1.3.8-websocket", "tests/v1_3_8/test_websocket.ipp"),
    ("v1.3.9", "tests/v1_3_9/test_error_handling.ipp"),
    ("v1.3.10", "tests/v1_3_10/test_tab_completion.ipp"),
    ("v1.3.10-repl", "tests/v1_3_10/test_repl_intelligence.ipp"),
    ("v1.3.10-fast", "tests/v1_3_10/test_repl_commands.py"),
    ("v1.3.10-slow", "tests/v1_3_10/test_repl_slow.py"),
    ("v1.3.10-practical", "tests/v1_3_10/test_repl_practical.py"),
    ("v1.4.0", "tests/v1_4_0/test_generators.ipp"),
    ("v1.5.0", "tests/v1_5_0/test_additional_builtins.ipp"),
    ("v1.5.0-async", "tests/v1_5_0/test_async_await.ipp"),
    ("v1.5.2", "tests/v1_5_2/test_wasm_backend.ipp"),
    ("v1.5.2a", "tests/v1_5_2/test_wasm_implementation.ipp"),
    ("v1.5.2b", "tests/v1_5_2/test_web_playground.ipp"),
    ("v1.5.3a", "tests/v1_5_3/test_canvas_2d.ipp"),
    ("v1.5.3b", "tests/v1_5_3/test_webgl.ipp"),
    ("v1.5.4.3", "tests/v1_5_4/test_repl_enhancements_v143.ipp"),
    ("v1.5.4.4", "tests/v1_5_4/test_repl_enhancements_v144.ipp"),
    ("v1.5.4.5", "tests/v1_5_4/test_repl_enhancements_v145.ipp"),
    ("v1.5.4.6", "tests/v1_5_4/test_repl_enhancements_v146.ipp"),
    ("v1.5.4.7", "tests/v1_5_4/test_repl_enhancements_v147.ipp"),
    ("v1.5.5.0", "tests/v1_5_5/test_3d_math_v150.ipp"),
    ("v1.5.5.1", "tests/v1_5_5/test_matrix_ops_v151.ipp"),
    ("v1.5.5.2", "tests/v1_5_5/test_quaternion_v152.ipp"),
    ("v1.5.5.3", "tests/v1_5_5/test_scene_graph_v153.ipp"),
    ("v1.5.5.4", "tests/v1_5_5/test_basic_renderer_v154.ipp"),
    ("v1.5.6", "tests/v1_5_6/test_primitives_v156.ipp"),
    # v1.5.21-25 Emergency Bug Fixes
    ("v1.5.21", "tests/v1_5_21/test_for_in_loop.ipp"),
    ("v1.5.22", "tests/v1_5_22/test_pi_e_constants.ipp"),
    ("v1.5.23", "tests/v1_5_23/test_let_immutable.ipp"),
    ("v1.5.24", "tests/v1_5_24/test_str_method.ipp"),
    ("v1.5.25", "tests/v1_5_25/test_static_methods.ipp"),
    # v1.5.26-27 Emergency Bug Fixes
    ("v1.5.26", "tests/v1_5_26/test_continue_while.ipp"),
    ("v1.5.27", "tests/v1_5_27/test_continue_for.ipp"),
    ("v1.5.28", "tests/v1_5_28/test_multi_var.ipp"),
]

def run_test(version, filepath):
    print("=" * 50)
    print(f"Testing {version}")
    print("=" * 50)
    
    # Python test files
    if filepath.endswith('.py'):
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"FAILED: {result.stderr}")
            return False
        print(result.stdout)
        return True
    
    # Ipp test files
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
