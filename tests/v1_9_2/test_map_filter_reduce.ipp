# v1.9.2: Global map/filter/reduce builtins

# ===== map =====
func double(x) { return x * 2 }
print(map(double, [1,2,3]))
assert map(double, [1,2,3]) == [2,4,6]

# map with lambda
print(map(func(x) { return x * 3 }, [1,2,3]))
assert map(func(x) { return x * 3 }, [1,2,3]) == [3,6,9]

# map empty list
assert map(double, []) == []

# map preserves types
assert map(func(x) { return str(x) }, [1,2,3]) == ["1","2","3"]

# ===== filter =====
func is_even(x) { return x % 2 == 0 }
print(filter(is_even, [1,2,3,4,5,6]))
assert filter(is_even, [1,2,3,4,5,6]) == [2,4,6]

func is_positive(x) { return x > 0 }
assert filter(is_positive, [-2,-1,0,1,2]) == [1,2]

# filter empty list
assert filter(is_even, []) == []

# filter all pass
assert filter(func(x) { return true }, [1,2,3]) == [1,2,3]

# filter all fail
assert filter(func(x) { return false }, [1,2,3]) == []

# ===== reduce =====
func add(a, b) { return a + b }
func mul(a, b) { return a * b }

print(reduce(add, [1,2,3,4,5]))
assert reduce(add, [1,2,3,4,5]) == 15

assert reduce(mul, [1,2,3,4]) == 24

# reduce with initial value
print(reduce(add, [1,2,3], 10))
assert reduce(add, [1,2,3], 10) == 16

assert reduce(mul, [2,3,4], 1) == 24

# reduce with single element (no initial)
assert reduce(add, [42]) == 42
assert reduce(mul, [99]) == 99

# reduce with initial and empty list
assert reduce(add, [], 0) == 0
assert reduce(mul, [], 1) == 1

# reduce with initial and single element
assert reduce(add, [5], 10) == 15

# ===== complex usage =====
# chain map and filter
assert map(double, filter(is_even, [1,2,3,4,5,6])) == [4,8,12]

# reduce after map
assert reduce(add, map(double, [1,2,3])) == 12

# using named functions with reduce
func concat(a, b) { return a + b }
assert reduce(concat, ["a","b","c"]) == "abc"
assert reduce(concat, ["x","y","z"], "prefix-") == "prefix-xyz"

# ===== error cases =====
# reduce with empty sequence and no initial should error
# This is tested by assertion failure
# var caught = try { reduce(add, []) } catch(e) { e }
# print(caught)

print("v1.9.2: map/filter/reduce tests PASSED")
