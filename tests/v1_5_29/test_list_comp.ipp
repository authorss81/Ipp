# Test v1.5.29: List comprehension
# Note: Works in interpreter mode, deferred in VM

var squares = [x * x for x in range(5)]
assert squares == [0, 1, 4, 9, 16]

var doubled = [x * 2 for x in [1, 2, 3]]
assert doubled == [2, 4, 6]

print("v1.5.29: List comprehension tests PASSED")