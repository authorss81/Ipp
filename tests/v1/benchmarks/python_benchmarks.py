# ============================================
# Python Benchmark Comparison for Ipp v1.2.0
# ============================================
# Run this file to compare Python performance with Ipp benchmarks.

import time

print("=" * 60)
print("PYTHON BENCHMARKS v1.2.0")
print("=" * 60)

# --------------------------------------------
# Benchmark 1: Integer Arithmetic
# --------------------------------------------
print("\n--- Benchmark 1: Integer Arithmetic ---")

def bench_integer_add(n):
    total = 0
    for i in range(n):
        total += i
    return total

def bench_integer_mul(n):
    product = 1
    for i in range(1, n + 1):
        product *= i
    return product

def bench_integer_mod(n):
    result = 0
    for i in range(n):
        result += (i % 7)
    return result

iterations = 100000

start = time.perf_counter()
result1 = bench_integer_add(iterations)
elapsed1 = time.perf_counter() - start
print(f"Integer Add: {result1} in {elapsed1:.6f}s")

start = time.perf_counter()
result1 = bench_integer_mul(10)
elapsed1 = time.perf_counter() - start
print(f"Integer Mul (10!): {result1} in {elapsed1:.6f}s")

start = time.perf_counter()
result1 = bench_integer_mod(iterations)
elapsed1 = time.perf_counter() - start
print(f"Integer Mod: {result1} in {elapsed1:.6f}s")

# --------------------------------------------
# Benchmark 2: Floating Point Math
# --------------------------------------------
print("\n--- Benchmark 2: Floating Point Math ---")

import math

def bench_float_trig(n):
    total = 0.0
    for i in range(n):
        total += math.sin(i)
    return total

def bench_float_sqrt(n):
    total = 0.0
    for i in range(1, n + 1):
        total += math.sqrt(i)
    return total

iterations = 50000

start = time.perf_counter()
result2 = bench_float_trig(iterations)
elapsed2 = time.perf_counter() - start
print(f"Float Trig (sin): {result2} in {elapsed2:.6f}s")

start = time.perf_counter()
result2 = bench_float_sqrt(iterations)
elapsed2 = time.perf_counter() - start
print(f"Float Sqrt: {result2} in {elapsed2:.6f}s")

# --------------------------------------------
# Benchmark 3: String Operations
# --------------------------------------------
print("\n--- Benchmark 3: String Operations ---")

def bench_string_concat(n):
    s = ""
    for i in range(n):
        s += "x"
    return len(s)

def bench_string_split(s, n):
    result = []
    for i in range(n):
        parts = s.split(",")
        result.append(len(parts))
    return len(result)

iterations = 5000

start = time.perf_counter()
result3 = bench_string_concat(iterations)
elapsed3 = time.perf_counter() - start
print(f"String Concat: {result3} in {elapsed3:.6f}s")

test_string = "a,b,c,d,e,f,g,h,i,j"
start = time.perf_counter()
result3 = bench_string_split(test_string, iterations)
elapsed3 = time.perf_counter() - start
print(f"String Split: {result3} in {elapsed3:.6f}s")

# --------------------------------------------
# Benchmark 4: Function Calls
# --------------------------------------------
print("\n--- Benchmark 4: Function Calls ---")

def bench_recursive_fib(n):
    if n <= 1:
        return n
    return bench_recursive_fib(n - 1) + bench_recursive_fib(n - 2)

