# Test v1.5.22: pi and e constants
# Bug: pi and e were lambda functions, not constants

assert pi > 3.14
assert pi < 3.15
assert e > 2.71
assert e < 2.72

# Test in expressions
var area = pi * 2 * 2  # pi * r^2 with r=2
assert area > 12.5
assert area < 12.6

var val = e * 2
assert val > 5.4
assert val < 5.5

print("v1.5.22: pi and e constants tests PASSED")