# v2.1.0.2.3 — Runtime types behavioral test
print("=== v2.1.0.2.3 Runtime Types Behavioral Tests ===")

# IppList
var lst = [1, 2, 3]
assert type(lst) == "list"
assert len(lst) == 3
lst.append(4)
assert len(lst) == 4
assert lst[0] == 1
assert lst[3] == 4
print("  [PASS] IppList operations")

# IppDict
var d = {"a": 1, "b": 2}
assert type(d) == "dict"
assert len(d) == 2
assert d["a"] == 1
d["c"] = 3
assert len(d) == 3
assert d["c"] == 3
print("  [PASS] IppDict operations")

# IppSet (created via set([]) syntax)
var s = set([1, 2, 3])
assert type(s) == "set"
assert len(s) == 3
s.add(4)
assert len(s) == 4
print("  [PASS] IppSet operations")

# IppRange
var r = range(0, 5)
var count = 0
for i in r {
    count = count + 1
}
assert count == 5
print("  [PASS] IppRange operations")

# IppFunction (user-defined)
func add(a, b) {
    return a + b
}
assert type(add) == "func"
assert add(2, 3) == 5
print("  [PASS] IppFunction operations")

print()
print("All v2.1.0.2.3 type behavioral tests passed!")
