# assert_frame exists and returns true when canvas not available
assert assert_frame != nil, "assert_frame exists"
assert type(assert_frame) == "function", "assert_frame is function"

# Without a canvas window open, assert_frame should return true (skip)
var result = assert_frame("nonexistent.png")
assert result == true, "assert_frame skips when no canvas"

# With threshold param
var result2 = assert_frame("nonexistent.png", 0.05)
assert result2 == true, "assert_frame with threshold"

print("All v2.0.20.3 assert_frame tests passed!")
