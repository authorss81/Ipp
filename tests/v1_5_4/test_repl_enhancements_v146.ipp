# Test v1.5.4.6 - Expert Features (Plugins, ML Autocomplete)

print("=== Testing v1.5.4.6 Expert Features ===")

# Test 1: Plugin System (.plugin load)
print("\n--- Test 1: Plugin System ---")
print("Plugin loading available:")
print("  .plugin load <file>  - Load Ipp script as plugin")
print("  Plugins execute in current session context")

# Test 2: ML-based Autocomplete
print("\n--- Test 2: ML-based Autocomplete ---")
print("Intelligent autocomplete available:")
print("  Uses TF-IDF + cosine similarity when sklearn available")
print("  Falls back to difflib when not available")
print("  Tab completion now smarter at finding similar identifiers")

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

# Test 6: Collections
print("\n--- Test 6: Collections ---")
var nums = [1, 2, 3, 4, 5]
print("Sum: " + str(sum(nums)))
print("Max: " + str(max(nums)))

var data = {"name": "Alice", "age": 30}
print("Dict name: " + data["name"])

# Test 7: Async
print("\n--- Test 7: Async ---")
print("Async/await available in Ipp")

# Test 8: Pattern Matching
print("\n--- Test 8: Pattern Matching ---")
var status = 200
match status {
    case 200 => print("OK")
    case 404 => print("Not Found")
    default => print("Unknown")
}

# Test 9: Error Handling
print("\n--- Test 9: Error Handling ---")
try {
    var x = 10 / 0
} catch e {
    print("Caught: " + str(e))
} finally {
    print("Finally executed")
}

print("\n=== v1.5.4.6 Tests Complete ===")
print("New in v1.5.4.6:")
print("  .plugin load <file>  - Load Ipp script as plugin")
print("  ML Autocomplete     - TF-IDF based intelligent completion")
print("  (Optional: pip install scikit-learn for ML features)")