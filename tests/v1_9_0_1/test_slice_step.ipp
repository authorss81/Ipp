# Test list[a..b..step] slice syntax (v1.9.0.1)

var lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Step slicing
assert lst[0..10..2] == [0, 2, 4, 6, 8]
assert lst[1..9..3] == [1, 4, 7]

# String slice with step
var s = "abcdefghij"
assert s[0..10..2] == "acegi"

# Basic slice (without step) still works
assert lst[1..4] == [1, 2, 3]
assert s[0..5] == "abcde"

# Step of 1 gives same as no step
assert lst[0..10..1] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Reversed slice (end is exclusive per .. convention)
assert lst[9..2..-1] == [9, 8, 7, 6, 5, 4, 3]
assert lst[5..0..-1] == [5, 4, 3, 2, 1]

# Animation frame sequence
var all_frames = range(24)
var key_frames = all_frames[0..24..4]
assert key_frames == [0, 4, 8, 12, 16, 20]

# Variable step
var step = 3
assert lst[0..10..step] == [0, 3, 6, 9]

print("OK")
