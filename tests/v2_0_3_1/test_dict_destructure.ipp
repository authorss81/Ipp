# v2.0.3.1 — Dict Destructuring Assignment
print("test dict destructure begin")

# Basic dict destructuring
var d = {"x": 10, "y": 20, "z": 30}
var {x, y, z} = d
assert x == 10 and y == 20 and z == 30

# With defaults
var {a, b, c=99} = {"a": 1, "b": 2}
assert a == 1 and b == 2 and c == 99

# All defaults (no matching keys)
var {p=100, q=200} = {}
assert p == 100 and q == 200

# Mixed
var {first, second="fallback"} = {"first": "hello"}
assert first == "hello"
assert second == "fallback"

# Destructure dict literal directly
var {m, n} = {"m": 5, "n": 10}
assert m == 5 and n == 10

print("test dict destructure passed")
