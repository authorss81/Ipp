# v1.9.4: Async return value fix (BUG-016) + await inside async functions

# ===== Basic async return value =====
async func double_async(x) {
    return x * 2
}
var result = async_run(double_async(21))
print(result)
assert result == 42

async func add_async(a, b) {
    return a + b
}
assert async_run(add_async(10, 20)) == 30

# ===== Async with string return =====
async func greet(name) {
    return "Hello, " + name + "!"
}
assert async_run(greet("Alice")) == "Hello, Alice!"

# ===== Async with complex logic =====
async func compute(n) {
    var total = 0
    var i = 0
    while i < n {
        total = total + i
        i = i + 1
    }
    return total
}
assert async_run(compute(100)) == 4950

# ===== await inside async functions =====
async func fetch(url) {
    return "data:" + url
}

async func process(url) {
    var raw = await fetch(url)
    return raw.upper()
}

var processed = async_run(process("api.example.com"))
print(processed)
assert processed == "DATA:API.EXAMPLE.COM"

# ===== Chained awaits =====
async func step1() {
    return 1
}

async func step2(x) {
    return x + 1
}

async func step3(x) {
    return x * 10
}

async func pipeline() {
    var a = await step1()
    var b = await step2(a)
    var c = await step3(b)
    return c
}

assert async_run(pipeline()) == 20

# ===== Multiple awaits in sequence =====
async func fetch_data() {
    sleep(0.01)
    return 42
}

async func process_data() {
    var x = await fetch_data()
    var y = await fetch_data()
    return x + y
}

assert async_run(process_data()) == 84

# ===== await with sleep =====
async func delayed_value(v, delay) {
    sleep(delay)
    return v
}

var val = async_run(delayed_value(99, 0.01))
assert val == 99

# ===== Nested async calls without await =====
async func inner() {
    return 5
}

async func outer_no_await() {
    var c = inner()
    return async_run(c)
}

assert async_run(outer_no_await()) == 5

# ===== is_coroutine works =====
assert is_coroutine(double_async(5)) == true
assert is_coroutine(42) == false
assert is_coroutine("hello") == false

# ===== async with conditionals =====
async func max_async(a, b) {
    if a > b {
        return a
    }
    return b
}
assert async_run(max_async(10, 20)) == 20
assert async_run(max_async(30, 5)) == 30

print("v1.9.4: Async return + await tests PASSED")
