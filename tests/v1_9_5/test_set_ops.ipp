var a = set([1, 2, 3, 4])
var b = set([3, 4, 5, 6])

# union
var u = a.union(b)
assert len(u) == 6
assert u.contains(1) == true
assert u.contains(2) == true
assert u.contains(3) == true
assert u.contains(4) == true
assert u.contains(5) == true
assert u.contains(6) == true
assert u.contains(7) == false

# intersect
var i = a.intersect(b)
assert len(i) == 2
assert i.contains(3) == true
assert i.contains(4) == true
assert i.contains(1) == false
assert i.contains(5) == false

# difference
var d = a.difference(b)
assert len(d) == 2
assert d.contains(1) == true
assert d.contains(2) == true
assert d.contains(3) == false

var d2 = b.difference(a)
assert len(d2) == 2
assert d2.contains(5) == true
assert d2.contains(6) == true

# union with empty set
var empty = set()
assert len(a.union(empty)) == 4
assert len(empty.union(a)) == 4

# intersect with empty set
assert len(a.intersect(empty)) == 0

# difference with empty set
assert len(a.difference(empty)) == 4

# chain operations
var u2 = a.union(b).union(set([7, 8]))
assert len(u2) == 8
assert u2.contains(7) == true
assert u2.contains(8) == true

# original sets unchanged
assert a.contains(3) == true
assert b.contains(3) == true

print("All set operation tests passed!")
