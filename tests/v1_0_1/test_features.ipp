# Test v1.0.1 - VM Stabilization

print("=== Testing v1.0.1 VM Stabilization ===")

# ====== Simple Math Test ======
print("\n--- Simple Math Test ---")

var result = 2 ** 10
print("2 ** 10 = " + str(result))

result = 15 // 4
print("15 // 4 = " + str(result))

result = 10 & 7
print("10 & 7 = " + str(result))

result = 5 | 3
print("5 | 3 = " + str(result))

result = 1 << 3
print("1 << 3 = " + str(result))

result = 8 >> 2
print("8 >> 2 = " + str(result))

# ====== List Operations ======
print("\n--- List Operations ---")

var nums = [1, 2, 3, 4, 5]
print("List: " + str(nums))
print("Length: " + str(len(nums)))

nums[0] = 10
print("After update: " + str(nums))

var sum_nums = sum(nums)
print("Sum: " + str(sum_nums))

# ====== String Operations ======
print("\n--- String Operations ---")

var name = "Ipp"
var greeting = "Hello, " + name + "!"
print(greeting)

# ====== Function Call ======
print("\n--- Function Call ---")

func add(a, b) {
    return a + b
}

var sum_result = add(5, 3)
print("add(5, 3) = " + str(sum_result))

func factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

print("5! = " + str(factorial(5)))

# ====== While Loop ======
print("\n--- While Loop ---")

var i = 0
var count = 0
while i < 5 {
    count = count + i
    i = i + 1
}
print("Sum 0..4 = " + str(count))

# ====== If/Else ======
print("\n--- If/Else ---")

func max(a, b) {
    if a > b {
        return a
    }
    return b
}

print("max(3, 7) = " + str(max(3, 7)))
print("max(10, 5) = " + str(max(10, 5)))

# ====== Dict Operations ======
print("\n--- Dict Operations ---")

var person = {"name": "Alice", "age": 30}
print("Person: " + str(person))
print("Name: " + str(person["name"]))

person["city"] = "NYC"
print("Updated: " + str(person))

# ====== Nested Functions ======
print("\n--- Nested Functions ---")

func outer(x) {
    func inner(y) {
        return x + y
    }
    return inner
}

var closure_fn = outer(10)
print("outer(10)(5) = " + str(closure_fn(5)))

# ====== Recursion ======
print("\n--- Recursion ---")

func fibonacci(n) {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

print("fibonacci(10) = " + str(fibonacci(10)))

# ====== Ternary Operator ======
print("\n--- Ternary Operator ---")

var ternary = 5 > 3 ? "yes" : "no"
print("5 > 3 ? 'yes' : 'no' = " + str(ternary))

# ====== Nullish Coalescing ======
print("\n--- Nullish Coalescing ---")

var null_val = nil
var coalesced = null_val ?? "default"
print("nil ?? 'default' = " + str(coalesced))

# ====== Built-in Functions ======
print("\n--- Built-in Functions ---")

print("abs(-5) = " + str(abs(-5)))
print("min(3, 7) = " + str(min(3, 7)))
print("max(3, 7) = " + str(max(3, 7)))
print("floor(3.7) = " + str(floor(3.7)))
print("ceil(3.2) = " + str(ceil(3.2)))
print("sqrt(16) = " + str(sqrt(16)))

# ====== Range Function ======
print("\n--- Range Function ---")

var r = range(5)
print("range(5) = " + str(r))

var r2 = range(1, 6)
print("range(1, 6) = " + str(r2))

var r3 = range(0, 10, 2)
print("range(0, 10, 2) = " + str(r3))

# ====== Try/Catch ======
print("\n--- Try/Catch ---")

try {
    throw "test error"
} catch e {
    print("Caught: " + str(e))
} finally {
    print("Finally block executed")
}

# ====== Do-While ======
print("\n--- Do-While ---")

var dw_i = 0
var dw_count = 0
repeat {
    dw_count = dw_count + dw_i
    dw_i = dw_i + 1
} until dw_i >= 5
print("Do-while sum 0..4 = " + str(dw_count))

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

print("\nv1.0.1 tests complete!")
