# Counter closure with nonlocal
func make_counter(start=0) {
    var count = start
    func inc() {
        nonlocal count
        count = count + 1
        return count
    }
    func reset() {
        nonlocal count
        count = start
    }
    func get() { return count }
    return [inc, reset, get]
}

var counter = make_counter(10)
var inc = counter[0]; var reset = counter[1]; var get = counter[2]
assert get() == 10
assert inc() == 11
assert inc() == 12
assert inc() == 13
reset()
assert get() == 10

# Multiple nonlocal names
func make_pair() {
    var a = 1
    var b = 2
    func swap() {
        nonlocal a, b
        var tmp = a
        a = b
        b = tmp
    }
    func read() { return [a, b] }
    return [swap, read]
}

var pair = make_pair()
var swap = pair[0]; var read = pair[1]
var vals = read()
assert vals[0] == 1
assert vals[1] == 2
swap()
vals = read()
assert vals[0] == 2
assert vals[1] == 1

# Nonlocal with compound assign
func make_accum() {
    var total = 0
    func add(n) {
        nonlocal total
        total = total + n
    }
    func get_total() { return total }
    return [add, get_total]
}

var accum = make_accum()
var add_fn = accum[0]; var get_total = accum[1]
add_fn(10)
add_fn(20)
add_fn(5)
assert get_total() == 35

# Memoization with nonlocal
func memoize(fn) {
    var cache = {}
    func wrapper(x) {
        nonlocal cache
        if cache.get(str(x)) != nil {
            return cache.get(str(x))
        }
        var result = fn(x)
        cache[str(x)] = result
        return result
    }
    return wrapper
}
var calls = 0
func slow_double(x) {
    calls = calls + 1
    return x * 2
}
var fast_double = memoize(slow_double)
assert fast_double(5) == 10
assert fast_double(5) == 10
assert calls == 1

# Nested nonlocal (closure in closure)
func make_nested() {
    var level1 = 1
    func outer() {
        nonlocal level1
        var level2 = 2
        func inner() {
            nonlocal level2
            level2 = level2 + 1
            level1 = level1 + 1
            return [level1, level2]
        }
        return inner
    }
    return outer()
}

var nested = make_nested()
var res = nested()
assert res[0] == 2
assert res[1] == 3
res = nested()
assert res[0] == 3
assert res[1] == 4
