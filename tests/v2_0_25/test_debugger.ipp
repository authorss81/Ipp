# v2.0.25 — Debugger with Breakpoints
print("=== v2.0.25 Debugger tests ===")

# Test 1: breakpoint() continues normally
var x = 1
breakpoint()
x = 2
assert x == 2
print("  PASS: breakpoint() continues normally")

# Test 2: breakpoint() in a function
func test_fn(n) {
    breakpoint()
    return n * 2
}

var result = test_fn(21)
assert result == 42
print("  PASS: breakpoint() in function")

# Test 3: multiple breakpoints
var a = 0
breakpoint()
a = 10
breakpoint()
a = 20
assert a == 20
print("  PASS: multiple breakpoints")

print("All v2.0.25 debugger tests passed!")
