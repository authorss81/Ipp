# Test v1.0.0 - Bytecode VM

print("=== Testing v1.0.0 Bytecode VM ===")

# ====== Simple Math Test ======
print("\n--- Simple Math Test ---")

var result = 2 ** 10
print("2 ** 10 = " + str(result))

result = 15 // 4
print("15 // 4 = " + str(result))

result = 10 & 7
print("10 & 7 = " + str(result))

# ====== List Operations ======
print("\n--- List Operations ---")

var nums = [1, 2, 3, 4, 5]
print("Sum: " + str(sum(nums)))

var doubled = [x * 2 for x in nums]
print("Doubled: " + str(doubled))

# ====== String Operations ======
print("\n--- String Operations ---")

var name = "Ipp"
var greeting = "Hello, " + name + "!"
print(greeting)

var upper = greeting.upper()
print("Upper: " + upper)

# ====== Function Call ======
print("\n--- Function Call ---")

func factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

print("5! = " + str(factorial(5)))

# ====== Class Test ======
print("\n--- Class Test ---")

class Point {
    func init(x, y) {
        this.x = x
        this.y = y
    }
    
    func __str__() {
        return "Point(" + str(this.x) + ", " + str(this.y) + ")"
    }
}

var p = Point(3, 4)
print(p)

print("\nv1.0.0 tests complete!")
