# Test v2.0.8.2: parallel(coro1, coro2, ...) Concurrent Execution

# Helper to create a simple async coroutine
async func make_sequence(name, steps) {
    var log = []
    var i = 0
    while i < steps {
        log.append(name + ":" + str(i))
        i = i + 1
    }
    return log
}

# parallel with IppAsyncCoroutines
var coro_a = make_sequence("A", 3)
var coro_b = make_sequence("B", 3)

var results = async_run(parallel(coro_a, coro_b))
assert len(results) == 2

var log_a = results[0]
var log_b = results[1]
assert len(log_a) == 3
assert len(log_b) == 3
assert log_a[0] == "A:0"
assert log_a[1] == "A:1"
assert log_a[2] == "A:2"
assert log_b[0] == "B:0"
assert log_b[1] == "B:1"
assert log_b[2] == "B:2"

# --- parallel with delay ---
async func delayed_greeting(msg, sec) {
    await delay(sec)
    return msg
}

var g1 = delayed_greeting("hello", 0.001)
var g2 = delayed_greeting("world", 0.002)

var greet_results = async_run(parallel(g1, g2))
assert len(greet_results) == 2
assert greet_results[0] == "hello"
assert greet_results[1] == "world"

# --- parallel with mixed async coroutines ---
async func compute_sum(a, b) {
    return a + b
}

async func compute_product(a, b) {
    return a * b
}

var mixed = async_run(parallel(compute_sum(10, 20), compute_product(4, 5)))
assert len(mixed) == 2
assert mixed[0] == 30
assert mixed[1] == 20

print("All v2.0.8.2 parallel tests passed!")
