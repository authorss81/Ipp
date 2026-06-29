# v2.0.25 — breakpoint() in nested functions
print("=== v2.0.25 breakpoint nested ===")

func inner(x) {
    breakpoint()
    return x + 1
}

func outer(n) {
    breakpoint()
    return inner(n * 2)
}

var result = outer(5)
assert result == 11
print("  PASS: breakpoint in nested functions")

func factorial(n) {
    if n <= 1 {
        return 1
    }
    breakpoint()
    return n * factorial(n - 1)
}

var f = factorial(4)
assert f == 24
print("  PASS: breakpoint in recursive function")

print("All v2.0.25 nested edge case tests passed!")
