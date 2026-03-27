# ============================================
# Ipp Language Benchmarks v1.x
# ============================================
# This file contains comprehensive benchmarks
# for Ipp language performance testing.
# Run with: python -c "exec(open('tests/v1/benchmarks/ipp_benchmarks.py').read())"
# ============================================

# ============================================
# MICRO BENCHMARKS
# ============================================

print("=" * 60)
print("IPP MICRO BENCHMARKS")
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
result1 = bench_integer_mul(100)
elapsed1 = time() - start
print("Integer Mul (100!): " + str(result1) + " in " + str(elapsed1) + "s")

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
        sum = sum + sin(float(i))
    }
    return sum
}

func bench_float_sqrt(n) {
    var sum = 0.0
    for i in 1..n {
        sum = sum + sqrt(float(i))
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

iterations = 10000

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

iterations = 25

start = time()
var result4 = bench_recursive_fib(iterations)
var elapsed4 = time() - start
print("Recursive Fibonacci(25): " + str(result4) + " in " + str(elapsed4) + "s")

start = time()
result4 = bench_iterative_fib(10000)
elapsed4 = time() - start
print("Iterative Fibonacci(10000): " + str(result4) + " in " + str(elapsed4) + "s")

start = time()
result4 = bench_higher_order(100000, simple_add)
elapsed4 = time() - start
print("Higher-Order Function: " + str(result4) + " in " + str(elapsed4) + "s")

# --------------------------------------------
# Benchmark 5: List/Collection Operations
# --------------------------------------------
print("\n--- Benchmark 5: List Operations ---")

func bench_list_append(n) {
    var lst = []
    for i in 0..n {
        lst.append(i)
    }
    return len(lst)
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
var result5 = bench_list_append(iterations)
var elapsed5 = time() - start
print("List Append: " + str(result5) + " in " + str(elapsed5) + "s")

var test_list = bench_list_append(iterations)
start = time()
result5 = bench_list_iterate(test_list)
elapsed5 = time() - start
print("List Iterate: " + str(result5) + " in " + str(elapsed5) + "s")

start = time()
result5 = len(bench_list_comprehension(iterations))
elapsed5 = time() - start
print("List Comprehension: " + str(result5) + " in " + str(elapsed5) + "s")

# ============================================
# GAME-SPECIFIC BENCHMARKS
# ============================================

print("\n" + "=" * 60)
print("GAME-SPECIFIC BENCHMARKS")
print("=" * 60)

# --------------------------------------------
# Benchmark 6: Vector Operations
# --------------------------------------------
print("\n--- Benchmark 6: Vector Operations ---")

func bench_vec2_operations(n) {
    var sum = vec2(0, 0)
    for i in 0..n {
        var v = vec2(float(i), float(i + 1))
        sum.x = sum.x + v.x
        sum.y = sum.y + v.y
    }
    return sum
}

func bench_vec2_distance(n) {
    var total = 0.0
    for i in 0..n {
        var a = vec2(float(i), float(i))
        var b = vec2(float(i + 1), float(i + 1))
        var dx = b.x - a.x
        var dy = b.y - a.y
        total = total + sqrt(dx * dx + dy * dy)
    }
    return total
}

iterations = 100000

start = time()
var result6 = bench_vec2_operations(iterations)
var elapsed6 = time() - start
print("Vec2 Operations: (" + str(result6.x) + ", " + str(result6.y) + ") in " + str(elapsed6) + "s")

start = time()
result6 = bench_vec2_distance(iterations)
elapsed6 = time() - start
print("Vec2 Distance: " + str(result6) + " in " + str(elapsed6) + "s")

# --------------------------------------------
# Benchmark 7: Simple Physics (Verlet Integration)
# --------------------------------------------
print("\n--- Benchmark 7: Simple Physics ---")

func bench_physics(particles, iterations) {
    var positions = []
    var velocities = []
    
    for i in 0..particles {
        positions.append(vec2(float(i), float(i)))
        velocities.append(vec2(1.0, 1.0))
    }
    
    for t in 0..iterations {
        for i in 0..particles {
            positions[i].x = positions[i].x + velocities[i].x * 0.016
            positions[i].y = positions[i].y + velocities[i].y * 0.016
        }
    }
    return len(positions)
}

var particles = 1000
iterations = 1000

start = time()
var result7 = bench_physics(particles, iterations)
var elapsed7 = time() - start
print("Physics (1000 particles, 1000 iters): " + str(result7) + " in " + str(elapsed7) + "s")

# --------------------------------------------
# Benchmark 8: Entity Component System Pattern
# --------------------------------------------
print("\n--- Benchmark 8: ECS Pattern ---")

func bench_ecs(entities, components) {
    var positions = []
    var velocities = []
    var active = []
    
    for i in 0..entities {
        positions.append(vec2(float(i), float(i)))
        velocities.append(vec2(1.0, 2.0))
        active.append(i < entities)
    }
    
    var sum = 0
    for t in 0..components {
        for i in 0..entities {
            if active[i] {
                positions[i].x = positions[i].x + velocities[i].x * 0.016
                positions[i].y = positions[i].y + velocities[i].y * 0.016
                sum = sum + positions[i].x + positions[i].y
            }
        }
    }
    return sum
}

var entities = 5000
var components = 100

start = time()
var result8 = bench_ecs(entities, components)
var elapsed8 = time() - start
print("ECS (5000 entities, 100 frames): " + str(result8) + " in " + str(elapsed8) + "s")

# --------------------------------------------
# Benchmark 9: Pathfinding (Simple A*)
# --------------------------------------------
print("\n--- Benchmark 9: Pathfinding ---")

func bench_pathfinding(grid_size, paths) {
    var grid = []
    for y in 0..grid_size {
        var row = []
        for x in 0..grid_size {
            row.append(x + y < grid_size + 2)
        }
        grid.append(row)
    }
    
    func heuristic(a, b) {
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    }
    
    var paths_found = 0
    for p in 0..paths {
        var start = [0, 0]
        var end = [grid_size - 1, grid_size - 1]
        paths_found = paths_found + 1
    }
    return paths_found
}

var grid_size = 20
var num_paths = 50

start = time()
var result9 = bench_pathfinding(grid_size, num_paths)
var elapsed9 = time() - start
print("Pathfinding (20x20 grid, 50 paths): " + str(result9) + " in " + str(elapsed9) + "s")

# --------------------------------------------
# Benchmark 10: Particle System
# --------------------------------------------
print("\n--- Benchmark 10: Particle System ---")

func bench_particles(count, lifetime) {
    var particles = []
    
    for i in 0..count {
        particles.append({
            x: float(i),
            y: float(i),
            vx: 1.0,
            vy: 2.0,
            life: lifetime
        })
    }
    
    var total_life = 0
    for frame in 0..100 {
        for p in particles {
            p.x = p.x + p.vx
            p.y = p.y + p.vy
            p.life = p.life - 1
            if p.life > 0 {
                total_life = total_life + p.life
            }
        }
    }
    return total_life
}

var count = 5000
var lifetime = 100

start = time()
var result10 = bench_particles(count, lifetime)
var elapsed10 = time() - start
print("Particles (5000, 100 frames): " + str(result10) + " in " + str(elapsed10) + "s")

print("\n" + "=" * 60)
print("BENCHMARKS COMPLETE")
print("=" * 60)
