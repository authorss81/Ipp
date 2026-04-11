# Test v1.5.16 - VM/Performance

print("=== Testing v1.5.16 VM/Performance ===")

# Test 1: for loop in VM mode (using 'total' to avoid conflict with builtin 'sum')
var total = 0
for i in 0..5 {
    total = total + i
}
print("for loop total: " + str(total))

# Test 2: function returning value
func add(a, b) {
    return a + b
}
var result = add(2, 3)
print("function return: " + str(result))

# Test 3: Lambda
var mul = func(x, y) => x * y
print("lambda return: " + str(mul(4, 5)))

# Test 4: Match expression
var n = 2
var msg = match n {
    case 1 => "one"
    case 2 => "two"
    else => "other"
}
print("match result: " + msg)

# Test 5: Enum
enum Color {
    RED,
    GREEN,
    BLUE
}
print("enum: " + str(Color.RED))

print("=== v1.5.16 Tests Complete ===")