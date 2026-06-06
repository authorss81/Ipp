# v1.9.7: zip() builtin

# Basic zip — pairs two lists
var a = [1, 2, 3]
var b = [4, 5, 6]
var zipped = zip(a, b)
assert zipped == [[1, 4], [2, 5], [3, 6]]

# Unequal lengths — stops at shortest
var c = [1, 2]
var d = [10, 20, 30]
assert len(zip(c, d)) == 2

# Single-element lists
var single_zip = zip(["x"], ["y"])
assert single_zip == [["x", "y"]]

# Empty lists
assert zip([], []) == []
assert zip([1], []) == []
assert zip([], [2]) == []

# Use in for loop with pair indexing
var sums = []
for pair in zip(a, b) {
    sums = sums + [pair[0] + pair[1]]
}
assert sums == [5, 7, 9]

# Use in for loop with destructuring
var names = ["Alice", "Bob", "Carol"]
var scores = [95, 87, 92]
var results = []
for name, score in zip(names, scores) {
    results = results + [name + ":" + str(score)]
}
assert results == ["Alice:95", "Bob:87", "Carol:92"]

# Zip with range() (lazy iterable)
var r = range(3)
var z = zip(r, ["a", "b", "c"])
assert z == [[0, "a"], [1, "b"], [2, "c"]]

# Zip three lists
var x = [1, 2]
var y = [3, 4]
var zz = [5, 6]
var triple = zip(x, y, zz)
assert triple == [[1, 3, 5], [2, 4, 6]]

# zip with no arguments
assert zip() == []

print("All zip tests passed!")
