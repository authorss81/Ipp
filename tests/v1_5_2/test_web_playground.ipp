# Test v1.5.2b - Web Playground Features

print("=== Testing v1.5.2b Web Playground Interpreter ===")

# ====== Variables ======
print("\n--- Variables ---")
var x = 10
var y = 20
var name = "Ipp"
var isActive = true
print("x = " + str(x))
print("y = " + str(y))
print("name = " + name)
print("isActive = " + str(isActive))
assert x == 10, "Variable assignment works"
assert name == "Ipp", "String variable works"
assert isActive == true, "Boolean variable works"

# ====== Arithmetic ======
print("\n--- Arithmetic ---")
print("x + y = " + str(x + y))
print("x - y = " + str(x - y))
print("x * y = " + str(x * y))
print("x / y = " + str(x / y))
print("x % y = " + str(x % y))
print("x ** 2 = " + str(x ** 2))
assert x + y == 30, "Addition works"
assert x - y == -10, "Subtraction works"
assert x * y == 200, "Multiplication works"
assert x / y == 0.5, "Division works"
assert x % y == 10, "Modulo works"
assert x ** 2 == 100, "Power works"

# ====== Lists ======
print("\n--- Lists ---")
var nums = [1, 2, 3, 4, 5]
print("List: " + str(nums))
print("Length: " + str(len(nums)))
print("First: " + str(nums[0]))
print("Last: " + str(nums[4]))
assert len(nums) == 5, "List length works"
assert nums[0] == 1, "List index access works"
assert nums[4] == 5, "List last element works"

# ====== For Loop ======
print("\n--- For Loop ---")
var sum = 0
for i in 0..5 {
    sum = sum + i
}
print("Sum 0..5 = " + str(sum))
assert sum == 10, "For loop range works"

# ====== Functions ======
print("\n--- Functions ---")
func add(a, b) {
    return a + b
}
print("add(3, 4) = " + str(add(3, 4)))
assert add(3, 4) == 7, "Function with args works"

func multiply(a, b) {
    return a * b
}
print("multiply(5, 6) = " + str(multiply(5, 6)))
assert multiply(5, 6) == 30, "Function multiply works"

func factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
print("factorial(5) = " + str(factorial(5)))
assert factorial(5) == 120, "Factorial recursion works"

# ====== String Functions ======
print("\n--- String Functions ---")
var text = "Hello, World!"
print("text: " + text)
print("len(text) = " + str(len(text)))
assert len(text) == 13, "String length works"

# ====== Math Functions ======
print("\n--- Math Functions ---")
print("abs(-42) = " + str(abs(-42)))
assert abs(-42) == 42, "abs works"

# ====== Boolean ======
print("\n--- Boolean ---")
var a = true
var b = false
print("a and b = " + str(a and b))
print("a or b = " + str(a or b))
print("not a = " + str(not a))
assert (a and b) == false, "and works"
assert (a or b) == true, "or works"
assert (not a) == false, "not works"

# ====== Comparison ======
print("\n--- Comparison ---")
print("10 == 10: " + str(10 == 10))
print("10 != 5: " + str(10 != 5))
print("5 < 10: " + str(5 < 10))
print("20 > 10: " + str(20 > 10))
assert 10 == 10 == true, "== works"
assert 10 != 5 == true, "!= works"
assert 5 < 10 == true, "< works"
assert 20 > 10 == true, "> works"

# ====== Fibonacci ======
print("\n--- Fibonacci ---")
func fib(n) {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

print("fib(0) = " + str(fib(0)))
print("fib(1) = " + str(fib(1)))
print("fib(5) = " + str(fib(5)))
print("fib(10) = " + str(fib(10)))
assert fib(0) == 0, "fib(0) is 0"
assert fib(1) == 1, "fib(1) is 1"
assert fib(5) == 5, "fib(5) is 5"
assert fib(10) == 55, "fib(10) is 55"

# ====== Classes ======
print("\n--- Classes ---")
class Counter {
    func init() {
        this.count = 0
    }
    func increment() {
        this.count = this.count + 1
        return this.count
    }
    func get() {
        return this.count
    }
}

var c = Counter()
print("Counter start: " + str(c.get()))
print("After increment: " + str(c.increment()))
print("After increment: " + str(c.increment()))
assert c.get() == 2, "Class init works"
assert c.increment() == 3, "Class method works"
assert c.increment() == 4, "Class method increments"

print("\n=== v1.5.2b Web Playground tests complete! ===")