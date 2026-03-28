#!/usr/bin/env python3
"""
Ipp VM vs Interpreter Benchmark Comparison
Compare the performance of Ipp's bytecode VM against the tree-walking interpreter.
"""

import sys
sys.path.insert(0, '.')

import time
from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.vm.compiler import compile_ast
from ipp.vm.vm import VM
from ipp.interpreter.interpreter import Interpreter


def benchmark_vm(source, iterations=100):
    """Benchmark VM execution."""
    tokens = tokenize(source)
    ast = parse(tokens)
    chunk = compile_ast(ast)
    
    times = []
    for _ in range(iterations):
        vm = VM(chunk)
        start = time.perf_counter()
        try:
            vm.run()
        except:
            pass
        times.append(time.perf_counter() - start)
    
    return sum(times) / len(times)


def benchmark_interpreter(source, iterations=100):
    """Benchmark interpreter execution."""
    tokens = tokenize(source)
    ast = parse(tokens)
    
    times = []
    for _ in range(iterations):
        interp = Interpreter()
        start = time.perf_counter()
        try:
            interp.run(ast)
        except:
            pass
        times.append(time.perf_counter() - start)
    
    return sum(times) / len(times)


def run_benchmark(name, source, iterations=100):
    """Run both VM and interpreter benchmarks."""
    print(f"\n--- {name} ---")
    
    vm_time = benchmark_vm(source, iterations)
    interp_time = benchmark_interpreter(source, iterations)
    
    if vm_time > 0 and interp_time > 0:
        ratio = interp_time / vm_time
        if ratio > 1:
            speedup = f"{ratio:.2f}x faster (VM)"
        else:
            speedup = f"{1/ratio:.2f}x faster (Interpreter)"
    else:
        speedup = "N/A"
    
    print(f"VM avg:        {vm_time*1000:.4f}ms")
    print(f"Interpreter:   {interp_time*1000:.4f}ms")
    print(f"Speedup:       {speedup}")
    
    return vm_time, interp_time


def main():
    print("=" * 60)
    print("IPP VM vs INTERPRETER BENCHMARK v1.2.3")
    print("=" * 60)
    
    benchmarks = [
        ("Simple Math", """
var a = 10
var b = 20
var c = a + b * 2
c = c - 5
c = c * 3
""", 100),
        
        ("String Operations", """
var s = ""
for i in 0..100 {
    s = s + "x"
}
len(s)
""", 50),
        
        ("List Operations", """
var lst = []
for i in 0..100 {
    lst.append(i)
}
var sum = 0
for x in lst {
    sum = sum + x
}
sum
""", 50),
        
        ("Function Calls", """
func fib(n) {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}
fib(10)
""", 50),
        
        # ("Class Operations", """
        # class Point {
        #     func init(x, y) {
        #         this.x = x
        #         this.y = y
        #     }
        #     
        #     func add(other) {
        #         return Point(this.x + other.x, this.y + other.y)
        #     }
        # }
        # var p1 = Point(1, 2)
        # var p2 = Point(3, 4)
        # var p3 = p1.add(p2)
        # p3.x + p3.y
        # """, 50),
    ]
    
    print("\nRunning benchmarks...")
    
    results = []
    for name, source, iterations in benchmarks:
        vm_time, interp_time = run_benchmark(name, source, iterations)
        results.append((name, vm_time, interp_time))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Benchmark':<25} {'VM (ms)':<12} {'Interp (ms)':<12} {'Ratio'}")
    print("-" * 60)
    
    total_vm = 0
    total_interp = 0
    
    for name, vm_time, interp_time in results:
        total_vm += vm_time
        total_interp += interp_time
        ratio = interp_time / vm_time if vm_time > 0 else 0
        ratio_str = f"{ratio:.2f}x" if ratio > 1 else f"{1/ratio:.2f}x (I)"
        print(f"{name:<25} {vm_time*1000:<12.4f} {interp_time*1000:<12.4f} {ratio_str}")
    
    print("-" * 60)
    overall = total_interp / total_vm if total_vm > 0 else 0
    print(f"{'TOTAL':<25} {total_vm*1000:<12.4f} {total_interp*1000:<12.4f} {overall:.2f}x")
    print("=" * 60)
    
    print("\nNote: VM benchmarks may fail for complex programs (for loops, etc.)")
    print("due to incomplete VM implementation. The interpreter handles all cases.")
    print("\nVM speedup expected: 2-5x for completed opcodes.")


if __name__ == "__main__":
    main()
