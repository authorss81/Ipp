# Test v1.0.1 - VM Stabilization

print("=== Testing v1.0.1 VM Stabilization ===")

# ====== Simple Math Test ======
print("\n--- Simple Math Test ---")

var result = 2 ** 10
print("2 ** 10 = " + str(result))
assert result == 1024

result = 15 // 4
print("15 // 4 = " + str(result))
assert result == 3

result = 10 & 7
print("10 & 7 = " + str(result))
assert result == 2

result = 5 | 3
print("5 | 3 = " + str(result))
assert result == 7

result = 1 << 3
print("1 << 3 = " + str(result))
assert result == 8

result = 8 >> 2
print("8 >> 2 = " + str(result))
assert result == 2

# ====== List Operations ======
print("\n--- List Operations ---")

var nums = [1, 2, 3, 4, 5]
print("List: " + str(nums))
print("Length: " + str(len(nums)))
assert len(nums) == 5

nums[0] = 10
print("After update: " + str(nums))
assert nums[0] == 10

var sum_nums = sum(nums)
print("Sum: " + str(sum_nums))
assert sum_nums == 24

# ====== String Operations ======
print("\n--- String Operations ---")

var name = "Ipp"
var greeting = "Hello, " + name + "!"
print(greeting)
assert greeting == "Hello, Ipp!"

# ====== Function Call ======
print("\n--- Function Call ---")

func add(a, b) {
    return a + b
}

var sum_result = add(5, 3)
print("add(5, 3) = " + str(sum_result))
assert sum_result == 8

func factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

var fact5 = factorial(5)
print("5! = " + str(fact5))
assert fact5 == 120

# ====== While Loop ======
print("\n--- While Loop ---")

var i = 0
var count = 0
while i < 5 {
    count = count + i
    i = i + 1
}
print("Sum 0..4 = " + str(count))
assert count == 10

# ====== If/Else ======
print("\n--- If/Else ---")

func max(a, b) {
    if a > b {
        return a
    }
    return b
}

var m1 = max(3, 7)
print("max(3, 7) = " + str(m1))
assert m1 == 7

var m2 = max(10, 5)
print("max(10, 5) = " + str(m2))
assert m2 == 10

# ====== Dict Operations ======
print("\n--- Dict Operations ---")

var person = {"name": "Alice", "age": 30}
print("Person: " + str(person))
print("Name: " + str(person["name"]))
assert person["name"] == "Alice"
assert person["age"] == 30

person["city"] = "NYC"
print("Updated: " + str(person))
assert person["city"] == "NYC"

# ====== Nested Functions ======
print("\n--- Nested Functions ---")

func outer(x) {
    func inner(y) {
        return x + y
    }
    return inner
}

var closure_fn = outer(10)
var closure_result = closure_fn(5)
print("outer(10)(5) = " + str(closure_result))
assert closure_result == 15

# ====== Recursion ======
print("\n--- Recursion ---")

func fibonacci(n) {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

var fib10 = fibonacci(10)
print("fibonacci(10) = " + str(fib10))
assert fib10 == 55

# ====== Ternary Operator ======
print("\n--- Ternary Operator ---")

var ternary = 5 > 3 ? "yes" : "no"
print("5 > 3 ? 'yes' : 'no' = " + str(ternary))
assert ternary == "yes"

# ====== Nullish Coalescing ======
print("\n--- Nullish Coalescing ---")

var null_val = nil
var coalesced = null_val ?? "default"
print("nil ?? 'default' = " + str(coalesced))
assert coalesced == "default"

# ====== Built-in Functions ======
print("\n--- Built-in Functions ---")

print("abs(-5) = " + str(abs(-5)))
assert abs(-5) == 5
print("min(3, 7) = " + str(min(3, 7)))
assert min(3, 7) == 3
print("max(3, 7) = " + str(max(3, 7)))
assert max(3, 7) == 7
print("floor(3.7) = " + str(floor(3.7)))
assert floor(3.7) == 3
print("ceil(3.2) = " + str(ceil(3.2)))
assert ceil(3.2) == 4
print("sqrt(16) = " + str(sqrt(16)))
assert sqrt(16) == 4

# ====== Range Function ======
print("\n--- Range Function ---")

var r = range(5)
print("range(5) = " + str(r))
assert r[0] == 0
assert len(r) == 5

var r2 = range(1, 6)
print("range(1, 6) = " + str(r2))
assert r2[0] == 1
assert len(r2) == 5

var r3 = range(0, 10, 2)
print("range(0, 10, 2) = " + str(r3))
assert r3[0] == 0
assert r3[4] == 8

# ====== Try/Catch ======
print("\n--- Try/Catch ---")

var caught_test = false
try {
    throw "test error"
} catch e {
    caught_test = true
    print("Caught: " + str(e))
} finally {
    print("Finally block executed")
}
assert caught_test == true

# ====== Do-While ======
print("\n--- Do-While ---")

var dw_i = 0
var dw_count = 0
repeat {
    dw_count = dw_count + dw_i
    dw_i = dw_i + 1
} until dw_i >= 5
print("Do-while sum 0..4 = " + str(dw_count))
assert dw_count == 10

# ====== Match Statement ======
print("\n--- Match Statement ---")

var day = 2
var match_result = 0
match day {
    case 1 => match_result = 1
    case 2 => match_result = 2
    case 3 => match_result = 3
    default => match_result = 0
}
print("Day " + str(day) + " = " + str(match_result))
assert match_result == 2

print("\nv1.0.1 tests complete!")
