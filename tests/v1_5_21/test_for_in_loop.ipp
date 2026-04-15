# Test v1.5.21: For-in loop in VM
# Bug: For-in loop never executed due to reversed comparison

var sum = 0
for i in [1, 2, 3, 4, 5] {
    sum = sum + i
}
assert sum == 15

# Test with range
var sum2 = 0
for i in range(5) {
    sum2 = sum2 + i
}
assert sum2 == 10

# Test with string iteration
var result = ""
for c in "abc" {
    result = result + c
}
assert result == "abc"

print("v1.5.21: For-in loop tests PASSED")