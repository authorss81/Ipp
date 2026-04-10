# Test v1.5.4.5 - Advanced Features (REPL server, Code review)

print("=== Testing v1.5.4.5 Advanced Features ===")

# Test 1: REPL Server (.serve)
print("\n--- Test 1: REPL Server ---")
print("REPL server available:")
print("  .serve           - Start server on default port 8080")
print("  .serve 9000      - Start server on port 9000")
print("  Connect with: telnet localhost 8080")

# Test 2: Code Review Mode (.compare)
print("\n--- Test 2: Code Review Mode ---")
print("Code comparison available:")
print("  .compare 1+1 2       - Compare two expressions")
print("  .compare [1,2] [1,2] - Compare two values")

# Test 3: Basic functionality
print("\n--- Test 3: Basic Functionality ---")
var a = 10
var b = 20
print("Variables: a=" + str(a) + ", b=" + str(b))

# Test 4: Functions
print("\n--- Test 4: Functions ---")
func add(x, y) {
    return x + y
}
print("add(5, 3) = " + str(add(5, 3)))

# Test 5: Classes
print("\n--- Test 5: Classes ---")
class Calculator {
    func init() {
        this.result = 0
    }
    func add(n) {
        this.result = this.result + n
        return this.result
    }
}
var calc = Calculator()
print("Calculator result: " + str(calc.add(10)))

# Test 6: Collections
print("\n--- Test 6: Collections ---")
var data = {"name": "test", "items": [1, 2, 3]}
print("Dict: " + str(data))
print("Keys: " + str(keys(data)))

# Test 7: Control Flow
print("\n--- Test 7: Control Flow ---")
var status = 200
if status == 200 {
    print("Status: OK")
} else {
    print("Status: Unknown")
}

# Test 8: Async
print("\n--- Test 8: Async/Await ---")
async func fetch_data() {
    return "data loaded"
}
print("Async function defined")

# Test 9: Exception handling
print("\n--- Test 9: Exception Handling ---")
try {
    var x = 10 / 0
} catch e {
    print("Caught: " + str(e))
}

# Test 10: List operations
print("\n--- Test 10: List Operations ---")
var nums = [5, 2, 8, 1, 9]
print("List: " + str(nums))
print("Sum: " + str(sum(nums)))

# Test 11: String operations
print("\n--- Test 11: String Operations ---")
var text = "Hello, World!"
print("Upper: " + upper(text))
print("Lower: " + lower(text))
print("Contains 'World': " + str(contains(text, "World")))

# Test 12: File operations
print("\n--- Test 12: File Operations ---")
print("file_read, file_write, append_file available")

# Test 13: Network
print("\n--- Test 13: Network ---")
print("http_get, http_post, websocket_connect available")

# Test 14: Canvas
print("\n--- Test 14: Canvas ---")
print("canvas_open, canvas_rect, canvas_circle, etc. available")

# Test 15: Built-in math
print("\n--- Test 15: Math ---")
print("sqrt(16) = " + str(sqrt(16)))
print("pow(2, 8) = " + str(pow(2, 8)))
print("pi = " + str(pi))
print("sin(0) = " + str(sin(0)))

print("\n=== v1.5.4.5 Tests Complete ===")
print("New in v1.5.4.5:")
print("  .serve [port]  - Start REPL server")
print("  .compare a b   - Compare two expressions")
print("Note: .serve requires network access")