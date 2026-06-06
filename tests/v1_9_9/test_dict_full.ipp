# v1.9.9: dict.map(), dict.filter(), dict.items() full support

# --- dict.items() returns proper list of pairs ---

var d = {"a": 1, "b": 2, "c": 3}

# items() works with for-in destructuring
var count = 0
for k, v in d.items() {
    count = count + v
    assert v > 0
}
assert count == 6

# items() returns list-like value
var pairs = d.items()
assert len(pairs) == 3
assert pairs[0] == ["a", 1] or pairs[1] == ["b", 2]

# --- dict.map() ---

var doubled = d.map(func(k, v) { return v * 2 })
assert doubled["a"] == 2
assert doubled["b"] == 4
assert doubled["c"] == 6

# Original unchanged
assert d["a"] == 1

# Map with key transformation
var keyed = d.map(func(k, v) { return k + str(v) })
assert keyed["a"] == "a1"
assert keyed["b"] == "b2"

# --- dict.filter() ---

var filtered = d.filter(func(k, v) { return v > 1 })
assert len(filtered) == 2
assert filtered["b"] == 2
assert filtered["c"] == 3

# Filter with key condition
var a_only = d.filter(func(k, v) { return k == "a" })
assert len(a_only) == 1
assert a_only["a"] == 1

# Filter all (empty result)
var empty = d.filter(func(k, v) { return false })
assert len(empty) == 0

# --- Chaining map and filter ---
var prices = {"apple": 1.5, "banana": 0.75, "cherry": 3.0}
var cheap = prices.filter(func(k, v) { return v < 2.0 })
assert len(cheap) == 2
var names = cheap.keys()
assert len(names) == 2

# --- Empty dict ---
var empty_dict = {}
assert empty_dict.items() == []
assert empty_dict.keys() == []
assert empty_dict.values() == []

print("All dict full API tests passed!")
