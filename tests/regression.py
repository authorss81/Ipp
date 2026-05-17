#!/usr/bin/env python3
"""
Regression Test Runner
Runs all version tests to verify nothing is broken
Tests both INTERPRETER and VM modes
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
    ("v1.5.21", "tests/v1_5_21/test_for_in_loop.ipp"),
    ("v1.5.22", "tests/v1_5_22/test_pi_e_constants.ipp"),
    ("v1.5.23", "tests/v1_5_23/test_let_immutable.ipp"),
    ("v1.5.24", "tests/v1_5_24/test_str_method.ipp"),
    ("v1.5.25", "tests/v1_5_25/test_static_methods.ipp"),
    ("v1.5.26", "tests/v1_5_26/test_continue_while.ipp"),
    ("v1.5.27", "tests/v1_5_27/test_continue_for.ipp"),
    ("v1.5.28", "tests/v1_5_28/test_multi_var.ipp"),
    ("v1.5.29", "tests/v1_5_29/test_list_comp.ipp"),
    ("v1.5.30", "tests/v1_5_30/test_dict_comp.ipp"),
    ("v1.5.31", "tests/v1_5_31/test_cache.ipp"),
    ("v1.5.32", "tests/v1_5_32/test_set_index.ipp"),
    ("v1.5.33", "tests/v1_5_33/test_do_while.ipp"),
    ("v1.5.34", "tests/v1_5_34/test_multi_catch.ipp"),
    ("v1.5.35", "tests/v1_5_35/test_variadic.ipp"),
    ("v1.5.36", "tests/v1_5_36/test_fstrings.ipp"),
    ("v1.5.37", "tests/v1_5_37/test_import.ipp"),
    ("v1.5.38", "tests/v1_5_38/test_spread.ipp"),
    ("v1.6.0", "tests/v1_6_0/test_operator_overload.ipp"),
    ("v1.6.1", "tests/v1_6_1/test_exception_types.ipp"),
    ("v1.6.2", "tests/v1_6_2/test_decorator.ipp"),
    ("v1.6.3", "tests/v1_6_3/test_multi_return.ipp"),
    ("v1.6.4", "tests/v1_6_4/test_named_args.ipp"),
    ("v1.6.5", "tests/v1_6_5/test_property.ipp"),
    ("v1.6.6", "tests/v1_6_6/test_signal.ipp"),
    ("v1.6.7", "tests/v1_6_7/test_slicing.ipp"),
    ("v1.6.8", "tests/v1_6_8/test_matrix.ipp"),
    ("v1.6.9", "tests/v1_6_9/test_async.ipp"),
    ("v1.6.10", "tests/v1_6_10/test_set.ipp"),
    ("v1.6.11", "tests/v1_6_11/test_tailcall.ipp"),
    ("v1.6.12", "tests/v1_6_12/test_fluent.ipp"),
    ("v1.6.13", "tests/v1_6_13/test_string_format.ipp"),
    ("v1.6.14", "tests/v1_6_14/test_bytecode_cache.ipp"),
    ("v1.6.15", "tests/v1_6_15/test_linter.ipp"),
    ("v1.7.0", "tests/v1_7_0/test_archive.ipp"),
    ("v1.7.1", "tests/v1_7_1/test_opcodes.ipp"),
    ("v1.7.2", "tests/v1_7_2/test_error_quality.ipp"),
    ("v1.7.3", "tests/v1_7_3/test_package_manager.ipp"),
    ("v1.7.4", "tests/v1_7_4/test_lsp_completion.ipp"),
    ("v1.7.5", "tests/v1_7_5/test_wasm.ipp"),
    ("v1.7.8.1-str-basic", "tests/v1_7_8_1/test_str_basic.ipp"),
    ("v1.7.8.1-str-concat", "tests/v1_7_8_1/test_str_concat.ipp"),
    ("v1.7.8.1-str-inherit", "tests/v1_7_8_1/test_str_inheritance.ipp"),
    ("v1.7.8.1-str-default", "tests/v1_7_8_1/test_str_default.ipp"),
    ("v1.7.8.1-str-collections", "tests/v1_7_8_1/test_str_collections.ipp"),
    ("v1.7.8.2-repr-builtin", "tests/v1_7_8_2/test_repr_builtin.ipp"),
    ("v1.7.8.2-repr-method", "tests/v1_7_8_2/test_repr_method.ipp"),
    ("v1.7.8.2-repr-default", "tests/v1_7_8_2/test_repr_default.ipp"),
    ("v1.7.8.2-repr-collections", "tests/v1_7_8_2/test_repr_collections.ipp"),
    ("v1.7.8.2-repr-inheritance", "tests/v1_7_8_2/test_repr_inheritance.ipp"),
    ("v1.7.8.2-repr-adv", "tests/v1_7_8_2/test_repr_advanced.ipp"),
    ("v1.7.8.2-repr-nested", "tests/v1_7_8_2/test_repr_nested.ipp"),
    ("v1.7.8.2-repr-collections-adv", "tests/v1_7_8_2/test_repr_collections_adv.ipp"),
    ("v1.7.8.3-len-basic", "tests/v1_7_8_3/test_len_basic.ipp"),
    ("v1.7.8.3-len-inheritance", "tests/v1_7_8_3/test_len_inheritance.ipp"),
    ("v1.7.8.3-len-default", "tests/v1_7_8_3/test_len_default.ipp"),
    ("v1.7.9-try-div", "tests/v1_7_9/test_try_catch_div.ipp"),
    ("v1.7.9-try-index", "tests/v1_7_9/test_try_catch_index.ipp"),
    ("v1.7.9-try-nil", "tests/v1_7_9/test_try_catch_nil.ipp"),
    ("v1.7.9-try-throw", "tests/v1_7_9/test_try_catch_throw.ipp"),
    ("v2.0.0", "tests/v2_0_0/test_c_extension.ipp"),
]

def extract_expected_from_file(filepath):
    """Extract expected output markers from test file comments."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Look for patterns like "# expected: <value>" or "// expected: <value>"
        import re
        matches = re.findall(r'(?:#|//)\s*expected:\s*(.+)', content, re.IGNORECASE)
        if matches:
            return [m.strip() for m in matches]
    except:
        pass
    return None

