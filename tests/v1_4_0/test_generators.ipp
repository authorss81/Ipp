# Test v1.4.0 - Generators

print("=== Testing v1.4.0 Generators ===")

# ====== Basic Generator Test ======
print("\n--- Basic Generator Test ---")
func count_up() {
    var i = 0
    while i < 5 {
        yield i
        i = i + 1
    }
}

var gen = count_up()
print("Generator type:", type(gen))
print("v1:", next(gen))
print("v2:", next(gen))
print("v3:", next(gen))
print("v4:", next(gen))
print("v5:", next(gen))
print("v6:", next(gen))
gen = count_up()
assert next(gen) == 0
assert next(gen) == 1
assert next(gen) == 2

# ====== Range Generator ======
print("\n--- Range Generator Test ---")
func range_gen(start, end) {
    var i = start
    while i < end {
        yield i
        i = i + 1
    }
}

var r = range_gen(0, 5)
print("r1:", next(r))
print("r2:", next(r))
print("r3:", next(r))
print("r4:", next(r))
print("r5:", next(r))
print("r6:", next(r))

# ====== For-in with Generator ======
print("\n--- For-in with Generator Test ---")
func fibonacci(n) {
    var a = 0
    var b = 1
    var count = 0
    while count < n {
        yield a
        var temp = a
        a = b
        b = temp + b
        count = count + 1
    }
}

for n in fibonacci(8) {
    print(n)
}

# ====== is_generator Test ======
print("\n--- is_generator Test ---")
var gen2 = count_up()
print("is_generator(gen):", is_generator(gen2))
print("is_generator(42):", is_generator(42))
print("is_generator([1,2,3]):", is_generator([1, 2, 3]))

# ====== Generator with Parameters ======
print("\n--- Generator with Parameters Test ---")
func multiply_gen(factor, count) {
    var i = 1
    while i <= count {
        yield i * factor
        i = i + 1
    }
}

var mg = multiply_gen(3, 4)
print("3x1:", next(mg))
print("3x2:", next(mg))
print("3x3:", next(mg))
print("3x4:", next(mg))
print("3x5:", next(mg))

# ====== Multiple Generators ======
print("\n--- Multiple Generators Test ---")
var g1 = range_gen(0, 3)
var g2 = range_gen(10, 13)
print("g1:", next(g1))
print("g2:", next(g2))
print("g1:", next(g1))
print("g2:", next(g2))
print("g1:", next(g1))
print("g2:", next(g2))

print("\n=== v1.4.0 Generator tests complete! ===")
