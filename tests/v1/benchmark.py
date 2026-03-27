#!/usr/bin/env python3
"""
Benchmark script for v1.0.0 Bytecode VM
Compares interpreter vs bytecode VM performance
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.interpreter.interpreter import Interpreter
from ipp.vm.compiler import compile_ast
from ipp.vm.vm import VM, benchmark_vm, compare_performance


BENCHMARK_TESTS = [
    ("Simple Math", """
var sum = 0
for i in 0..1000 {
    sum = sum + i
}
sum
"""),
    ("Fibonacci (iterative)", """
func fib(n) {
    if n <= 1 {
        return n
    }
    var a = 0
    var b = 1
    for i in 2..n+1 {
        var temp = b
        b = a + b
        a = temp
    }
    return b
}
fib(100)
"""),
    ("List Operations", """
var result = []
for i in 0..100 {
    result.append(i * 2)
}
var total = 0
for x in result {
    total = total + x
}
total
"""),
    ("String Operations", """
var s = ""
for i in 0..100 {
    s = s + "x"
}
len(s)
"""),
    ("Nested Loops", """
var count = 0
for i in 0..50 {
    for j in 0..50 {
        count = count + 1
    }
}
count
"""),
    ("Complex Math", """
func is_prime(n) {
    if n < 2 {
        return false
    }
    for i in 2..n {
        if n % i == 0 {
            return false
        }
    }
    return true
}
var count = 0
for i in 0..100 {
    if is_prime(i) {
        count = count + 1
    }
}
count
"""),
]


def run_benchmark(name, source, iterations=100):
    print(f"\n{'='*60}")
    print(f"Benchmark: {name}")
    print(f"{'='*60}")
    
    tokens = tokenize(source)
    ast = parse(tokens)
    
    print("\n--- Interpreter ---")
    interp_times = []
    for i in range(iterations):
        interp = Interpreter()
        start = time.perf_counter()
        interp.run(ast)
        end = time.perf_counter()
        interp_times.append(end - start)
    
    interp_avg = sum(interp_times) / len(interp_times) * 1000
    interp_min = min(interp_times) * 1000
    interp_max = max(interp_times) * 1000
    print(f"  Avg: {interp_avg:.4f} ms")
    print(f"  Min: {interp_min:.4f} ms")
    print(f"  Max: {interp_max:.4f} ms")
    
    print("\n--- Bytecode VM ---")
    chunk = compile_ast(ast)
    vm_times = []
    for i in range(iterations):
        vm = VM()
        start = time.perf_counter()
        vm.run(chunk)
        end = time.perf_counter()
        vm_times.append(end - start)
    
    vm_avg = sum(vm_times) / len(vm_times) * 1000
    vm_min = min(vm_times) * 1000
    vm_max = max(vm_times) * 1000
    print(f"  Avg: {vm_avg:.4f} ms")
    print(f"  Min: {vm_min:.4f} ms")
    print(f"  Max: {vm_max:.4f} ms")
    print(f"  Instructions: {vm_times[0] / vm_times[0] * 0 if not vm_times else 0}")
    
    speedup = interp_avg / vm_avg if vm_avg > 0 else 0
    print(f"\n  Speedup: {speedup:.2f}x")
    
    return {
        'name': name,
        'interp_avg_ms': interp_avg,
        'vm_avg_ms': vm_avg,
        'speedup': speedup,
    }


def main():
    print("=" * 60)
    print("v1.0.0 Bytecode VM Performance Benchmarks")
    print("=" * 60)
    
    results = []
    for name, source in BENCHMARK_TESTS:
        result = run_benchmark(name, source)
        results.append(result)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_interp = sum(r['interp_avg_ms'] for r in results)
    total_vm = sum(r['vm_avg_ms'] for r in results)
    avg_speedup = sum(r['speedup'] for r in results) / len(results)
    
    print(f"\nTotal avg time (Interpreter): {total_interp:.4f} ms")
    print(f"Total avg time (VM):         {total_vm:.4f} ms")
    print(f"Average speedup:             {avg_speedup:.2f}x")
    
    print("\nPer-benchmark results:")
    for r in results:
        print(f"  {r['name']:<25} {r['speedup']:.2f}x speedup")


if __name__ == "__main__":
    main()
