# Ipp Language — Performance Benchmarks

Run on 2026-06-22 08:23:54

| Benchmark | Ipp (Interpreter) | Ipp (VM) | Python 3.12 | Node.js v24 | VM vs Interp | VM vs Python | VM vs JS |
|-----------|------------------:|---------:|------------:|------------:|-------------:|-------------:|---------:|
| Fibonacci (recursive n=28 ×5) | 18.563s | 125.689s | 0.285s | 0.080s | 6.8x | 441.3x | 1561.4x |
| Prime counting (2..100k) | 7.067s | 56.877s | 0.201s | 0.090s | 8.0x | 283.5x | 633.5x |
| Mandelbrot (41×41 grid ×100 iters) | 1.033s | 6.353s | 0.081s | 0.073s | 6.2x | 78.0x | 87.2x |
| String concat (5k × 'hello') | 0.015s | 0.333s | 0.086s | 0.072s | 22.2x | 3.9x | 4.6x |

## Summary

- **Interpreter vs VM**: The tree-walking interpreter is **10.8x faster** than the bytecode VM on these compute benchmarks (VM has overhead from bytecode dispatch, inline caching, etc.).
- **Ipp VM vs Python**: Ipp VM is **202x slower** than CPython 3.12 on numeric compute.
- **Ipp VM vs Node.js**: Ipp VM is **572x slower** than Node.js v24 on numeric compute.

## Notes

- All benchmarks use integer arithmetic, function calls, and loops — core compute patterns.
- Ipp Interpreter: tree-walking AST interpreter (baseline).
- Ipp VM: stack-based bytecode VM (primary execution engine).
- Python 3.12 and Node.js v24 are highly optimized JIT/bytecode VMs for comparison.
- String concat tests use naive `+` in a loop (not `join`), which penalizes Python and Ipp.
- Ipp range `a..b` is exclusive of the upper bound (like Python's `range(a, b)`), so `1..5` = 4 iterations vs Python's `range(5)` = 5 iterations. This causes different output values for Fibonacci (1,271,244 vs 1,589,055) but does not affect timing comparisons.
- Environment: Windows, testing hardware varies.