# ============================================
# Python Benchmark Comparison for Ipp
# ============================================
# Run this file to compare Python performance
# with Ipp benchmarks.
# ============================================

import time
import math
import random

print("=" * 60)
print("PYTHON BENCHMARKS (for comparison)")
print("=" * 60)

# --------------------------------------------
# Benchmark 1: Integer Arithmetic
# --------------------------------------------
print("\n--- Benchmark 1: Integer Arithmetic ---")

def bench_integer_add(n):
    sum = 0
    for i in range(n):
        sum += i
    return sum

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
result = bench_integer_add(iterations)
elapsed = time.perf_counter() - start
print(f"Integer Add: {result} in {elapsed:.4f}s")

start = time.perf_counter()
result = bench_integer_mul(100)
elapsed = time.perf_counter() - start
print(f"Integer Mul (100!): {result} in {elapsed:.4f}s")

start = time.perf_counter()
result = bench_integer_mod(iterations)
elapsed = time.perf_counter() - start
print(f"Integer Mod: {result} in {elapsed:.4f}s")

# --------------------------------------------
# Benchmark 2: Floating Point Math
# --------------------------------------------
print("\n--- Benchmark 2: Floating Point Math ---")

def bench_float_trig(n):
    sum = 0.0
    for i in range(n):
        sum += math.sin(i)
    return sum

def bench_float_sqrt(n):
    sum = 0.0
    for i in range(1, n + 1):
        sum += math.sqrt(i)
    return sum

iterations = 50000

start = time.perf_counter()
result = bench_float_trig(iterations)
elapsed = time.perf_counter() - start
print(f"Float Trig (sin): {result} in {elapsed:.4f}s")

start = time.perf_counter()
result = bench_float_sqrt(iterations)
elapsed = time.perf_counter() - start
print(f"Float Sqrt: {result} in {elapsed:.4f}s")

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

iterations = 10000

start = time.perf_counter()
result = bench_string_concat(iterations)
elapsed = time.perf_counter() - start
print(f"String Concat: {result} in {elapsed:.4f}s")

test_string = "a,b,c,d,e,f,g,h,i,j"
start = time.perf_counter()
result = bench_string_split(test_string, iterations)
elapsed = time.perf_counter() - start
print(f"String Split: {result} in {elapsed:.4f}s")

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

iterations = 25

start = time.perf_counter()
result = bench_recursive_fib(iterations)
elapsed = time.perf_counter() - start
print(f"Recursive Fibonacci(25): {result} in {elapsed:.4f}s")

start = time.perf_counter()
result = bench_iterative_fib(10000)
elapsed = time.perf_counter() - start
print(f"Iterative Fibonacci(10000): {result} in {elapsed:.4f}s")

start = time.perf_counter()
result = bench_higher_order(100000, simple_add)
elapsed = time.perf_counter() - start
print(f"Higher-Order Function: {result} in {elapsed:.4f}s")

# --------------------------------------------
# Benchmark 5: List Operations
# --------------------------------------------
print("\n--- Benchmark 5: List Operations ---")

def bench_list_append(n):
    lst = []
    for i in range(n):
        lst.append(i)
    return len(lst)

def bench_list_iterate(lst):
    sum = 0
    for x in lst:
        sum += x
    return sum

def bench_list_comprehension(n):
    return [i * 2 for i in range(n)]

iterations = 50000

start = time.perf_counter()
result = bench_list_append(iterations)
elapsed = time.perf_counter() - start
print(f"List Append: {result} in {elapsed:.4f}s")

test_list = bench_list_append(iterations)
start = time.perf_counter()
result = bench_list_iterate(test_list)
elapsed = time.perf_counter() - start
print(f"List Iterate: {result} in {elapsed:.4f}s")

start = time.perf_counter()
result = len(bench_list_comprehension(iterations))
elapsed = time.perf_counter() - start
print(f"List Comprehension: {result} in {elapsed:.4f}s")

# --------------------------------------------
# Benchmark 6: Vector Operations
# --------------------------------------------
print("\n--- Benchmark 6: Vector Operations ---")

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

def bench_vec2_operations(n):
    sum = Vec2(0, 0)
    for i in range(n):
        v = Vec2(float(i), float(i + 1))
        sum.x += v.x
        sum.y += v.y
    return sum

def bench_vec2_distance(n):
    total = 0.0
    for i in range(n):
        a = Vec2(float(i), float(i))
        b = Vec2(float(i + 1), float(i + 1))
        dx = b.x - a.x
        dy = b.y - a.y
        total += math.sqrt(dx * dx + dy * dy)
    return total

iterations = 100000

start = time.perf_counter()
result = bench_vec2_operations(iterations)
elapsed = time.perf_counter() - start
print(f"Vec2 Operations: ({result.x}, {result.y}) in {elapsed:.4f}s")

start = time.perf_counter()
result = bench_vec2_distance(iterations)
elapsed = time.perf_counter() - start
print(f"Vec2 Distance: {result} in {elapsed:.4f}s")

# --------------------------------------------
# Benchmark 7: Physics
# --------------------------------------------
print("\n--- Benchmark 7: Physics ---")

def bench_physics(particles, iterations):
    positions = [Vec2(float(i), float(i)) for i in range(particles)]
    velocities = [Vec2(1.0, 1.0) for _ in range(particles)]
    
    for t in range(iterations):
        for i in range(particles):
            positions[i].x += velocities[i].x * 0.016
            positions[i].y += velocities[i].y * 0.016
    
    return len(positions)

particles = 1000
iterations = 1000

start = time.perf_counter()
result = bench_physics(particles, iterations)
elapsed = time.perf_counter() - start
print(f"Physics (1000 particles, 1000 iters): {result} in {elapsed:.4f}s")

# --------------------------------------------
# Benchmark 8: ECS
# --------------------------------------------
print("\n--- Benchmark 8: ECS Pattern ---")

def bench_ecs(entities, components):
    positions = [Vec2(float(i), float(i)) for i in range(entities)]
    velocities = [Vec2(1.0, 2.0) for _ in range(entities)]
    active = [i < entities for i in range(entities)]
    
    total = 0
    for t in range(components):
        for i in range(entities):
            if active[i]:
                positions[i].x += velocities[i].x * 0.016
                positions[i].y += velocities[i].y * 0.016
                total += positions[i].x + positions[i].y
    
    return total

entities = 5000
components = 100

start = time.perf_counter()
result = bench_ecs(entities, components)
elapsed = time.perf_counter() - start
print(f"ECS (5000 entities, 100 frames): {result} in {elapsed:.4f}s")

# --------------------------------------------
# Benchmark 9: Particles
# --------------------------------------------
print("\n--- Benchmark 9: Particle System ---")

def bench_particles(count, lifetime):
    particles = [
        {"x": float(i), "y": float(i), "vx": 1.0, "vy": 2.0, "life": lifetime}
        for i in range(count)
    ]
    
    total_life = 0
    for frame in range(100):
        for p in particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] > 0:
                total_life += p["life"]
    
    return total_life

count = 5000
lifetime = 100

start = time.perf_counter()
result = bench_particles(count, lifetime)
elapsed = time.perf_counter() - start
print(f"Particles (5000, 100 frames): {result} in {elapsed:.4f}s")

print("\n" + "=" * 60)
print("BENCHMARKS COMPLETE")
print("=" * 60)
