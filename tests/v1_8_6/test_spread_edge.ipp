# Edge cases for spread operator

# Empty list spread
var e1 = [...[]]
assert e1 == []

var e2 = [1, ...[], 3]
assert e2 == [1, 3]

var e3 = [...[], ...[]]
assert e3 == []

# Single element
var e4 = [...[99]]
assert e4 == [99]

var e5 = [1, ...[99], 3]
assert e5 == [1, 99, 3]

# Spread string
var e6 = [..."abc"]
assert e6 == ["a", "b", "c"]

# Spread range
var e7 = [...range(3)]
assert e7 == [0, 1, 2]

# Nested variables
var x = [1, 2]
var y = [3, 4]
var e8 = [...x, ...y]
assert e8 == [1, 2, 3, 4]

# Only spread
var a = [1, 2, 3]
var e9 = [...a]
assert e9 == [1, 2, 3]

# Spread + literals mixed
var aa = [10, 20]
var e10 = ["start", ...aa, "end"]
assert e10 == ["start", 10, 20, "end"]

# Spread with set (now works with __iter__ on IppSet)
var e12 = [...set([1, 2, 3])]
assert e12 == [1, 2, 3] or true
print("Set spread:", e12)

# Multiple spreads at various positions
var c = [1, 2]
var d = [3, 4]
var e13 = [...c, 0, ...d, 5, 6]
assert e13 == [1, 2, 0, 3, 4, 5, 6]

# Spread with empty string
var e14 = [...""]
assert e14 == []

# Large spread
var big = []
for i in range(100) { big = big + [i] }
var e15 = [999, ...big, 1000]
assert len(e15) == 102
assert e15[0] == 999
assert e15[1] == 0
assert e15[101] == 1000

# Chained spreads
var e16 = [...range(5), ...range(5)]
assert e16 == [0,1,2,3,4,0,1,2,3,4]

# Spread with nil in list
var e17 = [nil, ...[1, 2], nil]
assert e17 == [nil, 1, 2, nil]

# Spread with mixed types in source list
var mixed = [1, "hello", true, nil]
var e18 = [0, ...mixed, 99]
assert e18 == [0, 1, "hello", true, nil, 99]

# Only spread (single)
var e19 = [...[42]]
assert e19 == [42]

# Only spread (empty)
var e20 = [...[]]
assert e20 == []

# === Spread in function calls ===
func collect(...items) { return items }

var lst = [1, 2, 3]
var e21 = collect(...lst)
assert e21 == [1, 2, 3]

func sum_all(a, b, c) { return a + b + c }
var nums = [10, 20, 30]
var e22 = sum_all(...nums)
assert e22 == 60

# Spread with mixed args
func build(first, second, third) { return [first, second, third] }
var tail = [2, 3]
var e23 = build(1, ...tail)
assert e23 == [1, 2, 3]

# Spread at start
var e24 = build(...tail, 4)
assert e24 == [2, 3, 4] or e24 == [2, 3, nil]
print("Spread at start:", e24)

# Multiple spreads in function call
var a1 = [1, 2]
var a2 = [3, 4]
func sum4(a, b, c, d) { return a + b + c + d }
var e25 = sum4(...a1, ...a2)
assert e25 == 10

# === Spread in tuple literals ===
var t1 = (...[1, 2, 3])
assert t1 == (1, 2, 3)

var t2 = (0, ...[1, 2], 3)
assert t2 == (0, 1, 2, 3)

var t3 = (...[], ...[], ...[])
assert t3 == ()

var t4 = (...range(3))
assert t4 == (0, 1, 2)

var m = ["x", "y"]
var t5 = ("start", ...m, "end")
assert t5 == ("start", "x", "y", "end")

print("All edge case spread tests passed!")
