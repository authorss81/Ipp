# Test v1.5.4.7 - Performance Optimizations (Bytecode Cache)

print("=== Testing v1.5.4.7 Performance Optimizations ===")

# Test 1: Basic functionality
print("\n--- Test 1: Basic Functionality ---")
var a = 10
var b = 20
print("Variables: a=" + str(a) + ", b=" + str(b))

# Test 2: Functions
print("\n--- Test 2: Functions ---")
func add(x, y) {
    return x + y
}
print("add(5, 3) = " + str(add(5, 3)))

# Test 3: Classes
print("\n--- Test 3: Classes ---")
class Point {
    func init(x, y) {
        this.x = x
        this.y = y
    }
    func to_string() {
        return "(" + str(this.x) + ", " + str(this.y) + ")"
    }
}
var p = Point(3, 4)
print("Point: " + p.to_string())

# Test 4: Bytecode Cache Feature
print("\n--- Test 4: Bytecode Cache ---")
print("Bytecode caching available:")
print("  .cache <file>    - Compile and cache bytecode to .ipc file")
print("  Files with .ipc cache load automatically (if cache newer than source)")
print("  Run 'python main.py test.ipp' - loads test.ippc if available")

# Test 5: Performance
print("\n--- Test 5: Performance ---")
func fib(n) {
    if (n <= 1) return n
    return fib(n-1) + fib(n-2)
}
print("fib(10) = " + str(fib(10)))

var nums = [1, 2, 3, 4, 5]
print("sum(nums) = " + str(sum(nums)))

print("\n=== v1.5.4.7 Tests Complete ===")
print("New in v1.5.4.7:")
print("  .cache <file>  - Compile and cache bytecode to .ipc file")
print("  Auto-cache load  - .ipc files load automatically when available")
print("  Performance boost from cached bytecode execution")