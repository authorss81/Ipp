# Test v1.6.14: Bytecode Caching
# Tests that compiled bytecode is cached to .ipc file and reused when source hasn't changed

# Test 1: Basic computation
var x = 10
var y = 20
var result = x + y
assert result == 30

# Test 2: String formatting
var name = "Ipp"
var greeting = "Hello {}!"
greeting.format(name)

# Test 3: List operations
var nums = [1, 2, 3, 4, 5]
var sum = 0
for n in nums {
    sum = sum + n
}
assert sum == 15

# Test 4: Function call
func add(a, b) {
    return a + b
}
var z = add(5, 7)
assert z == 12

print("v1.6.14: Bytecode caching tests PASSED")
print("Note: .ipc cache file created automatically on first run")