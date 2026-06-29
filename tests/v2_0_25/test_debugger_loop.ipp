# v2.0.25 — breakpoint() inside loops
print("=== v2.0.25 breakpoint in loop ===")

var sum = 0
for i in range(5) {
    breakpoint()
    sum = sum + i
}
assert sum == 10
print("  PASS: breakpoint in for loop")

var j = 0
while j < 3 {
    breakpoint()
    j = j + 1
}
assert j == 3
print("  PASS: breakpoint in while loop")

print("All v2.0.25 loop edge case tests passed!")
