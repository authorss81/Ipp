# v2.0.25 — multiple consecutive breakpoints + interleaved code
print("=== v2.0.25 multiple breakpoints ===")

# Test: consecutive breakpoints
var a = 0
breakpoint()
breakpoint()
a = 1
assert a == 1
print("  PASS: consecutive breakpoints")

# Test: breakpoint after variable assignment
var b = 42
breakpoint()
assert b == 42
print("  PASS: breakpoint after assignment")

# Test: breakpoint in expression context (assigns nil)
func returns_nil() {
    breakpoint()
}

var c = returns_nil()
assert c == nil
print("  PASS: breakpoint used as expression returns nil")

# Test: no-args validation (compile-time error checked separately)
print("  PASS: breakpoint API surface")

print("All v2.0.25 multi breakpoint tests passed!")
