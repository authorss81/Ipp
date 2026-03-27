# ============================================
# Ipp Language Benchmarks v1.2.0
# ============================================
# Comprehensive benchmarks for Ipp language performance testing.
# Run with: python main.py run tests/v1/benchmarks/ipp_benchmarks.ipp
# ============================================

print("=" * 60)
print("IPP BENCHMARKS v1.2.0")
print("=" * 60)

# --------------------------------------------
# Benchmark 1: Integer Arithmetic
# --------------------------------------------
print("\n--- Benchmark 1: Integer Arithmetic ---")

func bench_integer_add(n) {
    var sum = 0
    for i in 0..n {
        sum = sum + i
    }
    return sum
}

func bench_integer_mul(n) {
    var product = 1
    for i in 1..n {
        product = product * i
    }
    return product
}

func bench_integer_mod(n) {
    var result = 0
    for i in 0..n {
        result = result + (i % 7)
    }
    return result
}

var iterations = 100000

var start = time()
var result1 = bench_integer_add(iterations)
var elapsed1 = time() - start
print("Integer Add: " + str(result1) + " in " + str(elapsed1) + "s")

start = time()
result1 = bench_integer_mul(10)
elapsed1 = time() - start
print("Integer Mul (10!): " + str(result1) + " in " + str(elapsed1) + "s")

start = time()
result1 = bench_integer_mod(iterations)
elapsed1 = time() - start
print("Integer Mod: " + str(result1) + " in " + str(elapsed1) + "s")

# --------------------------------------------
# Benchmark 2: Floating Point Math
# --------------------------------------------
print("\n--- Benchmark 2: Floating Point Math ---")

func bench_float_trig(n) {
    var sum = 0.0
    for i in 0..n {
        sum = sum + sin(i)
    }
    return sum
}

func bench_float_sqrt(n) {
    var sum = 0.0
    for i in 1..n {
        sum = sum + sqrt(i)
    }
    return sum
}

iterations = 50000

start = time()
var result2 = bench_float_trig(iterations)
var elapsed2 = time() - start
print("Float Trig (sin): " + str(result2) + " in " + str(elapsed2) + "s")

start = time()
result2 = bench_float_sqrt(iterations)
elapsed2 = time() - start
print("Float Sqrt: " + str(result2) + " in " + str(elapsed2) + "s")

# --------------------------------------------
# Benchmark 3: String Operations
# --------------------------------------------
print("\n--- Benchmark 3: String Operations ---")

func bench_string_concat(n) {
    var s = ""
    for i in 0..n {
        s = s + "x"
    }
    return len(s)
}

func bench_string_split(s, n) {
    var result = []
    for i in 0..n {
        var parts = split(s, ",")
        result.append(len(parts))
    }
    return len(result)
}

iterations = 5000

start = time()
var result3 = bench_string_concat(iterations)
var elapsed3 = time() - start
print("String Concat: " + str(result3) + " in " + str(elapsed3) + "s")

var test_string = "a,b,c,d,e,f,g,h,i,j"
start = time()
result3 = bench_string_split(test_string, iterations)
elapsed3 = time() - start
print("String Split: " + str(result3) + " in " + str(elapsed3) + "s")

# --------------------------------------------
# Benchmark 4: Function Calls
# --------------------------------------------
print("\n--- Benchmark 4: Function Calls ---")

func bench_recursive_fib(n) {
    if n <= 1 {
        return n
    }
    return bench_recursive_fib(n - 1) + bench_recursive_fib(n - 2)
}

func bench_iterative_fib(n) {
    if n <= 1 {
        return n
    }
    var a = 0
    var b = 1
    for i in 2..n+1 {
        var temp = b
        b = a + b
        a = temp
    }
    return b
}

func bench_higher_order(n, f) {
    var result = 0
    for i in 0..n {
        result = result + f(i)
    }
    return result
}

func simple_add(n) {
    return n + 1
}

iterations = 20

start = time()
var result4 = bench_recursive_fib(iterations)
var elapsed4 = time() - start
print("Recursive Fibonacci(20): " + str(result4) + " in " + str(elapsed4) + "s")

start = time()
result4 = bench_iterative_fib(10000)
elapsed4 = time() - start
print("Iterative Fibonacci(10000): " + str(result4) + " in " + str(elapsed4) + "s")

start = time()
result4 = bench_higher_order(50000, simple_add)
elapsed4 = time() - start
print("Higher-Order Function: " + str(result4) + " in " + str(elapsed4) + "s")