def bench_iterative_fib(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b

def bench_higher_order(n, f):
    result = 0
    for i in range(n):
        result += f(i)
    return result

def simple_add(n):
    return n + 1

iterations = 20

start = time.perf_counter()
result4 = bench_recursive_fib(iterations)
elapsed4 = time.perf_counter() - start
print(f"Recursive Fibonacci(20): {result4} in {elapsed4:.6f}s")

start = time.perf_counter()
result4 = bench_iterative_fib(10000)
elapsed4 = time.perf_counter() - start
print(f"Iterative Fibonacci(10000): {result4} in {elapsed4:.6f}s")

start = time.perf_counter()
result4 = bench_higher_order(50000, simple_add)
elapsed4 = time.perf_counter() - start
print(f"Higher-Order Function: {result4} in {elapsed4:.6f}s")

# --------------------------------------------
# Benchmark 5: List Operations
# --------------------------------------------
print("\n--- Benchmark 5: List Operations ---")

def bench_list_append(n):
    lst = []
    for i in range(n):
        lst.append(i)
    return lst

def bench_list_iterate(lst):
    total = 0
    for x in lst:
        total += x
    return total

def bench_list_comprehension(n):
    return [i * 2 for i in range(n)]

iterations = 50000

start = time.perf_counter()
test_list = bench_list_append(iterations)
elapsed5 = time.perf_counter() - start
print(f"List Append (50000): {len(test_list)} items in {elapsed5:.6f}s")

start = time.perf_counter()
result5 = bench_list_iterate(test_list)
elapsed5 = time.perf_counter() - start
print(f"List Iterate: {result5} in {elapsed5:.6f}s")

start = time.perf_counter()
comp_list = bench_list_comprehension(iterations)
elapsed5 = time.perf_counter() - start
print(f"List Comprehension: {len(comp_list)} items in {elapsed5:.6f}s")

# --------------------------------------------
# Benchmark 6: Dict Operations
# --------------------------------------------
print("\n--- Benchmark 6: Dict Operations ---")

def bench_dict_create(n):
    d = {}
    for i in range(n):
        d[str(i)] = i * i
    return len(d)

iterations = 10000

start = time.perf_counter()
test_dict = bench_dict_create(iterations)
elapsed6 = time.perf_counter() - start
print(f"Dict Create (10000 entries): {test_dict} entries in {elapsed6:.6f}s")

# --------------------------------------------
# Benchmark 7: Nested Loops
# --------------------------------------------
print("\n--- Benchmark 7: Nested Loops ---")

def bench_nested_loops(outer_n, inner_n):
    total = 0
    for i in range(outer_n):
        for j in range(inner_n):
            total += i + j
    return total

outer_n = 100
inner_n = 100

start = time.perf_counter()
result7 = bench_nested_loops(outer_n, inner_n)
elapsed7 = time.perf_counter() - start
print(f"Nested Loops (100x100): {result7} in {elapsed7:.6f}s")

# --------------------------------------------
# Benchmark 8: Closure Performance
# --------------------------------------------
print("\n--- Benchmark 8: Closure Performance ---")

def make_counter(start_val):
    count = [start_val]
    def increment():
        count[0] += 1
        return count[0]
    return increment

def bench_closures(n):
    counter = make_counter(0)
    total = 0
    for i in range(n):
        total += counter()
    return total

iterations = 10000

start = time.perf_counter()
result8 = bench_closures(iterations)
elapsed8 = time.perf_counter() - start
print(f"Closure Counter ({iterations} calls): {result8} in {elapsed8:.6f}s")

# --------------------------------------------
# Benchmark 9: List of Dicts
# --------------------------------------------
print("\n--- Benchmark 9: List of Dicts ---")

def bench_list_of_dicts_create(n):
    data = []
    for i in range(n):
        data.append({"id": i, "value": i * 10})
    return len(data)

def bench_list_of_dicts_access(data, n):
    total = 0
    for i in range(n):
        total += data[i]["value"]
    return total

iterations = 5000

start = time.perf_counter()
list_dict = []
for i in range(iterations):
    list_dict.append({"id": i, "value": i * 10})
elapsed9 = time.perf_counter() - start
print(f"List of Dicts Create ({iterations}): {len(list_dict)} in {elapsed9:.6f}s")

start = time.perf_counter()
result9 = bench_list_of_dicts_access(list_dict, iterations)
elapsed9 = time.perf_counter() - start
print(f"List of Dicts Access Sum: {result9} in {elapsed9:.6f}s")

# --------------------------------------------
# Benchmark 10: Class/Object Operations
# --------------------------------------------
print("\n--- Benchmark 10: Class/Object Operations ---")

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def add(self, other):
        return Point(self.x + other.x, self.y + other.y)

def bench_objects(n):
    points = []
    for i in range(n):
        points.append(Point(i, i))
    return len(points)

iterations = 5000

start = time.perf_counter()
points = bench_objects(iterations)
elapsed10 = time.perf_counter() - start
print(f"Object Create ({iterations} Points): {points} in {elapsed10:.6f}s")

print("\n" + "=" * 60)
print("BENCHMARKS COMPLETE")
print("=" * 60)
