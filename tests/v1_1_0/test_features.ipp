# Test v1.1.0 - Performance Optimization & Profiler

print("=== Testing v1.1.0 Performance Optimization ===")

# ====== Math Operations ======
print("\n--- Math Operations ---")

var result = 0
var i = 0
while i < 1000 {
    result = result + i
    i = i + 1
}
print("Sum 0..999 = " + str(result))

var fib_result = 0
func fib(n) {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

fib_result = fib(15)
print("fib(15) = " + str(fib_result))

# ====== List Operations ======
print("\n--- List Operations ---")

var nums = []
var j = 0
while j < 100 {
    nums.append(j * 2)
    j = j + 1
}
print("List length: " + str(len(nums)))

var total = 0
j = 0
while j < len(nums) {
    total = total + nums[j]
    j = j + 1
}
print("Sum of doubled: " + str(total))

# ====== String Operations ======
print("\n--- String Operations ---")

var s = ""
j = 0
while j < 50 {
    s = s + "x"
    j = j + 1
}
print("String length: " + str(len(s)))

# ====== Function Calls ======
print("\n--- Function Calls ---")

func add(a, b) {
    return a + b
}

func multiply(a, b) {
    return a * b
}

var func_result = 0
j = 0
while j < 100 {
    func_result = add(func_result, j)
    j = j + 1
}
print("Function call sum: " + str(func_result))

# ====== Class Operations ======
print("\n--- Class Operations ---")

class Counter {
    func init(start) {
        this.value = start
    }
    
    func increment() {
        this.value = this.value + 1
    }
    
    func get() {
        return this.value
    }
}

var counter = Counter(0)
j = 0
while j < 50 {
    counter.increment()
    j = j + 1
}
print("Counter value: " + str(counter.get()))

# ====== Dict Operations ======
print("\n--- Dict Operations ---")

var d = {}
j = 0
while j < 100 {
    d[str(j)] = j * j
    j = j + 1
}
print("Dict size: " + str(len(d)))

# ====== Closure Performance ======
print("\n--- Closure Performance ---")

func make_adder(n) {
    func adder(x) {
        return x + n
    }
    return adder
}

var add10 = make_adder(10)
var closure_result = 0
j = 0
while j < 100 {
    closure_result = closure_result + add10(j)
    j = j + 1
}
print("Closure sum: " + str(closure_result))

# ====== Nested Loops ======
print("\n--- Nested Loops ---")

var nested_sum = 0
var outer = 0
while outer < 10 {
    var inner = 0
    while inner < 10 {
        nested_sum = nested_sum + outer + inner
        inner = inner + 1
    }
    outer = outer + 1
}
print("Nested loop sum: " + str(nested_sum))

# ====== Recursion ======
print("\n--- Recursion ---")

func sum_range(start, end) {
    if start >= end {
        return 0
    }
    return start + sum_range(start + 1, end)
}

var recursive_result = sum_range(0, 100)
print("Recursive sum: " + str(recursive_result))

print("\nv1.1.0 tests complete!")
