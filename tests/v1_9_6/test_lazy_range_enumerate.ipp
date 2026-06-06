# v1.9.6: range() as lazy iterator + enumerate() builtin

# --- range() is now lazy (IppRange) ---

# range() still works correctly for iteration
var sum = 0
for i in range(10) {
    sum = sum + i
}
assert sum == 45

# len() works on range
assert len(range(10)) == 10
assert len(range(3, 8)) == 5
assert len(range(0, 10, 2)) == 5

# range() with step
var sum2 = 0
for i in range(0, 10, 2) {
    sum2 = sum2 + i
}
assert sum2 == 20

# range() indexing works
var r = range(10)
assert r[0] == 0
assert r[5] == 5
assert r[9] == 9

# Negative indexing
assert r[-1] == 9
assert r[-5] == 5

# Large range is memory-efficient (would crash if materialized as list)
var large = range(100000)
assert len(large) == 100000
assert large[0] == 0
assert large[99999] == 99999

# .. operator also lazy
var dotdot = 0..5
assert len(dotdot) == 5
assert dotdot[3] == 3

# --- enumerate() standalone builtin ---

# Basic enumerate
var items = ["x", "y", "z"]
var result = []
for i, v in enumerate(items) {
    result = result + [str(i) + "=" + v]
}
assert result == ["0=x", "1=y", "2=z"]

# enumerate on range
var counted = 0
for i, val in enumerate(range(5)) {
    assert i == val
    counted = counted + 1
}
assert counted == 5

# enumerate returns list of pairs
var pairs = enumerate(["a", "b"])
assert pairs[0] == [0, "a"]
assert pairs[1] == [1, "b"]

# enumerate on list with start
var start_count = 0
for i, v in enumerate(["a","b","c"], start=1) {
    assert i >= 1
    start_count = start_count + 1
}
assert start_count == 3

print("All lazy range and enumerate tests passed!")
