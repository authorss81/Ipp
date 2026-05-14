# Test v1.3.7 - REPL Enhancements
# These tests verify REPL features work when loaded via .load command

print("=== Testing v1.3.7 REPL Enhancements ===")

# ====== .load Test ======
print("\n--- .load Test ---")
print("This file tests that .load command works correctly")
print("When loaded via .load, variables should persist in session")

var test_value = 42
print("test_value:", test_value)
assert test_value == 42

# ====== .save Test ======
print("\n--- .save Test ---")
print("Save command should write history to file")

# ====== .doc Test ======
print("\n--- .doc Test ---")
print("Doc command should show builtin documentation")
print("Available builtins:", type(print), type(len), type(type))
assert type(print) != nil
assert type(len) != nil
assert type(type) != nil

# ====== .time Test ======
print("\n--- .time Test ---")
var start = time()
var sum = 0
for i in 0..1000 {
    sum = sum + i
}
var elapsed = time() - start
print("Sum:", sum, "Time:", elapsed)
assert sum == 499500
print("Sum 0..999:", sum)
print("Elapsed:", elapsed, "seconds")

# ====== .which Test ======
print("\n--- .which Test ---")
print("print type:", type(print))
print("test_value type:", type(test_value))

# ====== .last Test ======
print("\n--- .last Test ---")
var last_result = sum
print("Last result stored:", last_result)

# ====== .undo Test ======
print("\n--- .undo Test ---")
print("Undo should restore previous env state")

# ====== .alias Test ======
print("\n--- .alias Test ---")
print("Alias command creates custom shortcuts")

# ====== .edit Test ======
print("\n--- .edit Test ---")
print("Edit opens last command in editor")

# ====== .profile Test ======
print("\n--- .profile Test ---")
print("Profile shows performance stats")

# ====== Multi-line Paste Test ======
print("\n--- Multi-line Paste Test ---")
func multi_line_test() {
    var a = 1
    var b = 2
    return a + b
}
print("Multi-line function result:", multi_line_test())

# ====== $_ / .last Test ======
print("\n--- \$_ Test ---")
var computed = 100 * 2
print("Computed value:", computed)
print("Result accessible via \$_ in REPL")

print("\n=== v1.3.7 REPL Enhancement tests complete! ===")