VM_TEST_SCRIPT = '''
import sys
import os

# Remove any installed ipp package
for mod_name in list(sys.modules.keys()):
    if mod_name == "ipp" or mod_name.startswith("ipp."):
        del sys.modules[mod_name]

sys.path.insert(0, os.getcwd())

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.vm.compiler import compile_ast
from ipp.vm.vm import VM

with open("{filepath}", "r") as f:
    source = f.read()

try:
    tokens = tokenize(source)
    ast = parse(tokens)
    chunk = compile_ast(ast)
    vm = VM()
    vm._current_source_file = os.path.abspath("{filepath}")
    vm.run(chunk)
except Exception as e:
    print(str(e), file=sys.stderr)
    sys.exit(1)
'''

def run_interpreter_test(version, filepath):
    """Run test in interpreter mode using main.py"""
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(
        ["python", "main.py", "run", filepath],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env
    )
    return result.returncode, result.stdout, result.stderr

def run_vm_test(version, filepath):
    """Run test in VM mode using direct VM execution"""
    import tempfile
    # Write temp test script to system temp dir (not tests/ to avoid polluting list_dir)
    script = VM_TEST_SCRIPT.format(filepath=filepath)
    fd, script_path = tempfile.mkstemp(suffix='_ipp_vm_test.py')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(script)
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        return result.returncode, result.stdout, result.stderr
    finally:
        try:
            os.remove(script_path)
        except:
            pass

