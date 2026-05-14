# Test v1.6.13: String Format Method
# Uses format() builtin function or string.format() method

# Test basic positional format with builtin
var r1 = format("Hello {}!", "World")
assert r1 == "Hello World!"

# Test with multiple positional args
var r2 = format("x={}, y={}", 3, 4)
assert r2 == "x=3, y=4"

# Test with string concatenation in format
var name = "Bob"
var r3 = format("Hello {}!", name)
assert r3 == "Hello Bob!"

# Test empty format (no args)
var r4 = format("No args")
assert r4 == "No args"

# Test format with numbers
var r5 = format("Value: {}", 42)
assert r5 == "Value: 42"

# Test string.format() method with positional args
var r6 = "Hello {}!".format("World")
assert r6 == "Hello World!"

# Test string.format() method with named args (v1.6.13 key feature)
var r7 = "{name} is {age}".format(name="Alice", age=30)
assert r7 == "Alice is 30"

# Test mixed (named with method call)
var r8 = "Hello {}!".format("World")
assert r8 == "Hello World!"

print("v1.6.13: String Format Method tests PASSED")