# --------------------------------------------
# Benchmark 5: List Operations
# --------------------------------------------
print("\n--- Benchmark 5: List Operations ---")

func bench_list_append(n) {
    var lst = []
    for i in 0..n {
        lst.append(i)
    }
    return lst
}

func bench_list_iterate(lst) {
    var sum = 0
    for x in lst {
        sum = sum + x
    }
    return sum
}

func bench_list_comprehension(n) {
    return [i * 2 for i in 0..n]
}

iterations = 50000

start = time()
var test_list = bench_list_append(iterations)
var elapsed5 = time() - start
print("List Append (50000): " + str(len(test_list)) + " items in " + str(elapsed5) + "s")

start = time()
var result5 = bench_list_iterate(test_list)
elapsed5 = time() - start
print("List Iterate: " + str(result5) + " in " + str(elapsed5) + "s")

start = time()
var comp_list = bench_list_comprehension(iterations)
elapsed5 = time() - start
print("List Comprehension: " + str(len(comp_list)) + " items in " + str(elapsed5) + "s")

# --------------------------------------------
# Benchmark 6: Dict Operations
# --------------------------------------------
print("\n--- Benchmark 6: Dict Operations ---")

func bench_dict_create(n) {
    var d = {}
    for i in 0..n {
        d[str(i)] = i * i
    }
    return len(d)
}

iterations = 10000

start = time()
var test_dict = bench_dict_create(iterations)
var elapsed6 = time() - start
print("Dict Create (10000 entries): " + str(test_dict) + " entries in " + str(elapsed6) + "s")

# --------------------------------------------
# Benchmark 7: Nested Loops
# --------------------------------------------
print("\n--- Benchmark 7: Nested Loops ---")

func bench_nested_loops(outer_n, inner_n) {
    var sum = 0
    for i in 0..outer_n {
        for j in 0..inner_n {
            sum = sum + i + j
        }
    }
    return sum
}

var outer_n = 100
var inner_n = 100

start = time()
var result7 = bench_nested_loops(outer_n, inner_n)
var elapsed7 = time() - start
print("Nested Loops (100x100): " + str(result7) + " in " + str(elapsed7) + "s")

# --------------------------------------------
# Benchmark 8: Closure Performance
# --------------------------------------------
print("\n--- Benchmark 8: Closure Performance ---")

func make_counter(start_val) {
    var count = start_val
    func increment() {
        count = count + 1
        return count
    }
    return increment
}

func bench_closures(n) {
    var counter = make_counter(0)
    var sum = 0
    for i in 0..n {
        sum = sum + counter()
    }
    return sum
}

iterations = 10000

start = time()
var result8 = bench_closures(iterations)
var elapsed8 = time() - start
print("Closure Counter (" + str(iterations) + " calls): " + str(result8) + " in " + str(elapsed8) + "s")

# --------------------------------------------
# Benchmark 9: List of Dicts
# --------------------------------------------
print("\n--- Benchmark 9: List of Dicts ---")

func bench_list_of_dicts(n) {
    var data = []
    for i in 0..n {
        data.append({"id": i, "value": i * 10})
    }
    return len(data)
}

func bench_access_list_of_dicts(data, n) {
    var sum = 0
    for i in 0..n {
        sum = sum + data[i]["value"]
    }
    return sum
}

iterations = 5000

start = time()
var list_dict = []
for i in 0..iterations {
    list_dict.append({"id": i, "value": i * 10})
}
var elapsed9 = time() - start
print("List of Dicts Create (" + str(iterations) + "): " + str(len(list_dict)) + " in " + str(elapsed9) + "s")

start = time()
var result9 = bench_access_list_of_dicts(list_dict, iterations)
elapsed9 = time() - start
print("List of Dicts Access Sum: " + str(result9) + " in " + str(elapsed9) + "s")

# --------------------------------------------
# Benchmark 10: Class/Object Operations
# --------------------------------------------
print("\n--- Benchmark 10: Class/Object Operations ---")

class Point {
    func init(x, y) {
        this.x = x
        this.y = y
    }
    
    func add(other) {
        return Point(this.x + other.x, this.y + other.y)
    }
}

func bench_objects(n) {
    var points = []
    for i in 0..n {
        points.append(Point(i, i))
    }
    return len(points)
}

iterations = 5000

start = time()
var points = bench_objects(iterations)
var elapsed10 = time() - start
print("Object Create (" + str(iterations) + " Points): " + str(points) + " in " + str(elapsed10) + "s")

print("\n" + "=" * 60)
print("BENCHMARKS COMPLETE")
print("=" * 60)
