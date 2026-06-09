# v2.0.3 — List Destructuring Assignment
print("test list destructure begin")

# Basic destructuring
var [a, b, c] = [1, 2, 3]
assert a == 1 and b == 2 and c == 3

# Rest pattern
var [first, ...rest] = [10, 20, 30, 40, 50]
assert first == 10
assert rest == [20, 30, 40, 50]

# Destructure function return
func get_pos() { return [100.0, 200.0] }
var [px, py] = get_pos()
assert px == 100.0
assert py == 200.0

# Swap via destructuring
var x = 1
var y = 2
var [x, y] = [y, x]
assert x == 2 and y == 1

# Single element
var [only] = [42]
assert only == 42

# Rest with single element
var [head, ...tail] = [7]
assert head == 7
assert tail == []

print("test list destructure passed")