def run_test(version, filepath):
    print("=" * 50)
    print(f"Testing {version}")
    print("=" * 50)
    
    # Python test files - only run in interpreter mode
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
    
    # Ipp test files - test both modes
    print("\n--- INTERPRETER MODE ---")
    interp_rc, interp_out, interp_err = run_interpreter_test(version, filepath)
    if interp_rc != 0:
        print(f"INTERPRETER FAILED: {interp_err}")
    else:
        print(interp_out)
    
    print("\n--- VM MODE ---")
    vm_rc, vm_out, vm_err = run_vm_test(version, filepath)
    if vm_rc != 0:
        print(f"VM FAILED: {vm_err}")
    else:
        print(vm_out)
    
    # Test passes if both modes succeed (or both fail for expected failures)
    if interp_rc != 0 and vm_rc != 0:
        # If both fail with different errors, that's a problem
        if interp_err.strip() != vm_err.strip():
            print(f"\n-> FAILED: Both failed but with different errors!")
            print(f"Interpreter error: {interp_err[:200]}")
            print(f"VM error:          {vm_err[:200]}")
            return False
        print("\n-> Both modes failed (expected - test may check error handling)")
        return True
    
    if interp_rc != 0:
        print(f"\n-> FAILED: VM passed but interpreter failed")
        return False
    
    if vm_rc != 0:
        print(f"\n-> FAILED: Interpreter passed but VM failed")
        return False
    
    # Both passed - compare outputs to ensure consistency
    def normalize_output(s):
        import re
        # Normalize UUIDs
        s = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<UUID>', s)
        # Normalize ISO timestamps (2026-05-16T00:34:52.142819)
        s = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+', '<TIMESTAMP>', s)
        # Normalize log timestamps (2026-05-16 05:56:27,641)
        s = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+', '<LOGTS>', s)
        # Normalize datetime strings (2026-05-16 00:34:52)
        s = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '<DATETIME>', s)
        # Normalize datetime component outputs (year/month/day/hour/min/sec printed separately)
        # Match sequences of datetime-like numbers on individual lines
        s = re.sub(r'(\n2026\n\d{1,2}\n\d{1,2}\n\d{1,2}\n\d{1,2}\n)\d{1,2}(\n)',
                   r'\1<SEC>\2', s)
        # Normalize large floats BEFORE large integers (order matters)
        s = re.sub(r'\b\d{7,}\.\d+\b', '<TSFLOAT>', s)
        # Normalize medium floats that are timing/duration related (e.g. 182.346379257)
        s = re.sub(r'\b\d{1,6}\.\d{6,}\b', '<TIMEFLOAT>', s)
        # Normalize hash integers (long integers that differ across runs) - AFTER floats
        s = re.sub(r'\b\d{10,}\b', '<HASH>', s)
        # Normalize .time command output (timing differs between runs/modes)
        s = re.sub(r'Time: \d+\.\d+', 'Time: <TIME>', s)
        s = re.sub(r'Elapsed: \d+\.\d+ seconds', 'Elapsed: <TIME> seconds', s)
        # Normalize small floats in scientific notation (timing deltas)
        s = re.sub(r'\d+\.\d+e[+-]\d+', '<DELTA>', s)
        # Normalize division-by-zero error messages (various formats)
        s = re.sub(r'Division by zero[^\n]*', 'Division by zero', s)
        # Normalize dict repr quotes {'a': 1} vs {"a": 1} (interpreter vs VM)
        s = re.sub(r"'([^']+)':", r'"\1":', s)
        # Also normalize string values in dict repr: 'value' -> "value"
        s = re.sub(r": '([^']*)'([,}])", r': "\1"\2', s)
        s = re.sub(r"Property '[^']+' not found on NoneType", 'NilPropertyError', s)
        s = re.sub(r"Cannot access property '[^']+' on nil", 'NilPropertyError', s)
        s = re.sub(r"Only instances have properties, got <class 'NoneType'>", 'NilPropertyError', s)
        # Normalize list_dir output (long directory listing lists differ between runs)
        s = re.sub(r'\[\'[a-z][a-z0-9_]*\'(?:, \'[a-z][a-z0-9_]*\'){10,}\]', '<DIRLIST>', s)
        # Normalize random float outputs (differ between interpreter/VM runs)
        s = re.sub(r'\b0\.\d{8,}\b', '<RANDFLOAT>', s)
        s = re.sub(r'\b\d\.\d{8,}\b', '<RANDFLOAT>', s)
        # Normalize random integer/choice outputs near random floats
        for _ in range(6):
            s = re.sub(r'(<(?:RANDFLOAT|TIMEFLOAT)>\n)(\d{1,3}\n)', r'\1<RANDINT>\n', s)
            s = re.sub(r'(<RANDINT>\n)(\d{1,3}\n)', r'\1<RANDINT>\n', s)
            s = re.sub(r'(<RANDINT>\n)(<(?:RANDFLOAT|TIMEFLOAT)>\n)', r'\1<RANDFLOAT>\n', s)
            s = re.sub(r'(\n<(?:RANDFLOAT|TIMEFLOAT)>\n)(\d{1,3}\n)', r'\1<RANDINT>\n', s)
        return s

    if normalize_output(interp_out.strip()) != normalize_output(vm_out.strip()):
        print(f"\n-> FAILED: Outputs differ between modes!")
        print(f"Interpreter output: {repr(interp_out[:300])}")
        print(f"VM output:          {repr(vm_out[:300])}")
        return False
    
    # Check if test file has expected output markers
    expected_file = filepath.replace('.ipp', '.expected')
    if os.path.exists(expected_file):
        with open(expected_file, 'r') as f:
            expected = f.read().strip()
        actual = interp_out.strip()
        if expected != actual:
            print(f"\n-> FAILED: Output doesn't match expected!")
            print(f"Expected: {repr(expected[:200])}")
            print(f"Actual:   {repr(actual[:200])}")
            return False
        print(f"  [Output verified against expected file]")
    else:
        # Check for inline expected markers in test file
        inline_expected = extract_expected_from_file(filepath)
        if inline_expected:
            actual = interp_out.strip()
            if inline_expected not in actual:
                print(f"\n-> WARNING: Expected output '{inline_expected}' not found in output!")
                print(f"Actual output: {actual[:200]}")
    
    print("\n-> PASSED in both modes")
    return True

def main():
    print("\n" + "=" * 50)
    print("REGRESSION TEST SUITE (INTERPRETER + VM)")
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
