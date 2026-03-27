#!/usr/bin/env python3
"""
Ipp vs Python Benchmark Comparison Runner
Run this to compare Ipp language performance against Python.
"""

import subprocess
import time
import re

def run_command(cmd, cwd=None):
    """Run a command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result.stdout, result.stderr, result.returncode

def parse_results(output):
    """Parse benchmark results into a dict."""
    results = {}
    lines = output.split('\n')
    
    for line in lines:
        if 'in' in line and 's' in line:
            match = re.search(r'(.+?):\s*(.+)in\s*([\d.]+)s', line)
            if match:
                name = match.group(1).strip()
                value = match.group(2).strip()
                time_val = float(match.group(3))
                results[name] = {
                    'time': time_val,
                    'value': value
                }
    
    return results

def main():
    project_dir = "."
    
    print("=" * 80)
    print("IPP LANGUAGE BENCHMARK SUITE v1.2.0")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("Running Python Benchmarks...")
    print("=" * 80)
    
    python_start = time.perf_counter()
    stdout, stderr, code = run_command("python tests/v1/benchmarks/python_benchmarks.py", cwd=project_dir)
    python_total = time.perf_counter() - python_start
    
    if code != 0:
        print(f"Error running Python benchmarks: {stderr}")
        return
    
    print(stdout)
    python_results = parse_results(stdout)
    
    print("\n" + "=" * 80)
    print("Running Ipp Benchmarks...")
    print("=" * 80)
    
    ipp_start = time.perf_counter()
    stdout, stderr, code = run_command("python main.py run tests/v1/benchmarks/ipp_benchmarks.ipp", cwd=project_dir)
    ipp_total = time.perf_counter() - ipp_start
    
    if code != 0:
        print(f"Error running Ipp benchmarks: {stderr}")
        return
    
    print(stdout)
    ipp_results = parse_results(stdout)
    
    print("\n" + "=" * 80)
    print("BENCHMARK COMPARISON: Ipp vs Python")
    print("=" * 80)
    print(f"{'Benchmark':<35} {'Python (s)':<15} {'Ipp (s)':<15} {'Ratio':<15}")
    print("-" * 80)
    
    all_keys = set(python_results.keys()) | set(ipp_results.keys())
    
    for key in sorted(all_keys):
        py_data = python_results.get(key, {})
        ipp_data = ipp_results.get(key, {})
        
        py_time = py_data.get('time', 0)
        ipp_time = ipp_data.get('time', 0)
        
        if py_time > 0 and ipp_time > 0:
            ratio = ipp_time / py_time
            if ratio < 1:
                status = f"{ratio:.1f}x Ipp faster"
            else:
                status = f"{ratio:.1f}x Python faster"
        elif ipp_time > 0:
            status = "N/A"
        else:
            status = "N/A"
        
        py_str = f"{py_time:.4f}" if py_time > 0 else "N/A"
        ipp_str = f"{ipp_time:.4f}" if ipp_time > 0 else "N/A"
        
        print(f"{key:<35} {py_str:<15} {ipp_str:<15} {status:<15}")
    
    print("-" * 80)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Python benchmarks completed in: {python_total:.2f}s")
    print(f"Ipp benchmarks completed in: {ipp_total:.2f}s")
    print(f"Total time: {python_total + ipp_total:.2f}s")
    print()
    print("Note: Ipp runs on Python interpreter, so it's expected to be slower than")
    print("native Python. The bytecode VM (coming soon) should significantly improve performance.")
    print("=" * 80)

if __name__ == "__main__":
    main()
