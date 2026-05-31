# Test list[a..b] slice syntax (v1.9.0)

# Basic list slicing
var lst = [0, 1, 2, 3, 4, 5]
assert lst[1..4] == [1, 2, 3]
assert lst[0..3] == [0, 1, 2]
assert lst[3..6] == [3, 4, 5]
assert lst[0..1] == [0]
assert lst[5..5] == []

# String slicing
var s = "hello world"
assert s[0..5] == "hello"
assert s[6..11] == "world"
assert s[0..1] == "h"
assert s[11..11] == ""

# Slice with variables
var start = 1
var end = 4
assert lst[start..end] == [1, 2, 3]

# slice() function still works
assert slice(lst, 1, 4) == [1, 2, 3]

# Nested indexing still works
assert lst[0] == 0
assert lst[5] == 5

# Index access on result of slice
assert lst[1..4][0] == 1
assert lst[1..4][2] == 3

print("OK")
